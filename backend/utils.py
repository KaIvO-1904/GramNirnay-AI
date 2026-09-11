from typing import Dict

STATE_MAP = {
    "AP": "Andhra Pradesh",
    "AR": "Arunachal Pradesh",
    "AS": "Assam",
    "BR": "Bihar",
    "CH": "Chandigarh",
    "CT": "Chhattisgarh",
    "GA": "Goa",
    "GJ": "Gujarat",
    "HR": "Haryana",
    "HP": "Himachal Pradesh",
    "JK": "Jammu and Kashmir",
    "JH": "Jharkhand",
    "KA": "Karnataka",
    "KL": "Kerala",
    "MP": "Madhya Pradesh",
    "MH": "Maharashtra",
    "MN": "Manipur",
    "ML": "Meghalaya",
    "MZ": "Mizoram",
    "NL": "Nagaland",
    "OR": "Odisha",
    "PB": "Punjab",
    "RJ": "Rajasthan",
    "SK": "Sikkim",
    "TN": "Tamil Nadu",
    "TG": "Telangana",
    "TR": "Tripura",
    "UP": "Uttar Pradesh",
    "UK": "Uttarakhand",
    "WB": "West Bengal",
    "DN": "Delhi",
    "LD": "Lakshadweep",
    "PY": "Puducherry",
}

def normalize_state(state: str) -> str:
    """
    Normalizes state input to full state name.
    Handles state codes (e.g., 'KA' -> 'Karnataka') and basic casing.
    """
    if not state:
        return "India"
    
    clean_state = state.strip().upper()
    if clean_state in STATE_MAP:
        return STATE_MAP[clean_state]
    
    # Return as is but capitalized if not in map (e.g., 'karnataka' -> 'Karnataka')
    return state.strip().title()
