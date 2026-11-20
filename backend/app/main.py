"""FastAPI Main Application Entrypoint."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import logger
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Initializing AirGuard AI Database tables...")
    init_db()
    logger.info("AirGuard AI Platform successfully started.")
    yield
    logger.info("AirGuard AI shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Real-World Environmental Intelligence & Urban Air Quality Assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["System"])
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "operational",
        "documentation": "/docs",
        "version": "1.0.0",
    }
