import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from backend.agents.orchestrator import AgentOrchestrator
from backend.agents.base import AgentResponse, AgentStatus, NextAction
from backend.memory.models import RegionalContext
from backend.core.schemas.base import ConfidenceResult

@pytest.fixture
def orchestrator():
    return AgentOrchestrator()

@pytest.mark.asyncio
async def test_happy_path_journey(orchestrator):
    # Setup mocks for a successful flow
    for agent in orchestrator.agents.values():
        agent.execute = AsyncMock(
            return_value=AgentResponse(
                status=AgentStatus.SUCCESS,
                confidence=1.0,
                result={"mock": "data", "explanation": "mock explanation"},
                next_action=NextAction.PROCEED
            )
        )

    orchestrator.viability_engine.compute_viability = MagicMock(
        return_value=MagicMock(score=85, recommendation="Proceed")
    )

    input_data = {"text": "I want to start a poultry farm", "location_query": "Bangalore"}
    result = await orchestrator.run_pipeline(input_data)

    assert result["status"] == "SUCCESS"
    assert result["viability_score"] == 85
    assert "trace" in result["result"]

@pytest.mark.asyncio
async def test_invalid_flow_poultry_to_coffee(orchestrator):
    # Case 1: contradictory business type
    # Voice says poultry, but a later agent (e.g. BusinessAgent) finds it's actually coffee
    orchestrator.agents["voice"].execute = AsyncMock(
        return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result="Poultry Farm", next_action=NextAction.PROCEED)
    )
    orchestrator.agents["business"].execute = AsyncMock(
        return_value=AgentResponse(
            status=AgentStatus.FAILURE,
            confidence=0.4,
            errors=["Business type mismatch: Voice input 'Poultry' contradicts category 'Coffee'"],
            next_action=NextAction.ASK_USER
        )
    )

    input_data = {"text": "Poultry farm"}
    result = await orchestrator.run_pipeline(input_data)

    assert result["status"] == "NEED_INFO"
    assert "mismatch" in result["errors"][0].lower()

@pytest.mark.asyncio
async def test_invalid_flow_missing_business_type(orchestrator):
    # Case 2: missing business type
    orchestrator.agents["voice"].execute = AsyncMock(
        return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result="Something", next_action=NextAction.PROCEED)
    )
    orchestrator.agents["business"].execute = AsyncMock(
        return_value=AgentResponse(
            status=AgentStatus.FAILURE,
            confidence=0.0,
            errors=["Could not determine business type from input"],
            next_action=NextAction.ASK_USER
        )
    )

    input_data = {"text": "Hello"}
    result = await orchestrator.run_pipeline(input_data)

    assert result["status"] == "NEED_INFO"
    assert "could not determine" in result["errors"][0].lower()

@pytest.mark.asyncio
async def test_invalid_flow_ambiguous_location(orchestrator):
    # Case 3: ambiguous location
    orchestrator.agents["voice"].execute = AsyncMock(
        return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result="Farm", next_action=NextAction.PROCEED)
    )
    orchestrator.agents["business"].execute = AsyncMock(
        return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result={"type": "POULTRY"}, next_action=NextAction.PROCEED)
    )
    orchestrator.agents["validation"].execute = AsyncMock(
        return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result={}, next_action=NextAction.PROCEED)
    )
    orchestrator.agents["location"].execute = AsyncMock(
        return_value=AgentResponse(
            status=AgentStatus.AMBIGUOUS,
            confidence=0.5,
            result={"candidates": ["Location A", "Location B"]},
            errors=["Multiple locations found for query"],
            next_action=NextAction.ASK_USER
        )
    )

    input_data = {"text": "Farm", "location_query": "Ambiguous City"}
    result = await orchestrator.run_pipeline(input_data)

    assert result["status"] == "NEED_INFO"
    assert result["agent"] == "location"
    assert "multiple locations" in result["errors"][0].lower()

@pytest.mark.asyncio
async def test_invalid_flow_denied_location(orchestrator):
    # Case 4: denied location permission
    orchestrator.agents["voice"].execute = AsyncMock(
        return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result="Farm", next_action=NextAction.PROCEED)
    )
    orchestrator.agents["business"].execute = AsyncMock(
        return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result={"type": "POULTRY"}, next_action=NextAction.PROCEED)
    )
    orchestrator.agents["validation"].execute = AsyncMock(
        return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result={}, next_action=NextAction.PROCEED)
    )
    orchestrator.agents["location"].execute = AsyncMock(
        return_value=AgentResponse(
            status=AgentStatus.FAILURE,
            confidence=0.0,
            errors=["Location access denied"],
            next_action=NextAction.ASK_USER
        )
    )

    input_data = {"text": "Farm"}
    result = await orchestrator.run_pipeline(input_data)

    assert result["status"] == "NEED_INFO"
    assert "denied" in result["errors"][0].lower()

