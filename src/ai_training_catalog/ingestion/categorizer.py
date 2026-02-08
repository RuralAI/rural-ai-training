"""Refine domain and tag assignments using full text content."""

from __future__ import annotations

from dataclasses import dataclass, field

from ai_training_catalog.models.resource import SkillDomain
from ai_training_catalog.models.taxonomy import TAXONOMY, TaxonomyNode
from ai_training_catalog.utils.text_processing import keyword_score

from .scrapers.base import ScrapedContent


@dataclass
class CategorizedResult:
    """Output of categorisation: refined domain assignments and tags."""
    resource_id: str
    primary_domain: SkillDomain | None = None
    secondary_domains: list[SkillDomain] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    domain_scores: dict[str, float] = field(default_factory=dict)


class ContentCategorizer:
    """Categorise scraped content against the skill taxonomy.

    Uses keyword TF scoring against each taxonomy node's keyword list.
    """

    def __init__(
        self,
        taxonomy: list[TaxonomyNode] | None = None,
        primary_threshold: float = 0.05,
        secondary_threshold: float = 0.02,
    ) -> None:
        self._taxonomy = taxonomy or TAXONOMY
        self._primary_threshold = primary_threshold
        self._secondary_threshold = secondary_threshold

    def categorize(self, content: ScrapedContent) -> CategorizedResult:
        """Analyse *content* and return domain assignments."""
        # Combine headings + first portion of text for scoring
        text = " ".join(content.headings) + " " + content.text_content[:10_000]

        scores: list[tuple[float, TaxonomyNode]] = []
        for node in self._taxonomy:
            score = keyword_score(text, node.keywords)
            scores.append((score, node))

        scores.sort(key=lambda t: t[0], reverse=True)
        domain_scores = {node.domain.value: round(s, 4) for s, node in scores if s > 0}

        primary: SkillDomain | None = None
        secondary: list[SkillDomain] = []
        tags: list[str] = []

        for score, node in scores:
            if score >= self._primary_threshold and primary is None:
                primary = node.domain
                # Add subtopics as tags if their keywords appear
                for subtopic in node.subtopics:
                    if subtopic.lower() in text.lower():
                        tags.append(subtopic)
            elif score >= self._secondary_threshold:
                secondary.append(node.domain)

        return CategorizedResult(
            resource_id=content.resource_id,
            primary_domain=primary,
            secondary_domains=secondary[:4],
            tags=tags[:15],
            domain_scores=domain_scores,
        )
