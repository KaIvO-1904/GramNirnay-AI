from typing import List
from ..ontology.models import BusinessProfile

class LocationService:
    """Handles geo-spatial intelligence and regional constraints."""

    def get_regional_constraints(self, location: str) -> List[str]:
        """Returns constraints specific to the given location."""
        # Mock regional constraints - in production, this would query a database
        constraints = {
            "Maharashtra": ["Agricultural land ceiling applies", "Priority for women entrepreneurs in rural zones"],
            "Uttar Pradesh": ["Specific subsidies for food processing units", "District-level industrial permits required"],
            "Karnataka": ["Digital literacy requirement for some IT schemes", "Startup Karnataka incentives available"]
        }

        # Simple substring match for the demo
        for state, rules in constraints.items():
            if state.lower() in location.lower():
                return rules

        return ["Standard national guidelines apply"]

    def get_local_tips(self, location: str, category: str) -> List[str]:
        """Returns tailored tips for the region and business category."""
        # Mock regional tips
        return [f"Check the local district collector's office in {location} for {category} subsidies."]
