from typing import List, Dict, Any, Optional
from .models import (
    LocalIntelligenceResult,
    CompetitionAnalysis,
    SupplyChainAnalysis,
    LogisticsAnalysis,
    LocalDemandAnalysis,
    DataPointMetadata,
    DataSourceType
)
from .providers import ILocalIntelligenceProvider, MockLocalIntelligenceProvider
from .services.competition_service import CompetitionService
from .services.supply_chain_service import SupplyChainService
from .services.logistics_service import LogisticsService

class LocalIntelligenceEngine:
    """
    Orchestrates the local intelligence analysis.
    Aggregates data from multiple specialized services to produce a consolidated result.
    """

    def __init__(self, provider: Optional[ILocalIntelligenceProvider] = None):
        # Inject provider (Mock by default)
        self.provider = provider or MockLocalIntelligenceProvider()

        # Initialize sub-services
        self.competition_service = CompetitionService(self.provider)
        self.supply_chain_service = SupplyChainService(self.provider)
        self.logistics_service = LogisticsService(self.provider)

    def analyze_location(self, location_id, business_type: str) -> LocalIntelligenceResult:
        """
        Performs a full local intelligence evaluation for a specific location and business.
        """
        # 1. Calculate Competition
        comp_analysis = self.competition_service.analyze(location_id, business_type)

        # 2. Calculate Supply Chain
        supply_analysis = self.supply_chain_service.analyze(location_id, business_type)

        # 3. Calculate Logistics
        logistics_analysis = self.logistics_service.analyze(location_id)

        # 4. Handle Demand (Directly from provider as it's usually an estimation/proxy)
        demand_data = self.provider.get_demand_data(location_id, business_type)
        demand_analysis = LocalDemandAnalysis(
            local_demand_score=round(demand_data.get("estimated_demand_score", 0.5), 2),
            seasonality_index=round(demand_data.get("seasonality_index", 0.5), 2),
            operational_risks=demand_data.get("risks", []),
            metadata=DataPointMetadata(
                source="IntelligenceProvider",
                geographic_scope="District",
                confidence=0.8,
                data_type=DataSourceType.ESTIMATED
            )
        )

        # 5. Calculate overall confidence
        # Avg of all component confidences
        confidences = [
            comp_analysis.metadata.confidence,
            supply_analysis.metadata.confidence,
            logistics_analysis.metadata.confidence,
            demand_analysis.metadata.confidence
        ]
        overall_confidence = sum(confidences) / len(confidences)

        return LocalIntelligenceResult(
            competition=comp_analysis,
            supply_chain=supply_analysis,
            logistics=logistics_analysis,
            demand=demand_analysis,
            overall_confidence=round(overall_confidence, 2)
        )
