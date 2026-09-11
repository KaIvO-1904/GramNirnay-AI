from typing import TypeVar, Generic, List, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar("T")

class GramNirnayError(BaseModel):
    """Standardized error model for the system."""
    code: str
    message: str
    details: Optional[dict] = None
    is_deterministic: bool = True  # True if it's a business rule failure, False if AI failure

class ConfidenceResult(BaseModel, Generic[T]):
    """Wrapper for probabilistic results from LLMs/Agents."""
    value: T
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
    reasoning_trace: List[str] = Field(default_factory=list, description="Step-by-step logic used to reach result")
    source: str = Field(..., description="Source of the value (e.g., 'ontology', 'llm_estimate', 'user_input')")
