"""Sustainable transport, eco-route comparison, and carbon emission endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_current_user_optional, get_db
from app.models.travel_log import TravelLog
from app.models.user import User
from app.schemas.transport import (
    RouteCompareRequest,
    RouteCompareResponse,
    TravelLogCreate,
    TravelLogResponse,
)
from app.services.impact_calculator import impact_calculator
from app.services.open_meteo import open_meteo_service

router = APIRouter()


@router.post("/compare-routes", response_model=RouteCompareResponse, tags=["Sustainable Transport"])
async def compare_transport_modes(payload: RouteCompareRequest):
    """Compare travel duration, CO2 footprint, and inhaled pollutant exposure across transport modes."""
    try:
        aqi_data = await open_meteo_service.get_current_aqi(payload.origin_lat, payload.origin_lon)
        ambient_aqi = aqi_data.aqi_us
    except Exception:
        ambient_aqi = 75

    return impact_calculator.calculate_route_comparison(payload, current_ambient_aqi=ambient_aqi)


@router.post("/logs", response_model=TravelLogResponse, tags=["Sustainable Transport"])
def log_travel_commute(
    payload: TravelLogCreate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Save completed green commute and record net CO2 emissions saved."""
    new_log = TravelLog(
        user_id=current_user.id if current_user else None,
        mode=payload.mode.upper(),
        origin_name=payload.origin_name,
        destination_name=payload.destination_name,
        distance_km=payload.distance_km,
        duration_minutes=payload.duration_minutes,
        avg_aqi_exposure=payload.avg_aqi_exposure,
        co2_emitted_kg=payload.co2_emitted_kg,
        co2_saved_kg=payload.co2_saved_kg,
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


@router.get("/logs", response_model=List[TravelLogResponse], tags=["Sustainable Transport"])
def get_travel_logs(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """List recorded travel logs and environmental savings."""
    query = db.query(TravelLog).order_by(TravelLog.created_at.desc()).limit(50)
    if current_user:
        query = query.filter(TravelLog.user_id == current_user.id)
    
    return query.all()
