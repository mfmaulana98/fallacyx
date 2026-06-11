"""Supabase-backed analysis-result cache, used as a fallback when Redis is unavailable.

Stores entries in the ``analysis_cache`` table (columns: ``cache_key``,
``result_json``, ``expires_at``) via PostgREST, and implements the same
:class:`~app.core.cache_backend.CacheBackend` interface as the Redis cache.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from app.core.cache_backend import CacheBackend
from app.core.config import settings

logger = logging.getLogger(__name__)

_TABLE = "analysis_cache"


def _headers(*, prefer: str = "return=minimal") -> dict[str, str]:
    return {
        "apikey": settings.supabase_service_role_key or "",
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": "application/json",
        "Prefer": prefer,
    }


def _table_url() -> str:
    return f"{settings.supabase_url}/rest/v1/{_TABLE}"


class SupabaseCache(CacheBackend):
    """``CacheBackend`` backed by the ``analysis_cache`` table in Supabase."""

    async def get(self, key: str) -> Any | None:
        if not settings.supabase_url or not settings.supabase_service_role_key:
            return None

        params = {
            "select": "result_json,expires_at",
            "cache_key": f"eq.{key}",
            "limit": "1",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(_table_url(), headers=_headers(), params=params)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Failed to read cache key %s from Supabase: %s", key, exc)
            return None

        rows = response.json()
        if not rows:
            return None

        row = rows[0]
        expires_at = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))
        if expires_at < datetime.now(timezone.utc):
            await self.invalidate(key)
            return None

        return row["result_json"]

    async def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        if not settings.supabase_url or not settings.supabase_service_role_key:
            logger.warning("Supabase credentials not configured; skipping cache write for %s", key)
            return

        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        body = {
            "cache_key": key,
            "result_json": value,
            "expires_at": expires_at.isoformat(),
        }
        params = {"on_conflict": "cache_key"}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    _table_url(),
                    headers=_headers(prefer="resolution=merge-duplicates,return=minimal"),
                    params=params,
                    json=body,
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Failed to write cache key %s to Supabase: %s", key, exc)

    async def invalidate(self, key: str) -> None:
        if not settings.supabase_url or not settings.supabase_service_role_key:
            return

        params = {"cache_key": f"eq.{key}"}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.delete(_table_url(), headers=_headers(), params=params)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Failed to invalidate cache key %s in Supabase: %s", key, exc)


async def cleanup_expired_cache() -> None:
    """Delete all expired entries from the ``analysis_cache`` table."""
    if not settings.supabase_url or not settings.supabase_service_role_key:
        return

    params = {"expires_at": f"lt.{datetime.now(timezone.utc).isoformat()}"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.delete(_table_url(), headers=_headers(), params=params)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("Failed to clean up expired cache entries in Supabase: %s", exc)
        return

    logger.info("Cleaned up expired entries in %s", _TABLE)
