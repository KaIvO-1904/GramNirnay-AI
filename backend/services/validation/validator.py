from ...services.base_service import BaseService
from ...core.schemas.domain import VentureProfile
from ...core.schemas.validation import ValidationResult, ValidationIssue
from typing import List

class ValidationService(BaseService[ValidationResult]):
    """
    Deterministic service for semantic validation and contradiction detection.
    """

    def execute(self, profile: VentureProfile) -> ValidationResult:
        """
        Validate the venture profile for contradictions.
        """
        issues = []
        contradictions = []

        # Rule 1: Experience vs Age (Hypothetical - since age isn't in profile, we check experience vs target capital)
        if profile.experience > 50:
            issues.append(ValidationIssue(
                field="experience",
                message="Experience exceeds reasonable career length.",
                severity="Warning",
                suggestion="Please verify the years of experience."
            ))

        # Rule 2: Capital sanity check
        if profile.available_capital < 0:
            contradictions.append("Available capital cannot be negative.")
            issues.append(ValidationIssue(
                field="availableCapital",
                message="Negative capital provided.",
                severity="Error"
            ))

        # Rule 3: Target investment sanity
        if profile.target_investment < profile.available_capital:
            issues.append(ValidationIssue(
                field="targetInvestment",
                message="Target investment is lower than already available capital.",
                severity="Warning",
                suggestion="Ensure target investment includes the total project cost."
            ))

        is_valid = len([i for i in issues if i.severity == "Error"]) == 0

        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            contradictions=contradictions,
            confidence_score=1.0 # Deterministic
        )
