"""Tests for backend.app.v1.agents.runner — invoke_retail_agent."""

from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from backend.app.v1.agents.runner import invoke_retail_agent


def _make_agent(reply: str):
    agent = MagicMock()
    agent.invoke.return_value = {"messages": [AIMessage(content=reply)]}
    return agent


@pytest.mark.unit
def test_basic_text_invocation():
    agent = _make_agent("Here are blue sneakers!")
    result = invoke_retail_agent(agent, "blue sneakers")
    assert result == "Here are blue sneakers!"


@pytest.mark.unit
def test_no_history_sends_single_human_message():
    agent = _make_agent("result")
    invoke_retail_agent(agent, "white t-shirt")
    messages = agent.invoke.call_args[0][0]["messages"]
    assert len(messages) == 1
    assert isinstance(messages[0], HumanMessage)
    assert messages[0].content == "white t-shirt"


@pytest.mark.unit
def test_history_is_prepended():
    agent = _make_agent("More options!")
    history = [
        {"role": "user", "content": "red jacket"},
        {"role": "assistant", "content": "Here are red jackets."},
    ]
    invoke_retail_agent(agent, "anything else?", history)
    messages = agent.invoke.call_args[0][0]["messages"]
    assert len(messages) == 3
    assert isinstance(messages[0], HumanMessage)
    assert isinstance(messages[1], AIMessage)
    assert isinstance(messages[2], HumanMessage)
    assert messages[2].content == "anything else?"


@pytest.mark.unit
def test_image_results_are_appended_to_message():
    agent = _make_agent("Found matching products!")
    image_results = "- Blue Jacket (similarity: 0.95): Slim-fit blue denim jacket."
    invoke_retail_agent(agent, "what is this?", image_results=image_results)
    messages = agent.invoke.call_args[0][0]["messages"]
    last = messages[-1]
    assert isinstance(last, HumanMessage)
    assert isinstance(last.content, str)
    assert "what is this?" in last.content
    assert image_results in last.content


@pytest.mark.unit
def test_image_results_with_empty_message():
    agent = _make_agent("result")
    image_results = "- Some product (similarity: 0.90)"
    invoke_retail_agent(agent, "", image_results=image_results)
    messages = agent.invoke.call_args[0][0]["messages"]
    content = messages[-1].content
    assert image_results in content


@pytest.mark.unit
def test_fallback_when_no_ai_message():
    agent = MagicMock()
    agent.invoke.return_value = {"messages": [HumanMessage(content="echo")]}
    result = invoke_retail_agent(agent, "test")
    assert result == "I couldn't generate a response. Please try again."
