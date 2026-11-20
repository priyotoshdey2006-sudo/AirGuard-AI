"""AQI snapshot and cache database model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class AQICache(Base):
    __tablename__ = "aqi_cache"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    location_key: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    
    aqi_us: Mapped[int] = mapped_column(Integer, nullable=False)
    aqi_european: Mapped[int] = mapped_column(Integer, nullable=False)
    pm2_5: Mapped[float] = mapped_column(Float, default=0.0)
    pm10: Mapped[float] = mapped_column(Float, default=0.0)
    o3: Mapped[float] = mapped_column(Float, default=0.0)
    no2: Mapped[float] = mapped_column(Float, default=0.0)
    so2: Mapped[float] = mapped_column(Float, default=0.0)
    co: Mapped[float] = mapped_column(Float, default=0.0)
    uv_index: Mapped[float] = mapped_column(Float, default=0.0)
    
    dominant_pollutant: Mapped[str] = mapped_column(String(50), default="pm2_5")
    provenance: Mapped[str] = mapped_column(String(50), default="OBSERVED")  # OBSERVED | FORECAST | ESTIMATED
    
    forecast_json: Mapped[str] = mapped_column(Text, default="{}")
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
