"""Schemas for the Contextual AI Air Quality Assistant."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    sensitivity_level: Optional[str] = "NORMAL"
    current_aqi: Optional[int] = None
    category: Optional[str] = None
    dominant_pollutant: Optional[str] = None
    location_name: Optional[str] = None


class ContextData(BaseModel):
    location: str = "Detected Area"
    current_aqi: Optional[int] = None
    category: str = "Unavailable"
    dominant_pollutant: str = "unknown"
    sensitivity_profile: str = "NORMAL"
    is_live_data_available: bool = True


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    model_provider: str = "Gemini-2.0-Flash"
    context_used: ContextData
    suggested_followups: List[str] = []
