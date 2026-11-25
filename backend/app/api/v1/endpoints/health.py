"""Health, readiness, and database diagnostic probes."""

from datetime import datetime, timezone
from fastapi import APIRouter
from app.db.session import check_database_readiness

router = APIRouter()


@router.get("/health", tags=["System"])
async def health_check():
    """Liveness probe reporting system uptime and database connectivity."""
    db_health = await check_database_readiness()
    return {
        "status": "online",
        "service": "AirGuard AI Engine",
        "database": "healthy" if db_health["connected"] else "unhealthy",
        "postgis_enabled": db_health["postgis_installed"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0",
    }


@router.get("/health/db", tags=["System"])
async def database_health_check():
    """Detailed diagnostic probe for database dialect, driver, and PostGIS extension status."""
    db_health = await check_database_readiness()
    return {
        "status": "ready" if db_health["connected"] else "unavailable",
        "details": db_health,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
