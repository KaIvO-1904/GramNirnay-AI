from typing import Any, Dict, Optional
from .base import BaseAgent, AgentResponse, AgentStatus, NextAction
from ..scoring.viability_engine import ViabilityEngine

class ExplanationAgent(BaseAgent):
    def __init__(self, viability_engine: ViabilityEngine):
        super().__init__("ExplanationAgent")
        self.viability_engine = viability_engine

    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        All Results -> Human-Readable Synthesis
        """
        try:
            # Input data is the full state of the pipeline
            state = input_data.get("pipeline_state")
            if not state:
                return AgentResponse(
                    status=AgentStatus.INCOMPLETE,
                    confidence=0.0,
                    next_action=NextAction.ASK_USER,
                    errors=["Pipeline state missing for explanation"]
                )

            # In this architecture, the ViabilityEngine provides the scoring and explanation
            # We assume the viability report has already been computed by the service
            report = state.get("viability_report")
            explanation = state.get("final_explanation")

            if not report or not explanation:
                return AgentResponse(
                    status=AgentStatus.FAILURE,
                    confidence=0.0,
                    next_action=NextAction.RETRY,
                    errors=["Viability report or explanation not yet generated"]
                )

            return AgentResponse(
                status=AgentStatus.SUCCESS,
                confidence=0.9,
                result={
                    "report": report,
                    "explanation": explanation
                },
                evidence=["VIABILITY_ENGINE"],
                next_action=NextAction.PROCEED
            )
        except Exception as e:
            return AgentResponse(
                status=AgentStatus.FAILURE,
                confidence=0.0,
                next_action=NextAction.RETRY,
                errors=[str(e)]
            )
