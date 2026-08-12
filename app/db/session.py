"""
SQLAlchemy engine and session factory.

A single module-level engine is created (SQLAlchemy engines are meant to be
long-lived and shared, not re-created per request), and `get_db` is a
FastAPI dependency that hands each request its own Session, closing it
afterward so connections always get returned to the pool.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()

# pool_pre_ping avoids handing out dead connections after e.g. the Postgres
# container restarts or an idle connection is dropped by a proxy.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """FastAPI dependency: yield a DB session per-request, always closing it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
