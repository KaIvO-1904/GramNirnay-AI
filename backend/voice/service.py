from typing import Optional, Dict, Any
from .models import TranscriptionResult, VoiceRequest, NormalizedTranscript
from .providers import IVoiceProvider, MockVoiceProvider
from .normalization import NormalizationService

class VoiceService:
    """
    Orchestrates the voice-input pipeline.
    Audio -> STT -> Normalization -> Result.
    """

    def __init__(self, provider: Optional[IVoiceProvider] = None):
        self.provider = provider or MockVoiceProvider()
        self.normalizer = NormalizationService()

    async def process_audio(self, audio_data: bytes, language_hint: Optional[str] = None) -> TranscriptionResult:
        """
        Processes raw audio into a transcribed and normalized result.
        """
        # 1. Transcription (STT)
        transcription = await self.provider.transcribe(audio_data, language_hint)

        # 2. Normalization (Dialect/Terminology mapping)
        norm_res = self.normalizer.normalize(transcription.raw_text)

        # Update result with normalized text
        transcription.normalized_text = norm_res.final_text

        # Combine confidence: Avg of STT and Normalization
        combined_conf = (transcription.confidence.score + norm_res.confidence_score) / 2
        transcription.confidence.score = round(combined_conf, 2)

        return transcription
