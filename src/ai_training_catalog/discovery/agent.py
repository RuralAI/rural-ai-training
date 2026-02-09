"""Discovery agent: orchestrates search, evaluation, and cataloguing."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from ai_training_catalog.config import Settings
from ai_training_catalog.models.resource import SkillDomain
from ai_training_catalog.models.taxonomy import TAXONOMY
from ai_training_catalog.utils.logging import log

from .catalog import ResourceCatalog
from .evaluator import ResourceEvaluator
from .searchers.base import BaseSearcher, SearchResult


@dataclass
class DiscoveryReport:
    """Summary of a discovery run."""
    queries_executed: int = 0
    raw_results: int = 0
    new_resources: int = 0
    updated_resources: int = 0
    below_threshold: int = 0
    errors: list[str] = field(default_factory=list)


class DiscoveryAgent:
    """Orchestrate multi-source search for free AI training content.

    Workflow
    --------
    1. Generate search queries from the taxonomy for each requested domain.
    2. Fan out queries to all registered searchers concurrently.
    3. Deduplicate raw results by URL.
    4. Evaluate each result into a scored ``Resource``.
    5. Upsert qualifying resources into the catalog.
    """

    # Query templates — the ``{topic}`` placeholder is replaced per-domain
    _QUERY_TEMPLATES = [
        "free {topic} course open source",
        "{topic} tutorial beginner 2024 2025",
        "{topic} training materials open access",
        "learn {topic} free online",
        "best free resources {topic}",
    ]

    # Extra templates targeting GitHub specifically (hands-on content)
    _GITHUB_TEMPLATES = [
        "{topic} tutorial notebook",
        "{topic} course exercises",
        "awesome {topic}",
        "{topic} hands-on examples",
        "{topic} learning resources",
        "{topic} workshop lab",
        "{keyword} jupyter notebook tutorial",
        "{keyword} project beginner",
    ]

    def __init__(
        self,
        settings: Settings,
        searchers: list[BaseSearcher],
        evaluator: ResourceEvaluator,
        catalog: ResourceCatalog,
    ) -> None:
        self._settings = settings
        self._searchers = searchers
        self._evaluator = evaluator
        self._catalog = catalog

    def _build_queries(self, domains: list[SkillDomain]) -> list[str]:
        """Generate search query strings from the taxonomy."""
        queries: list[str] = []
        for node in TAXONOMY:
            if node.domain not in domains:
                continue
            topic = node.display_name
            for tmpl in self._QUERY_TEMPLATES:
                queries.append(tmpl.format(topic=topic))
            # Add a couple of keyword-specific queries
            for kw in node.keywords[:3]:
                queries.append(f"free {kw} tutorial course")
        return queries

    def _build_github_queries(self, domains: list[SkillDomain]) -> list[str]:
        """Generate extra queries specifically for GitHub hands-on content."""
        queries: list[str] = []
        for node in TAXONOMY:
            if node.domain not in domains:
                continue
            topic = node.display_name
            for tmpl in self._GITHUB_TEMPLATES:
                queries.append(tmpl.format(topic=topic, keyword=node.keywords[0]))
            # Add more keyword-specific GitHub queries
            for kw in node.keywords[:5]:
                queries.append(f"{kw} tutorial notebook exercises")
        return queries

    async def _search_one(
        self, searcher: BaseSearcher, query: str, max_results: int
    ) -> list[SearchResult]:
        """Run a single searcher/query combo, catching errors."""
        try:
            return await searcher.search(query, max_results=max_results)
        except Exception as exc:
            log.warning("Searcher %s failed for query '%s': %s", searcher.name, query, exc)
            return []

    async def run(
        self,
        domains: list[SkillDomain] | None = None,
        max_results_per_query: int = 10,
    ) -> DiscoveryReport:
        """Execute the full discovery pipeline.

        Parameters
        ----------
        domains:
            Limit discovery to these skill domains. ``None`` means all.
        max_results_per_query:
            Cap on results per searcher per query.
        """
        target_domains = domains or [d for d in SkillDomain]
        queries = self._build_queries(target_domains)
        github_queries = self._build_github_queries(target_domains)

        # Find the GitHub searcher for targeted queries
        github_searchers = [s for s in self._searchers if s.name == "github"]

        total_tasks = len(queries) * len(self._searchers) + len(github_queries) * len(github_searchers)
        report = DiscoveryReport(queries_executed=total_tasks)

        log.info(
            "Starting discovery: %d general queries × %d searchers + %d GitHub-specific queries",
            len(queries),
            len(self._searchers),
            len(github_queries),
        )

        # Fan out all queries concurrently (bounded by HttpClient semaphore)
        tasks = [
            self._search_one(searcher, query, max_results_per_query)
            for query in queries
            for searcher in self._searchers
        ]
        # Add GitHub-specific queries for hands-on content
        for query in github_queries:
            for searcher in github_searchers:
                tasks.append(self._search_one(searcher, query, max_results_per_query))

        all_results_nested = await asyncio.gather(*tasks)

        # Flatten and deduplicate by URL
        seen_urls: set[str] = set()
        unique_results: list[SearchResult] = []
        for batch in all_results_nested:
            for result in batch:
                canonical = result.url.strip().rstrip("/").lower()
                if canonical not in seen_urls:
                    seen_urls.add(canonical)
                    unique_results.append(result)
        report.raw_results = len(unique_results)

        log.info("Collected %d unique results from %d raw", len(unique_results), report.raw_results)

        # Evaluate and catalog
        for result in unique_results:
            try:
                resource = self._evaluator.evaluate(result)
                is_new = await self._catalog.upsert(
                    resource, min_score=self._settings.min_quality_score
                )
                if is_new:
                    report.new_resources += 1
                elif resource.quality_score >= self._settings.min_quality_score:
                    report.updated_resources += 1
                else:
                    report.below_threshold += 1
            except Exception as exc:
                msg = f"Failed to evaluate {result.url}: {exc}"
                log.warning(msg)
                report.errors.append(msg)

        log.info(
            "Discovery complete: %d new, %d updated, %d below threshold",
            report.new_resources,
            report.updated_resources,
            report.below_threshold,
        )
        return report
