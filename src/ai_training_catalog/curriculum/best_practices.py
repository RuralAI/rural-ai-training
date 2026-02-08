"""Best-practices validation and enhancement engine for curricula."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ai_training_catalog.models.curriculum import Curriculum, LearningPath
from ai_training_catalog.models.resource import (
    ContentType,
    DifficultyLevel,
    Resource,
    SkillCategory,
    SkillDomain,
    DOMAIN_CATEGORY,
)


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ValidationIssue:
    """A single validation finding."""
    path_id: str
    rule: str
    severity: Severity
    message: str


@dataclass
class ValidationReport:
    """Aggregated validation results."""
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)


class BestPracticesEngine:
    """Validate and enhance a :class:`Curriculum` against training best practices.

    Rules
    -----
    1. Every path should include at least one hands-on resource (notebook/exercise).
    2. Beginner paths must not exceed 20 hours.
    3. Advanced paths should include at least one research paper.
    4. Business-skill paths should include case-study or strategy content.
    5. Every path must declare prerequisites.
    6. No single provider should represent >40% of a path's resources.
    7. Each module should have at least one learning objective.
    """

    def __init__(
        self,
        resources_by_id: dict[str, Resource] | None = None,
        max_beginner_hours: float = 20.0,
        diversity_cap: float = 0.4,
    ) -> None:
        self._resources = resources_by_id or {}
        self._max_beginner = max_beginner_hours
        self._diversity_cap = diversity_cap

    def _get_path_resources(self, path: LearningPath) -> list[Resource]:
        rids = []
        for mod in path.modules:
            rids.extend(mod.resource_ids)
        return [self._resources[rid] for rid in rids if rid in self._resources]

    def validate(self, curriculum: Curriculum) -> ValidationReport:
        """Run all validation rules against *curriculum*."""
        report = ValidationReport()

        for path in curriculum.learning_paths:
            resources = self._get_path_resources(path)
            content_types = {r.content_type for r in resources}
            providers = [r.provider for r in resources if r.provider]

            # Rule 1: hands-on content
            hands_on = {ContentType.INTERACTIVE_NOTEBOOK, ContentType.COURSE}
            if not content_types & hands_on:
                report.issues.append(ValidationIssue(
                    path_id=path.id,
                    rule="hands_on_required",
                    severity=Severity.WARNING,
                    message=f"Path '{path.title}' has no hands-on resources (notebooks or interactive courses).",
                ))

            # Rule 2: beginner hour cap
            if path.difficulty == DifficultyLevel.BEGINNER and path.total_estimated_hours > self._max_beginner:
                report.issues.append(ValidationIssue(
                    path_id=path.id,
                    rule="beginner_hour_cap",
                    severity=Severity.WARNING,
                    message=(
                        f"Beginner path '{path.title}' is {path.total_estimated_hours}h, "
                        f"exceeding the recommended {self._max_beginner}h cap."
                    ),
                ))

            # Rule 3: advanced paths need a paper
            if path.difficulty == DifficultyLevel.ADVANCED and ContentType.PAPER not in content_types:
                report.issues.append(ValidationIssue(
                    path_id=path.id,
                    rule="advanced_needs_paper",
                    severity=Severity.INFO,
                    message=f"Advanced path '{path.title}' has no research papers — consider adding one.",
                ))

            # Rule 4: business paths need case studies
            for domain in path.domains:
                if DOMAIN_CATEGORY.get(domain) == SkillCategory.BUSINESS:
                    has_strategy = any(
                        "case study" in (r.description + " ".join(r.tags)).lower()
                        or "strategy" in (r.description + " ".join(r.tags)).lower()
                        for r in resources
                    )
                    if not has_strategy:
                        report.issues.append(ValidationIssue(
                            path_id=path.id,
                            rule="business_needs_cases",
                            severity=Severity.INFO,
                            message=f"Business path '{path.title}' could benefit from case-study content.",
                        ))
                    break  # only check once per path

            # Rule 5: prerequisites declared
            if not path.prerequisites and path.difficulty != DifficultyLevel.BEGINNER:
                report.issues.append(ValidationIssue(
                    path_id=path.id,
                    rule="prerequisites_required",
                    severity=Severity.WARNING,
                    message=f"Non-beginner path '{path.title}' has no prerequisites listed.",
                ))

            # Rule 6: provider diversity
            if providers:
                from collections import Counter
                counts = Counter(providers)
                total = len(providers)
                for prov, cnt in counts.items():
                    if cnt / total > self._diversity_cap:
                        report.issues.append(ValidationIssue(
                            path_id=path.id,
                            rule="provider_diversity",
                            severity=Severity.WARNING,
                            message=(
                                f"Provider '{prov}' represents {cnt}/{total} "
                                f"({cnt/total:.0%}) of path '{path.title}' — "
                                f"cap is {self._diversity_cap:.0%}."
                            ),
                        ))

            # Rule 7: objectives per module
            for mod in path.modules:
                if not mod.objectives:
                    report.issues.append(ValidationIssue(
                        path_id=path.id,
                        rule="module_objectives",
                        severity=Severity.INFO,
                        message=f"Module '{mod.title}' in path '{path.title}' has no learning objectives.",
                    ))

        return report
