from fastapi import APIRouter
from fastapi.responses import FileResponse
import uuid, os

from app.models.request_models import MergeRequest
from app.services.merge_service import merge_video_audio
from app.utils.file_utils import cleanup

router = APIRouter()

BASE_DIR = "./tmp"
FFMPEG_PATH = "ffmpeg"

@router.post("/merge")
def merge(data: MergeRequest):

    video_file = f"{BASE_DIR}/{uuid.uuid4()}.mp4"
    audio_file = f"{BASE_DIR}/{uuid.uuid4()}.mp3"
    output_file = f"{BASE_DIR}/{uuid.uuid4()}.mp4"

    try:
        result = merge_video_audio(
            data.video_url,
            data.audio_url,
            data.offset,
            video_file,
            audio_file,
            output_file,
            FFMPEG_PATH
        )

        if result.returncode != 0:
            return {"error": result.stderr}

        return FileResponse(
            output_file,
            media_type="video/mp4",
            filename="output.mp4",
            background=lambda: cleanup(video_file, audio_file, output_file)
        )

    except Exception as e:
        return {"error": str(e)}