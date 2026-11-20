"""Schemas for sustainable transport, commute planning, and carbon metrics."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class RouteCompareRequest(BaseModel):
    origin_lat: float = Field(..., ge=-90.0, le=90.0)
    origin_lon: float = Field(..., ge=-180.0, le=180.0)
    dest_lat: float = Field(..., ge=-90.0, le=90.0)
    dest_lon: float = Field(..., ge=-180.0, le=180.0)
    distance_km: Optional[float] = Field(None, ge=0.1, le=1000.0)
    origin_name: str = "Origin"
    dest_name: str = "Destination"


class RouteOption(BaseModel):
    mode: str  # WALK | BICYCLE | ELECTRIC_BUS | METRO | EV | ICE_CAR
    mode_label: str
    duration_minutes: float
    co2_kg: float
    co2_saved_kg: float
    aqi_exposure_score: float  # Inhaled pollutant intake index based on ventilation rate + ambient AQI
    exposure_level: str  # LOW | MODERATE | HIGH
    recommended: bool = False
    recommendation_reason: str = ""


class RouteCompareResponse(BaseModel):
    distance_km: float
    origin_name: str
    dest_name: str
    options: List[RouteOption]
    cleanest_mode: str
    lowest_carbon_mode: str
    total_trees_equivalent: float


class TravelLogCreate(BaseModel):
    mode: str
    origin_name: str = "Origin"
    destination_name: str = "Destination"
    distance_km: float
    duration_minutes: float = 0.0
    avg_aqi_exposure: float = 50.0
    co2_emitted_kg: float = 0.0
    co2_saved_kg: float = 0.0


class TravelLogResponse(BaseModel):
    id: str
    mode: str
    origin_name: str
    destination_name: str
    distance_km: float
    duration_minutes: float
    avg_aqi_exposure: float
    co2_emitted_kg: float
    co2_saved_kg: float
    created_at: datetime
