#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
InteractRadar - Main Application

Campaign-based Twitter engagement automation system.
Finds seed users, maps interactions, filters posts, and auto-replies with tracked links.
"""

import uvicorn
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Generator, Any
from datetime import datetime
import os

from utils.config import get_config_manager
from utils.logging_config import setup_logging
from middleware.request_middleware import RequestMiddleware

from api.campaigns import router as campaigns_router
from api.analytics import router as analytics_router
from api.tracking import router as tracking_router
from api.settings import router as settings_router

from modules.integrations.twitter_adapter import TwitterAdapter
from modules.campaign.campaign_manager import CampaignManager
from modules.campaign.interaction_mapper import InteractionMapper
from modules.campaign.post_filter import PostFilter
from modules.campaign.auto_replier import AutoReplier
from modules.tracking.link_shortener import LinkShortener
from modules.tracking.analytics_collector import AnalyticsCollector
from modules.scheduler.task_scheduler import TaskScheduler
from modules.scheduler.rate_limiter import RateLimiter

from database.mongodb import get_database

config_manager = get_config_manager()
config = config_manager.get_config_dict()
logger = setup_logging(config)


class ApplicationLifecycleManager:
    """Manages the application lifecycle for InteractRadar."""

    def __init__(self, app: FastAPI) -> None:
        self.app = app
        self.logger = logging.getLogger(__name__)
        self.startup_time = None

    async def startup(self) -> None:
        """Initialize all application services."""
        self.startup_time = datetime.now()
        self.logger.info("🚀 Starting InteractRadar initialization")

        try:
            # Initialize database
            self.logger.info("Initializing database connection")
            self.app.state.db = await get_database()

            # Initialize Twitter adapter with cookie authentication
            self.logger.info("Initializing Twitter adapter")
            self.app.state.twitter_adapter = TwitterAdapter()

            # Load cookies from file
            cookie_file = os.path.join(os.path.dirname(__file__), "cookie.json")
            if os.path.exists(cookie_file):
                auth_success = await self.app.state.twitter_adapter.initialize_from_file(cookie_file)
                if auth_success:
                    self.logger.info("✅ Twitter authentication successful")
                else:
                    self.logger.warning("⚠️  Twitter authentication failed - some features may not work")
            else:
                self.logger.warning(f"⚠️  Cookie file not found at {cookie_file}")
                self.logger.warning("   Please create cookie.json to enable Twitter features")

            # Initialize tracking modules
            self.logger.info("Initializing tracking modules")
            self.app.state.link_shortener = LinkShortener(db_client=self.app.state.db)
            self.app.state.analytics_collector = AnalyticsCollector(db_client=self.app.state.db)

            # Initialize campaign modules
            self.logger.info("Initializing campaign modules")
            self.app.state.campaign_manager = CampaignManager(
                db_client=self.app.state.db,
                twitter_adapter=self.app.state.twitter_adapter
            )

            # Initialize scheduler
            self.logger.info("Initializing task scheduler")
            self.app.state.task_scheduler = TaskScheduler(
                db_client=self.app.state.db,
                campaign_manager=self.app.state.campaign_manager
            )

            # Start the scheduler
            self.app.state.task_scheduler.start()

            startup_duration = (datetime.now() - self.startup_time).total_seconds()
            self.logger.info(
                f"✅ InteractRadar started successfully in {startup_duration:.2f}s"
            )

        except Exception as e:
            self.logger.critical(f"❌ Critical startup failure: {e}", exc_info=True)
            raise SystemExit(1) from e

    async def shutdown(self) -> None:
        """Gracefully shutdown all application services."""
        shutdown_start = datetime.now()
        self.logger.info("🛑 Starting graceful shutdown of InteractRadar")

        try:
            # Stop the scheduler
            if hasattr(self.app.state, 'task_scheduler'):
                self.logger.info("Stopping task scheduler")
                self.app.state.task_scheduler.stop()

            shutdown_duration = (datetime.now() - shutdown_start).total_seconds()
            self.logger.info(f"✅ Shutdown completed in {shutdown_duration:.2f}s")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> Generator[None, Any, None]:
    """FastAPI lifespan context manager for startup and shutdown."""
    lifecycle_manager = ApplicationLifecycleManager(app)

    await lifecycle_manager.startup()

    yield

    await lifecycle_manager.shutdown()


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app_config = config_manager.get_app_config()

    app = FastAPI(
        title="InteractRadar",
        description="Campaign-based Twitter engagement automation system",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )

    _configure_middleware(app)
    _configure_routes(app)
    _configure_exception_handlers(app)

    return app


def _configure_middleware(app: FastAPI) -> None:
    """Configure application middleware."""
    cors_config = config_manager.get_cors_config()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config.origins,
        allow_credentials=cors_config.allow_credentials,
        allow_methods=cors_config.allow_methods,
        allow_headers=cors_config.allow_headers,
    )

    app.add_middleware(RequestMiddleware)


def _configure_routes(app: FastAPI) -> None:
    """Configure application routes."""
    app.include_router(campaigns_router, prefix="/api/v1", tags=["Campaigns"])
    app.include_router(analytics_router, prefix="/api/v1", tags=["Analytics"])
    app.include_router(settings_router, prefix="/api/v1", tags=["Settings"])
    app.include_router(tracking_router, tags=["Tracking"])


def _configure_exception_handlers(app: FastAPI) -> None:
    """Configure global exception handlers."""

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Global exception handler for unhandled exceptions."""
        error_id = f"error_{int(datetime.now().timestamp())}"

        logger.error(
            f"Unhandled exception [{error_id}]: {str(exc)}",
            extra={
                "error_id": error_id,
                "path": request.url.path,
                "method": request.method
            }
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "error_id": error_id,
                "message": str(exc) if config_manager.is_development() else "An error occurred"
            }
        )


