from typing import Any, Dict, Optional
from .base import BaseAgent, AgentResponse, AgentStatus, NextAction
from ..memory.manager import MemoryManager

class LearningAgent(BaseAgent):
    def __init__(self, memory_manager: MemoryManager):
        super().__init__("LearningAgent")
        self.memory_manager = memory_manager

    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Corrections -> Memory/Candidate Mapping
        """
        try:
            # Expects correction details
            user_id = input_data.get("user_id")
            session_id = input_data.get("session_id")
            phrase = input_data.get("phrase")
            canonical = input_data.get("canonical")
            lang = input_data.get("lang", "en-IN")
            state = input_data.get("state")
            district = input_data.get("district")
            biz = input_data.get("biz", "GENERAL")

            if not all([user_id, session_id, phrase, canonical, state]):
                return AgentResponse(
                    status=AgentStatus.INCOMPLETE,
                    confidence=0.0,
                    next_action=NextAction.ASK_USER,
                    errors=["Missing required correction data"]
                )

            from .base import RegionalContext # Should use models.RegionalContext
            # Note: Need to import correctly. Let's use the one from backend.memory.models
            from ..memory.models import RegionalContext
            region = RegionalContext(state=state, district=district)

            mapping = self.memory_manager.record_correction(
                user_id=user_id, session_id=session_id, phrase=phrase,
                canonical=canonical, lang=lang, region=region, biz=biz
            )

            return AgentResponse(
                status=AgentStatus.SUCCESS,
                confidence=1.0,
                result=mapping,
                evidence=["MEMORY_MANAGER"],
                next_action=NextAction.PROCEED
            )
        except Exception as e:
            return AgentResponse(
                status=AgentStatus.FAILURE,
                confidence=0.0,
                next_action=NextAction.RETRY,
                errors=[str(e)]
            )
