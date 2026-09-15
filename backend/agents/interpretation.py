import json
from ..intelligence.client import ai_client
from .base import BaseAgent
from ..ontology.models import AgentResponse, BusinessProfile, FinancialParams
from ..config import settings
from ..interpreter import BusinessInterpreter

class InterpretationAgent(BaseAgent):
    """Agent that transforms natural language into structured business models."""

    def __init__(self):
        super().__init__(name="InterpretationAgent", model_name=settings.llm_model)
        self.client = ai_client.client
        self.interpreter = BusinessInterpreter()

    def execute(self, user_input: str, **kwargs) -> AgentResponse:
        # 1. First, use the LLM to extract the profile and basic intents
        prompt = (
            "You are a Professional Business Analyst. Your task is to transform natural language "
            "descriptions of business ideas into a structured business model.\n\n"
            f"USER INPUT: '{user_input}'\n\n"
            "CRITICAL GUIDELINES:\n"
            "1. BENCHMARKING: If the user does not provide specific numerical values for capital, revenue, or expenses, provide realistic, benchmarked estimates based on the business category and location. Do NOT simply return 0.0 unless the business is fundamentally non-viable.\n"
            "2. CATEGORIZATION: Map the business to the most appropriate category (agriculture, livestock, "
            "handicrafts, services, trading, other).\n"
            "3. OUTPUT FORMAT: Return ONLY a JSON object with two keys: 'profile' and 'financials'.\n\n"
            "STRUCTURE:\n"
            "- profile: { business_idea, category, available_capital, location, experience_years, target_audience }\n"
            "- financials: { setup_cost, monthly_revenue, monthly_expenses, interest_rate, tenure_years, user_capital }\n\n"
            "EXAMPLE:\n"
            "Input: 'I want to start a small organic poultry farm in Mysore with 2 lakhs.'\n"
            "Output: {\"profile\": {\"business_idea\": \"organic poultry farm\", \"category\": \"poultry\", \"available_capital\": 200000, \"location\": \"Mysore\", \"experience_years\": 0, \"target_audience\": \"local markets\"}, \"financials\": {\"setup_cost\": 0.0, \"monthly_revenue\": 0.0, \"monthly_expenses\": 0.0, \"interest_rate\": 0.0, \"tenure_years\": 0, \"user_capital\": 200000}}"
        )

        def call_llm():
            resp = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return resp.choices[0].message.content

        def retry_llm(failed_output):
            retry_prompt = (
                f"The previous JSON output was malformed. Please fix the JSON escaping and return ONLY the corrected JSON object. "
                f"MALFORMED OUTPUT: {failed_output}"
            )
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": retry_prompt}],
                response_format={"type": "json_object"}
            )
            return resp.choices[0].message.content

        # Using a generic Dict schema since InterpretationAgent returns a custom merged structure
        from pydantic import BaseModel
        class InterpretationSchema(BaseModel):
            profile: Dict[str, Any]
            financials: Dict[str, Any]

        data = StructuredOutputHandler.execute_with_retry(
            llm_call_fn=call_llm,
            schema=InterpretationSchema,
            operation_name="initial_interpretation",
            model_name=self.model_name,
            retry_fn=retry_llm
        )

        if not data:
            return self.wrap_response(
                content=f"Failed to interpret input: JSON validation failed after retries.",
                score=0.0,
                reason="Parsing error"
            )

        # 2. Use the domain-specific BusinessInterpreter to enrich the result with deterministic calculations
        profile_data = data.profile
        # Extract location as a dict for the interpreter
        location = {
            "district": profile_data.get("location", "Rural District"),
            "state": "India"
        }

        # Enrich with deterministic calculations (Poultry, Dairy, etc.)
        enriched_data = self.interpreter.interpret_from_answers(
            idea=profile_data.get("business_idea", ""),
            location=location,
            experience_years=profile_data.get("experience_years", 0),
            answers={} # In a full flow, these would come from the questionnaire
        )

        # Merge the profile and the enriched financials/blueprints
        final_structured_data = {
            "profile": BusinessProfile(**profile_data),
            "financials": enriched_data # The interpreter returns the full dictionary including blueprint, etc.
        }

        return self.wrap_response(
            content="Successfully interpreted and enriched the business requirements.",
            structured_data=final_structured_data,
            score=0.9,
            reason="LLM extracted profile and domain-engine enriched the financial model."
        )
