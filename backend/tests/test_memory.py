import pytest
from backend.memory.manager import MemoryManager
from backend.memory.models import RegionalContext, VerificationStatus

@pytest.fixture
def memory_manager():
    return MemoryManager()

def test_repeated_corrections(memory_manager):
    # Same user correcting the same term multiple times
    user_id = "user_1"
    session_id = "sess_1"
    region = RegionalContext(state="Karnataka", district="Bangalore")

    memory_manager.record_correction(user_id, session_id, "nati koli", "COUNTRY_CHICKEN", "kn-IN", region, "POULTRY")
    memory_manager.record_correction(user_id, session_id, "nati koli", "COUNTRY_CHICKEN", "kn-IN", region, "POULTRY")

    candidates = memory_manager.store.community_knowledge[memory_manager.store.generate_key("nati koli", "kn-IN", region, "POULTRY")]
    mapping = candidates[0]
    # Should only count as 1 evidence point (unique user)
    assert mapping.evidence_count == 1

def test_conflicting_corrections(memory_manager):
    # Different users suggesting different meanings for the same phrase
    region = RegionalContext(state="Karnataka", district="Bangalore")

    memory_manager.record_correction("user_1", "s1", "desi murgi", "COUNTRY_CHICKEN", "hi-IN", region, "POULTRY")
    memory_manager.record_correction("user_2", "s2", "desi murgi", "BROILER", "hi-IN", region, "POULTRY")

    # They are different candidates for the same phrase
    key = memory_manager.store.generate_key("desi murgi", "hi-IN", region, "POULTRY")
    assert len(memory_manager.store.community_knowledge[key]) == 2

def test_high_evidence_promotion(memory_manager):
    region = RegionalContext(state="Karnataka", district="Bangalore")
    phrase = "rural farm"
    canonical = "AGRI"

    # Simulate 5 different users
    for i in range(5):
        memory_manager.record_correction(f"user_{i}", f"s{i}", phrase, canonical, "en-IN", region, "GENERAL")

    key = memory_manager.store.generate_key(phrase, "en-IN", region, "GENERAL")
    candidates = memory_manager.store.community_knowledge[key]
    mapping = candidates[0]

    assert mapping.evidence_count == 5
    assert mapping.confidence > 0.5

def test_regional_mappings(memory_manager):
    # Same phrase, different meaning in different regions
    phrase = "koli"
    canonical_1 = "POULTRY"
    canonical_2 = "TRADING"

    region_1 = RegionalContext(state="Maharashtra", district="Mumbai")
    region_2 = RegionalContext(state="Karnataka", district="Mangalore")

    memory_manager.record_correction("u1", "s1", phrase, canonical_1, "mr-IN", region_1, "GENERAL")
    memory_manager.record_correction("u2", "s2", phrase, canonical_2, "kn-IN", region_2, "GENERAL")

    res_1 = memory_manager.resolve_phrase(phrase, "mr-IN", region_1, "GENERAL")
    res_2 = memory_manager.resolve_phrase(phrase, "kn-IN", region_2, "GENERAL")

    assert res_1 == canonical_1
    assert res_2 == canonical_2

def test_malicious_invalid_mapping(memory_manager):
    region = RegionalContext(state="Karnataka")
    # Try to map to a non-existent ontology ID
    with pytest.raises(ValueError, match="Invalid canonical meaning"):
        memory_manager.record_correction("u1", "s1", "bad phrase", "NON_EXISTENT_ID", "en-IN", region, "GENERAL")

def test_rejected_mapping(memory_manager):
    region = RegionalContext(state="Karnataka")
    phrase = "test phrase"
    canonical = "COUNTRY_CHICKEN"

    memory_manager.record_correction("u1", "s1", phrase, canonical, "en-IN", region, "GENERAL")
    key = memory_manager.store.generate_key(phrase, "en-IN", region, "GENERAL")

    memory_manager.promote_mapping(phrase, "en-IN", region, "GENERAL", VerificationStatus.REJECTED)

    # Should not resolve now
    res = memory_manager.resolve_phrase(phrase, "en-IN", region, "GENERAL")
    assert res is None
