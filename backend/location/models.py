from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class LocationSource(str, Enum):
    GPS = "gps"
    MANUAL = "manual"
    IP = "ip"

class LocationHierarchy(BaseModel):
    country: str = "India"
    state: str
    district: str
    taluk: Optional[str] = None
    village: str

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class LocationSource(str, Enum):
    GPS = "gps"
    MANUAL = "manual"
    IP = "ip"

class LocationHierarchy(BaseModel):
    country: str = "India"
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
    country: str
    pincode: Optional[str] = None
    coordinates: Dict[str, float] = Field(..., description="{'lat': float, 'lng': float}")
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


class LocationCandidate(BaseModel):
    """A potential location match during search."""
    provider_id: str
    label: str # Human readable: "Anekal, Karnataka"
    hierarchy: LocationHierarchy
    lat: float
    lng: float
    confidence: float
