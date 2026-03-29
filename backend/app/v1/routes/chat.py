"""Retail Chat Agent — Chat Route."""

from fastapi import APIRouter, HTTPException, Request

from ..core.history import RedisHistoryStore
from ..models import ChatRequest, ChatResponse
from ..services.chat import handle_chat

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, app_request: Request) -> ChatResponse:
    """Send a text or image query to the retail agent and return product matches."""
    store = RedisHistoryStore(app_request.app.state.redis)
    try:
        response, session_id = handle_chat(
            app_request.app.state.agent,
            store,
            request.message,
            request.image_b64,
            request.session_id,
        )
        return ChatResponse(response=response, session_id=session_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
