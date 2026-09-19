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

class BlueprintStep(BaseModel):
    step: str
    desc: str

class RoadmapWeek(BaseModel):
    week: int
    tasks: List[str]

class RegulatoryDoc(BaseModel):
    doc: str
    status: str
    source: str

class RiskFactor(BaseModel):
    risk: str
    severity: str
    probability: str
    mitigation: str

class BlueprintEnrichment(BaseModel):
    """Schema for the LLM-generated business blueprint enrichment."""
    business_blueprint: Optional[Dict[str, Any]] = None
    startup_roadmap: Optional[List[RoadmapWeek]] = None
    regulatory_requirements: Optional[List[RegulatoryDoc]] = None
    risk_matrix: Optional[List[RiskFactor]] = None
    provenance: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {"source": "AI_ESTIMATE", "confidence": "Medium"},
        description="Data provenance for the generated content"
    )

class InterpretationResult(BaseModel):
    """Schema for the LLM-generated initial interpretation."""
    setup_cost: float = 0.0
    min_viable_capital: float = 0.0
    monthly_revenue: float = 0.0
    monthly_expenses: float = 0.0
    interest_rate: float = 0.0
    tenure_years: int = 5
    category: str = "other"
    capital_breakdown: Dict[str, float] = Field(default_factory=dict)
    business_blueprint: Optional[Dict[str, Any]] = None
    startup_roadmap: Optional[List[Dict[str, Any]]] = None
    regulatory_requirements: Optional[List[Dict[str, Any]]] = None
    risk_matrix: Optional[List[Dict[str, Any]]] = None
    reasoning: str = ""
    modifications: List[str] = Field(default_factory=list)

class MarketProxyResult(BaseModel):
    """Schema for hyper-local market proxies."""
    demand: float = 50.0
    competition: float = 50.0
    accessibility: float = 50.0
    seasonality: float = 50.0
    reasoning: str = ""

class SchemeRankResult(BaseModel):
    """Schema for AI ranking of government schemes."""
    ranked_ids: List[str] = Field(default_factory=list)

class SchemeEnrichmentResult(BaseModel):
    """Schema for AI-driven scheme application guides."""
    application_steps: List[str] = Field(default_factory=list)
    detailed_eligibility: str = "Refer to official portal."

class NormalizationJSON(BaseModel):
    """Schema for semantic normalization output."""
    canonical_name: Optional[str] = None
    confidence: float = 0.0
    mapping_type: str = "NONE" # EXACT, ALIAS, FUZZY, INCOMPATIBLE
    reason: str = ""

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
    monthly_expenses: Optional[float] = Field(0.0, description="Estimated monthly operating expenses")
    interest_rate: float = Field(0.0, description="Expected loan interest rate")
    tenure_years: int = Field(5, description="Loan repayment period in years")
    user_capital: float = Field(0.0, description="Amount of capital provided by the user")
    # Enriched data from the interpreter
    capital_breakdown: Dict[str, float] = Field(default_factory=dict)
    business_blueprint: Optional[Dict[str, Any]] = None
    startup_roadmap: Optional[List[Dict[str, Any]]] = None
    regulatory_requirements: Optional[List[Dict[str, Any]]] = None
    risk_matrix: Optional[List[Dict[str, Any]]] = None

class FinancialResult(BaseModel):
    """Output of the deterministic financial engine."""
    total_project_cost: float
    financing_required: float
    monthly_emi: float

    # Income
    monthly_revenue: float
    annual_revenue: float

    # Expenditure
    monthly_expenses: float
    annual_expenses: float

    # Profits
    monthly_net_profit: float
    annual_net_profit: float

    roi_percent: float
    break_even_months: Optional[float]
    is_viable: bool

    # Detailed Breakdown for UI
    expenditure_breakdown: Dict[str, float] = Field(default_factory=dict)
    income_breakdown: Dict[str, float] = Field(default_factory=dict)
    assumptions: Dict[str, str] = Field(default_factory=dict)

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

class AnalysisRequest(BaseModel):
    """Canonical request for the analysis pipeline."""
    user_input: str = Field(..., description="Natural language description of the business")
    profile: Optional[BusinessProfile] = None
    financial_params: Optional[FinancialParams] = None
    answers: Dict[str, Any] = Field(default_factory=dict, description="Structured answers from the questionnaire")
    location: Optional[Dict[str, Any]] = None

class InterpretationError(GramNirnayError):
    """Raised when LLM fails to structure the input."""
    pass

class ValidationError(GramNirnayError):
    """Raised when business rules are violated."""
    pass

class CalculationError(GramNirnayError):
    """Raised when financial engine fails."""
    pass
