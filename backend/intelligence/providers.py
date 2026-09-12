from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..location.models import LocationIdentity
from .models import (
    CompetitionAnalysis,
    SupplyChainAnalysis,
    LogisticsAnalysis,
    LocalDemandAnalysis
)

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..location.models import LocationIdentity
from .models import (
    CompetitionAnalysis,
    SupplyChainAnalysis,
    LogisticsAnalysis,
    LocalDemandAnalysis
)
from openai import OpenAI
from ..config import settings
import json

class ILocalIntelligenceProvider(ABC):
    """
    Abstract Base Class for local intelligence data sourcing.
    Allows replacing mock data with real API integrations (e.g., Google Places, Govt APIs).
    """

    @abstractmethod
    def get_competitor_data(self, location: LocationIdentity, business_type: str) -> List[Dict[str, Any]]:
        """Returns a list of nearby competitors with coordinates and metadata."""
        pass

    @abstractmethod
    def get_supplier_data(self, location: LocationIdentity, business_type: str) -> List[Dict[str, Any]]:
        """Returns available suppliers for the business type in the region."""
        pass

    @abstractmethod
    def get_logistics_data(self, location: LocationIdentity) -> Dict[str, Any]:
        """Returns data on road accessibility, transport hubs, and costs."""
        pass

    @abstractmethod
    def get_demand_data(self, location: LocationIdentity, business_type: str) -> Dict[str, Any]:
        """Returns estimated demand metrics for the specific business type."""
        pass

class AIIntelligenceProvider(ILocalIntelligenceProvider):
    """
    Production provider that uses LLM to synthesize realistic regional intelligence
    based on the specific district and business type.
    """

    def __init__(self):
        # Use Groq if available, otherwise OpenAI
        api_key = settings.groq_api_key or settings.openai_api_key
        base_url = "https://api.groq.com/openai/v1" if settings.groq_api_key else settings.openai_base_url

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = settings.llm_model

    def _query_ai(self, prompt: str) -> Dict[str, Any]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "You are a regional market intelligence expert for rural India. Return only JSON."},
                          {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"AI Intelligence Error: {e}")
            return {}

    def get_competitor_data(self, location: LocationIdentity, business_type: str) -> List[Dict[str, Any]]:
        prompt = (
            f"Identify 3 realistic competitors for a '{business_type}' business in "
            f"{location.hierarchy.district}, {location.hierarchy.state}. "
            f"Return a JSON list of objects with: name, size (Small/Medium/Large), and a brief description."
        )
        res = self._query_ai(prompt)
        competitors = res.get("competitors", [])

        # Add synthetic coordinates relative to the location
        return [
            {**c, "lat": location.lat + 0.01, "lng": location.lng + 0.01}
            for c in competitors
        ]

    def get_supplier_data(self, location: LocationIdentity, business_type: str) -> List[Dict[str, Any]]:
        prompt = (
            f"Identify 2 realistic regional suppliers for '{business_type}' in "
            f"{location.hierarchy.district}, {location.hierarchy.state}. "
            f"Return a JSON list of objects with: name, category, and distance_km."
        )
        res = self._query_ai(prompt)
        suppliers = res.get("suppliers", [])

        return [
            {**s, "lat": location.lat + 0.02, "lng": location.lng - 0.02}
            for s in suppliers
        ]

    def get_logistics_data(self, location: LocationIdentity) -> Dict[str, Any]:
        prompt = (
            f"Analyze logistics for {location.hierarchy.district}, {location.hierarchy.state}. "
            f"Return a JSON object with: road_quality (Poor/Fair/Good), nearest_hub_km (number), "
            f"avg_transport_cost_index (0.0-1.0), and accessibility_rating (0.0-1.0)."
        )
        return self._query_ai(prompt)

    def get_demand_data(self, location: LocationIdentity, business_type: str) -> Dict[str, Any]:
        prompt = (
            f"Estimate demand for '{business_type}' in {location.hierarchy.district}, {location.hierarchy.state}. "
            f"Return a JSON object with: estimated_demand_score (0.0-1.0), seasonality_index (0.0-1.0), "
            f"risks (list of strings), and footfall_proxy (Low/Medium/High)."
        )
        return self._query_ai(prompt)

class MockLocalIntelligenceProvider(ILocalIntelligenceProvider):
    """Fallback synthetic provider."""
    def get_competitor_data(self, location: LocationIdentity, business_type: str) -> List[Dict[str, Any]]:
        return [{"name": "Generic Competitor", "lat": location.lat, "lng": location.lng, "size": "Medium"}]

    def get_supplier_data(self, location: LocationIdentity, business_type: str) -> List[Dict[str, Any]]:
        return [{"name": "Generic Supplier", "lat": location.lat, "lng": location.lng, "category": "General"}]

    def get_logistics_data(self, location: LocationIdentity) -> Dict[str, Any]:
        return {"road_quality": "Fair", "nearest_hub_km": 10.0, "avg_transport_cost_index": 0.5, "accessibility_rating": 0.5}

    def get_demand_data(self, location: LocationIdentity, business_type: str) -> Dict[str, Any]:
        return {"estimated_demand_score": 0.5, "seasonality_index": 0.5, "risks": [], "footfall_proxy": "Medium"}
