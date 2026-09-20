import pytest
from backend.location.service import LocationService
from backend.location.models import LocationSource, LocationIdentity

def test_valid_gps():
    service = LocationService()
    result = service.resolve_gps(12.97, 77.59)
    assert result.lat == 12.97
    assert result.source == LocationSource.GPS
    assert result.state == "Karnataka"

def test_invalid_coordinates():
    service = LocationService()
    with pytest.raises(ValueError, match="Invalid coordinates"):
        service.resolve_gps(100.0, 200.0)

def test_reverse_geocoding_success():
    service = LocationService()
    result = service.resolve_gps(12.97, 77.59)
    assert "Bengaluru" in result.name

def test_duplicate_place_names():
    service = LocationService()
    candidates = service.search_place("Anekal")
    assert len(candidates) > 1
    assert any("Karnataka" in c.label for c in candidates)
    assert any("Kerala" in c.label for c in candidates)

def test_manual_override():
    service = LocationService()
    candidates = service.search_place("Anekal")
    selected = candidates[0]
    result = service.handle_manual_confirmation(selected)
    assert result.source == LocationSource.MANUAL
    assert result.provider_id == selected.provider_id

def test_missing_location():
    service = LocationService()
    with pytest.raises(ValueError, match="Could not resolve location ID"):
        service.resolve_location("non_existent", LocationSource.MANUAL)
