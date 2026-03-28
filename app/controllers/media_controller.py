from fastapi import APIRouter
from app.models.request_models import AudioRequest
from app.services.media_service import MediaService

router = APIRouter()

@router.post("/duration")
def get_duration(request: AudioRequest):
    duration = MediaService.get_audio_duration(request.audio_url)
    target = round(duration * 2.9)
    return {
        "duration": duration,
        "targetWords": target,
        "minWords": round(target * 0.9),
        "maxWords": round(target * 1.08)
    }