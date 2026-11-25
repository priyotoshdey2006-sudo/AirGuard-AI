"""Initial schema for atmospheric aqi_cache.

Revision ID: 001_initial
Revises: 
Create Date: 2026-11-21 21:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'aqi_cache',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('location_key', sa.String(length=64), nullable=False),
        sa.Column('grid_latitude', sa.Float(), nullable=False),
        sa.Column('grid_longitude', sa.Float(), nullable=False),
        
        # CPCB Model Proxy (Nullable)
        sa.Column('cpcb_proxy_index', sa.Integer(), nullable=True),
        sa.Column('cpcb_category', sa.String(length=32), nullable=True),
        sa.Column('cpcb_dominant_pollutant', sa.String(length=16), nullable=True),
        sa.Column('cpcb_criteria_met', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('cpcb_pollutant_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
        
        # US EPA Model Proxy (Nullable)
        sa.Column('us_proxy_index', sa.Integer(), nullable=True),
        sa.Column('us_category', sa.String(length=32), nullable=True),
        sa.Column('us_dominant_pollutant', sa.String(length=16), nullable=True),
        
        # Nullable Pollutant Concentrations
        sa.Column('pm2_5', sa.Float(), nullable=True),
        sa.Column('pm10', sa.Float(), nullable=True),
        sa.Column('no2', sa.Float(), nullable=True),
        sa.Column('so2', sa.Float(), nullable=True),
        sa.Column('co', sa.Float(), nullable=True),
        sa.Column('o3', sa.Float(), nullable=True),
        sa.Column('nh3', sa.Float(), nullable=True),
        sa.Column('pb', sa.Float(), nullable=True),
        sa.Column('uv_index', sa.Float(), nullable=True),
        
        # Provenance & CAMS Metadata
        sa.Column('source_provider', sa.String(length=64), nullable=False),
        sa.Column('native_atmospheric_model', sa.String(length=64), nullable=False),
        sa.Column('native_spatial_resolution', sa.String(length=32), nullable=False),
        sa.Column('native_temporal_resolution', sa.String(length=32), nullable=False),
        sa.Column('temporal_processing', sa.String(length=255), nullable=False),
        sa.Column('data_provenance', sa.String(length=32), nullable=False),
        sa.Column('is_ground_observation', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        
        # Timestamps
        sa.Column('model_cycle_utc', sa.DateTime(timezone=True), nullable=True),
        sa.Column('model_valid_utc', sa.DateTime(timezone=True), nullable=False),
        sa.Column('model_valid_local', sa.String(length=64), nullable=False),
        sa.Column('forecast_hourly_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('retrieved_at_utc', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expires_at_utc', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('idx_aqi_grid_lookup', 'aqi_cache', ['location_key', 'expires_at_utc'])


def downgrade() -> None:
    op.drop_index('idx_aqi_grid_lookup', table_name='aqi_cache')
    op.drop_table('aqi_cache')
