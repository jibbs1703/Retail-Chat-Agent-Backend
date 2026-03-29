"""Retail Chat Agent Runner Module.

Handles message construction (including multimodal image input) and
extracts the final AI reply from the LangGraph response.
"""

from langchain_core.messages import AIMessage, HumanMessage


def invoke_retail_agent(
    agent,
    message: str,
    history: list[dict] | None = None,
    image_b64: str | None = None,
) -> str:
    """Invoke the retail agent with a message and optional image.

    The agent uses GPT-4o's vision capability when an image is provided —
    it sees the image directly in the conversation and decides autonomously
    to call ``search_products_by_image_description`` with an extracted
    visual description.

    Args:
        agent: The compiled LangGraph agent.
        message: The customer's current text message.
        history: Prior exchanges as dicts with ``role`` and ``content``.
        image_b64: Optional base64-encoded product image (JPEG or PNG).

    Returns:
        The agent's reply as a plain string.
    """
    messages: list = []

    for entry in history or []:
        if entry["role"] == "user":
            messages.append(HumanMessage(content=entry["content"]))
        else:
            messages.append(AIMessage(content=entry["content"]))

    if image_b64:
        content = [
            {"type": "text", "text": message or "Find products similar to this image."},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
            },
        ]
        messages.append(HumanMessage(content=content))
    else:
        messages.append(HumanMessage(content=message))

    response = agent.invoke({"messages": messages})

    ai_messages = [
        msg
        for msg in response["messages"]
        if hasattr(msg, "content") and msg.type == "ai"
    ]
    if ai_messages:
        return ai_messages[-1].content
    return "I couldn't generate a response. Please try again."
