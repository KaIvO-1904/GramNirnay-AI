from pydantic import BaseModel, Field
from typing import List, Optional

class ValidationIssue(BaseModel):
    """A single contradiction or business rule violation."""
    field: str
    message: str
    severity: str = Field("Error", description="Error, Warning, or Info")
    suggestion: Optional[str] = None

class ValidationResult(BaseModel):
    """The outcome of a semantic validation pass."""
    is_valid: bool
    issues: List[ValidationIssue] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
    confidence_score: float = Field(1.0, ge=0.0, le=1.0)
