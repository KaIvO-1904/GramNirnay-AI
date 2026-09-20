from typing import List, Optional, Dict, Any
from .models import LocationIdentity, LocationCandidate, LocationSource
from .provider import (
    ILocationProvider,
    MockLocationProvider,
    OSMLocationProvider,
    GoogleLocationProvider,
    ProviderError,
    ConfigurationError,
    ProviderUnavailableError
)
from ..config import settings
from ..logger import logger

class LocationAmbiguityError(Exception):
    """Raised when multiple locations match a query."""
    def __init__(self, candidates: List[LocationCandidate]):
        self.candidates = candidates
        super().__init__("Multiple locations matched the query. User must choose.")

class LocationServiceError(Exception):
    """Controlled service error for location resolution failures."""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.original_error = original_error
        super().__init__(message)

class LocationService:
    """High-level service for managing geolocation logic."""

    def __init__(self, provider: Optional[ILocationProvider] = None):
        # 1. If a provider is explicitly passed, use it
        if provider:
            self.provider = provider
        # 2. Use Google provider if API key is available
        elif settings.google_maps_api_key:
            self.provider = GoogleLocationProvider(settings.google_maps_api_key)
        # 3. Fallback to OSM for production/standard use
        elif not settings.demo_mode:
            self.provider = OSMLocationProvider()
        # 4. Default to Mock for demo/test mode
        else:
            self.provider = MockLocationProvider()

        # Initialize IP provider if token is available
        self.ip_provider = None
        if settings.ipinfo_token:
            from .provider import IPInfoLocationProvider
            self.ip_provider = IPInfoLocationProvider(settings.ipinfo_token)


    def search_place(self, query: str) -> List[LocationCandidate]:
        """Search for a place and return candidates with fallback."""
        try:
            return self.provider.forward_geocode(query)
        except ProviderError as e:
            logger.error(f"Primary provider failed search: {e}. Trying fallback.")
            # Fallback to OSM if primary was Google
            if isinstance(self.provider, GoogleLocationProvider):
                try:
                    osm = OSMLocationProvider()
                    return osm.forward_geocode(query)
                except ProviderError as fallback_e:
                    raise LocationServiceError("All location providers failed search.", original_error=fallback_e)
            raise LocationServiceError("Location provider failed search.", original_error=e)

    def resolve_location(self, provider_id: str, source: LocationSource) -> LocationIdentity:
        """Resolves a provider ID into a canonical LocationIdentity."""
        try:
            identity = self.provider.resolve_hierarchy(provider_id)
            if not identity:
                raise ValueError("Could not resolve location ID.")

            # Update source
            identity.source = source
            return identity
        except ProviderError as e:
            raise LocationServiceError("Could not resolve location identity.", original_error=e)

    def resolve_gps(self, lat: float, lng: float) -> LocationIdentity:
        """Resolves coordinates to a structured identity via reverse geocoding with fallback."""
        # Validate coordinates
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            raise ValueError("Invalid coordinates provided.")

        try:
            identity = self.provider.reverse_geocode(lat, lng)
            if identity:
                identity.source = LocationSource.GPS
                return identity

            # If primary returned no result, try fallback
            return self._resolve_gps_fallback(lat, lng)
        except ProviderError as e:
            logger.error(f"Primary provider failed GPS resolution: {e}. Trying fallback.")
            return self._resolve_gps_fallback(lat, lng)

    def _resolve_gps_fallback(self, lat: float, lng: float) -> LocationIdentity:
        """Internal helper for GPS fallback."""
        try:
            if isinstance(self.provider, GoogleLocationProvider):
                fallback = OSMLocationProvider()
            elif isinstance(self.provider, OSMLocationProvider):
                # Google is usually primary, if we are already on OSM, we have no more fallbacks
                raise ProviderError("No further fallback providers available.")
            else:
                # Mock or others
                fallback = OSMLocationProvider()

            identity = fallback.reverse_geocode(lat, lng)
            if not identity:
                raise ValueError("No location found in any provider for these coordinates.")

            identity.source = LocationSource.GPS
            return identity
        except (ProviderError, ValueError) as e:
            raise LocationServiceError("Could not resolve coordinates to a location.", original_error=e)

    def detect_by_ip(self, ip: str) -> Optional[LocationIdentity]:
        """Detects location based on IP address using IPInfo."""
        if not self.ip_provider:
            # This is a configuration failure
            from .provider import ConfigurationError
            raise ConfigurationError("IPInfo provider not initialized. Missing IPINFO_TOKEN.")

        # Let ProviderError (ConfigurationError, ProviderUnavailableError) bubble up
        return self.ip_provider.resolve_by_ip(ip)

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
