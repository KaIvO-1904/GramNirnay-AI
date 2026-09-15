from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from ..intelligence.client import ai_client
from ..structured_output import StructuredOutputHandler
from ..ontology.models import NormalizationJSON, BUSINESS_GRAPH, get_node_by_canonical_name
from ..ontology.semantic_map import lookup_alias
import json

class NormalizationResult(BaseModel):
    canonical_id: Optional[str] = None
    confidence: float = 0.0
    mapping_type: str = "NONE" # EXACT, ALIAS, FUZZY, INCOMPATIBLE
    reason: str = ""

class SemanticNormalizer:
    """LLM-powered agent that maps natural language to canonical ontology terms."""

    def __init__(self):
        self.client = ai_client.client
        self.model = ai_client.model

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

        def call_llm():
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return resp.choices[0].message.content

        def retry_llm(failed_output):
            retry_prompt = (
                f"The previous JSON output was malformed. Please fix the JSON escaping and return ONLY the corrected JSON object. "
                f"MALFORMED OUTPUT: {failed_output}"
            )
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": retry_prompt}],
                response_format={"type": "json_object"}
            )
            return resp.choices[0].message.content

        res = StructuredOutputHandler.execute_with_retry(
            llm_call_fn=call_llm,
            schema=NormalizationJSON,
            operation_name="semantic_normalization",
            model_name=self.model,
            retry_fn=retry_llm
        )

        if res:
            canonical_name = res.canonical_name
            confidence = res.confidence
            mapping_type = res.mapping_type
            reason = res.reason

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

        return NormalizationResult(
            canonical_id=None,
            confidence=0.0,
            mapping_type="ERROR",
            reason="LLM failed to produce a valid JSON response after retries."
        )
