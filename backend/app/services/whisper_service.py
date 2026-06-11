"""Audio transcription via faster-whisper (Whisper Large-v3) on AMD GPUs (ROCm)."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass, field

from faster_whisper import WhisperModel

from app.core.config import settings

logger = logging.getLogger(__name__)


class WhisperTranscriptionError(Exception):
    """Raised when audio transcription fails."""


@dataclass(frozen=True)
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass(frozen=True)
class TranscriptResult:
    text: str
    segments: list[TranscriptSegment] = field(default_factory=list)
    language: str = ""
    duration_seconds: float = 0.0


ProgressCallback = Callable[[dict], None]

_model: WhisperModel | None = None


def _is_oom_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "out of memory" in message or "cuda error" in message or "hip error" in message


def load_whisper_model() -> WhisperModel:
    """Load Whisper Large-v3 onto the GPU once and cache it as a module-level singleton."""

    global _model

    if _model is not None:
        return _model

    logger.info(
        "Loading Whisper model %s (device=%s, compute_type=%s)",
        settings.whisper_model_size,
        settings.whisper_device,
        settings.whisper_compute_type,
    )

    try:
        _model = WhisperModel(
            settings.whisper_model_size,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
        )
    except RuntimeError as exc:
        if _is_oom_error(exc):
            raise WhisperTranscriptionError(
                "Out of GPU memory while loading Whisper Large-v3. Try a lighter "
                "compute_type (e.g. 'int8_float16') or free up VRAM before retrying."
            ) from exc
        raise WhisperTranscriptionError(f"Failed to load Whisper model: {exc}") from exc

    logger.info("Whisper model loaded successfully")
    return _model


def _transcribe_segments(
    audio_path: str, language: str
) -> tuple[list, object]:
    """Run the blocking faster-whisper transcription, normalizing OOM errors."""

    model = load_whisper_model()
    try:
        return model.transcribe(audio_path, language=language, beam_size=5)
    except RuntimeError as exc:
        if _is_oom_error(exc):
            raise WhisperTranscriptionError(
                "Out of GPU memory while transcribing audio. Try a shorter clip, a "
                "lighter compute_type (e.g. 'int8_float16'), or free up VRAM."
            ) from exc
        raise


async def transcribe_audio(audio_path: str, language: str = "id") -> TranscriptResult:
    """Transcribe an audio file end-to-end, returning the full text and per-segment timestamps."""

    def _run() -> TranscriptResult:
        segments_iter, info = _transcribe_segments(audio_path, language)
        segments = [
            TranscriptSegment(start=segment.start, end=segment.end, text=segment.text.strip())
            for segment in segments_iter
        ]
        full_text = " ".join(segment.text for segment in segments).strip()
        return TranscriptResult(
            text=full_text,
            segments=segments,
            language=info.language,
            duration_seconds=info.duration,
        )

    try:
        return await asyncio.to_thread(_run)
    except WhisperTranscriptionError:
        raise
    except Exception as exc:  # noqa: BLE001 - normalize all backend failures into one error type
        logger.exception("Whisper transcription failed for %s", audio_path)
        raise WhisperTranscriptionError(str(exc)) from exc


async def transcribe_with_progress(
    audio_path: str,
    progress_callback: ProgressCallback,
    language: str = "id",
) -> TranscriptResult:
    """Transcribe an audio file, invoking progress_callback after each completed segment."""

    def _run() -> TranscriptResult:
        segments_iter, info = _transcribe_segments(audio_path, language)
        duration = info.duration or 0.0

        segments: list[TranscriptSegment] = []
        for segment in segments_iter:
            parsed = TranscriptSegment(
                start=segment.start, end=segment.end, text=segment.text.strip()
            )
            segments.append(parsed)

            percent = min(100.0, (parsed.end / duration) * 100) if duration > 0 else 0.0
            progress_callback({"percent": percent, "text": parsed.text})

        full_text = " ".join(segment.text for segment in segments).strip()
        return TranscriptResult(
            text=full_text,
            segments=segments,
            language=info.language,
            duration_seconds=duration,
        )

    try:
        return await asyncio.to_thread(_run)
    except WhisperTranscriptionError:
        raise
    except Exception as exc:  # noqa: BLE001 - normalize all backend failures into one error type
        logger.exception("Whisper transcription failed for %s", audio_path)
        raise WhisperTranscriptionError(str(exc)) from exc
