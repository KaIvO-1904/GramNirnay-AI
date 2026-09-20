from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import httpx
from .models import LocationIdentity, LocationCandidate, LocationHierarchy, CurrencyInfo
from .currency import get_currency_for_country
from ..logger import logger

class ProviderError(Exception):
    """Base class for all provider-related errors."""
    pass

class ConfigurationError(ProviderError):
    """Raised when required API keys/tokens are missing or invalid."""
    pass

class ProviderUnavailableError(ProviderError):
    """Raised for timeouts, network failures, or 5xx/429 responses."""
    pass

class MalformedResponseError(ProviderError):
    """Raised when the API response format is unexpected."""
    pass

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
        if not self.api_key:
            raise ConfigurationError("Google Maps API key is missing.")
        try:
            with httpx.Client() as client:
                resp = client.get(
                    f"{self.base_url}/json",
                    params={"address": query, "key": self.api_key},
                    timeout=5.0
                )
                if resp.status_code == 403:
                    raise ConfigurationError(f"Google Maps API key invalid or restricted: {resp.text}")
                if resp.status_code >= 500 or resp.status_code == 429:
                    raise ProviderUnavailableError(f"Google Maps API unavailable: {resp.status_code}")

                resp.raise_for_status()
                data = resp.json()
                if data.get("status") != "OK":
                    if data.get("status") == "ZERO_RESULTS":
                        return []
                    logger.error(f"Google Forward Geocode Error: {data.get('status')}")
                    raise ProviderError(f"Google Maps API returned error status: {data.get('status')}")

                results = []
                for item in data.get("results", []):
                    addr_map = {comp["types"][0]: comp["long_name"] for comp in item.get("address_components", [])}
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
        except httpx.RequestError as e:
            raise ProviderUnavailableError(f"Google Maps network error: {e}")
        except (KeyError, TypeError) as e:
            raise MalformedResponseError(f"Unexpected Google Maps response format: {e}")
        except ProviderError:
            raise
        except Exception as e:
            logger.exception(f"Unexpected Google Forward Geocode Exception: {e}")
            raise ProviderError(f"Internal provider error: {e}")

    def reverse_geocode(self, lat: float, lng: float) -> Optional[LocationIdentity]:
        if not self.api_key:
            raise ConfigurationError("Google Maps API key is missing.")
        try:
            with httpx.Client() as client:
                resp = client.get(
                    f"{self.base_url}/json",
                    params={"latlng": f"{lat},{lng}", "key": self.api_key},
                    timeout=5.0
                )
                if resp.status_code == 403:
                    raise ConfigurationError(f"Google Maps API key invalid or restricted: {resp.text}")
                if resp.status_code >= 500 or resp.status_code == 429:
                    raise ProviderUnavailableError(f"Google Maps API unavailable: {resp.status_code}")

                resp.raise_for_status()
                data = resp.json()
                if data.get("status") != "OK":
                    if data.get("status") == "ZERO_RESULTS":
                        return None
                    logger.error(f"Google Reverse Geocode Error: {data.get('status')}")
                    raise ProviderError(f"Google Maps API returned error status: {data.get('status')}")

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
                    lat=lat,
                    lng=lng,
                    provider_id=None,
                    coordinates={"lat": lat, "lng": lng},
                    source="gps",
                    currency=CurrencyInfo(**get_currency_for_country(country))
                )
        except httpx.RequestError as e:
            raise ProviderUnavailableError(f"Google Maps network error: {e}")
        except (KeyError, TypeError) as e:
            raise MalformedResponseError(f"Unexpected Google Maps response format: {e}")
        except ProviderError:
            raise
        except Exception as e:
            logger.exception(f"Unexpected Google Reverse Geocode Exception: {e}")
            raise ProviderError(f"Internal provider error: {e}")

    def resolve_hierarchy(self, provider_id: str) -> Optional[LocationIdentity]:
        if not self.api_key:
            raise ConfigurationError("Google Maps API key is missing.")
        try:
            with httpx.Client() as client:
                resp = client.get(
                    f"https://maps.googleapis.com/maps/api/place/details/json",
                    params={"place_id": provider_id, "key": self.api_key},
                    timeout=5.0
                )
                if resp.status_code == 403:
                    raise ConfigurationError(f"Google Maps API key invalid or restricted: {resp.text}")
                if resp.status_code >= 500 or resp.status_code == 429:
                    raise ProviderUnavailableError(f"Google Maps API unavailable: {resp.status_code}")

                resp.raise_for_status()
                data = resp.json()
                if data.get("status") != "OK":
                    if data.get("status") == "NOT_FOUND":
                        return None
                    logger.error(f"Google Resolve Hierarchy Error: {data.get('status')}")
                    raise ProviderError(f"Google Maps API returned error status: {data.get('status')}")

                result = data.get("result", {})
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
                    lat=result["geometry"]["location"]["lat"],
                    lng=result["geometry"]["location"]["lng"],
                    provider_id=provider_id,
                    coordinates={
                        "lat": result.get("geometry", {}).get("location", {}).get("lat", 0.0),
                        "lng": result.get("geometry", {}).get("location", {}).get("lng", 0.0)
                    },
                    source="manual",
                    currency=CurrencyInfo(**get_currency_for_country(country))
                )
        except httpx.RequestError as e:
            raise ProviderUnavailableError(f"Google Maps network error: {e}")
        except (KeyError, TypeError) as e:
            raise MalformedResponseError(f"Unexpected Google Maps response format: {e}")
        except ProviderError:
            raise
        except Exception as e:
            logger.exception(f"Google Resolve Hierarchy Error: {e}")
            raise ProviderError(f"Internal provider error: {e}")

