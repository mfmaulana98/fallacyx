"""End-to-end orchestrator: YouTube URL -> transcript -> fallacy verdict.

Drives the full examination pipeline (validate -> cache check -> metadata ->
download -> transcribe -> analyze -> merge -> persist -> cache -> cleanup),
reporting progress through an ``asyncio.Queue`` consumed by an SSE endpoint.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Literal

from redis import asyncio as aioredis

from app.core.config import settings
from app.core.prompts import STRICT_JSON_REMINDER, build_youtube_prompt
from app.services import youtube_service
from app.services.supabase_service import save_fallacy_analysis
from app.services.vllm_service import VLLMResponseError, VLLMTimeoutError, generate_completion
from app.services.whisper_service import WhisperTranscriptionError, transcribe_audio
from app.services.youtube_service import YouTubeExtractionError, YouTubeUnavailableError

logger = logging.getLogger(__name__)

MAX_GENERATION_ATTEMPTS = 2
CONFIDENCE_THRESHOLD = 0.6

_CODE_FENCE_PATTERN = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)
_CACHE_KEY_PREFIX = "fallacyx:youtube"


class PipelineError(Exception):
    """A pipeline failure with an HTTP-style status code for the SSE endpoint."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


@dataclass(frozen=True)
class PipelineProgress:
    """A single progress update emitted onto the pipeline's progress queue."""

    step: str
    percent: int
    message: str


@dataclass
class AnalysisResult:
    """The final, persisted result of a YouTube fallacy examination."""

    id: str
    video_id: str
    video_title: str
    video_duration_seconds: int
    transcript: str
    fallacies: list[dict[str, Any]]
    overall_assessment: str
    is_clean: bool
    mode: str
    language: str
    model_used: str
    analysis_duration_ms: int
    created_at: str
    cached: bool = False

    @property
    def total_fallacies(self) -> int:
        return len(self.fallacies)


def _redis_cache_key(video_id: str, mode: str) -> str:
    return f"{_CACHE_KEY_PREFIX}:{video_id}:{mode}"


async def _get_cached_result(video_id: str, mode: str) -> AnalysisResult | None:
    """Look up a previously cached analysis for ``video_id``/``mode`` in Redis."""

    try:
        client = aioredis.from_url(settings.redis_url)
    except Exception:
        logger.warning("Failed to construct Redis client", exc_info=True)
        return None

    try:
        raw = await client.get(_redis_cache_key(video_id, mode))
    except Exception:
        logger.warning("Redis unavailable while checking cache for %s", video_id, exc_info=True)
        return None
    finally:
        await client.aclose()

    if raw is None:
        return None

    try:
        data = json.loads(raw)
        data["cached"] = True
        return AnalysisResult(**data)
    except (json.JSONDecodeError, TypeError, KeyError):
        logger.warning("Failed to parse cached result for %s", video_id, exc_info=True)
        return None


async def _set_cached_result(video_id: str, mode: str, result: AnalysisResult) -> None:
    """Persist ``result`` in Redis under a 24h TTL."""

    try:
        client = aioredis.from_url(settings.redis_url)
    except Exception:
        logger.warning("Failed to construct Redis client", exc_info=True)
        return

    try:
        payload = json.dumps(asdict(result), ensure_ascii=False)
        await client.set(
            _redis_cache_key(video_id, mode),
            payload,
            ex=int(settings.youtube_cache_ttl_seconds),
        )
    except Exception:
        logger.warning("Failed to cache result for %s in Redis", video_id, exc_info=True)
    finally:
        await client.aclose()


def _extract_json(raw: str) -> dict:
    """Strip optional markdown code fences and parse the model output as JSON."""

    cleaned = _CODE_FENCE_PATTERN.sub("", raw.strip())
    return json.loads(cleaned)


