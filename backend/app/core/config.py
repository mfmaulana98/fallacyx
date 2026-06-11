"""Application configuration loaded from environment variables (.env)."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    # App
    app_env: Literal["development", "staging", "production"] = "development"
    app_version: str = "1.0.0"

    # CORS
    cors_origins: str = "http://localhost:5173,https://fallacyx.revonalar.io"

    # vLLM
    vllm_host: str = "localhost"
    vllm_port: int = 8000
    vllm_model_name: str = "meta-llama/Llama-3-70b-instruct"
    vllm_max_tokens: int = 2048
    vllm_temperature: float = 0.1
    vllm_top_p: float = 0.95
    vllm_timeout_seconds: float = 30.0

    # Supabase
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # Whisper (speech-to-text)
    whisper_model_size: str = "large-v3"
    whisper_device: str = "cuda"
    whisper_compute_type: str = "float16"

    # YouTube pipeline
    youtube_max_duration_seconds: int = 7200
    youtube_cache_ttl_seconds: float = 86400.0
    audio_temp_dir: str = "/tmp/fallacyx-audio"

    # Audio upload pipeline
    audio_max_file_size_bytes: int = 100 * 1024 * 1024
    audio_max_duration_seconds: int = 7200

    @property
    def vllm_base_url(self) -> str:
        return f"http://{self.vllm_host}:{self.vllm_port}"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
