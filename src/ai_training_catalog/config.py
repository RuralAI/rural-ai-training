"""Central configuration loaded from environment variables and .env file."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings. All values can be overridden via environment
    variables prefixed with ``ATC_`` or via a ``.env`` file."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="ATC_")

    # --- API keys ---
    google_api_key: str = ""
    google_cse_id: str = ""
    github_token: str = ""

    # --- Operational ---
    max_concurrent_requests: int = 10
    request_timeout_seconds: int = 30
    rate_limit_per_second: float = 2.0
    cache_ttl_hours: int = 24
    min_quality_score: float = 0.3

    # --- Storage paths ---
    data_dir: Path = Field(default=Path("data"))
    catalog_path: Path = Field(default=Path("data/catalog.json"))
    curricula_dir: Path = Field(default=Path("data/curricula"))
    cache_dir: Path = Field(default=Path("data/cache"))

    # --- Curriculum generation ---
    max_resources_per_module: int = 5
    max_hours_beginner_path: float = 20.0
    provider_diversity_cap: float = 0.4  # no single provider > 40% of a path

    def ensure_dirs(self) -> None:
        """Create data directories if they don't exist."""
        for d in (self.data_dir, self.curricula_dir, self.cache_dir):
            d.mkdir(parents=True, exist_ok=True)
