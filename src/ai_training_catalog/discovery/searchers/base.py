"""Abstract base for all search backends."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Raw search result before evaluation."""
    url: str
    title: str
    snippet: str = ""
    source: str = ""  # name of the searcher that produced this
    raw: dict = Field(default_factory=dict)


class BaseSearcher(ABC):
    """Interface that every search backend must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this searcher."""

    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        """Execute *query* and return up to *max_results* results."""
