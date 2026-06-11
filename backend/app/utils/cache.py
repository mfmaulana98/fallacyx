"""A small in-process async TTL cache used to avoid re-running expensive pipelines."""

from __future__ import annotations

import asyncio
import time
from typing import Generic, TypeVar

T = TypeVar("T")


class TTLCache(Generic[T]):
    """An async-safe in-memory cache where entries expire after ``ttl_seconds``."""

    def __init__(self, ttl_seconds: float) -> None:
        self._ttl_seconds = ttl_seconds
        self._store: dict[str, tuple[float, T]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> T | None:
        async with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None

            expires_at, value = entry
            if expires_at < time.monotonic():
                del self._store[key]
                return None

            return value

    async def set(self, key: str, value: T) -> None:
        async with self._lock:
            self._store[key] = (time.monotonic() + self._ttl_seconds, value)

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._store.pop(key, None)
