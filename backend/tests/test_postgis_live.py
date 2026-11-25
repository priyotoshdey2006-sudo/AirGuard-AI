"""Live integration test against PostgreSQL 16/17 + PostGIS 3.x.

Verifies:
1. Native PostGIS extension availability and version reporting.
2. Geometry column insertion with SRID 4326 representing true CAMS grid centroids.
3. Functional geography GiST index (idx_aqi_records_geom_geog) presence and query planner usage.
4. PostGIS ST_DWithin metric radius filtering on geography.
5. PostGIS ST_Distance calculation matching known geodesic distances.
6. Record deduplication on PostgreSQL returning only the latest valid forecast/observation per grid cell.
7. Clean skip when PostgreSQL is not running in the current test environment.
"""

from datetime import datetime, timezone, timedelta
import uuid
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from geoalchemy2.elements import WKTElement
from app.db.base import Base
import app.models  # noqa: F401 - Register all models for SQLAlchemy mapper configuration
from app.models.aqi_record import AQIRecord
from app.services.aqi_persistence import aqi_persistence_service

POSTGRES_TEST_URL = "postgresql+asyncpg://postgres@127.0.0.1:15432/postgres"


@pytest.mark.asyncio
async def test_live_postgis_spatial_operations():
    """Verify live PostgreSQL + PostGIS spatial queries when database server is reachable."""
    try:
        engine = create_async_engine(POSTGRES_TEST_URL, echo=False)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT PostGIS_Version()"))
            postgis_ver = result.scalar()
    except Exception as exc:
        pytest.skip(f"PostgreSQL + PostGIS server not reachable on {POSTGRES_TEST_URL} ({exc}).")

    assert postgis_ver is not None
    assert "3." in str(postgis_ver)

    Session = async_sessionmaker(bind=engine, expire_on_commit=False)

    now_utc = datetime.now(timezone.utc)
    unique_key = f"test_{uuid.uuid4().hex[:8]}"

    async with Session() as session:
        # Insert test PostGIS record at Delhi (28.6139, 77.2090)
        rec = AQIRecord(
            id=str(uuid.uuid4()),
            location_key=unique_key,
            grid_latitude=28.6139,
            grid_longitude=77.2090,
            geom=WKTElement("POINT(77.2090 28.6139)", srid=4326),
            pm2_5=90.0,
            pm10=150.0,
            cpcb_criteria_met=True,
            cpcb_pollutant_count=2,
            cpcb_proxy_index=200,
            cpcb_category="Moderate",
            source_provider="Open-Meteo",
            native_atmospheric_model="ECMWF CAMS Global",
            native_spatial_resolution="0.4° (~45 km)",
            native_temporal_resolution="3-hourly",
            temporal_processing="Hourly",
            data_provenance="MODEL_ANALYSIS",
            is_ground_observation=False,
            model_valid_utc=now_utc,
            model_valid_local=now_utc.isoformat(),
            retrieved_at_utc=now_utc,
            expires_at_utc=now_utc + timedelta(hours=1),
        )
        session.add(rec)
        await session.commit()

        # Query using PostGIS native ST_DWithin from 4.2 km away (28.6250, 77.2500)
        nearby_results = await aqi_persistence_service.query_nearby_grids(
            session=session,
            latitude=28.6250,
            longitude=77.2500,
            radius_km=10.0,
            limit=5,
        )

        matching_test = [r for r, d in nearby_results if r.location_key == unique_key]
        assert len(matching_test) == 1
        distance = next(d for r, d in nearby_results if r.location_key == unique_key)

        # PostGIS distance between (28.6250, 77.2500) and (28.6139, 77.2090) is ~4.19 km
        assert 4.0 < distance < 4.5

        # Query with 1.0 km radius: should NOT include the test point
        tight_results = await aqi_persistence_service.query_nearby_grids(
            session=session,
            latitude=28.6250,
            longitude=77.2500,
            radius_km=1.0,
            limit=5,
        )
        assert not any(r.location_key == unique_key for r, _ in tight_results)

        # Clean up test record
        await session.delete(rec)
        await session.commit()

    await engine.dispose()


