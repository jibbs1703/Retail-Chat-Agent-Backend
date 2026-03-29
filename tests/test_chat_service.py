"""Tests for backend.app.v1.services.chat — handle_chat."""

from unittest.mock import MagicMock, patch

import pytest

from backend.app.v1.services.chat import handle_chat


@pytest.mark.unit
def test_generates_session_id_when_none():
    agent = MagicMock()
    store = MagicMock()
    store.get_history.return_value = []

    with patch("backend.app.v1.services.chat.invoke_retail_agent", return_value="Products found!"):
        _, session_id = handle_chat(agent, store, "blue shoes")

    assert session_id is not None
    assert len(session_id) == 36


@pytest.mark.unit
def test_uses_provided_session_id():
    agent = MagicMock()
    store = MagicMock()
    store.get_history.return_value = []

    with patch("backend.app.v1.services.chat.invoke_retail_agent", return_value="result"):
        _, session_id = handle_chat(agent, store, "query", session_id="my-sess")

    assert session_id == "my-sess"


@pytest.mark.unit
def test_loads_history_for_session():
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
    mock_run.assert_called_once_with(agent, "more options", prior, None)


@pytest.mark.unit
def test_passes_image_to_runner():
    agent = MagicMock()
    store = MagicMock()
    store.get_history.return_value = []

    with patch(
        "backend.app.v1.services.chat.invoke_retail_agent", return_value="visual match"
    ) as mock_run:
        handle_chat(agent, store, "", image_b64="abc123", session_id="img-sess")

    mock_run.assert_called_once_with(agent, "", [], "abc123")


@pytest.mark.unit
def test_persists_exchange():
    agent = MagicMock()
    store = MagicMock()
    store.get_history.return_value = []

    with patch("backend.app.v1.services.chat.invoke_retail_agent", return_value="great finds!"):
        _, session_id = handle_chat(agent, store, "leather belt", session_id="sess")

    store.append_exchange.assert_called_once_with("sess", "leather belt", "great finds!")


@pytest.mark.unit
def test_returns_agent_response():
    agent = MagicMock()
    store = MagicMock()
    store.get_history.return_value = []

    with patch(
        "backend.app.v1.services.chat.invoke_retail_agent",
        return_value="perfect match!",
    ):
        response, _ = handle_chat(agent, store, "any query")

    assert response == "perfect match!"
