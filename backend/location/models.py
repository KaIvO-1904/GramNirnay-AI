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

class LocationIdentity(BaseModel):
    """The canonical location identity."""
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    hierarchy: LocationHierarchy
    provider_id: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    source: LocationSource

class LocationCandidate(BaseModel):
    """A potential location match during search."""
    provider_id: str
    label: str # Human readable: "Anekal, Karnataka"
    hierarchy: LocationHierarchy
    lat: float
    lng: float
    confidence: float
