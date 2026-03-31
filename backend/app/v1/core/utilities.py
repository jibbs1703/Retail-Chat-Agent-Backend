"""Retail Chat Agent — Core Utilities Module.

Provides helpers for:
  - Creating a Qdrant client
  - Generating text embeddings via CLIP (openai/clip-vit-large-patch14)
  - Querying the Qdrant vector database
  - Formatting product search results
"""

import base64
from io import BytesIO

import requests
from PIL import Image as PILImage
from qdrant_client import QdrantClient

from .configuration import get_settings

_clip_model = None
_clip_processor = None
_qdrant_client: QdrantClient | None = None
_CLIP_MODEL_NAME: str = "openai/clip-vit-large-patch14"


def _get_device() -> str:
    import torch

    return "cuda" if torch.cuda.is_available() else "cpu"


def _load_clip_model():
    from transformers import CLIPModel

    global _clip_model
    if _clip_model is None:
        _clip_model = CLIPModel.from_pretrained(_CLIP_MODEL_NAME).to(_get_device())
    return _clip_model


def _load_clip_processor():
    from transformers import CLIPProcessor

    global _clip_processor
    if _clip_processor is None:
        _clip_processor = CLIPProcessor.from_pretrained(_CLIP_MODEL_NAME)
    return _clip_processor


def warm_up_clip() -> None:
    """Load the CLIP model and processor into memory.

    Call this once at application startup so the first request is not delayed
    by model weight loading.
    """
    _load_clip_model()
    _load_clip_processor()


def _to_tensor(emb):
    """Extract a plain 2-D tensor from a model output or raw tensor.

    Handles the case where transformers returns a ``BaseModelOutputWithPooling``
    object instead of a bare tensor, depending on the installed version.
    """
    if hasattr(emb, "pooler_output") and emb.pooler_output is not None:
        return emb.pooler_output
    if hasattr(emb, "last_hidden_state"):
        return emb.last_hidden_state[:, 0]
    return emb


def get_qdrant_client() -> QdrantClient:
    """Return a cached Qdrant client, creating it on first call."""
    global _qdrant_client
    if _qdrant_client is None:
        settings = get_settings()
        _qdrant_client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            timeout=30,
            check_compatibility=False,
        )
    return _qdrant_client


def embed_text(text: str) -> list[float]:
    """Generate a normalized text embedding vector using CLIP.

    Args:
        text: The text to embed.

    Returns:
        A list of floats representing the normalized CLIP embedding vector.
    """
    device = _get_device()
    model = _load_clip_model()
    processor = _load_clip_processor()
    inputs = processor(
        text=[text], return_tensors="pt", padding=True, truncation=True, max_length=77
    ).to(device)
    import torch

    with torch.no_grad():
        emb = model.get_text_features(**inputs)
    emb = _to_tensor(emb)
    emb = emb / emb.norm(dim=-1, keepdim=True)
    return emb.cpu().numpy().flatten().astype("float32").tolist()


def embed_image(image_b64: str) -> list[float]:
    """Generate a normalized image embedding vector using CLIP.

    Args:
        image_b64: Base64-encoded image (JPEG or PNG).

    Returns:
        A list of floats representing the normalized CLIP embedding vector.
    """
    image_bytes = base64.b64decode(image_b64)
    image = PILImage.open(BytesIO(image_bytes)).convert("RGB")
    device = _get_device()
    model = _load_clip_model()
    processor = _load_clip_processor()
    inputs = processor(images=image, return_tensors="pt").to(device)
    import torch

    with torch.no_grad():
        emb = model.get_image_features(**inputs)
    emb = _to_tensor(emb)
    emb = emb / emb.norm(dim=-1, keepdim=True)
    return emb.cpu().numpy().flatten().astype("float32").tolist()


def search_products_in_collection(
    collection: str,
    vector: list[float],
    top_k: int | None = None,
) -> list[dict]:
    """Query a Qdrant collection with an embedding vector.

    Args:
        collection: Name of the Qdrant collection to search.
        vector: Query embedding vector.
        top_k: Number of results to return; defaults to settings.qdrant_top_k.

    Returns:
        List of dicts with keys ``score`` and ``product`` (the payload dict).
    """
    settings = get_settings()
    top_k = top_k or settings.qdrant_top_k
    client = get_qdrant_client()
    response = client.query_points(
        collection_name=collection,
        query=vector,
        limit=top_k,
        with_payload=True,
    )
    return [{"score": round(r.score, 4), "product": r.payload} for r in response.points]


def format_product_results(results: list[dict]) -> str:
    """Format a list of product search results into a readable string.

    Args:
        results: Output of :func:`search_products_in_collection`.

    Returns:
        A formatted multi-line string for the agent to include in its response.
    """
    if not results:
        return "No matching products found."

    from .db import get_product_by_id

    lines = []
    for r in results:
        payload = r["product"]

        product_id = payload.get("product_id")
        product_row = get_product_by_id(product_id) if product_id else None

        name = (product_row or {}).get("product_title") or "Unknown Product"
        product_url = (product_row or {}).get("product_url") or ""

        line = f"- **{name}**"
        if product_url:
            line += f" — {product_url}"
        lines.append(line)
    return "\n".join(lines)


def check_qdrant_connection() -> bool:
    """Return True if the Qdrant service is reachable, False otherwise."""
    settings = get_settings()
    try:
        response = requests.get(
            f"http://{settings.qdrant_host}:{settings.qdrant_port}/healthz",
            timeout=30.0,
        )
        return response.status_code == 200
    except requests.RequestException:
        return False
