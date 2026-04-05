import io
import os
import uuid
from fastapi import APIRouter, HTTPException, Response, Request
from fastapi.responses import StreamingResponse, JSONResponse
import logging
from app.models.image_models import ImageMergeRequest
from app.services.image_service import merge_logo_to_image

router = APIRouter(prefix="/image", tags=["Image Processing"])
logger = logging.getLogger(__name__)

@router.post("/merge-logo")
async def merge_logo(data: ImageMergeRequest, request: Request):
    """
    API endpoint to merge a logo with an image from URL or Base64.
    """
    logger.info("Received image merge request")
    
    try:
        # Run processing
        output = merge_logo_to_image(data)
        
        # Save to tmp directory
        filename = f"{uuid.uuid4()}_merged.jpg"
        file_path = os.path.join("./tmp", filename)
        with open(file_path, "wb") as f:
            f.write(output.getvalue())
            
        # Optional Request parameter to get base URL, but for simplicity we can return relative or absolute
        # The main app.py uses base relative paths or we can just return the path
        download_url = f"{request.base_url}files/{filename}"
        
        return JSONResponse(content={
            "message": "Image merged successfully",
            "download_url": download_url,
            "file_path": file_path
        })
        
    except FileNotFoundError as e:
        logger.error(f"Logo file error: {str(e)}")
        raise HTTPException(status_code=500, detail="Logo assets not found on server")
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.exception(f"Unexpected error during image processing: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Image processing failed", "detail": str(e)}
        )
