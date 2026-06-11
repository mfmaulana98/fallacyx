"""Endpoints for submitting raw text and YouTube videos to the fallacy examination pipeline."""

from __future__ import annotations

import json
import logging
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Literal

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import ValidationError

from app.core.prompts import STRICT_JSON_REMINDER, build_prompt, build_youtube_prompt
from app.core.config import settings
from app.models.request import TextAnalysisRequest, YouTubeAnalysisRequest
from app.models.response import AnalysisResponse, YouTubeAnalysisResponse
from app.services.supabase_service import get_cached_youtube_analysis, save_fallacy_analysis
from app.services.vllm_service import (
    VLLMResponseError,
    VLLMTimeoutError,
    generate_completion,
)
from app.services.whisper_service import WhisperTranscriptionError, transcribe_audio
from app.services.youtube_service import (
    VideoInfo,
    YouTubeExtractionError,
    YouTubeUnavailableError,
    cleanup_audio_file,
    download_audio,
    extract_video_id,
    get_video_info,
)
from app.utils.cache import TTLCache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyze", tags=["analyze"])

MIN_TEXT_LENGTH = 10
MAX_TEXT_LENGTH = 10_000
MAX_GENERATION_ATTEMPTS = 2
CONFIDENCE_THRESHOLD = 0.6

_youtube_result_cache: TTLCache[dict[str, Any]] = TTLCache(ttl_seconds=settings.youtube_cache_ttl_seconds)

_CODE_FENCE_PATTERN = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


def _extract_json(raw: str) -> dict:
    """Strip optional markdown code fences and parse the model output as JSON."""

    cleaned = _CODE_FENCE_PATTERN.sub("", raw.strip())
    return json.loads(cleaned)


@router.post(
    "/text",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit a piece of text for examination",
)
async def analyze_text(payload: TextAnalysisRequest) -> AnalysisResponse:
    text = payload.text.strip()

    if len(text) < MIN_TEXT_LENGTH:
        logger.warning("Rejected /analyze/text request: text too short (%d chars)", len(text))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Text must be at least {MIN_TEXT_LENGTH} characters long.",
        )

    if len(text) > MAX_TEXT_LENGTH:
        logger.warning("Rejected /analyze/text request: text too long (%d chars)", len(text))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Text must not exceed {MAX_TEXT_LENGTH} characters.",
        )

    logger.info("Building prompt (mode=%s, language=%s, chars=%d)", payload.mode, payload.language, len(text))
    prompt = build_prompt(text, mode=payload.mode)

    start_time = time.perf_counter()
    parsed: dict | None = None
    last_error: Exception | None = None

    for attempt in range(1, MAX_GENERATION_ATTEMPTS + 1):
        current_prompt = prompt
        if attempt > 1:
            current_prompt = f"{prompt}\n\n{STRICT_JSON_REMINDER[payload.language]}"
            logger.warning("Retrying vLLM call with stricter JSON instructions (attempt %d)", attempt)

        try:
            logger.info("Sending prompt to vLLM (attempt %d/%d)", attempt, MAX_GENERATION_ATTEMPTS)
            raw_output = await generate_completion(current_prompt)
        except VLLMTimeoutError as exc:
            logger.error("vLLM timeout on attempt %d: %s", attempt, exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="The examination service is taking too long to respond. Please try again shortly.",
            ) from exc
        except VLLMResponseError as exc:
            logger.error("vLLM error on attempt %d: %s", attempt, exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="The examination service is currently unavailable. Please try again shortly.",
            ) from exc

        try:
            parsed = _extract_json(raw_output)
            break
        except (json.JSONDecodeError, ValueError) as exc:
            last_error = exc
            logger.warning("Failed to parse JSON from vLLM output on attempt %d: %s", attempt, exc)

    if parsed is None:
        logger.error("Giving up after %d attempts; last error: %s", MAX_GENERATION_ATTEMPTS, last_error)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The examination service returned an invalid response. Please try again.",
        )

    duration_ms = int((time.perf_counter() - start_time) * 1000)
    logger.info("vLLM analysis completed in %dms", duration_ms)

    fallacies = [
        f for f in parsed.get("fallacies", []) if f.get("confidence", 0) >= CONFIDENCE_THRESHOLD
    ]
    overall_assessment = parsed.get("overall_assessment", "")
    is_clean = parsed.get("is_clean", len(fallacies) == 0)

    analysis_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    try:
        await save_fallacy_analysis(
            analysis_id=analysis_id,
            input_content=text,
            fallacies=fallacies,
            overall_assessment=overall_assessment,
            is_clean=is_clean,
            analysis_duration_ms=duration_ms,
            model_used=settings.vllm_model_name,
            metadata={"mode": payload.mode, "language": payload.language},
        )
    except Exception:  # noqa: BLE001 - persistence failures shouldn't hide the verdict
        logger.exception("Failed to persist analysis %s to Supabase", analysis_id)

    return AnalysisResponse(
        id=analysis_id,
        mode=payload.mode,
        language=payload.language,
        fallacies=fallacies,
        overall_assessment=overall_assessment,
        is_clean=is_clean,
        total_fallacies=len(fallacies),
        model_used=settings.vllm_model_name,
        analysis_duration_ms=duration_ms,
        created_at=created_at,
    )


