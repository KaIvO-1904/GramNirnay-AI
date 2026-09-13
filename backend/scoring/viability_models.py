from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime

class ComponentStatus(str, Enum):
    STRONG = "Strong"
    WARNING = "Warning"
    CRITICAL = "Critical"

class ComponentScore(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    weight: float
    contribution: float
    status: ComponentStatus
    reason: str

class ViabilityConfig(BaseModel):
    """Configurable weights for the viability aggregation."""
    weights: Dict[str, float] = {
        "financials": 0.4,
        "demand": 0.2,
        "competition": 0.15,
        "supply_chain": 0.1,
        "logistics": 0.1,
        "risk": 0.05
    }
    thresholds: Dict[str, float] = {
        "critical": 0.3,
        "warning": 0.6,
        "strong": 0.8
    }

class ViabilityReport(BaseModel):
    """The final, deterministic viability report."""
    overall_score: float
    recommendation: str
    headline: str
    component_scores: Dict[str, ComponentScore]
    positive_factors: List[str]
    negative_factors: List[str]
    risk_flags: List[str]
    overall_confidence: float
    data_sources: List[str]
    timestamp: datetime = Field(default_factory=datetime.now)
