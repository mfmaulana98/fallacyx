"""Selects the analysis-result cache backend for the application.

If ``REDIS_URL`` is configured and reachable, the Redis-backed cache is used.
Otherwise the app falls back to the Supabase-backed ``analysis_cache`` table.
Both implement :class:`~app.core.cache_backend.CacheBackend`.
"""

from __future__ import annotations

import logging
import os

from app.core.cache_backend import CacheBackend
from app.core.redis_config import RedisCache, get_redis_client, ping_redis
from app.services.supabase_cache import SupabaseCache

logger = logging.getLogger(__name__)

_backend: CacheBackend | None = None


async def init_cache_backend() -> CacheBackend:
    """Pick and cache the backend to use, logging the decision once."""
    global _backend

    if os.getenv("REDIS_URL") and await ping_redis():
        logger.info("Cache backend: Redis")
        _backend = RedisCache(get_redis_client())
        return _backend

    logger.info("Cache backend: Supabase (analysis_cache table)")
    _backend = SupabaseCache()
    return _backend


async def get_cache_backend() -> CacheBackend:
    """Return the active cache backend, initializing it on first use."""
    if _backend is None:
        return await init_cache_backend()
    return _backend
