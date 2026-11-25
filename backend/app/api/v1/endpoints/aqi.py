"""Air Quality monitoring, model proxy, diurnal forecast, and geospatial nearby queries."""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.logging import logger
from app.db.session import get_async_db
from app.schemas.aqi import CurrentAQIResponse, ForecastAQIResponse
from app.schemas.spatial import NearbyAQIResponse, QueryLocationMetadata
from app.services.aqi_persistence import aqi_persistence_service
from app.services.open_meteo import open_meteo_service, _parse_to_utc

router = APIRouter()


@router.get("/current", response_model=CurrentAQIResponse, tags=["Air Quality"])
async def get_current_air_quality(
    lat: float = Query(28.6139, ge=-90.0, le=90.0, description="Latitude between -90 and 90"),
    lon: float = Query(77.2090, ge=-180.0, le=180.0, description="Longitude between -180 and 180"),
    db: AsyncSession = Depends(get_async_db),
):
    """Retrieve real-time atmospheric model analysis with CPCB & US EPA proxies, WHO benchmark comparison, and provenance."""
    result = await open_meteo_service.get_current_aqi(lat=lat, lon=lon)
    try:
        await aqi_persistence_service.persist_current_aqi(db, result)
    except Exception as exc:
        logger.warning(f"Could not persist AQI model record to database: {exc}")
    return result


@router.get("/forecast", response_model=ForecastAQIResponse, tags=["Air Quality"])
async def get_air_quality_forecast(
    lat: float = Query(28.6139, ge=-90.0, le=90.0, description="Latitude between -90 and 90"),
    lon: float = Query(77.2090, ge=-180.0, le=180.0, description="Longitude between -180 and 180"),
):
    """Retrieve 24-hour diurnal forward model atmospheric projection."""
    return await open_meteo_service.get_forecast(lat=lat, lon=lon)


@router.get("/nearby", response_model=NearbyAQIResponse, tags=["Geospatial Air Quality"])
async def get_nearby_air_quality(
    lat: float = Query(..., ge=-90.0, le=90.0, description="Latitude between -90 and 90"),
    lon: float = Query(..., ge=-180.0, le=180.0, description="Longitude between -180 and 180"),
    radius_km: float = Query(
        settings.DEFAULT_NEARBY_RADIUS_KM,
        gt=0.0,
        le=settings.MAX_NEARBY_RADIUS_KM,
        description="Search radius in kilometers (max 250 km)",
    ),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of nearby grid points to return"),
    target_time_utc: Optional[str] = Query(
        None,
        description="Optional ISO 8601 UTC timestamp to evaluate (defaults to current system time)",
    ),
    include_forecast: bool = Query(
        False,
        description="Whether to include future model forecast records beyond target_time (default False strictly queries current valid conditions)",
    ),
    db: AsyncSession = Depends(get_async_db),
):
    """Query nearby atmospheric model grid points using PostGIS distance queries.

    Scientific Constraint:
    - Coordinates represent model grid centroids (native resolution ~0.4° / ~45 km).
    - Distances are computed to model grid centroids, NOT to physical sensor stations.
    - Furthest-future forecast records are strictly excluded when querying current conditions (include_forecast=False).
    """
    eval_dt = _parse_to_utc(target_time_utc) if target_time_utc else datetime.now(timezone.utc)

    nearby_records = await aqi_persistence_service.query_nearby_grids(
        session=db,
        latitude=lat,
        longitude=lon,
        radius_km=radius_km,
        limit=limit,
        target_time_utc=eval_dt,
        include_forecast=include_forecast,
    )

    items = [
        aqi_persistence_service.record_to_grid_item(rec, dist, evaluation_time=eval_dt)
        for rec, dist in nearby_records
    ]

    message = (
        f"Found {len(items)} atmospheric model grid centroid(s) within {radius_km} km."
        if items
        else f"No atmospheric model data available within {radius_km} km of the requested location ({lat}, {lon})."
    )

    return NearbyAQIResponse(
        query_location=QueryLocationMetadata(
            query_latitude=lat,
            query_longitude=lon,
            search_radius_km=radius_km,
        ),
        total_matching_grids=len(items),
        evaluation_time_utc=eval_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        include_forecast=include_forecast,
        items=items,
        message=message,
    )
