from typing import List, Optional, Dict, Any
from .models import LocationIdentity, LocationCandidate, LocationSource
from .provider import ILocationProvider, MockLocationProvider, OSMLocationProvider
from ..config import settings

class LocationAmbiguityError(Exception):
    """Raised when multiple locations match a query."""
    def __init__(self, candidates: List[LocationCandidate]):
        self.candidates = candidates
        super().__init__("Multiple locations matched the query. User must choose.")

class LocationService:
    """High-level service for managing geolocation logic."""

    def __init__(self, provider: Optional[ILocationProvider] = None):
        # 1. If a provider is explicitly passed, use it
        if provider:
            self.provider = provider
        # 2. Use Google provider if API key is available
        elif settings.google_maps_api_key:
            from .provider import GoogleLocationProvider
            self.provider = GoogleLocationProvider(settings.google_maps_api_key)
        # 3. Fallback to OSM for production/standard use
        elif not settings.demo_mode:
            self.provider = OSMLocationProvider()
        # 4. Default to Mock for demo/test mode
        else:
            from .provider import MockLocationProvider
            self.provider = MockLocationProvider()

        # Initialize IP provider if token is available
        self.ip_provider = None
        if settings.ipinfo_token:
            from .provider import IPInfoLocationProvider
            self.ip_provider = IPInfoLocationProvider(settings.ipinfo_token)


    def search_place(self, query: str) -> List[LocationCandidate]:
        """Search for a place and return candidates."""
        return self.provider.forward_geocode(query)

    def resolve_location(self, provider_id: str, source: LocationSource) -> LocationIdentity:
        """Resolves a provider ID into a canonical LocationIdentity."""
        identity = self.provider.resolve_hierarchy(provider_id)
        if not identity:
            raise ValueError("Could not resolve location ID.")

        # Update source
        identity.source = source
        return identity

    def resolve_gps(self, lat: float, lng: float) -> LocationIdentity:
        """Resolves coordinates to a structured identity via reverse geocoding."""
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            raise ValueError("Invalid coordinates provided.")

        identity = self.provider.reverse_geocode(lat, lng)
        if not identity:
            raise ValueError("Could not reverse geocode coordinates.")

        identity.source = LocationSource.GPS
        return identity

    def get_regional_constraints(self, location: str) -> List[str]:
        """Returns constraints specific to the given location."""
        constraints = {
            "Maharashtra": ["Agricultural land ceiling applies", "Priority for women entrepreneurs in rural zones"],
            "Uttar Pradesh": ["Specific subsidies for food processing units", "District-level industrial permits required"],
            "Karnataka": ["Digital literacy requirement for some IT schemes", "Startup Karnataka incentives available"]
        }

        for state, rules in constraints.items():
            if state.lower() in location.lower():
                return rules

        return ["Standard national guidelines apply"]

    def get_local_tips(self, location: str, category: str) -> List[str]:
        """Returns tailored tips for the region and business category."""
        return [f"Check the local district collector's office in {location} for {category} subsidies."]

    def detect_by_ip(self, ip: str) -> Optional[LocationIdentity]:
        """Detects location based on IP address using IPInfo."""
        if not self.ip_provider:
            logger.error("IPInfo provider not initialized. Missing IPINFO_TOKEN.")
            return None

        try:
            return self.ip_provider.resolve_by_ip(ip)
        except Exception as e:
            logger.error(f"IP-based location detection failed: {e}")
            return None
