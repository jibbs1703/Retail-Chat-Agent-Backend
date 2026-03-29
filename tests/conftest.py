"""Shared pytest fixtures for the Retail Chat Agent backend tests."""

from unittest.mock import MagicMock, patch

import fakeredis
import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

from backend.app.v1.core.history import RedisHistoryStore


@pytest.fixture
def fake_redis():
    """In-memory Redis substitute (no real Redis needed)."""
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture
def history_store(fake_redis):
    """RedisHistoryStore backed by fakeredis."""
    return RedisHistoryStore(fake_redis)


@pytest.fixture
def mock_agent():
    """Mocked LangGraph agent that returns a canned product recommendation."""
    agent = MagicMock()
    agent.invoke.return_value = {
        "messages": [AIMessage(content="Here are some matching products!")]
    }
    return agent


@pytest.fixture
def client(mock_agent, fake_redis):
    """FastAPI TestClient with mocked agent and in-memory Redis."""
    from backend.app.v1.server.server import app

    with (
        patch(
            "backend.app.v1.server.server.get_retail_agent",
            return_value=mock_agent,
        ),
        patch(
            "backend.app.v1.server.server.redis.Redis.from_url",
            return_value=fake_redis,
        ),
    ):
        with TestClient(app) as c:
            yield c
