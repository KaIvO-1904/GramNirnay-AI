from typing import List, Optional, Dict, Any
from .models import LocationIdentity, LocationCandidate, LocationSource
from .provider import ILocationProvider, MockLocationProvider, OSMLocationProvider

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
        # 2. Use Google Maps if API key is provided (Production Choice)
        elif settings.google_maps_api_key:
            from .provider import GoogleLocationProvider
            self.provider = GoogleLocationProvider(settings.google_maps_api_key)
        # 3. Fallback to OSM (Free Choice)
        else:
            self.provider = OSMLocationProvider()

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

    def handle_manual_confirmation(self, candidate: LocationCandidate) -> LocationIdentity:
        """Converts a selected candidate into a final identity."""
        return self.resolve_location(candidate.provider_id, LocationSource.MANUAL)
