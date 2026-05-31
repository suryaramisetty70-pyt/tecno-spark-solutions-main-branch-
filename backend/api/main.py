"""
Buddy AI Operating System - FastAPI Application Entry Point
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from config.settings import settings
from config.logging_config import setup_logging
from db.database import init_db, get_db_session
from core.buddy_core import BuddyCore

# Initialize logging
setup_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """FastAPI lifespan - startup and shutdown events"""
    # Startup
    logger.info("🚀 Buddy AI OS Backend starting up...")

    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")

    # Initialize Buddy Core
    buddy_core = BuddyCore()
    app.state.buddy_core = buddy_core
    logger.info("✅ Buddy Core initialized")

    logger.info("🎉 Buddy AI OS Backend ready!")

    yield

    # Shutdown
    logger.info("👋 Buddy AI OS Backend shutting down...")
    logger.info("✅ Cleanup complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title="Buddy AI Operating System API",
        description="Central intelligence for AI agent ecosystem",
        version="0.1.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # Security middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "version": "0.1.0",
            "environment": settings.ENVIRONMENT
        }

    # Add ready endpoint
    @app.get("/ready")
    async def readiness_check():
        """Readiness check endpoint"""
        # Check database connection
        try:
            async with get_db_session() as session:
                await session.execute("SELECT 1")
            return {"status": "ready"}
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return {"status": "not ready", "error": str(e)}, 503

    # Include API routes
    from api.v1 import auth, users, agents, workflows, integrations, notifications, admin, files, analytics, search
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(agents.router)
    app.include_router(workflows.router)
    app.include_router(integrations.router)
    app.include_router(notifications.router)
    app.include_router(admin.router)
    app.include_router(files.router)
    app.include_router(analytics.router)
    app.include_router(search.router)

    return app


# Create FastAPI application with lifespan
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
