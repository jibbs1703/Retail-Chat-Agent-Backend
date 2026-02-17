"""Retail Chat Agent Backend Configuration Module."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class ApplicationSettings(BaseSettings):
    """Application settings for the Retail Chat Agent Backend."""

    load_dotenv()

    application_api_prefix: str = "/api/v1"
    application_description: str = (
        "A backend service for a retail chat agent application."
    )
    application_name: str = "Retail Chat Agent Backend"
    application_version: str = "1.0.0"

    postgres_database: str = os.getenv("POSTGRES_DATABASE")
    postgres_host: str = os.getenv("POSTGRES_HOST")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD")
    postgres_port: int = int(os.getenv("POSTGRES_PORT"))
    postgres_user: str = os.getenv("POSTGRES_USER")

    qdrant_host: str = os.getenv("QDRANT_HOST")
    qdrant_image_collection: str = os.getenv("QDRANT_IMAGE_COLLECTION")
    qdrant_text_collection: str = os.getenv("QDRANT_TEXT_COLLECTION")
    qdrant_url: str = os.getenv("QDRANT_URL")


@lru_cache
def get_settings() -> ApplicationSettings:
    """Get application settings with caching."""
    return ApplicationSettings()
