from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter()

BASE_DIR = "./tmp"

@router.get("/files/{filename}")
def get_file(filename: str):
    file_path = os.path.join(BASE_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)