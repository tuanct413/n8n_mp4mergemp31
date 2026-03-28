from fastapi import APIRouter
from app.models.request_models import AudioRequest
from app.services.media_service import MediaService

router = APIRouter()

@router.post("/duration")
def get_duration(request: AudioRequest):
    duration = MediaService.get_audio_duration(request.audio_url)
    return {
        "duration": duration
    }