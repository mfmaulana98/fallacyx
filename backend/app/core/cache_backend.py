"""Shared interface implemented by all analysis-result cache backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class CacheBackend(ABC):
    """A key/value cache for JSON-serializable analysis results with TTL expiry."""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Return the cached value for ``key``, or ``None`` if missing/expired."""

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Store ``value`` under ``key``, expiring after ``ttl_seconds``."""

    @abstractmethod
    async def invalidate(self, key: str) -> None:
        """Remove ``key`` from the cache, if present."""
