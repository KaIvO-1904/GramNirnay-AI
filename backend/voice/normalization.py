from typing import List, Dict, Optional, Any
from .models import NormalizedTranscript
from ..ontology.semantic_map import lookup_alias
from ..memory.manager import MemoryManager

# Global instance for the memory manager
memory_manager = MemoryManager()

class NormalizationService:
    """
    Bridges the gap between rural speech and the business ontology.
    Maps colloquial/regional terms to canonical IDs.
    """

    def __init__(self):
        pass

    def normalize(self, text: str, lang: str = "en-IN", region: Optional[Dict[str, Any]] = None,
                      biz_context: Optional[str] = None, user_id: Optional[str] = None,
                      session_id: Optional[str] = None) -> NormalizedTranscript:
        """
        Processes the raw transcript, applying semantic mappings and noise reduction.
        """
        if not text:
            return NormalizedTranscript(
                original_text="",
                final_text="",
                mappings_applied=[],
                confidence_score=0.0
            )

        original_text = text
        normalized_text = text.lower().strip()
        mappings = []

        # Simple noise reduction: remove common STT fillers
        fillers = ["uh", "um", "like", "basically", "actually"]
        words = normalized_text.split()
        filtered_words = [w for w in words if w not in fillers]
        normalized_text = " ".join(filtered_words)

        # Setup region context for memory resolution
        from ..memory.models import RegionalContext # avoid circular import
        region_ctx = RegionalContext(
            state=region.get("state", "Unknown") if region else "Unknown",
            district=region.get("district") if region else None
        )

        i = 0
        final_words = []
        while i < len(words):
            matched = False
            # Try windows of 3, then 2, then 1
            for window_size in [3, 2, 1]:
                if i + window_size <= len(words):
                    phrase = " ".join(words[i : i + window_size])

                    # 1. Check Layered Memory first (Personal/Session/Community)
                    resolved = memory_manager.resolve_phrase(
                        phrase=phrase,
                        lang=lang,
                        region=region_ctx,
                        biz=biz_context or "GENERAL",
                        user_id=user_id,
                        session_id=session_id
                    )

                    if resolved:
                        final_words.append(resolved)
                        mappings.append({"from": phrase, "to": resolved})
                        i += window_size
                        matched = True
                        break

                    # 2. Fallback to Static Semantic Map (The Core L4 Ontology)
                    canonical_id = lookup_alias(phrase)
                    if canonical_id:
                        final_words.append(canonical_id)
                        mappings.append({"from": phrase, "to": canonical_id})
                        i += window_size
                        matched = True
                        break

            if not matched:
                final_words.append(words[i])
                i += 1

        final_text = " ".join(final_words)

        # Confidence is higher if mappings were found and the text isn't too short
        conf = 0.7
        if mappings:
            conf += 0.2
        if len(words) < 3:
            conf -= 0.3

        return NormalizedTranscript(
            original_text=original_text,
            final_text=final_text,
            mappings_applied=mappings,
            confidence_score=min(1.0, conf)
        )
