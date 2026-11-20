"""Database engine and session management."""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import settings

db_url = settings.DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://")
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    db_url,
    echo=False,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a scoped database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables if they do not exist."""
    from app.db.base import Base
    import app.models.user  # noqa: F401
    import app.models.aqi_cache  # noqa: F401
    import app.models.community_report  # noqa: F401
    import app.models.travel_log  # noqa: F401
    import app.models.chat_history  # noqa: F401

    Base.metadata.create_all(bind=engine)
