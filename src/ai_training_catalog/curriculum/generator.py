"""Top-level curriculum generator: transforms the resource catalog into structured training programmes."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from datetime import datetime, timezone

from ai_training_catalog.config import Settings
from ai_training_catalog.discovery.catalog import ResourceCatalog
from ai_training_catalog.models.curriculum import Curriculum
from ai_training_catalog.models.resource import Resource, SkillCategory, SkillDomain, DOMAIN_CATEGORY
from ai_training_catalog.storage.repository import CurriculumRepository
from ai_training_catalog.utils.logging import log

from .best_practices import BestPracticesEngine, ValidationReport
from .learning_path import LearningPathBuilder


class CurriculumGenerator:
    """Generate best-practices training curricula from the resource catalog.

    Process
    -------
    1. Load all active resources above the quality threshold.
    2. Group resources by primary domain.
    3. For each domain, build learning paths (beginner → advanced).
    4. Validate the assembled curriculum against best-practice rules.
    5. Persist the curriculum to storage.
    """

    def __init__(
        self,
        settings: Settings,
        catalog: ResourceCatalog,
        path_builder: LearningPathBuilder | None = None,
        curriculum_repo: CurriculumRepository | None = None,
    ) -> None:
        self._settings = settings
        self._catalog = catalog
        self._path_builder = path_builder or LearningPathBuilder(settings)
        self._repo = curriculum_repo

    async def generate(
        self,
        target_domains: list[SkillDomain] | None = None,
        title: str | None = None,
    ) -> tuple[Curriculum, ValidationReport]:
        """Generate a curriculum covering *target_domains* (all if ``None``).

        Returns
        -------
        curriculum:
            The generated curriculum.
        report:
            Best-practices validation report.
        """
        resources = await self._catalog.get_all(min_score=self._settings.min_quality_score)
        resources = [r for r in resources if r.is_active]

        if target_domains:
            resources = [
                r for r in resources
                if any(d in target_domains for d in r.domains)
            ]

        log.info("Generating curriculum from %d resources", len(resources))

        # Group by primary domain (first in list)
        by_domain: dict[SkillDomain, list[Resource]] = defaultdict(list)
        for r in resources:
            if r.domains:
                by_domain[r.domains[0]].append(r)

        # Build learning paths for each domain
        all_paths = []
        for domain in sorted(by_domain.keys(), key=lambda d: d.value):
            if target_domains and domain not in target_domains:
                continue
            domain_resources = by_domain[domain]
            paths = self._path_builder.build(domain, domain_resources)
            all_paths.extend(paths)
            log.info("  %s: %d paths from %d resources", domain.value, len(paths), len(domain_resources))

        # Determine title
        if not title:
            if target_domains:
                categories = {DOMAIN_CATEGORY.get(d, SkillCategory.TECHNICAL) for d in target_domains}
                cat_label = " & ".join(sorted(c.value.title() for c in categories))
                title = f"AI {cat_label} Best Practices Curriculum"
            else:
                title = "Comprehensive AI Best Practices Curriculum"

        catalog_hash = await self._catalog.catalog_hash()
        curriculum_id = hashlib.sha256(
            f"{title}-{catalog_hash}".encode()
        ).hexdigest()[:12]

        curriculum = Curriculum(
            id=curriculum_id,
            title=title,
            description=(
                f"Auto-generated curriculum with {len(all_paths)} learning paths "
                f"covering {len(by_domain)} skill domains, built from "
                f"{len(resources)} curated free and open-source resources."
            ),
            learning_paths=all_paths,
            generated_at=datetime.now(timezone.utc),
            source_catalog_hash=catalog_hash,
            metadata={
                "domains_covered": [d.value for d in sorted(by_domain.keys(), key=lambda d: d.value)],
                "total_resources": len(resources),
                "total_paths": len(all_paths),
            },
        )

        # Validate
        resources_by_id = {r.id: r for r in resources}
        engine = BestPracticesEngine(
            resources_by_id=resources_by_id,
            max_beginner_hours=self._settings.max_hours_beginner_path,
            diversity_cap=self._settings.provider_diversity_cap,
        )
        validation = engine.validate(curriculum)

        if validation.error_count:
            log.warning("Curriculum has %d errors and %d warnings",
                        validation.error_count, validation.warning_count)
        elif validation.warning_count:
            log.info("Curriculum has %d warnings", validation.warning_count)

        # Persist
        if self._repo:
            path = await self._repo.save(curriculum)
            log.info("Curriculum saved to %s", path)

        return curriculum, validation
