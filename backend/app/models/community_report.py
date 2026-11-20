"""Crowdsourced community pollution hazard report model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class CommunityReport(Base):
    __tablename__ = "community_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reporter_name: Mapped[str] = mapped_column(String(100), default="Anonymous Citizen")
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # STUBBLE_BURNING | INDUSTRIAL_EMISSION | VEHICULAR_SMOKE | CONSTRUCTION_DUST | GARBAGE_BURNING | OTHER
    severity: Mapped[int] = mapped_column(Integer, default=3)  # 1 (Low) to 5 (Critical)
    
    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), default="PENDING")  # PENDING | VERIFIED | RESOLVED | REJECTED
    upvotes_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="community_reports")
