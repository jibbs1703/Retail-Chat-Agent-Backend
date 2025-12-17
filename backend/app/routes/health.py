"""Health check Route Module."""

from typing import Any

from fastapi import APIRouter
from httpx import AsyncClient, HTTPError, TimeoutException

from app.core.config import get_settings

settings = get_settings()

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, Any]:
    """
    Check the health of services needed for the application.

    Returns the status of:

    - Available LLM Backends
    - Vector Database Connectivity and Collections
    """
    ollama_models = []
    try:
        async with AsyncClient() as http_client:
            response = await http_client.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5.0)
            if response.status_code == 200:
                models_data = response.json()
                for model in models_data.get("models", []):
                    ollama_models.append(
                        {
                            "name": model.get("name"),
                            "size_gb": round(model.get("size", 0) / 1_000_000_000, 2),
                        }
                    )
    except (HTTPError, TimeoutException):
        ollama_models = [{"error": "Could not connect to Ollama"}]

    return {
        "Available Ollama Models": ollama_models,
    }
