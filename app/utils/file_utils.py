# app/utils/file_utils.py
import os

def cleanup(*files):
    for file in files:
        try:
            if os.path.exists(file):
                os.remove(file)
        except Exception:
            pass