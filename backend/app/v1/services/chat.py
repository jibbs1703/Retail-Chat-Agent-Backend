"""Retail Chat Agent — Chat Service."""

import logging
import uuid

from ..agents.runner import invoke_retail_agent
from ..core.configuration import get_settings
from ..core.db import get_product_by_id
from ..core.history import HistoryStore
from ..core.s3 import generate_presigned_url
from ..core.utilities import (
    embed_image,
    embed_text,
    format_product_results,
    search_products_in_collection,
)
from ..models.chat import ProductMatch

logger = logging.getLogger(__name__)


def _enrich(raw_results: list[dict], embedding_type: str) -> list[ProductMatch]:
    """Enrich raw Qdrant results with PostgreSQL product details and presigned URLs.

    Args:
        raw_results: Output of ``search_products_in_collection``.
        embedding_type: ``"text"`` or ``"image"``.

    Returns:
        List of :class:`ProductMatch` with name, presigned image_url, and product_url.
    """
    products: list[ProductMatch] = []
    for r in raw_results:
        payload = r["product"]
        product_id = payload.get("product_id")
        if product_id is None:
            continue
        db_row = get_product_by_id(product_id) or {}
        logger.debug(
            "_enrich product_id=%r db_row keys=%r s3_urls=%r",
            product_id,
            list(db_row.keys()) if db_row else [],
            db_row.get("product_s3_image_urls"),
        )

        db_urls = db_row.get("product_s3_image_urls") or []
        s3_url = db_urls[0] if db_urls else None
        image_url: str | None = (
            generate_presigned_url(s3_url) if s3_url else None
        ) or s3_url

        products.append(
            ProductMatch(
                product_id=str(product_id),
                score=r["score"],
                name=db_row.get("product_title"),
                image_url=image_url,
                product_url=db_row.get("product_url"),
            )
        )
    return products


def handle_chat(
    agent,
    store: HistoryStore,
    message: str,
    image_b64: str | None = None,
    session_id: str | None = None,
) -> tuple[str, str, list[ProductMatch]]:
    """Orchestrate a single chat turn.

    Searches both the text and image Qdrant collections directly, enriches the
    results with PostgreSQL product details and presigned S3 image URLs, and
    also runs the conversational agent so it can reason over the same results.

    Args:
        agent: The compiled LangGraph retail agent.
        store: A HistoryStore implementation for loading and saving history.
        message: The customer's text description of the product they want.
        image_b64: Optional base64-encoded image for direct CLIP image search.
        session_id: Existing session ID, or None to create a new one.

    Returns:
        A ``(response, session_id, products)`` tuple where ``products`` is a
        list of enriched :class:`ProductMatch` objects.
    """
    session_id = session_id or str(uuid.uuid4())
    history = store.get_history(session_id)
    settings = get_settings()

    # --- Text search (always) ---
    text_raw: list[dict] = []
    if message:
        text_vector = embed_text(message)
        text_raw = search_products_in_collection(
            settings.qdrant_text_collection, text_vector
        )
    text_products = _enrich(text_raw, "text")

    # --- Image search (only when image is provided) ---
    image_raw: list[dict] = []
    image_results: str | None = None
    if image_b64:
        image_vector = embed_image(image_b64)
        image_raw = search_products_in_collection(
            settings.qdrant_image_collection, image_vector
        )
        image_results = format_product_results(image_raw)
    image_products = _enrich(image_raw, "image")

    products = text_products + image_products

    response = invoke_retail_agent(agent, message, history, image_results=image_results)
    store.append_exchange(session_id, message, response)
    return response, session_id, products
