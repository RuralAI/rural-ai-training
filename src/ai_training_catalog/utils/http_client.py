"""Shared async HTTP client with retry logic and rate limiting."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ai_training_catalog.config import Settings
from ai_training_catalog.utils.rate_limiter import RateLimiter


@dataclass
class HttpResponse:
    status: int
    text: str
    headers: dict[str, str] = field(default_factory=dict)
    url: str = ""


class HttpClient:
    """Async HTTP client wrapping ``aiohttp`` with rate limiting and retries."""

    USER_AGENT = (
        "AITrainingCatalog/0.1 (+https://github.com/ai-training-catalog; research bot)"
    )

    def __init__(self, settings: Settings, rate_limiter: RateLimiter | None = None) -> None:
        self._settings = settings
        self._rate_limiter = rate_limiter or RateLimiter(settings.rate_limit_per_second)
        self._semaphore = asyncio.Semaphore(settings.max_concurrent_requests)
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self._settings.request_timeout_seconds)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers={"User-Agent": self.USER_AGENT},
            )
        return self._session

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        reraise=True,
    )
    async def get(self, url: str, headers: dict[str, str] | None = None) -> HttpResponse:
        """Perform a rate-limited, retried GET request."""
        await self._rate_limiter.acquire(url)
        async with self._semaphore:
            session = await self._get_session()
            async with session.get(url, headers=headers, allow_redirects=True) as resp:
                text = await resp.text()
                return HttpResponse(
                    status=resp.status,
                    text=text,
                    headers=dict(resp.headers),
                    url=str(resp.url),
                )

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> "HttpClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
