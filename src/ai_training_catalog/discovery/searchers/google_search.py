"""Google Custom Search JSON API backend."""

from __future__ import annotations

import json

from ai_training_catalog.config import Settings
from ai_training_catalog.utils.http_client import HttpClient
from ai_training_catalog.utils.logging import log

from .base import BaseSearcher, SearchResult


class GoogleSearcher(BaseSearcher):
    """Search the web using Google Custom Search Engine API.

    Requires ``ATC_GOOGLE_API_KEY`` and ``ATC_GOOGLE_CSE_ID`` to be set.
    Falls back to returning an empty list if credentials are missing.
    """

    BASE_URL = "https://www.googleapis.com/customsearch/v1"

    def __init__(self, settings: Settings, http: HttpClient) -> None:
        self._api_key = settings.google_api_key
        self._cse_id = settings.google_cse_id
        self._http = http

    @property
    def name(self) -> str:
        return "google"

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        if not self._api_key or not self._cse_id:
            log.warning("Google API credentials not configured — skipping Google search")
            return []

        results: list[SearchResult] = []
        start = 1
        while len(results) < max_results:
            url = (
                f"{self.BASE_URL}?key={self._api_key}&cx={self._cse_id}"
                f"&q={query}&start={start}&num=10"
            )
            try:
                resp = await self._http.get(url)
                if resp.status != 200:
                    log.warning("Google search returned status %d", resp.status)
                    break
                data = json.loads(resp.text)
                items = data.get("items", [])
                if not items:
                    break
                for item in items:
                    results.append(
                        SearchResult(
                            url=item.get("link", ""),
                            title=item.get("title", ""),
                            snippet=item.get("snippet", ""),
                            source=self.name,
                            raw=item,
                        )
                    )
                start += 10
            except Exception:
                log.exception("Error during Google search for query: %s", query)
                break

        return results[:max_results]
