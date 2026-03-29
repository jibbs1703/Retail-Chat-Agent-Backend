"""Retail Chat Agent — Core Utilities Module.

Provides helpers for:
  - Creating OpenAI and Qdrant clients
  - Generating text embeddings via OpenAI
  - Describing product images via GPT-4o vision
  - Querying the Qdrant vector database
  - Formatting product search results

Note on image embeddings: product images are described via GPT-4o vision and
the resulting description is embedded with the same text embedding model used
for text search. This keeps dependencies minimal while leveraging OpenAI's
strong vision capabilities. If the vector collections were built with a
dedicated image encoder (e.g. CLIP), replace `describe_image` and
`embed_text` accordingly.
"""

import requests
from openai import OpenAI
from qdrant_client import QdrantClient

from .configuration import get_settings


def get_openai_client() -> OpenAI:
    """Create an OpenAI client using settings."""
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError(
            "OpenAI API key not configured. Set OPENAI_API_KEY in the .env file."
        )
    return OpenAI(api_key=settings.openai_api_key)


def get_qdrant_client() -> QdrantClient:
    """Create a Qdrant client using settings."""
    settings = get_settings()
    return QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)


def embed_text(text: str) -> list[float]:
    """Generate a text embedding vector using OpenAI.

    Args:
        text: The text to embed.

    Returns:
        A list of floats representing the embedding vector.
    """
    settings = get_settings()
    client = get_openai_client()
    response = client.embeddings.create(
        model=settings.openai_embedding_model,
        input=text,
    )
    return response.data[0].embedding


def describe_image(image_b64: str) -> str:
    """Use GPT-4o vision to produce a detailed product description from an image.

    The description is later embedded and used to query the image collection,
    so it focuses on attributes relevant to retail search (color, material,
    style, category).

    Args:
        image_b64: Base64-encoded image (JPEG or PNG).

    Returns:
        A natural-language product description.
    """
    settings = get_settings()
    client = get_openai_client()
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Describe this retail product image in detail for search"
                            " purposes. Include: product category, color(s), material,"
                            " style, key features, and any visible branding or"
                            " distinctive characteristics."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                    },
                ],
            }
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content


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
    results = client.search(
        collection_name=collection,
        query_vector=vector,
        limit=top_k,
        with_payload=True,
    )
    return [{"score": round(r.score, 4), "product": r.payload} for r in results]


def format_product_results(results: list[dict]) -> str:
    """Format a list of product search results into a readable string.

    Args:
        results: Output of :func:`search_products_in_collection`.

    Returns:
        A formatted multi-line string for the agent to include in its response.
    """
    if not results:
        return "No matching products found."

    lines = []
    for r in results:
        p = r["product"]
        name = p.get("name") or p.get("product_name") or "Unknown Product"
        desc = p.get("description") or p.get("product_description") or ""
        score = r["score"]
        line = f"- **{name}** (similarity: {score})"
        if desc:
            line += f": {desc[:200]}"
        lines.append(line)
    return "\n".join(lines)


def check_qdrant_connection() -> bool:
    """Return True if the Qdrant service is reachable, False otherwise."""
    settings = get_settings()
    try:
        response = requests.get(
            f"http://{settings.qdrant_host}:{settings.qdrant_port}/healthz",
            timeout=3.0,
        )
        return response.status_code == 200
    except requests.RequestException:
        return False
