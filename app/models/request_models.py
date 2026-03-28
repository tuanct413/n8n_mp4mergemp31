from pydantic import BaseModel

class MergeRequest(BaseModel):
    video_url: str
    audio_url: str
    offset: float = 2.5

class TTSRequest(BaseModel):
    text: str
    voice: str = "vi-VN-HoaiMyNeural"
    rate: str = "+0%"
    volume: str = "+0%"
    pitch: str = "+0Hz"
    target_duration: float = None  # truyền vào để tính rate động
class AudioRequest(BaseModel):
    audio_url: str