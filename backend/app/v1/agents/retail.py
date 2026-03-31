"""Retail Chat Agent Factory Module."""

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from ..core.configuration import get_settings
from ..core.prompts import SYSTEM_PROMPT
from ..core.tools import get_all_tools


def get_retail_agent(
    model: str | None = None,
    api_key: str | None = None,
    tools: list | None = None,
    system_prompt: str = SYSTEM_PROMPT,
):
    """Create and return a retail product-search agent.

    Args:
        model: OpenAI model name (defaults to settings.openai_model).
        api_key: OpenAI API key (defaults to settings.openai_api_key).
        tools: List of LangChain tools; defaults to all retail tools.
        system_prompt: Agent system prompt.

    Returns:
        A compiled LangGraph agent ready to invoke.

    Raises:
        ValueError: If the OpenAI API key is not configured.
    """
    settings = get_settings()
    model = model or settings.openai_model
    api_key = api_key or settings.openai_api_key

    if not api_key:
        raise ValueError(
            "OpenAI API key not configured. Set OPENAI_API_KEY in the .env file."
        )

    if tools is None:
        tools = get_all_tools()

    llm = ChatOpenAI(
        model=model,
        temperature=0.1,
        api_key=api_key,
    )

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
    )