class OSMLocationProvider(ILocationProvider):
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org"
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

    def forward_geocode(self, query: str) -> List[LocationCandidate]:
        try:
            with httpx.Client(headers=self.headers) as client:
                search_query = f"{query}, India" if "india" not in query.lower() else query
                resp = client.get(
                    f"{self.base_url}/search",
                    params={"q": search_query, "format": "json", "addressdetails": 1, "limit": 10},
                    timeout=5.0
                )
                if resp.status_code == 429:
                    raise ProviderUnavailableError("OSM Nominatim Rate Limit exceeded (429).")
                if resp.status_code >= 500:
                    raise ProviderUnavailableError(f"OSM Search API Server Error {resp.status_code}")
                if resp.status_code != 200:
                    raise ProviderError(f"OSM Search API Error {resp.status_code}: {resp.text}")

                data = resp.json()
                if not isinstance(data, list):
                    raise MalformedResponseError("OSM Search API returned unexpected non-list response")

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
                            provider_id=str(osm_id),
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
                    except Exception as e:
                        logger.error(f"LocationCandidate creation failed: {e}")
                        continue
                return results
        except httpx.RequestError as e:
            raise ProviderUnavailableError(f"OSM network error: {e}")
        except (KeyError, TypeError) as e:
            raise MalformedResponseError(f"Unexpected OSM response format: {e}")
        except ProviderError:
            raise
        except Exception as e:
            logger.exception(f"Unexpected OSM Forward Geocode Exception: {e}")
            raise ProviderError(f"Internal provider error: {e}")

    def reverse_geocode(self, lat: float, lng: float) -> Optional[LocationIdentity]:
        try:
            with httpx.Client(headers=self.headers) as client:
                resp = client.get(
                    f"{self.base_url}/reverse",
                    params={"lat": lat, "lon": lng, "format": "json", "addressdetails": 1},
                    timeout=5.0
                )
                if resp.status_code == 429:
                    raise ProviderUnavailableError("OSM Nominatim Rate Limit exceeded (429).")
                if resp.status_code >= 500:
                    raise ProviderUnavailableError(f"OSM Reverse Geocode Server Error {resp.status_code}")
                if resp.status_code != 200:
                    raise ProviderError(f"OSM Reverse Geocode API Error {resp.status_code}: {resp.text}")

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
                    lat=lat,
                    lng=lng,
                    provider_id=None,
                    coordinates={"lat": lat, "lng": lng},
                    source="gps",
                    currency=CurrencyInfo(**get_currency_for_country(country))
                )
        except httpx.RequestError as e:
            raise ProviderUnavailableError(f"OSM network error: {e}")
        except (KeyError, TypeError) as e:
            raise MalformedResponseError(f"Unexpected OSM response format: {e}")
        except ProviderError:
            raise
        except Exception as e:
            logger.exception(f"Unexpected OSM Reverse Geocode Exception: {e}")
            raise ProviderError(f"Internal provider error: {e}")

    def resolve_hierarchy(self, provider_id: str) -> Optional[LocationIdentity]:
        try:
            with httpx.Client(headers=self.headers) as client:
                resp = client.get(
                    f"{self.base_url}/search",
                    params={"q": provider_id, "format": "json", "addressdetails": 1},
                    timeout=5.0
                )
                if resp.status_code == 429:
                    raise ProviderUnavailableError("OSM Nominatim Rate Limit exceeded (429).")
                if resp.status_code >= 500:
                    raise ProviderUnavailableError(f"OSM Resolve Hierarchy Server Error {resp.status_code}")
                if resp.status_code != 200:
                    raise ProviderError(f"OSM Resolve Hierarchy API Error {resp.status_code}: {resp.text}")

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
                    lat=float(item.get("lat", 0)),
                    lng=float(item.get("lon", 0)),
                    provider_id=str(item.get("osm_id", "")),
                    coordinates={
                        "lat": float(item.get("lat", 0)),
                        "lng": float(item.get("lon", 0))
                    },
                    source="manual",
                    currency=CurrencyInfo(**get_currency_for_country(country))
                )
        except httpx.RequestError as e:
            raise ProviderUnavailableError(f"OSM network error: {e}")
        except (KeyError, TypeError) as e:
            raise MalformedResponseError(f"Unexpected OSM response format: {e}")
        except ProviderError:
            raise
        except Exception as e:
            logger.exception(f"Unexpected OSM Resolve Hierarchy Exception: {e}")
            raise ProviderError(f"Internal provider error: {e}")

