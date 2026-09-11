from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import LearnedMapping, MemoryEntry, VerificationStatus, RegionalContext
from .store import MemoryStore
from .pipeline import LearningPipeline
from ..ontology.business_graph import BUSINESS_GRAPH

class MemoryManager:
    """
    Coordinates the layered memory system (L1-L4).
    """
    def __init__(self):
        self.store = MemoryStore()
        self.pipeline = LearningPipeline(self.store)

    def _validate_canonical(self, canonical: str) -> bool:
        """
        Ensures the suggested canonical meaning exists in the business ontology.
        """
        # Check if it's a key in the business graph
        if canonical in BUSINESS_GRAPH:
            return True

        # Also check if it matches any canonical_name (case-insensitive)
        for node in BUSINESS_GRAPH.values():
            if node.canonical_name.lower() == canonical.lower():
                return True
        return False

    def record_correction(self, user_id: str, session_id: str, phrase: str,
                           canonical: str, lang: str, region: RegionalContext, biz: str):
        """
        Records a correction across L1 and L2, and feeds the L3 pipeline.
        """
        if not self._validate_canonical(canonical):
            raise ValueError(f"Invalid canonical meaning '{canonical}'. Not found in ontology.")

        # L1: Session Memory
        if session_id not in self.store.session_memory:
            self.store.session_memory[session_id] = []
        self.store.session_memory[session_id].append(
            MemoryEntry(phrase=phrase, canonical_meaning=canonical)
        )

        # L2: User Memory
        if user_id not in self.store.user_memory:
            self.store.user_memory[user_id] = []
        self.store.user_memory[user_id].append(
            MemoryEntry(phrase=phrase, canonical_meaning=canonical)
        )

        # L3: Community Knowledge (via Pipeline)
        mapping = self.pipeline.process_correction(user_id, phrase, canonical, lang, region, biz)

        return mapping

    def resolve_phrase(self, phrase: str, lang: str, region: RegionalContext, biz: str,
                       user_id: Optional[str] = None, session_id: Optional[str] = None) -> Optional[str]:
        """
        Resolves a phrase using the Trust Pyramid (L4 -> L2 -> L1 -> L3).
        """
        phrase_lower = phrase.lower()

        # 1. L4: Curated Knowledge (Global Authority)
        key = self.store.generate_key(phrase, lang, region, biz)
        if key in self.store.curated_knowledge:
            return self.store.curated_knowledge[key].canonical_meaning

        # 2. L2: User Memory (Personal Preference)
        if user_id and user_id in self.store.user_memory:
            for entry in reversed(self.store.user_memory[user_id]):
                if entry.phrase.lower() == phrase_lower:
                    return entry.canonical_meaning

        # 3. L1: Session Memory (Immediate Correction)
        if session_id and session_id in self.store.session_memory:
            for entry in reversed(self.store.session_memory[session_id]):
                if entry.phrase.lower() == phrase_lower:
                    return entry.canonical_meaning

        # 4. L3: Community Knowledge (Pending Candidates)
        if key in self.store.community_knowledge:
            candidates = self.store.community_knowledge[key]
            # Return candidate with highest confidence above threshold (0.6)
            best_candidate = max(candidates, key=lambda m: m.confidence, default=None)
            if best_candidate and best_candidate.confidence >= 0.5 and best_candidate.verification_status != VerificationStatus.REJECTED:
                return best_candidate.canonical_meaning

        return None

    def promote_mapping(self, phrase: str, lang: str, region: RegionalContext, biz: str, status: VerificationStatus):
        """
        Admin action: Promote a mapping to L4 or explicitly reject it.
        """
        key = self.store.generate_key(phrase, lang, region, biz)
        if key not in self.store.community_knowledge:
            raise ValueError("Mapping not found in community knowledge.")

        candidates = self.store.community_knowledge[key]
        # Promote the best candidate or the first one if multiple exist
        best_candidate = max(candidates, key=lambda m: m.confidence, default=None)
        if not best_candidate:
            raise ValueError("No candidates found for this phrase.")

        best_candidate.verification_status = status
        best_candidate.updated_at = datetime.now()

        if status == VerificationStatus.VERIFIED:
            # Promote to L4
            self.store.curated_knowledge[key] = best_candidate
            self.store.log_event("MAPPING_PROMOTED", {"key": key, "phrase": phrase})
        elif status == VerificationStatus.REJECTED:
            self.store.log_event("MAPPING_REJECTED_ADMIN", {"key": key, "phrase": phrase})

        return best_candidate

    def get_community_stats(self) -> List[LearnedMapping]:
        """Returns all candidate mappings for admin review."""
        return list(self.store.community_knowledge.values())
