import json
from openai import OpenAI
from .base import BaseAgent
from ..ontology.models import AgentResponse, BusinessProfile, FinancialParams, BusinessCategory
from ..config import settings

class InterpretationAgent(BaseAgent):
    """Agent that transforms natural language into structured business models."""

    def __init__(self):
        super().__init__(name="InterpretationAgent", model_name=settings.llm_model)
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )

    def execute(self, user_input: str, **kwargs) -> AgentResponse:
        prompt = (
            f"Extract business details from the following input: '{user_input}'. "
            "Return ONLY a JSON object with two keys: 'profile' and 'financials'. "
            "Profile should have: business_idea, category (one of: agriculture, livestock, handicrafts, services, trading, other), "
            "available_capital, location, experience_years, target_audience. "
            "Financials should have: setup_cost, monthly_revenue, monthly_expenses, interest_rate, tenure_years, user_capital. "
            "Use 0.0 for unknown numerical values."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)

            # Convert to Pydantic models for validation
            profile = BusinessProfile(**data.get("profile", {}))
            financials = FinancialParams(**data.get("financials", {}))

            return self.wrap_response(
                content="Successfully interpreted the business requirements.",
                structured_data={"profile": profile, "financials": financials},
                score=0.9,
                reason="LLM successfully extracted all required fields."
            )
        except Exception as e:
            return self.wrap_response(
                content=f"Failed to interpret input: {str(e)}",
                score=0.0,
                reason="Parsing error"
            )
