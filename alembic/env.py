"""Alembic environment: wires migrations to our app's settings and models
instead of a hardcoded URL, and enables autogenerate by exposing our
Base.metadata."""
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Import the app's models package so every model is registered on
# Base.metadata before Alembic compares it against the DB schema.
from app.core.config import get_settings
from app.db.base import Base
import app.models  # noqa: F401  (import for side effect: registers models)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Point Alembic at our real DB URL (from env vars via pydantic-settings)
# rather than whatever's in alembic.ini, so there's a single source of truth.
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Generate SQL scripts without a live DB connection (`alembic upgrade
    --sql`), useful for review before applying in restricted environments."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Normal path: connect to the DB and apply migrations directly."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
