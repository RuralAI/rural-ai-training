"""Atomic, async-safe JSON file storage."""

from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path
from typing import Any, Callable


class JsonStore:
    """Read / write JSON files with atomic writes and async locking."""

    def __init__(self, file_path: Path) -> None:
        self._path = file_path
        self._lock = asyncio.Lock()

    @property
    def path(self) -> Path:
        return self._path

    def _read_sync(self) -> dict[str, Any]:
        if not self._path.exists() or self._path.stat().st_size == 0:
            return {}
        return json.loads(self._path.read_text(encoding="utf-8"))

    def _write_sync(self, data: dict[str, Any]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(
            dir=self._path.parent, suffix=".tmp", prefix=".store_"
        )
        try:
            with open(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            Path(tmp).replace(self._path)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise

    async def read(self) -> dict[str, Any]:
        """Load the JSON file. Returns ``{}`` if missing or empty."""
        async with self._lock:
            return self._read_sync()

    async def write(self, data: dict[str, Any]) -> None:
        """Atomically write *data* to the JSON file."""
        async with self._lock:
            self._write_sync(data)

    async def update(self, transform: Callable[[dict[str, Any]], dict[str, Any]]) -> None:
        """Read, apply *transform*, and write back atomically.

        *transform* must be a **synchronous** callable.
        """
        async with self._lock:
            current = self._read_sync()
            updated = transform(current)
            self._write_sync(updated)
