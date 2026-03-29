"""Retail Chat Agent — Chat History Module."""

import json
from typing import Protocol, runtime_checkable

import redis

_HISTORY_KEY_PREFIX = "retail:history:"
_MAX_MESSAGES = 20


@runtime_checkable
class HistoryStore(Protocol):
    """Protocol for chat history persistence backends."""

    def get_history(self, session_id: str) -> list[dict]: ...

    def list_sessions(self) -> list[str]: ...

    def delete_session(self, session_id: str) -> bool: ...

    def append_exchange(self, session_id: str, user_msg: str, ai_msg: str) -> None: ...


class RedisHistoryStore:
    """Redis-backed implementation of HistoryStore."""

    def __init__(self, client: redis.Redis, max_messages: int = _MAX_MESSAGES) -> None:
        self._client = client
        self._max = max_messages

    def get_history(self, session_id: str) -> list[dict]:
        """Return the last max_messages entries for a session."""
        key = f"{_HISTORY_KEY_PREFIX}{session_id}"
        raw = self._client.lrange(key, -self._max, -1)
        return [json.loads(m) for m in raw]

    def list_sessions(self) -> list[str]:
        """Return all session IDs that have stored history."""
        keys = self._client.keys(f"{_HISTORY_KEY_PREFIX}*")
        return [k.removeprefix(_HISTORY_KEY_PREFIX) for k in keys]

    def delete_session(self, session_id: str) -> bool:
        """Delete all history for a session. Returns True if it existed."""
        key = f"{_HISTORY_KEY_PREFIX}{session_id}"
        return bool(self._client.delete(key))

    def append_exchange(self, session_id: str, user_msg: str, ai_msg: str) -> None:
        """Append a user/AI exchange and trim the list to max_messages pairs."""
        key = f"{_HISTORY_KEY_PREFIX}{session_id}"
        pipe = self._client.pipeline()
        pipe.rpush(key, json.dumps({"role": "user", "content": user_msg}))
        pipe.rpush(key, json.dumps({"role": "assistant", "content": ai_msg}))
        pipe.ltrim(key, -self._max, -1)
        pipe.execute()
