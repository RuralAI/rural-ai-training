"""Repository classes mapping domain objects to/from JSON storage."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from ai_training_catalog.models.curriculum import Curriculum
from ai_training_catalog.models.resource import Resource
from ai_training_catalog.storage.json_store import JsonStore


class ResourceRepository:
    """CRUD operations for :class:`Resource` objects stored in a single JSON file."""

    def __init__(self, store: JsonStore) -> None:
        self._store = store

    async def save(self, resource: Resource) -> None:
        def _upsert(data: dict) -> dict:
            resources = data.get("resources", {})
            resources[resource.id] = resource.model_dump(mode="json")
            data["resources"] = resources
            return data

        await self._store.update(_upsert)

    async def save_many(self, resources: list[Resource]) -> None:
        def _upsert_many(data: dict) -> dict:
            existing = data.get("resources", {})
            for r in resources:
                existing[r.id] = r.model_dump(mode="json")
            data["resources"] = existing
            return data

        await self._store.update(_upsert_many)

    async def find_by_id(self, resource_id: str) -> Resource | None:
        data = await self._store.read()
        raw = data.get("resources", {}).get(resource_id)
        return Resource.model_validate(raw) if raw else None

    async def find_all(self, min_score: float = 0.0) -> list[Resource]:
        data = await self._store.read()
        resources = [
            Resource.model_validate(v) for v in data.get("resources", {}).values()
        ]
        if min_score > 0:
            resources = [r for r in resources if r.quality_score >= min_score]
        return resources

    async def delete(self, resource_id: str) -> bool:
        removed = False

        def _del(data: dict) -> dict:
            nonlocal removed
            resources = data.get("resources", {})
            removed = resource_id in resources
            resources.pop(resource_id, None)
            data["resources"] = resources
            return data

        await self._store.update(_del)
        return removed

    async def catalog_hash(self) -> str:
        """SHA-256 of the current catalog for integrity tracking."""
        data = await self._store.read()
        raw = json.dumps(data.get("resources", {}), sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


class CurriculumRepository:
    """Stores each curriculum as a separate JSON file."""

    def __init__(self, directory: Path) -> None:
        self._dir = directory
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, curriculum_id: str) -> Path:
        safe = curriculum_id.replace("/", "_").replace(" ", "_")
        return self._dir / f"{safe}.json"

    async def save(self, curriculum: Curriculum) -> Path:
        store = JsonStore(self._path_for(curriculum.id))
        await store.write(curriculum.model_dump(mode="json"))
        return store.path

    async def load(self, curriculum_id: str) -> Curriculum | None:
        path = self._path_for(curriculum_id)
        if not path.exists():
            return None
        store = JsonStore(path)
        data = await store.read()
        return Curriculum.model_validate(data)

    async def list_all(self) -> list[str]:
        return [p.stem for p in self._dir.glob("*.json")]
