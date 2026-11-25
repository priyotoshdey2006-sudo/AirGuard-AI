"""AQI atmospheric cache database model matching the approved schema."""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class AQICache(Base):
    __tablename__ = "aqi_cache"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    location_key: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    grid_latitude: Mapped[float] = mapped_column(Float, nullable=False)
    grid_longitude: Mapped[float] = mapped_column(Float, nullable=False)

    # CPCB Model Proxy (Nullable if criteria not met)
    cpcb_proxy_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cpcb_category: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    cpcb_dominant_pollutant: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    cpcb_criteria_met: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cpcb_pollutant_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # US EPA Model Proxy (Nullable if criteria not met)
    us_proxy_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    us_category: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    us_dominant_pollutant: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)

    # Pollutant Concentrations (Explicitly NULLABLE to reflect upstream reality)
    pm2_5: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pm10: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    no2: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    so2: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    co: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    o3: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    nh3: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    uv_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Provenance & CAMS Metadata
    source_provider: Mapped[str] = mapped_column(String(64), default="Open-Meteo Air Quality API", nullable=False)
    native_atmospheric_model: Mapped[str] = mapped_column(String(64), default="ECMWF CAMS Global (IFS-AER)", nullable=False)
    native_spatial_resolution: Mapped[str] = mapped_column(String(32), default="0.4° (~45 km)", nullable=False)
    native_temporal_resolution: Mapped[str] = mapped_column(String(32), default="3-hourly", nullable=False)
    temporal_processing: Mapped[str] = mapped_column(String(255), default="Hourly output as provided by Open-Meteo API", nullable=False)
    data_provenance: Mapped[str] = mapped_column(String(32), default="MODEL_ANALYSIS", nullable=False)
    is_ground_observation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps (UTC & Local)
    model_cycle_utc: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    model_valid_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    model_valid_local: Mapped[str] = mapped_column(String(64), nullable=False)
    forecast_hourly_json: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    retrieved_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
