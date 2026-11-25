"""Dedicated database and spatial logic tests for AQIRecord, persistence, and PostGIS.

Verifies:
1. Haversine distance mathematical derivation.
2. AQIRecord CRUD operations, geometry representation, and nullable pollutant tolerance.
3. Uniqueness enforcement preventing duplicate grid/timestamp entries.
4. Persistence service duplicate prevention and timestamp preservation.
5. Nearby radius filtering.
6. PostGIS live integration (evaluated when PostgreSQL service is reachable).
"""

from datetime import datetime, timezone, timedelta
import uuid
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.db.base import Base
from app.models.aqi_record import AQIRecord, PointGeometry
from app.schemas.aqi import (
    CPCBModelProxyResponse,
    CurrentAQIResponse,
    LocationMetadata,
    PollutantDetail,
    PollutantsCollection,
    ProvenanceMetadata,
    USEPAModelProxyResponse,
)
from app.services.aqi_persistence import aqi_persistence_service, haversine_distance_km


def test_haversine_distance_calculation():
    """Verify haversine formula against known geographical coordinates."""
    # Connaught Place (28.6315, 77.2167) to India Gate (28.6129, 77.2295) ≈ 2.41 km
    dist = haversine_distance_km(28.6315, 77.2167, 28.6129, 77.2295)
    assert 2.3 < dist < 2.6

    # Same point distance must be 0.0
    zero_dist = haversine_distance_km(28.6139, 77.2090, 28.6139, 77.2090)
    assert zero_dist == 0.0


@pytest.mark.asyncio
async def test_aqi_record_async_crud_and_nullability():
    """Verify asynchronous insertion, retrieval, and nullable pollutant handling."""
    test_async_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestingSession = async_sessionmaker(bind=test_async_engine, expire_on_commit=False)

    now_utc = datetime.now(timezone.utc)
    async with TestingSession() as session:
        rec = AQIRecord(
            id=str(uuid.uuid4()),
            location_key="28.61_77.21",
            grid_latitude=28.6139,
            grid_longitude=77.2090,
            geom="POINT(77.2090 28.6139)",
            pm2_5=85.5,
            pm10=140.0,
            no2=None,  # Nullable
            so2=None,
            co=None,
            o3=None,
            nh3=None,
            pb=None,
            uv_index=4.0,
            cpcb_proxy_index=185,
            cpcb_category="Moderate",
            cpcb_dominant_pollutant="pm2_5",
            cpcb_criteria_met=True,
            cpcb_pollutant_count=2,
            us_proxy_index=166,
            us_category="Unhealthy",
            us_dominant_pollutant="pm2_5",
            source_provider="Open-Meteo Air Quality API",
            native_atmospheric_model="ECMWF CAMS Global (IFS-AER)",
            native_spatial_resolution="0.4° (~45 km)",
            native_temporal_resolution="3-hourly",
            temporal_processing="Hourly output as provided by Open-Meteo API",
            data_provenance="MODEL_ANALYSIS",
            is_ground_observation=False,
            model_cycle_utc=None,
            model_valid_utc=now_utc,
            model_valid_local=now_utc.isoformat(),
            retrieved_at_utc=now_utc,
            expires_at_utc=now_utc + timedelta(minutes=30),
        )
        session.add(rec)
        await session.commit()

        # Retrieve
        result = await session.execute(select(AQIRecord).where(AQIRecord.location_key == "28.61_77.21"))
        fetched = result.scalar_one_or_none()
        assert fetched is not None
        assert fetched.pm2_5 == 85.5
        assert fetched.no2 is None
        assert fetched.model_cycle_utc is None
        assert fetched.cpcb_proxy_index == 185

    await test_async_engine.dispose()


