from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import LearnedMapping, MemoryEntry, VerificationStatus, RegionalContext
from .store import MemoryStore

class LearningPipeline:
    """
    Implements the logic for promoting corrections to authoritative knowledge.
    """
    def __init__(self, store: MemoryStore):
        self.store = store

    def calculate_confidence(self, mapping: LearnedMapping) -> float:
        """
        Confidence = (Evidence - Corrections) / (Evidence + 1)
        """
        score = (mapping.evidence_count - mapping.correction_count) / (mapping.evidence_count + 1)
        return max(0.0, min(1.0, score))

    def process_correction(self, user_id: str, phrase: str, canonical: str,
                           lang: str, region: RegionalContext, biz: str):
        """
        The core learning pipeline:
        Correction -> Candidate -> Evidence -> Confidence
        """
        key = self.store.generate_key(phrase, lang, region, biz)

        # 1. Evidence Aggregation
        if key in self.store.community_knowledge:
            candidates = self.store.community_knowledge[key]
            # Find if this specific canonical meaning already exists as a candidate
            existing = next((m for m in candidates if m.canonical_meaning == canonical), None)
            if existing:
                if user_id not in existing.source_users:
                    existing.evidence_count += 1
                    existing.source_users.append(user_id)
                mapping = existing
            else:
                # Create new candidate for this phrase
                mapping = LearnedMapping(
                    phrase=phrase,
                    canonical_meaning=canonical,
                    language=lang,
                    regional_context=region,
                    business_context=biz,
                    evidence_count=1,
                    source_users=[user_id],
                    verification_status=VerificationStatus.PENDING
                )
                candidates.append(mapping)
        else:
            # Initialize candidate list for this phrase
            mapping = LearnedMapping(
                phrase=phrase,
                canonical_meaning=canonical,
                language=lang,
                regional_context=region,
                business_context=biz,
                evidence_count=1,
                source_users=[user_id],
                verification_status=VerificationStatus.PENDING
            )
            self.store.community_knowledge[key] = [mapping]

        # 2. Confidence Scoring
        mapping.confidence = self.calculate_confidence(mapping)
        mapping.updated_at = datetime.now()

        self.store.log_event("CORRECTION_PROCESSED", {
            "user_id": user_id,
            "phrase": phrase,
            "canonical": canonical,
            "new_confidence": mapping.confidence
        })

        return mapping

    def process_rejection(self, user_id: str, phrase: str, lang: str,
                          region: RegionalContext, biz: str):
        """
        Increments correction count when a user rejects a suggested mapping.
        """
        key = self.store.generate_key(phrase, lang, region, biz)
        if key in self.store.community_knowledge:
            mapping = self.store.community_knowledge[key]
            mapping.correction_count += 1
            mapping.confidence = self.calculate_confidence(mapping)
            mapping.updated_at = datetime.now()

            self.store.log_event("MAPPING_REJECTED", {
                "user_id": user_id,
                "phrase": phrase,
                "new_confidence": mapping.confidence
            })
            return mapping
        return None
