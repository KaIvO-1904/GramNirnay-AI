# Design Plan: IPInfo Integration and Hardcoding Cleanup

## Goal
Implement a location resolution hierarchy: **Browser GPS $\rightarrow$ IPInfo Fallback $\rightarrow$ Manual Search**, and remove hardcoded "India"/"Rural India" defaults.

## 1. Backend Implementation

### 1.1 `IPInfoLocationProvider` Class
- **File**: `backend/location/provider.py`
- **Implementation**:
    - Implement `ILocationProvider` (even if some methods return empty lists for IP-based flow).
    - Use `httpx` to call `https://ipinfo.io/{ip}?token={token}`.
    - Use `settings.ipinfo_token` (to be added to `Settings`).
    - **Key methods**:
        - `forward_geocode`: Return empty list.
        - `reverse_geocode`: Return `None`.
        - `resolve_hierarchy`: Return `None`.
    - **NEW Method**: `resolve_by_ip(ip_address: str) -> Optional[LocationIdentity]`.
        - Fetches data from IPInfo.
        - Maps IPInfo fields (city, region, country) to `LocationIdentity`.
        - Sets `source = LocationSource.IP`.
        - Resolves currency using `get_currency_for_country`.

### 1.2 `LocationService` Enhancements
- **File**: `backend/location/service.py`
- **Changes**:
    - Add `ip_provider: IPInfoLocationProvider` to `__init__`.
    - Implement `resolve_by_ip(ip_address: str) -> LocationIdentity`.
        - Calls `ip_provider.resolve_by_ip(ip_address)`.
        - Raises `ValueError` if resolution fails.

### 1.3 `backend/main.py` API Exposure
- **Changes**:
    - Add `ipinfo_token` to `Settings` in `backend/config.py`.
    - New Endpoint: `POST /api/location/ip`.
        - Extracts client IP from `request.client.host`.
        - Calls `location_service.resolve_by_ip(ip)`.
        - Returns `LocationIdentity`.

## 2. Frontend Implementation

### 2.1 `LocationJourney.tsx` Fallback Flow
- **File**: `frontend/components/ui/LocationJourney.tsx`
- **Logic Update in `detectLocation`**:
    1. `navigator.geolocation.getCurrentPosition` $\rightarrow$ `resolveGps`.
    2. **On Error/Timeout**:
        - Call `POST /api/location/ip`.
        - If success: `setSelectedLocation` $\rightarrow$ `setStep('confirming')`.
        - If failure: `setError('Unable to detect location...')` $\rightarrow$ `setStep('resolving')` (Manual search).
    3. **On Manual Selection**: `resolveLocation` with `source='manual'`.

## 3. Hardcoding Cleanup Plan

### 3.1 Identification
The following patterns were found:
- `backend/location/models.py`: `country: str = "India"`
- `backend/location/provider.py`: Defaulting to `"India"` in `reverse_geocode` and `forward_geocode`.
- `backend/context_engine.py`, `backend/interpreter.py`: Defaulting to `"India"` and `"Rural India"`.
- `backend/location/currency.py`: Fallback to `COUNTRY_CURRENCY_MAP["India"]`.

### 3.2 Remediation Strategy
- **Models**: Remove default values from `LocationHierarchy` and `LocationIdentity`. Make them required or use `Optional`.
- **Providers**: 
    - Instead of `addr_map.get("country", "India")`, use `addr_map.get("country", "Unknown")`.
    - If the app is strictly for India, this should be a config setting (`settings.default_country`), not hardcoded in the logic.
- **Context/Interpreter**: 
    - Replace `"India"` and `"Rural India"` defaults with variables passed from the resolved `LocationIdentity`.
    - Use `LocationIdentity.country` and `LocationIdentity.district`.
- **Currency**: 
    - Update `get_currency_for_country` to return a generic fallback or raise an error if the country is unknown, instead of defaulting to India.

## 4. Critical Files for Implementation
- `backend/config.py`
- `backend/location/provider.py`
- `backend/location/service.py`
- `backend/main.py`
- `frontend/components/ui/LocationJourney.tsx`
- `backend/location/models.py`
EOF`
