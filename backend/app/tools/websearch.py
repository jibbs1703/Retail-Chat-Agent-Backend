"""Web Search module for Research Paper Agent."""

import requests

from app.core.config import get_settings

settings = get_settings()


def google_search(
    text: str,
    engine: str = settings.WEB_SEARCH_ENGINE,
    lang: str = settings.WEB_SEARCH_LANGUAGE,
    limit: int = settings.WEB_SEARCH_RESULTS_LIMIT,
) -> dict:
    """
    Make a request to the Web Search API.

    Args:
        text: Search query text
        engine: Search engine to use (default: "google")
        lang: Language code (default: "EN")
        limit: Number of results to return (default: 3)

    Returns:
        JSON response from the Web Search API
    """
    url = f"{settings.WEB_SEARCH_URL}/{engine}/search"
    params = {"text": text, "lang": lang, "limit": limit}

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    result = google_search("What is FastAPI?", limit=5)
    print(result)
