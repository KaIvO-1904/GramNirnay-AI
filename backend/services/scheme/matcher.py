from ..base_service import BaseService
from ...rag_engine import RAGEngine
from ...core.schemas.domain import Scheme, VentureProfile, FinancialBenchmarks
from typing import List, Dict, Any

class SchemeService(BaseService[List[Scheme]]):
    """
    Service for government scheme matching.
    Wraps RAGEngine for deterministic filtering and AI ranking.
    """

    def __init__(self):
        self.engine = RAGEngine()

    def execute(self, profile: VentureProfile, benchmarks: FinancialBenchmarks) -> List[Scheme]:
        """
        Match and rank government schemes.
        """
        try:
            # Wrap models as dicts for legacy engine
            profile_dict = profile.model_dump(by_alias=True)
            benchmarks_dict = benchmarks.model_dump(by_alias=True)

            results = self.engine.get_best_schemes(profile_dict, benchmarks_dict)

            # Map to Scheme models
            return [
                Scheme(
                    id=s.get("schemeId", "unknown"),
                    name=s.get("name", "Unknown Scheme"),
                    description=s.get("description", ""),
                    benefit=s.get("benefit", ""),
                    eligibility=s.get("eligibility", {}).get("categories", []),
                    link=s.get("link", ""),
                    match_score=s.get("match_score", 0.0)
                ) for s in results
            ]
        except Exception as e:
            self.handle_error(e, "Scheme matching failed")
