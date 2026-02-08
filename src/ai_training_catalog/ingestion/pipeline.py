"""Ingestion pipeline: scrape, deduplicate, and categorise discovered resources."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from ai_training_catalog.config import Settings
from ai_training_catalog.discovery.catalog import ResourceCatalog
from ai_training_catalog.models.resource import Resource
from ai_training_catalog.utils.logging import log

from .categorizer import ContentCategorizer
from .deduplicator import ContentDeduplicator
from .scrapers.base import BaseScraper, ScrapedContent


@dataclass
class IngestionReport:
    """Summary of an ingestion run."""
    total_resources: int = 0
    scraped: int = 0
    failed: int = 0
    duplicate_groups: int = 0
    duplicates_flagged: int = 0
    recategorized: int = 0
    errors: list[str] = field(default_factory=list)


class IngestionPipeline:
    """Orchestrate content ingestion for catalogued resources.

    Stages
    ------
    1. Select resources to ingest (all or by ID).
    2. Scrape full content using the appropriate scraper.
    3. Detect near-duplicate content.
    4. Refine domain/tag categorisation with full text.
    5. Update the catalog with enriched metadata.
    """

    def __init__(
        self,
        settings: Settings,
        catalog: ResourceCatalog,
        scrapers: list[BaseScraper],
        deduplicator: ContentDeduplicator | None = None,
        categorizer: ContentCategorizer | None = None,
    ) -> None:
        self._settings = settings
        self._catalog = catalog
        self._scrapers = scrapers
        self._dedup = deduplicator or ContentDeduplicator()
        self._categorizer = categorizer or ContentCategorizer()

    def _pick_scraper(self, resource: Resource) -> BaseScraper | None:
        for s in self._scrapers:
            if s.can_handle(resource):
                return s
        return None

    async def _scrape_one(self, resource: Resource) -> ScrapedContent | None:
        scraper = self._pick_scraper(resource)
        if scraper is None:
            log.warning("No scraper available for %s (%s)", resource.url, resource.content_type)
            return None
        return await scraper.scrape(resource)

    async def run(
        self,
        resource_ids: list[str] | None = None,
        min_score: float = 0.0,
    ) -> IngestionReport:
        """Run the ingestion pipeline.

        Parameters
        ----------
        resource_ids:
            Specific resources to ingest. ``None`` means all above *min_score*.
        min_score:
            Minimum quality score for automatic selection.
        """
        all_resources = await self._catalog.get_all(min_score=min_score)
        if resource_ids:
            all_resources = [r for r in all_resources if r.id in set(resource_ids)]

        report = IngestionReport(total_resources=len(all_resources))
        log.info("Ingestion starting for %d resources", len(all_resources))

        # Stage 1: Scrape concurrently
        tasks = [self._scrape_one(r) for r in all_resources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        contents: list[ScrapedContent] = []
        resource_map: dict[str, Resource] = {r.id: r for r in all_resources}

        for res in results:
            if isinstance(res, Exception):
                report.failed += 1
                report.errors.append(str(res))
            elif res is None:
                report.failed += 1
            else:
                contents.append(res)
                report.scraped += 1

        log.info("Scraped %d / %d resources", report.scraped, report.total_resources)

        # Stage 2: Deduplicate
        dup_groups = self._dedup.find_duplicates(contents)
        report.duplicate_groups = len(dup_groups)
        flagged_ids: set[str] = set()
        for group in dup_groups:
            for dup_id in group.duplicate_ids:
                flagged_ids.add(dup_id)
                report.duplicates_flagged += 1
        if flagged_ids:
            log.info("Flagged %d resources as duplicates in %d groups",
                     report.duplicates_flagged, report.duplicate_groups)

        # Stage 3: Categorise and update catalog
        for content in contents:
            if content.resource_id in flagged_ids:
                # Mark duplicate resources as inactive
                resource = resource_map.get(content.resource_id)
                if resource:
                    resource.is_active = False
                    await self._catalog.upsert(resource)
                continue

            cat_result = self._categorizer.categorize(content)
            resource = resource_map.get(content.resource_id)
            if resource is None:
                continue

            # Enrich the resource with categorisation data
            if cat_result.primary_domain:
                if cat_result.primary_domain not in resource.domains:
                    resource.domains.insert(0, cat_result.primary_domain)
                for sd in cat_result.secondary_domains:
                    if sd not in resource.domains:
                        resource.domains.append(sd)
            if cat_result.tags:
                resource.tags = list(set(resource.tags + cat_result.tags))

            # Estimate hours from word count (rough: 200 words/min reading + 2x for exercises)
            if content.word_count > 0 and resource.estimated_hours is None:
                reading_hours = content.word_count / (200 * 60)
                resource.estimated_hours = round(reading_hours * 2, 1)

            await self._catalog.upsert(resource)
            report.recategorized += 1

        log.info("Ingestion complete: %d recategorised, %d duplicates flagged",
                 report.recategorized, report.duplicates_flagged)
        return report
