"""Geospatial AQI record model supporting PostGIS geometry, continuous CAMS grids, and CPCB/EPA model proxies.

Scientific Constraint:
- ECMWF CAMS Global has ~0.4° (~45 km) native spatial resolution.
- Coordinates represent model grid points/centroids, NEVER physical ground monitoring stations.
"""

from datetime import datetime, timezone
from typing import Any, Optional
import uuid
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import String as SAString, TypeDecorator
from geoalchemy2 import Geometry
from app.db.base import Base


class PointGeometry(TypeDecorator):
    """Platform-independent Point Geometry type.

    - On PostgreSQL + PostGIS: compiles to native Geometry('POINT', srid=4326).
    - On SQLite (lightweight dev/test): falls back to String(64) 'POINT(lon lat)'.
    """

    impl = Geometry
    cache_ok = True

    def __init__(self, srid: int = 4326, spatial_index: bool = True, **kwargs):
        super().__init__(geometry_type="POINT", srid=srid, spatial_index=spatial_index, **kwargs)

    def load_dialect_impl(self, dialect):
        if dialect is None:
            return self.impl
        if dialect.name == "sqlite":
            return dialect.type_descriptor(SAString(64))
        return dialect.type_descriptor(Geometry("POINT", srid=4326, spatial_index=True))


class AQIRecord(Base):
    __tablename__ = "aqi_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    location_key: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    grid_latitude: Mapped[float] = mapped_column(Float, nullable=False)
    grid_longitude: Mapped[float] = mapped_column(Float, nullable=False)

    # PostGIS geometry: POINT(longitude, latitude) with SRID 4326 (WGS 84)
    geom: Mapped[Any] = mapped_column(PointGeometry(srid=4326, spatial_index=True), nullable=False)

    # Pollutant Concentrations (Nullable: strictly reflects upstream model availability without fabrication)
    pm2_5: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pm10: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    no2: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    so2: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    co: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # In mg/m³
    o3: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    nh3: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    uv_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

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

    # CAMS Atmospheric Model Provenance & Metadata
    source_provider: Mapped[str] = mapped_column(String(64), default="Open-Meteo Air Quality API", nullable=False)
    native_atmospheric_model: Mapped[str] = mapped_column(String(64), default="ECMWF CAMS Global (IFS-AER)", nullable=False)
    native_spatial_resolution: Mapped[str] = mapped_column(String(32), default="0.4° (~45 km)", nullable=False)
    native_temporal_resolution: Mapped[str] = mapped_column(String(32), default="3-hourly", nullable=False)
    temporal_processing: Mapped[str] = mapped_column(String(255), default="Hourly output as provided by Open-Meteo API", nullable=False)
    data_provenance: Mapped[str] = mapped_column(String(32), default="MODEL_ANALYSIS", nullable=False)
    is_ground_observation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps (Timezone-Aware UTC and Regional Offset Local)
    model_cycle_utc: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # Explicitly null: never fabricated
    model_valid_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    model_valid_local: Mapped[str] = mapped_column(String(64), nullable=False)
    retrieved_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        # Uniqueness constraint: prevents duplicate records for same grid point and forecast validity timestamp
        UniqueConstraint("grid_latitude", "grid_longitude", "model_valid_utc", name="uq_grid_timestamp"),
        # B-tree index on validity timestamp for historical time-series queries
        Index("idx_aqi_records_valid_utc", "model_valid_utc"),
        # Composite index for grid expiration lookup
        Index("idx_aqi_records_lookup", "location_key", "expires_at_utc"),
    )
