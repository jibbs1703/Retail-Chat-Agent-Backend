"""Retail Chat Agent Runner Module.

Builds the message list for the LangGraph agent and extracts the final AI reply.
Pre-computed image search results (from CLIP) are injected as text context so
the agent can incorporate them alongside its own text-collection search.
"""

from langchain_core.messages import AIMessage, HumanMessage


def invoke_retail_agent(
    agent,
    message: str,
    history: list[dict] | None = None,
    image_results: str | None = None,
) -> str:
    """Invoke the retail agent with a message and optional image search context.

    When ``image_results`` is provided (pre-computed CLIP image-collection
    results from the service layer) they are appended to the human message so
    the agent can reference them while also searching the text collection.

    Args:
        agent: The compiled LangGraph agent.
        message: The customer's current text description.
        history: Prior exchanges as dicts with ``role`` and ``content``.
        image_results: Optional formatted string of image-collection matches,
                       produced by embedding the uploaded image with CLIP.

    Returns:
        The agent's reply as a plain string.
    """
    messages: list = []

    for entry in history or []:
        content = entry["content"]
        if isinstance(content, list):
            content = " ".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in content
            )
        if entry["role"] == "user":
            messages.append(HumanMessage(content=content))
        else:
            messages.append(AIMessage(content=content))

    human_text = message or ""
    if image_results:
        suffix = (
            f"\n\n[Visually similar products found via image search]\n{image_results}"
        )
        human_text = (human_text + suffix) if human_text else suffix.lstrip()

    messages.append(HumanMessage(content=human_text or "Find products for me."))

    response = agent.invoke({"messages": messages})

    ai_messages = [
        msg
        for msg in response["messages"]
        if hasattr(msg, "content") and msg.type == "ai"
    ]
    if ai_messages:
        content = ai_messages[-1].content
        if isinstance(content, list):
            content = " ".join(
                block.get("text", "") if isinstance(block, dict) else str(block)
                for block in content
            )
        return content or "I couldn't generate a response. Please try again."
    return "I couldn't generate a response. Please try again."
