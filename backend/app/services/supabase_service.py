"""Persistence helpers for the Supabase ``fallacy_analyses`` table."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def _supabase_headers() -> dict[str, str]:
    return {
        "apikey": settings.supabase_service_role_key or "",
        "Authorization": f"Bearer {settings.supabase_service_role_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }


async def save_fallacy_analysis(
    *,
    analysis_id: str,
    input_content: str,
    fallacies: list[dict[str, Any]],
    overall_assessment: str,
    is_clean: bool,
    analysis_duration_ms: int,
    model_used: str,
    metadata: dict[str, Any],
    input_type: str = "text",
) -> None:
    """Insert a completed analysis into the ``fallacy_analyses`` table via PostgREST."""

    if not settings.supabase_url or not settings.supabase_service_role_key:
        logger.warning("Supabase credentials not configured; skipping persistence of analysis %s", analysis_id)
        return

    url = f"{settings.supabase_url}/rest/v1/fallacy_analyses"
    body = {
        "id": analysis_id,
        "input_type": input_type,
        "input_content": input_content,
        "fallacies_found": fallacies,
        "analysis_duration_ms": analysis_duration_ms,
        "model_used": model_used,
        "metadata": {
            **metadata,
            "overall_assessment": overall_assessment,
            "is_clean": is_clean,
        },
    }

    logger.info("Saving analysis %s to Supabase", analysis_id)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=_supabase_headers(), json=body)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.error("Failed to save analysis %s to Supabase: %s", analysis_id, exc)
        raise

    logger.info("Saved analysis %s to Supabase", analysis_id)


async def get_cached_youtube_analysis(video_id: str, mode: str) -> dict[str, Any] | None:
    """Return the most recent stored YouTube analysis for ``video_id``/``mode``, if any."""

    if not settings.supabase_url or not settings.supabase_service_role_key:
        return None

    url = f"{settings.supabase_url}/rest/v1/fallacy_analyses"
    params = {
        "input_type": "eq.youtube",
        "metadata->>video_id": f"eq.{video_id}",
        "metadata->>mode": f"eq.{mode}",
        "order": "created_at.desc",
        "limit": "1",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=_supabase_headers(), params=params)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        logger.warning("Failed to query cached YouTube analysis for %s: %s", video_id, exc)
        return None

    rows = response.json()
    return rows[0] if rows else None
