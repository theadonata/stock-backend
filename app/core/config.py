"""
Application configuration.

We use pydantic-settings so that every config value is read from environment
variables (with sane defaults only for local/dev convenience), validated at
startup, and typed everywhere else in the app rather than passed around as
raw strings pulled from os.environ ad hoc.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Loaded from a .env file when present (docker-compose injects real env
    # vars directly in containers; the .env file is a convenience for running
    # the app outside Docker, e.g. `uvicorn app.main:app` on a dev machine).
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Database ---
    # Full SQLAlchemy connection string, e.g.
    # postgresql+psycopg2://user:pass@host:5432/dbname
    DATABASE_URL: str = "postgresql+psycopg2://stock_hpp_user:stock_hpp_pass@localhost:5432/stock_hpp_db"

    # --- Auth / JWT ---
    # Secret used to sign JWTs. MUST be overridden with a real secret outside
    # local dev — the default here is intentionally obviously fake so nobody
    # mistakes it for something safe to ship.
    JWT_SECRET: str = "CHANGE_ME_INSECURE_DEV_ONLY_SECRET"
    JWT_ALGORITHM: str = "HS256"
    # How long an access token stays valid. Kept short-ish since this is a
    # single-role internal tool without refresh-token rotation yet.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12  # 12 hours — covers a work shift

    # --- App metadata ---
    PROJECT_NAME: str = "Stock/HPP Backend"
    API_V1_PREFIX: str = "/api/v1"

    # --- CORS ---
    # Comma-separated list of allowed origins for the frontend SPA. Kept
    # permissive-by-default for local dev; should be locked down via env var
    # in real deployments (stock-infrastructure sets this per environment).
    CORS_ORIGINS: str = "*"


@lru_cache
def get_settings() -> Settings:
    # Cached so we don't re-parse env vars on every request; Settings is
    # immutable for the lifetime of the process anyway.
    return Settings()
