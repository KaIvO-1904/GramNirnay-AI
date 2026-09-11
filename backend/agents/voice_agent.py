from typing import Any, Dict, Optional
from .base import BaseAgent, AgentResponse, AgentStatus, NextAction
from ..voice.service import VoiceService
from ..voice.normalization import NormalizationService

class VoiceAgent(BaseAgent):
    def __init__(self, voice_service: VoiceService, normalizer: NormalizationService):
        super().__init__("VoiceAgent")
        self.voice_service = voice_service
        self.normalizer = normalizer

    async def execute(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Audio -> STT -> Normalization -> Intent
        """
        try:
            audio_data = input_data.get("audio")
            lang = input_data.get("language", "en-IN")

            if not audio_data:
                return AgentResponse(
                    status=AgentStatus.FAILURE,
                    confidence=0.0,
                    next_action=NextAction.ASK_USER,
                    errors=["No audio data provided"]
                )

            # Call deterministic service
            transcription = await self.voice_service.process_audio(audio_data, lang)

            return AgentResponse(
                status=AgentStatus.SUCCESS,
                confidence=transcription.confidence.score,
                result=transcription.normalized_text,
                evidence=["STT_PROVIDER", "NORMALIZATION_SERVICE"],
                next_action=NextAction.PROCEED
            )
        except Exception as e:
            return AgentResponse(
                status=AgentStatus.FAILURE,
                confidence=0.0,
                next_action=NextAction.RETRY,
                errors=[str(e)]
            )
