"""Command-line interface for the AI Training Catalog.

Usage examples::

    ai-catalog discover --domains ml_basics,deep_learning
    ai-catalog ingest --min-score 0.4
    ai-catalog generate --title "Technical AI Curriculum"
    ai-catalog catalog stats
    ai-catalog catalog list --domain ml_basics --min-score 0.5
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import click

from ai_training_catalog.config import Settings
from ai_training_catalog.models.resource import SkillDomain


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_domains(raw: str | None) -> list[SkillDomain] | None:
    if not raw:
        return None
    names = [s.strip() for s in raw.split(",") if s.strip()]
    domains: list[SkillDomain] = []
    for name in names:
        try:
            domains.append(SkillDomain(name))
        except ValueError:
            click.echo(f"Unknown domain: {name}. Valid: {[d.value for d in SkillDomain]}", err=True)
            sys.exit(1)
    return domains


def _make_settings() -> Settings:
    settings = Settings()
    settings.ensure_dirs()
    return settings


# ---------------------------------------------------------------------------
# Root group
# ---------------------------------------------------------------------------

@click.group()
@click.version_option(package_name="ai-training-catalog")
def main() -> None:
    """AI Training Catalog — discover free AI content and generate curricula."""


# ---------------------------------------------------------------------------
# discover
# ---------------------------------------------------------------------------

@main.command()
@click.option("--domains", default=None, help="Comma-separated SkillDomain values (e.g. ml_basics,nlp)")
@click.option("--max-results", default=10, type=int, help="Max results per query per searcher")
def discover(domains: str | None, max_results: int) -> None:
    """Run the discovery agent to find new AI training resources."""
    asyncio.run(_discover(domains, max_results))


async def _discover(domains_raw: str | None, max_results: int) -> None:
    from ai_training_catalog.discovery.agent import DiscoveryAgent
    from ai_training_catalog.discovery.catalog import ResourceCatalog
    from ai_training_catalog.discovery.evaluator import ResourceEvaluator
    from ai_training_catalog.discovery.searchers.arxiv_search import ArxivSearcher
    from ai_training_catalog.discovery.searchers.github_search import GitHubSearcher
    from ai_training_catalog.discovery.searchers.google_search import GoogleSearcher
    from ai_training_catalog.storage.json_store import JsonStore
    from ai_training_catalog.storage.repository import ResourceRepository
    from ai_training_catalog.utils.http_client import HttpClient

    settings = _make_settings()
    parsed = _parse_domains(domains_raw)

    store = JsonStore(settings.catalog_path)
    repo = ResourceRepository(store)
    catalog = ResourceCatalog(repo)

    async with HttpClient(settings) as http:
        searchers = [
            GoogleSearcher(settings, http),
            GitHubSearcher(settings, http),
            ArxivSearcher(settings, http),
        ]
        evaluator = ResourceEvaluator()
        agent = DiscoveryAgent(settings, searchers, evaluator, catalog)

        report = await agent.run(domains=parsed, max_results_per_query=max_results)

    click.echo(f"\n{'='*60}")
    click.echo("Discovery Report")
    click.echo(f"{'='*60}")
    click.echo(f"  Queries executed:     {report.queries_executed}")
    click.echo(f"  Unique results found: {report.raw_results}")
    click.echo(f"  New resources added:  {report.new_resources}")
    click.echo(f"  Resources updated:    {report.updated_resources}")
    click.echo(f"  Below threshold:      {report.below_threshold}")
    if report.errors:
        click.echo(f"  Errors:               {len(report.errors)}")
    total = await catalog.count()
    click.echo(f"  Total in catalog:     {total}")
    click.echo(f"{'='*60}")


# ---------------------------------------------------------------------------
# ingest
# ---------------------------------------------------------------------------

@main.command()
@click.option("--min-score", default=0.3, type=float, help="Minimum quality score to ingest")
@click.option("--resource-id", default=None, help="Specific resource ID to ingest")
def ingest(min_score: float, resource_id: str | None) -> None:
    """Ingest and rationalise content from catalogued resources."""
    asyncio.run(_ingest(min_score, resource_id))


async def _ingest(min_score: float, resource_id: str | None) -> None:
    from ai_training_catalog.discovery.catalog import ResourceCatalog
    from ai_training_catalog.ingestion.pipeline import IngestionPipeline
    from ai_training_catalog.ingestion.scrapers.html_scraper import HtmlScraper
    from ai_training_catalog.storage.json_store import JsonStore
    from ai_training_catalog.storage.repository import ResourceRepository
    from ai_training_catalog.utils.http_client import HttpClient

    settings = _make_settings()

    store = JsonStore(settings.catalog_path)
    repo = ResourceRepository(store)
    catalog = ResourceCatalog(repo)

    resource_ids = [resource_id] if resource_id else None

    async with HttpClient(settings) as http:
        scrapers = [HtmlScraper(http)]
        pipeline = IngestionPipeline(settings, catalog, scrapers)
        report = await pipeline.run(resource_ids=resource_ids, min_score=min_score)

    click.echo(f"\n{'='*60}")
    click.echo("Ingestion Report")
    click.echo(f"{'='*60}")
    click.echo(f"  Resources processed:  {report.total_resources}")
    click.echo(f"  Successfully scraped: {report.scraped}")
    click.echo(f"  Failed:               {report.failed}")
    click.echo(f"  Duplicate groups:     {report.duplicate_groups}")
    click.echo(f"  Duplicates flagged:   {report.duplicates_flagged}")
    click.echo(f"  Recategorised:        {report.recategorized}")
    if report.errors:
        click.echo(f"  Errors:               {len(report.errors)}")
    click.echo(f"{'='*60}")


# ---------------------------------------------------------------------------
# generate
# ---------------------------------------------------------------------------

@main.command()
@click.option("--domains", default=None, help="Comma-separated SkillDomain values")
@click.option("--title", default=None, help="Custom title for the curriculum")
@click.option("--output", default=None, type=click.Path(), help="Output JSON path")
def generate(domains: str | None, title: str | None, output: str | None) -> None:
    """Generate a best-practices AI training curriculum."""
    asyncio.run(_generate(domains, title, output))


async def _generate(domains_raw: str | None, title: str | None, output: str | None) -> None:
    from ai_training_catalog.curriculum.generator import CurriculumGenerator
    from ai_training_catalog.discovery.catalog import ResourceCatalog
    from ai_training_catalog.storage.json_store import JsonStore
    from ai_training_catalog.storage.repository import CurriculumRepository, ResourceRepository

    settings = _make_settings()
    parsed = _parse_domains(domains_raw)

    store = JsonStore(settings.catalog_path)
    repo = ResourceRepository(store)
    catalog = ResourceCatalog(repo)
    curriculum_repo = CurriculumRepository(settings.curricula_dir)

    generator = CurriculumGenerator(settings, catalog, curriculum_repo=curriculum_repo)
    curriculum, validation = await generator.generate(target_domains=parsed, title=title)

    # Write to custom output if specified
    if output:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(curriculum.model_dump(mode="json"), indent=2, default=str),
            encoding="utf-8",
        )
        click.echo(f"Curriculum written to {out_path}")

    click.echo(f"\n{'='*60}")
    click.echo("Curriculum Generation Report")
    click.echo(f"{'='*60}")
    click.echo(f"  Title:            {curriculum.title}")
    click.echo(f"  Learning paths:   {len(curriculum.learning_paths)}")
    click.echo(f"  Total hours:      {curriculum.total_hours:.1f}")
    click.echo(f"  Domains covered:  {curriculum.metadata.get('domains_covered', [])}")
    click.echo()
    for path in curriculum.learning_paths:
        click.echo(f"  [{path.difficulty.value:>12}] {path.title}")
        click.echo(f"                    {len(path.modules)} modules, {path.total_estimated_hours:.1f}h")
    click.echo()
    click.echo(f"  Validation: {validation.error_count} errors, {validation.warning_count} warnings")
    for issue in validation.issues:
        icon = {"error": "X", "warning": "!", "info": "i"}[issue.severity.value]
        click.echo(f"    [{icon}] {issue.message}")
    click.echo(f"{'='*60}")


# ---------------------------------------------------------------------------
# catalog subcommand group
# ---------------------------------------------------------------------------

@main.group()
def catalog() -> None:
    """Inspect and manage the resource catalog."""


@catalog.command("list")
@click.option("--domain", default=None, help="Filter by SkillDomain")
@click.option("--min-score", default=0.0, type=float, help="Minimum quality score")
@click.option("--limit", default=50, type=int, help="Max items to show")
def catalog_list(domain: str | None, min_score: float, limit: int) -> None:
    """List catalogued resources."""
    asyncio.run(_catalog_list(domain, min_score, limit))


async def _catalog_list(domain_raw: str | None, min_score: float, limit: int) -> None:
    from ai_training_catalog.discovery.catalog import ResourceCatalog
    from ai_training_catalog.storage.json_store import JsonStore
    from ai_training_catalog.storage.repository import ResourceRepository

    settings = _make_settings()
    store = JsonStore(settings.catalog_path)
    repo = ResourceRepository(store)
    catalog = ResourceCatalog(repo)

    if domain_raw:
        try:
            dom = SkillDomain(domain_raw)
        except ValueError:
            click.echo(f"Unknown domain: {domain_raw}", err=True)
            sys.exit(1)
        resources = await catalog.get_by_domain(dom)
    else:
        resources = await catalog.get_all(min_score=min_score)

    for r in resources[:limit]:
        domains_str = ", ".join(d.value for d in r.domains[:2])
        click.echo(
            f"  [{r.quality_score:.2f}] {r.title[:60]:<60} "
            f"({domains_str}) {r.url}"
        )
    click.echo(f"\nShowing {min(limit, len(resources))} of {len(resources)} resources")


@catalog.command("stats")
def catalog_stats() -> None:
    """Show catalog statistics."""
    asyncio.run(_catalog_stats())


async def _catalog_stats() -> None:
    from collections import Counter

    from ai_training_catalog.discovery.catalog import ResourceCatalog
    from ai_training_catalog.storage.json_store import JsonStore
    from ai_training_catalog.storage.repository import ResourceRepository

    settings = _make_settings()
    store = JsonStore(settings.catalog_path)
    repo = ResourceRepository(store)
    catalog_obj = ResourceCatalog(repo)

    resources = await catalog_obj.get_all()
    if not resources:
        click.echo("Catalog is empty. Run 'ai-catalog discover' first.")
        return

    domain_counts: Counter[str] = Counter()
    type_counts: Counter[str] = Counter()
    provider_counts: Counter[str] = Counter()
    for r in resources:
        for d in r.domains:
            domain_counts[d.value] += 1
        type_counts[r.content_type.value] += 1
        provider_counts[r.provider or "unknown"] += 1

    scores = [r.quality_score for r in resources]
    avg_score = sum(scores) / len(scores) if scores else 0

    click.echo(f"\n{'='*60}")
    click.echo("Catalog Statistics")
    click.echo(f"{'='*60}")
    click.echo(f"  Total resources: {len(resources)}")
    click.echo(f"  Active:          {sum(1 for r in resources if r.is_active)}")
    click.echo(f"  Avg quality:     {avg_score:.3f}")
    click.echo(f"  Score range:     {min(scores):.3f} — {max(scores):.3f}")
    click.echo()
    click.echo("  By domain:")
    for domain, count in domain_counts.most_common(10):
        click.echo(f"    {domain:<30} {count}")
    click.echo()
    click.echo("  By content type:")
    for ctype, count in type_counts.most_common():
        click.echo(f"    {ctype:<30} {count}")
    click.echo()
    click.echo("  Top providers:")
    for prov, count in provider_counts.most_common(10):
        click.echo(f"    {prov:<30} {count}")
    click.echo(f"{'='*60}")


@catalog.command("export")
@click.option("--output", default="catalog_export.json", help="Output file path")
def catalog_export(output: str) -> None:
    """Export the full catalog to JSON."""
    asyncio.run(_catalog_export(output))


async def _catalog_export(output: str) -> None:
    from ai_training_catalog.storage.json_store import JsonStore

    settings = _make_settings()
    store = JsonStore(settings.catalog_path)
    data = await store.read()

    out = Path(output)
    out.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    resource_count = len(data.get("resources", {}))
    click.echo(f"Exported {resource_count} resources to {out}")


# ---------------------------------------------------------------------------
# web — generate searchable HTML page
# ---------------------------------------------------------------------------

@main.command()
@click.option("--output", default="catalog.html", help="Output HTML file path")
def web(output: str) -> None:
    """Generate a searchable HTML catalog you can open in your browser."""
    asyncio.run(_web(output))


async def _web(output: str) -> None:
    from ai_training_catalog.discovery.catalog import ResourceCatalog
    from ai_training_catalog.export_html import generate_html
    from ai_training_catalog.models.curriculum import Curriculum
    from ai_training_catalog.storage.json_store import JsonStore
    from ai_training_catalog.storage.repository import CurriculumRepository, ResourceRepository

    settings = _make_settings()
    store = JsonStore(settings.catalog_path)
    repo = ResourceRepository(store)
    catalog_obj = ResourceCatalog(repo)

    resources = await catalog_obj.get_all()
    if not resources:
        click.echo("Catalog is empty. Run 'ai-catalog discover' first.")
        return

    # Load the most recent curriculum if available
    curriculum_repo = CurriculumRepository(settings.curricula_dir)
    curriculum_ids = await curriculum_repo.list_all()
    curriculum = None
    if curriculum_ids:
        curriculum = await curriculum_repo.load(curriculum_ids[-1])

    out_path = Path(output)
    generate_html(resources, curriculum, out_path)
    click.echo(f"Searchable catalog generated: {out_path.resolve()}")
    click.echo(f"Open it in your browser: file:///{out_path.resolve()}")


# ---------------------------------------------------------------------------
# contextualize — rural contextualization of a learning path
# ---------------------------------------------------------------------------

@main.command()
@click.option("--path-title", default=None, help="Partial title match for the learning path (default: ML Basics)")
@click.option("--output", default="rural_course.html", help="Output HTML file path")
@click.option("--json-output", default=None, help="Also write raw JSON to this path")
def contextualize(path_title: str | None, output: str, json_output: str | None) -> None:
    """Generate a rural-contextualized version of a learning path."""
    asyncio.run(_contextualize(path_title, output, json_output))


async def _contextualize(
    path_title: str | None, output: str, json_output: str | None
) -> None:
    from ai_training_catalog.contextualization.engine import (
        contextualize_path,
        generate_rural_html,
    )
    from ai_training_catalog.discovery.catalog import ResourceCatalog
    from ai_training_catalog.storage.json_store import JsonStore
    from ai_training_catalog.storage.repository import CurriculumRepository, ResourceRepository

    settings = _make_settings()

    # Load resources
    store = JsonStore(settings.catalog_path)
    repo = ResourceRepository(store)
    catalog_obj = ResourceCatalog(repo)
    all_resources = await catalog_obj.get_all()
    resource_map = {r.id: r for r in all_resources}

    # Load the most recent curriculum
    curriculum_repo = CurriculumRepository(settings.curricula_dir)
    curriculum_ids = await curriculum_repo.list_all()
    if not curriculum_ids:
        click.echo("No curriculum found. Run 'ai-catalog generate' first.", err=True)
        sys.exit(1)

    curriculum = await curriculum_repo.load(curriculum_ids[-1])
    if curriculum is None:
        click.echo("Failed to load curriculum.", err=True)
        sys.exit(1)

    # Find matching learning path
    search = (path_title or "ml basics").lower()
    matched = None
    for lp in curriculum.learning_paths:
        if search in lp.title.lower():
            matched = lp
            break

    if not matched:
        click.echo(f"No learning path matching '{search}'. Available paths:", err=True)
        for lp in curriculum.learning_paths:
            click.echo(f"  - {lp.title}", err=True)
        sys.exit(1)

    click.echo(f"Contextualizing: {matched.title}")
    click.echo(f"  {len(matched.modules)} modules, {matched.total_estimated_hours:.1f}h original")

    # Run contextualization
    result = contextualize_path(matched, resource_map)

    # Write JSON if requested
    if json_output:
        json_path = Path(json_output)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
        click.echo(f"  JSON written to: {json_path.resolve()}")

    # Generate HTML
    html_path = Path(output)
    generate_rural_html(result, html_path)

    click.echo(f"\n{'='*60}")
    click.echo("Rural Contextualization Complete")
    click.echo(f"{'='*60}")
    click.echo(f"  Original:    {matched.title}")
    click.echo(f"  Rural title: {result['title']}")
    click.echo(f"  Modules:     {len(result['modules'])}")
    click.echo(f"  Hours:       {result['total_estimated_hours']:.1f}h (includes rural exercises)")
    click.echo(f"  Datasets:    {len(result.get('rural_datasets', []))}")
    click.echo(f"  Projects:    {len(result.get('community_projects', []))}")
    click.echo(f"  HTML output: {html_path.resolve()}")
    click.echo(f"{'='*60}")
    click.echo(f"\nOpen in your browser: file:///{html_path.resolve()}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    main()
