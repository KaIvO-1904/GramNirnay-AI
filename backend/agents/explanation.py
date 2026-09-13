import json
from openai import OpenAI
from .base import BaseAgent
from ..ontology.models import AgentResponse, BusinessProfile, FinancialResult, IntelligenceResult
from ..config import settings

class ExplanationAgent(BaseAgent):
    """Agent that transforms structured results into empathetic, personalized advice."""

    def __init__(self):
        super().__init__(name="ExplanationAgent", model_name=settings.llm_model)

        # Use Groq if available, otherwise OpenAI
        api_key = settings.groq_api_key or settings.openai_api_key
        base_url = "https://api.groq.com/openai/v1" if settings.groq_api_key else settings.openai_base_url

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

    def execute(self, context: dict, **kwargs) -> AgentResponse:
        profile = context.get("profile")
        financials = context.get("financials")
        intelligence = context.get("intelligence")
        viability = context.get("viability")
        schemes = context.get("schemes")

        prompt = (
            "You are a supportive Rural Entrepreneurship Advisor. Your goal is to synthesize complex "
            "financial data into a personalized, encouraging, and actionable advice letter.\n\n"
            f"CONTEXT:\n"
            f"- User Profile: {profile}\n"
            f"- Financial Projections: {financials}\n"
            f"- Viability Report: {viability}\n"
            f"- Matched Schemes: {schemes}\n\n"
            "STRUCTURE YOUR RESPONSE AS FOLLOWS:\n"
            "1. VIABILITY VERDICT: Start with a clear, encouraging verdict on whether the business is viable.\n"
            "2. FINANCIAL ROADMAP: Explain the ROI, Break-even, and Monthly Profit in simple terms. "
            "If the numbers are risky, explain why gently and suggest pivots.\n"
            "3. GOVT SUPPORT GUIDE: Highlight the best matched schemes. Explain exactly how they help "
            "(e.g., 'This subsidy reduces your initial cost by X%').\n"
            "4. FINAL ACTION STEP: Provide one clear, immediate next step for the user.\n\n"
            "CONSTRAINTS:\n"
            "- ZERO FABRICATION: Only mention schemes and benefits present in the context.\n"
            "- TONE: Empathetic, professional, and accessible for a rural entrepreneur.\n"
            "- LANGUAGE: Use clear, jargon-free English."
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
