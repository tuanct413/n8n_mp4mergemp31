import subprocess
import requests
import random
import glob

MUSIC_DIR = "./app/assets/music"

import re
from datetime import datetime, timedelta

def shift_srt_timestamps(srt_content, offset_seconds):
    def shift_time(match):
        time_str = match.group(0)
        sep = ',' if ',' in time_str else '.'
        try:
            dt = datetime.strptime(time_str.replace('.', ','), "%H:%M:%S,%f")
            dt += timedelta(seconds=offset_seconds)
            return dt.strftime(f'%H:%M:%S{sep}%f')[:-3]
        except Exception:
            return time_str
            
    pattern = r"\d{2}:\d{2}:\d{2}[,\.]\d{3}"
    return re.sub(pattern, shift_time, srt_content)

def merge_video_audio(video_url, audio_url, offset, video_file, audio_file, output_file, ffmpeg_path, subtitle_url=None, subtitle_color="&H00FFFFFF"):
    headers = {"User-Agent": "Mozilla/5.0"}

    with requests.get(video_url, headers=headers, stream=True, timeout=30) as r:
        r.raise_for_status()
        with open(video_file, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                f.write(chunk)

    with requests.get(audio_url, headers=headers, stream=True, timeout=30) as r:
        r.raise_for_status()
        with open(audio_file, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                f.write(chunk)

    vf_filter = None
    if subtitle_url:
        import uuid
        srt_shifted = f"tmp/{uuid.uuid4()}_shifted.srt"
        with requests.get(subtitle_url, headers=headers, timeout=10) as r:
            r.raise_for_status()
            srt_content = r.text
        
        if offset > 0:
            srt_content = shift_srt_timestamps(srt_content, offset)
            
        with open(srt_shifted, "w", encoding="utf-8") as f:
            f.write(srt_content)
            
        # Add basic styling to the ffmpeg filter using clean relative path
        vf_filter = f"subtitles={srt_shifted}:force_style='FontSize=24,PrimaryColour={subtitle_color},Alignment=2'"

    # random nhạc nền
    music_files = glob.glob(f"{MUSIC_DIR}/*.mp3")
    music_file = random.choice(music_files) if music_files else None

    cmd = [
        ffmpeg_path, "-y",
        "-i", video_file,
        "-itsoffset", str(offset),
        "-i", audio_file
    ]

    if music_file:
        cmd.extend([
            "-stream_loop", "-1", "-i", music_file,
            "-map", "0:v:0",
            "-filter_complex", "[1:a][2:a]amix=inputs=2:duration=first:weights=3 0.3[aout]",
            "-map", "[aout]"
        ])
    else:
        cmd.extend([
            "-map", "0:v:0",
            "-map", "1:a:0"
        ])

    if vf_filter:
        cmd.extend(["-vf", vf_filter])
        # burning subtitles requires re-encoding the video
        cmd.extend(["-c:v", "libx264"])
    else:
        cmd.extend(["-c:v", "copy"])

    cmd.extend([
        "-c:a", "aac",
        "-shortest",
        output_file
    ])

    return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')