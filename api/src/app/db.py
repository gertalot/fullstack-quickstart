"""
Database setup for Savour Herbs backend.
Defines engine, sessionmaker, and declarative base for SQLAlchemy ORM.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from dotenv import load_dotenv

load_dotenv()

class Base(DeclarativeBase):
    pass

def get_engine(db_url: str | None = None):
    if db_url is None:
        db_url = os.environ.get("DATABASE_URL")
        if not db_url:
            raise RuntimeError(
                "DATABASE_URL environment variable is not set. "
                "Please set DATABASE_URL to a valid SQLAlchemy database URL (e.g., postgresql+psycopg2://user:pass@host:port/db)."
            )
    return create_engine(db_url, echo=False, future=True)

def get_session(engine) -> Session:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)() 