app = create_application()


@app.get("/", tags=["System"])
async def root():
    """Root endpoint with system information."""
    return {
        "name": "InteractRadar",
        "status": "online",
        "version": "1.0.0",
        "description": "Campaign-based Twitter engagement automation",
        "endpoints": {
            "campaigns": "/api/v1/campaigns",
            "analytics": "/api/v1/analytics",
            "tracking": "/r/{short_code}",
            "docs": "/docs"
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    try:
        # Check database
        if hasattr(app.state, 'db'):
            await app.state.db.command("ping")
            db_status = "operational"
        else:
            db_status = "offline"

        # Check Twitter
        twitter_status = "operational" if (
            hasattr(app.state, 'twitter_adapter') and
            app.state.twitter_adapter.is_authenticated
        ) else "offline"

        # Check scheduler
        scheduler_status = "operational" if (
            hasattr(app.state, 'task_scheduler') and
            app.state.task_scheduler.is_running
        ) else "offline"

        return {
            "status": "operational",
            "services": {
                "database": db_status,
                "twitter": twitter_status,
                "scheduler": scheduler_status
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def configure_uvicorn_logging() -> None:
    """Configure uvicorn logging."""
    uvicorn_loggers = [
        "uvicorn", "uvicorn.error", "uvicorn.access",
        "starlette", "fastapi"
    ]

    for logger_name in uvicorn_loggers:
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.setLevel(logging.WARNING)


def main() -> None:
    """Main entry point for the application."""
    app_config = config_manager.get_app_config()

    logger.info(
        f"Starting InteractRadar",
        extra={
            "version": "1.0.0",
            "environment": app_config.environment,
            "host": app_config.host,
            "port": app_config.port
        }
    )

    configure_uvicorn_logging()

    uvicorn.run(
        "main:app",
        host=app_config.host,
        port=app_config.port,
        reload=app_config.debug and app_config.environment == "development",
        log_config=None,
        access_log=False,
        workers=1  # Single worker for scheduler
    )


if __name__ == "__main__":
    main()
