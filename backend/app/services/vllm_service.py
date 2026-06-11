"""Client for the local vLLM OpenAI-compatible inference server."""

from __future__ import annotations

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class VLLMTimeoutError(Exception):
    """Raised when the vLLM server does not respond within the configured timeout."""


class VLLMResponseError(Exception):
    """Raised when the vLLM server returns an error or an unexpected response shape."""


async def generate_completion(prompt: str) -> str:
    """Send a prompt to the vLLM chat completions endpoint and return the raw text content."""

    url = f"{settings.vllm_base_url}/v1/chat/completions"
    payload = {
        "model": settings.vllm_model_name,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": settings.vllm_max_tokens,
        "temperature": settings.vllm_temperature,
        "top_p": settings.vllm_top_p,
    }

    logger.info("Calling vLLM at %s (model=%s)", url, settings.vllm_model_name)

    try:
        async with httpx.AsyncClient(timeout=settings.vllm_timeout_seconds) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        logger.error("vLLM request timed out after %.0fs", settings.vllm_timeout_seconds)
        raise VLLMTimeoutError(
            f"vLLM did not respond within {settings.vllm_timeout_seconds:.0f}s"
        ) from exc
    except httpx.HTTPStatusError as exc:
        logger.error(
            "vLLM returned HTTP %s: %s", exc.response.status_code, exc.response.text[:500]
        )
        raise VLLMResponseError(f"vLLM returned HTTP {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        logger.error("vLLM request failed: %s", exc)
        raise VLLMResponseError(str(exc)) from exc

    data = response.json()
    try:
        content: str = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        logger.error("Unexpected vLLM response shape: %s", data)
        raise VLLMResponseError("Unexpected response structure from vLLM") from exc

    logger.info("vLLM responded with %d characters", len(content))
    return content
