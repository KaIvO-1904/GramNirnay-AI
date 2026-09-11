from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from .models import TranscriptionResult, VoiceConfidence

class IVoiceProvider(ABC):
    """Abstract base class for Speech-to-Text providers."""

    @abstractmethod
    async def transcribe(self, audio_data: bytes, language_hint: Optional[str] = None) -> TranscriptionResult:
        """Converts audio bytes to text with confidence scores."""
        pass

    @abstractmethod
    async def detect_language(self, audio_data: bytes) -> str:
        """Identifies the spoken language/dialect."""
        pass

class MockVoiceProvider(IVoiceProvider):
    """Synthetic provider for testing and development."""

    async def transcribe(self, audio_data: bytes, language_hint: Optional[str] = None) -> TranscriptionResult:
        import uuid

        # Handle empty audio
        if not audio_data or len(audio_data) == 0:
            raise ValueError("Audio data is empty")

        # Simulate different outcomes based on audio length for testing
        # In a real mock, we might look at the bytes or a specific magic value
        if len(audio_data) < 10:
            raw_text = "I want to start a nati koli farm" # a known dialect term
            conf = 0.9
        elif len(audio_data) < 100:
            raw_text = "I want to start a poultry business"
            conf = 0.95
        else:
            raw_text = "something unclear and noisy"
            conf = 0.4

        return TranscriptionResult(
            request_id=str(uuid.uuid4()),
            raw_text=raw_text,
            normalized_text=raw_text, # To be filled by NormalizationService
            detected_language="kn-IN" if "nati koli" in raw_text else "en-IN",
            confidence=VoiceConfidence(score=conf, stage="stt", provider="MockVoiceProvider"),
            metadata={"duration_sec": len(audio_data) / 1000}
        )

    async def detect_language(self, audio_data: bytes) -> str:
        return "kn-IN" if len(audio_data) < 10 else "en-IN"
