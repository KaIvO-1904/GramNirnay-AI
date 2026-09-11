import pytest
from backend.core.schemas.base import ConfidenceResult, GramNirnayError
from backend.core.schemas.domain import VentureProfile, LocationContext, FinancialBenchmarks, FinancialMetrics
from backend.core.schemas.validation import ValidationResult, ValidationIssue
from backend.services.financial.calculator import FinancialService
from backend.services.validation.validator import ValidationService

def test_confidence_result():
    res = ConfidenceResult(value=100, score=0.8, source="llm_estimate", reasoning_trace=["Step 1", "Step 2"])
    assert res.value == 100
    assert res.score == 0.8
    assert "Step 1" in res.reasoning_trace

def test_venture_profile_creation():
    loc = LocationContext(district="Ramanagara", state="Karnataka")
    profile = VentureProfile(
        businessIdea="Dairy Farm",
        location=loc,
        experience=5,
        availableCapital=100000,
        targetInvestment=500000,
        answers={"q1": "option_a"}
    )
    assert profile.business_idea == "Dairy Farm"
    assert profile.location.district == "Ramanagara"

def test_financial_service():
    service = FinancialService()
    benchmarks = FinancialBenchmarks(
        setup_cost=500000,
        monthly_revenue=50000,
        monthly_expenses=20000,
        user_capital=100000,
        category="dairy"
    )
    metrics = service.execute(benchmarks)
    assert isinstance(metrics, FinancialMetrics)
    assert metrics.total_project_cost == 500000
    assert metrics.monthly_net_profit > 0

def test_validation_service():
    service = ValidationService()
    # Invalid profile (negative capital)
    loc = LocationContext(district="Ramanagara", state="Karnataka")
    profile = VentureProfile(
        businessIdea="Dairy Farm",
        location=loc,
        experience=5,
        availableCapital=-100,
        targetInvestment=500000
    )
    result = service.execute(profile)
    assert result.is_valid is False
    assert any("negative" in issue.message.lower() for issue in result.issues)

def test_error_model():
    err = GramNirnayError(code="VAL_001", message="Invalid input", is_deterministic=True)
    assert err.code == "VAL_001"
    assert err.is_deterministic is True
