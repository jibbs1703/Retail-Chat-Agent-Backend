"""Retail Chat Agent Backend Configuration Module."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class BackendSettings(BaseSettings):
    """Application settings for the Retail Chat Agent Backend."""

    load_dotenv()

    application_api_prefix: str = "/api/v1"
    application_description: str = (
        "A backend server for a retail chat agent application."
    )
    application_frontend_url: str = os.getenv("FRONTEND_URL", "")
    application_name: str = "Retail Chat Agent Backend"
    application_version: str = "1.0.0"

    postgres_database: str = os.getenv("POSTGRES_DATABASE", "")
    postgres_host: str = os.getenv("POSTGRES_HOST", "")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", 5432))
    postgres_user: str = os.getenv("POSTGRES_USER", "")

    qdrant_host: str = os.getenv("QDRANT_HOST", "")
    qdrant_image_collection: str = os.getenv("QDRANT_IMAGE_COLLECTION", "")
    qdrant_text_collection: str = os.getenv("QDRANT_TEXT_COLLECTION", "")
    qdrant_port: int = int(os.getenv("QDRANT_PORT", 6333))


@lru_cache
def get_settings() -> BackendSettings:
    """Get application settings with caching."""
    return BackendSettings()
