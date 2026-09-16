import uuid
import re
from typing import Optional, Any, Dict
from .state import PipelineState
from ..logger import logger
from ..ontology.models import (
    InterpretationError,
    ValidationError,
    CalculationError,
    GramNirnayError
)
from ..agents.interpretation import InterpretationAgent
from ..agents.explanation import ExplanationAgent
from ..validation.rules_engine import ValidationEngine
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
        self.viability_engine = ViabilityEngine()
        self.knowledge_manager = KnowledgeManager()
        self.financial_engine = FinancialEngine()
        self.rag_engine = RAGEngine()
        from ..operational_engine import OperationalEngine
        self.operational_engine = OperationalEngine()

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
                if interp_res.confidence < 0.3:
                    raise InterpretationError("Could not understand the business request.", "INTERP_FAILED")

                data = interp_res.result
                state.profile = data["profile"]
                state.financial_params = data["financials"]
                state.interpretation_confidence = interp_res.confidence

            # 2. VALIDATION
            val_res = self.validation_engine.validate_profile(state.profile)
            if val_res.status == "invalid":
                raise ValidationError(f"Profile validation failed: {', '.join(val_res.errors)}", "VAL_FAILED")
            state.validation_result = val_res

            # 3. CALCULATION
            params_dict = state.financial_params.model_dump() if hasattr(state.financial_params, "model_dump") else state.financial_params
            fin_data = self.financial_engine.compute_full_model(params_dict)
            from ..ontology.models import FinancialResult
            state.financial_result = FinancialResult(**fin_data)
            state.viability_score = self.viability_engine._calculate_financial_score(state.financial_result)

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
            try:
                context = {
                    "profile": state.profile,
                    "financials": state.financial_result,
                    "intelligence": state.intelligence_result,
                    "viability": state.viability_report,
                    "schemes": state.matched_schemes,
                    "location": state.location_identity
                }
                expl_res = self.explanation_agent.execute(context)
                state.final_explanation = expl_res.result if expl_res.result else " ".join(expl_res.evidence)
                state.status = "SUCCESS"
            except Exception as e:
                logger.error(f"Explanation generation failed: {e}")
                state.final_explanation = "Analysis completed, but the personalized advice letter could not be generated."
                state.status = "PARTIAL"

            return state

        except GramNirnayError as e:
            logger.warning(f"Pipeline halted by business rule: {e.message} (Code: {e.code})")
            state.status = "FAILED"
            state.final_explanation = f"I encountered an issue: {e.message}"
            return state
        except Exception as e:
            logger.exception(f"Unexpected pipeline failure: {e}")
            state.status = "FAILED"
            state.final_explanation = f"A technical error occurred while processing your analysis. Please try again."
            return state

    def _clean_markdown(self, text: str) -> str:
        """Removes common Markdown formatting markers for a cleaner plain-text display."""
        if not text:
            return ""
        # Remove bold/italic markers: **, __, *, _
        text = re.sub(r'(\*\*|__)', '', text)
        text = re.sub(r'(\*|_)', '', text)
        # Remove hashtag headers: #
        text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
        return text.strip()

    def format_for_frontend(self, state: PipelineState) -> Dict[str, Any]:
        """Converts PipelineState to the AnalysisResult structure expected by the frontend."""

        # 0. Deterministic Operational Data (Always available based on category)
        category = getattr(state.profile, 'category', 'other')
        blueprint = self.operational_engine.get_blueprint(category)
        roadmap = self.operational_engine.get_roadmap(category)
        requirements = self.operational_engine.get_requirements(category)
        risks = self.operational_engine.get_risks(category)

        # 1. Determine Status
        status = "SUCCESS"
        if not state.financial_result:
            status = "FAILED"
        elif not state.intelligence_result or not state.viability_report:
            status = "PARTIAL"

        if status == "FAILED":
            return {
                "status": "FAILED",
                "error": "ANALYSIS_FAILED",
                "message": state.final_explanation or "A critical error occurred during financial calculation.",
                "viabilityScore": 0,
                "recommendation": "Analysis Incomplete",
                "marketAnalysis": {
                    "demand": None, "competition": None, "accessibility": None, "seasonality": None,
                    "source": "Unavailable", "confidence": "None", "reasoning": "Financial engine failed."
                },
                "financials": state.financial_result.model_dump() if state.financial_result else {},
                "interpreter_reasoning": self._clean_markdown(state.final_explanation),
                "modifications": [],
                "matchedSchemes": [],
                "business_blueprint": blueprint,
                "startup_roadmap": roadmap,
                "regulatory_requirements": requirements,
                "risk_matrix": risks,
                "is_demo": state.metadata.get("is_demo", False)
            }

        # 2. Canonical Viability Score
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
                "status": "PARTIAL",
                "error": "INTELLIGENCE_MISSING",
                "message": "Market intelligence data was not generated.",
                "viabilityScore": int(score),
                "recommendation": recommendation,
                "marketAnalysis": {
                    "demand": None, "competition": None, "accessibility": None, "seasonality": None,
                    "source": "Unavailable", "confidence": "None", "reasoning": "Intelligence result was empty."
                },
                "financials": state.financial_result.model_dump() if state.financial_result else {},
                "interpreter_reasoning": self._clean_markdown(state.final_explanation),
                "modifications": [],
                "matchedSchemes": [],
                "business_blueprint": blueprint,
                "startup_roadmap": roadmap,
                "regulatory_requirements": requirements,
                "risk_matrix": risks,
                "is_demo": state.metadata.get("is_demo", False)
            }

        conf_val = intel.overall_confidence if hasattr(intel, 'overall_confidence') else 0.6
        conf_label = "Low"
        if conf_val >= 0.9: conf_label = "High"
        elif conf_val >= 0.7: conf_label = "Medium"

        # 3. Deterministic Scenarios
        params_dict = state.financial_params.model_dump() if hasattr(state.financial_params, 'model_dump') else (state.financial_params if isinstance(state.financial_params, dict) else {})
        scenario_engine = FinancialEngine()
        scenarios_raw = scenario_engine.calculate_scenarios(params_dict)
        scenarios = {name: res.__dict__ for name, res in scenarios_raw.items()}

        return {
            "status": status,
            "viabilityScore": int(score),
            "recommendation": recommendation,
            "headline": state.viability_report.headline if hasattr(state, 'viability_report') and state.viability_report else "Evaluating venture viability...",
            "location": state.location_identity,
            "marketAnalysis": {
                "demand": round(intel.demand.local_demand_score * 100) if hasattr(intel.demand, 'local_demand_score') else None,
                "competition": round(intel.competition.competition_score * 100) if hasattr(intel.competition, 'competition_score') else None,
                "accessibility": round(((intel.logistics.transport_score + intel.logistics.accessibility_score) / 2) * 100) if hasattr(intel.logistics, 'transport_score') else None,
                "seasonality": round(intel.demand.seasonality_index * 100) if hasattr(intel.demand, 'seasonality_index') else None,
                "source": ", ".join(state.viability_report.data_sources) if hasattr(state, 'viability_report') and state.viability_report else intel.demand.metadata.source,
                "confidence": conf_label,
                "reasoning": self._clean_markdown(state.final_explanation[:200]) + "..." if state.final_explanation else "",
            },
            "financials": state.financial_result.model_dump() if state.financial_result else {},
            "scenarios": scenarios,
            "interpreter_reasoning": state.final_explanation,
            "modifications": state.viability_report.negative_factors if hasattr(state, 'viability_report') and state.viability_report else [],
            "matchedSchemes": state.matched_schemes if hasattr(state, 'matched_schemes') and state.matched_schemes else [],
            "is_demo": state.metadata.get("is_demo", False),
            "business_blueprint": blueprint,
            "startup_roadmap": roadmap,
            "regulatory_requirements": requirements,
            "risk_matrix": risks,
            "provenance": {
                "generated_at": "Now", # In real implementation, use datetime.now().isoformat()
                "model_version": "GramNirnay-v2-Prod"
            }
        }
