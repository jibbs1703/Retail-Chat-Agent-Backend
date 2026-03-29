"""Tests for backend.app.v1.core.history — RedisHistoryStore."""

import pytest

from backend.app.v1.core.history import HistoryStore


@pytest.mark.unit
def test_implements_protocol(history_store):
    assert isinstance(history_store, HistoryStore)


@pytest.mark.unit
def test_get_history_empty(history_store):
    assert history_store.get_history("session-1") == []


@pytest.mark.unit
def test_append_and_get(history_store):
    history_store.append_exchange("session-1", "blue sneakers", "Here are some options!")
    history = history_store.get_history("session-1")
    assert len(history) == 2
    assert history[0] == {"role": "user", "content": "blue sneakers"}
    assert history[1] == {"role": "assistant", "content": "Here are some options!"}


@pytest.mark.unit
def test_multiple_exchanges_order(history_store):
    history_store.append_exchange("s", "msg1", "reply1")
    history_store.append_exchange("s", "msg2", "reply2")
    history = history_store.get_history("s")
    assert history[0]["content"] == "msg1"
    assert history[2]["content"] == "msg2"


@pytest.mark.unit
def test_list_sessions(history_store):
    history_store.append_exchange("sess-a", "hello", "hi")
    sessions = history_store.list_sessions()
    assert "sess-a" in sessions


@pytest.mark.unit
def test_delete_session(history_store):
    history_store.append_exchange("to-delete", "query", "result")
    assert history_store.delete_session("to-delete") is True
    assert history_store.get_history("to-delete") == []


@pytest.mark.unit
def test_delete_nonexistent_session_returns_false(history_store):
    assert history_store.delete_session("ghost") is False


@pytest.mark.unit
def test_max_messages_trim(fake_redis):
    """History must not exceed max_messages entries."""
    from backend.app.v1.core.history import RedisHistoryStore

    store = RedisHistoryStore(fake_redis, max_messages=4)
    for i in range(4):
        store.append_exchange("s", f"q{i}", f"a{i}")
    history = store.get_history("s")
    assert len(history) == 4