@pytest.mark.asyncio
async def test_invalid_flow_invalid_coordinates(orchestrator):
    # Case 5: invalid coordinates
    orchestrator.agents["voice"].execute = AsyncMock(
        return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result="Farm", next_action=NextAction.PROCEED)
    )
    orchestrator.agents["business"].execute = AsyncMock(
        return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result={"type": "POULTRY"}, next_action=NextAction.PROCEED)
    )
    orchestrator.agents["validation"].execute = AsyncMock(
        return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result={}, next_action=NextAction.PROCEED)
    )
    orchestrator.agents["location"].execute = AsyncMock(
        return_value=AgentResponse(
            status=AgentStatus.FAILURE,
            confidence=0.0,
            errors=["Invalid GPS coordinates provided"],
            next_action=NextAction.RETRY
        )
    )

    input_data = {"text": "Farm", "coords": {"lat": 999, "lng": 999}}
    result = await orchestrator.run_pipeline(input_data)

    # Should retry and then we'll make it succeed
    location_calls = 0
    async def location_mock(*args, **kwargs):
        nonlocal location_calls
        location_calls += 1
        if location_calls == 1:
            return AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["Invalid GPS coordinates provided"], next_action=NextAction.RETRY)
        return AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result={"id": "loc1"}, next_action=NextAction.PROCEED)

    orchestrator.agents["location"].execute = AsyncMock(side_effect=location_mock)

    # Re-run since we changed the mock
    result = await orchestrator.run_pipeline(input_data)
    # Note: we need other agents to be mocked too for the final SUCCESS
    for agent in ["intelligence", "financial", "scheme", "explanation"]:
        orchestrator.agents[agent].execute = AsyncMock(
            return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result={"explanation": "mock"}, next_action=NextAction.PROCEED)
        )
    orchestrator.viability_engine.compute_viability = MagicMock(return_value=MagicMock(score=70))

    result = await orchestrator.run_pipeline(input_data)
    assert result["status"] == "SUCCESS"

@pytest.mark.asyncio
async def test_invalid_flow_insufficient_capital(orchestrator):
    # Case 6: insufficient capital
    # This is a financial risk, not necessarily a pipeline failure
    for agent in orchestrator.agents.values():
        agent.execute = AsyncMock(
            return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result={"explanation": "mock"}, next_action=NextAction.PROCEED)
        )

    # Mock financial agent to return high capital requirement
    orchestrator.agents["financial"].execute = AsyncMock(
        return_value=AgentResponse(
            status=AgentStatus.SUCCESS,
            confidence=1.0,
            result={"total_cost": 1000000, "available": 1000},
            next_action=NextAction.PROCEED
        )
    )

    orchestrator.viability_engine.compute_viability = MagicMock(
        return_value=MagicMock(score=30, recommendation="High Risk")
    )

    input_data = {"text": "Big Farm"}
    result = await orchestrator.run_pipeline(input_data)

    assert result["status"] == "SUCCESS"
    assert result["viability_score"] == 30

@pytest.mark.asyncio
async def test_invalid_flow_contradictory_answers(orchestrator):
    # Case 7: contradictory answers
    orchestrator.agents["voice"].execute = AsyncMock(
        return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result="Farm", next_action=NextAction.PROCEED)
    )
    orchestrator.agents["business"].execute = AsyncMock(
        return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result={"type": "POULTRY"}, next_action=NextAction.PROCEED)
    )
    orchestrator.agents["validation"].execute = AsyncMock(
        return_value=AgentResponse(
            status=AgentStatus.FAILURE,
            confidence=0.0,
            errors=["Contradictory answers: Shed type 'Open' is incompatible with 'Industrial' feed source"],
            next_action=NextAction.ASK_USER
        )
    )

    input_data = {"text": "Farm"}
    result = await orchestrator.run_pipeline(input_data)

    assert result["status"] == "NEED_INFO"
    assert "contradictory" in result["errors"][0].lower()

@pytest.mark.asyncio
async def test_invalid_flow_low_confidence_interpretation(orchestrator):
    # Case 8: low-confidence semantic interpretation
    orchestrator.agents["voice"].execute = AsyncMock(
        return_value=AgentResponse(
            status=AgentStatus.AMBIGUOUS,
            confidence=0.3,
            result=None,
            errors=["Could not confidently interpret voice input"],
            next_action=NextAction.ASK_USER
        )
    )

    input_data = {"audio": b"noise"}
    result = await orchestrator.run_pipeline(input_data)

    assert result["status"] == "NEED_INFO"
    assert "confidently interpret" in result["errors"][0].lower()

