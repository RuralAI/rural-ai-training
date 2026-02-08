"""GitHub repository search backend."""

from __future__ import annotations

import json

from ai_training_catalog.config import Settings
from ai_training_catalog.utils.http_client import HttpClient
from ai_training_catalog.utils.logging import log

from .base import BaseSearcher, SearchResult


class GitHubSearcher(BaseSearcher):
    """Search GitHub repositories for AI training content.

    Uses the GitHub REST API ``/search/repositories`` endpoint.
    A token (``ATC_GITHUB_TOKEN``) is recommended for higher rate limits.
    """

    API_URL = "https://api.github.com/search/repositories"

    def __init__(self, settings: Settings, http: HttpClient) -> None:
        self._token = settings.github_token
        self._http = http

    @property
    def name(self) -> str:
        return "github"

    async def search(self, query: str, max_results: int = 10) -> list[SearchResult]:
        headers: dict[str, str] = {"Accept": "application/vnd.github+json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        search_query = f"{query} in:name,description,readme"
        url = f"{self.API_URL}?q={search_query}&sort=stars&order=desc&per_page={max_results}"

        try:
            resp = await self._http.get(url, headers=headers)
            if resp.status != 200:
                log.warning("GitHub search returned status %d", resp.status)
                return []
            data = json.loads(resp.text)
            results: list[SearchResult] = []
            for repo in data.get("items", [])[:max_results]:
                results.append(
                    SearchResult(
                        url=repo.get("html_url", ""),
                        title=repo.get("full_name", ""),
                        snippet=repo.get("description", "") or "",
                        source=self.name,
                        raw={
                            "stars": repo.get("stargazers_count", 0),
                            "language": repo.get("language", ""),
                            "topics": repo.get("topics", []),
                            "updated_at": repo.get("updated_at", ""),
                        },
                    )
                )
            return results
        except Exception:
            log.exception("Error during GitHub search for query: %s", query)
            return []
