from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class AliasMapping(BaseModel):
    term: str
    language: str
    region: str
    confidence: float
    evidence: str
    verification_status: str

# Mapping: Canonical_ID -> List of AliasMappings
# This map supports regional and rural terminology.
SEMANTIC_MAP: Dict[str, List[AliasMapping]] = {
    "COUNTRY_CHICKEN": [
        AliasMapping(term="desi chicken", language="en", region="national", confidence=1.0, evidence="common usage", verification_status="verified"),
        AliasMapping(term="nati koli", language="kn", region="Karnataka", confidence=1.0, evidence="local term", verification_status="verified"),
        AliasMapping(term="country birds", language="en", region="national", confidence=0.8, evidence="colloquial", verification_status="verified"),
        AliasMapping(term="country chicken", language="en", region="national", confidence=1.0, evidence="standard", verification_status="verified"),
    ],
    "BROILER": [
        AliasMapping(term="meat chicken", language="en", region="national", confidence=0.9, evidence="common", verification_status="verified"),
        AliasMapping(term="white chicken", language="en", region="national", confidence=0.7, evidence="visual descriptor", verification_status="unverified"),
    ],
    "KIRANA": [
        AliasMapping(term="general store", language="en", region="national", confidence=0.9, evidence="synonym", verification_status="verified"),
        AliasMapping(term="small shop", language="en", region="national", confidence=0.6, evidence="generic", verification_status="unverified"),
    ],
    "ORGANIC_VEG": [
        AliasMapping(term="chemical free vegetables", language="en", region="national", confidence=1.0, evidence="descriptor", verification_status="verified"),
        AliasMapping(term="natural farming", language="en", region="national", confidence=0.7, evidence="broad term", verification_status="verified"),
    ]
}

def lookup_alias(term: str) -> Optional[str]:
    """Returns the canonical ID if the term is a known alias."""
    term_lower = term.lower().strip()
    for canonical_id, aliases in SEMANTIC_MAP.items():
        for alias in aliases:
            if alias.term.lower() == term_lower:
                return canonical_id
    return None
