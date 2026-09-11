from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class RegionalContext(BaseModel):
    state: str
    district: Optional[str] = None

class LearnedMapping(BaseModel):
    phrase: str = Field(..., description="The colloquial term")
    canonical_meaning: str = Field(..., description="The ontology ID")
    language: str = Field(..., description="ISO language code")
    regional_context: RegionalContext
    business_context: str = Field(..., description="Sector ID")
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    evidence_count: int = Field(0, ge=0)
    correction_count: int = Field(0, ge=0)
    verification_status: VerificationStatus = VerificationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    source_users: List[str] = Field(default_factory=list)

class MemoryEntry(BaseModel):
    phrase: str
    canonical_meaning: str
    timestamp: datetime = Field(default_factory=datetime.now)
