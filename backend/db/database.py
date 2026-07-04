"""
Database configuration and setup for Buddy AI OS
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import logging
import os

logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./buddy_ai.db"  # SQLite for Windows development
)

# Engine kwargs - SQLite needs connect_args
engine_kwargs = {
    "echo": os.getenv("SQL_ECHO", "false").lower() == "true",
}

# Add SQLite specific configuration
if "sqlite" in DATABASE_URL:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    engine_kwargs["poolclass"] = NullPool
elif os.getenv("ENV") == "test":
    engine_kwargs["poolclass"] = NullPool

# For async operations
engine = create_async_engine(DATABASE_URL, **engine_kwargs)

# Create async session maker (SQLAlchemy 1.4 compatible)
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# For synchronous operations (migrations)
# Convert async database URL to sync for Alembic
if "sqlite" in DATABASE_URL:
    SYNC_DATABASE_URL = DATABASE_URL.replace("+aiosqlite", "")
elif "+asyncpg" in DATABASE_URL:
    SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")
else:
    SYNC_DATABASE_URL = DATABASE_URL

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in SYNC_DATABASE_URL else {}
)

sync_session_maker = sessionmaker(sync_engine, expire_on_commit=False)


async def init_db() -> None:
    """Initialize database and create all tables"""
    try:
        logger.info("Initializing database...")
        from db.models import Base

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session as dependency"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def close_db() -> None:
    """Close database connection"""
    await engine.dispose()
    logger.info("Database connection closed")
