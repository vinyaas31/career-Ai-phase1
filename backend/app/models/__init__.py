"""
Import every model here. Alembic's env.py imports this package to make
sure all tables are registered on Base.metadata before autogenerating
migrations -- a model that isn't imported here will be invisible to
`alembic revision --autogenerate`.
"""

from app.models.user import User, UserProfile  # noqa: F401
