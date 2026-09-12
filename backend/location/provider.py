from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import httpx
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

class OSMLocationProvider(ILocationProvider):
    """Free provider using OpenStreetMap Nominatim."""

    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org"
        self.headers = {"User-Agent": "GramNirnayAI/1.0 (contact: support@gramnirnay.ai)"}

    def forward_geocode(self, query: str) -> List[LocationCandidate]:
        try:
            with httpx.Client(headers=self.headers) as client:
                resp = client.get(
                    f"{self.base_url}/search",
                    params={"q": query, "format": "json", "addressdetails": 1, "limit": 5},
                    timeout=5.0
                )
                data = resp.json()

                results = []
                for item in data:
                    addr = item.get("address", {})
                    results.append(LocationCandidate(
                        provider_id=item.get("osm_id", "unknown"),
                        label=item.get("display_name", "Unknown Location"),
                        hierarchy=LocationHierarchy(
                            state=addr.get("state", "Unknown"),
                            district=addr.get("county") or addr.get("city") or addr.get("town", "Unknown"),
                            village=addr.get("village") or addr.get("suburb", "Unknown")
                        ),
                        lat=float(item.get("lat", 0)),
                        lng=float(item.get("lon", 0)),
                        confidence=0.8
                    ))
                return results
        except Exception as e:
            print(f"OSM Forward Geocode Error: {e}")
            return []

    def reverse_geocode(self, lat: float, lng: float) -> Optional[LocationIdentity]:
        try:
            with httpx.Client(headers=self.headers) as client:
                resp = client.get(
                    f"{self.base_url}/reverse",
                    params={"lat": lat, "lon": lng, "format": "json", "addressdetails": 1},
                    timeout=5.0
                )
                data = resp.json()
                addr = data.get("address", {})

                return LocationIdentity(
                    lat=lat, lng=lng,
                    hierarchy=LocationHierarchy(
                        state=addr.get("state", "Unknown"),
                        district=addr.get("county") or addr.get("city") or addr.get("town", "Unknown"),
                        village=addr.get("village") or addr.get("suburb", "Unknown")
                    ),
                    provider_id=data.get("osm_id", "unknown"),
                    confidence=0.9,
                    source="gps"
                )
        except Exception as e:
            print(f"OSM Reverse Geocode Error: {e}")
            return None

    def resolve_hierarchy(self, provider_id: str) -> Optional[LocationIdentity]:
        return None

class MockLocationProvider(ILocationProvider):
    """Mock implementation for testing and development."""

    def forward_geocode(self, query: str) -> List[LocationCandidate]:
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
        return [
            LocationCandidate(
                provider_id="gen_1",
                label=f"{query}, India",
                hierarchy=LocationHierarchy(state="Unknown", district="Unknown", village=query),
                lat=12.97, lng=77.59, confidence=0.8
            )
        ]

    def reverse_geocode(self, lat: float, lng: float) -> Optional[LocationIdentity]:
        return LocationIdentity(
            lat=lat, lng=lng,
            hierarchy=LocationHierarchy(state="Karnataka", district="Bengaluru", village="Bengaluru City"),
            provider_id="bengaluru_city",
            confidence=1.0,
            source="gps"
        )

    def resolve_hierarchy(self, provider_id: str) -> Optional[LocationIdentity]:
        if provider_id == "non_existent":
            return None
        return LocationIdentity(
            lat=12.97, lng=77.59,
            hierarchy=LocationHierarchy(state="Karnataka", district="Bengaluru", village="Bengaluru City"),
            provider_id=provider_id,
            confidence=1.0,
            source="manual"
        )
