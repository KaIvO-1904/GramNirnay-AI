from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class LocationContext(BaseModel):
    """Geospatial and administrative context of the venture."""
    district: str
    state: str
    coordinates: Optional[Dict[str, float]] = None  # {"lat": 0.0, "lng": 0.0}
    rural_classification: Optional[str] = None  # e.g., "Tier-3", "Village"
    timezone: str = "IST"

class BusinessContext(BaseModel):
    """Normalized business parameters extracted from user input."""
    venture_type: str
    scale: str  # e.g., "micro", "small", "medium"
    operational_model: str # e.g., "direct-to-consumer", "wholesale"
    estimated_capacity: Optional[float] = None
    industry_standard_proxies: Dict[str, Any] = Field(default_factory=dict)

class LocalIntelligence(BaseModel):
    """Hyper-local market data used for viability scoring."""
    demand_index: float = Field(..., ge=0.0, le=1.0)
    competition_density: str # "Low", "Medium", "High"
    infrastructure_score: float = Field(..., ge=0.0, le=1.0)
    supplier_availability: str # "Readily Available", "Limited", "Difficult"
    transport_accessibility: str # "Good", "Fair", "Poor"
    market_proxies: Dict[str, Any] = Field(default_factory=dict)
