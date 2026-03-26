from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter()

BASE_DIR = "./tmp"

@router.get("/files/{filename}")
def get_file(filename: str):
    file_path = os.path.join(BASE_DIR, filename)

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    return FileResponse(file_path)