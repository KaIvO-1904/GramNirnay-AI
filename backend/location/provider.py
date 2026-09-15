from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import httpx
from .models import LocationIdentity, LocationCandidate, LocationHierarchy
from ..logger import logger

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

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import httpx
from .models import LocationIdentity, LocationCandidate, LocationHierarchy, CurrencyInfo
from .currency import get_currency_for_country
from ..logger import logger

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

class GoogleLocationProvider(ILocationProvider):
    """Production provider using Google Maps Geocoding API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/geocode"

    def forward_geocode(self, query: str) -> List[LocationCandidate]:
        try:
            with httpx.Client() as client:
                resp = client.get(
                    f"{self.base_url}/json",
                    params={"address": query, "key": self.api_key},
                    timeout=5.0
                )
                data = resp.json()
                if data.get("status") != "OK":
                    logger.error(f"Google Forward Geocode Error: {data.get('status')}")
                    return []

                results = []
                for item in data.get("results", []):
                    # Parse address components
                    addr_map = {comp["types"][0]: comp["long_name"] for comp in item.get("address_components", [])}

                    # Map Google types to our hierarchy
                    state = addr_map.get("administrative_area_level_1", "Unknown")
                    district = addr_map.get("administrative_area_level_2") or addr_map.get("locality", "Unknown")
                    village = addr_map.get("sublocality_level_1") or addr_map.get("neighborhood", "Unknown")

                    results.append(LocationCandidate(
                        provider_id=item.get("place_id", "unknown"),
                        label=item.get("formatted_address", "Unknown Location"),
                        hierarchy=LocationHierarchy(
                            state=state,
                            district=district,
                            village=village
                        ),
                        lat=item["geometry"]["location"]["lat"],
                        lng=item["geometry"]["location"]["lng"],
                        confidence=0.9
                    ))
                return results
        except Exception as e:
            logger.error(f"Google Forward Geocode Exception: {e}")
            return []

    def reverse_geocode(self, lat: float, lng: float) -> Optional[LocationIdentity]:
        try:
            with httpx.Client() as client:
                resp = client.get(
                    f"{self.base_url}/json",
                    params={"latlng": f"{lat},{lng}", "key": self.api_key},
                    timeout=5.0
                )
                data = resp.json()
                if data.get("status") != "OK":
                    logger.error(f"Google Reverse Geocode Error: {data.get('status')}")
                    return None

                result = data.get("results", [{}])[0]
                addr_map = {comp["types"][0]: comp["long_name"] for comp in result.get("address_components", [])}

                state = addr_map.get("administrative_area_level_1", "Unknown")
                district = addr_map.get("administrative_area_level_2") or addr_map.get("locality", "Unknown")
                village = addr_map.get("sublocality_level_1") or addr_map.get("neighborhood", "Unknown")
                country = addr_map.get("country", "India")

                return LocationIdentity(
                    name=result.get("formatted_address", "Unknown Location"),
                    district=district,
                    state=state,
                    country=country,
                    coordinates={"lat": lat, "lng": lng},
                    source="gps",
                    currency=CurrencyInfo(**get_currency_for_country(country))
                )
        except Exception as e:
            logger.error(f"Google Reverse Geocode Exception: {e}")
            return None

    def resolve_hierarchy(self, provider_id: str) -> Optional[LocationIdentity]:
        try:
            with httpx.Client() as client:
                resp = client.get(
                    f"https://maps.googleapis.com/maps/api/place/details/json",
                    params={"place_id": provider_id, "key": self.api_key},
                    timeout=5.0
                )
                data = resp.json()
                if data.get("status") != "OK":
                    return None

                result = data.get("result", {})

                # Parse address components directly from result
                addr_map = {comp["types"][0]: comp["long_name"] for comp in result.get("address_components", [])}

                state = addr_map.get("administrative_area_level_1", "Unknown")
                district = addr_map.get("administrative_area_level_2") or addr_map.get("locality", "Unknown")
                village = addr_map.get("sublocality_level_1") or addr_map.get("neighborhood", "Unknown")
                country = addr_map.get("country", "India")

                return LocationIdentity(
                    name=result.get("formatted_address", "Unknown Location"),
                    district=district,
                    state=state,
                    country=country,
                    coordinates={
                        "lat": result.get("geometry", {}).get("location", {}).get("lat", 0.0),
                        "lng": result.get("geometry", {}).get("location", {}).get("lng", 0.0)
                    },
                    source="manual",
                    currency=CurrencyInfo(**get_currency_for_country(country))
                )
        except Exception as e:
            logger.error(f"Google Resolve Hierarchy Error: {e}")
            return None

class OSMLocationProvider(ILocationProvider):
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org"
        self.headers = {"User-Agent": "GramNirnayAI/1.0 (contact: support@gramnirnay.ai)"}

    def forward_geocode(self, query: str) -> List[LocationCandidate]:
        try:
            with httpx.Client(headers=self.headers) as client:
                search_query = f"{query}, India" if "india" not in query.lower() else query

                resp = client.get(
                    f"{self.base_url}/search",
                    params={"q": search_query, "format": "json", "addressdetails": 1, "limit": 10},
                    timeout=5.0
                )

                if resp.status_code != 200:
                    logger.error(f"OSM Search API Error {resp.status_code}: {resp.text}")
                    return []

                data = resp.json()
                if not isinstance(data, list):
                    return []

                results = []
                for item in data:
                    addr = item.get("address", {})
                    osm_id = item.get("osm_id")
                    if not osm_id:
                        continue

                    state = addr.get("state") or addr.get("province") or addr.get("region") or "Unknown"
                    district = (
                        addr.get("county") or
                        addr.get("city") or
                        addr.get("town") or
                        addr.get("village") or
                        addr.get("administrative_area_level_2") or
                        "Unknown"
                    )
                    village = (
                        addr.get("village") or
                        addr.get("suburb") or
                        addr.get("hamlet") or
                        addr.get("neighbourhood") or
                        "Unknown"
                    )

                    try:
                        results.append(LocationCandidate(
                            provider_id=osm_id,
                            label=item.get("display_name", "Unknown Location"),
                            hierarchy=LocationHierarchy(
                                state=str(state),
                                district=str(district),
                                village=str(village)
                            ),
                            lat=float(item.get("lat", 0)),
                            lng=float(item.get("lon", 0)),
                            confidence=0.8
                        ))
                    except Exception:
                        continue
                return results
        except Exception as e:
            logger.error(f"OSM Forward Geocode Exception: {e}")
            return []

    def reverse_geocode(self, lat: float, lng: float) -> Optional[LocationIdentity]:
        try:
            with httpx.Client(headers=self.headers) as client:
                resp = client.get(
                    f"{self.base_url}/reverse",
                    params={"lat": lat, "lon": lng, "format": "json", "addressdetails": 1},
                    timeout=5.0
                )
                if resp.status_code != 200:
                    logger.error(f"OSM Reverse Geocode API Error {resp.status_code}: {resp.text}")
                    return None

                data = resp.json()
                if "error" in data:
                    logger.error(f"OSM Reverse Geocode Error: {data['error']}")
                    return None

                addr = data.get("address", {})
                country = addr.get("country", "India")

                return LocationIdentity(
                    name=data.get("display_name", "Unknown Location"),
                    district=addr.get("county") or addr.get("city") or addr.get("town", "Unknown"),
                    state=addr.get("state", "Unknown"),
                    country=country,
                    coordinates={"lat": lat, "lng": lng},
                    source="gps",
                    currency=CurrencyInfo(**get_currency_for_country(country))
                )
        except Exception as e:
            logger.error(f"OSM Reverse Geocode Exception: {e}")
            return None

    def resolve_hierarchy(self, provider_id: str) -> Optional[LocationIdentity]:
        try:
            with httpx.Client(headers=self.headers) as client:
                resp = client.get(
                    f"{self.base_url}/search",
                    params={"q": provider_id, "format": "json", "addressdetails": 1},
                    timeout=5.0
                )
                data = resp.json()
                if not data:
                    return None

                item = data[0]
                addr = item.get("address", {})
                country = addr.get("country", "India")
                return LocationIdentity(
                    name=item.get("display_name", "Unknown Location"),
                    district=addr.get("county") or addr.get("city") or addr.get("town", "Unknown"),
                    state=addr.get("state", "Unknown"),
                    country=country,
                    coordinates={
                        "lat": float(item.get("lat", 0)),
                        "lng": float(item.get("lon", 0))
                    },
                    provider_id=item.get("osm_id", "unknown"),
                    source="manual",
                    currency=CurrencyInfo(**get_currency_for_country(country))
                )
        except Exception as e:
            logger.error(f"OSM Resolve Hierarchy Error: {e}")
            return None

class MockLocationProvider(ILocationProvider):
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
            name="Bengaluru City",
            district="Bengaluru",
            state="Karnataka",
            country="India",
            coordinates={"lat": lat, "lng": lng},
            source="gps",
            currency=CurrencyInfo(code="INR", symbol="₹", locale="en-IN")
        )

    def resolve_hierarchy(self, provider_id: str) -> Optional[LocationIdentity]:
        return LocationIdentity(
            name="Bengaluru City",
            district="Bengaluru",
            state="Karnataka",
            country="India",
            coordinates={"lat": 12.97, "lng": 77.59},
            source="manual",
            currency=CurrencyInfo(code="INR", symbol="₹", locale="en-IN")
        )

        try:
            with httpx.Client() as client:
                resp = client.get(
                    f"https://maps.googleapis.com/maps/api/place/details/json",
                    params={"place_id": provider_id, "key": self.api_key},
                    timeout=5.0
                )
                data = resp.json()
                if data.get("status") != "OK":
                    return None

                result = data.get("result", {})

                # Parse address components directly from result
                addr_map = {comp["types"][0]: comp["long_name"] for comp in result.get("address_components", [])}

                state = addr_map.get("administrative_area_level_1", "Unknown")
                district = addr_map.get("administrative_area_level_2") or addr_map.get("locality", "Unknown")
                village = addr_map.get("sublocality_level_1") or addr_map.get("neighborhood", "Unknown")

                return LocationIdentity(
                    lat=result.get("geometry", {}).get("location", {}).get("lat", 0.0),
                    lng=result.get("geometry", {}).get("location", {}).get("lng", 0.0),
                    hierarchy=LocationHierarchy(
                        state=state,
                        district=district,
                        village=village
                    ),
                    provider_id=provider_id,
                    confidence=1.0,
                    source="manual"
                )
        except Exception as e:
            logger.error(f"Google Resolve Hierarchy Error: {e}")
            return None

class OSMLocationProvider(ILocationProvider):


    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org"
        self.headers = {"User-Agent": "GramNirnayAI/1.0 (contact: support@gramnirnay.ai)"}

    def forward_geocode(self, query: str) -> List[LocationCandidate]:
        try:
            with httpx.Client(headers=self.headers) as client:
                # Use a more generic search query to increase hit rate
                # We search for the query as is, and optionally with ", India"
                search_query = f"{query}, India" if "india" not in query.lower() else query

                resp = client.get(
                    f"{self.base_url}/search",
                    params={"q": search_query, "format": "json", "addressdetails": 1, "limit": 10},
                    timeout=5.0
                )

                if resp.status_code != 200:
                    logger.error(f"OSM Search API Error {resp.status_code}: {resp.text}")
                    return []

                data = resp.json()
                if not isinstance(data, list):
                    return []

                results = []
                for item in data:
                    addr = item.get("address", {})
                    osm_id = item.get("osm_id")
                    if not osm_id:
                        continue

                    # Broaden the search for district/state/village to avoid "Unknown" blocks
                    # OSM uses different keys depending on the region
                    state = addr.get("state") or addr.get("province") or addr.get("region") or "Unknown"

                    # District mapping: county -> city -> town -> village -> administrative_area_level_2
                    district = (
                        addr.get("county") or
                        addr.get("city") or
                        addr.get("town") or
                        addr.get("village") or
                        addr.get("administrative_area_level_2") or
                        "Unknown"
                    )

                    village = (
                        addr.get("village") or
                        addr.get("suburb") or
                        addr.get("hamlet") or
                        addr.get("neighbourhood") or
                        "Unknown"
                    )

                    try:
                        results.append(LocationCandidate(
                            provider_id=osm_id,
                            label=item.get("display_name", "Unknown Location"),
                            hierarchy=LocationHierarchy(
                                state=str(state),
                                district=str(district),
                                village=str(village)
                            ),
                            lat=float(item.get("lat", 0)),
                            lng=float(item.get("lon", 0)),
                            confidence=0.8
                        ))
                    except Exception:
                        continue
                return results
        except Exception as e:
            logger.error(f"OSM Forward Geocode Exception: {e}")
            return []

    def reverse_geocode(self, lat: float, lng: float) -> Optional[LocationIdentity]:
        try:
            with httpx.Client(headers=self.headers) as client:
                resp = client.get(
                    f"{self.base_url}/reverse",
                    params={"lat": lat, "lon": lng, "format": "json", "addressdetails": 1},
                    timeout=5.0
                )
                if resp.status_code != 200:
                    logger.error(f"OSM Reverse Geocode API Error {resp.status_code}: {resp.text}")
                    return None

                data = resp.json()
                if "error" in data:
                    logger.error(f"OSM Reverse Geocode Error: {data['error']}")
                    return None

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
            logger.error(f"OSM Reverse Geocode Exception: {e}")
            return None

    def resolve_hierarchy(self, provider_id: str) -> Optional[LocationIdentity]:
        try:
            # Nominatim /search can work with osm_id if we use the right syntax
            # but /details is the correct way. Since we don't have osm_type,
            # we attempt a general search for the ID.
            with httpx.Client(headers=self.headers) as client:
                resp = client.get(
                    f"{self.base_url}/search",
                    params={"q": provider_id, "format": "json", "addressdetails": 1},
                    timeout=5.0
                )
                data = resp.json()
                if not data:
                    return None

                item = data[0]
                addr = item.get("address", {})
                return LocationIdentity(
                    lat=float(item.get("lat", 0)),
                    lng=float(item.get("lon", 0)),
                    hierarchy=LocationHierarchy(
                        state=addr.get("state", "Unknown"),
                        district=addr.get("county") or addr.get("city") or addr.get("town", "Unknown"),
                        village=addr.get("village") or addr.get("suburb", "Unknown")
                    ),
                    provider_id=item.get("osm_id", "unknown"),
                    confidence=1.0,
                    source="manual"
                )
        except Exception as e:
            logger.error(f"OSM Resolve Hierarchy Error: {e}")
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
