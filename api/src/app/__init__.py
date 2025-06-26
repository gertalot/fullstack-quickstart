from dotenv import load_dotenv
load_dotenv()
import time
import os
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
from .db import Base, get_engine
from . import models
from .auth import auth_router

start_time = time.time()

router = APIRouter()

@router.get("/healthcheck")
def healthcheck():
    uptime_seconds = int(time.time() - start_time)
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return {
        "message": "Savour Herbs API is healthy!",
        "uptime": {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
        },
    }

@asynccontextmanager
async def lifespan(app):
    engine = get_engine()
    Base.metadata.create_all(engine)
    yield

my_app = FastAPI(lifespan=lifespan)
my_app.add_middleware(SessionMiddleware, secret_key=os.environ.get("SESSION_SECRET_KEY", "dummy-session-secret"))
allow_origins = [o.strip() for o in os.environ.get("ALLOW_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
my_app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
my_app.include_router(router, prefix="/api/v1")
my_app.include_router(auth_router, prefix="/api/v1")

