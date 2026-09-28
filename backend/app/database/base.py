"""
Shared declarative base for all SQLAlchemy models.

Every model file in app/models/ must import `Base` from here and inherit
from it. Alembic's env.py imports Base.metadata to auto-detect tables
when generating migrations -- so a model that doesn't inherit from this
Base will silently never get a migration.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