async def _generate_fallacy_report(
    prompt: str, language: Literal["id", "en"], video_id: str
) -> dict:
    """Call vLLM, retrying once with a stricter JSON reminder on parse failure."""

    parsed: dict | None = None

    for attempt in range(1, MAX_GENERATION_ATTEMPTS + 1):
        current_prompt = prompt
        if attempt > 1:
            current_prompt = f"{prompt}\n\n{STRICT_JSON_REMINDER[language]}"
            logger.warning(
                "Retrying vLLM call for video %s with stricter JSON instructions (attempt %d)",
                video_id,
                attempt,
            )

        try:
            raw_output = await generate_completion(current_prompt)
        except (VLLMTimeoutError, VLLMResponseError) as exc:
            logger.error("vLLM error analyzing video %s: %s", video_id, exc)
            raise PipelineError(
                503, "The examination service is currently unavailable. Please try again shortly."
            ) from exc

        try:
            parsed = _extract_json(raw_output)
            break
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning(
                "Failed to parse JSON from vLLM output for video %s on attempt %d: %s",
                video_id,
                attempt,
                exc,
            )

    if parsed is None:
        raise PipelineError(
            503, "The examination service returned an invalid response. Please try again."
        )

    return parsed


async def analyze_youtube(url: str, mode: str, progress_queue: asyncio.Queue) -> AnalysisResult:
    """Run the full YouTube examination pipeline, reporting progress on ``progress_queue``.

    Raises:
        PipelineError: on any recoverable failure, carrying an HTTP-style status code
            and a user-facing detail message.
    """

    pipeline_start = time.perf_counter()
    last_percent = 0
    audio_path: str | None = None

    async def emit(step: str, percent: int, message: str) -> None:
        nonlocal last_percent
        last_percent = percent
        await progress_queue.put(PipelineProgress(step=step, percent=percent, message=message))

    try:
        # 1. Validate URL and extract video ID
        step_start = time.perf_counter()
        await emit("validate", 2, "Validating the submitted URL...")
        video_id = youtube_service.extract_video_id(url)
        if video_id is None:
            raise PipelineError(
                400,
                "The supplied URL is not a valid YouTube watch, youtu.be, shorts, or live link.",
            )
        logger.info(
            "Step 'validate' done in %.2fs (video_id=%s)", time.perf_counter() - step_start, video_id
        )

        # 2. Check Redis cache
        step_start = time.perf_counter()
        await emit("cache_check", 5, "Checking if this video has already been examined...")
        cached_result = await _get_cached_result(video_id, mode)
        if cached_result is not None:
            logger.info(
                "Step 'cache_check' done in %.2fs (cache hit for %s)",
                time.perf_counter() - step_start,
                video_id,
            )
            await emit("done", 100, "Retrieved a previously recorded verdict.")
            return cached_result
        logger.info(
            "Step 'cache_check' done in %.2fs (cache miss for %s)",
            time.perf_counter() - step_start,
            video_id,
        )

        # 3. Get video metadata
        step_start = time.perf_counter()
        await emit("metadata", 10, "Fetching video information...")
        try:
            video_info = await youtube_service.get_video_info(url)
        except YouTubeUnavailableError as exc:
            raise PipelineError(
                404, "The video is private, deleted, or otherwise unavailable."
            ) from exc
        except YouTubeExtractionError as exc:
            raise PipelineError(
                502, "Could not retrieve information about this video. Please try again later."
            ) from exc

        if video_info.duration_seconds > settings.youtube_max_duration_seconds:
            max_hours = settings.youtube_max_duration_seconds / 3600
            raise PipelineError(
                400, f"The video is too long to examine (maximum {max_hours:.0f} hours)."
            )
        logger.info(
            "Step 'metadata' done in %.2fs (title=%r, duration=%ds)",
            time.perf_counter() - step_start,
            video_info.title,
            video_info.duration_seconds,
        )

        # 4. Download audio
        step_start = time.perf_counter()
        await emit("downloading_audio", 20, "Extracting audio from the video...")
        try:
            audio_path = await youtube_service.download_audio(url, video_id)
        except YouTubeUnavailableError as exc:
            raise PipelineError(
                404, "The video is private, deleted, or otherwise unavailable."
            ) from exc
        except YouTubeExtractionError as exc:
            raise PipelineError(
                502, "Failed to extract audio from this video. Please try again later."
            ) from exc
        logger.info(
            "Step 'downloading_audio' done in %.2fs (path=%s)",
            time.perf_counter() - step_start,
            audio_path,
        )

        # 5. Transcribe audio
        step_start = time.perf_counter()
        await emit("transcribing", 40, "Transcribing the audio with Whisper Large-v3...")
        try:
            transcription = await transcribe_audio(audio_path)
        except WhisperTranscriptionError as exc:
            raise PipelineError(500, f"Audio transcription failed: {exc}") from exc

        if not transcription.text.strip():
            raise PipelineError(422, "No speech could be detected in this video.")
        logger.info(
            "Step 'transcribing' done in %.2fs (chars=%d, segments=%d)",
            time.perf_counter() - step_start,
            len(transcription.text),
            len(transcription.segments),
        )

        language: Literal["id", "en"] = (
            "id" if (transcription.language or "id").lower().startswith("id") else "en"
        )

        # 6. Send transcript to vLLM with timestamp-aware prompt
        step_start = time.perf_counter()
        await emit("analyzing", 65, "Examining the transcript for fallacies...")
        segments = [(seg.start, seg.end, seg.text) for seg in transcription.segments]
        prompt = build_youtube_prompt(segments, mode=mode)
        parsed = await _generate_fallacy_report(prompt, language, video_id)
        logger.info("Step 'analyzing' done in %.2fs", time.perf_counter() - step_start)

        # 7. Merge fallacy results with transcript timestamps
        step_start = time.perf_counter()
        await emit("merging", 85, "Cross-referencing findings with the transcript...")
        fallacies = [
            f for f in parsed.get("fallacies", []) if f.get("confidence", 0) >= CONFIDENCE_THRESHOLD
        ]
        for fallacy in fallacies:
            fallacy.setdefault("timestamp_seconds", 0.0)
        overall_assessment = parsed.get("overall_assessment", "")
        is_clean = parsed.get("is_clean", len(fallacies) == 0)
        logger.info(
            "Step 'merging' done in %.2fs (%d fallacies)",
            time.perf_counter() - step_start,
            len(fallacies),
        )

        analysis_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        analysis_duration_ms = int((time.perf_counter() - pipeline_start) * 1000)

        result = AnalysisResult(
            id=analysis_id,
            video_id=video_id,
            video_title=video_info.title,
            video_duration_seconds=video_info.duration_seconds,
            transcript=transcription.text,
            fallacies=fallacies,
            overall_assessment=overall_assessment,
            is_clean=is_clean,
            mode=mode,
            language=language,
            model_used=settings.vllm_model_name,
            analysis_duration_ms=analysis_duration_ms,
            created_at=created_at,
            cached=False,
        )

        # 8. Save to Supabase
        step_start = time.perf_counter()
        await emit("saving", 92, "Recording the verdict...")
        try:
            await save_fallacy_analysis(
                analysis_id=analysis_id,
                input_content=transcription.text,
                fallacies=fallacies,
                overall_assessment=overall_assessment,
                is_clean=is_clean,
                analysis_duration_ms=analysis_duration_ms,
                model_used=settings.vllm_model_name,
                metadata={
                    "mode": mode,
                    "language": language,
                    "video_id": video_id,
                    "video_title": video_info.title,
                    "video_duration_seconds": video_info.duration_seconds,
                    "overall_assessment": overall_assessment,
                    "is_clean": is_clean,
                },
                input_type="youtube",
            )
        except Exception:  # noqa: BLE001 - persistence failures shouldn't hide the verdict
            logger.exception("Failed to persist YouTube analysis %s to Supabase", analysis_id)
        logger.info("Step 'saving' done in %.2fs", time.perf_counter() - step_start)

        # 9. Save to Redis cache (TTL: 24h)
        step_start = time.perf_counter()
        await emit("caching", 97, "Caching the verdict for future requests...")
        await _set_cached_result(video_id, mode, result)
        logger.info("Step 'caching' done in %.2fs", time.perf_counter() - step_start)

        await emit("done", 100, "The verdict is ready.")
        logger.info(
            "YouTube pipeline for %s completed in %.2fs total",
            video_id,
            time.perf_counter() - pipeline_start,
        )
        return result

    except PipelineError as exc:
        logger.warning("YouTube pipeline for %s failed: %s", url, exc.detail)
        await emit("error", last_percent, exc.detail)
        raise
    except Exception as exc:  # noqa: BLE001 - normalize unexpected failures for the SSE endpoint
        logger.exception("Unexpected error in YouTube pipeline for %s", url)
        await emit("error", last_percent, "An unexpected error occurred while examining this video.")
        raise PipelineError(
            500, "An unexpected error occurred while examining this video."
        ) from exc
    finally:
        # 10. Cleanup temporary audio file
        youtube_service.cleanup_audio_file(audio_path)
        await progress_queue.put(None)
