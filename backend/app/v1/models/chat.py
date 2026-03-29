"""Retail Chat Agent API Models — Chat."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat request payload.

    Either ``message``, ``image_b64``, or both must be provided.
    When ``image_b64`` is supplied the agent will use GPT-4o vision to
    analyse it and search the image embedding collection.
    """

    message: str = Field(default="", description="Customer's text query.")
    session_id: str | None = Field(
        default=None, description="Existing session ID; omit to start a new session."
    )
    image_b64: str | None = Field(
        default=None,
        description=(
            "Base64-encoded product image (JPEG or PNG) for visual product search."
        ),
    )


class ChatResponse(BaseModel):
    """Outgoing chat response payload."""

    response: str
    session_id: str
