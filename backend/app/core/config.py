"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────
    environment: Literal["development", "staging", "production"] = "development"
    cors_origins: list[str] = [
        "http://localhost:3000",
        "https://3000--019dd676-8a08-774e-a49c-fe815807db48.us-east-1-01.gitpod.dev",
    ]

    # ── Database ─────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://nexus:nexus_secret@localhost:5432/nexus_wellness"

    # ── Redis ────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── Auth ─────────────────────────────────────────────────
    jwt_secret_key: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    # ── Nexus AI (OpenAI — voice + complex reasoning) ────────
    nexus_api_key: str = ""
    nexus_api_base_url: str = "https://api.openai.com/v1"
    nexus_model: str = "gpt-4o"
    openai_image_model: str = "dall-e-3"
    openai_video_model: str = "sora-2"

    # ── Groq (fast chat) ─────────────────────────────────────
    groq_api_key: str = ""
    groq_api_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "llama-3.3-70b-versatile"

    # ── External APIs ────────────────────────────────────────
    usda_api_key: str = ""
    usda_api_base_url: str = "https://api.nal.usda.gov/fdc/v1"

    astrology_api_key: str = ""
    astrology_api_base_url: str = "https://api.astrology-engine.example.com/v1"

    # ── Creative media providers ─────────────────────────────
    elevenlabs_api_key: str = ""
    elevenlabs_api_base_url: str = "https://api.elevenlabs.io/v1"
    elevenlabs_music_model: str = "music_v1"

    suno_api_key: str = ""
    suno_api_base_url: str = "https://api.sunoapi.org"
    suno_music_model: str = "V5"

    # ── Storage ──────────────────────────────────────────────
    storage_backend: Literal["local", "s3", "gcs"] = "local"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_s3_bucket: str = "nexus-wellness-media"
    aws_region: str = "us-east-1"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: str | list) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
