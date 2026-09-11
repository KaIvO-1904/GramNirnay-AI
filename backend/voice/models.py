from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class VoiceConfidence(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    stage: str # "stt", "language", "normalization"
    provider: str

class TranscriptionResult(BaseModel):
    request_id: str
    raw_text: str
    normalized_text: str
    detected_language: str
    confidence: VoiceConfidence
    metadata: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)

class NormalizedTranscript(BaseModel):
    original_text: str
    final_text: str
    mappings_applied: List[Dict[str, str]] # [{"from": "nati koli", "to": "COUNTRY_CHICKEN"}]
    confidence_score: float

class VoiceRequest(BaseModel):
    user_id: str
    audio_format: str
    language_hint: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
