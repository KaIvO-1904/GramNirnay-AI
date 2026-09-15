from typing import List, Optional, Any
from ..ontology.models import BusinessProfile, FinancialParams, IntelligenceResult, SchemeMatch
from ..location.service import LocationService
from ..rag_engine import RAGEngine
from .engine import LocalIntelligenceEngine

class KnowledgeManager:
    """Orchestrates RAG, Location, and Local Intelligence services."""

    def __init__(self):
        self.rag_engine = RAGEngine()
        self.location_service = LocationService()
        self.local_intel_engine = LocalIntelligenceEngine()

    def get_intelligence(self, profile: BusinessProfile, financial_params: Any, location_identity: Optional[Any] = None) -> IntelligenceResult:
        # 1. Get matched schemes from RAG
        # Convert Pydantic models to dict for existing RAGEngine compatibility
        schemes = self.rag_engine.get_best_schemes(
            profile.model_dump(),
            financial_params.model_dump()
        )

        # 2. Local Intelligence (The new engine)
        if location_identity:
            local_intel = self.local_intel_engine.analyze_location(
                location_identity,
                profile.category.value
            )
        else:
            # Location could not be resolved.
            # Instead of silently defaulting to Bengaluru, mark intelligence as unavailable.
            local_intel = None
            from ..logger import logger
            logger.warning(f"Intelligence analysis failed: No resolved location identity for profile {profile.business_idea}")

        # 3. Get regional intelligence from LocationService
        constraints = self.location_service.get_regional_constraints(profile.location)
        tips = self.location_service.get_local_tips(profile.location, profile.category.value)

        return IntelligenceResult(
            local_intelligence=local_intel,
            matched_schemes=schemes,
            regional_constraints=constraints,
            local_tips=tips,
        )
