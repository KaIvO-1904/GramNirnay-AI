from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class LocationSource(str, Enum):
    GPS = "gps"
    MANUAL = "manual"
    IP = "ip"

class LocationHierarchy(BaseModel):
    country: Optional[str] = None
    state: str
    district: str
    taluk: Optional[str] = None
    village: str

class CurrencyInfo(BaseModel):
    code: str
    symbol: str
    locale: str

class LocationIdentity(BaseModel):
    """The canonical location identity."""
    name: str
    district: str
    state: str
    country: Optional[str] = None
    pincode: Optional[str] = None
    lat: float = 0.0
    lng: float = 0.0
    provider_id: Optional[str] = None
    coordinates: Dict[str, float] = Field(default_factory=lambda: {"lat": 0.0, "lng": 0.0}, description="{'lat': float, 'lng': float}")
    source: str
    currency: CurrencyInfo

class LocationCandidate(BaseModel):
    """A potential location match during search."""
    provider_id: str
    label: str # Human readable: "Anekal, Karnataka"
    hierarchy: LocationHierarchy
    lat: float
    lng: float
    confidence: float
