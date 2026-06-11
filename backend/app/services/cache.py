"""Redis-backed cache for fallacy analysis results.

Falls back to a no-op (cache miss / skipped write) if Redis is unreachable,
so analysis requests never fail because of the cache layer.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import TypeVar

from pydantic import BaseModel, ValidationError
from redis import asyncio as aioredis
from redis.exceptions import RedisError

from app.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

CACHE_KEY_PREFIX = "fallacyx"
CACHE_KEY_PATTERN = f"{CACHE_KEY_PREFIX}:*"

# TTL per input type, in seconds. Audio uploads are unique per request and are
# never cached (ttl <= 0 means "do not cache").
CACHE_TTL_SECONDS: dict[str, int] = {
    "text": 60 * 60,  # 1 hour - text can repeat but isn't critical to cache long
    "url": 6 * 60 * 60,  # 6 hours - articles can be updated
    "youtube": 24 * 60 * 60,  # 24 hours - videos don't change
    "audio": 0,  # never cached
}

_client: aioredis.Redis | None = None


def _get_client() -> aioredis.Redis:
    """Lazily create the shared Redis client backed by a bounded connection pool."""

    global _client
    if _client is None:
        pool = aioredis.ConnectionPool.from_url(
            settings.redis_url, max_connections=10, decode_responses=True
        )
        _client = aioredis.Redis(connection_pool=pool)
    return _client


def generate_cache_key(input_type: str, content: str) -> str:
    """Build a deterministic cache key from the input type and content hash."""

    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return f"{CACHE_KEY_PREFIX}:{input_type}:{digest[:16]}"


async def get_cached_analysis(cache_key: str, model_cls: type[T]) -> T | None:
    """Return the cached analysis result, or None if missing, expired, or unavailable."""

    try:
        raw = await _get_client().get(cache_key)
    except RedisError as exc:
        logger.warning("Redis unavailable, skipping cache lookup for %s: %s", cache_key, exc)
        return None

    if raw is None:
        return None

    try:
        return model_cls.model_validate(json.loads(raw))
    except (json.JSONDecodeError, ValidationError) as exc:
        logger.warning("Failed to deserialize cached analysis %s: %s", cache_key, exc)
        return None


async def cache_analysis(cache_key: str, result: BaseModel, ttl_seconds: int) -> None:
    """Store an analysis result as JSON with the given TTL. No-op if ttl_seconds <= 0."""

    if ttl_seconds <= 0:
        return

    try:
        await _get_client().set(cache_key, result.model_dump_json(), ex=ttl_seconds)
    except RedisError as exc:
        logger.warning("Redis unavailable, skipping cache write for %s: %s", cache_key, exc)


async def invalidate_cache(cache_key: str) -> None:
    """Remove a cached analysis result, if present."""

    try:
        await _get_client().delete(cache_key)
    except RedisError as exc:
        logger.warning("Redis unavailable, skipping cache invalidation for %s: %s", cache_key, exc)


async def get_cache_stats() -> dict:
    """Return cache hit/miss counters and the number of cached analysis keys.

    Hits/misses come from Redis' server-wide keyspace stats (``INFO stats``),
    so they reflect all keys, not only ``fallacyx:*`` ones.
    """

    try:
        client = _get_client()
        info = await client.info("stats")

        total_keys = 0
        async for _ in client.scan_iter(match=CACHE_KEY_PATTERN, count=100):
            total_keys += 1

        return {
            "available": True,
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
            "total_keys": total_keys,
        }
    except RedisError as exc:
        logger.warning("Redis unavailable, cannot fetch cache stats: %s", exc)
        return {"available": False, "hits": 0, "misses": 0, "total_keys": 0}
