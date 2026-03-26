import subprocess
import requests

def merge_video_audio(video_url, audio_url, offset, video_file, audio_file, output_file, ffmpeg_path):

    headers = {"User-Agent": "Mozilla/5.0"}

    with requests.get(video_url, headers=headers, stream=True, timeout=30) as r:
        with open(video_file, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                f.write(chunk)

    with requests.get(audio_url, headers=headers, stream=True, timeout=30) as r:
        with open(audio_file, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                f.write(chunk)

    result = subprocess.run([
        ffmpeg_path,
        "-y",
        "-i", video_file,
        "-itsoffset", str(offset),
        "-i", audio_file,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        output_file
    ], capture_output=True, text=True)

    return result