"""Build individual learning paths from resources within a domain."""

from __future__ import annotations

import hashlib
from collections import defaultdict

from ai_training_catalog.config import Settings
from ai_training_catalog.models.curriculum import LearningObjective, LearningPath, ModuleUnit
from ai_training_catalog.models.resource import DifficultyLevel, Resource, SkillDomain


# Pre-requisite relationships between domains
DEPENDENCY_MAP: dict[SkillDomain, list[SkillDomain]] = {
    SkillDomain.DEEP_LEARNING: [SkillDomain.ML_BASICS],
    SkillDomain.NLP: [SkillDomain.DEEP_LEARNING],
    SkillDomain.COMPUTER_VISION: [SkillDomain.DEEP_LEARNING],
    SkillDomain.MLOPS: [SkillDomain.ML_BASICS],
    SkillDomain.GENERATIVE_AI: [SkillDomain.DEEP_LEARNING, SkillDomain.NLP],
    SkillDomain.REINFORCEMENT_LEARNING: [SkillDomain.ML_BASICS],
    SkillDomain.AI_PROJECT_MANAGEMENT: [SkillDomain.AI_STRATEGY],
    SkillDomain.AI_ROI: [SkillDomain.AI_STRATEGY],
    SkillDomain.AI_GOVERNANCE: [SkillDomain.AI_ETHICS],
}

# Difficulty ordering
_DIFF_ORDER = {
    DifficultyLevel.BEGINNER: 0,
    DifficultyLevel.INTERMEDIATE: 1,
    DifficultyLevel.ADVANCED: 2,
}

# Audience descriptions by difficulty
_AUDIENCE = {
    DifficultyLevel.BEGINNER: "Newcomers with no prior experience in this domain",
    DifficultyLevel.INTERMEDIATE: "Practitioners with foundational knowledge seeking deeper skills",
    DifficultyLevel.ADVANCED: "Experienced professionals aiming for expert-level mastery",
}


def _path_id(domain: SkillDomain, difficulty: DifficultyLevel) -> str:
    raw = f"{domain.value}-{difficulty.value}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def _bloom_from_difficulty(difficulty: DifficultyLevel) -> str:
    return {
        DifficultyLevel.BEGINNER: "understand",
        DifficultyLevel.INTERMEDIATE: "apply",
        DifficultyLevel.ADVANCED: "evaluate",
    }[difficulty]


class LearningPathBuilder:
    """Build :class:`LearningPath` objects from a set of resources in one domain."""

    def __init__(self, settings: Settings) -> None:
        self._max_per_module = settings.max_resources_per_module
        self._max_hours_beginner = settings.max_hours_beginner_path
        self._diversity_cap = settings.provider_diversity_cap

    def build(self, domain: SkillDomain, resources: list[Resource]) -> list[LearningPath]:
        """Build one learning path per difficulty level that has resources."""
        by_diff: dict[DifficultyLevel, list[Resource]] = defaultdict(list)
        for r in resources:
            by_diff[r.difficulty].append(r)

        paths: list[LearningPath] = []
        for diff in (DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED):
            bucket = by_diff.get(diff, [])
            if not bucket:
                continue
            path = self._build_path(domain, diff, bucket)
            if path.modules:
                paths.append(path)
        return paths

    def _build_path(
        self, domain: SkillDomain, difficulty: DifficultyLevel, resources: list[Resource]
    ) -> LearningPath:
        # Sort by quality descending
        resources = sorted(resources, key=lambda r: r.quality_score, reverse=True)

        # Enforce provider diversity
        resources = self._apply_diversity(resources)

        # Select top N
        selected = resources[: self._max_per_module * 3]  # allow up to 3 modules

        # Split into modules of max_per_module resources
        modules: list[ModuleUnit] = []
        for i in range(0, len(selected), self._max_per_module):
            chunk = selected[i: i + self._max_per_module]
            module_order = len(modules) + 1
            module = ModuleUnit(
                title=f"Module {module_order}: {domain.value.replace('_', ' ').title()}",
                description=f"{difficulty.value.title()}-level resources — part {module_order}",
                resource_ids=[r.id for r in chunk],
                objectives=[
                    LearningObjective(
                        description=f"{_bloom_from_difficulty(difficulty).title()} {r.title}",
                        bloom_level=_bloom_from_difficulty(difficulty),
                    )
                    for r in chunk
                ],
                estimated_hours=sum(r.estimated_hours or 2.0 for r in chunk),
                order=module_order,
            )
            modules.append(module)

        # Cap beginner hours
        total_hours = sum(m.estimated_hours for m in modules)
        if difficulty == DifficultyLevel.BEGINNER and total_hours > self._max_hours_beginner:
            # Trim modules from the end
            trimmed: list[ModuleUnit] = []
            running = 0.0
            for m in modules:
                if running + m.estimated_hours <= self._max_hours_beginner:
                    trimmed.append(m)
                    running += m.estimated_hours
                else:
                    break
            modules = trimmed
            total_hours = sum(m.estimated_hours for m in modules)

        # Derive prerequisites from dependency map
        prereqs: list[str] = []
        for dep_domain in DEPENDENCY_MAP.get(domain, []):
            prereqs.append(f"Complete the {dep_domain.value.replace('_', ' ').title()} path")
        if difficulty == DifficultyLevel.INTERMEDIATE:
            prereqs.append(f"Complete the Beginner path for {domain.value.replace('_', ' ').title()}")
        elif difficulty == DifficultyLevel.ADVANCED:
            prereqs.append(f"Complete the Intermediate path for {domain.value.replace('_', ' ').title()}")

        return LearningPath(
            id=_path_id(domain, difficulty),
            title=f"{domain.value.replace('_', ' ').title()} — {difficulty.value.title()}",
            description=(
                f"A {difficulty.value}-level learning path covering "
                f"{domain.value.replace('_', ' ')} using curated free and open-source resources."
            ),
            target_audience=_AUDIENCE[difficulty],
            difficulty=difficulty,
            domains=[domain],
            modules=modules,
            total_estimated_hours=round(total_hours, 1),
            prerequisites=prereqs,
        )

    def _apply_diversity(self, resources: list[Resource]) -> list[Resource]:
        """Ensure no single provider exceeds the diversity cap."""
        from collections import Counter
        total = len(resources)
        if total == 0:
            return resources

        max_per_provider = max(1, int(total * self._diversity_cap))
        provider_counts: Counter[str] = Counter()
        result: list[Resource] = []
        deferred: list[Resource] = []

        for r in resources:
            p = r.provider or "unknown"
            if provider_counts[p] < max_per_provider:
                result.append(r)
                provider_counts[p] += 1
            else:
                deferred.append(r)

        # Append deferred at the end (lower priority but still available)
        return result + deferred
