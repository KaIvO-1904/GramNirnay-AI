from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..ontology.business_graph import BUSINESS_GRAPH, BusinessNode

class Contradiction(BaseModel):
    attribute: str
    value: str
    reason: str

class ContradictionResult(BaseModel):
    has_contradictions: bool
    contradictions: List[Contradiction] = []

class ContradictionEngine:
    """Detects logically incompatible values within a business profile."""

    def check_contradictions(self, canonical_id: str, attributes: Dict[str, Any]) -> ContradictionResult:
        """
        Checks if the provided attributes contradict the rules of the canonical business node.
        """
        node = BUSINESS_GRAPH.get(canonical_id)
        if not node:
            return ContradictionResult(has_contradictions=False)

        contradictions = []

        # Check incompatibility rules defined in the business graph
        # incompatible_attributes: attr_name -> list of forbidden values
        for attr_name, forbidden_values in node.incompatible_attributes.items():
            if attr_name in attributes:
                val = attributes[attr_name]
                if val in forbidden_values:
                    contradictions.append(Contradiction(
                        attribute=attr_name,
                        value=str(val),
                        reason=f"For {node.canonical_name}, {val} is not a compatible value for {attr_name}."
                    ))

        return ContradictionResult(
            has_contradictions=len(contradictions) > 0,
            contradictions=contradictions
        )
