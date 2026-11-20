"""Schemas for the Contextual AI Air Quality Assistant."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    sensitivity_level: Optional[str] = "NORMAL"


class ContextData(BaseModel):
    location: str = "Detected Area"
    current_aqi: int = 50
    category: str = "Good"
    dominant_pollutant: str = "pm2_5"
    sensitivity_profile: str = "NORMAL"


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    model_provider: str = "Gemini-2.0-Flash"
    context_used: ContextData
    suggested_followups: List[str] = []
