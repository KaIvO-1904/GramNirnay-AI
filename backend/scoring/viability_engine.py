from typing import List, Dict, Any, Optional
from .viability_models import ViabilityConfig, ComponentScore, ViabilityReport, ComponentStatus
from ..intelligence.models import LocalIntelligenceResult, DataPointMetadata, DataSourceType
from ..ontology.models import FinancialResult

class ViabilityEngine:
    """
    Deterministic aggregation engine that calculates the overall business viability score.
    Combines financial metrics and local intelligence data.
    """

    def __init__(self, config: Optional[ViabilityConfig] = None):
        self.config = config or ViabilityConfig()

    def _calculate_financial_score(self, fin: FinancialResult) -> float:
        """
        Maps financial metrics to a 0-1 score.
        Logic:
        - is_viable: +0.4
        - roi_percent > 20%: +0.3
        - break_even < 24 months: +0.3
        """
        score = 0.0
        if fin.is_viable:
            score += 0.4
        if fin.roi_percent > 20.0:
            score += 0.3
        if fin.break_even_months < 24.0:
            score += 0.3
        return min(1.0, score)

    def calculate_viability(
        self,
        financials: FinancialResult,
        intel: Optional[LocalIntelligenceResult]
    ) -> ViabilityReport:
        if not intel:
            # Calculate Financial Score since intelligence is missing
            fin_score = self._calculate_financial_score(financials)
            # Return a schema-valid report using the financial score as the base
            return ViabilityReport(
                overall_score=round(fin_score, 2),
                recommendation="Proceed with Caution" if fin_score >= 0.5 else "Insufficient Data",
                headline="Viability calculated based on financial projections; market intelligence is unavailable.",
                component_scores={"financials": self._create_component("Financials", fin_score, "Financial feasibility based on ROI and Break-even.")},
                positive_factors=["Financial projections show positive potential"] if fin_score >= 0.5 else [],
                negative_factors=["Market intelligence data unavailable"],
                risk_flags=["MISSING_INTELLIGENCE"],
                overall_confidence=0.3, # Low confidence due to missing intel
                data_sources=[]
            )
        # 1. Component Score Mapping
        components = {}

        # Financials
        fin_score = self._calculate_financial_score(financials)
        components["financials"] = self._create_component(
            "Financials", fin_score, "Financial feasibility based on ROI and Break-even."
        )

        # Demand
        demand_score = intel.demand.local_demand_score
        components["demand"] = self._create_component(
            "Market Demand", demand_score, f"Local demand estimated as {demand_score}."
        )

        # Competition
        # Higher competition score means MORE competition, which is NEGATIVE for viability.
        comp_score = 1.0 - intel.competition.competition_score
        components["competition"] = self._create_component(
            "Competition", comp_score, f"Competition level: {intel.competition.competition_score}."
        )

        # Supply Chain (Averaging Supplier Access and Raw Material Access)
        supply_score = (intel.supply_chain.supplier_access_score + intel.supply_chain.raw_material_score) / 2
        components["supply_chain"] = self._create_component(
            "Supply Chain", supply_score, f"Avg supply chain access: {supply_score}."
        )

        # Logistics (Averaging Transport and Accessibility)
        logistics_score = (intel.logistics.transport_score + intel.logistics.accessibility_score) / 2
        components["logistics"] = self._create_component(
            "Logistics", logistics_score, f"Logistics and accessibility: {logistics_score}."
        )

        # Risk (Calculated from operational risks count)
        # 0 risks = 1.0, 1 risk = 0.7, 2+ risks = 0.4
        risk_count = len(intel.demand.operational_risks)
        risk_score = 1.0 if risk_count == 0 else (0.7 if risk_count == 1 else 0.4)
        components["risk"] = self._create_component(
            "Risk", risk_score, f"Operational risk index based on {risk_count} identified risks."
        )

        # 2. Weighted Aggregation
        overall_score = 0.0
        total_weight = 0.0

        for key, component in components.items():
            weight = self.config.weights.get(key, 0.0)
            component.weight = weight
            component.contribution = component.score * weight
            overall_score += component.contribution
            total_weight += weight

        # Normalize if weights don't sum to 1
        if total_weight > 0 and total_weight != 1.0:
            overall_score /= total_weight

        # 3. Determine Recommendation and Headline
        score_pct = round(overall_score * 100, 0)
        if score_pct >= 80:
            recommendation = "Proceed"
            headline = "Strong market indicators and financial health. Ideal for immediate implementation."
        elif score_pct >= 50:
            recommendation = "Proceed with Modification"
            headline = "Viable potential, but requires strategic adjustments to reduce risk."
        else:
            recommendation = "Reconsider"
            headline = "Significant risks detected. We recommend pivoting the model before investing capital."

        # 4. Extract Positive/Negative Factors and Risk Flags
        positives = []
        negatives = []
        risk_flags = []

        for name, comp in components.items():
            if comp.score >= self.config.thresholds["strong"]:
                positives.append(f"{name.capitalize().replace('_', ' ')} is a strong point")
            elif comp.score <= self.config.thresholds["critical"]:
                negatives.append(f"{name.capitalize().replace('_', ' ')} is a critical weakness")
                risk_flags.append(f"Critical {name.capitalize().replace('_', ' ')} Risk")

        # 4. Data Sources and Confidence
        # Collect sources from the intelligence result
        sources = [
            intel.competition.metadata.source,
            intel.supply_chain.metadata.source,
            intel.logistics.metadata.source,
            intel.demand.metadata.source
        ]

        # Overall confidence is the average of component confidences
        overall_conf = (
            intel.competition.metadata.confidence +
            intel.supply_chain.metadata.confidence +
            intel.logistics.metadata.confidence +
            intel.demand.metadata.confidence
        ) / 4

        return ViabilityReport(
            overall_score=round(overall_score, 2),
            recommendation=recommendation,
            headline=headline,
            component_scores=components,
            positive_factors=positives,
            negative_factors=negatives,
            risk_flags=risk_flags,
            overall_confidence=round(overall_conf, 2),
            data_sources=list(set(sources))
        )

    def _create_component(self, name: str, score: float, reason: str) -> ComponentScore:
        status = ComponentStatus.STRONG
        if score <= self.config.thresholds["critical"]:
            status = ComponentStatus.CRITICAL
        elif score <= self.config.thresholds["warning"]:
            status = ComponentStatus.WARNING

        return ComponentScore(
            score=round(score, 2),
            weight=0.0, # Set during aggregation
            contribution=0.0, # Set during aggregation
            status=status,
            reason=reason
        )
