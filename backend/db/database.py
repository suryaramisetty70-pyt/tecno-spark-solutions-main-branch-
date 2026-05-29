"""
Database configuration and setup for Buddy AI OS
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import logging
import os

logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://buddy_user:buddy_password@localhost/buddy_ai_db"
)

# For async operations
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    future=True,
    poolclass=NullPool if os.getenv("ENV") == "test" else None,
)

# Create async session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

# For synchronous operations (migrations)
SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "") if "+asyncpg" in DATABASE_URL else DATABASE_URL
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=False,
    future=True,
)

sync_session_maker = async_sessionmaker(sync_engine, expire_on_commit=False)


async def init_db() -> None:
    """Initialize database and create all tables"""
    try:
        logger.info("Initializing database...")
        from db.models import Base

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
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
    logger.info("✅ Database connection closed")

