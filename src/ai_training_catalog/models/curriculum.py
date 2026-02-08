"""Data models for generated training curricula."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from .resource import DifficultyLevel, SkillDomain


class LearningObjective(BaseModel):
    """A single measurable learning objective."""
    description: str
    bloom_level: str = "understand"  # remember / understand / apply / analyze / evaluate / create


class ModuleUnit(BaseModel):
    """A unit within a learning path, grouping related resources."""
    title: str
    description: str = ""
    resource_ids: list[str] = Field(default_factory=list)
    objectives: list[LearningObjective] = Field(default_factory=list)
    estimated_hours: float = 0.0
    order: int = 0


class LearningPath(BaseModel):
    """An ordered sequence of modules forming a coherent learning journey."""
    id: str
    title: str
    description: str = ""
    target_audience: str = ""
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    domains: list[SkillDomain] = Field(default_factory=list)
    modules: list[ModuleUnit] = Field(default_factory=list)
    total_estimated_hours: float = 0.0
    prerequisites: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0"

    def recalculate_hours(self) -> None:
        self.total_estimated_hours = sum(m.estimated_hours for m in self.modules)


class Curriculum(BaseModel):
    """A complete training programme made up of multiple learning paths."""
    id: str
    title: str
    description: str = ""
    learning_paths: list[LearningPath] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_catalog_hash: str = ""
    metadata: dict = Field(default_factory=dict)

    @property
    def total_hours(self) -> float:
        return sum(p.total_estimated_hours for p in self.learning_paths)
