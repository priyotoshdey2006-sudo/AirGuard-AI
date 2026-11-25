"""Database engine, connection pooling, and session management for PostgreSQL+PostGIS and SQLite dev.

Supports:
1. SQLAlchemy 2.0 Async connectivity with `postgresql+asyncpg://` or `sqlite+aiosqlite:///`.
2. Connection pooling with pre-ping validation and bounded overflow for production reliability.
3. Synchronous compatibility engine for existing synchronous dependencies and Alembic.
4. Database health/readiness check with PostGIS extension validation.
5. Strict protection: never automatically executes `create_all()` in production environments.
"""

from typing import Any, AsyncGenerator, Dict, Generator
from sqlalchemy import create_engine, select, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import settings
from app.core.logging import logger


def get_async_database_url(url: str) -> str:
    """Ensure URL uses an asynchronous DBAPI driver."""
    if url.startswith("sqlite://") and not url.startswith("sqlite+aiosqlite://"):
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    if url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def get_sync_database_url(url: str) -> str:
    """Ensure URL uses a synchronous DBAPI driver."""
    if url.startswith("sqlite+aiosqlite://"):
        return url.replace("sqlite+aiosqlite://", "sqlite://", 1)
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return url


# Asynchronous Database Configuration
async_db_url = get_async_database_url(settings.DATABASE_URL)
async_connect_args: Dict[str, Any] = {}
async_engine_kwargs: Dict[str, Any] = {
    "echo": False,
    "pool_pre_ping": settings.DATABASE_POOL_PRE_PING,
}

if async_db_url.startswith("sqlite"):
    async_connect_args["check_same_thread"] = False
    async_engine_kwargs["connect_args"] = async_connect_args
else:
    # PostgreSQL / asyncpg connection pool parameters
    async_engine_kwargs["pool_size"] = settings.DATABASE_POOL_SIZE
    async_engine_kwargs["max_overflow"] = settings.DATABASE_MAX_OVERFLOW
    async_engine_kwargs["pool_recycle"] = 300

async_engine: AsyncEngine = create_async_engine(async_db_url, **async_engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# Synchronous Database Configuration (Backward compatibility & Alembic)
sync_db_url = get_sync_database_url(settings.DATABASE_URL)
sync_connect_args: Dict[str, Any] = {}
sync_engine_kwargs: Dict[str, Any] = {
    "echo": False,
    "pool_pre_ping": settings.DATABASE_POOL_PRE_PING,
}

engine = None
SessionLocal = None
if sync_db_url.startswith("sqlite"):
    sync_connect_args["check_same_thread"] = False
    sync_engine_kwargs["connect_args"] = sync_connect_args
    engine = create_engine(sync_db_url, **sync_engine_kwargs)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
else:
    try:
        engine = create_engine(sync_db_url, **sync_engine_kwargs)
        SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    except Exception:
        engine = None
        SessionLocal = None


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI async dependency yielding an AsyncSession."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


def get_db() -> Generator[Session, None, None]:
    """FastAPI sync dependency yielding a scoped Session."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def init_db() -> None:
    """Create tables if they do not exist (LOCAL DEV / TESTING ONLY).

    In production, database schema must be managed exclusively through Alembic migrations.
    """
    if settings.ENVIRONMENT.lower() == "production":
        logger.warning("Automatic table creation is blocked in production. Use Alembic migrations.")
        return

    from app.db.base import Base
    import app.models.aqi_cache  # noqa: F401
    import app.models.aqi_record  # noqa: F401

    Base.metadata.create_all(bind=engine)


async def check_database_readiness() -> Dict[str, Any]:
    """Execute a live probe of the database connection and verify PostGIS extension status."""
    readiness: Dict[str, Any] = {
        "connected": False,
        "dialect": async_engine.dialect.name,
        "driver": async_engine.dialect.driver,
        "postgis_installed": False,
        "postgis_version": None,
        "error": None,
    }

    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            readiness["connected"] = (result.scalar() == 1)

            if readiness["dialect"] == "postgresql":
                try:
                    postgis_ver = await conn.execute(text("SELECT PostGIS_Version()"))
                    ver_str = postgis_ver.scalar()
                    if ver_str:
                        readiness["postgis_installed"] = True
                        readiness["postgis_version"] = str(ver_str)
                except Exception as pg_err:
                    readiness["postgis_installed"] = False
                    readiness["postgis_error"] = str(pg_err)
    except Exception as exc:
        readiness["connected"] = False
        readiness["error"] = str(exc)

    return readiness
