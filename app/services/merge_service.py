import subprocess
import requests
import random
import glob

MUSIC_DIR = "./app/assets/music"

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

    # random nhạc nền
    music_files = glob.glob(f"{MUSIC_DIR}/*.mp3")
    music_file = random.choice(music_files) if music_files else None

    if music_file:
        cmd = [
            ffmpeg_path, "-y",
            "-i", video_file,
            "-itsoffset", str(offset),
            "-i", audio_file,
            "-stream_loop", "-1", "-i", music_file,
            "-map", "0:v:0",
            "-filter_complex", "[1:a][2:a]amix=inputs=2:duration=first:weights=3 0.3[aout]",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_file
        ]
    else:
        # không có nhạc nền thì merge bình thường
        cmd = [
            ffmpeg_path, "-y",
            "-i", video_file,
            "-itsoffset", str(offset),
            "-i", audio_file,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_file
        ]

    return subprocess.run(cmd, capture_output=True, text=True)