@pytest.mark.asyncio
async def test_live_postgis_index_and_deduplication():
    """Verify functional geography GiST index and query deduplication on live PostgreSQL."""
    try:
        engine = create_async_engine(POSTGRES_TEST_URL, echo=False)
        async with engine.connect() as conn:
            idx_res = await conn.execute(
                text("SELECT indexname FROM pg_indexes WHERE tablename = 'aqi_records' AND indexname = 'idx_aqi_records_geom_geog';")
            )
            has_geog_index = idx_res.scalar() is not None
    except Exception as exc:
        pytest.skip(f"PostgreSQL + PostGIS server not reachable ({exc}).")

    assert has_geog_index, "Functional GiST index idx_aqi_records_geom_geog must exist on aqi_records"

    # Verify query plan utilizes the geography index
    async with engine.connect() as conn:
        explain_res = await conn.execute(
            text("""
                EXPLAIN (COSTS OFF)
                SELECT id FROM aqi_records
                WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(77.25, 28.625), 4326)::geography, 50000.0);
            """)
        )
        explain_lines = " ".join([row[0] for row in explain_res.fetchall()])
        assert "idx_aqi_records_geom_geog" in explain_lines or "Index Scan" in explain_lines or "Bitmap Index Scan" in explain_lines

    # Verify deduplication & temporal current-vs-future forecast selection policy on PostgreSQL
    Session = async_sessionmaker(bind=engine, expire_on_commit=False)
    grid_lat = 27.9500
    grid_lon = 78.1500
    loc_key = f"live_dedup_{uuid.uuid4().hex[:6]}"
    now_live = datetime.now(timezone.utc)
    t_v1 = now_live - timedelta(hours=2)        # Historical past
    t_v2 = now_live - timedelta(minutes=5)      # Current analysis
    t_v3 = now_live + timedelta(hours=5)        # Future forecast

    async with Session() as session:
        r1 = AQIRecord(
            id=str(uuid.uuid4()),
            location_key=loc_key,
            grid_latitude=grid_lat,
            grid_longitude=grid_lon,
            geom=WKTElement(f"POINT({grid_lon} {grid_lat})", srid=4326),
            pm2_5=35.0,
            pm10=70.0,
            cpcb_criteria_met=True,
            cpcb_pollutant_count=2,
            source_provider="Open-Meteo",
            native_atmospheric_model="ECMWF CAMS Global",
            native_spatial_resolution="0.4° (~45 km)",
            native_temporal_resolution="3-hourly",
            temporal_processing="Hourly",
            data_provenance="MODEL_ANALYSIS",
            is_ground_observation=False,
            model_valid_utc=t_v1,
            model_valid_local=t_v1.isoformat(),
            retrieved_at_utc=t_v1,
            expires_at_utc=t_v1 + timedelta(hours=1),
        )
        r2 = AQIRecord(
            id=str(uuid.uuid4()),
            location_key=loc_key,
            grid_latitude=grid_lat,
            grid_longitude=grid_lon,
            geom=WKTElement(f"POINT({grid_lon} {grid_lat})", srid=4326),
            pm2_5=95.0,
            pm10=180.0,
            cpcb_criteria_met=True,
            cpcb_pollutant_count=2,
            source_provider="Open-Meteo",
            native_atmospheric_model="ECMWF CAMS Global",
            native_spatial_resolution="0.4° (~45 km)",
            native_temporal_resolution="3-hourly",
            temporal_processing="Hourly",
            data_provenance="MODEL_ANALYSIS",
            is_ground_observation=False,
            model_valid_utc=t_v2,
            model_valid_local=t_v2.isoformat(),
            retrieved_at_utc=now_live,
            expires_at_utc=now_live + timedelta(hours=1),
        )
        r3 = AQIRecord(
            id=str(uuid.uuid4()),
            location_key=loc_key,
            grid_latitude=grid_lat,
            grid_longitude=grid_lon,
            geom=WKTElement(f"POINT({grid_lon} {grid_lat})", srid=4326),
            pm2_5=160.0,
            pm10=290.0,
            cpcb_criteria_met=True,
            cpcb_pollutant_count=2,
            source_provider="Open-Meteo",
            native_atmospheric_model="ECMWF CAMS Global",
            native_spatial_resolution="0.4° (~45 km)",
            native_temporal_resolution="3-hourly",
            temporal_processing="Hourly",
            data_provenance="MODEL_FORECAST",
            is_ground_observation=False,
            model_valid_utc=t_v3,
            model_valid_local=t_v3.isoformat(),
            retrieved_at_utc=now_live,
            expires_at_utc=now_live + timedelta(hours=1),
        )
        session.add(r1)
        session.add(r2)
        session.add(r3)
        await session.commit()

        # 1. Current query (include_forecast=False default): MUST select r2 (current), NOT r3 (future)
        results = await aqi_persistence_service.query_nearby_grids(
            session=session,
            latitude=grid_lat,
            longitude=grid_lon,
            radius_km=10.0,
            limit=10,
            target_time_utc=now_live,
            include_forecast=False,
        )

        matched = [rec for rec, _ in results if rec.location_key == loc_key]
        assert len(matched) == 1, "Must return exactly one record per grid centroid"
        assert matched[0].model_valid_utc == t_v2, "Must select latest valid current observation, NOT future forecast"
        assert matched[0].pm2_5 == 95.0

        # 2. Forecast query (include_forecast=True): MUST select r3 (furthest future)
        results_fc = await aqi_persistence_service.query_nearby_grids(
            session=session,
            latitude=grid_lat,
            longitude=grid_lon,
            radius_km=10.0,
            limit=10,
            target_time_utc=now_live,
            include_forecast=True,
        )
        matched_fc = [rec for rec, _ in results_fc if rec.location_key == loc_key]
        assert len(matched_fc) == 1
        assert matched_fc[0].model_valid_utc == t_v3
        assert matched_fc[0].pm2_5 == 160.0

        await session.delete(r1)
        await session.delete(r2)
        await session.delete(r3)
        await session.commit()

    await engine.dispose()