def _sse_event(event: str, data: dict[str, Any]) -> str:
    """Format a single Server-Sent Event."""

    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _record_to_response_dict(record: dict[str, Any], *, cached: bool) -> dict[str, Any]:
    """Build a YouTubeAnalysisResponse-shaped dict from a stored ``fallacy_analyses`` row."""

    metadata = record.get("metadata") or {}
    fallacies = record.get("fallacies_found") or []

    return {
        "id": record["id"],
        "input_type": "youtube",
        "mode": metadata.get("mode", "quick"),
        "language": metadata.get("language", "id"),
        "video_id": metadata.get("video_id", ""),
        "video_title": metadata.get("video_title", ""),
        "video_duration_seconds": metadata.get("video_duration_seconds", 0),
        "transcript": record.get("input_content", ""),
        "fallacies": fallacies,
        "overall_assessment": metadata.get("overall_assessment", ""),
        "is_clean": metadata.get("is_clean", len(fallacies) == 0),
        "total_fallacies": len(fallacies),
        "model_used": record.get("model_used", settings.vllm_model_name),
        "analysis_duration_ms": record.get("analysis_duration_ms", 0),
        "created_at": record.get("created_at", datetime.now(timezone.utc).isoformat()),
        "cached": cached,
    }


async def _stream_cached_result(record: dict[str, Any]) -> AsyncIterator[str]:
    """Replay a previously computed YouTube analysis as an SSE stream."""

    yield _sse_event(
        "progress",
        {"stage": "cache_hit", "message": "This video has already been examined. Retrieving the verdict..."},
    )

    try:
        response_model = YouTubeAnalysisResponse(**_record_to_response_dict(record, cached=True))
    except ValidationError as exc:
        logger.error("Cached YouTube analysis %s failed validation: %s", record.get("id"), exc)
        yield _sse_event(
            "error",
            {"status_code": 500, "detail": "The cached verdict for this video is corrupted."},
        )
        return

    yield _sse_event("result", response_model.model_dump(mode="json"))


