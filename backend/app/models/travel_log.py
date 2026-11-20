"""Sustainable travel and commute impact log model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class TravelLog(Base):
    __tablename__ = "travel_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    mode: Mapped[str] = mapped_column(String(50), nullable=False)  # WALK | BICYCLE | ELECTRIC_BUS | METRO | EV | ICE_CAR
    origin_name: Mapped[str] = mapped_column(String(200), default="Current Location")
    destination_name: Mapped[str] = mapped_column(String(200), default="Destination")
    
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    duration_minutes: Mapped[float] = mapped_column(Float, default=0.0)
    avg_aqi_exposure: Mapped[float] = mapped_column(Float, default=50.0)
    co2_emitted_kg: Mapped[float] = mapped_column(Float, default=0.0)
    co2_saved_kg: Mapped[float] = mapped_column(Float, default=0.0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="travel_logs")
