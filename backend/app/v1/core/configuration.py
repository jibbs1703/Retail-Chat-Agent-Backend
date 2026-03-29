"""Retail Chat Agent Backend Configuration Module."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class BackendSettings(BaseSettings):
    """Application settings for the Retail Chat Agent Backend."""

    application_api_prefix: str = "/api/v1"
    application_description: str = (
        "A backend server for a retail chat agent application."
    )
    application_frontend_url: str = ""
    application_name: str = "Retail Chat Agent Backend"
    application_version: str = "1.0.0"
    application_image_optimal_size: tuple[int, int] = (224, 224)
    application_image_min_size: tuple[int, int] = (64, 64)
    application_allowed_image_types: list[str] = ["jpeg", "jpg", "png", "webp", "gif"]

    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"

    redis_url: str = "redis://localhost:6379"

    postgres_database: str = ""
    postgres_host: str = ""
    postgres_password: str = ""
    postgres_port: int = 5432
    postgres_user: str = ""

    qdrant_host: str = "localhost"
    qdrant_image_collection: str = "product_images"
    qdrant_text_collection: str = "product_text"
    qdrant_port: int = 6333
    qdrant_top_k: int = 5

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> BackendSettings:
    """Get application settings with caching."""
    return BackendSettings()
