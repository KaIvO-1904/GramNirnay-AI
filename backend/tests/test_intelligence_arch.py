import pytest
from backend.ontology.models import BusinessProfile, BusinessCategory, FinancialParams, FinancialResult
from backend.validation.rules_engine import ValidationEngine, ValidationStatus
from backend.scoring.viability_engine import ViabilityEngine
from backend.location.service import LocationService

def test_business_profile_validation():
    # Valid profile
    profile = BusinessProfile(
        business_idea="Organic Farming",
        category=BusinessCategory.AGRICULTURE,
        available_capital=10000.0,
        location="Maharashtra",
        experience_years=2
    )
    result = ValidationEngine.validate_profile(profile)
    assert result.status == ValidationStatus.VALID

    # Invalid profile
    invalid_profile = BusinessProfile(
        business_idea="Too",
        category=BusinessCategory.OTHER,
        available_capital=-100.0,
        location="Unknown",
        experience_years=0
    )
    result = ValidationEngine.validate_profile(invalid_profile)
    assert result.status == ValidationStatus.INVALID
    assert any("too short" in e for e in result.errors)
    assert any("negative" in e for e in result.errors)

def test_financial_params_validation():
    # Valid params
    params = FinancialParams(
        setup_cost=50000.0,
        monthly_revenue=10000.0,
        monthly_expenses=5000.0,
        interest_rate=8.0,
        tenure_years=5,
        user_capital=10000.0
    )
    result = ValidationEngine.validate_financials(params)
    assert result.status == ValidationStatus.VALID

    # Invalid params
    invalid_params = FinancialParams(
        setup_cost=-1000.0,
        monthly_revenue=10000.0,
        monthly_expenses=-500.0,
        interest_rate=8.0,
        tenure_years=5,
        user_capital=10000.0
    )
    result = ValidationEngine.validate_financials(invalid_params)
    assert result.status == ValidationStatus.INVALID

def test_viability_scoring():
    # High viability
    engine = ViabilityEngine()
    result = FinancialResult(
        total_project_cost=100000.0,
        financing_required=50000.0,
        monthly_emi=1000.0,
        monthly_net_profit=5000.0,
        annual_net_profit=60000.0,
        roi_percent=60.0,
        break_even_months=12.0,
        is_viable=True,
        monthly_revenue=10000.0,
        annual_revenue=120000.0,
        monthly_expenses=5000.0,
        annual_expenses=60000.0
    )
    # Using the internal method for a direct test
    score = engine._calculate_financial_score(result)
    assert score == 1.0

    # Low viability
    low_result = FinancialResult(
        total_project_cost=100000.0,
        financing_required=90000.0,
        monthly_emi=2000.0,
        monthly_net_profit=-100.0,
        annual_net_profit=-1200.0,
        roi_percent=-1.2,
        break_even_months=120.0,
        is_viable=False,
        monthly_revenue=1000.0,
        annual_revenue=12000.0,
        monthly_expenses=5000.0,
        annual_expenses=60000.0
    )
    score = engine._calculate_financial_score(low_result)
    assert score == 0.0

def test_location_service():
    service = LocationService()
    constraints = service.get_regional_constraints("Maharashtra")
    assert any("land ceiling" in c for c in constraints)

    tips = service.get_local_tips("Maharashtra", "agriculture")
    assert any("Maharashtra" in t and "agriculture" in t for t in tips)
