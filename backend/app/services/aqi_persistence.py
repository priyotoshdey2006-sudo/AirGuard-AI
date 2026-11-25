"""Atmospheric AQI persistence and geospatial PostGIS querying service.

Handles:
1. Persistence of Open-Meteo / ECMWF CAMS model analyses into PostgreSQL + PostGIS.
2. Prevention of duplicate grid records via composite constraints and uniqueness checks.
3. PostGIS ST_DWithin / ST_Distance spatial queries leveraging GiST indexes.
4. Python Haversine fallback for standalone lightweight SQLite unit testing.
5. Strict adherence to zero-fabrication and scientific disclaimer contracts.
"""

from datetime import datetime, timedelta, timezone
import math
from typing import Any, List, Optional, Tuple
from sqlalchemy import cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2 import Geography
from geoalchemy2.elements import WKTElement

from app.core.config import settings
from app.core.logging import logger
from app.models.aqi_record import AQIRecord
from app.schemas.aqi import (
    CPCBModelProxyResponse,
    CurrentAQIResponse,
    PollutantDetail,
    PollutantsCollection,
    ProvenanceMetadata,
    USEPAModelProxyResponse,
)
from app.schemas.spatial import NearbyAQIGridItem
from app.services.open_meteo import _parse_to_utc


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two geographic coordinates in kilometers."""
    r = 6371.0  # Mean radius of Earth in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(r * c, 3)


class AQIPersistenceService:
    @staticmethod
    async def persist_current_aqi(
        session: AsyncSession,
        current_data: CurrentAQIResponse,
    ) -> AQIRecord:
        """Persist verified atmospheric model data into database, preventing duplicates."""
        # Ensure we persist the actual upstream atmospheric model grid centroid, NOT the user query point
        grid_lat = (
            current_data.location.grid_latitude
            if current_data.location.grid_latitude is not None
            else current_data.location.latitude
        )
        grid_lon = (
            current_data.location.grid_longitude
            if current_data.location.grid_longitude is not None
            else current_data.location.longitude
        )
        location_key = f"{round(grid_lat, 2)}_{round(grid_lon, 2)}"
        model_valid_utc_dt = _parse_to_utc(current_data.provenance.model_valid_utc)

        # Check for existing record at this grid point and valid timestamp
        query = select(AQIRecord).where(
            AQIRecord.grid_latitude == grid_lat,
            AQIRecord.grid_longitude == grid_lon,
            AQIRecord.model_valid_utc == model_valid_utc_dt,
        )
        existing = (await session.execute(query)).scalar_one_or_none()
        if existing:
            # Update expiry and retrieved timestamps
            existing.retrieved_at_utc = datetime.now(timezone.utc)
            existing.expires_at_utc = datetime.now(timezone.utc) + timedelta(seconds=settings.AQI_CACHE_TTL_SECONDS)
            await session.commit()
            await session.refresh(existing)
            return existing

        # Extract pollutants safely
        p = current_data.pollutants
        cpcb = current_data.cpcb_model_proxy
        epa = current_data.us_epa_model_proxy
        prov = current_data.provenance

        # Create geometry: WKTElement for PostGIS, string representation for SQLite
        is_postgres = session.bind.dialect.name == "postgresql" if session.bind else False
        geom_val = WKTElement(f"POINT({grid_lon} {grid_lat})", srid=4326) if is_postgres else f"POINT({grid_lon} {grid_lat})"

        record = AQIRecord(
            location_key=location_key,
            grid_latitude=grid_lat,
            grid_longitude=grid_lon,
            geom=geom_val,
            # Nullable pollutants (never fabricated)
            pm2_5=p.pm2_5.concentration,
            pm10=p.pm10.concentration,
            no2=p.no2.concentration,
            so2=p.so2.concentration,
            co=p.co.concentration,
            o3=p.o3.concentration,
            nh3=p.nh3.concentration if p.nh3 else None,
            pb=p.pb.concentration if p.pb else None,
            uv_index=p.uv_index.concentration if p.uv_index else None,
            # CPCB Model Proxy
            cpcb_proxy_index=cpcb.proxy_index,
            cpcb_category=cpcb.category,
            cpcb_dominant_pollutant=cpcb.dominant_pollutant,
            cpcb_criteria_met=cpcb.criteria_met,
            cpcb_pollutant_count=cpcb.pollutant_count_evaluated,
            # US EPA Model Proxy
            us_proxy_index=epa.proxy_index,
            us_category=epa.category,
            us_dominant_pollutant=epa.dominant_pollutant,
            # Provenance & Resolution Metadata
            source_provider=prov.source_provider,
            native_atmospheric_model=prov.native_atmospheric_model,
            native_spatial_resolution=prov.native_spatial_resolution,
            native_temporal_resolution=prov.native_temporal_resolution,
            temporal_processing=prov.temporal_processing,
            data_provenance=prov.data_provenance,
            is_ground_observation=prov.is_ground_observation,
            # Timestamps
            model_cycle_utc=None,  # Nullable: never fabricated
            model_valid_utc=model_valid_utc_dt,
            model_valid_local=prov.model_valid_local,
            retrieved_at_utc=datetime.now(timezone.utc),
            expires_at_utc=datetime.now(timezone.utc) + timedelta(seconds=settings.AQI_CACHE_TTL_SECONDS),
        )

        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record

    @staticmethod
    async def query_nearby_grids(
        session: AsyncSession,
        latitude: float,
        longitude: float,
        radius_km: float,
        limit: int = 10,
        target_time_utc: Optional[datetime] = None,
        include_forecast: bool = False,
    ) -> List[Tuple[AQIRecord, float]]:
        """Query atmospheric model grids within radius_km.

        Scientific Selection Policy:
        1. Current Conditions: Evaluates records valid at or prior to target_time_utc (model_valid_utc <= target_time).
           Furthest-future forecast records (model_valid_utc > target_time) are strictly excluded from current AQI.
        2. Forecast Policy: When include_forecast is True, future model forecasts are also evaluated.
        3. Deduplication: Per unique (grid_latitude, grid_longitude), the latest valid record is returned.
        4. Spatial Indexing: Uses PostGIS ST_DWithin / ST_Distance with functional GiST index on PostgreSQL.
        5. SQLite Fallback: Uses bounding-box prefiltering with Haversine distance.
        """
        eval_dt = target_time_utc or datetime.now(timezone.utc)
        if eval_dt.tzinfo is None:
            eval_dt = eval_dt.replace(tzinfo=timezone.utc)

        dialect_name = session.bind.dialect.name if session.bind else "sqlite"

        if dialect_name == "postgresql":
            # Native PostGIS spatial query using geography casting for metric distance
            # Deduplicate by (grid_latitude, grid_longitude) taking latest model_valid_utc up to eval_dt
            pt_geog = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326).cast(Geography)
            dist_km_expr = (func.ST_Distance(cast(AQIRecord.geom, Geography), pt_geog) / 1000.0).label("distance_km")

            rn_expr = (
                func.row_number()
                .over(
                    partition_by=[AQIRecord.grid_latitude, AQIRecord.grid_longitude],
                    order_by=AQIRecord.model_valid_utc.desc(),
                )
                .label("rn")
            )

            where_clauses = [
                func.ST_DWithin(cast(AQIRecord.geom, Geography), pt_geog, radius_km * 1000.0)
            ]
            if not include_forecast:
                where_clauses.append(AQIRecord.model_valid_utc <= eval_dt)

            subq = (
                select(
                    AQIRecord.id.label("rec_id"),
                    dist_km_expr,
                    rn_expr,
                )
                .where(*where_clauses)
                .subquery()
            )

            stmt = (
                select(AQIRecord, subq.c.distance_km)
                .join(subq, AQIRecord.id == subq.c.rec_id)
                .where(subq.c.rn == 1)
                .order_by(subq.c.distance_km.asc())
                .limit(limit)
            )
            res = await session.execute(stmt)
            rows = res.all()
            return [(row[0], float(round(row[1], 3))) for row in rows]

        # SQLite / In-Memory Fallback: Filter by approximate bounding box then compute Haversine
        delta_lat = radius_km / 111.0
        cos_lat = max(0.01, math.cos(math.radians(latitude)))
        delta_lon = radius_km / (111.0 * cos_lat)

        where_clauses = [
            AQIRecord.grid_latitude.between(latitude - delta_lat, latitude + delta_lat),
            AQIRecord.grid_longitude.between(longitude - delta_lon, longitude + delta_lon),
        ]
        if not include_forecast:
            where_clauses.append(AQIRecord.model_valid_utc <= eval_dt)

        stmt = select(AQIRecord).where(*where_clauses)
        res = await session.execute(stmt)
        candidates = res.scalars().all()

        # Deduplicate to keep only the latest record up to eval_dt per unique grid cell
        latest_by_grid: dict[tuple[float, float], AQIRecord] = {}
        for cand in candidates:
            grid_pt = (round(cand.grid_latitude, 4), round(cand.grid_longitude, 4))
            cand_valid = cand.model_valid_utc.replace(tzinfo=timezone.utc) if cand.model_valid_utc.tzinfo is None else cand.model_valid_utc
            if grid_pt not in latest_by_grid:
                latest_by_grid[grid_pt] = cand
            else:
                curr_valid = latest_by_grid[grid_pt].model_valid_utc
                if curr_valid.tzinfo is None:
                    curr_valid = curr_valid.replace(tzinfo=timezone.utc)
                if cand_valid > curr_valid:
                    latest_by_grid[grid_pt] = cand

        results: List[Tuple[AQIRecord, float]] = []
        for cand in latest_by_grid.values():
            dist = haversine_distance_km(latitude, longitude, cand.grid_latitude, cand.grid_longitude)
            if dist <= radius_km:
                results.append((cand, dist))

        # Sort by distance ascending, then latest validity timestamp
        results.sort(key=lambda item: (item[1], -item[0].model_valid_utc.timestamp()))
        return results[:limit]

    @staticmethod
    def record_to_grid_item(
        record: AQIRecord,
        distance_km: float,
        evaluation_time: Optional[datetime] = None,
    ) -> NearbyAQIGridItem:
        """Convert a database AQIRecord to a validated NearbyAQIGridItem schema."""
        eval_dt = evaluation_time or datetime.now(timezone.utc)
        if eval_dt.tzinfo is None:
            eval_dt = eval_dt.replace(tzinfo=timezone.utc)

        rec_valid = record.model_valid_utc
        if rec_valid.tzinfo is None:
            rec_valid = rec_valid.replace(tzinfo=timezone.utc)

        # Freshness determination: mark stale if record is older than configured cache TTL
        is_stale = (eval_dt - rec_valid).total_seconds() > settings.AQI_CACHE_TTL_SECONDS
        pollutants_coll = PollutantsCollection(
            pm2_5=PollutantDetail(concentration=record.pm2_5, unit="µg/m³"),
            pm10=PollutantDetail(concentration=record.pm10, unit="µg/m³"),
            no2=PollutantDetail(concentration=record.no2, unit="µg/m³"),
            o3=PollutantDetail(concentration=record.o3, unit="µg/m³"),
            so2=PollutantDetail(concentration=record.so2, unit="µg/m³"),
            co=PollutantDetail(concentration=record.co, unit="mg/m³"),
            nh3=PollutantDetail(concentration=record.nh3, unit="µg/m³") if record.nh3 is not None else None,
            pb=PollutantDetail(concentration=record.pb, unit="µg/m³") if record.pb is not None else None,
            uv_index=PollutantDetail(concentration=record.uv_index, unit="index") if record.uv_index is not None else None,
        )

        cpcb_proxy = None
        if record.cpcb_criteria_met and record.cpcb_proxy_index is not None:
            cpcb_proxy = CPCBModelProxyResponse(
                proxy_index=record.cpcb_proxy_index,
                category=record.cpcb_category or "Unknown",
                dominant_pollutant=record.cpcb_dominant_pollutant,
                index_type="CPCB_BREAKPOINT_BASED_MODEL_PROXY",
                criteria_met=record.cpcb_criteria_met,
                pollutant_count_evaluated=record.cpcb_pollutant_count,
                sub_indices={},
                regulatory_disclaimer="This value is a point-in-time model proxy applied to atmospheric reanalysis data.",
                criteria_explanation="CPCB minimum criteria met.",
            )

        epa_proxy = None
        if record.us_proxy_index is not None:
            epa_proxy = USEPAModelProxyResponse(
                proxy_index=record.us_proxy_index,
                category=record.us_category,
                dominant_pollutant=record.us_dominant_pollutant,
                index_type="US_EPA_BREAKPOINT_BASED_MODEL_PROXY",
                sub_indices={},
                regulatory_disclaimer="This value is a point-in-time model proxy applied to atmospheric reanalysis data.",
            )

        provenance = ProvenanceMetadata(
            source_provider=record.source_provider,
            native_atmospheric_model=record.native_atmospheric_model,
            native_spatial_resolution=record.native_spatial_resolution,
            native_temporal_resolution=record.native_temporal_resolution,
            temporal_processing=record.temporal_processing,
            data_provenance=record.data_provenance,
            is_ground_observation=record.is_ground_observation,
            model_cycle_utc=None,
            model_valid_utc=record.model_valid_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            model_valid_local=record.model_valid_local,
            retrieved_at_utc=record.retrieved_at_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

        return NearbyAQIGridItem(
            grid_latitude=record.grid_latitude,
            grid_longitude=record.grid_longitude,
            distance_km=distance_km,
            model_valid_utc=record.model_valid_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            model_valid_local=record.model_valid_local,
            cpcb_model_proxy=cpcb_proxy,
            us_epa_model_proxy=epa_proxy,
            pollutants=pollutants_coll,
            provenance=provenance,
            spatial_resolution=record.native_spatial_resolution,
            is_stale=is_stale,
        )


aqi_persistence_service = AQIPersistenceService()
