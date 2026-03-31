from fastapi import APIRouter, Request
import uuid, os

from app.models.request_models import TTSRequest
from app.services.tts_service import generate_tts, calculate_rate  # thêm calculate_rate

router = APIRouter()

BASE_DIR = "./tmp"

EDGE_VOICES = [
    "vi-VN-HoaiMyNeural",
    "vi-VN-NamMinhNeural"
]

@router.post("/tts-fast")
async def tts_fast(request: Request, data: TTSRequest):
    output_file = f"{BASE_DIR}/{uuid.uuid4()}.mp3"

    try:
        rate = calculate_rate(data.text, data.target_duration) if data.target_duration else data.rate
        
        await generate_tts(data.text, data.voice, output_file, rate, data.volume, data.pitch)
        file_url = f"{request.base_url}files/{os.path.basename(output_file)}"
        return {"url": file_url, "voice": data.voice, "rate": rate}
    except Exception as e:
        return {"error": str(e)}

@router.get("/voices")
def list_voices():
    return {"voices": EDGE_VOICES}