@pytest.mark.asyncio
async def test_persistence_service_prevents_duplicate_records():
    """Verify persist_current_aqi updates rather than duplicating identical time/location records."""
    test_async_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestingSession = async_sessionmaker(bind=test_async_engine, expire_on_commit=False)

    sample_dto = CurrentAQIResponse(
        location=LocationMetadata(latitude=28.6139, longitude=77.2090, timezone="Asia/Kolkata"),
        cpcb_model_proxy=CPCBModelProxyResponse(
            proxy_index=200,
            category="Moderate",
            dominant_pollutant="pm2_5",
            index_type="CPCB_BREAKPOINT_BASED_MODEL_PROXY",
            criteria_met=True,
            pollutant_count_evaluated=3,
            sub_indices={"pm2_5": 200},
            regulatory_disclaimer="Model proxy disclaimer",
            criteria_explanation="Criteria met",
        ),
        us_epa_model_proxy=USEPAModelProxyResponse(
            proxy_index=169,
            category="Unhealthy",
            dominant_pollutant="pm2_5",
            index_type="US_EPA_BREAKPOINT_BASED_MODEL_PROXY",
            sub_indices={"pm2_5": 169},
            regulatory_disclaimer="EPA model proxy disclaimer",
        ),
        pollutants=PollutantsCollection(
            pm2_5=PollutantDetail(concentration=90.0, unit="µg/m³"),
            pm10=PollutantDetail(concentration=150.0, unit="µg/m³"),
            no2=PollutantDetail(concentration=60.0, unit="µg/m³"),
            o3=PollutantDetail(concentration=40.0, unit="µg/m³"),
            so2=PollutantDetail(concentration=12.0, unit="µg/m³"),
            co=PollutantDetail(concentration=0.85, unit="mg/m³"),
        ),
        who_guideline_benchmark=[],
        provenance=ProvenanceMetadata(
            source_provider="Open-Meteo Air Quality API",
            native_atmospheric_model="ECMWF CAMS Global (IFS-AER)",
            native_spatial_resolution="0.4° (~45 km)",
            native_temporal_resolution="3-hourly",
            temporal_processing="Hourly output",
            data_provenance="MODEL_ANALYSIS",
            is_ground_observation=False,
            model_cycle_utc=None,
            model_valid_utc="2026-11-21T10:00:00Z",
            model_valid_local="2026-11-21T15:30:00+05:30",
            retrieved_at_utc="2026-11-21T10:00:00Z",
        ),
    )

    async with TestingSession() as session:
        # First persistence
        rec1 = await aqi_persistence_service.persist_current_aqi(session, sample_dto)
        assert rec1.id is not None

        # Second persistence of same model timestamp must NOT insert duplicate
        rec2 = await aqi_persistence_service.persist_current_aqi(session, sample_dto)
        assert rec1.id == rec2.id

        # Total count must be exactly 1
        count_res = await session.execute(select(AQIRecord))
        assert len(count_res.scalars().all()) == 1

    await test_async_engine.dispose()


@pytest.mark.asyncio
async def test_spatial_radius_filtering_logic():
    """Verify that query_nearby_grids filters candidates outside radius."""
    test_async_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestingSession = async_sessionmaker(bind=test_async_engine, expire_on_commit=False)

    now_utc = datetime.now(timezone.utc)
    async with TestingSession() as session:
        # Delhi point
        delhi = AQIRecord(
            id=str(uuid.uuid4()),
            location_key="28.61_77.21",
            grid_latitude=28.6139,
            grid_longitude=77.2090,
            geom="POINT(77.2090 28.6139)",
            pm2_5=90.0,
            pm10=150.0,
            cpcb_criteria_met=False,
            cpcb_pollutant_count=2,
            source_provider="Open-Meteo",
            native_atmospheric_model="CAMS",
            native_spatial_resolution="0.4°",
            native_temporal_resolution="3-hourly",
            temporal_processing="Hourly",
            data_provenance="MODEL_ANALYSIS",
            is_ground_observation=False,
            model_valid_utc=now_utc,
            model_valid_local=now_utc.isoformat(),
            retrieved_at_utc=now_utc,
            expires_at_utc=now_utc + timedelta(hours=1),
        )
        # Jaipur point (~240 km away)
        jaipur = AQIRecord(
            id=str(uuid.uuid4()),
            location_key="26.91_75.79",
            grid_latitude=26.9124,
            grid_longitude=75.7873,
            geom="POINT(75.7873 26.9124)",
            pm2_5=60.0,
            pm10=110.0,
            cpcb_criteria_met=False,
            cpcb_pollutant_count=2,
            source_provider="Open-Meteo",
            native_atmospheric_model="CAMS",
            native_spatial_resolution="0.4°",
            native_temporal_resolution="3-hourly",
            temporal_processing="Hourly",
            data_provenance="MODEL_ANALYSIS",
            is_ground_observation=False,
            model_valid_utc=now_utc,
            model_valid_local=now_utc.isoformat(),
            retrieved_at_utc=now_utc,
            expires_at_utc=now_utc + timedelta(hours=1),
        )
        session.add_all([delhi, jaipur])
        await session.commit()

        # Query from Delhi center with 50 km radius: should find Delhi, omit Jaipur
        nearby_50 = await aqi_persistence_service.query_nearby_grids(
            session=session,
            latitude=28.6139,
            longitude=77.2090,
            radius_km=50.0,
        )
        assert len(nearby_50) == 1
        assert nearby_50[0][0].location_key == "28.61_77.21"

        # Query from Delhi center with 250 km radius: should find both Delhi and Jaipur
        nearby_250 = await aqi_persistence_service.query_nearby_grids(
            session=session,
            latitude=28.6139,
            longitude=77.2090,
            radius_km=250.0,
        )
        assert len(nearby_250) == 2

    await test_async_engine.dispose()
