"""Schemas for community crowdsourced pollution reporting."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class CommunityReportCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    description: str = Field("", max_length=1000)
    category: str = Field(
        ...,
        description="STUBBLE_BURNING | INDUSTRIAL_EMISSION | VEHICULAR_SMOKE | CONSTRUCTION_DUST | GARBAGE_BURNING | OTHER"
    )
    severity: int = Field(3, ge=1, le=5)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    image_url: Optional[str] = None
    reporter_name: str = "Anonymous Citizen"


class CommunityReportResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str
    severity: int
    latitude: float
    longitude: float
    image_url: Optional[str] = None
    status: str
    upvotes_count: int
    reporter_name: str
    created_at: datetime
    distance_km: Optional[float] = None


class CommunityReportList(BaseModel):
    total: int
    reports: List[CommunityReportResponse]
