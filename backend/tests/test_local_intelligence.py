import pytest
from backend.intelligence.engine import LocalIntelligenceEngine
from backend.intelligence.models import DataSourceType
from backend.location.models import LocationIdentity, LocationHierarchy, CurrencyInfo

def test_local_intelligence_deterministic_scores():
    engine = LocalIntelligenceEngine()

    # Create a mock location
    loc = LocationIdentity(
        name="Bengaluru City",
        district="Bengaluru",
        state="Karnataka",
        country="India",
        lat=12.97, lng=77.59,
        provider_id="bengaluru_city",
        source="manual",
        currency=CurrencyInfo(code="INR", symbol="₹", locale="en-IN")
    )

    result = engine.analyze_location(loc, "poultry")

    # Test Competition
    assert 0.0 <= result.competition.competition_score <= 1.0
    assert result.competition.metadata.data_type == DataSourceType.OBSERVED

    # Test Supply Chain
    assert 0.0 <= result.supply_chain.supplier_access_score <= 1.0
    assert result.supply_chain.metadata.geographic_scope == "District"

    # Test Logistics
    assert 0.0 <= result.logistics.transport_score <= 1.0
    assert result.logistics.metadata.source == "IntelligenceProvider"

    # Test Demand
    assert 0.0 <= result.demand.local_demand_score <= 1.0
    assert result.demand.metadata.data_type == DataSourceType.ESTIMATED

def test_determinism():
    engine = LocalIntelligenceEngine()
    loc = LocationIdentity(
        name="Bengaluru City",
        district="Bengaluru",
        state="Karnataka",
        country="India",
        lat=12.97, lng=77.59,
        provider_id="bengaluru_city",
        source="manual",
        currency=CurrencyInfo(code="INR", symbol="₹", locale="en-IN")
    )

    res1 = engine.analyze_location(loc, "poultry")
    res2 = engine.analyze_location(loc, "poultry")

    assert res1.competition.competition_score == res2.competition.competition_score
    assert res1.supply_chain.supplier_access_score == res2.supply_chain.supplier_access_score
    assert res1.overall_confidence == res2.overall_confidence

def test_confidence_aggregation():
    engine = LocalIntelligenceEngine()
    loc = LocationIdentity(
        name="Bengaluru City",
        district="Bengaluru",
        state="Karnataka",
        country="India",
        lat=12.97, lng=77.59,
        provider_id="bengaluru_city",
        source="manual",
        currency=CurrencyInfo(code="INR", symbol="₹", locale="en-IN")
    )

    result = engine.analyze_location(loc, "poultry")
    # Sum of confidences / 4
    expected_conf = (
        result.competition.metadata.confidence +
        result.supply_chain.metadata.confidence +
        result.logistics.metadata.confidence +
        result.demand.metadata.confidence
    ) / 4

    assert result.overall_confidence == round(expected_conf, 2)
