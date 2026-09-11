from dataclasses import dataclass, field
from typing import Optional, Any
from .ontology.models import BusinessProfile, FinancialParams, FinancialResult, IntelligenceResult, ValidationResult

@dataclass
class PipelineState:
    """Holds the state of a single request as it moves through the pipeline."""
    request_id: str
    user_input: str

    # Interpretation Stage
    profile: Optional[BusinessProfile] = None
    financial_params: Optional[FinancialParams] = None
    interpretation_confidence: float = 0.0

    # Validation Stage
    validation_result: Optional[ValidationResult] = None

    # Calculation Stage
    financial_result: Optional[FinancialResult] = None
    viability_score: float = 0.0

    # Intelligence Stage
    intelligence_result: Optional[IntelligenceResult] = None

    # Final Stage
    final_explanation: Optional[str] = None

    metadata: dict = field(default_factory=dict)
