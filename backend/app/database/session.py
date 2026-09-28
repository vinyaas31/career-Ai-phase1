"""
Database engine and session management.

`get_db` is a FastAPI dependency: any route that needs database access
declares `db: Session = Depends(get_db)` in its function signature, and
FastAPI handles opening/closing the session automatically per-request.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
