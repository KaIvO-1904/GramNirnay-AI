import json
from openai import OpenAI
from .base import BaseAgent
from ..ontology.models import AgentResponse, BusinessProfile, FinancialResult, IntelligenceResult
from ..config import settings

class ExplanationAgent(BaseAgent):
    """Agent that transforms structured results into empathetic, personalized advice."""

    def __init__(self):
        super().__init__(model_name=settings.llm_model)
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )

    def execute(self, context: dict, **kwargs) -> AgentResponse:
        profile = context.get("profile")
        financials = context.get("financials")
        intelligence = context.get("intelligence")

        prompt = (
            f"You are a supportive Rural Entrepreneurship Advisor. Based on the following data:\n"
            f"User Profile: {profile}\n"
            f"Financial Projections: {financials}\n"
            f"Recommended Schemes: {intelligence}\n\n"
            "Provide a personalized, empathetic, and encouraging recommendation. "
            "Explain the financial viability simply and guide them on how to apply for the schemes. "
            "Keep it professional yet accessible for a rural entrepreneur."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content

            return self.wrap_response(
                content=content,
                score=0.9,
                reason="Generated comprehensive explanation based on provided context."
            )
        except Exception as e:
            return self.wrap_response(
                content=f"I encountered an error while preparing your advice: {str(e)}",
                score=0.0,
                reason="API error"
            )
