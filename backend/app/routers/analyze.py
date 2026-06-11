"""Endpoints for submitting raw text and YouTube videos to the fallacy examination pipeline."""

from __future__ import annotations

import asyncio
import hashlib
import ipaddress
import json
import logging
import os
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Literal
from urllib.parse import urlparse

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import ValidationError

from app.core.prompts import STRICT_JSON_REMINDER, build_prompt, build_youtube_prompt
from app.core.config import settings
from app.models.request import TextAnalysisRequest, UrlAnalysisRequest, YouTubeAnalysisRequest
from app.models.response import (
    AnalysisResponse,
    AudioAnalysisResponse,
    UrlAnalysisResponse,
    YouTubeAnalysisResponse,
)
from app.services.audio_service import (
    ALLOWED_AUDIO_EXTENSIONS,
    AudioProbeError,
    AudioTooLargeError,
    convert_to_wav,
    probe_audio_duration,
    save_upload_to_temp,
)
from app.services.jina_service import (
    JinaReaderTimeoutError,
    JinaReaderUnavailableError,
    JinaReaderUnsupportedContentError,
    extract_article,
)
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

URL_CACHE_TTL_SECONDS = 6 * 60 * 60
MIN_ARTICLE_WORD_COUNT = 100

_BLOCKED_HOSTNAMES = {"localhost", "0.0.0.0"}

_youtube_result_cache: TTLCache[dict[str, Any]] = TTLCache(ttl_seconds=settings.youtube_cache_ttl_seconds)
_url_result_cache: TTLCache[dict[str, Any]] = TTLCache(ttl_seconds=URL_CACHE_TTL_SECONDS)

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
    description=(
        "File a raw piece of text with the tribunal. The text is sent to "
        "Llama-3-70B-Instruct (vLLM, AMD MI300X), which returns every logical "
        "fallacy it finds, an overall verdict, and a confidence score per "
        "finding. Fallacies below the confidence threshold (0.6) are dropped.\n\n"
        "**Use case:** paste a paragraph, social media post, or argument and "
        "receive an itemized breakdown of the reasoning errors it contains."
    ),
    response_description=(
        "The verdict: every fallacy found (with quote, explanation, confidence, "
        "and severity), an overall assessment, and metadata about the model run."
    ),
    responses={
        400: {
            "description": "The text is shorter than 10 characters or longer than 10,000 characters.",
        },
        422: {"description": "The request body failed validation (missing or malformed fields)."},
        503: {
            "description": (
                "The examination service (vLLM) timed out, is unavailable, or "
                "returned a response that could not be parsed."
            ),
        },
    },
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


def _validate_article_url(url: str) -> str:
    """Ensure ``url`` is a public HTTP/HTTPS URL, rejecting localhost and private addresses."""

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The URL must start with http:// or https://.",
        )

    hostname = (parsed.hostname or "").lower()
    if not hostname:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The supplied URL is invalid.")

    if hostname in _BLOCKED_HOSTNAMES or hostname.endswith(".localhost"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URLs pointing to localhost are not allowed.",
        )

    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        ip = None

    if ip is not None and (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_unspecified):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URLs pointing to private or internal addresses are not allowed.",
        )

    return url


