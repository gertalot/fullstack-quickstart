import time
from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

start_time = time.time()

router = APIRouter()

@router.get("/healthcheck")
def healthcheck():
    uptime_seconds = int(time.time() - start_time)
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime = {
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
    }
    return {
        "message": "Savour Herbs API is healthy!",
        "uptime": uptime,
    }

app = FastAPI()

# Read allowed origins from environment variable, default to localhost:3000
allow_origins = os.environ.get("ALLOW_ORIGINS", "http://localhost:3000").split(",")
allow_origins = [origin.strip() for origin in allow_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

