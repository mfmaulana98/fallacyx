"""Health check endpoints for FallacyX backend.

Provides liveness, deep dependency, and GPU telemetry checks.
All responses are plain JSON (Prometheus-friendly key/value structures).
"""

from __future__ import annotations

import asyncio
import os
import time
from datetime import datetime, timezone
from typing import Literal, Optional

import httpx
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/health", tags=["health"])

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

VLLM_HEALTH_URL = os.getenv("VLLM_HEALTH_URL", "http://vllm:8000/health")
WHISPER_HEALTH_URL = os.getenv("WHISPER_HEALTH_URL", "http://whisper:8001/health")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

CHECK_TIMEOUT_SECONDS = 5.0

ComponentStatus = Literal["healthy", "degraded", "down"]
OverallStatus = Literal["healthy", "degraded", "critical"]


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    timestamp: str
    version: str = APP_VERSION


class ComponentHealth(BaseModel):
    name: str
    status: ComponentStatus
    response_time_ms: float
    detail: Optional[str] = None


class DetailedHealthResponse(BaseModel):
    status: OverallStatus
    timestamp: str
    version: str = APP_VERSION
    components: list[ComponentHealth]


class GPUHealthResponse(BaseModel):
    status: Literal["ok", "unavailable"]
    timestamp: str
    gpu_name: Optional[str] = None
    vram_total_mb: Optional[float] = None
    vram_used_mb: Optional[float] = None
    vram_free_mb: Optional[float] = None
    gpu_utilization_pct: Optional[float] = None
    temperature_celsius: Optional[float] = None
    model_loaded: Optional[str] = None
    detail: Optional[str] = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _timed(coro_factory) -> tuple[ComponentStatus, float, Optional[str]]:
    """Run a check coroutine, capturing elapsed time and status/detail."""
    start = time.perf_counter()
    try:
        detail = await asyncio.wait_for(coro_factory(), timeout=CHECK_TIMEOUT_SECONDS)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return "healthy", elapsed_ms, detail
    except asyncio.TimeoutError:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return "down", elapsed_ms, f"timed out after {CHECK_TIMEOUT_SECONDS}s"
    except Exception as exc:  # noqa: BLE001 - surface any dependency failure as "down"
        elapsed_ms = (time.perf_counter() - start) * 1000
        return "down", elapsed_ms, str(exc)


async def _check_http_service(url: str) -> Optional[str]:
    async with httpx.AsyncClient(timeout=CHECK_TIMEOUT_SECONDS) as client:
        response = await client.get(url)
        response.raise_for_status()
    return None


async def _check_vllm() -> Optional[str]:
    return await _check_http_service(VLLM_HEALTH_URL)


async def _check_whisper() -> Optional[str]:
    return await _check_http_service(WHISPER_HEALTH_URL)


async def _check_qdrant() -> Optional[str]:
    from qdrant_client import AsyncQdrantClient

    client = AsyncQdrantClient(url=QDRANT_URL)
    try:
        collections = await client.get_collections()
        return f"{len(collections.collections)} collection(s)"
    finally:
        await client.close()


async def _check_redis() -> Optional[str]:
    from redis import asyncio as aioredis

    client = aioredis.from_url(REDIS_URL)
    try:
        await client.ping()
        return None
    finally:
        await client.aclose()


async def _check_supabase() -> Optional[str]:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("Supabase credentials are not configured")

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    async with httpx.AsyncClient(timeout=CHECK_TIMEOUT_SECONDS) as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/",
            headers=headers,
        )
        response.raise_for_status()
    return None


@router.get("", response_model=HealthResponse, summary="Liveness probe")
async def health() -> HealthResponse:
    """Fast liveness check. Should respond in well under 100ms."""
    return HealthResponse(timestamp=_now_iso())


@router.get(
    "/detailed",
    response_model=DetailedHealthResponse,
    summary="Deep dependency health check",
)
async def health_detailed() -> DetailedHealthResponse:
    """Concurrently checks every downstream dependency."""
    checks = {
        "vllm": _check_vllm,
        "whisper": _check_whisper,
        "qdrant": _check_qdrant,
        "redis": _check_redis,
        "supabase": _check_supabase,
    }

    results = await asyncio.gather(*(_timed(fn) for fn in checks.values()))

    components: list[ComponentHealth] = []
    for (name, _), (status, elapsed_ms, detail) in zip(checks.items(), results):
        components.append(
            ComponentHealth(
                name=name,
                status=status,
                response_time_ms=round(elapsed_ms, 2),
                detail=detail,
            )
        )

    statuses = {c.name: c.status for c in components}

    critical_components = {"vllm", "supabase"}
    if any(statuses[name] == "down" for name in critical_components):
        overall: OverallStatus = "critical"
    elif any(status == "down" for status in statuses.values()):
        overall = "degraded"
    else:
        overall = "healthy"

    return DetailedHealthResponse(
        status=overall,
        timestamp=_now_iso(),
        components=components,
    )


@router.get("/gpu", response_model=GPUHealthResponse, summary="AMD GPU telemetry")
async def health_gpu() -> GPUHealthResponse:
    """Reports AMD GPU memory/utilization/temperature via rocm-smi, if available."""
    try:
        gpu_info = await asyncio.wait_for(_read_amd_gpu_info(), timeout=CHECK_TIMEOUT_SECONDS)
        return GPUHealthResponse(status="ok", timestamp=_now_iso(), **gpu_info)
    except asyncio.TimeoutError:
        return GPUHealthResponse(
            status="unavailable",
            timestamp=_now_iso(),
            detail=f"rocm-smi timed out after {CHECK_TIMEOUT_SECONDS}s",
        )
    except Exception as exc:  # noqa: BLE001
        return GPUHealthResponse(
            status="unavailable",
            timestamp=_now_iso(),
            detail=str(exc),
        )


async def _read_amd_gpu_info() -> dict:
    """Query rocm-smi for VRAM, utilization, and temperature on the MI300X."""
    proc = await asyncio.create_subprocess_exec(
        "rocm-smi",
        "--showmeminfo",
        "vram",
        "--showuse",
        "--showtemp",
        "--showproductname",
        "--json",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"rocm-smi failed: {stderr.decode().strip()}")

    import json

    raw = json.loads(stdout.decode())
    card_key = next(iter(raw.keys()))
    card = raw[card_key]

    vram_total_bytes = float(card.get("VRAM Total Memory (B)", 0))
    vram_used_bytes = float(card.get("VRAM Total Used Memory (B)", 0))

    return {
        "gpu_name": card.get("Card series") or card.get("Card Series"),
        "vram_total_mb": round(vram_total_bytes / (1024 * 1024), 2) if vram_total_bytes else None,
        "vram_used_mb": round(vram_used_bytes / (1024 * 1024), 2) if vram_used_bytes else None,
        "vram_free_mb": (
            round((vram_total_bytes - vram_used_bytes) / (1024 * 1024), 2)
            if vram_total_bytes
            else None
        ),
        "gpu_utilization_pct": _parse_percent(card.get("GPU use (%)")),
        "temperature_celsius": _parse_float(card.get("Temperature (Sensor edge) (C)")),
        "model_loaded": os.getenv("VLLM_MODEL_NAME", "meta-llama/Meta-Llama-3-70B-Instruct"),
    }


def _parse_percent(value) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(str(value).replace("%", "").strip())
    except ValueError:
        return None


def _parse_float(value) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None
