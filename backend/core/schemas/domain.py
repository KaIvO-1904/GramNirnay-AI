from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from .base import ConfidenceResult
from .context import LocationContext

class VentureProfile(BaseModel):
    """The canonical state of a business idea."""
    business_idea: str = Field(..., alias="businessIdea")
    location: LocationContext
    experience: int = 0
    available_capital: float = Field(0.0, alias="availableCapital")
    target_investment: Optional[float] = Field(0.0, alias="targetInvestment")
    answers: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        populate_by_name = True

class FinancialBenchmarks(BaseModel):
    """Deterministic inputs for financial calculations."""
    setup_cost: float = Field(..., alias="setup_cost")
    monthly_revenue: float = Field(..., alias="monthly_revenue")
    monthly_expenses: float = Field(..., alias="monthly_expenses")
    user_capital: float = Field(0.0, alias="user_capital")
    min_viable_capital: Optional[float] = None
    capital_breakdown: Dict[str, float] = Field(default_factory=dict)
    category: str = "rural_enterprise"
    business_blueprint: Optional[Dict[str, Any]] = None
    startup_roadmap: Optional[List[Dict[str, Any]]] = None
    regulatory_requirements: Optional[List[Dict[str, Any]]] = None
    risk_matrix: Optional[List[Dict[str, Any]]] = None

class FinancialMetrics(BaseModel):
    """Deterministic output of the Financial Engine."""
    total_project_cost: float
    financing_required: float
    min_viable_capital: float
    monthly_revenue: float
    monthly_expenses: float
    monthly_emi: float
    monthly_net_profit: float
    annual_net_profit: float
    roi_percent: float
    break_even_months: float
    is_viable: bool
    user_capital: float
    capital_breakdown: Dict[str, float] = Field(default_factory=dict)

    class Config:
        populate_by_name = True

class MarketAnalysis(BaseModel):
    """Deterministic local intelligence data."""
    demand: float = Field(..., ge=0.0, le=100.0)
    competition: float = Field(..., ge=0.0, le=100.0)
    accessibility: float = Field(..., ge=0.0, le=100.0)
    seasonality: float = Field(0.0, ge=0.0, le=100.0)
    source: str = "Estimated"
    confidence: str = "Medium"
    reasoning: Optional[str] = None
    market_proxies: Dict[str, Any] = Field(default_factory=dict)
    regional_risks: List[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True

class Scheme(BaseModel):
    """Government scheme data."""
    schemeId: str
    name: str
    ministry: str
    benefit: Dict[str, Any] = Field(..., description="Object containing subsidyPercent and loanAmount")
    sourceUrl: str
    eligibility: Dict[str, Any] = Field(..., description="Object containing minCapital, maxCapital, and categories")
    match_score: float = 0.0
    application_steps: Optional[List[str]] = Field(default=None, description="Step-by-step guide to apply for the scheme")
    detailed_eligibility: Optional[str] = Field(default=None, description="Detailed eligibility criteria for the scheme")


class ViabilityReport(BaseModel):
    """Final comprehensive report."""
    viability_score: int = Field(..., alias="viabilityScore")
    recommendation: str
    category: str
    market_analysis: MarketAnalysis = Field(..., alias="marketAnalysis")
    financials: FinancialMetrics
    interpreter_reasoning: str = Field(..., alias="interpreter_reasoning")
    modifications: List[str]
    matched_schemes: List[Scheme] = Field(..., alias="matchedSchemes")
