"""Application configuration and environment settings."""

from typing import List, Union
import json
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Core Application Settings
    PROJECT_NAME: str = "AirGuard AI"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8000
    
    # Security & JWT
    SECRET_KEY: str = "airguard-development-secret-key-change-in-production-min32"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    ALGORITHM: str = "HS256"

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v_stripped = v.strip()
            if v_stripped.startswith("[") and v_stripped.endswith("]"):
                try:
                    return json.loads(v_stripped)
                except Exception:
                    pass
            return [origin.strip() for origin in v_stripped.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        return []

    # Database (PostgreSQL with PostGIS in production, SQLite dev fallback)
    DATABASE_URL: str = "sqlite:///./airguard_dev.db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_PRE_PING: bool = True

    # Geospatial Query Configuration
    DEFAULT_NEARBY_RADIUS_KM: float = 50.0
    MAX_NEARBY_RADIUS_KM: float = 250.0

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Redis Cache / Rate Limiting (Optional in local dev, recommended in multi-worker production)
    REDIS_URL: str = ""

    # AI Providers (Optional for local deterministic fallback)
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    DEFAULT_AI_PROVIDER: str = "gemini"  # gemini | groq | expert_fallback

    # Environmental APIs
    OPEN_METEO_BASE_URL: str = "https://air-quality-api.open-meteo.com/v1/air-quality"
    OPEN_METEO_WEATHER_URL: str = "https://api.open-meteo.com/v1/forecast"
    AQI_CACHE_TTL_SECONDS: int = 1800  # 30 minutes cache

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        """Ensure production deployment rejects insecure placeholder secrets."""
        if self.ENVIRONMENT.lower() == "production":
            insecure_defaults = [
                "airguard-development-secret-key-change-in-production-min32",
                "replace-with-a-secure-random-secret-key-in-production-min-32-chars",
                "secret",
                "changethis",
                "",
            ]
            key_lower = self.SECRET_KEY.lower() if self.SECRET_KEY else ""
            if (
                not self.SECRET_KEY
                or self.SECRET_KEY in insecure_defaults
                or len(self.SECRET_KEY) < 32
                or "change-in-production" in key_lower
                or "insecure" in key_lower
            ):
                raise ValueError(
                    "Insecure default SECRET_KEY cannot be used in production environment! "
                    "A cryptographically secure secret of at least 32 characters must be configured."
                )

            # Fail fast if production DATABASE_URL is SQLite or contains insecure defaults
            db_url_lower = self.DATABASE_URL.lower() if self.DATABASE_URL else ""
            if db_url_lower.startswith("sqlite"):
                raise ValueError(
                    "SQLite database cannot be used in production environment. "
                    "A production PostgreSQL + PostGIS database URL must be configured."
                )

            insecure_db_patterns = [
                "airguard_dev_insecure_pw",
                "airguard_secure_password_replace_in_prod",
                "postgres:postgres@",
                "set_strong_database_password_here",
                ":password@",
            ]
            if any(pattern in db_url_lower for pattern in insecure_db_patterns):
                raise ValueError(
                    "Insecure default or placeholder database credentials detected in DATABASE_URL for production! "
                    "A secure production database credential must be provided."
                )
        return self


settings = Settings()
