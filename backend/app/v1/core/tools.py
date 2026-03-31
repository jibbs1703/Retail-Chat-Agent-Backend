"""Retail Chat Agent — LangChain Tools Module.

Each tool wraps a vector-database query so the LangGraph agent can call them
autonomously during a conversation turn.
"""

from langchain.tools import tool

from .configuration import get_settings
from .utilities import (
    embed_text,
    format_product_results,
    search_products_in_collection,
)


@tool
def search_products_by_text(query: str) -> str:
    """Search for retail products using a text description or query.

    Use this tool when the customer describes what they are looking for in
    words — e.g. "blue leather handbag", "men's running shoes size 10",
    "waterproof hiking jacket".

    Args:
        query: Natural-language description of the desired product.

    Returns:
        A formatted list of the closest matching products from the text
        embedding collection.
    """
    settings = get_settings()
    vector = embed_text(query)
    results = search_products_in_collection(settings.qdrant_text_collection, vector)
    return format_product_results(results)


@tool
def search_products_by_image_description(description: str) -> str:
    """Search for retail products that visually match a product description.

    Use this tool when the customer shares an image or describes a product's
    visual appearance. Pass a detailed description that captures color, style,
    material, product category, and any other visible characteristics.

    Args:
        description: Visual description of the product derived from an image
                     or from the customer's description of how it looks.

    Returns:
        A formatted list of the closest matching products from the image
        embedding collection.
    """
    settings = get_settings()
    vector = embed_text(description)
    results = search_products_in_collection(settings.qdrant_image_collection, vector)
    return format_product_results(results)


def get_all_tools() -> list:
    """Return all tools available to the retail agent.

    Returns:
        List of LangChain tool callables.
    """
    return [search_products_by_text, search_products_by_image_description]
