from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class DataSourceType(str, Enum):
    OBSERVED = "Observed"      # Direct data from API/Database
    ESTIMATED = "Estimated"    # Calculated based on known patterns
    PROXY = "Proxy"            # Estimated via a related metric
    SYNTHETIC = "Synthetic"    # Generated for demo/testing

class DataPointMetadata(BaseModel):
    source: str
    timestamp: datetime = Field(default_factory=datetime.now)
    geographic_scope: str # "Village", "Taluk", "District", "State"
    confidence: float = Field(..., ge=0.0, le=1.0)
    data_type: DataSourceType

class LocalIntelligenceFeature(BaseModel):
    value: float # The normalized score (0.0 - 1.0)
    metadata: DataPointMetadata
    reasoning: str

class CompetitionAnalysis(BaseModel):
    competition_score: float
    competitor_density: float
    nearest_competitor_distance_km: float
    metadata: DataPointMetadata

class SupplyChainAnalysis(BaseModel):
    supplier_access_score: float
    raw_material_score: float
    avg_supplier_distance_km: float
    metadata: DataPointMetadata

class LogisticsAnalysis(BaseModel):
    transport_score: float
    accessibility_score: float
    estimated_transport_cost_index: float # 0.0 (low) to 1.0 (high)
    metadata: DataPointMetadata

class LocalDemandAnalysis(BaseModel):
    local_demand_score: float
    seasonality_index: float # 0.0 to 1.0
    operational_risks: List[str]
    metadata: DataPointMetadata

class LocalIntelligenceResult(BaseModel):
    """Consolidated local intelligence evaluation."""
    competition: CompetitionAnalysis
    supply_chain: SupplyChainAnalysis
    logistics: LogisticsAnalysis
    demand: LocalDemandAnalysis
    overall_confidence: float
    timestamp: datetime = Field(default_factory=datetime.now)

class CompetitorJSON(BaseModel):
    competitors: List[Dict[str, Any]]

class SupplierJSON(BaseModel):
    suppliers: List[Dict[str, Any]]

class LogisticsJSON(BaseModel):
    road_quality: str
    nearest_hub_km: float
    avg_transport_cost_index: float
    accessibility_rating: float

class DemandJSON(BaseModel):
    estimated_demand_score: float
    seasonality_index: float
    risks: List[str]
    footfall_proxy: str
