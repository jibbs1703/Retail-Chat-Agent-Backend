"""Retail Chat Agent API Models — Chat."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat request payload.

    Either ``message``, ``image_b64``, or both must be provided.
    When ``image_b64`` is supplied the image is embedded directly with CLIP and
    the image collection is searched.  The text description is always searched
    against the text collection via the agent's ``search_products_by_text`` tool.
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


class ProductMatch(BaseModel):
    """A single product result enriched with database details."""

    product_id: int
    score: float
    embedding_type: str = Field(
        description="'text' or 'image', indicating which collection matched."
    )
    name: str | None = None
    description: str | None = None
    price: float | None = None
    category: str | None = None
    image_url: str | None = Field(
        default=None,
        description="Presigned S3 URL for the product image (image results only).",
    )


class ChatResponse(BaseModel):
    """Outgoing chat response payload."""

    response: str
    session_id: str
    products: list[ProductMatch] = Field(
        default_factory=list,
        description="Enriched product matches from the vector database.",
    )
