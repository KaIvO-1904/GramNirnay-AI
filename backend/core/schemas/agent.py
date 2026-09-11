from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from .base import ConfidenceResult

class AgentResponse(BaseModel):
    """Standardized response from any agent in the system."""
    agent_id: str
    content: Any
    confidence: float = Field(..., ge=0.0, le=1.0)
    tool_calls: List[str] = Field(default_factory=list, description="List of tools invoked during reasoning")
    reasoning_trace: List[str] = Field(default_factory=list)

class MemoryEntry(BaseModel):
    """A learned fact or preference stored for a user/venture."""
    key: str
    value: Any
    timestamp: float
    source: str # "user_correction", "system_inference", "external_data"
    verification_status: str = "unverified" # "unverified", "verified", "deprecated"

class LearningSession(BaseModel):
    """A collection of learned insights from a single analysis session."""
    session_id: str
    user_id: str
    insights: List[MemoryEntry]
    overall_confidence: float
