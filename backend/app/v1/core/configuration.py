"""Retail Chat Agent Backend Configuration Module."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class BackendSettings(BaseSettings):
    """Application settings for the Retail Chat Agent Backend."""

    application_api_prefix: str = "/api/v1"
    application_description: str = (
        "A backend server for a retail chat agent application."
    )
    application_frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    application_name: str = "Retail Chat Agent Backend"
    application_version: str = "1.0.0"
    application_image_optimal_size: tuple[int, int] = (224, 224)
    application_image_min_size: tuple[int, int] = (64, 64)
    application_allowed_image_types: list[str] = ["jpeg", "jpg", "png", "webp", "gif"]

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5-nano")

    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_region: str = os.getenv("AWS_REGION", "us-east-2")
    aws_s3_bucket_name: str = os.getenv("AWS_S3_BUCKET_NAME", "")
    aws_s3_presigned_url_expiry: int = 3600

    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    postgres_database: str = os.getenv("POSTGRES_DATABASE", "")
    postgres_host: str = os.getenv("POSTGRES_HOST", "")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", 5432))
    postgres_user: str = os.getenv("POSTGRES_USER", "")

    qdrant_host: str = os.getenv("QDRANT_HOST", "localhost")
    qdrant_image_collection: str = os.getenv("QDRANT_IMAGE_COLLECTION", "")
    qdrant_text_collection: str = os.getenv("QDRANT_TEXT_COLLECTION", "")
    qdrant_port: int = int(os.getenv("QDRANT_PORT", 6333))
    qdrant_top_k: int = int(os.getenv("QDRANT_TOP_K", 5))


@lru_cache
def get_settings() -> BackendSettings:
    """Get application settings with caching."""
    return BackendSettings()
