"""Retail Chat Agent — Sessions Routes."""

from fastapi import APIRouter, HTTPException, Request

from ..core.history import RedisHistoryStore

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("")
def list_sessions(request: Request) -> dict:
    """List all session IDs that have stored history in Redis."""
    store = RedisHistoryStore(request.app.state.redis)
    return {"sessions": store.list_sessions()}


@router.get("/{session_id}")
def session_history(session_id: str, request: Request) -> dict:
    """Return the full message history for a given session."""
    store = RedisHistoryStore(request.app.state.redis)
    history = store.get_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "messages": history}


@router.delete("/{session_id}", status_code=204)
def delete_session(session_id: str, request: Request) -> None:
    """Delete all history for a session from Redis."""
    store = RedisHistoryStore(request.app.state.redis)
    if not store.delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
