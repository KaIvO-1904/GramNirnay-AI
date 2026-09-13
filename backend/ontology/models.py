from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from ..core.schemas.domain import Scheme
from ..intelligence.models import LocalIntelligenceResult

class BusinessCategory(str, Enum):
    AGRICULTURE = "agriculture"
    LIVESTOCK = "livestock"
    POULTRY = "poultry"
    DAIRY = "dairy"
    GOAT_FARMING = "goat_farming"
    HANDICRAFTS = "handicrafts"
    SERVICES = "services"
    TRADING = "trading"
    RETAIL_CLOTH = "retail_cloth"
    RETAIL_KIRANA = "retail_kirana"
    AGRO_RETAIL = "agro_retail"
    MICRO_ENTERPRISE = "micro_enterprise"
    OTHER = "other"

class BusinessProfile(BaseModel):
    """Normalized business context."""
    business_idea: str = Field(..., description="Detailed description of the business idea")
    category: BusinessCategory = Field(BusinessCategory.OTHER, description="The sector the business belongs to")
    available_capital: float = Field(0.0, description="Capital available with the user")
    location: str = Field("Unknown", description="User's location (state/district)")
    experience_years: int = Field(0, description="Relevant experience of the user")
    target_audience: Optional[str] = None

class FinancialParams(BaseModel):
    """Parameters required for financial projection."""
    setup_cost: float = Field(..., description="Total initial cost to start the business")
    monthly_revenue: float = Field(0.0, description="Estimated monthly revenue")
    monthly_expenses: float = Field(0.0, description="Estimated monthly operating expenses")
    interest_rate: float = Field(0.0, description="Expected loan interest rate")
    tenure_years: int = Field(5, description="Loan repayment period in years")
    user_capital: float = Field(0.0, description="Amount of capital provided by the user")

class FinancialResult(BaseModel):
    """Output of the deterministic financial engine."""
    total_project_cost: float
    financing_required: float
    monthly_emi: float
    monthly_net_profit: float
    annual_net_profit: float
    roi_percent: float
    break_even_months: Optional[float]
    is_viable: bool

class SchemeMatch(BaseModel):
    """Model for a matched government scheme."""
    scheme_id: str
    name: str
    benefit: str
    eligibility_score: float = Field(0.0, description="How well the user fits the scheme")
    match_reason: str = Field(..., description="Why this scheme was recommended")


class IntelligenceResult(BaseModel):
    """Consolidated intelligence output."""
    local_intelligence: Optional[LocalIntelligenceResult] = None
    matched_schemes: List[Scheme]
    regional_constraints: List[str] = []
    local_tips: List[str] = []

class ValidationStatus(str, Enum):
    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"

class ValidationResult(BaseModel):
    """Model for deterministic business rule validation."""
    status: ValidationStatus
    errors: List[str] = []
    warnings: List[str] = []
    fixed_data: Optional[Dict[str, Any]] = None

class ConfidenceScore(BaseModel):
    """Standardized confidence model for AI outputs."""
    score: float = Field(..., ge=0.0, le=1.0)
    reason: str
    is_reliable: bool

class AgentResponse(BaseModel):
    """Standardized response model for LLM agents."""
    content: str
    structured_data: Optional[Any] = None
    confidence: ConfidenceScore
    metadata: Dict[str, Any] = {}

class GramNirnayError(Exception):
    """Base exception for the architecture."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", details: Any = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details

class InterpretationError(GramNirnayError):
    """Raised when LLM fails to structure the input."""
    pass

class ValidationError(GramNirnayError):
    """Raised when business rules are violated."""
    pass

class CalculationError(GramNirnayError):
    """Raised when financial engine fails."""
    pass
