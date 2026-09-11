from typing import Any, Dict, Optional
from .base import BaseAgent, AgentResponse, AgentStatus, NextAction
from ..validation.rules_engine import ValidationEngine

class ValidationAgent(BaseAgent):
    def __init__(self, validation_engine: ValidationEngine):
        super().__init__("ValidationAgent")
        self.validation_engine = validation_engine

    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Parameters -> Rule Compliance -> Gap Analysis
        """
        try:
            params = input_data.get("financial_params")
            if not params:
                return AgentResponse(
                    status=AgentStatus.INCOMPLETE,
                    confidence=0.0,
                    next_action=NextAction.ASK_USER,
                    errors=["No financial parameters to validate"]
                )

            # Call deterministic validation engine
            # Assuming ValidationEngine has a validate() method
            validation_result = self.validation_engine.validate(params)

            if validation_result.is_valid:
                return AgentResponse(
                    status=AgentStatus.SUCCESS,
                    confidence=1.0,
                    result=validation_result,
                    evidence=["VALIDATION_ENGINE"],
                    next_action=NextAction.PROCEED
                )
            else:
                return AgentResponse(
                    status=AgentStatus.AMBIGUOUS,
                    confidence=0.5,
                    result=validation_result,
                    next_action=NextAction.ASK_USER,
                    errors=validation_result.errors
                )
        except Exception as e:
            return AgentResponse(
                status=AgentStatus.FAILURE,
                confidence=0.0,
                next_action=NextAction.RETRY,
                errors=[str(e)]
            )
