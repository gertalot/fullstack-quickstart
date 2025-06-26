import time
from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
import os

load_dotenv()

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from .db import Base, get_engine
from . import models  # Ensure all models are imported
from .auth import auth_router

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

my_app = FastAPI()

# Add session middleware for OAuth state
session_secret = os.environ.get("SESSION_SECRET_KEY", "dummy-session-secret")
my_app.add_middleware(SessionMiddleware, secret_key=session_secret)

# Read allowed origins from environment variable, default to localhost:3000
allow_origins = os.environ.get("ALLOW_ORIGINS", "http://localhost:3000").split(",")
allow_origins = [origin.strip() for origin in allow_origins if origin.strip()]

my_app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

my_app.include_router(router, prefix="/api/v1")
my_app.include_router(auth_router, prefix="/api/v1")

@my_app.on_event("startup")
def ensure_schema():
    engine = get_engine()
    Base.metadata.create_all(engine)

