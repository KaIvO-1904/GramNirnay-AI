from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from .models import TranscriptionResult, VoiceConfidence
from openai import OpenAI
from ..config import settings

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

class OpenAIVoiceProvider(IVoiceProvider):
    """Production provider using OpenAI Whisper."""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )

    async def transcribe(self, audio_data: bytes, language_hint: Optional[str] = None) -> TranscriptionResult:
        import uuid
        import tempfile
        import os

        if not audio_data or len(audio_data) == 0:
            raise ValueError("Audio data is empty")

        # Whisper requires a file-like object or path. Write bytes to temp file.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as audio_file:
                # Note: Whisper API doesn't provide per-word confidence in the same way
                # as some other STT, but we can use the result.
                response = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-1",
                    language=language_hint
                )
                text = response.text

            # Whisper is highly confident usually, we assign a default for this wrapper
            return TranscriptionResult(
                request_id=str(uuid.uuid4()),
                raw_text=text,
                normalized_text=text,
                detected_language=language_hint or "auto",
                confidence=VoiceConfidence(score=0.95, stage="stt", provider="OpenAI-Whisper"),
                metadata={"provider": "openai"}
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    async def detect_language(self, audio_data: bytes) -> str:
        # Simplified: Use a small chunk to detect language or let transcribe handle it
        return "auto"

class MockVoiceProvider(IVoiceProvider):
    """Synthetic provider for testing and development."""
    # ... (existing MockVoiceProvider code) ...