@router.post(
    "/url",
    response_model=UrlAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit an article URL for examination",
    description=(
        "Hand the tribunal a public article URL. The article body is extracted "
        "via Jina Reader, then examined the same way as `/analyze/text`. Results "
        "for a given URL + mode are cached for 6 hours.\n\n"
        "**Use case:** drop a link to a news article or opinion piece and "
        "receive a fallacy breakdown without copy-pasting the text."
    ),
    response_description=(
        "The verdict for the extracted article: every fallacy found, an overall "
        "assessment, article metadata (title, URL, word count), and whether the "
        "result was served from cache."
    ),
    responses={
        400: {
            "description": (
                "The URL is malformed, points to a localhost/private address, or "
                "the extracted article is shorter than 100 words."
            ),
        },
        404: {"description": "The article URL could not be reached."},
        422: {"description": "The request body failed validation (missing or malformed fields)."},
        503: {
            "description": (
                "The article extraction service (Jina Reader) or the examination "
                "service (vLLM) timed out or is unavailable."
            ),
        },
    },
)
async def analyze_url(payload: UrlAnalysisRequest) -> UrlAnalysisResponse:
    url = _validate_article_url(payload.url.strip())

    cache_key = hashlib.sha256(f"{url}:{payload.mode}".encode("utf-8")).hexdigest()

    cached = await _url_result_cache.get(cache_key)
    if cached is not None:
        logger.info("Serving cached URL analysis for %s (mode=%s)", url, payload.mode)
        return UrlAnalysisResponse(**{**cached, "cached": True})

    logger.info("Extracting article content from %s via Jina Reader", url)
    try:
        article = await extract_article(url)
    except JinaReaderTimeoutError as exc:
        logger.error("Jina Reader timed out for %s: %s", url, exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The article extraction service is taking too long to respond. Please try again shortly.",
        ) from exc
    except JinaReaderUnsupportedContentError as exc:
        logger.warning("Jina Reader found no readable content at %s: %s", url, exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This URL does not appear to contain readable article text (it may be a PDF, image, or non-text page).",
        ) from exc
    except JinaReaderUnavailableError as exc:
        logger.warning("Jina Reader could not reach %s: %s", url, exc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The article URL could not be accessed. Please check the link and try again.",
        ) from exc

    if article.word_count < MIN_ARTICLE_WORD_COUNT:
        logger.warning("Article at %s is too short (%d words)", url, article.word_count)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"The extracted article only has {article.word_count} words, which is too short to "
                f"examine (minimum {MIN_ARTICLE_WORD_COUNT}). Try submitting the full article text directly "
                "via /analyze/text instead."
            ),
        )

    text = article.text[:MAX_TEXT_LENGTH]

    analysis = await analyze_text(TextAnalysisRequest(text=text, mode=payload.mode, language="en"))

    response = UrlAnalysisResponse(
        **analysis.model_dump(exclude={"input_type"}),
        input_type="url",
        article_title=article.title,
        article_url=url,
        word_count=article.word_count,
        cached=False,
    )

    await _url_result_cache.set(cache_key, response.model_dump(mode="json"))

    return response


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
    description=(
        "File a YouTube video with the tribunal. The audio is downloaded "
        "(yt-dlp), transcribed with Whisper Large-v3, then examined by "
        "Llama-3-70B-Instruct. Each detected fallacy is mapped back to the "
        "timestamp in the video where it occurs.\n\n"
        "The response is a `text/event-stream` (Server-Sent Events) so the "
        "client can render each pipeline stage as it happens. Previously "
        "examined videos (same video + mode) are replayed instantly from cache.\n\n"
        "**Use case:** drop a link to a debate, lecture, or commentary video "
        "and receive a fallacy breakdown synced to the video timeline.\n\n"
        "**Event stream:**\n"
        "- `event: progress` — `{stage, message}` for each pipeline step "
        "(`downloading_audio`, `transcribing`, `analyzing`, `saving`, `cache_hit`)\n"
        "- `event: result` — the final `YouTubeAnalysisResponse` payload\n"
        "- `event: error` — `{status_code, detail}` if the pipeline fails midway"
    ),
    response_description=(
        "An SSE stream of progress events followed by a final `result` event "
        "containing the verdict, transcript, and per-fallacy timestamps."
    ),
    responses={
        200: {
            "description": "SSE stream of progress, result, or error events.",
            "content": {"text/event-stream": {}},
        },
        400: {"description": "The URL is not a valid YouTube link, or the video exceeds the maximum allowed duration."},
        404: {"description": "The video is private, deleted, or otherwise unavailable (also sent as an `error` SSE event)."},
        422: {"description": "The request body failed validation (missing or malformed fields)."},
        502: {"description": "Failed to retrieve metadata for the video (also sent as an `error` SSE event)."},
    },
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


