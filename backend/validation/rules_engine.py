from typing import Dict, Any, List, Set
from ..ontology.models import BusinessProfile, FinancialParams, ValidationResult, ValidationStatus
import re

# Deterministic mappings for domain validation
SECTOR_KEYWORDS = {
    "LIVESTOCK": ["chicken", "poultry", "cow", "dairy", "goat", "sheep", "eggs", "milk", "livestock"],
    "SERVICES": ["tailoring", "stitching", "clothing", "garments", "salon", "repair", "textile"],
    "AGRI": ["farming", "crops", "vegetables", "organic", "plantation", "agriculture"],
    "MANUFACTURING": ["factory", "production", "manufacturing", "tools", "industrial"],
}

INCOMPATIBLE_SECTORS = [
    {"LIVESTOCK", "SERVICES"}, # e.g., Poultry + Tailoring
    {"LIVESTOCK", "MANUFACTURING"}, # e.g., Dairy + Industrial Tools
]

class ValidationEngine:
    """Deterministic business rule validation."""

    @staticmethod
    def check_domain_contradictions(idea: str) -> List[str]:
        """Detects incompatible business domains within a single idea."""
        idea_lower = idea.lower()
        found_sectors = set()

        for sector, keywords in SECTOR_KEYWORDS.items():
            if any(kw in idea_lower for kw in keywords):
                found_sectors.add(sector)

        errors = []
        for incompatible_set in INCOMPATIBLE_SECTORS:
            if incompatible_set.issubset(found_sectors):
                sectors_str = " & ".join(incompatible_set)
                errors.append(f"Domain contradiction detected: Idea combines incompatible sectors ({sectors_str}).")

        return errors

    @staticmethod
    def validate_profile(profile: BusinessProfile) -> ValidationResult:
        errors = []
        warnings = []

        if not profile.business_idea or len(profile.business_idea) < 5:
            errors.append("Business idea is too short or missing.")

        if profile.available_capital < 0:
            errors.append("Available capital cannot be negative.")

        # Business Domain Validation
        domain_errors = ValidationEngine.check_domain_contradictions(profile.business_idea)
        errors.extend(domain_errors)

        status = ValidationStatus.VALID if not errors else ValidationStatus.INVALID
        if not errors and warnings:
            status = ValidationStatus.WARNING

        return ValidationResult(
            status=status,
            errors=errors,
            warnings=warnings
        )

    @staticmethod
    def validate_financials(params: FinancialParams) -> ValidationResult:
        errors = []
        warnings = []

        if params.setup_cost <= 0:
            errors.append("Setup cost must be greater than zero.")

        if params.monthly_expenses < 0:
            errors.append("Monthly expenses cannot be negative.")

        if params.interest_rate < 0 or params.interest_rate > 50:
            warnings.append("Interest rate is unusual (outside 0-50% range).")

        status = ValidationStatus.VALID if not errors else ValidationStatus.INVALID
        if not errors and warnings:
            status = ValidationStatus.WARNING

        return ValidationResult(
            status=status,
            errors=errors,
            warnings=warnings
        )
