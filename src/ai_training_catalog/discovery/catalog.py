"""In-memory resource catalog backed by the JSON repository."""

from __future__ import annotations

from ai_training_catalog.models.resource import Resource, SkillDomain
from ai_training_catalog.storage.repository import ResourceRepository
from ai_training_catalog.utils.logging import log


class ResourceCatalog:
    """High-level interface over the resource repository.

    Handles deduplication by URL, upsert semantics, and filtered queries.
    """

    def __init__(self, repo: ResourceRepository) -> None:
        self._repo = repo
        self._cache: dict[str, Resource] = {}
        self._loaded = False

    async def _ensure_loaded(self) -> None:
        if not self._loaded:
            resources = await self._repo.find_all()
            self._cache = {r.id: r for r in resources}
            self._loaded = True

    async def upsert(self, resource: Resource, min_score: float = 0.0) -> bool:
        """Insert or update a resource. Returns True if new.

        Resources below *min_score* are silently dropped.
        """
        if resource.quality_score < min_score:
            return False

        await self._ensure_loaded()
        is_new = resource.id not in self._cache
        if not is_new:
            existing = self._cache[resource.id]
            # Keep the higher quality score
            resource.quality_score = max(resource.quality_score, existing.quality_score)
            resource.discovered_at = existing.discovered_at

        self._cache[resource.id] = resource
        await self._repo.save(resource)
        action = "Added" if is_new else "Updated"
        log.info("%s resource: %s (%s)", action, resource.title[:60], resource.id)
        return is_new

    async def get_all(self, min_score: float = 0.0) -> list[Resource]:
        await self._ensure_loaded()
        resources = list(self._cache.values())
        if min_score > 0:
            resources = [r for r in resources if r.quality_score >= min_score]
        return sorted(resources, key=lambda r: r.quality_score, reverse=True)

    async def get_by_domain(self, domain: SkillDomain) -> list[Resource]:
        all_res = await self.get_all()
        return [r for r in all_res if domain in r.domains]

    async def count(self) -> int:
        await self._ensure_loaded()
        return len(self._cache)

    async def catalog_hash(self) -> str:
        return await self._repo.catalog_hash()
