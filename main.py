from fastapi import FastAPI
from fastapi.responses import FileResponse
import subprocess
import requests

app = FastAPI()

FFMPEG_PATH = "ffmpeg"

@app.post("/merge")
def merge(data: dict):
    video_url = data["video_url"]
    audio_url = data["audio_url"]

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # download video
    with open("video.mp4", "wb") as f:
        f.write(requests.get(video_url, headers=headers).content)

    # download audio
    with open("audio.mp3", "wb") as f:
        f.write(requests.get(audio_url, headers=headers).content)

    # 🔥 merge + fix sync
    result = subprocess.run([
    FFMPEG_PATH,
    "-y",

    "-fflags", "+genpts",

    "-i", "video.mp4",

    # 🔥 delay audio 3s
    "-itsoffset", "2.5",
    "-i", "audio.mp3",

    "-map", "0:v:0",
    "-map", "1:a:0",

    "-c:v", "libx264",
    "-c:a", "aac",

    "-shortest",
    "output.mp4"
    ], capture_output=True, text=True)

    if result.returncode != 0:
        return {
            "error": result.stderr
        }

    return FileResponse("output.mp4", media_type="video/mp4", filename="output.mp4")