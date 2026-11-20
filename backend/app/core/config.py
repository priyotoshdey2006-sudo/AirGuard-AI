"""Application configuration and environment settings."""

from typing import List
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

    # Database
    DATABASE_URL: str = "sqlite:///./airguard_dev.db"

    # AI Providers
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    DEFAULT_AI_PROVIDER: str = "gemini"  # gemini | groq | expert_fallback

    # Environmental APIs
    OPEN_METEO_BASE_URL: str = "https://air-quality-api.open-meteo.com/v1/air-quality"
    OPEN_METEO_WEATHER_URL: str = "https://api.open-meteo.com/v1/forecast"
    AQI_CACHE_TTL_SECONDS: int = 1800  # 30 minutes cache


settings = Settings()
