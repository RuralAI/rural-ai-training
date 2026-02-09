"""HTML content extraction using BeautifulSoup."""

from __future__ import annotations

from bs4 import BeautifulSoup

from ai_training_catalog.models.resource import ContentType, Resource
from ai_training_catalog.utils.http_client import HttpClient
from ai_training_catalog.utils.logging import log
from ai_training_catalog.utils.text_processing import content_hash

from .base import BaseScraper, ScrapedContent

# Tags to strip before extraction
_STRIP_TAGS = {"nav", "footer", "header", "aside", "script", "style", "noscript", "iframe"}


class HtmlScraper(BaseScraper):
    """Extract main text content from HTML pages."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def can_handle(self, resource: Resource) -> bool:
        return resource.content_type not in (ContentType.PAPER,)

    async def scrape(self, resource: Resource) -> ScrapedContent | None:
        try:
            resp = await self._http.get(resource.url)
            if resp.status != 200:
                log.warning("HTTP %d for %s", resp.status, resource.url)
                return None
            return self._extract(resource, resp.text)
        except Exception:
            log.exception("Failed to scrape %s", resource.url)
            return None

    def _extract(self, resource: Resource, html: str) -> ScrapedContent:
        soup = BeautifulSoup(html, "html.parser")

        # Remove noisy tags
        for tag in soup.find_all(_STRIP_TAGS):
            tag.decompose()

        # Prefer <main> or <article>; fall back to <body>
        main = soup.find("main") or soup.find("article") or soup.find("body") or soup
        text = main.get_text(separator="\n", strip=True)

        headings = [
            h.get_text(strip=True)
            for h in main.find_all(["h1", "h2", "h3", "h4"])
        ]

        code_blocks = [
            code.get_text(strip=True)
            for code in main.find_all(["code", "pre"])
            if len(code.get_text(strip=True)) > 20
        ]

        links = [
            a["href"]
            for a in main.find_all("a", href=True)
            if a["href"].startswith("http")
        ]

        words = text.split()
        return ScrapedContent(
            resource_id=resource.id,
            url=resource.url,
            text_content=text[:50_000],  # cap to avoid huge payloads
            headings=headings[:50],
            code_blocks=code_blocks[:30],
            links=links[:100],
            content_hash=content_hash(text),
            word_count=len(words),
        )
