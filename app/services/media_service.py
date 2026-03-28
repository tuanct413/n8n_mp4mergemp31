import subprocess
import requests
import tempfile

import subprocess
import requests
import tempfile

class MediaService:

    @staticmethod
    def get_audio_duration(audio_url: str) -> float:
        # tải file về tạm
        r = requests.get(audio_url)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(r.content)
            path = f.name

        # gọi ffprobe
        result = subprocess.run(
            [
                "ffprobe",
                "-i", path,
                "-show_entries", "format=duration",
                "-v", "quiet",
                "-of", "csv=p=0"
            ],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        duration = float(result.stdout.strip())
        return duration