async def _run_audio_pipeline(
    *,
    input_path: str,
    extension: str,
    filename: str,
    mode: Literal["quick", "educational"],
) -> AsyncIterator[str]:
    """Run the convert -> transcribe -> analyze pipeline for an uploaded audio file, streaming SSE."""

    wav_path: str | None = None
    try:
        yield _sse_event(
            "progress",
            {"stage": "validating", "message": "Verifying the audio file..."},
        )

        try:
            duration_seconds = await probe_audio_duration(input_path)
        except AudioProbeError as exc:
            logger.warning("Failed to probe uploaded audio file %s: %s", filename, exc)
            yield _sse_event(
                "error",
                {"status_code": 400, "detail": "File audio tidak dapat dibaca"},
            )
            return

        if duration_seconds > settings.audio_max_duration_seconds:
            max_hours = settings.audio_max_duration_seconds / 3600
            logger.warning(
                "Rejected uploaded audio %s: %.1fs long (max %ds)",
                filename,
                duration_seconds,
                settings.audio_max_duration_seconds,
            )
            yield _sse_event(
                "error",
                {"status_code": 400, "detail": f"The audio is too long to examine (maximum {max_hours:.0f} hours)."},
            )
            return

        if extension == "wav":
            wav_path = input_path
        else:
            wav_path = f"{os.path.splitext(input_path)[0]}.wav"

            yield _sse_event(
                "progress",
                {"stage": "converting", "message": "Converting audio to WAV..."},
            )

            converted = await asyncio.to_thread(convert_to_wav, input_path, wav_path)
            if not converted:
                logger.error("ffmpeg failed to convert uploaded audio %s to WAV", filename)
                yield _sse_event(
                    "error",
                    {"status_code": 400, "detail": "File audio tidak dapat dibaca"},
                )
                return

        yield _sse_event(
            "progress",
            {"stage": "transcribing", "message": "Transcribing the audio with Whisper Large-v3..."},
        )

        try:
            transcription = await transcribe_audio(wav_path)
        except WhisperTranscriptionError as exc:
            logger.error("Whisper transcription failed for %s: %s", filename, exc)
            yield _sse_event(
                "error",
                {"status_code": 500, "detail": f"Audio transcription failed: {exc}"},
            )
            return

        if not transcription.text.strip():
            yield _sse_event(
                "error",
                {"status_code": 422, "detail": "No speech could be detected in this audio file."},
            )
            return

        language: Literal["id", "en"] = (
            "id" if (transcription.language or "id").lower().startswith("id") else "en"
        )

        yield _sse_event(
            "progress",
            {"stage": "analyzing", "message": "Examining the transcript for fallacies..."},
        )

        prompt = build_prompt(transcription.text, mode=mode)

        start_time = time.perf_counter()
        parsed: dict | None = None

        for attempt in range(1, MAX_GENERATION_ATTEMPTS + 1):
            current_prompt = prompt
            if attempt > 1:
                current_prompt = f"{prompt}\n\n{STRICT_JSON_REMINDER[language]}"
                logger.warning(
                    "Retrying vLLM call for audio %s with stricter JSON instructions (attempt %d)",
                    filename,
                    attempt,
                )

            try:
                raw_output = await generate_completion(current_prompt)
            except (VLLMTimeoutError, VLLMResponseError) as exc:
                logger.error("vLLM error analyzing audio %s: %s", filename, exc)
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
                    "Failed to parse JSON from vLLM output for audio %s on attempt %d: %s",
                    filename,
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
        logger.info("vLLM analysis for audio %s completed in %dms", filename, duration_ms)

        fallacies = [
            f for f in parsed.get("fallacies", []) if f.get("confidence", 0) >= CONFIDENCE_THRESHOLD
        ]
        overall_assessment = parsed.get("overall_assessment", "")
        is_clean = parsed.get("is_clean", len(fallacies) == 0)

        analysis_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        metadata = {
            "mode": mode,
            "language": language,
            "filename": filename,
            "duration_seconds": duration_seconds,
            "overall_assessment": overall_assessment,
            "is_clean": is_clean,
        }

        try:
            response_model = AudioAnalysisResponse(
                id=analysis_id,
                mode=mode,
                language=language,
                filename=filename,
                duration_seconds=duration_seconds,
                transcript=transcription.text,
                fallacies=fallacies,
                overall_assessment=overall_assessment,
                is_clean=is_clean,
                total_fallacies=len(fallacies),
                model_used=settings.vllm_model_name,
                analysis_duration_ms=duration_ms,
                created_at=created_at,
            )
        except ValidationError as exc:
            logger.error("Audio analysis result for %s failed validation: %s", filename, exc)
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
                input_type="audio",
            )
        except Exception:  # noqa: BLE001 - persistence failures shouldn't hide the verdict
            logger.exception("Failed to persist audio analysis %s to Supabase", analysis_id)

        yield _sse_event("result", response_model.model_dump(mode="json"))
    finally:
        cleanup_audio_file(input_path)
        if wav_path and wav_path != input_path:
            cleanup_audio_file(wav_path)


