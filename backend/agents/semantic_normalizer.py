from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from openai import OpenAI
from ..config import settings
from ..ontology.business_graph import BUSINESS_GRAPH, get_node_by_canonical_name
from ..ontology.semantic_map import lookup_alias

class NormalizationResult(BaseModel):
    canonical_id: Optional[str] = None
    confidence: float = 0.0
    mapping_type: str = "NONE" # EXACT, ALIAS, FUZZY, INCOMPATIBLE
    reason: str = ""

class SemanticNormalizer:
    """LLM-powered agent that maps natural language to canonical ontology terms."""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )
        self.model = settings.llm_model

    def normalize(self, user_input: str, expected_node_id: str) -> NormalizationResult:
        """
        Uses LLM to interpret user input and map it to a canonical business term.
        """
        from .ontology.business_graph import get_children_of
        allowed_values = [BUSINESS_GRAPH[cid].canonical_name for cid in get_children_of(expected_node_id)]

        # If no children, the node might be a leaf or a sector, allow a broader set
        if not allowed_values:
            allowed_values = ["Other"]

        prompt = (
            f"You are a Semantic Normalization Expert for GramNirnay.ai. "
            f"The user is answering a question about a business in the domain: {expected_node_id}. "
            f"The expected valid options for this domain are: {allowed_values}. "
            f"User Input: '{user_input}'. "
            "\n\n"
            "Your task: Map the user input to one of the allowed options or mark it as 'Other' "
            "if it is a valid business but doesn't fit the list. "
            "Return ONLY a JSON object with keys: 'canonical_name', 'confidence' (0.0-1.0), "
            "'mapping_type' (EXACT, ALIAS, FUZZY, or INCOMPATIBLE), and 'reason'."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            res_data = json.loads(response.choices[0].message.content)

            canonical_name = res_data.get("canonical_name")
            confidence = res_data.get("confidence", 0.0)
            mapping_type = res_data.get("mapping_type", "NONE")
            reason = res_data.get("reason", "")

            # Deterministic Verification:
            # Check if the LLM proposed a name that actually exists in the graph
            node = get_node_by_canonical_name(canonical_name)
            if node:
                return NormalizationResult(
                    canonical_id=node.id,
                    confidence=confidence,
                    mapping_type=mapping_type,
                    reason=reason
                )

            return NormalizationResult(
                canonical_id=None,
                confidence=0.0,
                mapping_type="INCOMPATIBLE",
                reason=f"LLM proposed '{canonical_name}', but it is not in the ontology."
            )

        except Exception as e:
            return NormalizationResult(
                canonical_id=None,
                confidence=0.0,
                mapping_type="ERROR",
                reason=str(e)
            )

import json
