"""Tests for backend.app.v1.services.chat — handle_chat."""

from unittest.mock import MagicMock, patch

import pytest

from backend.app.v1.services.chat import handle_chat


@pytest.fixture()
def service_patches():
    """Patch all external I/O dependencies of handle_chat."""
    with (
        patch("backend.app.v1.services.chat.embed_text", return_value=[0.1] * 768),
        patch("backend.app.v1.services.chat.embed_image", return_value=[0.1] * 768),
        patch("backend.app.v1.services.chat.search_products_in_collection", return_value=[]),
        patch("backend.app.v1.services.chat.format_product_results", return_value=""),
        patch("backend.app.v1.services.chat.get_product_by_id", return_value=None),
        patch("backend.app.v1.services.chat.generate_presigned_url", return_value=None),
    ):
        yield


@pytest.mark.unit
def test_generates_session_id_when_none(service_patches):
    agent = MagicMock()
    store = MagicMock()
    store.get_history.return_value = []

    with patch("backend.app.v1.services.chat.invoke_retail_agent", return_value="Products found!"):
        _, session_id, _ = handle_chat(agent, store, "blue shoes")

    assert session_id is not None
    assert len(session_id) == 36


@pytest.mark.unit
def test_uses_provided_session_id(service_patches):
    agent = MagicMock()
    store = MagicMock()
    store.get_history.return_value = []

    with patch("backend.app.v1.services.chat.invoke_retail_agent", return_value="result"):
        _, session_id, _ = handle_chat(agent, store, "query", session_id="my-sess")

    assert session_id == "my-sess"


@pytest.mark.unit
def test_loads_history_for_session(service_patches):
    agent = MagicMock()
    store = MagicMock()
    prior = [
        {"role": "user", "content": "jacket"},
        {"role": "assistant", "content": "Here are jackets."},
    ]
    store.get_history.return_value = prior

    with patch("backend.app.v1.services.chat.invoke_retail_agent", return_value="r") as mock_run:
        handle_chat(agent, store, "more options", session_id="s1")

    store.get_history.assert_called_once_with("s1")
    mock_run.assert_called_once_with(agent, "more options", prior, image_results=None)


@pytest.mark.unit
def test_passes_image_results_to_runner():
    agent = MagicMock()
    store = MagicMock()
    store.get_history.return_value = []

    with (
        patch("backend.app.v1.services.chat.embed_text", return_value=[0.1] * 768),
        patch("backend.app.v1.services.chat.embed_image", return_value=[0.1, 0.2]),
        patch("backend.app.v1.services.chat.search_products_in_collection", return_value=[]),
        patch(
            "backend.app.v1.services.chat.format_product_results",
            return_value="No matching products found.",
        ),
        patch("backend.app.v1.services.chat.get_product_by_id", return_value=None),
        patch("backend.app.v1.services.chat.generate_presigned_url", return_value=None),
        patch(
            "backend.app.v1.services.chat.invoke_retail_agent", return_value="visual match"
        ) as mock_run,
    ):
        handle_chat(agent, store, "red jacket", image_b64="abc123", session_id="img-sess")

    mock_run.assert_called_once_with(
        agent, "red jacket", [], image_results="No matching products found."
    )


@pytest.mark.unit
def test_persists_exchange(service_patches):
    agent = MagicMock()
    store = MagicMock()
    store.get_history.return_value = []

    with patch("backend.app.v1.services.chat.invoke_retail_agent", return_value="great finds!"):
        _, session_id, _ = handle_chat(agent, store, "leather belt", session_id="sess")

    store.append_exchange.assert_called_once_with("sess", "leather belt", "great finds!")


@pytest.mark.unit
def test_returns_agent_response(service_patches):
    agent = MagicMock()
    store = MagicMock()
    store.get_history.return_value = []

    with patch(
        "backend.app.v1.services.chat.invoke_retail_agent",
        return_value="perfect match!",
    ):
        response, _, _ = handle_chat(agent, store, "any query")

    assert response == "perfect match!"


@pytest.mark.unit
def test_returns_enriched_products_from_text_search():
    """Products from the text collection are returned with DB details."""
    agent = MagicMock()
    store = MagicMock()
    store.get_history.return_value = []
    qdrant_hit = {"score": 0.92, "product": {"product_id": 123, "embedding_type": "text"}}
    db_row = {
        "product_title": "Blue Jacket",
        "product_url": "https://example.com/blue-jacket",
    }

    with (
        patch("backend.app.v1.services.chat.embed_text", return_value=[0.1] * 768),
        patch(
            "backend.app.v1.services.chat.search_products_in_collection", return_value=[qdrant_hit]
        ),
        patch("backend.app.v1.services.chat.format_product_results", return_value=""),
        patch("backend.app.v1.services.chat.get_product_by_id", return_value=db_row),
        patch("backend.app.v1.services.chat.generate_presigned_url", return_value=None),
        patch("backend.app.v1.services.chat.invoke_retail_agent", return_value="result"),
    ):
        _, _, products = handle_chat(agent, store, "blue jacket")

    assert len(products) == 1
    assert products[0].product_id == "123"
    assert products[0].score == 0.92
    assert products[0].name == "Blue Jacket"
    assert products[0].image_url is None


@pytest.mark.unit
def test_returns_enriched_products_with_presigned_url():
    """Image collection results include a presigned S3 URL."""
    agent = MagicMock()
    store = MagicMock()
    store.get_history.return_value = []
    qdrant_hit = {
        "score": 0.88,
        "product": {
            "product_id": 456,
            "embedding_type": "image",
            "product_s3_image_url": "https://bucket.s3.us-east-2.amazonaws.com/456/image_0.jpg",
        },
    }

    with (
        patch("backend.app.v1.services.chat.embed_text", return_value=[0.1] * 768),
        patch("backend.app.v1.services.chat.embed_image", return_value=[0.1] * 768),
        patch(
            "backend.app.v1.services.chat.search_products_in_collection", return_value=[qdrant_hit]
        ),
        patch("backend.app.v1.services.chat.format_product_results", return_value=""),
        patch(
            "backend.app.v1.services.chat.get_product_by_id",
            return_value={
                "product_title": "Red Dress",
                "product_s3_image_urls": [
                    "https://bucket.s3.us-east-2.amazonaws.com/456/image_0.jpg"
                ],
            },
        ),
        patch(
            "backend.app.v1.services.chat.generate_presigned_url",
            return_value="https://signed.example.com/img",
        ),
        patch("backend.app.v1.services.chat.invoke_retail_agent", return_value="result"),
    ):
        _, _, products = handle_chat(agent, store, "", image_b64="abc123")

    assert len(products) == 1
    assert products[0].product_id == "456"
    assert products[0].image_url == "https://signed.example.com/img"
