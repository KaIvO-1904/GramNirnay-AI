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

class FinancialMetrics(BaseModel):
    """Deterministic output of the Financial Engine."""
    total_project_cost: float
    is_viable: bool
    roi_percent: float
    break_even_months: float
    monthly_profit: float = Field(..., alias="monthly_net_profit")
    monthly_revenue: float = Field(..., alias="monthly_revenue")
    monthly_expenses: float = Field(..., alias="monthly_expenses")
    emi: float
    loan_amount: float
    user_capital: float
    min_viable_capital: float
    capital_breakdown: Dict[str, float]

    class Config:
        populate_by_name = True

class MarketAnalysis(BaseModel):
    """Deterministic local intelligence data."""
    demand_score: float = Field(..., alias="demand", ge=0.0, le=100.0)
    competition_level: Any = Field(..., alias="competition")
    accessibility_score: float = Field(..., alias="accessibility", ge=0.0, le=100.0)
    market_proxies: Dict[str, Any] = Field(default_factory=dict)
    regional_risks: List[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True

class Scheme(BaseModel):
    """Government scheme data."""
    id: str
    name: str
    description: str
    benefit: str
    eligibility: List[str]
    link: str
    match_score: float = 0.0

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
