from pydantic import BaseModel

class MergeRequest(BaseModel):
    video_url: str
    audio_url: str
    offset: float = 2.5

class TTSRequest(BaseModel):
    text: str
    voice: str = "vi-VN-HoaiMyNeural" # mặc định
    rate: str = "-20%"
    volume: str = "+0%"
    pitch: str = "-3Hz"