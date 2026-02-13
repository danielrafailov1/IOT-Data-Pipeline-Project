import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


def _resolve_database_url() -> str:
    """Prefer DATABASE_URL env (Render, etc.) over config."""
    url = (
        os.environ.get("DATABASE_URL")
        or os.environ.get("INTERNAL_DATABASE_URL")
        or os.environ.get("POSTGRES_URL")
    )
    if url:
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url
    from app.core.config import get_settings
    return get_settings().database_url


_db_url = _resolve_database_url()
_connect_args = {"check_same_thread": False} if "sqlite" in _db_url else {}
engine = create_engine(_db_url, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