@router.post(
    "/audio",
    summary="Submit an audio recording for examination",
    description=(
        "Upload an audio recording (e.g. a speech, podcast clip, or voice "
        "memo) for examination. The file is converted to WAV (ffmpeg), "
        "transcribed with Whisper Large-v3, then examined by "
        "Llama-3-70B-Instruct.\n\n"
        "The response is a `text/event-stream` (Server-Sent Events) so the "
        "client can render each pipeline stage as it happens.\n\n"
        "**Use case:** record or upload spoken argument and receive a fallacy "
        "breakdown of the transcript.\n\n"
        "**Event stream:**\n"
        "- `event: progress` — `{stage, message}` for each pipeline step "
        "(`validating`, `converting`, `transcribing`, `analyzing`, `saving`)\n"
        "- `event: result` — the final `AudioAnalysisResponse` payload\n"
        "- `event: error` — `{status_code, detail}` if the pipeline fails midway"
    ),
    response_description=(
        "An SSE stream of progress events followed by a final `result` event "
        "containing the verdict and full transcript."
    ),
    responses={
        200: {
            "description": "SSE stream of progress, result, or error events.",
            "content": {"text/event-stream": {}},
        },
        400: {"description": "Unsupported audio format, or the audio could not be read (also sent as an `error` SSE event)."},
        413: {"description": "The uploaded file exceeds the maximum allowed size."},
        422: {"description": "The request failed validation (missing file or malformed form fields)."},
    },
)
async def analyze_audio(
    file: UploadFile = File(...),
    mode: Literal["quick", "educational"] = Form("quick"),
) -> StreamingResponse:
    filename = file.filename or "audio"
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension not in ALLOWED_AUDIO_EXTENSIONS:
        logger.warning("Rejected /analyze/audio request: unsupported format %r", extension)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unsupported audio format. Supported formats: "
                + ", ".join(sorted(ALLOWED_AUDIO_EXTENSIONS))
                + "."
            ),
        )

    try:
        input_path = await save_upload_to_temp(file, extension)
    except AudioTooLargeError as exc:
        logger.warning("Rejected /analyze/audio request: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"File terlalu besar (maksimal {settings.audio_max_file_size_bytes // (1024 * 1024)}MB)."
            ),
        ) from exc

    return StreamingResponse(
        _run_audio_pipeline(input_path=input_path, extension=extension, filename=filename, mode=mode),
        media_type="text/event-stream",
    )
