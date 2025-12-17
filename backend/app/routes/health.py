"""Health check Route Module."""

from typing import Any

from fastapi import APIRouter
from httpx import AsyncClient, HTTPError, TimeoutException

from app.core.config import get_settings

settings = get_settings()

router = APIRouter()


async def get_ollama_models() -> list[dict[str, Any]]:
    """Retrieve available Ollama models."""
    ollama_models = []
    try:
        async with AsyncClient() as http_client:
            response = await http_client.get(
                f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5.0
            )
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
    return ollama_models


async def get_qdrant_collections() -> list[str]:
    """Retrieve Qdrant collections."""
    qdrant_collections = []
    try:
        async with AsyncClient() as http_client:
            response = await http_client.get(
                f"{settings.QDRANT_BASE_URL}/collections", timeout=5.0
            )
            if response.status_code == 200:
                collections_data = response.json()
                for collection in collections_data.get("collections", []):
                    qdrant_collections.append(collection.get("name"))
        return qdrant_collections
    except (HTTPError, TimeoutException):
        qdrant_collections = [{"error": "Could not connect to Qdrant"}]
    return qdrant_collections


@router.get("/health")
async def health() -> dict[str, Any]:
    """
    Check the health of services needed for the application.

    Returns the status of:

    - Available LLM Backends
    - Available Vector Database Collections
    """
    ollama_models = await get_ollama_models()
    qdrant_collections = await get_qdrant_collections()
    return {
        "Ollama Models": ollama_models,
        "Qdrant Collections": qdrant_collections,
    }
