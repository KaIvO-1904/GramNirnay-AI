from typing import List, Dict, Any
from ..models import CompetitionAnalysis, DataPointMetadata, DataSourceType
from ..providers import ILocalIntelligenceProvider
from ..utils import haversine_distance

class CompetitionService:
    """Calculates competition metrics based on nearby businesses."""

    def __init__(self, provider: ILocalIntelligenceProvider):
        self.provider = provider

    def analyze(self, location_id, business_type: str) -> CompetitionAnalysis:
        # 1. Fetch raw competitor data
        competitors = self.provider.get_competitor_data(location_id, business_type)

        if not competitors:
            return CompetitionAnalysis(
                competition_score=1.0, # No competition is great
                competitor_density=0.0,
                nearest_competitor_distance_km=999.0,
                metadata=DataPointMetadata(
                    source="IntelligenceProvider",
                    geographic_scope="Village",
                    confidence=1.0,
                    data_type=DataSourceType.OBSERVED
                )
            )

        # 2. Calculate metrics
        distances = []
        for comp in competitors:
            dist = haversine_distance(
                (location_id.lat, location_id.lng),
                (comp["lat"], comp["lng"])
            )
            distances.append(dist)

        nearest_dist = min(distances)
        density = len(competitors) / 5.0 # Normalized: 5+ competitors = max density (1.0)
        density = min(1.0, density)

        # 3. Deterministic Score
        # Score is high if density is low and nearest competitor is far
        # Range 0.0 to 1.0
        competition_score = 1.0 - (0.7 * density + 0.3 * (1.0 / (1.0 + nearest_dist)))

        return CompetitionAnalysis(
            competition_score=round(competition_score, 2),
            competitor_density=round(density, 2),
            nearest_competitor_distance_km=round(nearest_dist, 2),
            metadata=DataPointMetadata(
                source="IntelligenceProvider",
                geographic_scope="Village",
                confidence=0.9,
                data_type=DataSourceType.OBSERVED
            )
        )
