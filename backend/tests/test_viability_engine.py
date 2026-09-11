import pytest
from backend.scoring.viability_engine import ViabilityEngine
from backend.scoring.viability_models import ViabilityConfig, ComponentStatus
from backend.ontology.models import FinancialResult
from backend.intelligence.models import LocalIntelligenceResult, CompetitionAnalysis, SupplyChainAnalysis, LogisticsAnalysis, LocalDemandAnalysis, DataPointMetadata, DataSourceType

def create_mock_intel(
    comp_score=0.5,
    supply_score=0.5,
    log_score=0.5,
    demand_score=0.5,
    risks=None
):
    def get_meta():
        return DataPointMetadata(
            source="test", geographic_scope="Village", confidence=1.0, data_type=DataSourceType.OBSERVED
        )

    return LocalIntelligenceResult(
        competition=CompetitionAnalysis(competition_score=comp_score, competitor_density=0.2, nearest_competitor_distance_km=5.0, metadata=get_meta()),
        supply_chain=SupplyChainAnalysis(supplier_access_score=supply_score, raw_material_score=supply_score, avg_supplier_distance_km=10.0, metadata=get_meta()),
        logistics=LogisticsAnalysis(transport_score=log_score, accessibility_score=log_score, estimated_transport_cost_index=0.5, metadata=get_meta()),
        demand=LocalDemandAnalysis(local_demand_score=demand_score, seasonality_index=0.5, operational_risks=risks or [], metadata=get_meta()),
        overall_confidence=1.0
    )

def create_mock_financials(is_viable=True, roi=25.0, break_even=12.0):
    return FinancialResult(
        total_project_cost=100000.0,
        financing_required=50000.0,
        monthly_emi=1000.0,
        monthly_net_profit=5000.0,
        annual_net_profit=60000.0,
        roi_percent=roi,
        break_even_months=break_even,
        is_viable=is_viable
    )

def test_highly_viable_business():
    engine = ViabilityEngine()
    fin = create_mock_financials(is_viable=True, roi=30.0, break_even=10.0)
    intel = create_mock_intel(comp_score=0.9, supply_score=0.9, log_score=0.9, demand_score=0.9)

    report = engine.calculate_viability(fin, intel)
    assert report.overall_score > 0.8
    assert "Financials is a strong point" in report.positive_factors

def test_financially_impossible_business():
    engine = ViabilityEngine()
    fin = create_mock_financials(is_viable=False, roi=2.0, break_even=120.0)
    intel = create_mock_intel(comp_score=0.9, supply_score=0.9, log_score=0.9, demand_score=0.9)

    report = engine.calculate_viability(fin, intel)
    # Financials should pull down the score significantly
    assert report.component_scores["financials"].status == ComponentStatus.CRITICAL
    assert "Financials is a critical weakness" in report.negative_factors

def test_high_competition_low_score():
    engine = ViabilityEngine()
    fin = create_mock_financials()
    intel = create_mock_intel(comp_score=0.1, supply_score=0.9, log_score=0.9, demand_score=0.9)

    report = engine.calculate_viability(fin, intel)
    assert report.component_scores["competition"].status == ComponentStatus.CRITICAL
    assert "Critical Competition Risk" in report.risk_flags

def test_poor_supplier_access():
    engine = ViabilityEngine()
    fin = create_mock_financials()
    intel = create_mock_intel(comp_score=0.5, supply_score=0.2, log_score=0.5, demand_score=0.5)

    report = engine.calculate_viability(fin, intel)
    assert report.component_scores["supply_chain"].status == ComponentStatus.CRITICAL
    assert "Supply chain is a critical weakness" in report.negative_factors

def test_high_transport_cost():
    engine = ViabilityEngine()
    fin = create_mock_financials()
    intel = create_mock_intel(comp_score=0.5, supply_score=0.5, log_score=0.1, demand_score=0.5)

    report = engine.calculate_viability(fin, intel)
    assert report.component_scores["logistics"].status == ComponentStatus.CRITICAL
    assert "Critical Logistics Risk" in report.risk_flags

def test_missing_data_fallback():
    engine = ViabilityEngine()
    # Use low financial scores to simulate overall low viability
    fin = create_mock_financials(is_viable=False, roi=2.0, break_even=120.0)
    # Very low scores simulating poor data or bad metrics
    intel = create_mock_intel(comp_score=0.0, supply_score=0.0, log_score=0.0, demand_score=0.0)

    report = engine.calculate_viability(fin, intel)
    assert report.overall_score < 0.3
    assert len(report.risk_flags) > 1

def test_conflicting_data():
    engine = ViabilityEngine()
    # Great financials but terrible local demand (e.g. luxury store in a poverty-stricken village)
    fin = create_mock_financials(is_viable=True, roi=50.0, break_even=6.0)
    intel = create_mock_intel(comp_score=0.5, supply_score=0.5, log_score=0.5, demand_score=0.1)

    report = engine.calculate_viability(fin, intel)
    assert "Financials is a strong point" in report.positive_factors
    assert "Demand is a critical weakness" in report.negative_factors

def test_low_confidence_aggregation():
    engine = ViabilityEngine()
    fin = create_mock_financials()
    intel = create_mock_intel()
    # Manually lower confidence in one component
    intel.competition.metadata.confidence = 0.2

    report = engine.calculate_viability(fin, intel)
    # Overall confidence should be (1.0+1.0+1.0+0.2)/4 = 0.8
    assert report.overall_confidence == 0.8
