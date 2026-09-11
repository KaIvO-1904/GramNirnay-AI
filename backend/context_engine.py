from typing import Dict, Any
from openai import OpenAI
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
        # Configuration from settings
        api_key = settings.openai_api_key
        base_url = settings.openai_base_url
        self.model = settings.llm_model

        if api_key:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = None
            logger.warning("OPENAI_API_KEY not found. AI proxy generation will be disabled.")

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

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            res = json.loads(response.choices[0].message.content)

            return {
                "demand": res.get("demand", 50),
                "competition": res.get("competition", 50),
                "accessibility": res.get("accessibility", 50),
                "seasonality": res.get("seasonality", 50),
                "source": f"AI-derived proxy based on {district} regional benchmarks",
                "confidence": "Medium (AI Estimate)",
                "reasoning": res.get("reasoning", "")
            }
        except Exception as e:
            logger.error(f"AI proxy generation failed: {e}. Using safe defaults.")
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
