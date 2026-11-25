"""Pydantic schemas for geospatial air quality queries and spatial grid responses."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.aqi import (
    CPCBModelProxyResponse,
    PollutantsCollection,
    ProvenanceMetadata,
    USEPAModelProxyResponse,
)


class QueryLocationMetadata(BaseModel):
    query_latitude: float
    query_longitude: float
    search_radius_km: float


class NearbyAQIGridItem(BaseModel):
    grid_latitude: float
    grid_longitude: float
    distance_km: float
    model_valid_utc: str
    model_valid_local: str
    cpcb_model_proxy: Optional[CPCBModelProxyResponse] = None
    us_epa_model_proxy: Optional[USEPAModelProxyResponse] = None
    pollutants: PollutantsCollection
    provenance: ProvenanceMetadata
    spatial_resolution: str = "0.4° (~45 km)"
    is_stale: bool = Field(False, description="True if atmospheric record exceeds freshness threshold")
    scientific_notes: str = (
        "Point-in-time model proxy calculated from ECMWF CAMS Global atmospheric reanalysis. "
        "Coordinates represent the atmospheric model grid centroid, NOT a physical ground sensor."
    )


class NearbyAQIResponse(BaseModel):
    query_location: QueryLocationMetadata
    total_matching_grids: int
    evaluation_time_utc: str = Field(..., description="UTC timestamp against which atmospheric validity was evaluated")
    include_forecast: bool = Field(False, description="Whether future model forecast records were included in the evaluation")
    items: List[NearbyAQIGridItem]
    message: str
    spatial_disclaimer: str = (
        "Results represent regional atmospheric reanalysis/forecast grid points with native 0.4° (~45 km) "
        "resolution. They do not constitute street-level microclimate observations or regulatory CAAQMS measurements."
    )
