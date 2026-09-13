import uuid
from typing import Optional, Any, Dict
from .state import PipelineState
from ..ontology.models import (
    InterpretationError,
    ValidationError,
    CalculationError,
    GramNirnayError
)
from ..agents.interpretation import InterpretationAgent
from ..agents.explanation import ExplanationAgent
from ..validation.rules_engine import ValidationEngine
from ..scoring.viability import ScoringEngine
from ..scoring.viability_engine import ViabilityEngine
from ..intelligence.knowledge import KnowledgeManager
from ..financial_engine import FinancialEngine
from ..rag_engine import RAGEngine

class WorkflowManager:
    """Orchestrates the GramNirnay.ai intelligence pipeline."""

    def __init__(self):
        self.interpretation_agent = InterpretationAgent()
        self.explanation_agent = ExplanationAgent()
        self.validation_engine = ValidationEngine()
        self.scoring_engine = ScoringEngine() # Keep for backward compatibility
        self.viability_engine = ViabilityEngine()
        self.knowledge_manager = KnowledgeManager()
        self.financial_engine = FinancialEngine()
        self.rag_engine = RAGEngine()

    def run_pipeline(self, user_input: str, profile: Optional[Any] = None, financial_params: Optional[Any] = None) -> PipelineState:
        state = PipelineState(request_id=str(uuid.uuid4()), user_input=user_input)

        try:
            # 1. INTERPRETATION
            if profile and financial_params:
                state.profile = profile
                state.financial_params = financial_params
                state.interpretation_confidence = 1.0
            else:
                interp_res = self.interpretation_agent.execute(user_input)
                if interp_res.confidence.score < 0.3:
                    raise InterpretationError("Could not understand the business request.", "INTERP_FAILED")

                data = interp_res.structured_data
                state.profile = data["profile"]
                state.financial_params = data["financials"]
                state.interpretation_confidence = interp_res.confidence.score

            # 2. VALIDATION
            val_res = self.validation_engine.validate_profile(state.profile)
            if val_res.status == "invalid":
                raise ValidationError(f"Profile validation failed: {', '.join(val_res.errors)}", "VAL_FAILED")
            state.validation_result = val_res

            # 3. CALCULATION
            fin_data = self.financial_engine.compute_full_model(state.financial_params.model_dump())
            from ..ontology.models import FinancialResult
            state.financial_result = FinancialResult(**fin_data)
            state.viability_score = self.scoring_engine.calculate_financial_viability(state.financial_result)

            # Resolve location if it's a string (for Local Intelligence)
            if hasattr(state.profile, "location") and isinstance(state.profile.location, str):
                try:
                    candidates = self.knowledge_manager.location_service.search_place(state.profile.location)
                    if candidates:
                        state.location_identity = self.knowledge_manager.location_service.resolve_location(
                            candidates[0].provider_id,
                            __import__('backend.location.models', fromlist=['LocationSource']).LocationSource.MANUAL
                        )
                    else:
                        state.location_identity = None
                except Exception:
                    state.location_identity = None
            else:
                state.location_identity = getattr(state.profile, "location", None)

            # 4. LOCAL INTELLIGENCE
            state.intelligence_result = self.knowledge_manager.get_intelligence(
                state.profile,
                state.financial_params,
                location_identity=state.location_identity
            )

            # 5. VIABILITY AGGREGATION
            state.viability_report = self.viability_engine.calculate_viability(
                state.financial_result,
                state.intelligence_result.local_intelligence if state.intelligence_result else None
            )

            # 6. SCHEMES MATCHING (RAG)
            state.matched_schemes = self.rag_engine.get_best_schemes(
                state.profile,
                state.financial_params
            )

            # 7. EXPLANATION
            context = {
                "profile": state.profile,
                "financials": state.financial_result,
                "intelligence": state.intelligence_result,
                "viability": state.viability_report,
                "schemes": state.matched_schemes
            }
            expl_res = self.explanation_agent.execute(context)
            state.final_explanation = expl_res.content

            return state

        except GramNirnayError as e:
            state.final_explanation = f"I encountered an issue: {e.message}"
            return state
        except Exception as e:
            state.final_explanation = f"An unexpected error occurred: {str(e)}"
            return state

    def format_for_frontend(self, state: PipelineState) -> Dict[str, Any]:
        """Converts PipelineState to the AnalysisResult structure expected by the frontend."""
        if not state.financial_result or not state.intelligence_result:
            return {
                "error": "ANALYSIS_FAILED",
                "message": state.final_explanation or "An unexpected error occurred during analysis.",
                "viabilityScore": 0,
                "recommendation": "Error",
                "marketAnalysis": {
                    "demand": 0, "competition": 0, "accessibility": 0, "seasonality": 0,
                    "source": "Unavailable", "confidence": "None", "reasoning": "Analysis failed to complete."
                },
                "financials": {},
                "interpreter_reasoning": state.final_explanation,
                "modifications": [],
                "matchedSchemes": [],
                "is_demo": state.metadata.get("is_demo", False)
            }

        raw_score = 0.0
        recommendation = "Reconsider"
        if hasattr(state, 'viability_report') and state.viability_report:
            raw_score = state.viability_report.overall_score
            recommendation = state.viability_report.recommendation
        elif hasattr(state, 'viability_score'):
            raw_score = state.viability_score
            score_pct = round(raw_score * 100, 0)
            if score_pct >= 80: recommendation = "Proceed"
            elif score_pct >= 50: recommendation = "Proceed with Modification"

        score = round(raw_score * 100, 0)
        intel = state.intelligence_result.local_intelligence if state.intelligence_result else None

        if not intel:
            return {
                "error": "INTELLIGENCE_MISSING",
                "message": "Market intelligence data was not generated.",
                "viabilityScore": 0,
                "recommendation": "Error",
                "marketAnalysis": {
                    "demand": 0, "competition": 0, "accessibility": 0, "seasonality": 0,
                    "source": "Unavailable", "confidence": "None", "reasoning": "Intelligence result was empty."
                },
                "financials": state.financial_result.model_dump() if state.financial_result else {},
                "interpreter_reasoning": state.final_explanation,
                "modifications": [],
                "matchedSchemes": [],
                "is_demo": state.metadata.get("is_demo", False)
            }

        conf_val = intel.overall_confidence if hasattr(intel, 'overall_confidence') else 0.6
        conf_label = "Low"
        if conf_val >= 0.9: conf_label = "High"
        elif conf_val >= 0.7: conf_label = "Medium"

        params = state.financial_params.model_dump() if hasattr(state.financial_params, 'model_dump') else (state.financial_params if isinstance(state.financial_params, dict) else {})

        return {
            "viabilityScore": int(score),
            "recommendation": recommendation,
            "headline": state.viability_report.headline if hasattr(state, 'viability_report') and state.viability_report else "Evaluating venture viability...",
            "marketAnalysis": {
                "demand": round(intel.demand.local_demand_score * 100),
                "competition": round(intel.competition.competition_score * 100),
                "accessibility": round(((intel.logistics.transport_score + intel.logistics.accessibility_score) / 2) * 100),
                "seasonality": round(intel.demand.seasonality_index * 100),
                "source": ", ".join(state.viability_report.data_sources) if hasattr(state, 'viability_report') and state.viability_report else intel.demand.metadata.source,
                "confidence": conf_label,
                "reasoning": state.final_explanation[:200] + "..." if state.final_explanation else ""
            },
            "financials": state.financial_result.model_dump() if state.financial_result else {},
            "interpreter_reasoning": state.final_explanation,
            "modifications": state.viability_report.negative_factors if hasattr(state, 'viability_report') and state.viability_report else [],
            "matchedSchemes": state.matched_schemes if hasattr(state, 'matched_schemes') and state.matched_schemes else [],
            "is_demo": state.metadata.get("is_demo", False),
            "business_blueprint": params.get("business_blueprint") or {"flow": [], "inputs": [], "outputs": []},
            "startup_roadmap": params.get("startup_roadmap") or [],
            "regulatory_requirements": params.get("regulatory_requirements") or [],
            "risk_matrix": params.get("risk_matrix") or []
        }
