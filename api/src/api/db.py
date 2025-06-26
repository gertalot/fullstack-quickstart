"""
Database setup for Savour Herbs backend.
Defines engine, sessionmaker, and declarative base for SQLAlchemy ORM.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

def get_engine(db_url: str | None = None):
    if db_url is None:
        db_url = os.environ.get("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/savour")
    return create_engine(db_url, echo=False, future=True)

def get_session(engine) -> Session:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)() 