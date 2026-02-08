"""Core domain model for a discovered AI training resource."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class SkillCategory(str, Enum):
    """Top-level division: technical vs. business."""
    TECHNICAL = "technical"
    BUSINESS = "business"


class SkillDomain(str, Enum):
    """Specific skill domains covered by training content."""
    # Technical
    ML_BASICS = "ml_basics"
    DEEP_LEARNING = "deep_learning"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"
    MLOPS = "mlops"
    GENERATIVE_AI = "generative_ai"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    DATA_ENGINEERING = "data_engineering"
    # Business
    AI_STRATEGY = "ai_strategy"
    AI_ETHICS = "ai_ethics"
    AI_PROJECT_MANAGEMENT = "ai_project_management"
    AI_ROI = "ai_roi"
    AI_GOVERNANCE = "ai_governance"


DOMAIN_CATEGORY: dict[SkillDomain, SkillCategory] = {
    SkillDomain.ML_BASICS: SkillCategory.TECHNICAL,
    SkillDomain.DEEP_LEARNING: SkillCategory.TECHNICAL,
    SkillDomain.NLP: SkillCategory.TECHNICAL,
    SkillDomain.COMPUTER_VISION: SkillCategory.TECHNICAL,
    SkillDomain.MLOPS: SkillCategory.TECHNICAL,
    SkillDomain.GENERATIVE_AI: SkillCategory.TECHNICAL,
    SkillDomain.REINFORCEMENT_LEARNING: SkillCategory.TECHNICAL,
    SkillDomain.DATA_ENGINEERING: SkillCategory.TECHNICAL,
    SkillDomain.AI_STRATEGY: SkillCategory.BUSINESS,
    SkillDomain.AI_ETHICS: SkillCategory.BUSINESS,
    SkillDomain.AI_PROJECT_MANAGEMENT: SkillCategory.BUSINESS,
    SkillDomain.AI_ROI: SkillCategory.BUSINESS,
    SkillDomain.AI_GOVERNANCE: SkillCategory.BUSINESS,
}


class ContentType(str, Enum):
    COURSE = "course"
    TUTORIAL = "tutorial"
    DOCUMENTATION = "documentation"
    VIDEO_SERIES = "video_series"
    BOOK = "book"
    PAPER = "paper"
    BLOG_SERIES = "blog_series"
    INTERACTIVE_NOTEBOOK = "interactive_notebook"
    CERTIFICATION_PREP = "certification_prep"


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class LicenseType(str, Enum):
    CC_BY = "cc_by"
    CC_BY_SA = "cc_by_sa"
    CC_BY_NC = "cc_by_nc"
    MIT = "mit"
    APACHE_2 = "apache_2"
    FREE_ACCESS = "free_access"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Resource model
# ---------------------------------------------------------------------------

def _resource_id(url: str) -> str:
    """Deterministic ID from the canonical URL."""
    return hashlib.sha256(url.strip().rstrip("/").lower().encode()).hexdigest()[:16]


class Resource(BaseModel):
    """A single AI training resource discovered on the web."""

    id: str = Field(default="", description="Derived from URL hash; set automatically")
    url: str
    title: str
    description: str = ""
    provider: str = ""
    domains: list[SkillDomain] = Field(default_factory=list)
    content_type: ContentType = ContentType.TUTORIAL
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    license_type: LicenseType = LicenseType.UNKNOWN
    language: str = "en"
    estimated_hours: float | None = None
    prerequisites: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_verified_at: datetime | None = None
    is_active: bool = True
    raw_metadata: dict = Field(default_factory=dict)

    def model_post_init(self, _context: object) -> None:
        if not self.id:
            self.id = _resource_id(self.url)
