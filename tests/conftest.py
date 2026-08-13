"""
Shared test fixtures.

Tests run against an in-memory SQLite DB rather than Postgres: fast, needs
no running container, and our models/queries avoid Postgres-only features
(the one enum column works fine under SQLite too), so it's a faithful
enough substitute for testing business logic in the service layer.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - registers all models on Base.metadata
from app.core.security import create_access_token, hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app as fastapi_app
from app.models.user import User


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


@pytest.fixture()
def client(db_session):
    """TestClient wired to the same in-memory session as `db_session`, so a
    test can set up rows via `db_session` and then hit the API and see them
    -- `get_current_user` isn't overridden here, so it still resolves
    through this same override, exercising the real auth dependency chain
    (deps.py + security.py) rather than bypassing it."""

    def _get_db_override():
        yield db_session

    fastapi_app.dependency_overrides[get_db] = _get_db_override
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(db_session):
    """A real persisted user + a real signed JWT for it, as a ready-to-use
    Authorization header for hitting protected routes."""
    user = User(username="testuser", hashed_password=hash_password("testpass"))
    db_session.add(user)
    db_session.commit()
    token = create_access_token(subject=user.username)
    return {"Authorization": f"Bearer {token}"}
