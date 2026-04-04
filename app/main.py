from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.controllers import media_controller, tts_controller, merge_controller, file_controller
from app.utils.logger import setup_logging
from app.utils.context import set_request_id
from contextlib import asynccontextmanager
import asyncio, os, time, logging, uuid

# Initialize premium logging
logger_listener = setup_logging()
logging.info("FastAPI Application Starting...")

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
    # Stop the logger listener on shutdown
    logger_listener.stop()

app = FastAPI(lifespan=lifespan)

# Middleware to manage the Request ID context
@app.middleware("http")
async def log_request_id_middleware(request: Request, call_next):
    # Try to get existing ID from header or generate new one
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    
    # Store in context
    token = set_request_id(request_id)
    try:
        response = await call_next(request)
        # Also return the ID in response headers for easier client-side tracking
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        # Context is automatically handled by contextvars in async, 
        # but cleanup is good practice if we used tokens
        pass

os.makedirs("./tmp", exist_ok=True)

app.include_router(tts_controller.router)
app.include_router(merge_controller.router)
app.include_router(file_controller.router)
app.include_router(media_controller.router)