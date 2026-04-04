from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import uuid, os, logging
from fastapi.concurrency import run_in_threadpool

from app.models.request_models import MergeRequest
from app.services.merge_service import merge_video_audio
from app.utils.file_utils import cleanup
from app.utils.log_utils import clean_ffmpeg_error
from starlette.background import BackgroundTask

router = APIRouter()
logger = logging.getLogger(__name__)

BASE_DIR = "./tmp"
FFMPEG_PATH = "ffmpeg"

@router.post("/merge")
async def merge(data: MergeRequest):
    """
    Asynchronous route handler for merging video and audio.
    Uses run_in_threadpool to execute blocking ffmpeg/download calls
    while maintaining the request context (Request ID).
    """
    logger.info(f"Received merge request | Video URL: {data.video_url} | Audio URL: {data.audio_url}")

    request_id = str(uuid.uuid4())
    video_file = f"{BASE_DIR}/{request_id}_video.mp4"
    audio_file = f"{BASE_DIR}/{request_id}_audio.mp3"
    output_file = f"{BASE_DIR}/{request_id}_output.mp4"

    try:
        logger.info("Starting ffmpeg merge process")
        # Explicitly run the blocking service in a threadpool to ensure context propagation
        result = await run_in_threadpool(
            merge_video_audio,
            data.video_url,
            data.audio_url,
            data.offset,
            video_file,
            audio_file,
            output_file,
            FFMPEG_PATH
        )

        if result.returncode != 0:
            # Clean up the noisy ffmpeg output before logging and returning
            cleaned_error = clean_ffmpeg_error(result.stderr)
            logger.error(f"Ffmpeg failed (code {result.returncode}) | Error: {cleaned_error}")
            
            # Return proper 500 status code for processing errors
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Video processing failed", 
                    "detail": cleaned_error,
                    "code": result.returncode
                }
            )

        logger.info(f"Merge successful. Delivering file: {output_file}")
        return FileResponse(
            output_file,
            media_type="video/mp4",
            filename="output.mp4",
            background=BackgroundTask(cleanup, video_file, audio_file, output_file)
        )

    except Exception as e:
        logger.exception(f"Unexpected error during merge: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(e)}
        )