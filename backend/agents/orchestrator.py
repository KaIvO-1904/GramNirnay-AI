import logging
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base import AgentResponse, AgentStatus, NextAction
from .voice_agent import VoiceAgent
from .location_agent import LocationAgent
from .business_agent import BusinessAgent
from .validation_agent import ValidationAgent
from .intelligence_agent import IntelligenceAgent
from .financial_agent import FinancialAgent
from .scheme_agent import SchemeAgent
from .learning_agent import LearningAgent
from .explanation_agent import ExplanationAgent

# Import deterministic services
from ..voice.service import VoiceService
from ..voice.normalization import NormalizationService
from ..location.service import LocationService
from ..interpreter import BusinessInterpreter
from ..validation.rules_engine import ValidationEngine
from ..intelligence.engine import LocalIntelligenceEngine
from ..financial_engine import FinancialEngine
from ..rag_engine import RAGEngine
from ..scoring.viability_engine import ViabilityEngine
from ..memory.manager import MemoryManager

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    The central orchestrator that coordinates the bounded agents.
    Ensures deterministic state transitions and prevents infinite loops.
    """
    def __init__(self):
        # Initialize Services
        self.voice_service = VoiceService()
        self.normalizer = NormalizationService()
        self.location_service = LocationService()
        self.interpreter = BusinessInterpreter()
        self.validation_engine = ValidationEngine()
        self.intel_engine = LocalIntelligenceEngine()
        self.fin_engine = FinancialEngine()
        self.rag_engine = RAGEngine()
        self.viability_engine = ViabilityEngine()
        self.memory_manager = MemoryManager()

        # Initialize Agents
        self.agents = {
            "voice": VoiceAgent(self.voice_service, self.normalizer),
            "location": LocationAgent(self.location_service),
            "business": BusinessAgent(self.interpreter),
            "validation": ValidationAgent(self.validation_engine),
            "intelligence": IntelligenceAgent(self.intel_engine),
            "financial": FinancialAgent(self.fin_engine),
            "scheme": SchemeAgent(self.rag_engine),
            "learning": LearningAgent(self.memory_manager),
            "explanation": ExplanationAgent(self.viability_engine)
        }

    async def run_pipeline(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinates the Golden Path:
        Interpretation -> Validation -> Location -> Intelligence -> Finance -> Viability -> Schemes -> Explanation
        """
        state = {
            "input": user_input,
            "normalized_text": None,
            "location": None,
            "financial_params": None,
            "market_data": None,
            "financial_results": None,
            "viability_report": None,
            "schemes": None,
            "explanation": None,
            "trace": []
        }

        # Sequence of agent keys to execute
        pipeline_sequence = ["voice", "business", "validation", "location", "intelligence", "financial", "scheme", "explanation"]

        iteration_count = 0
        max_iterations = 20
        current_step_idx = 0

        while current_step_idx < len(pipeline_sequence):
            if iteration_count >= max_iterations:
                logger.error("Orchestration failed: Maximum iterations reached.")
                return {"status": "ERROR", "message": "Maximum orchestration depth reached", "state": state}

            agent_key = pipeline_sequence[current_step_idx]
            agent = self.agents[agent_key]

            # Prepare input for the agent based on current state
            agent_input = self._prepare_agent_input(agent_key, state)

            logger.info(f"Orchestrator: Executing {agent_key}...")
            response = await agent.execute(agent_input)

            # Log trace
            state["trace"].append({
                "step": agent_key,
                "status": response.status,
                "confidence": response.confidence,
                "timestamp": datetime.now().isoformat()
            })

            if response.status == AgentStatus.SUCCESS:
                self._update_state(agent_key, response.result, state)
                current_step_idx += 1
            elif response.status == AgentStatus.AMBIGUOUS or response.status == AgentStatus.INCOMPLETE:
                return {
                    "status": "NEED_INFO",
                    "agent": agent_key,
                    "errors": response.errors,
                    "next_action": response.next_action,
                    "state": state
                }
            elif response.status == AgentStatus.FAILURE:
                if response.next_action == NextAction.RETRY:
                    iteration_count += 1
                    continue # Retry same agent
                elif response.next_action == NextAction.ASK_USER:
                    return {
                        "status": "NEED_INFO",
                        "agent": agent_key,
                        "errors": response.errors,
                        "next_action": response.next_action,
                        "state": state
                    }
                else:
                    return {"status": "ERROR", "agent": agent_key, "errors": response.errors, "state": state}

            iteration_count += 1

        # Final step: The Viability Engine (Service) computes the final score
        # based on everything gathered.
        try:
            # We use the underlying deterministic service directly for the final score
            # to ensure no "AI guessing" occurs at the most critical point.
            viability_report = self.viability_engine.compute_viability(
                state["financial_results"],
                state["market_data"]
            )
            state["viability_report"] = viability_report

            # Finally, the Explanation Agent synthesizes the report
            explanation_res = await self.agents["explanation"].execute({"pipeline_state": state})
            state["explanation"] = explanation_res.result["explanation"]
            state["viability_score"] = viability_report.score
        except Exception as e:
            logger.exception(f"Final viability computation failed: {e}")
            return {"status": "ERROR", "message": "Final viability computation failed", "state": state}

        return {
            "status": "SUCCESS",
            "result": state,
            "viability_score": state["viability_score"]
        }

    def _prepare_agent_input(self, agent_key: str, state: Dict[str, Any]) -> Dict[str, Any]:
        if agent_key == "voice":
            return {"audio": state["input"].get("audio"), "language": state["input"].get("language")}
        if agent_key == "business":
            return {
                "text": state["normalized_text"] or state["input"].get("text"),
                "location": state["location"].model_dump() if state["location"] else {},
                "experience": state["input"].get("experience", 0),
                "answers": state["input"].get("answers", {})
            }
        if agent_key == "validation":
            return {"financial_params": state["financial_params"]}
        if agent_key == "location":
            return {
                "location_query": state["input"].get("location_query"),
                "lat": state["input"].get("lat"),
                "lng": state["input"].get("lng")
            }
        if agent_key == "intelligence":
            return {"location": state["location"], "profile": state["input"]}
        if agent_key == "financial":
            return {"financial_params": state["financial_params"]}
        if agent_key == "scheme":
            return {
                "profile": state["input"],
                "financial_params": state["financial_params"]
            }
        if agent_key == "explanation":
            return {"pipeline_state": state}
        return {}

    def _update_state(self, agent_key: str, result: Any, state: Dict[str, Any]):
        if agent_key == "voice":
            state["normalized_text"] = result
        elif agent_key == "business":
            state["financial_params"] = result
        elif agent_key == "location":
            state["location"] = result
        elif agent_key == "intelligence":
            state["market_data"] = result
        elif agent_key == "financial":
            state["financial_results"] = result
        elif agent_key == "scheme":
            state["schemes"] = result
