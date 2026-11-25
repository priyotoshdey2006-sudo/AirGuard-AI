"""Alembic environment configuration supporting both asyncpg (PostgreSQL) and SQLite."""

import asyncio
import os
import sys
from logging.config import fileConfig
from sqlalchemy import pool
from alembic import context

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.db.base import Base
from app.db.session import async_engine, engine, get_sync_database_url
import app.models.aqi_cache  # noqa: F401
import app.models.aqi_record  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

if settings.DATABASE_URL.startswith("sqlite"):
    config.set_main_option("sqlalchemy.url", get_sync_database_url(settings.DATABASE_URL))
else:
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations asynchronously using SQLAlchemy 2.0 AsyncEngine (asyncpg)."""
    async with async_engine.connect() as connection:
        await connection.run_sync(do_run_migrations)


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Uses asyncpg via run_async_migrations for PostgreSQL, and standard sync connection for SQLite.
    """
    if settings.DATABASE_URL.startswith("sqlite"):
        with engine.connect() as connection:
            do_run_migrations(connection)
    else:
        asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
