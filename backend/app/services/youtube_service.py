"""YouTube URL validation, metadata lookup, and audio extraction (yt-dlp based)."""

from __future__ import annotations

import asyncio
import logging
import os
import re
import uuid
from dataclasses import dataclass

import yt_dlp

from app.core.config import settings

logger = logging.getLogger(__name__)

_YOUTUBE_URL_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.|m\.)?"
    r"(?:youtube\.com/(?:watch\?v=|shorts/|embed/|live/)|youtu\.be/)"
    r"([A-Za-z0-9_-]{11})"
)

_UNAVAILABLE_MARKERS = (
    "private",
    "unavailable",
    "removed",
    "does not exist",
    "no longer available",
    "members-only",
    "this video is not available",
)


class YouTubeUnavailableError(Exception):
    """Raised when the video is private, deleted, region-locked, or otherwise unreachable."""


class YouTubeExtractionError(Exception):
    """Raised when yt-dlp fails for a reason other than the video being unavailable."""


@dataclass(frozen=True)
class VideoInfo:
    video_id: str
    title: str
    duration_seconds: int


def extract_video_id(url: str) -> str | None:
    """Extract the 11-character video ID from a watch/shorts/youtu.be URL, if valid."""

    match = _YOUTUBE_URL_PATTERN.search(url.strip())
    return match.group(1) if match else None


def is_valid_youtube_url(url: str) -> bool:
    """Return True if ``url`` looks like a watch, youtu.be, or shorts YouTube link."""

    return extract_video_id(url) is not None


def _classify_download_error(exc: yt_dlp.utils.DownloadError) -> Exception:
    message = str(exc).lower()
    if any(marker in message for marker in _UNAVAILABLE_MARKERS):
        return YouTubeUnavailableError(str(exc))
    return YouTubeExtractionError(str(exc))


async def get_video_info(url: str) -> VideoInfo:
    """Fetch video metadata (title, duration) without downloading any media."""

    def _extract() -> dict:
        ydl_opts = {"quiet": True, "no_warnings": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    try:
        info = await asyncio.to_thread(_extract)
    except yt_dlp.utils.DownloadError as exc:
        logger.warning("yt-dlp failed to fetch info for %s: %s", url, exc)
        raise _classify_download_error(exc) from exc

    return VideoInfo(
        video_id=info.get("id", ""),
        title=info.get("title") or "Untitled",
        duration_seconds=int(info.get("duration") or 0),
    )


async def download_audio(url: str, video_id: str) -> str:
    """Download the video's audio track and return the path to the extracted WAV file."""

    output_dir = settings.audio_temp_dir
    os.makedirs(output_dir, exist_ok=True)
    output_template = os.path.join(output_dir, f"{video_id}-{uuid.uuid4().hex}.%(ext)s")

    def _download() -> str:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "192",
                }
            ],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        base, _ = os.path.splitext(output_template)
        return f"{base}.wav"

    try:
        return await asyncio.to_thread(_download)
    except yt_dlp.utils.DownloadError as exc:
        logger.warning("yt-dlp failed to download audio for %s: %s", url, exc)
        raise _classify_download_error(exc) from exc


def cleanup_audio_file(path: str | None) -> None:
    """Best-effort removal of a temporary audio file."""

    if not path:
        return

    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        logger.warning("Failed to remove temporary audio file %s", path, exc_info=True)
