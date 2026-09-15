import os
import json
from unittest.mock import MagicMock, patch
from backend.orchestration.workflow import WorkflowManager
from backend.ontology.models import BusinessProfile, FinancialParams, BusinessCategory

def mock_ai_response(content, structured_data=None, confidence=0.9):
    mock = MagicMock()
    mock.result = structured_data if structured_data else content
    mock.confidence = confidence
    mock.evidence = []
    return mock

def test_pipeline():
    wm = WorkflowManager()

    # --- TEST CASE 1: Indian Dairy Profile (Full Data) ---
    print("\n--- Testing Case 1: Indian Dairy Profile ---")
    profile1 = BusinessProfile(
        business_idea="Modern Dairy Farm in Punjab",
        category=BusinessCategory.DAIRY,
        available_capital=500000,
        location="Ludhiana, Punjab",
        experience_years=2
    )
    params1 = FinancialParams(
        setup_cost=2000000,
        monthly_revenue=150000,
        monthly_expenses=80000,
        interest_rate=9.0,
        tenure_years=5,
        user_capital=500000
    )

    with patch('backend.agents.interpretation.InterpretationAgent.execute') as mock_interp, \
         patch('backend.agents.explanation.ExplanationAgent.execute') as mock_expl:

        mock_interp.return_value = mock_ai_response("Interpreted", structured_data={"profile": profile1, "financials": params1}, confidence=1.0)
        mock_expl.return_value = mock_ai_response("Advice Letter Content")

        state = wm.run_pipeline("I want to start a dairy farm in Punjab", profile=profile1, financial_params=params1)
        result = wm.format_for_frontend(state)

        print(f"Status: {result['status']}")
        print(f"Viability Score: {result['viabilityScore']}")
        print(f"Blueprint Step 1: {result['business_blueprint']['flow'][0]['step']}")
        print(f"Roadmap Week 1: {result['startup_roadmap'][0]['tasks'][0]}")
        print(f"Financials - ROI: {result['financials']['roi_percent']}")

        assert result['status'] in ["SUCCESS", "PARTIAL"]
        assert result['business_blueprint']['flow'][0]['step'] == "Livestock Procurement"

    # --- TEST CASE 2: International Hydroponics (Mixed/Partial Data) ---
    print("\n--- Testing Case 2: International Hydroponics ---")
    profile2 = BusinessProfile(
        business_idea="Urban Hydroponic Farm in Singapore",
        category=BusinessCategory.OTHER, # Hydroponics isn't explicitly in enum
        available_capital=10000,
        location="Singapore",
        experience_years=0
    )
    params2 = FinancialParams(
        setup_cost=50000,
        monthly_revenue=5000,
        monthly_expenses=None, # Test expense fallback
        interest_rate=5.0,
        tenure_years=3,
        user_capital=10000
    )

    with patch('backend.agents.interpretation.InterpretationAgent.execute') as mock_interp, \
         patch('backend.agents.explanation.ExplanationAgent.execute') as mock_expl:

        mock_interp.return_value = mock_ai_response("Interpreted", structured_data={"profile": profile2, "financials": params2}, confidence=1.0)
        mock_expl.return_value = mock_ai_response("Advice Letter Content")

        state = wm.run_pipeline("Urban hydroponics in Singapore", profile=profile2, financial_params=params2)
        result = wm.format_for_frontend(state)

        print(f"Status: {result['status']}")
        print(f"Expenses (Fallback): {result['financials']['monthly_expenses']}")
        print(f"Blueprint Step 1: {result['business_blueprint']['flow'][0]['step']}")

        assert result['financials']['monthly_expenses'] is not None
        assert result['business_blueprint']['flow'][0]['step'] == "Market Research" # Fallback for OTHER

    # --- TEST CASE 3: Critical Failure (Missing setup_cost) ---
    print("\n--- Testing Case 3: Critical Failure ---")
    params3 = {"setup_cost": None} # Missing critical input

    state = wm.run_pipeline("Invalid request", profile=profile1, financial_params=params3)
    result = wm.format_for_frontend(state)
    print(f"Status: {result['status']}")
    assert result['status'] == "FAILED"

    print("\nALL TESTS PASSED SUCCESSFULLY")

if __name__ == "__main__":
    test_pipeline()