async def _run_youtube_pipeline(
    *,
    url: str,
    video_id: str,
    video_info: VideoInfo,
    payload: YouTubeAnalysisRequest,
    cache_key: str,
) -> AsyncIterator[str]:
    """Run the extract -> transcribe -> analyze pipeline, streaming progress as SSE."""

    audio_path: str | None = None
    try:
        yield _sse_event(
            "progress",
            {"stage": "downloading_audio", "message": "Extracting audio from the video..."},
        )

        try:
            audio_path = await download_audio(url, video_id)
        except YouTubeUnavailableError as exc:
            logger.warning("YouTube video %s became unavailable during download: %s", video_id, exc)
            yield _sse_event(
                "error",
                {"status_code": 404, "detail": "The video is private, deleted, or otherwise unavailable."},
            )
            return
        except YouTubeExtractionError as exc:
            logger.error("Audio extraction failed for %s: %s", video_id, exc)
            yield _sse_event(
                "error",
                {"status_code": 502, "detail": "Failed to extract audio from this video. Please try again later."},
            )
            return

        yield _sse_event(
            "progress",
            {"stage": "transcribing", "message": "Transcribing the audio with Whisper Large-v3..."},
        )

        try:
            transcription = await transcribe_audio(audio_path)
        except WhisperTranscriptionError as exc:
            logger.error("Whisper transcription failed for %s: %s", video_id, exc)
            yield _sse_event(
                "error",
                {"status_code": 500, "detail": f"Audio transcription failed: {exc}"},
            )
            return

        if not transcription.text.strip():
            yield _sse_event(
                "error",
                {"status_code": 422, "detail": "No speech could be detected in this video."},
            )
            return

        language: Literal["id", "en"] = (
            "id" if (transcription.language or "id").lower().startswith("id") else "en"
        )

        yield _sse_event(
            "progress",
            {"stage": "analyzing", "message": "Examining the transcript for fallacies..."},
        )

        segments = [(seg.start, seg.end, seg.text) for seg in transcription.segments]
        prompt = build_youtube_prompt(segments, mode=payload.mode)

        start_time = time.perf_counter()
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
                yield _sse_event(
                    "error",
                    {
                        "status_code": 503,
                        "detail": "The examination service is currently unavailable. Please try again shortly.",
                    },
                )
                return

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
            yield _sse_event(
                "error",
                {
                    "status_code": 503,
                    "detail": "The examination service returned an invalid response. Please try again.",
                },
            )
            return

        duration_ms = int((time.perf_counter() - start_time) * 1000)
        logger.info("vLLM analysis for video %s completed in %dms", video_id, duration_ms)

        fallacies = [
            f for f in parsed.get("fallacies", []) if f.get("confidence", 0) >= CONFIDENCE_THRESHOLD
        ]
        for fallacy in fallacies:
            fallacy.setdefault("timestamp_seconds", 0.0)

        overall_assessment = parsed.get("overall_assessment", "")
        is_clean = parsed.get("is_clean", len(fallacies) == 0)

        analysis_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        metadata = {
            "mode": payload.mode,
            "language": language,
            "video_id": video_id,
            "video_title": video_info.title,
            "video_duration_seconds": video_info.duration_seconds,
            "overall_assessment": overall_assessment,
            "is_clean": is_clean,
        }

        record = {
            "id": analysis_id,
            "input_content": transcription.text,
            "fallacies_found": fallacies,
            "analysis_duration_ms": duration_ms,
            "model_used": settings.vllm_model_name,
            "metadata": metadata,
            "created_at": created_at,
        }

        try:
            response_model = YouTubeAnalysisResponse(**_record_to_response_dict(record, cached=False))
        except ValidationError as exc:
            logger.error("YouTube analysis result for video %s failed validation: %s", video_id, exc)
            yield _sse_event(
                "error",
                {"status_code": 503, "detail": "The examination service returned a malformed result."},
            )
            return

        yield _sse_event("progress", {"stage": "saving", "message": "Recording the verdict..."})

        try:
            await save_fallacy_analysis(
                analysis_id=analysis_id,
                input_content=transcription.text,
                fallacies=fallacies,
                overall_assessment=overall_assessment,
                is_clean=is_clean,
                analysis_duration_ms=duration_ms,
                model_used=settings.vllm_model_name,
                metadata=metadata,
                input_type="youtube",
            )
        except Exception:  # noqa: BLE001 - persistence failures shouldn't hide the verdict
            logger.exception("Failed to persist YouTube analysis %s to Supabase", analysis_id)

        await _youtube_result_cache.set(cache_key, record)

        yield _sse_event("result", response_model.model_dump(mode="json"))
    finally:
        cleanup_audio_file(audio_path)


@router.post(
    "/youtube",
    summary="Submit a YouTube video for examination",
)
async def analyze_youtube(payload: YouTubeAnalysisRequest) -> StreamingResponse:
    url = payload.youtube_url.strip()
    video_id = extract_video_id(url)

    if video_id is None:
        logger.warning("Rejected /analyze/youtube request: invalid URL %r", url)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The supplied URL is not a valid YouTube watch, youtu.be, shorts, or live link.",
        )

    cache_key = f"{video_id}:{payload.mode}"

    cached_record = await _youtube_result_cache.get(cache_key)
    if cached_record is None:
        cached_record = await get_cached_youtube_analysis(video_id, payload.mode)
        if cached_record is not None:
            await _youtube_result_cache.set(cache_key, cached_record)

    if cached_record is not None:
        logger.info("Serving cached YouTube analysis for video %s (mode=%s)", video_id, payload.mode)
        return StreamingResponse(_stream_cached_result(cached_record), media_type="text/event-stream")

    try:
        video_info = await get_video_info(url)
    except YouTubeUnavailableError as exc:
        logger.warning("Rejected /analyze/youtube request: video %s unavailable: %s", video_id, exc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The video is private, deleted, or otherwise unavailable.",
        ) from exc
    except YouTubeExtractionError as exc:
        logger.error("Failed to fetch metadata for %s: %s", url, exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not retrieve information about this video. Please try again later.",
        ) from exc

    if video_info.duration_seconds > settings.youtube_max_duration_seconds:
        max_hours = settings.youtube_max_duration_seconds / 3600
        logger.warning(
            "Rejected /analyze/youtube request: video %s is %ds long (max %ds)",
            video_id,
            video_info.duration_seconds,
            settings.youtube_max_duration_seconds,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The video is too long to examine (maximum {max_hours:.0f} hours).",
        )

    return StreamingResponse(
        _run_youtube_pipeline(
            url=url,
            video_id=video_id,
            video_info=video_info,
            payload=payload,
            cache_key=cache_key,
        ),
        media_type="text/event-stream",
    )
