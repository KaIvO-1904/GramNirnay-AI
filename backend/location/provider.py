from abc import ABC, abstractmethod
from typing import List, Optional
from .models import LocationIdentity, LocationCandidate, LocationHierarchy

class ILocationProvider(ABC):
    """Abstraction for the geolocation provider to allow easy replacement."""

    @abstractmethod
    def forward_geocode(self, query: str) -> List[LocationCandidate]:
        """Search for place names and return candidates."""
        pass

    @abstractmethod
    def reverse_geocode(self, lat: float, lng: float) -> Optional[LocationIdentity]:
        """Convert coordinates to a structured location identity."""
        pass

    @abstractmethod
    def resolve_hierarchy(self, provider_id: str) -> Optional[LocationIdentity]:
        """Get full hierarchy details for a specific provider ID."""
        pass

class MockLocationProvider(ILocationProvider):
    """Mock implementation for testing and development."""

    def forward_geocode(self, query: str) -> List[LocationCandidate]:
        # Simulate ambiguity for "Anekal"
        if "anekal" in query.lower():
            return [
                LocationCandidate(
                    provider_id="ka_anekal",
                    label="Anekal, Karnataka",
                    hierarchy=LocationHierarchy(state="Karnataka", district="Bengaluru Rural", village="Anekal"),
                    lat=12.81, lng=77.75, confidence=1.0
                ),
                LocationCandidate(
                    provider_id="kl_anekal",
                    label="Anekal, Kerala",
                    hierarchy=LocationHierarchy(state="Kerala", district="Unknown", village="Anekal"),
                    lat=10.21, lng=76.55, confidence=0.9
                )
            ]

        # Generic mock return
        return [
            LocationCandidate(
                provider_id="gen_1",
                label=f"{query}, India",
                hierarchy=LocationHierarchy(state="Unknown", district="Unknown", village=query),
                lat=12.97, lng=77.59, confidence=0.8
            )
        ]

    def reverse_geocode(self, lat: float, lng: float) -> Optional[LocationIdentity]:
        # Mock reverse geocoding
        return LocationIdentity(
            lat=lat, lng=lng,
            hierarchy=LocationHierarchy(state="Karnataka", district="Bengaluru", village="Bengaluru City"),
            provider_id="bengaluru_city",
            confidence=1.0,
            source="gps"
        )

    def resolve_hierarchy(self, provider_id: str) -> Optional[LocationIdentity]:
        # Mock resolution
        if provider_id == "non_existent":
            return None
        return LocationIdentity(
            lat=12.97, lng=77.59,
            hierarchy=LocationHierarchy(state="Karnataka", district="Bengaluru", village="Bengaluru City"),
            provider_id=provider_id,
            confidence=1.0,
            source="manual"
        )
