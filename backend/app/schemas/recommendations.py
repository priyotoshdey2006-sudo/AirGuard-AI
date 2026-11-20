"""Pydantic schemas for personalized AI recommendations."""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.aqi import ProvenanceEnum


class ActivityWindow(BaseModel):
    activity_name: str
    optimal_time: str
    expected_aqi: int
    safety_rating: str  # SAFE | CAUTION | AVOID
    mask_recommendation: str  # NONE | SURGICAL | N95_REQUIRED
    mitigation_tips: str


class RoutineRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    sensitivity_level: str = "NORMAL"  # NORMAL | ASTHMATIC | CARDIOVASCULAR | ELDERLY | CHILD | ATHLETE
    planned_activities: List[str] = Field(
        default=["Morning Jog", "Commute to Work", "Evening Walk"],
        description="List of planned activities for the day"
    )


class RoutineResponse(BaseModel):
    sensitivity_level: str
    overall_risk_assessment: str
    daily_summary: str
    activity_windows: List[ActivityWindow]
    action_items: List[str]
    indoor_guidance: str
    model_provider: str = "Gemini-2.0-Flash"
    provenance: ProvenanceEnum = ProvenanceEnum.ESTIMATED
