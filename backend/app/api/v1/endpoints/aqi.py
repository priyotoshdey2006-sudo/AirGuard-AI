"""Air Quality monitoring, forecast, and indoor guidance endpoints."""

from fastapi import APIRouter, Query
from app.schemas.aqi import (
    CurrentAQIResponse,
    ForecastAQIResponse,
    IndoorGuidanceRequest,
    IndoorGuidanceResponse,
)
from app.services.open_meteo import open_meteo_service
from app.services.recommendation import recommendation_service

router = APIRouter()


@router.get("/current", response_model=CurrentAQIResponse, tags=["Air Quality"])
async def get_current_air_quality(
    lat: float = Query(28.6139, ge=-90.0, le=90.0, description="Latitude"),
    lon: float = Query(77.2090, ge=-180.0, le=180.0, description="Longitude"),
):
    """Retrieve real-time observed pollutant metrics (PM2.5, PM10, O3, NO2, SO2, CO, UV, AQI)."""
    return await open_meteo_service.get_current_aqi(lat=lat, lon=lon)


@router.get("/forecast", response_model=ForecastAQIResponse, tags=["Air Quality"])
async def get_air_quality_forecast(
    lat: float = Query(28.6139, ge=-90.0, le=90.0, description="Latitude"),
    lon: float = Query(77.2090, ge=-180.0, le=180.0, description="Longitude"),
):
    """Retrieve 24-hour diurnal curve and 7-day projection."""
    return await open_meteo_service.get_forecast(lat=lat, lon=lon)


@router.post("/indoor-guidance", response_model=IndoorGuidanceResponse, tags=["Indoor Air Quality"])
async def calculate_indoor_guidance(payload: IndoorGuidanceRequest):
    """Calculate indoor air quality estimates, HEPA runtime, and ventilation windows."""
    return await recommendation_service.get_indoor_guidance(payload)


@router.get("/indoor-guidance", response_model=IndoorGuidanceResponse, tags=["Indoor Air Quality"])
async def get_indoor_guidance_query(
    lat: float = Query(28.6139, ge=-90.0, le=90.0),
    lon: float = Query(77.2090, ge=-180.0, le=180.0),
    room_sqft: float = Query(350.0, ge=50.0, le=10000.0),
    has_hepa_filter: bool = Query(True),
    has_ac: bool = Query(True),
    building_seal_quality: str = Query("standard"),
):
    """Convenience GET endpoint for calculating indoor air quality advisories."""
    req = IndoorGuidanceRequest(
        latitude=lat,
        longitude=lon,
        room_sqft=room_sqft,
        has_hepa_filter=has_hepa_filter,
        has_ac=has_ac,
        building_seal_quality=building_seal_quality,
    )
    return await recommendation_service.get_indoor_guidance(req)
