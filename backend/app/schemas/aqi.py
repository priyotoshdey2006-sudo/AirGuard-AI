"""Pydantic schemas for Air Quality monitoring, forecasts, and indoor guidance."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ProvenanceEnum(str, Enum):
    OBSERVED = "OBSERVED"
    FORECAST = "FORECAST"
    ESTIMATED = "ESTIMATED"


class AQICategoryEnum(str, Enum):
    GOOD = "Good"
    MODERATE = "Moderate"
    UNHEALTHY_SENSITIVE = "Unhealthy for Sensitive Groups"
    UNHEALTHY = "Unhealthy"
    VERY_UNHEALTHY = "Very Unhealthy"
    HAZARDOUS = "Hazardous"


class Pollutants(BaseModel):
    pm2_5: float = Field(..., description="PM2.5 concentration in µg/m³")
    pm10: float = Field(..., description="PM10 concentration in µg/m³")
    o3: float = Field(0.0, description="Ozone concentration in µg/m³")
    no2: float = Field(0.0, description="Nitrogen dioxide in µg/m³")
    so2: float = Field(0.0, description="Sulfur dioxide in µg/m³")
    co: float = Field(0.0, description="Carbon monoxide in µg/m³")
    uv_index: float = Field(0.0, description="Ultraviolet radiation index")


class CurrentAQIResponse(BaseModel):
    latitude: float
    longitude: float
    location_name: Optional[str] = "Detected Location"
    aqi_us: int = Field(..., description="US EPA Air Quality Index (0-500)")
    aqi_european: int = Field(..., description="European Air Quality Index (0-100)")
    category: AQICategoryEnum
    category_color: str
    dominant_pollutant: str
    pollutants: Pollutants
    health_advice: str
    provenance: ProvenanceEnum = ProvenanceEnum.OBSERVED
    timestamp: datetime


class HourlyForecastItem(BaseModel):
    time: str
    aqi_us: int
    pm2_5: float
    pm10: float
    category: str


class DailyForecastItem(BaseModel):
    date: str
    max_aqi: int
    min_aqi: int
    dominant_pollutant: str
    category: str


class ForecastAQIResponse(BaseModel):
    latitude: float
    longitude: float
    hourly: List[HourlyForecastItem]
    daily: List[DailyForecastItem]
    provenance: ProvenanceEnum = ProvenanceEnum.FORECAST


class IndoorGuidanceRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    room_sqft: float = Field(350.0, ge=50.0, le=10000.0)
    has_hepa_filter: bool = True
    has_ac: bool = True
    building_seal_quality: str = Field("standard", description="poor | standard | airtight")


class SafeVentilationWindow(BaseModel):
    start_time: str
    end_time: str
    expected_outdoor_aqi: int
    recommendation: str


class IndoorGuidanceResponse(BaseModel):
    outdoor_aqi: int
    estimated_indoor_aqi: int
    indoor_category: str
    window_advice: str
    safe_ventilation_windows: List[SafeVentilationWindow]
    hepa_runtime_recommendation_hours: float
    air_cleaner_speed: str
    tips: List[str]
    provenance: ProvenanceEnum = ProvenanceEnum.ESTIMATED
