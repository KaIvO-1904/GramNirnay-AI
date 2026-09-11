from typing import List, Dict, Optional, Any
from datetime import datetime
from .models import LearnedMapping, MemoryEntry, VerificationStatus, RegionalContext

class MemoryStore:
    """
    In-memory persistence for the layered memory system.
    In production, this would be backed by a database (e.g., PostgreSQL + pgvector).
    """
    def __init__(self):
        # L1: Session Memory {session_id: [MemoryEntry]}
        self.session_memory: Dict[str, List[MemoryEntry]] = {}

        # L2: User Memory {user_id: [MemoryEntry]}
        self.user_memory: Dict[str, List[MemoryEntry]] = {}

        # L3: Community Knowledge {phrase_key: List[LearnedMapping]}
        # phrase_key = hash(phrase + language + region + business_context)
        self.community_knowledge: Dict[str, List[LearnedMapping]] = {}

        # L4: Curated Knowledge {phrase_key: LearnedMapping}
        self.curated_knowledge: Dict[str, LearnedMapping] = {}

        # Learning Audit Log
        self.audit_log: List[Dict[str, Any]] = []

    def generate_key(self, phrase: str, lang: str, region: RegionalContext, biz: str) -> str:
        district = region.district or "all"
        return f"{phrase.lower()}|{lang}|{region.state}|{district}|{biz}"

    def log_event(self, event_type: str, details: Dict[str, Any]):
        self.audit_log.append({
            "timestamp": datetime.now(),
            "event": event_type,
            **details
        })
