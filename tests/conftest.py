"""
Shared test fixtures.

Tests run against an in-memory SQLite DB rather than Postgres: fast, needs
no running container, and our models/queries avoid Postgres-only features
(the one enum column works fine under SQLite too), so it's a faithful
enough substitute for testing business logic in the service layer.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
import app.models  # noqa: F401 - registers all models on Base.metadata


@pytest.fixture()
def db_session():
    # StaticPool + check_same_thread=False: keep a single SQLite connection
    # alive for the whole test (an in-memory DB disappears if the
    # connection closes), shared safely since tests are single-threaded.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
