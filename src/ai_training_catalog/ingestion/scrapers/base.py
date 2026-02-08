"""Abstract base for content scrapers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from ai_training_catalog.models.resource import Resource


class ScrapedContent(BaseModel):
    """Extracted content from a single resource."""
    resource_id: str
    url: str = ""
    text_content: str = ""
    headings: list[str] = Field(default_factory=list)
    code_blocks: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)
    content_hash: str = ""
    word_count: int = 0
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BaseScraper(ABC):
    """Interface for content extraction backends."""

    @abstractmethod
    def can_handle(self, resource: Resource) -> bool:
        """Return True if this scraper supports the given resource."""

    @abstractmethod
    async def scrape(self, resource: Resource) -> ScrapedContent | None:
        """Extract content from *resource*. Return None on failure."""
