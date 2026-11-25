"""Indoor Air Quality (IAQ) mass-balance screening and CADR evaluation endpoints."""

from fastapi import APIRouter, Query
from app.schemas.indoor import IndoorScreeningRequest, IndoorScreeningResponse
from app.services.indoor_estimator import calculate_indoor_screening
from app.services.open_meteo import open_meteo_service

router = APIRouter()


@router.post("/screening", response_model=IndoorScreeningResponse, tags=["Indoor Air Quality"])
async def run_indoor_screening(payload: IndoorScreeningRequest):
    """Calculate indoor PM2.5 scenario-based heuristic screening estimates, dynamic tau, and ACH."""
    # Fetch live outdoor PM2.5 from Open-Meteo model analysis
    aqi_data = await open_meteo_service.get_current_aqi(lat=payload.latitude, lon=payload.longitude)
    outdoor_pm25 = aqi_data.pollutants.pm2_5.concentration or 45.0

    result = calculate_indoor_screening(
        outdoor_pm2_5=outdoor_pm25,
        room_area_sqm=payload.room_area_sqm,
        ceiling_height_m=payload.ceiling_height_m,
        purifier_cadr_m3h=payload.purifier_cadr_m3h,
    )
    return IndoorScreeningResponse(**result)


@router.get("/screening", response_model=IndoorScreeningResponse, tags=["Indoor Air Quality"])
async def get_indoor_screening_query(
    lat: float = Query(28.6139, ge=-90.0, le=90.0),
    lon: float = Query(77.2090, ge=-180.0, le=180.0),
    room_area_sqm: float = Query(25.0, ge=1.0, le=1000.0),
    ceiling_height_m: float = Query(2.6, ge=1.5, le=10.0),
    purifier_cadr_m3h: float = Query(250.0, ge=0.0, le=5000.0),
):
    """Convenience GET endpoint for running scenario-based IAQ mass-balance screening."""
    payload = IndoorScreeningRequest(
        latitude=lat,
        longitude=lon,
        room_area_sqm=room_area_sqm,
        ceiling_height_m=ceiling_height_m,
        purifier_cadr_m3h=purifier_cadr_m3h,
    )
    return await run_indoor_screening(payload)
