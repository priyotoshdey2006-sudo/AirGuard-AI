"""User and user profile database models."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), default="")
    role: Mapped[str] = mapped_column(String(50), default="USER")  # USER | MODERATOR | ADMIN
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    profile: Mapped["UserProfile"] = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    community_reports: Mapped[list["CommunityReport"]] = relationship("CommunityReport", back_populates="user")
    travel_logs: Mapped[list["TravelLog"]] = relationship("TravelLog", back_populates="user")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    sensitivity_level: Mapped[str] = mapped_column(String(50), default="NORMAL")  # NORMAL | ASTHMATIC | CARDIOVASCULAR | ELDERLY | CHILD | ATHLETE
    home_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    home_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    work_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    work_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    notify_on_poor_aqi: Mapped[bool] = mapped_column(Boolean, default=True)
    alert_threshold_aqi: Mapped[int] = mapped_column(Integer, default=100)

    user: Mapped["User"] = relationship("User", back_populates="profile")
