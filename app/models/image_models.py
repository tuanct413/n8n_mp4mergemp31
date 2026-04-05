from pydantic import BaseModel
from typing import Optional

class ImageMergeRequest(BaseModel):
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    scale: Optional[float] = 0.2  # Logo size relative to image height
    auto_position: Optional[bool] = True
    position_ratio: Optional[tuple[float, float]] = None  # (x, y) relative to bottom-right, used if auto_position is False
    padding: Optional[int] = 20
