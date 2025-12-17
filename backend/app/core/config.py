"""Configuration settings for Research Paper Agent."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class ConfigSettings(BaseSettings):
    """
    Application configuration settings for Research Paper Agent.

    The settings can be:
    - loaded from environment variables
    - loaded from a .env file
    - or hardcoded defaults.
    """

    # Application Settings
    APP_API_PREFIX: str = "/api/v1"
    APP_DESCRIPTION: str = "Research Paper Agent Backend Service"
    APP_NAME: str = "Research Paper Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    # LLM Settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8B")

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> ConfigSettings:
    """Get or create a cached Settings instance.

    Returns:
        ConfigSettings: Cached application settings instance.
    """
    return ConfigSettings()
