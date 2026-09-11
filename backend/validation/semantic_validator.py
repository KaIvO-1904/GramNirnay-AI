from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from ..ontology.business_graph import BUSINESS_GRAPH, get_all_descendants, get_node_by_canonical_name
from ..ontology.semantic_map import lookup_alias

class ValidationStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    AMBIGUOUS = "AMBIGUOUS"

class ValidationResult(BaseModel):
    status: ValidationStatus
    canonical_id: Optional[str] = None
    reason: Optional[str] = None
    suggestions: List[str] = []
    confidence: float = 0.0

class SemanticValidator:
    """Deterministic validation of business categories and answers."""

    def __init__(self):
        pass

    def validate_answer(self, expected_node_id: str, user_answer: str) -> ValidationResult:
        """
        Validates if the user_answer belongs to the expected_node_id domain.
        """
        if not user_answer or not user_answer.strip():
            return ValidationResult(
                status=ValidationStatus.INVALID,
                reason="Answer is missing.",
                suggestions=self._get_suggestions(expected_node_id)
            )

        answer_clean = user_answer.strip().lower()

        # 1. Check if it's already a canonical name (case insensitive)
        node = get_node_by_canonical_name(answer_clean)
        if node:
            canonical_id = node.id
        else:
            # 2. Check the semantic map for aliases
            canonical_id = lookup_alias(answer_clean)

        # 3. Check if the identified canonical_id is a child of the expected domain
        if canonical_id:
            descendants = get_all_descendants(expected_node_id)
            if canonical_id in descendants:
                return ValidationResult(
                    status=ValidationStatus.VALID,
                    canonical_id=canonical_id,
                    confidence=1.0,
                    reason="Answer matches a valid category in the domain."
                )
            else:
                # It's a valid business node, but NOT in the expected domain
                return ValidationResult(
                    status=ValidationStatus.INVALID,
                    reason=f"'{user_answer}' is a valid business, but does not belong to the {expected_node_id} domain.",
                    suggestions=self._get_suggestions(expected_node_id)
                )

        # 4. Not found in ontology or semantic map
        return ValidationResult(
            status=ValidationStatus.INVALID,
            reason=f"'{user_answer}' is not recognized as a valid option for this business type.",
            suggestions=self._get_suggestions(expected_node_id)
        )

    def _get_suggestions(self, node_id: str) -> List[str]:
        """Returns canonical names of children for suggestions."""
        from ..ontology.business_graph import BUSINESS_GRAPH
        children = [BUSINESS_GRAPH[nid].canonical_name for nid, node in BUSINESS_GRAPH.items() if node.parent_id == node_id]
        return children if children else ["Other"]

# Adding Enum since I missed it in the Write call
from enum import Enum
