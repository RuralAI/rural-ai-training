"""Score candidate resources on a 0–1 quality scale."""

from __future__ import annotations

from datetime import datetime, timezone

from ai_training_catalog.models.resource import (
    ContentType,
    DifficultyLevel,
    LicenseType,
    Resource,
    SkillDomain,
)
from ai_training_catalog.models.taxonomy import TAXONOMY
from ai_training_catalog.utils.text_processing import keyword_score

from .searchers.base import SearchResult

# Providers with established reputation for quality AI content.
REPUTABLE_PROVIDERS: dict[str, float] = {
    "fast.ai": 0.20,
    "deeplearning.ai": 0.20,
    "stanford": 0.20,
    "mit": 0.20,
    "google": 0.15,
    "microsoft": 0.15,
    "huggingface": 0.18,
    "openai": 0.15,
    "coursera": 0.12,
    "kaggle": 0.14,
    "arxiv": 0.10,
    "github": 0.10,
}


def _detect_provider(url: str, title: str) -> str:
    """Best-effort provider detection from URL and title."""
    combined = (url + " " + title).lower()
    for name in REPUTABLE_PROVIDERS:
        if name in combined:
            return name
    return ""


def _detect_content_type(url: str, snippet: str) -> ContentType:
    """Heuristic content-type detection."""
    combined = (url + " " + snippet).lower()
    if any(kw in combined for kw in ["course", "mooc", "syllabus", "lecture"]):
        return ContentType.COURSE
    if any(kw in combined for kw in ["tutorial", "how to", "step by step", "guide"]):
        return ContentType.TUTORIAL
    if "arxiv" in combined or "paper" in combined:
        return ContentType.PAPER
    if any(kw in combined for kw in ["video", "youtube", "watch"]):
        return ContentType.VIDEO_SERIES
    if any(kw in combined for kw in ["book", "textbook", "ebook"]):
        return ContentType.BOOK
    if any(kw in combined for kw in ["notebook", "colab", "jupyter"]):
        return ContentType.INTERACTIVE_NOTEBOOK
    if "documentation" in combined or "docs" in combined:
        return ContentType.DOCUMENTATION
    return ContentType.TUTORIAL


def _detect_difficulty(snippet: str) -> DifficultyLevel:
    s = snippet.lower()
    if any(kw in s for kw in ["advanced", "expert", "research", "state-of-the-art"]):
        return DifficultyLevel.ADVANCED
    if any(kw in s for kw in ["intermediate", "practical", "hands-on project"]):
        return DifficultyLevel.INTERMEDIATE
    return DifficultyLevel.BEGINNER


def _detect_domains(text: str) -> list[SkillDomain]:
    """Match text against the taxonomy and return relevant domains."""
    scored: list[tuple[float, SkillDomain]] = []
    for node in TAXONOMY:
        score = keyword_score(text, node.keywords)
        if score > 0.02:
            scored.append((score, node.domain))
    scored.sort(key=lambda t: t[0], reverse=True)
    return [domain for _, domain in scored[:3]]  # top-3 domains


class ResourceEvaluator:
    """Convert a raw :class:`SearchResult` into a scored :class:`Resource`.

    Scoring breakdown (sums to ~1.0):
    - Reputable provider:        up to 0.20
    - Keyword relevance:         up to 0.25
    - Content type richness:     up to 0.15
    - Community signals (stars):  up to 0.15
    - Freshness:                 up to 0.15
    - Has description / snippet: up to 0.10
    """

    def evaluate(self, result: SearchResult) -> Resource:
        combined_text = f"{result.title} {result.snippet}"
        score = 0.0

        # 1. Provider reputation
        provider = _detect_provider(result.url, result.title)
        score += REPUTABLE_PROVIDERS.get(provider, 0.0)

        # 2. Keyword relevance
        domains = _detect_domains(combined_text)
        if domains:
            best_kw = max(
                keyword_score(combined_text, node.keywords)
                for node in TAXONOMY
                if node.domain in domains
            )
            score += min(best_kw, 0.25)

        # 3. Content type richness (courses and notebooks score higher)
        ctype = _detect_content_type(result.url, result.snippet)
        richness = {
            ContentType.COURSE: 0.15,
            ContentType.INTERACTIVE_NOTEBOOK: 0.14,
            ContentType.BOOK: 0.12,
            ContentType.VIDEO_SERIES: 0.11,
            ContentType.TUTORIAL: 0.10,
            ContentType.PAPER: 0.08,
            ContentType.DOCUMENTATION: 0.07,
            ContentType.BLOG_SERIES: 0.06,
            ContentType.CERTIFICATION_PREP: 0.10,
        }
        score += richness.get(ctype, 0.05)

        # 4. Community signals (GitHub stars)
        stars = result.raw.get("stars", 0)
        if isinstance(stars, int) and stars > 0:
            # logarithmic scaling: 100 stars ≈ 0.10, 10k+ ≈ 0.15
            import math
            score += min(math.log10(stars + 1) / 35.0, 0.15)

        # 5. Freshness
        updated = result.raw.get("updated_at", "")
        if updated:
            try:
                dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                age_days = (datetime.now(timezone.utc) - dt).days
                if age_days < 365:
                    score += 0.15
                elif age_days < 730:
                    score += 0.08
            except (ValueError, TypeError):
                pass

        # 6. Description completeness
        if len(result.snippet) > 50:
            score += 0.10
        elif len(result.snippet) > 10:
            score += 0.05

        score = min(score, 1.0)

        return Resource(
            url=result.url,
            title=result.title,
            description=result.snippet,
            provider=provider,
            domains=domains,
            content_type=ctype,
            difficulty=_detect_difficulty(result.snippet),
            quality_score=round(score, 3),
            raw_metadata=result.raw,
        )
