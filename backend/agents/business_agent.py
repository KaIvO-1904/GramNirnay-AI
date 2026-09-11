from typing import Any, Dict, Optional
from .base import BaseAgent, AgentResponse, AgentStatus, NextAction
from ..interpreter import BusinessInterpreter

class BusinessAgent(BaseAgent):
    def __init__(self, interpreter: BusinessInterpreter):
        super().__init__("BusinessAgent")
        self.interpreter = interpreter

    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Intent -> Standardized Business Parameters
        """
        try:
            text = input_data.get("text")
            location = input_data.get("location", {})
            experience = input_data.get("experience", 0)
            answers = input_data.get("answers", {})

            if not text:
                return AgentResponse(
                    status=AgentStatus.INCOMPLETE,
                    confidence=0.0,
                    next_action=NextAction.ASK_USER,
                    errors=["No business idea text provided"]
                )

            # Call deterministic interpreter
            params = self.interpreter.interpret_from_answers(
                text, location, experience, answers
            )

            return AgentResponse(
                status=AgentStatus.SUCCESS,
                confidence=0.9,
                result=params,
                evidence=["BUSINESS_INTERPRETER", "ONTOLOGY"],
                next_action=NextAction.PROCEED
            )
        except Exception as e:
            return AgentResponse(
                status=AgentStatus.FAILURE,
                confidence=0.0,
                next_action=NextAction.RETRY,
                errors=[str(e)]
            )
