import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from backend.orchestration.workflow import WorkflowManager
from backend.agents.base import AgentResponse, AgentStatus, NextAction
from backend.ontology.models import FinancialParams, BusinessProfile
from pydantic import BaseModel
from unittest.mock import MagicMock

def test_explanation_stage_success():
    print("Testing explanation stage success...")
    wf = WorkflowManager()
    
    # Mock successful dependencies
    wf.interpretation_agent = MagicMock()
    wf.interpretation_agent.execute.return_value = AgentResponse(
        status=AgentStatus.SUCCESS,
        confidence=0.9,
        result={"profile": {"business_idea": "test", "location": "test"}, "financials": {"setup_cost": 100}},
        next_action=NextAction.PROCEED
    )
    
    wf.validation_engine = MagicMock()
    wf.validation_engine.validate_profile.return_value = MagicMock(status="valid")
    
    wf.financial_engine = MagicMock()
    wf.financial_engine.compute_full_model.return_value = {"total_project_cost": 100, "financing_required": 50, "monthly_emi": 10, "monthly_net_profit": 20, "annual_net_profit": 240, "roi_percent": 20, "break_even_months": 12, "is_viable": True}
    
    wf.viability_engine = MagicMock()
    wf.viability_engine._calculate_financial_score = lambda x: 0.8
    wf.viability_engine.calculate_viability = lambda x, y: MagicMock(overall_score=0.8, recommendation="Proceed", headline="Good")
    
    wf.knowledge_manager = MagicMock()
    # Fix the lambda to accept all arguments
    wf.knowledge_manager.get_intelligence = lambda p, f, location_identity=None: MagicMock(
        local_intelligence=MagicMock(
            overall_confidence=0.8, 
            demand=MagicMock(local_demand_score=0.8, operational_risks=[]), 
            competition=MagicMock(competition_score=0.2, metadata=MagicMock(source="S1", confidence=0.8)), 
            supply_chain=MagicMock(supplier_access_score=0.8, raw_material_score=0.8, metadata=MagicMock(source="S2", confidence=0.8)), 
            logistics=MagicMock(transport_score=0.8, accessibility_score=0.8, metadata=MagicMock(source="S3", confidence=0.8))
        )
    )
    
    wf.rag_engine = MagicMock()
    wf.rag_engine.get_best_schemes = lambda p, f: []
    
    # Mock ExplanationAgent to return an AgentResponse with evidence but no result
    wf.explanation_agent = MagicMock()
    wf.explanation_agent.execute.return_value = AgentResponse(
        status=AgentStatus.SUCCESS,
        confidence=0.9,
        result=None,
        evidence=["This is a great business idea!"],
        next_action=NextAction.PROCEED
    )
    
    state = wf.run_pipeline("Test idea")
    
    assert state.status == "SUCCESS"
    assert state.final_explanation == "This is a great business idea!"
    print("Success: Final explanation correctly retrieved from evidence.")

def test_explanation_stage_failure_partial():
    print("Testing explanation stage failure (PARTIAL)...")
    wf = WorkflowManager()
    
    # Mock successful dependencies
    wf.interpretation_agent = MagicMock()
    wf.interpretation_agent.execute.return_value = AgentResponse(
        status=AgentStatus.SUCCESS,
        confidence=0.9,
        result={"profile": {"business_idea": "test", "location": "test"}, "financials": {"setup_cost": 100}},
        next_action=NextAction.PROCEED
    )
    wf.validation_engine = MagicMock()
    wf.validation_engine.validate_profile.return_value = MagicMock(status="valid")
    wf.financial_engine = MagicMock()
    wf.financial_engine.compute_full_model.return_value = {"total_project_cost": 100, "financing_required": 50, "monthly_emi": 10, "monthly_net_profit": 20, "annual_net_profit": 240, "roi_percent": 20, "break_even_months": 12, "is_viable": True}
    wf.viability_engine = MagicMock()
    wf.viability_engine._calculate_financial_score = lambda x: 0.8
    wf.viability_engine.calculate_viability = lambda x, y: MagicMock(overall_score=0.8, recommendation="Proceed", headline="Good")
    wf.knowledge_manager = MagicMock()
    wf.knowledge_manager.get_intelligence = lambda p, f, location_identity=None: MagicMock(
        local_intelligence=MagicMock(
            overall_confidence=0.8, 
            demand=MagicMock(local_demand_score=0.8, operational_risks=[]), 
            competition=MagicMock(competition_score=0.2, metadata=MagicMock(source="S1", confidence=0.8)), 
            supply_chain=MagicMock(supplier_access_score=0.8, raw_material_score=0.8, metadata=MagicMock(source="S2", confidence=0.8)), 
            logistics=MagicMock(transport_score=0.8, accessibility_score=0.8, metadata=MagicMock(source="S3", confidence=0.8))
        )
    )
    wf.rag_engine = MagicMock()
    wf.rag_engine.get_best_schemes = lambda p, f: []
    
    # Mock ExplanationAgent to throw an exception
    wf.explanation_agent = MagicMock()
    wf.explanation_agent.execute.side_effect = Exception("LLM Timeout")
    
    state = wf.run_pipeline("Test idea")
    
    assert state.status == "PARTIAL"
    assert "Analysis completed, but the personalized advice letter could not be generated" in state.final_explanation
    assert state.financial_result is not None
    print("Success: Pipeline returned PARTIAL status and preserved financials.")

if __name__ == "__main__":
    try:
        test_explanation_stage_success()
        test_explanation_stage_failure_partial()
        print("All tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        exit(1)
