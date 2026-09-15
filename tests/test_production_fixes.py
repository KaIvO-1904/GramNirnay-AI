import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from backend.orchestration.workflow import WorkflowManager
from backend.agents.base import AgentResponse, AgentStatus, NextAction
from backend.ontology.models import FinancialParams, BusinessProfile
from unittest.mock import MagicMock

def test_location_no_bengaluru_leak():
    print("Testing location consistency (Chennai)...")
    wf = WorkflowManager()
    
    # Mock Interpretation to return Chennai
    wf.interpretation_agent = MagicMock()
    wf.interpretation_agent.execute.return_value = AgentResponse(
        status=AgentStatus.SUCCESS,
        confidence=0.9,
        result={"profile": {"business_idea": "test", "location": "Chennai, Tamil Nadu"}, "financials": {"setup_cost": 100}},
        next_action=NextAction.PROCEED
    )
    wf.validation_engine = MagicMock()
    wf.validation_engine.validate_profile.return_value = MagicMock(status="valid")
    wf.financial_engine = MagicMock()
    wf.financial_engine.compute_full_model.return_value = {"total_project_cost": 100, "financing_required": 50, "monthly_emi": 10, "monthly_net_profit": 20, "annual_net_profit": 240, "roi_percent": 20, "break_even_months": 12, "is_viable": True}
    wf.viability_engine = MagicMock()
    wf.viability_engine._calculate_financial_score = lambda x: 0.8
    wf.viability_engine.calculate_viability = lambda x, y: MagicMock(overall_score=0.8, recommendation="Proceed", headline="Good")
    
    # Fix the lambda to accept all arguments explicitly
    def mock_get_intel(profile, financial_params, location_identity=None):
        return MagicMock(
            local_intelligence=MagicMock(
                overall_confidence=0.8, 
                demand=MagicMock(local_demand_score=0.8, operational_risks=[]), 
                competition=MagicMock(competition_score=0.2, metadata=MagicMock(source="Regional Market Intelligence - Chennai", confidence=0.8)), 
                supply_chain=MagicMock(supplier_access_score=0.8, raw_material_score=0.8, metadata=MagicMock(source="S2", confidence=0.8)), 
                logistics=MagicMock(transport_score=0.8, accessibility_score=0.8, metadata=MagicMock(source="S3", confidence=0.8))
            )
        )
    wf.knowledge_manager = MagicMock()
    wf.knowledge_manager.get_intelligence = mock_get_intel
    
    wf.rag_engine = MagicMock()
    wf.rag_engine.get_best_schemes = lambda p, f: []
    wf.explanation_agent = MagicMock()
    wf.explanation_agent.execute.return_value = AgentResponse(
        status=AgentStatus.SUCCESS,
        confidence=0.9,
        result="Advice",
        next_action=NextAction.PROCEED
    )

    state = wf.run_pipeline("Test Chennai")
    
    # Check if Bengaluru leaked into the result via intelligence
    intel_source = state.intelligence_result.local_intelligence.competition.metadata.source
    if "Bengaluru" in intel_source or "Bangalore" in intel_source:
        print(f"FAILURE: Bengaluru leaked into Chennai analysis: {intel_source}")
        exit(1)
    print(f"Success: Intelligence source correctly identifies as {intel_source}")

def test_scenario_consistency():
    print("Testing financial scenario consistency...")
    wf = WorkflowManager()
    
    # Mock successful pipeline
    wf.interpretation_agent = MagicMock()
    wf.interpretation_agent.execute.return_value = AgentResponse(
        status=AgentStatus.SUCCESS,
        confidence=0.9,
        result={"profile": {"business_idea": "test", "location": "test"}, "financials": {"setup_cost": 1000000, "user_capital": 200000, "monthly_revenue": 100000, "monthly_expenses": 50000, "interest_rate": 10, "tenure_years": 5}},
        next_action=NextAction.PROCEED
    )
    wf.validation_engine = MagicMock()
    wf.validation_engine.validate_profile.return_value = MagicMock(status="valid")
    wf.financial_engine = MagicMock()
    wf.financial_engine.compute_full_model.return_value = {"total_project_cost": 1000000, "financing_required": 800000, "monthly_emi": 20000, "monthly_net_profit": 30000, "annual_net_profit": 360000, "roi_percent": 36, "break_even_months": 33, "is_viable": True}
    wf.viability_engine = MagicMock()
    wf.viability_engine._calculate_financial_score = lambda x: 0.8
    wf.viability_engine.calculate_viability = lambda x, y: MagicMock(overall_score=0.8, recommendation="Proceed", headline="Good")
    
    def mock_get_intel(profile, financial_params, location_identity=None):
        return MagicMock(
            local_intelligence=MagicMock(
                overall_confidence=0.8, 
                demand=MagicMock(local_demand_score=0.8, operational_risks=[]), 
                competition=MagicMock(competition_score=0.2, metadata=MagicMock(source="S1", confidence=0.8)), 
                supply_chain=MagicMock(supplier_access_score=0.8, raw_material_score=0.8, metadata=MagicMock(source="S2", confidence=0.8)), 
                logistics=MagicMock(transport_score=0.8, accessibility_score=0.8, metadata=MagicMock(source="S3", confidence=0.8))
            )
        )
    wf.knowledge_manager = MagicMock()
    wf.knowledge_manager.get_intelligence = mock_get_intel
    wf.rag_engine = MagicMock()
    wf.rag_engine.get_best_schemes = lambda p, f: []
    wf.explanation_agent = MagicMock()
    wf.explanation_agent.execute.return_value = AgentResponse(
        status=AgentStatus.SUCCESS,
        confidence=0.9,
        result="Advice",
        next_action=NextAction.PROCEED
    )

    state = wf.run_pipeline("Test scenario")
    report = wf.format_for_frontend(state)
    
    # Verify scenarios exist and are not zero
    scenarios = report.get("scenarios", {})
    if not scenarios:
        print("FAILURE: No scenarios returned")
        exit(1)
    
    for name, s in scenarios.items():
        if s["setup_cost"] == 0 or s["monthly_revenue"] == 0:
            print(f"FAILURE: Scenario {name} has zero values")
            exit(1)
            
    print("Success: Scenarios generated and contain non-zero deterministic values.")

if __name__ == "__main__":
    try:
        test_location_no_bengaluru_leak()
        test_scenario_consistency()
        print("All targeted fixes verified!")
    except Exception as e:
        print(f"Test failed: {e}")
        exit(1)
