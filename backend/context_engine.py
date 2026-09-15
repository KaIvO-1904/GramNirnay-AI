from typing import Dict, Any
from .intelligence.client import ai_client
from .structured_output import StructuredOutputHandler
from .ontology.models import MarketProxyResult
from .logger import logger
import json
import os
try:
    from .config import settings
    from .logger import logger
except (ImportError, ValueError):
    from config import settings
    from logger import logger

class ContextEngine:
    """
    Engine for providing hyper-local business context and market proxies.
    Combines static scenario data with AI-generated estimates for new locations.
    """

    def __init__(self):
        self.client = ai_client.client
        self.model = ai_client.model

        # Load demo scenarios for fallback/demo mode
        try:
            # Use settings for data directory
            scenario_path = os.path.join(settings.data_dir, "demo_scenarios.json")
            with open(scenario_path, "r") as f:
                self.demo_scenarios = json.load(f)
        except Exception as e:
            logger.error(f"Could not load demo_scenarios.json: {e}")
            self.demo_scenarios = {}

    def get_market_proxies(self, profile: Dict[str, Any], business_idea: str) -> Dict[str, Any]:
        """
        Provides market proxies (demand, competition, etc.) based on profile and business idea.
        """
        # 1. Check if this is a known demo scenario (e.g. based on location and idea)
        district = profile.get("location", {}).get("district", "").lower()
        for scenario_id, scenario in self.demo_scenarios.items():
            if scenario["profile"]["location"]["district"].lower() == district:
                return {
                    "demand": scenario["market_proxies"]["demand"],
                    "competition": scenario["market_proxies"]["competition"],
                    "accessibility": scenario["market_proxies"]["accessibility"],
                    "seasonality": scenario["market_proxies"].get("seasonality", 50),
                    "source": scenario["market_proxies"]["source"],
                    "confidence": "High (Verified Demo Scenario)"
                }

        # 2. Fallback: AI-generated proxies
        return self._generate_ai_proxies(profile, business_idea)

    def _generate_ai_proxies(self, profile: Dict[str, Any], business_idea: str) -> Dict[str, Any]:
        """
        Uses LLM to generate realistic market proxies based on location and business type.
        """
        if not self.client:
            return self._get_safe_defaults()

        location = profile.get("location", {})
        district = location.get("district", "Rural India")
        state = location.get("state", "India")

        prompt = (
            f"You are a Hyper-Local Market Analyst for rural India. "
            f"The user wants to start a business: '{business_idea}' in {district}, {state}. \n\n"
            f"Provide realistic market proxies for this specific location and business type. "
            f"Return ONLY a JSON object with these keys: \n"
            f"- demand: (0-100, where 100 is extremely high demand)\n"
            f"- competition: (0-100, where 100 is saturated market)\n"
            f"- accessibility: (0-100, based on logistics and infrastructure in that region)\n"
            f"- seasonality: (0-100, where 100 means highly seasonal)\n"
            f"- reasoning: (One sentence explaining why these scores were given)\n"
        )

        def call_llm():
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "You are a regional market intelligence expert. Return only JSON."},
                          {"role": "user", "content": prompt}],
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
            schema=MarketProxyResult,
            operation_name="market_proxy_generation",
            model_name=self.model,
            retry_fn=retry_llm
        )

        if res:
            res_dict = res.model_dump()
            return {
                "demand": res_dict.get("demand", 50),
                "competition": res_dict.get("competition", 50),
                "accessibility": res_dict.get("accessibility", 50),
                "seasonality": res_dict.get("seasonality", 50),
                "source": f"AI-derived proxy based on {district} regional benchmarks",
                "confidence": "Medium (AI Estimate)",
                "reasoning": res_dict.get("reasoning", "")
            }

        return self._get_safe_defaults()

    def _get_safe_defaults(self) -> Dict[str, Any]:
        return {
            "demand": 50,
            "competition": 50,
            "accessibility": 50,
            "seasonality": 50,
            "source": "Generic regional defaults",
            "confidence": "Low (Fallback)",
            "reasoning": "Using generic defaults due to system failure."
        }
