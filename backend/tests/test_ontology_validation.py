import pytest
from backend.ontology.business_graph import BUSINESS_GRAPH
from backend.ontology.semantic_map import lookup_alias
from backend.validation.semantic_validator import SemanticValidator, ValidationStatus
from backend.validation.contradiction_engine import ContradictionEngine

def test_valid_answer():
    validator = SemanticValidator()
    # Valid child of POULTRY
    result = validator.validate_answer("POULTRY", "Broiler")
    assert result.status == ValidationStatus.VALID
    assert result.canonical_id == "BROILER"

def test_synonym_mapping():
    validator = SemanticValidator()
    # "desi chicken" -> COUNTRY_CHICKEN (Child of POULTRY)
    result = validator.validate_answer("POULTRY", "desi chicken")
    assert result.status == ValidationStatus.VALID
    assert result.canonical_id == "COUNTRY_CHICKEN"

def test_regional_term():
    validator = SemanticValidator()
    # "nati koli" -> COUNTRY_CHICKEN
    result = validator.validate_answer("POULTRY", "nati koli")
    assert result.status == ValidationStatus.VALID
    assert result.canonical_id == "COUNTRY_CHICKEN"

def test_typo_handling():
    validator = SemanticValidator()
    # Exact match usually fails on typos, but if it's a common typo, semantic map helps.
    # For now, we test that it rejects if not in map.
    result = validator.validate_answer("POULTRY", "Broilerrr")
    assert result.status == ValidationStatus.INVALID

def test_unrelated_answer():
    validator = SemanticValidator()
    # "coffee" in POULTRY domain
    result = validator.validate_answer("POULTRY", "coffee")
    assert result.status == ValidationStatus.INVALID
    assert "does not belong to the POULTRY domain" in result.reason or "not recognized" in result.reason

def test_ambiguous_answer():
    validator = SemanticValidator()
    # An answer that is valid but not a child of POULTRY
    result = validator.validate_answer("POULTRY", "Dairy")
    assert result.status == ValidationStatus.INVALID
    assert "valid business, but does not belong" in result.reason

def test_missing_answer():
    validator = SemanticValidator()
    result = validator.validate_answer("POULTRY", "")
    assert result.status == ValidationStatus.INVALID
    assert "missing" in result.reason

def test_contradictory_answers():
    engine = ContradictionEngine()
    # Broiler cannot have high egg production
    attrs = {"egg_production_target": "High"}
    result = engine.check_contradictions("BROILER", attrs)
    assert result.has_contradictions is True
    assert result.contradictions[0].attribute == "egg_production_target"

def test_low_confidence_scenario():
    # This would typically test the Normalizer agent.
    # Since Normalizer needs API keys, we test the deterministic part here.
    validator = SemanticValidator()
    result = validator.validate_answer("POULTRY", "Something weird")
    assert result.status == ValidationStatus.INVALID
    assert len(result.suggestions) > 0
