from typing import Dict, Any, List
from ..services.financial.calculator import FinancialService
from ..services.scheme.matcher import SchemeService
from ..services.validation.validator import ValidationService
from ..core.schemas.domain import VentureProfile, FinancialBenchmarks, ViabilityReport, FinancialMetrics, MarketAnalysis
from ..core.schemas.base import GramNirnayError

class OrchestrationManager:
    """
    Coordinates the interaction between Agents and Services.
    Acts as the high-level workflow manager.
    """

    def __init__(self):
        self.financial_service = FinancialService()
        self.scheme_service = SchemeService()
        self.validation_service = ValidationService()

    async def run_viability_pipeline(self, profile: VentureProfile, benchmarks: FinancialBenchmarks, market_analysis: MarketAnalysis) -> ViabilityReport:
        """
        The core orchestrated pipeline: Validation -> Calculation -> Scheme Matching.
        """
        # 1. Deterministic Validation
        val_result = self.validation_service.execute(profile)
        if not val_result.is_valid:
            # We can decide to stop or just warn. For now, we continue but log issues.
            pass

        # 2. Deterministic Calculation
        financials = self.financial_service.execute(benchmarks)

        # 3. Scheme Matching
        schemes = self.scheme_service.execute(profile, benchmarks)

        # 4. Final Heuristic Scoring (Legacy logic preserved)
        base_score = 55
        if financials.is_viable:
            base_score += 25

        roi_bonus = min(15, max(0, (financials.roi_percent / 6)))
        be_bonus = max(0, 10 - (financials.break_even_months / 6))

        viability_score = int(base_score + roi_bonus + be_bonus)
        viability_score = min(100, max(0, viability_score))

        recommendation = "Highly Viable" if viability_score >= 80 else ("Proceed with Modification" if financials.is_viable else "Reconsider")

        return ViabilityReport(
            viabilityScore=viability_score,
            recommendation=recommendation,
            category=benchmarks.category,
            marketAnalysis=market_analysis,
            financials=financials,
            interpreter_reasoning="Orchestrated analysis based on deterministic financial modeling.",
            modifications=[
                "Structure phased capital deployment to optimize initial cashflow.",
                "Leverage government credit-linked subsidies to reduce debt burden."
            ],
            matchedSchemes=schemes
        )
