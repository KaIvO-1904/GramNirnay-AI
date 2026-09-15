from typing import List, Dict, Any
from .intelligence.client import ai_client
from .structured_output import StructuredOutputHandler
from .ontology.models import Scheme, SchemeRankResult, SchemeEnrichmentResult
import os
import json
try:
    from .config import settings
    from .logger import logger
    from .core.schemas.domain import Scheme
except (ImportError, ValueError):
    from config import settings
    from logger import logger
    from core.schemas.domain import Scheme

class RAGEngine:
    """
    Hybrid RAG engine for government scheme matching.
    Combines deterministic filtering with AI-based semantic ranking.
    Supports any OpenAI-compatible provider (OpenRouter, Groq, Ollama, etc.)
    """

    def __init__(self):
        # Load configuration from settings
        self.client = ai_client.client
        self.model = ai_client.model

        try:
            # Use settings for data directory
            scheme_path = os.path.join(settings.data_dir, "schemes.json")
            with open(scheme_path, "r") as f:
                self.schemes = json.load(f)
        except FileNotFoundError:
            logger.error("schemes.json not found. Checking relative paths...")
            try:
                with open("data/schemes.json", "r") as f:
                    self.schemes = json.load(f)
            except Exception as e:
                logger.critical(f"Could not find schemes.json: {e}")
                self.schemes = []

    def filter_eligible_schemes(self, capital_required: float, category: str) -> List[Dict]:
        """
        Step 1: Deterministic Filtering.
        Returns schemes where the user fits the capital and category criteria.
        """
        eligible = []
        for scheme in self.schemes:
            elig = scheme["eligibility"]

            # Check capital range - More permissive for MVP
            capital_match = False
            if capital_required <= 0:
                if capital_required <= elig["maxCapital"]:
                    capital_match = True
            elif elig["minCapital"] <= capital_required <= elig["maxCapital"]:
                capital_match = True

            if capital_match:
                # Check category match (broad match)
                if any(cat.lower() in category.lower() for cat in elig["categories"]):
                    eligible.append(scheme)
        return eligible

    def rank_schemes_with_ai(self, business_description: str, eligible_schemes: List[Dict]) -> List[Dict]:
        """
        Step 2: Semantic Ranking.
        Uses LLM to rank filtered schemes based on specific business needs.
        """
        if not eligible_schemes:
            return eligible_schemes

        # Construct a condensed list of schemes for the prompt
        schemes_context = "\n".join([
            f"ID: {s['schemeId']} | Name: {s['name']} | Benefit: {s['benefit']}"
            for s in eligible_schemes
        ])

        prompt = (
            f"You are a Government Scheme Expert. Given the following business description: '{business_description}', "
            f"rank the following eligible schemes by relevance. Return ONLY a JSON object with a key 'ranked_ids' "
            f"containing a list of IDs in order of relevance.\n\n"
            f"Schemes:\n{schemes_context}"
        )

        def call_llm():
            resp = self.client.chat.completions.create(
                model=self.model,
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

        res = StructuredOutputHandler.execute_with_retry(
            llm_call_fn=call_llm,
            schema=SchemeRankResult,
            operation_name="rank_schemes",
            model_name=self.model,
            retry_fn=retry_llm
        )

        if res:
            ranked_ids = res.ranked_ids
            ordered_schemes = []
            for rid in ranked_ids:
                scheme = next((s for s in eligible_schemes if s["schemeId"] == rid), None)
                if scheme:
                    ordered_schemes.append(scheme)
            return ordered_schemes if ordered_schemes else eligible_schemes

        return eligible_schemes

    def enrich_scheme_details(self, scheme: Dict, business_description: str) -> Dict:
        """
        Uses LLM to turn scheme metadata into a customized application guide.
        Adheres to Zero Fabrication: only interprets provided data.
        """
        if not self.client:
            return scheme

        prompt = (
            f"You are a Govt Scheme Advisor. Based on this scheme metadata: {json.dumps(scheme)} "
            f"and the user's business: '{business_description}', "
            f"create a professional, step-by-step application guide. "
            f"Do NOT fabricate external links or deadlines. If info is missing, state 'Refer to official portal'. "
            f"Return ONLY a JSON object with keys 'application_steps' (list of strings) and 'detailed_eligibility' (string)."
        )

        def call_llm():
            resp = self.client.chat.completions.create(
                model=self.model,
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

        enrichment = StructuredOutputHandler.execute_with_retry(
            llm_call_fn=call_llm,
            schema=SchemeEnrichmentResult,
            operation_name="enrich_scheme",
            model_name=self.model,
            retry_fn=retry_llm
        )

        if enrichment:
            return {
                **scheme,
                "application_steps": enrichment.application_steps,
                "detailed_eligibility": enrichment.detailed_eligibility
            }

        return scheme

    def get_best_schemes(self, profile: Dict[str, Any], financial_params: Dict[str, Any]) -> List[Scheme]:
        """
        Main entry point for scheme matching with enrichment.
        """
        gap = financial_params.get("setup_cost", 0) - profile.get("availableCapital", 0)
        category = profile.get("businessIdea", "general")

        eligible = self.filter_eligible_schemes(gap, category)
        ranked = self.rank_schemes_with_ai(category, eligible)
        top_schemes = ranked[:3]
        enriched_schemes = []
        for s in top_schemes:
            enriched_schemes.append(self.enrich_scheme_details(s, category))

        final_list = enriched_schemes + ranked[3:]
        return [Scheme(**s) for s in final_list]
