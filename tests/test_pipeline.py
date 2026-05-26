"""
Integration tests for the research pipeline.
Uses mocked Anthropic client to avoid real API calls.
"""

from __future__ import annotations

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_client():
    client = AsyncMock()

    def make_response(text: str, stop_reason: str = "end_turn"):
        block = MagicMock()
        block.type = "text"
        block.text = text
        response = MagicMock()
        response.stop_reason = stop_reason
        response.content = [block]
        return response

    client.messages.create = AsyncMock(
        return_value=make_response('["sub-query 1", "sub-query 2"]')
    )
    return client, make_response


def test_orchestrator_decompose(mock_client):
    client, make_response = mock_client
    client.messages.create = AsyncMock(
        return_value=make_response('["query 1", "query 2", "query 3"]')
    )

    from src.agents.orchestrator import OrchestratorAgent
    agent = OrchestratorAgent(client)
    result = asyncio.run(agent.decompose("test topic"))

    assert isinstance(result, list)
    assert len(result) == 3
    assert result[0] == "query 1"


def test_researcher_agent(mock_client):
    client, make_response = mock_client
    client.messages.create = AsyncMock(
        return_value=make_response("## Findings\n- Fact 1\n- Fact 2")
    )

    from src.agents.researcher import ResearcherAgent
    agent = ResearcherAgent(client)
    result = asyncio.run(agent.research("test sub-query"))

    assert "Findings" in result


def test_critic_agent(mock_client):
    client, make_response = mock_client
    client.messages.create = AsyncMock(
        return_value=make_response("## Critique\n✅ Strengths: good sources")
    )

    from src.agents.critic import CriticAgent
    agent = CriticAgent(client)
    result = asyncio.run(agent.critique("topic", [("q1", "findings")]))

    assert "Critique" in result


def test_synthesizer_agent(mock_client):
    client, make_response = mock_client
    client.messages.create = AsyncMock(
        return_value=make_response("# Final Report\n## Executive Summary\nThis is a summary.")
    )

    from src.agents.synthesizer import SynthesizerAgent
    agent = SynthesizerAgent(client)
    result = asyncio.run(agent.synthesize("topic", [("q1", "f1")], "critique"))

    assert "Final Report" in result


def test_memory_session():
    from src.memory.session import ResearchMemory
    mem = ResearchMemory()
    mem.add("researcher", "found something")
    mem.add("critic", "issues here")

    assert len(mem.get_all()) == 2
    assert mem.get_by_role("researcher")[0]["content"] == "found something"

    summary = mem.summary()
    assert "RESEARCHER" in summary
    assert "CRITIC" in summary
