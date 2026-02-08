"""Per-domain async rate limiter for polite crawling."""

from __future__ import annotations

import asyncio
from urllib.parse import urlparse


class RateLimiter:
    """Token-bucket rate limiter keyed by hostname.

    Parameters
    ----------
    default_rate:
        Maximum requests per second for any single domain.
    overrides:
        Domain-specific rate overrides, e.g. ``{"api.github.com": 0.5}``.
    """

    def __init__(
        self,
        default_rate: float = 2.0,
        overrides: dict[str, float] | None = None,
    ) -> None:
        self._default_rate = default_rate
        self._overrides = overrides or {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._last_request: dict[str, float] = {}

    @staticmethod
    def _domain(url: str) -> str:
        return urlparse(url).hostname or url

    def _interval(self, domain: str) -> float:
        rate = self._overrides.get(domain, self._default_rate)
        return 1.0 / rate if rate > 0 else 0.0

    async def acquire(self, url: str) -> None:
        """Wait until a request to *url*'s domain is allowed."""
        domain = self._domain(url)
        if domain not in self._locks:
            self._locks[domain] = asyncio.Lock()

        async with self._locks[domain]:
            loop = asyncio.get_event_loop()
            now = loop.time()
            last = self._last_request.get(domain, 0.0)
            wait = self._interval(domain) - (now - last)
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_request[domain] = loop.time()
