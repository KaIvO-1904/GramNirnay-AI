from typing import List
from ..ontology.models import BusinessProfile, FinancialParams, IntelligenceResult, SchemeMatch
from ..location.geo_service import LocationService
from ..rag_engine import RAGEngine
from .engine import LocalIntelligenceEngine

class KnowledgeManager:
    """Orchestrates RAG, Location, and Local Intelligence services."""

    def __init__(self):
        self.rag_engine = RAGEngine()
        self.location_service = LocationService()
        self.local_intel_engine = LocalIntelligenceEngine()

    def get_intelligence(self, profile: BusinessProfile, financial_params: FinancialParams) -> IntelligenceResult:
        # 1. Get matched schemes from RAG
        # Convert Pydantic models to dict for existing RAGEngine compatibility
        schemes = self.rag_engine.get_best_schemes(
            profile.model_dump(),
            financial_params.model_dump()
        )

        # 2. Convert raw schemes to SchemeMatch models
        matched_schemes = []
        for s in schemes:
            matched_schemes.append(SchemeMatch(
                scheme_id=s["schemeId"],
                name=s["name"],
                benefit=s["benefit"],
                eligibility_score=0.9, # Placeholder for ranking score
                match_reason="Matches your business category and capital requirements."
            ))

        # 3. Get Local Intelligence (The new engine)
        # We use the coordinates from the profile if available, otherwise fallback
        # Note: profile.location is a string in BusinessProfile, we'd need the actual LocationIdentity
        # For now, we assume the coordinates are passed or resolved

        # Mocking coordinates for the la_intel_engine call since BusinessProfile doesn't have them
        from .models import LocationIdentity, LocationHierarchy
        mock_coords = LocationIdentity(
            lat=12.97, lng=77.59,
            hierarchy=LocationHierarchy(state="Karnataka", district="Bengaluru", village="Bengaluru City"),
            provider_id="bengaluru_city",
            confidence=1.0,
            source="manual"
        )

        local_intel = self.local_intel_engine.analyze_location(
            mock_coords,
            profile.category.value
        )

        # 4. Get regional intelligence from LocationService
        constraints = self.location_service.get_regional_constraints(profile.location)
        tips = self.location_service.get_local_tips(profile.location, profile.category.value)

        return IntelligenceResult(
            matched_schemes=matched_schemes,
            regional_constraints=constraints,
            local_tips=tips,
            # We'd add local_intel to the IntelligenceResult model in a real scenario
        )
