"""User and Profile schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    email: str = Field(..., min_length=5, max_length=255, description="Citizen email address")
    password: str = Field(..., min_length=6)
    full_name: str = ""
    sensitivity_level: str = "NORMAL"  # NORMAL | ASTHMATIC | CARDIOVASCULAR | ELDERLY | CHILD | ATHLETE


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserProfileResponse(BaseModel):
    id: str
    sensitivity_level: str
    home_lat: Optional[float] = None
    home_lon: Optional[float] = None
    work_lat: Optional[float] = None
    work_lon: Optional[float] = None
    notify_on_poor_aqi: bool = True
    alert_threshold_aqi: int = 100


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    profile: Optional[UserProfileResponse] = None


class UserProfileUpdate(BaseModel):
    sensitivity_level: Optional[str] = None
    home_lat: Optional[float] = None
    home_lon: Optional[float] = None
    work_lat: Optional[float] = None
    work_lon: Optional[float] = None
    notify_on_poor_aqi: Optional[bool] = None
    alert_threshold_aqi: Optional[int] = None
