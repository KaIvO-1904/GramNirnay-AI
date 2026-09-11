from ..ontology.models import ConfidenceScore, FinancialResult

class ScoringEngine:
    """Deterministic scoring for AI and Financial outputs."""

    @staticmethod
    def calculate_financial_viability(result: FinancialResult) -> float:
        """
        Calculates a viability score from 0.0 to 1.0.
        Criteria:
        - Is viable: +0.4
        - ROI > 20%: +0.3
        - Break-even < 24 months: +0.3
        """
        score = 0.0
        if result.is_viable:
            score += 0.4
        if result.roi_percent > 20.0:
            score += 0.3
        if result.break_even_months < 24.0:
            score += 0.3

        return round(score, 2)

    @staticmethod
    def create_confidence(score: float, reason: str) -> ConfidenceScore:
        """Wraps a raw score into a ConfidenceScore model."""
        return ConfidenceScore(
            score=score,
            reason=reason,
            is_reliable=score >= 0.7
        )
