from pydantic import BaseModel

class MergeRequest(BaseModel):
    video_url: str
    audio_url: str
    offset: float = 2.5

class TTSRequest(BaseModel):
    text: str
    voice: str = "vi-VN-HoaiMyNeural"
    rate: str = "+50%"
    volume: str = "+0%"
    pitch: str = "+30Hz"