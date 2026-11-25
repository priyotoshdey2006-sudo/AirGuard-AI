"""Add PostGIS spatial extension and aqi_records spatial table.

Revision ID: 002_spatial
Revises: 001_initial
Create Date: 2026-11-21 21:55:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision: str = "002_spatial"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    # 1. Enable PostGIS extension on PostgreSQL
    if is_postgres:
        op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # 2. Geometry column type definition
    geom_col = Geometry("POINT", srid=4326, spatial_index=True) if is_postgres else sa.String(length=64)

    # 3. Create aqi_records spatial table
    op.create_table(
        "aqi_records",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("location_key", sa.String(length=64), nullable=False),
        sa.Column("grid_latitude", sa.Float(), nullable=False),
        sa.Column("grid_longitude", sa.Float(), nullable=False),
        sa.Column("geom", geom_col, nullable=False),
        # Nullable Pollutant Concentrations (reflecting actual upstream model availability)
        sa.Column("pm2_5", sa.Float(), nullable=True),
        sa.Column("pm10", sa.Float(), nullable=True),
        sa.Column("no2", sa.Float(), nullable=True),
        sa.Column("so2", sa.Float(), nullable=True),
        sa.Column("co", sa.Float(), nullable=True),
        sa.Column("o3", sa.Float(), nullable=True),
        sa.Column("nh3", sa.Float(), nullable=True),
        sa.Column("pb", sa.Float(), nullable=True),
        sa.Column("uv_index", sa.Float(), nullable=True),
        # CPCB Model Proxy (Nullable)
        sa.Column("cpcb_proxy_index", sa.Integer(), nullable=True),
        sa.Column("cpcb_category", sa.String(length=32), nullable=True),
        sa.Column("cpcb_dominant_pollutant", sa.String(length=16), nullable=True),
        sa.Column("cpcb_criteria_met", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("cpcb_pollutant_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        # US EPA Model Proxy (Nullable)
        sa.Column("us_proxy_index", sa.Integer(), nullable=True),
        sa.Column("us_category", sa.String(length=32), nullable=True),
        sa.Column("us_dominant_pollutant", sa.String(length=16), nullable=True),
        # Provenance & Resolution Metadata
        sa.Column("source_provider", sa.String(length=64), nullable=False),
        sa.Column("native_atmospheric_model", sa.String(length=64), nullable=False),
        sa.Column("native_spatial_resolution", sa.String(length=32), nullable=False),
        sa.Column("native_temporal_resolution", sa.String(length=32), nullable=False),
        sa.Column("temporal_processing", sa.String(length=255), nullable=False),
        sa.Column("data_provenance", sa.String(length=32), nullable=False),
        sa.Column("is_ground_observation", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        # Timestamps
        sa.Column("model_cycle_utc", sa.DateTime(timezone=True), nullable=True),
        sa.Column("model_valid_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("model_valid_local", sa.String(length=64), nullable=False),
        sa.Column("retrieved_at_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at_utc", sa.DateTime(timezone=True), nullable=False),
        # Uniqueness constraint: prevents duplicate records for same grid point and forecast validity timestamp
        sa.UniqueConstraint("grid_latitude", "grid_longitude", "model_valid_utc", name="uq_grid_timestamp"),
    )

    # 4. Indexes
    op.create_index("idx_aqi_records_valid_utc", "aqi_records", ["model_valid_utc"])
    op.create_index("idx_aqi_records_lookup", "aqi_records", ["location_key", "expires_at_utc"])


def downgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == "postgresql"

    op.drop_index("idx_aqi_records_lookup", table_name="aqi_records")
    op.drop_index("idx_aqi_records_valid_utc", table_name="aqi_records")
    if is_postgres:
        op.drop_index("idx_aqi_records_geom", table_name="aqi_records")

    op.drop_table("aqi_records")
