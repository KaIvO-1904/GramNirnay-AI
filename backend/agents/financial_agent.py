from typing import Any, Dict, Optional
from .base import BaseAgent, AgentResponse, AgentStatus, NextAction
from ..financial_engine import FinancialEngine

class FinancialAgent(BaseAgent):
    def __init__(self, financial_engine: FinancialEngine):
        super().__init__("FinancialAgent")
        self.financial_engine = financial_engine

    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Parameters -> Financial Simulation Results
        """
        try:
            params = input_data.get("financial_params")
            if not params:
                return AgentResponse(
                    status=AgentStatus.INCOMPLETE,
                    confidence=0.0,
                    next_action=NextAction.ASK_USER,
                    errors=["No financial parameters provided"]
                )

            # Call deterministic financial engine
            result = self.financial_engine.compute_full_model(params)

            return AgentResponse(
                status=AgentStatus.SUCCESS,
                confidence=1.0,
                result=result,
                evidence=["FINANCIAL_ENGINE"],
                next_action=NextAction.PROCEED
            )
        except Exception as e:
            return AgentResponse(
                status=AgentStatus.FAILURE,
                confidence=0.0,
                next_action=NextAction.RETRY,
                errors=[str(e)]
            )
