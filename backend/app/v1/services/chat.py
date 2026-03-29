"""Retail Chat Agent — Chat Service."""

import uuid

from ..agents.runner import invoke_retail_agent
from ..core.history import HistoryStore


def handle_chat(
    agent,
    store: HistoryStore,
    message: str,
    image_b64: str | None = None,
    session_id: str | None = None,
) -> tuple[str, str]:
    """Orchestrate a single chat turn: load history, run agent, persist exchange.

    Args:
        agent: The compiled LangGraph retail agent.
        store: A HistoryStore implementation for loading and saving history.
        message: The customer's current text message.
        image_b64: Optional base64-encoded image for visual product search.
        session_id: Existing session ID, or None to create a new one.

    Returns:
        A ``(response, session_id)`` tuple.
    """
    session_id = session_id or str(uuid.uuid4())
    history = store.get_history(session_id)
    response = invoke_retail_agent(agent, message, history, image_b64)
    store.append_exchange(session_id, message, response)
    return response, session_id
