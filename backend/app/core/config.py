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
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    OLLAMA_EMBEDDING_MODEL: str = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

    # LangGraph Settings
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    SEARCH_MAX_RESULTS: int = int(os.getenv("SEARCH_MAX_RESULTS", "10"))
    ANALYSIS_MAX_PAPERS: int = int(os.getenv("ANALYSIS_MAX_PAPERS", "5"))

    # Vector Database Settings
    QDRANT_BASE_URL: str = os.getenv("QDRANT_BASE_URL", "http://localhost:6333")
    QDRANT_COLLECTIONS: list[str] = ["papers", "search_history", "citations", "generated_docs"]

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
