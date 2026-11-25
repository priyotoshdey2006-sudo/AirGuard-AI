"""FastAPI Main Application Entrypoint for AirGuard AI."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import AirGuardException, UpstreamServiceUnavailableException
from app.core.logging import logger
from app.core.rate_limiter import SlidingWindowRateLimiter
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    if settings.ENVIRONMENT.lower() != "production":
        logger.info("Initializing AirGuard AI Database tables (local dev mode)...")
        init_db()
    else:
        logger.info("Production mode: automatic table creation disabled; schema is managed via Alembic migrations.")
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

# Exception Handler for Upstream Failures (HTTP 503)
@app.exception_handler(UpstreamServiceUnavailableException)
async def upstream_service_unavailable_handler(request: Request, exc: UpstreamServiceUnavailableException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "error_type": "UpstreamServiceUnavailable",
            "zero_fabrication_policy": "Enforced. No synthetic data generated.",
        },
    )

# Generic AirGuard custom exception handler
@app.exception_handler(AirGuardException)
async def airguard_exception_handler(request: Request, exc: AirGuardException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "error_type": exc.__class__.__name__,
        },
    )

# Exception handler for Pydantic input validation (HTTP 422)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "status_code": 422,
            "error_type": "ValidationError",
        },
    )

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount sliding-window rate limiter (60 requests/minute per client IP)
app.add_middleware(
    SlidingWindowRateLimiter,
    max_requests=settings.RATE_LIMIT_PER_MINUTE if hasattr(settings, "RATE_LIMIT_PER_MINUTE") else 60,
    window_seconds=60,
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


@app.get("/health", tags=["System"])
async def root_health():
    """Root liveness probe returning system status."""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", getattr(settings, "PORT", 8000)))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)

