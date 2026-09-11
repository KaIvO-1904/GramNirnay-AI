from typing import Dict, Any, List
from ..ontology.models import BusinessProfile, FinancialParams, ValidationResult, ValidationStatus

class ValidationEngine:
    """Deterministic business rule validation."""

    @staticmethod
    def validate_profile(profile: BusinessProfile) -> ValidationResult:
        errors = []
        warnings = []

        if not profile.business_idea or len(profile.business_idea) < 5:
            errors.append("Business idea is too short or missing.")

        if profile.available_capital < 0:
            errors.append("Available capital cannot be negative.")

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