class MockLocationProvider(ILocationProvider):
    """Local mock provider for development and testing."""

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
            lat=lat,
            lng=lng,
            provider_id=None,
            coordinates={"lat": lat, "lng": lng},
            source="gps",
            currency=CurrencyInfo(code="INR", symbol="₹", locale="en-IN")
        )

    def resolve_hierarchy(self, provider_id: str) -> Optional[LocationIdentity]:
        # Match the specific mock IDs used in forward_geocode
        mock_data = {
            "ka_anekal": {
                "name": "Anekal, Karnataka",
                "district": "Bengaluru Rural",
                "state": "Karnataka",
                "country": "India",
                "lat": 12.81, "lng": 77.75
            },
            "kl_anekal": {
                "name": "Anekal, Kerala",
                "district": "Unknown",
                "state": "Kerala",
                "country": "India",
                "lat": 10.21, "lng": 76.55
            },
            "gen_1": {
                "name": "Generic Location",
                "district": "Unknown",
                "state": "Unknown",
                "country": "India",
                "lat": 12.97, "lng": 77.59
            }
        }

        data = mock_data.get(provider_id)
        if not data:
            return None

        return LocationIdentity(
            name=data["name"],
            district=data["district"],
            state=data["state"],
            country=data["country"],
            lat=data["lat"],
            lng=data["lng"],
            provider_id=provider_id,
            coordinates={"lat": data["lat"], "lng": data["lng"]},
            source="manual",
            currency=CurrencyInfo(code="INR", symbol="₹", locale="en-IN")
        )

class IPInfoLocationProvider(ILocationProvider):

    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://ipinfo.io"

    def resolve_by_ip(self, ip: str) -> Optional[LocationIdentity]:
        if not self.token:
            raise ConfigurationError("IPInfo token is missing.")
        try:
            with httpx.Client() as client:
                resp = client.get(f"{self.base_url}/{ip}?token={self.token}", timeout=5.0)
                if resp.status_code == 403:
                    raise ConfigurationError(f"IPInfo token invalid: {resp.text}")
                if resp.status_code >= 500 or resp.status_code == 429:
                    raise ProviderUnavailableError(f"IPInfo API unavailable: {resp.status_code}")
                if resp.status_code != 200:
                    raise ProviderError(f"IPInfo API Error {resp.status_code}: {resp.text}")

                data = resp.json()
                loc_parts = data.get("loc", "0,0").split(",")
                lat = float(loc_parts[0]) if len(loc_parts) > 0 else 0.0
                lng = float(loc_parts[1]) if len(loc_parts) > 1 else 0.0

                country = data.get("country", "Unknown")

                return LocationIdentity(
                    name=data.get("city", "Unknown City"),
                    district=data.get("region", "Unknown Region"),
                    state=data.get("region", "Unknown State"),
                    country=country,
                    lat=lat,
                    lng=lng,
                    provider_id=None,
                    pincode=data.get("postal"),
                    coordinates={"lat": lat, "lng": lng},
                    source="ip",
                    currency=CurrencyInfo(**get_currency_for_country(country))
                )
        except httpx.RequestError as e:
            raise ProviderUnavailableError(f"IPInfo network error: {e}")
        except (KeyError, TypeError) as e:
            raise MalformedResponseError(f"Unexpected IPInfo response format: {e}")
        except ProviderError:
            raise
        except Exception as e:
            logger.exception(f"Unexpected IPInfo Lookup Exception: {e}")
            raise ProviderError(f"Internal provider error: {e}")

    def forward_geocode(self, query: str) -> List[LocationCandidate]:
        raise NotImplementedError("IPInfo does not support forward geocoding.")

    def reverse_geocode(self, lat: float, lng: float) -> Optional[LocationIdentity]:
        raise NotImplementedError("IPInfo does not support reverse geocoding.")

    def resolve_hierarchy(self, provider_id: str) -> Optional[LocationIdentity]:
        raise NotImplementedError("IPInfo does not support hierarchy resolution.")
