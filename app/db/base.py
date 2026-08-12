"""
Declarative base shared by all ORM models.

Kept in its own module (rather than in models/__init__.py) to avoid circular
imports: models import `Base` from here, and Alembic's env.py imports
`app.models` (which imports every model) plus `Base.metadata` from here.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
