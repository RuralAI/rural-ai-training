"""arXiv search backend for finding survey / tutorial papers."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from ai_training_catalog.config import Settings
from ai_training_catalog.utils.http_client import HttpClient
from ai_training_catalog.utils.logging import log

from .base import BaseSearcher, SearchResult

_NS = {"atom": "http://www.w3.org/2005/Atom"}


class ArxivSearcher(BaseSearcher):
    """Search arXiv for tutorial and survey papers on AI topics.

    Uses the arXiv API (no key required).
    """

    API_URL = "http://export.arxiv.org/api/query"

    def __init__(self, _settings: Settings, http: HttpClient) -> None:
        self._http = http

    @property
    def name(self) -> str:
        return "arxiv"

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        search_query = f"all:{query} AND (ti:tutorial OR ti:survey OR ti:introduction)"
        url = (
            f"{self.API_URL}?search_query={search_query}"
            f"&start=0&max_results={max_results}&sortBy=relevance"
        )

        try:
            resp = await self._http.get(url)
            if resp.status != 200:
                log.warning("arXiv search returned status %d", resp.status)
                return []

            root = ET.fromstring(resp.text)
            results: list[SearchResult] = []
            for entry in root.findall("atom:entry", _NS):
                title_el = entry.find("atom:title", _NS)
                summary_el = entry.find("atom:summary", _NS)
                link_el = entry.find("atom:id", _NS)

                title = (title_el.text or "").strip() if title_el is not None else ""
                summary = (summary_el.text or "").strip() if summary_el is not None else ""
                link = (link_el.text or "").strip() if link_el is not None else ""

                if link:
                    results.append(
                        SearchResult(
                            url=link,
                            title=title,
                            snippet=summary[:500],
                            source=self.name,
                            raw={"full_summary": summary},
                        )
                    )
            return results[:max_results]
        except Exception:
            log.exception("Error during arXiv search for query: %s", query)
            return []
