from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..location.models import LocationIdentity
from .models import (
    CompetitionAnalysis,
    SupplyChainAnalysis,
    LogisticsAnalysis,
    LocalDemandAnalysis
)

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

class MockLocalIntelligenceProvider(ILocalIntelligenceProvider):
    """
    Synthetic provider for development and demo purposes.
    Does NOT fabricate precise local facts but provides structured proxy data.
    """

    def get_competitor_data(self, location: LocationIdentity, business_type: str) -> List[Dict[str, Any]]:
        # Mocking competitors based on business type
        # In reality, this would query Google Places API with a radius
        return [
            {"name": "Competitor A", "lat": location.lat + 0.01, "lng": location.lng + 0.01, "size": "Small"},
            {"name": "Competitor B", "lat": location.lat - 0.02, "lng": location.lng + 0.01, "size": "Medium"},
            {"name": "Competitor C", "lat": location.lat + 0.03, "lng": location.lng - 0.01, "size": "Large"},
        ]

    def get_supplier_data(self, location: LocationIdentity, business_type: str) -> List[Dict[str, Any]]:
        # Mocking suppliers
        return [
            {"name": "District Feed Store", "lat": location.lat + 0.05, "lng": location.lng + 0.05, "category": "Feed"},
            {"name": "Regional Seed Bank", "lat": location.lat - 0.04, "lng": location.lng - 0.02, "category": "Seeds"},
        ]

    def get_logistics_data(self, location: LocationIdentity) -> Dict[str, Any]:
        return {
            "road_quality": "Fair",
            "nearest_hub_km": 15.0,
            "avg_transport_cost_index": 0.4,
            "accessibility_rating": 0.7
        }

    def get_demand_data(self, location: LocationIdentity, business_type: str) -> Dict[str, Any]:
        return {
            "estimated_demand_score": 0.65,
            "seasonality_index": 0.4,
            "risks": ["Monsoon flooding", "Power instability"],
            "footfall_proxy": "Medium"
        }
