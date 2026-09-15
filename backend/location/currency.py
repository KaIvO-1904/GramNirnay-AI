from typing import Dict, TypedDict

class CurrencyInfo(TypedDict):
    code: str
    symbol: str
    locale: str

COUNTRY_CURRENCY_MAP: Dict[str, CurrencyInfo] = {
    "India": {
        "code": "INR",
        "symbol": "₹",
        "locale": "en-IN"
    },
    "United States": {
        "code": "USD",
        "symbol": "$",
        "locale": "en-US"
    },
    "United Kingdom": {
        "code": "GBP",
        "symbol": "£",
        "locale": "en-GB"
    },
    "European Union": {
        "code": "EUR",
        "symbol": "€",
        "locale": "de-DE"
    },
    "Canada": {
        "code": "CAD",
        "symbol": "CA$",
        "locale": "en-CA"
    },
    "Australia": {
        "code": "AUD",
        "symbol": "A$",
        "locale": "en-AU"
    },
    "Singapore": {
        "code": "SGD",
        "symbol": "S$",
        "locale": "en-SG"
    },
}

def get_currency_for_country(country: str) -> CurrencyInfo:
    """Returns deterministic currency info for a given country name."""
    return COUNTRY_CURRENCY_MAP.get(country, COUNTRY_CURRENCY_MAP["India"])
