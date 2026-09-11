from typing import List, Dict, Any
from ..models import LogisticsAnalysis, DataPointMetadata, DataSourceType
from ..providers import ILocalIntelligenceProvider

class LogisticsService:
    """Evaluates transportation and accessibility."""

    def __init__(self, provider: ILocalIntelligenceProvider):
        self.provider = provider

    def analyze(self, location_id) -> LogisticsAnalysis:
        # 1. Fetch raw logistics data
        logistics_data = self.provider.get_logistics_data(location_id)

        # 2. Map raw data to scores
        # Road quality: Fair(0.5), Good(0.8), Poor(0.2)
        quality_map = {"Poor": 0.2, "Fair": 0.5, "Good": 0.8, "Excellent": 1.0}
        quality_score = quality_map.get(logistics_data.get("road_quality", "Fair"), 0.5)

        # Hub distance: < 5km (1.0), 5-20km (0.6), > 20km (0.3)
        hub_dist = logistics_data.get("nearest_hub_km", 20.0)
        if hub_dist < 5:
            hub_score = 1.0
        elif hub_dist < 20:
            hub_score = 0.6
        else:
            hub_score = 0.3

        # Transport score = avg of road quality and hub accessibility
        transport_score = (quality_score + hub_score) / 2

        # Accessibility score (direct from provider or proxy)
        accessibility_score = logistics_data.get("accessibility_rating", 0.5)

        # Transport cost index (0 to 1)
        cost_index = logistics_data.get("avg_transport_cost_index", 0.5)

        return LogisticsAnalysis(
            transport_score=round(transport_score, 2),
            accessibility_score=round(accessibility_score, 2),
            estimated_transport_cost_index=round(cost_index, 2),
            metadata=DataPointMetadata(
                source="IntelligenceProvider",
                geographic_scope="Taluk",
                confidence=0.7,
                data_type=DataSourceType.OBSERVED
            )
        )
