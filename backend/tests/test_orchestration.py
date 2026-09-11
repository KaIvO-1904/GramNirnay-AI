import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from backend.agents.orchestrator import AgentOrchestrator
from backend.agents.base import AgentResponse, AgentStatus, NextAction

@pytest.fixture
def orchestrator():
    return AgentOrchestrator()

@pytest.mark.asyncio
async def test_successful_pipeline_flow(orchestrator):
    # Mock all agents to return success
    for agent in orchestrator.agents.values():
        agent.execute = AsyncMock(
            return_value=AgentResponse(
                status=AgentStatus.SUCCESS,
                confidence=1.0,
                result={"mock": "data", "explanation": "mock explanation"},
                next_action=NextAction.PROCEED
            )
        )

    # Mock the viability engine directly
    orchestrator.viability_engine.compute_viability = MagicMock(
        return_value=MagicMock(score=85)
    )

    input_data = {"text": "I want to start a poultry farm", "location_query": "Bangalore"}
    result = await orchestrator.run_pipeline(input_data)

    assert result["status"] == "SUCCESS"
    assert result["viability_score"] == 85
    assert len(result["result"]["trace"]) == 8 # All agents in pipeline_sequence

@pytest.mark.asyncio
async def test_ambiguous_input_triggers_ask_user(orchestrator):
    # Mock BusinessAgent to return AMBIGUOUS
    orchestrator.agents["business"].execute = AsyncMock(
        return_value=AgentResponse(
            status=AgentStatus.AMBIGUOUS,
            confidence=0.5,
            result=None,
            errors=["Insufficient details about flock size"],
            next_action=NextAction.ASK_USER
        )
    )
    # VoiceAgent must succeed first
    orchestrator.agents["voice"].execute = AsyncMock(
        return_value=AgentResponse(
            status=AgentStatus.SUCCESS,
            confidence=1.0,
            result="I want a farm",
            next_action=NextAction.PROCEED
        )
    )

    input_data = {"audio": b"fake audio"}
    result = await orchestrator.run_pipeline(input_data)

    assert result["status"] == "NEED_INFO"
    assert result["agent"] == "business"
    assert "Insufficient details" in result["errors"][0]

@pytest.mark.asyncio
async def test_failure_with_retry(orchestrator):
    # Mock LocationAgent to fail once then succeed
    orchestrator.agents["voice"].execute = AsyncMock(
        return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result="text", next_action=NextAction.PROCEED)
    )
    orchestrator.agents["business"].execute = AsyncMock(
        return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result={}, next_action=NextAction.PROCEED)
    )
    orchestrator.agents["validation"].execute = AsyncMock(
        return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result={}, next_action=NextAction.PROCEED)
    )

    # Sequence of return values: first Failure (Retry), then Success
    orchestrator.agents["location"].execute = AsyncMock(
        side_effect=[
            AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["Timeout"], next_action=NextAction.RETRY),
            AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result={"id": "loc1"}, next_action=NextAction.PROCEED)
        ]
    )

    # Other agents after location must succeed
    for key in ["intelligence", "financial", "scheme", "explanation"]:
        orchestrator.agents[key].execute = AsyncMock(
            return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result={"explanation": "mock"}, next_action=NextAction.PROCEED)
        )

    orchestrator.viability_engine.compute_viability = MagicMock(return_value=MagicMock(score=70))

    input_data = {"text": "farm"}
    result = await orchestrator.run_pipeline(input_data)

    assert result["status"] == "SUCCESS"
    # Check trace to see if location was called twice
    location_steps = [t for t in result["result"]["trace"] if t["step"] == "location"]
    assert len(location_steps) == 2
