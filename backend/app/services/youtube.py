"""YouTube video ID parsing, metadata lookup, and audio extraction via the yt-dlp CLI."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
import uuid

from app.core.config import settings

logger = logging.getLogger(__name__)

_YOUTUBE_URL_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.|m\.)?"
    r"(?:youtube\.com/(?:watch\?v=|shorts/|embed/|live/)|youtu\.be/)"
    r"([A-Za-z0-9_-]{11})"
)

_CLEANUP_DELAY_SECONDS = 3600


class YtDlpError(Exception):
    """Raised when the yt-dlp CLI exits with a non-zero status."""


def extract_video_id(url: str) -> str:
    """Extract the 11-character video ID from a watch/shorts/embed/youtu.be URL.

    Raises:
        ValueError: if ``url`` does not look like a YouTube URL.
    """

    match = _YOUTUBE_URL_PATTERN.search(url.strip())
    if not match:
        raise ValueError(f"Not a valid YouTube URL: {url}")

    video_id = match.group(1)
    logger.debug("Extracted video ID %s from %s", video_id, url)
    return video_id


async def _run_yt_dlp(args: list[str]) -> tuple[str, str, int]:
    logger.debug("Running yt-dlp %s", " ".join(args))
    process = await asyncio.create_subprocess_exec(
        "yt-dlp",
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    return stdout.decode(errors="replace"), stderr.decode(errors="replace"), process.returncode


async def get_video_metadata(video_id: str) -> dict:
    """Fetch title, duration, uploader, and thumbnail for a video without downloading it."""

    url = f"https://www.youtube.com/watch?v={video_id}"
    logger.info("Fetching metadata for video %s", video_id)

    stdout, stderr, returncode = await _run_yt_dlp(
        ["--dump-json", "--no-warnings", "--skip-download", url]
    )
    if returncode != 0:
        logger.error("yt-dlp metadata fetch failed for %s: %s", video_id, stderr.strip())
        raise YtDlpError(f"Failed to fetch metadata for video {video_id}: {stderr.strip()}")

    info = json.loads(stdout)
    metadata = {
        "title": info.get("title") or "Untitled",
        "duration_seconds": int(info.get("duration") or 0),
        "uploader": info.get("uploader") or "Unknown",
        "thumbnail_url": info.get("thumbnail") or "",
    }
    logger.info(
        "Fetched metadata for %s: title=%r duration=%ds",
        video_id,
        metadata["title"],
        metadata["duration_seconds"],
    )
    return metadata


async def _schedule_cleanup(path: str, delay_seconds: float) -> None:
    await asyncio.sleep(delay_seconds)
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.info("Removed temporary audio file %s after scheduled cleanup", path)
    except OSError:
        logger.warning("Failed to remove temporary audio file %s", path, exc_info=True)


async def download_audio(url: str, output_dir: str) -> str:
    """Download the video's audio as 16kHz mono WAV and return the output file path.

    The file is scheduled for automatic cleanup one hour after download.
    """

    video_id = extract_video_id(url)
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{video_id}-{uuid.uuid4().hex}"
    output_template = os.path.join(output_dir, f"{filename}.%(ext)s")
    output_path = os.path.join(output_dir, f"{filename}.wav")

    args = [
        "-f", "bestaudio/best",
        "-x",
        "--audio-format", "wav",
        "--postprocessor-args", "ffmpeg:-ar 16000 -ac 1",
        "--no-warnings",
        "-o", output_template,
        url,
    ]

    logger.info("Downloading audio for %s to %s", url, output_path)
    stdout, stderr, returncode = await _run_yt_dlp(args)
    if returncode != 0:
        logger.error("yt-dlp audio download failed for %s: %s", url, stderr.strip())
        raise YtDlpError(f"Failed to download audio for {url}: {stderr.strip()}")

    if not os.path.exists(output_path):
        logger.error("Expected audio output missing after download: %s", output_path)
        raise YtDlpError(f"Audio download succeeded but output file not found: {output_path}")

    logger.info("Downloaded audio for %s to %s", video_id, output_path)

    asyncio.create_task(_schedule_cleanup(output_path, _CLEANUP_DELAY_SECONDS))

    return output_path


def cleanup_temp_files(older_than_hours: int = 1) -> int:
    """Remove WAV files in the audio temp dir older than ``older_than_hours``.

    Returns the number of files removed.
    """

    output_dir = settings.audio_temp_dir
    if not os.path.isdir(output_dir):
        logger.debug("Temp audio dir %s does not exist, nothing to clean up", output_dir)
        return 0

    cutoff = time.time() - older_than_hours * 3600
    removed = 0

    for entry in os.listdir(output_dir):
        if not entry.endswith(".wav"):
            continue

        path = os.path.join(output_dir, entry)
        try:
            if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
                os.remove(path)
                removed += 1
                logger.info("Removed stale temp audio file %s", path)
        except OSError:
            logger.warning("Failed to remove temp audio file %s", path, exc_info=True)

    logger.info(
        "Cleanup complete: removed %d stale audio file(s) older than %dh from %s",
        removed,
        older_than_hours,
        output_dir,
    )
    return removed
