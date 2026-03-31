from fastapi import FastAPI
from app.controllers import media_controller, tts_controller, merge_controller, file_controller
from contextlib import asynccontextmanager
import asyncio, os, time

async def clean_tmp():
    while True:
        await asyncio.sleep(600)  # chạy mỗi 10 phút
        for f in os.listdir("./tmp"):
            path = f"./tmp/{f}"
            try:
                if time.time() - os.path.getmtime(path) > 600:
                    os.remove(path)
            except Exception:
                pass

@asynccontextmanager
async def lifespan(app):
    asyncio.create_task(clean_tmp())
    yield

app = FastAPI(lifespan=lifespan)

os.makedirs("./tmp", exist_ok=True)

app.include_router(tts_controller.router)
app.include_router(merge_controller.router)
app.include_router(file_controller.router)
app.include_router(media_controller.router)