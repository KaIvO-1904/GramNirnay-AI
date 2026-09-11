from typing import List, Dict, Any
from ..models import SupplyChainAnalysis, DataPointMetadata, DataSourceType
from ..providers import ILocalIntelligenceProvider
from ..utils import haversine_distance

class SupplyChainService:
    """Evaluates raw material and supplier availability."""

    def __init__(self, provider: ILocalIntelligenceProvider):
        self.provider = provider

    def analyze(self, location_id, business_type: str) -> SupplyChainAnalysis:
        # 1. Fetch raw supplier data
        suppliers = self.provider.get_supplier_data(location_id, business_type)

        if not suppliers:
            return SupplyChainAnalysis(
                supplier_access_score=0.0,
                raw_material_score=0.0,
                avg_supplier_distance_km=999.0,
                metadata=DataPointMetadata(
                    source="IntelligenceProvider",
                    geographic_scope="District",
                    confidence=1.0,
                    data_type=DataSourceType.OBSERVED
                )
            )

        # 2. Calculate metrics
        distances = []
        for sup in suppliers:
            dist = haversine_distance(
                (location_id.lat, location_id.lng),
                (sup["lat"], sup["lng"])
            )
            distances.append(dist)

        avg_dist = sum(distances) / len(distances)

        # Score based on number of suppliers and distance
        # 3+ suppliers and distance < 10km = high score
        count_factor = min(1.0, len(suppliers) / 3.0)
        dist_factor = 1.0 / (1.0 + (avg_dist / 10.0))

        supplier_access_score = (count_factor * 0.5) + (dist_factor * 0.5)
        raw_material_score = (count_factor * 0.7) + (dist_factor * 0.3)

        return SupplyChainAnalysis(
            supplier_access_score=round(supplier_access_score, 2),
            raw_material_score=round(raw_material_score, 2),
            avg_supplier_distance_km=round(avg_dist, 2),
            metadata=DataPointMetadata(
                source="IntelligenceProvider",
                geographic_scope="District",
                confidence=0.8,
                data_type=DataSourceType.OBSERVED
            )
        )
