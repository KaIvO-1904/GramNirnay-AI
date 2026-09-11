from typing import Any, Dict, Optional
from .base import BaseAgent, AgentResponse, AgentStatus, NextAction
from ..intelligence.engine import LocalIntelligenceEngine

class IntelligenceAgent(BaseAgent):
    def __init__(self, intelligence_engine: LocalIntelligenceEngine):
        super().__init__("IntelligenceAgent")
        self.intelligence_engine = intelligence_engine

    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Location -> Hyper-Local Market Proxies
        """
        try:
            location = input_data.get("location")
            profile = input_data.get("profile")

            if not location:
                return AgentResponse(
                    status=AgentStatus.INCOMPLETE,
                    confidence=0.0,
                    next_action=NextAction.ASK_USER,
                    errors=["No location provided for intelligence gathering"]
                )

            # Call deterministic intelligence engine
            market_data = self.intelligence_engine.get_market_proxies(profile, location)

            return AgentResponse(
                status=AgentStatus.SUCCESS,
                confidence=0.9,
                result=market_data,
                evidence=["LOCAL_INTELLIGENCE_ENGINE"],
                next_action=NextAction.PROCEED
            )
        except Exception as e:
            return AgentResponse(
                status=AgentStatus.FAILURE,
                confidence=0.0,
                next_action=NextAction.RETRY,
                errors=[str(e)]
            )
