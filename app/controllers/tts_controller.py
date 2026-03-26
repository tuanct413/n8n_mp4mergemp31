from fastapi import APIRouter, Request
import uuid, os, asyncio, random

from app.models.request_models import TTSRequest
from app.services.tts_service import generate_tts

router = APIRouter()

BASE_DIR = "./tmp"

EDGE_VOICES = [
    "vi-VN-HoaiMyNeural",
    "vi-VN-NamMinhNeural"
]

@router.post("/tts-fast")
def tts_fast(request: Request, data: TTSRequest):
    output_file = f"{BASE_DIR}/{uuid.uuid4()}.mp3"

    try:
        asyncio.run(generate_tts(data.text, data.voice, output_file, data.rate, data.volume, data.pitch))
        file_url = f"{request.base_url}files/{os.path.basename(output_file)}"
        return {"url": file_url, "voice": data.voice}
    except Exception as e:
        return {"error": str(e)}

@router.get("/voices")
def list_voices():
    return {"voices": EDGE_VOICES}