@pytest.mark.asyncio
async def test_invalid_flow_voice_transcription_error(orchestrator):
    # Case 9: voice transcription error
    orchestrator.agents["voice"].execute = AsyncMock(
        return_value=AgentResponse(
            status=AgentStatus.FAILURE,
            confidence=0.0,
            errors=["STT Service unavailable"],
            next_action=NextAction.RETRY
        )
    )

    input_data = {"audio": b"fake"}
    result = await orchestrator.run_pipeline(input_data)

    # Should be in NEED_INFO or ERROR depending on retry logic
    # In our orchestrator, if it's RETRY it will try again.
    # Let's make it fail twice.
    orchestrator.agents["voice"].execute.side_effect = [
        AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["STT Service unavailable"], next_action=NextAction.RETRY),
        AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["STT Service unavailable"], next_action=NextAction.RETRY),
        AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["STT Service unavailable"], next_action=NextAction.RETRY),
        AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["STT Service unavailable"], next_action=NextAction.RETRY),
        AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["STT Service unavailable"], next_action=NextAction.RETRY),
        AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["STT Service unavailable"], next_action=NextAction.RETRY),
        AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["STT Service unavailable"], next_action=NextAction.RETRY),
        AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["STT Service unavailable"], next_action=NextAction.RETRY),
        AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["STT Service unavailable"], next_action=NextAction.RETRY),
        AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["STT Service unavailable"], next_action=NextAction.RETRY),
        AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["STT Service unavailable"], next_action=NextAction.RETRY),
        AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["STT Service unavailable"], next_action=NextAction.RETRY),
        AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["STT Service unavailable"], next_action=NextAction.RETRY),
        AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["STT Service unavailable"], next_action=NextAction.RETRY),
        AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["STT Service unavailable"], next_action=NextAction.RETRY),
        AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["STT Service unavailable"], next_action=NextAction.RETRY),
        AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["STT Service unavailable"], next_action=NextAction.RETRY),
        AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["STT Service unavailable"], next_action=NextAction.RETRY),
        AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["STT Service unavailable"], next_action=NextAction.RETRY),
        AgentResponse(status=AgentStatus.FAILURE, confidence=0.0, errors=["STT Service unavailable"], next_action=NextAction.RETRY),
    ]

    result = await orchestrator.run_pipeline(input_data)
    assert result["status"] == "ERROR"
    assert "Maximum orchestration depth reached" in result["message"]

@pytest.mark.asyncio
async def test_invalid_flow_unavailable_provider(orchestrator):
    # Case 10: unavailable external provider
    # This is handled by the agent returning FAILURE.
    orchestrator.agents["location"].execute = AsyncMock(
        return_value=AgentResponse(
            status=AgentStatus.FAILURE,
            confidence=0.0,
            errors=["External Geo-Provider API Down"],
            next_action=NextAction.ASK_USER
        )
    )

    # Setup previous agents
    orchestrator.agents["voice"].execute = AsyncMock(return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result="Farm", next_action=NextAction.PROCEED))
    orchestrator.agents["business"].execute = AsyncMock(return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result={"type": "POULTRY"}, next_action=NextAction.PROCEED))
    orchestrator.agents["validation"].execute = AsyncMock(return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result={}, next_action=NextAction.PROCEED))

    input_data = {"text": "Farm"}
    result = await orchestrator.run_pipeline(input_data)

    assert result["status"] == "NEED_INFO"
    assert "Provider API Down" in result["errors"][0]

@pytest.mark.asyncio
async def test_invalid_flow_missing_local_data(orchestrator):
    # Case 11: missing local data
    # Intelligence agent returns a result but with low confidence or "No data found"
    orchestrator.agents["intelligence"].execute = AsyncMock(
        return_value=AgentResponse(
            status=AgentStatus.SUCCESS,
            confidence=0.2,
            result={"demand": 50, "competition": 50, "note": "Limited local data available"},
            next_action=NextAction.PROCEED
        )
    )

    # Setup previous agents
    for agent in ["voice", "business", "validation", "location"]:
        orchestrator.agents[agent].execute = AsyncMock(return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result={"explanation": "mock"}, next_action=NextAction.PROCEED))

    # Other subsequent agents
    for agent in ["financial", "scheme", "explanation"]:
        orchestrator.agents[agent].execute = AsyncMock(return_value=AgentResponse(status=AgentStatus.SUCCESS, confidence=1.0, result={"explanation": "mock"}, next_action=NextAction.PROCEED))

    orchestrator.viability_engine.compute_viability = MagicMock(return_value=MagicMock(score=50))

    input_data = {"text": "Farm"}
    result = await orchestrator.run_pipeline(input_data)

    assert result["status"] == "SUCCESS"
    assert result["viability_score"] == 50

@pytest.mark.asyncio
async def test_invalid_flow_conflicting_terminology(orchestrator):
    # Case 12: conflicting learned terminology
    # We test this by resolving a phrase that has multiple candidates in memory
    from backend.memory.manager import MemoryManager
    from backend.memory.models import RegionalContext

    mm = MemoryManager()
    region = RegionalContext(state="Karnataka", district="Bangalore")
    phrase = "test term"

    # User 1 says it means POULTRY
    mm.record_correction("u1", "s1", phrase, "POULTRY", "en-IN", region, "GENERAL")
    # User 2 says it means TRADING
    mm.record_correction("u2", "s2", phrase, "TRADING", "en-IN", region, "GENERAL")

    # Resolve should pick the one with more evidence or higher confidence.
    # Since both have 1, it picks the first one encountered or based on logic.
    res = mm.resolve_phrase(phrase, "en-IN", region, "GENERAL")
    assert res in ["POULTRY", "TRADING"]
