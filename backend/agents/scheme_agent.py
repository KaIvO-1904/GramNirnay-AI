from typing import Any, Dict, Optional
from .base import BaseAgent, AgentResponse, AgentStatus, NextAction
from ..rag_engine import RAGEngine

class SchemeAgent(BaseAgent):
    def __init__(self, rag_engine: RAGEngine):
        super().__init__("SchemeAgent")
        self.rag_engine = rag_engine

    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Params -> Verified Government Subsidies
        """
        try:
            profile = input_data.get("profile")
            params = input_data.get("financial_params")

            if not profile or not params:
                return AgentResponse(
                    status=AgentStatus.INCOMPLETE,
                    confidence=0.0,
                    next_action=NextAction.ASK_USER,
                    errors=["Missing profile or financial parameters for scheme matching"]
                )

            # Call deterministic RAG engine
            schemes = self.rag_engine.get_best_schemes(profile, params)

            return AgentResponse(
                status=AgentStatus.SUCCESS,
                confidence=0.8,
                result=schemes,
                evidence=["RAG_ENGINE", "OFFICIAL_GOVT_SOURCES"],
                next_action=NextAction.PROCEED
            )
        except Exception as e:
            return AgentResponse(
                status=AgentStatus.FAILURE,
                confidence=0.0,
                next_action=NextAction.RETRY,
                errors=[str(e)]
            )
