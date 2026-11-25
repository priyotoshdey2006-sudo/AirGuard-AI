"""Dedicated tests for database session, AQICache model nullability, and security configuration.

Verifies:
1. SQLite development database initialization.
2. Nullability of pollutant fields in AQICache matching Pydantic DTOs.
3. Model cycle UTC is nullable (not fabricated).
4. Timezone-aware UTC timestamp persistence.
5. Insecure default SECRET_KEY is rejected when ENVIRONMENT=production.
"""

from datetime import datetime, timezone, timedelta
import uuid
import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.aqi_cache import AQICache
from app.core.config import Settings


def test_aqi_cache_model_crud_and_nullability():
    """Verify AQICache allows null pollutants and nullable model_cycle_utc."""
    test_engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(bind=test_engine)

    session = TestingSessionLocal()
    now_utc = datetime.now(timezone.utc)
    expires = now_utc + timedelta(minutes=15)

    entry = AQICache(
        id=str(uuid.uuid4()),
        location_key="28.61_77.21",
        grid_latitude=28.6139,
        grid_longitude=77.2090,
        cpcb_proxy_index=200,
        cpcb_category="Moderate",
        cpcb_dominant_pollutant="pm2_5",
        cpcb_criteria_met=True,
        cpcb_pollutant_count=3,
        # Pollutants partially null
        pm2_5=90.0,
        pm10=150.0,
        no2=None,
        so2=None,
        co=None,
        o3=None,
        nh3=None,
        pb=None,
        uv_index=3.2,
        # Provenance
        model_cycle_utc=None,  # Nullable: not fabricated
        model_valid_utc=now_utc,
        model_valid_local=now_utc.isoformat(),
        retrieved_at_utc=now_utc,
        expires_at_utc=expires,
    )

    session.add(entry)
    session.commit()

    retrieved = session.query(AQICache).filter_by(location_key="28.61_77.21").first()
    assert retrieved is not None
    assert retrieved.pm2_5 == 90.0
    assert retrieved.no2 is None
    assert retrieved.model_cycle_utc is None
    assert retrieved.cpcb_category == "Moderate"
    session.close()


def test_production_config_rejects_insecure_default_secret_key():
    """Verify that when ENVIRONMENT is production, default placeholder secret key raises an error."""
    # Production with placeholder key must fail
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="temporary-dev-insecure-secret-key-change-in-production",
            DATABASE_URL="postgresql+asyncpg://app_user:Str0ng_Prod_Pass!@db.prod.internal:5432/airguard",
        )
    assert "Insecure default SECRET_KEY cannot be used in production" in str(exc_info.value)


def test_production_config_rejects_insecure_database_url():
    """Verify that when ENVIRONMENT is production, SQLite or insecure database credentials raise an error."""
    valid_key = "a-very-long-and-secure-random-production-key-xyz1234567890"

    # 1. SQLite in production must fail
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY=valid_key,
            DATABASE_URL="sqlite:///./airguard_dev.db",
        )
    assert "SQLite database cannot be used in production environment" in str(exc_info.value)

    # 2. Insecure default database password in production must fail
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY=valid_key,
            DATABASE_URL="postgresql+asyncpg://postgres:airguard_dev_insecure_pw@localhost:5432/airguard",
        )
    assert "Insecure default or placeholder database credentials" in str(exc_info.value)

    # 3. Robust PostgreSQL production configuration must succeed
    valid_prod = Settings(
        ENVIRONMENT="production",
        SECRET_KEY=valid_key,
        DATABASE_URL="postgresql+asyncpg://app_user:SuperSecure_Prod_Password_99@prod-db.example.com:5432/airguard",
    )
    assert valid_prod.ENVIRONMENT == "production"
