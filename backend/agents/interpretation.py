import json
from openai import OpenAI
from .base import BaseAgent
from ..ontology.models import AgentResponse, BusinessProfile, FinancialParams
from ..config import settings
from ..interpreter import BusinessInterpreter

class InterpretationAgent(BaseAgent):
    """Agent that transforms natural language into structured business models."""

    def __init__(self):
        super().__init__(name="InterpretationAgent", model_name=settings.llm_model)

        # Use Groq if available, otherwise OpenAI
        api_key = settings.groq_api_key or settings.openai_api_key
        base_url = "https://api.groq.com/openai/v1" if settings.groq_api_key else settings.openai_base_url

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.interpreter = BusinessInterpreter()

    def execute(self, user_input: str, **kwargs) -> AgentResponse:
        # 1. First, use the LLM to extract the profile and basic intents
        prompt = (
            "You are a Professional Business Analyst. Your task is to transform natural language "
            "descriptions of business ideas into a structured business model.\n\n"
            f"USER INPUT: '{user_input}'\n\n"
            "CRITICAL GUIDELINES:\n"
            "1. ZERO FABRICATION: Use 0.0 for unknown numerical values. Do NOT guess or estimate capital/revenue "
            "unless the user explicitly provides them. If a field is missing, set it to null or 0.0.\n"
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

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)

            # 2. Use the domain-specific BusinessInterpreter to enrich the result with deterministic calculations
            profile_data = data.get("profile", {})
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
        except Exception as e:
            return self.wrap_response(
                content=f"Failed to interpret input: {str(e)}",
                score=0.0,
                reason="Parsing error"
            )
