from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
import subprocess
import requests
import uuid
import os

app = FastAPI()

FFMPEG_PATH = "ffmpeg"

# ✅ request model (không bị KeyError nữa)
class MergeRequest(BaseModel):
    video_url: str
    audio_url: str
    offset: float = 2.5  # default nếu không truyền

@app.post("/merge")
def merge(data: MergeRequest):
    video_url = data.video_url
    audio_url = data.audio_url
    offset = data.offset

    # 🔥 file tạm random (tránh crash)
    video_file = f"/tmp/{uuid.uuid4()}.mp4"
    audio_file = f"/tmp/{uuid.uuid4()}.mp3"
    output_file = f"/tmp/{uuid.uuid4()}.mp4"

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        # 📥 download video (stream)
        with requests.get(video_url, headers=headers, stream=True) as r:
            with open(video_file, "wb") as f:
                for chunk in r.iter_content(1024 * 1024):
                    f.write(chunk)

        # 📥 download audio (stream)
        with requests.get(audio_url, headers=headers, stream=True) as r:
            with open(audio_file, "wb") as f:
                for chunk in r.iter_content(1024 * 1024):
                    f.write(chunk)

        # ⚡ merge nhanh + giữ offset
        result = subprocess.run([
            FFMPEG_PATH,
            "-y",

            "-i", video_file,

            "-itsoffset", str(offset),
            "-i", audio_file,

            "-map", "0:v:0",
            "-map", "1:a:0",

            "-c:v", "copy",   # ⚡ KHÔNG encode lại → nhanh
            "-c:a", "aac",

            "-shortest",
            output_file
        ], capture_output=True, text=True)

        if result.returncode != 0:
            return {"error": result.stderr}

        # 📤 trả file + xoá sau khi gửi xong
        return FileResponse(
            output_file,
            media_type="video/mp4",
            filename="output.mp4",
            background=lambda: cleanup(video_file, audio_file, output_file)
        )

    except Exception as e:
        return {"error": str(e)}


# 🧹 xoá file sau khi xong
def cleanup(*files):
    for f in files:
        try:
            if os.path.exists(f):
                os.remove(f)
        except:
            pass