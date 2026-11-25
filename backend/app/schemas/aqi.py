"""Pydantic v2 schemas for Air Quality monitoring, forecasts, and provenance tracking."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ProvenanceEnum(str, Enum):
    MODEL_ANALYSIS = "MODEL_ANALYSIS"
    MODEL_FORECAST = "MODEL_FORECAST"
    GROUND_OBSERVATION = "GROUND_OBSERVATION"
    UNVERIFIED_ESTIMATE = "UNVERIFIED_ESTIMATE"
    ESTIMATED = "UNVERIFIED_ESTIMATE"
    OBSERVED = "GROUND_OBSERVATION"
    FORECAST = "MODEL_FORECAST"


class LocationMetadata(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Requested query latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Requested query longitude")
    grid_latitude: Optional[float] = Field(
        None, ge=-90.0, le=90.0, description="Upstream atmospheric model grid centroid latitude"
    )
    grid_longitude: Optional[float] = Field(
        None, ge=-180.0, le=180.0, description="Upstream atmospheric model grid centroid longitude"
    )
    timezone: str = "UTC"


class CPCBModelProxyResponse(BaseModel):
    proxy_index: Optional[int] = Field(None, description="CPCB-breakpoint-based model proxy index (0-500)")
    category: Optional[str] = Field(None, description="Good | Satisfactory | Moderate | Poor | Very Poor | Severe")
    dominant_pollutant: Optional[str] = Field(None, description="Pollutant yielding highest sub-index")
    index_type: str = "CPCB_BREAKPOINT_BASED_MODEL_PROXY"
    criteria_met: bool = Field(..., description="True if >= 3 pollutants available including PM2.5 or PM10")
    pollutant_count_evaluated: int = 0
    sub_indices: Dict[str, int] = Field(default_factory=dict)
    regulatory_disclaimer: str
    criteria_explanation: str


class USEPAModelProxyResponse(BaseModel):
    proxy_index: Optional[int] = Field(None, description="US EPA AQI proxy index (0-500)")
    category: Optional[str] = Field(None, description="Good | Moderate | USG | Unhealthy | Very Unhealthy | Hazardous")
    dominant_pollutant: Optional[str] = None
    index_type: str = "US_EPA_BREAKPOINT_BASED_MODEL_PROXY"
    sub_indices: Dict[str, int] = Field(default_factory=dict)
    regulatory_disclaimer: str


class PollutantDetail(BaseModel):
    concentration: Optional[float] = None
    unit: str
    averaging_basis: str = "HOURLY_MODEL_ESTIMATE"


class PollutantsCollection(BaseModel):
    pm2_5: PollutantDetail
    pm10: PollutantDetail
    no2: PollutantDetail
    o3: PollutantDetail
    so2: PollutantDetail
    co: PollutantDetail
    nh3: Optional[PollutantDetail] = None
    pb: Optional[PollutantDetail] = None
    uv_index: Optional[PollutantDetail] = None


class WHOGuidelineBenchmarkItem(BaseModel):
    pollutant: str
    hourly_model_concentration: float
    guideline_24h_benchmark_level: float
    ratio_to_24h_benchmark: float
    comparison_status: str
    benchmark_disclaimer: str


class ProvenanceMetadata(BaseModel):
    source_provider: str = "Open-Meteo Air Quality API"
    native_atmospheric_model: str = "ECMWF CAMS Global (IFS-AER)"
    native_spatial_resolution: str = "0.4° (~45 km)"
    native_temporal_resolution: str = "3-hourly"
    temporal_processing: str = (
        "Hourly output as provided by Open-Meteo API "
        "(resampled/interpolated from ECMWF CAMS 3-hourly model grid by upstream provider; "
        "exact interpolation algorithm is not specified by Open-Meteo documentation)."
    )
    data_provenance: str = "MODEL_ANALYSIS"
    is_ground_observation: bool = False
    model_cycle_utc: Optional[str] = None
    model_valid_utc: str
    model_valid_local: str
    retrieved_at_utc: str


class CurrentAQIResponse(BaseModel):
    location: LocationMetadata
    cpcb_model_proxy: CPCBModelProxyResponse
    us_epa_model_proxy: USEPAModelProxyResponse
    pollutants: PollutantsCollection
    who_guideline_benchmark: List[WHOGuidelineBenchmarkItem]
    provenance: ProvenanceMetadata


class HourlyForecastItem(BaseModel):
    time_utc: str
    time_local: str
    cpcb_proxy_index: Optional[int] = None
    us_proxy_index: Optional[int] = None
    pm2_5: Optional[float] = None
    pm10: Optional[float] = None
    category: Optional[str] = None


class ForecastAQIResponse(BaseModel):
    location: LocationMetadata
    provenance: ProvenanceMetadata
    forecast_series: List[HourlyForecastItem]
