import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from backend.orchestration.workflow import WorkflowManager
from backend.agents.base import AgentResponse, AgentStatus, NextAction
from backend.ontology.models import FinancialParams, BusinessProfile
from unittest.mock import MagicMock

def test_missing_location_no_crash():
    print("Testing missing location identity handles gracefully...")
    wf = WorkflowManager()
    
    # Mock Interpretation to return a profile with NO location resolveable
    wf.interpretation_agent = MagicMock()
    wf.interpretation_agent.execute.return_value = AgentResponse(
        status=AgentStatus.SUCCESS,
        confidence=0.9,
        result={"profile": {"business_idea": "Cloth Store", "location": "Invalid Location"}, "financials": {"setup_cost": 100}},
        next_action=NextAction.PROCEED
    )
    
    # Mock location service to return no candidates
    wf.knowledge_manager = MagicMock()
    wf.knowledge_manager.location_service.search_place.return_value = []
    wf.knowledge_manager.get_intelligence = MagicMock(return_value=MagicMock(local_intelligence=None))
    
    wf.validation_engine = MagicMock()
    wf.validation_engine.validate_profile.return_value = MagicMock(status="valid")
    wf.financial_engine = MagicMock()
    wf.financial_engine.compute_full_model.return_value = {"total_project_cost": 100, "financing_required": 50, "monthly_emi": 10, "monthly_net_profit": 20, "annual_net_profit": 240, "roi_percent": 20, "break_even_months": 12, "is_viable": True}
    wf.viability_engine = MagicMock()
    wf.viability_engine._calculate_financial_score = lambda x: 0.8
    wf.viability_engine.calculate_viability = MagicMock(return_value=MagicMock(
        overall_score=0.0, 
        recommendation="Insufficient Data", 
        headline="Viability could not be fully calculated due to missing market intelligence.",
        component_scores={},
        positive_factors=[],
        negative_factors=["Market intelligence data unavailable"],
        risk_flags=["MISSING_INTELLIGENCE"],
        overall_confidence=0.0,
        data_sources=[]
    ))
    wf.rag_engine = MagicMock()
    wf.rag_engine.get_best_schemes = lambda p, f: []
    wf.explanation_agent = MagicMock()
    wf.explanation_agent.execute.return_value = AgentResponse(
        status=AgentStatus.SUCCESS,
        confidence=0.9,
        result="Advice",
        next_action=NextAction.PROCEED
    )

    state = wf.run_pipeline("Cloth & Saree Store")
    
    assert state.status == "SUCCESS" or state.status == "PARTIAL"
    assert state.viability_report.recommendation == "Insufficient Data"
    print("Success: Pipeline did not crash on missing location and returned valid ViabilityReport.")

if __name__ == "__main__":
    try:
        test_missing_location_no_crash()
        print("All tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        exit(1)
