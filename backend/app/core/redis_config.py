"""Redis connection management for the analysis-result cache.

Exposes a singleton ``redis.asyncio`` client via :func:`get_redis_client` and a
:func:`ping_redis` health check. ``RedisCache`` adapts that client to the
:class:`~app.core.cache_backend.CacheBackend` interface, while ``DummyCache``
provides a no-op implementation used when Redis is unavailable.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import redis.asyncio as aioredis

from app.core.cache_backend import CacheBackend
from app.core.config import settings

logger = logging.getLogger(__name__)

_client: aioredis.Redis | None = None


class DummyCache(CacheBackend):
    """No-op cache backend used when Redis is unavailable."""

    async def get(self, key: str) -> Any | None:
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        return None

    async def invalidate(self, key: str) -> None:
        return None


class RedisCache(CacheBackend):
    """``CacheBackend`` backed by Redis, storing values as JSON strings."""

    def __init__(self, client: aioredis.Redis) -> None:
        self._client = client

    async def get(self, key: str) -> Any | None:
        raw = await self._client.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        await self._client.set(key, json.dumps(value), ex=ttl_seconds)

    async def invalidate(self, key: str) -> None:
        await self._client.delete(key)


def get_redis_client() -> aioredis.Redis | DummyCache:
    """Return a singleton Redis client, or a :class:`DummyCache` if one cannot be created."""
    global _client

    if _client is not None:
        return _client

    try:
        _client = aioredis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    except Exception:
        logger.warning("Failed to create Redis client; falling back to DummyCache", exc_info=True)
        return DummyCache()

    return _client


async def ping_redis() -> bool:
    """Return ``True`` if Redis responds to a PING, ``False`` otherwise."""
    client = get_redis_client()
    if isinstance(client, DummyCache):
        return False

    try:
        return bool(await client.ping())
    except Exception:
        logger.warning("Redis ping failed", exc_info=True)
        return False
