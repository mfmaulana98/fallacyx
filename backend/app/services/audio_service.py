"""Validation, storage, and format conversion helpers for the audio upload pipeline."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
import uuid

from fastapi import UploadFile

from app.core.config import settings

logger = logging.getLogger(__name__)

ALLOWED_AUDIO_EXTENSIONS = {"mp3", "mp4", "wav", "m4a", "ogg", "webm"}

_UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1MB


class AudioValidationError(Exception):
    """Base class for audio upload validation errors."""


class AudioTooLargeError(AudioValidationError):
    """Raised when an uploaded audio file exceeds the configured size limit."""


class AudioProbeError(Exception):
    """Raised when ffprobe cannot read metadata from an audio file (likely corrupt)."""


async def save_upload_to_temp(file: UploadFile, extension: str) -> str:
    """Stream an uploaded file to a uniquely named temp file.

    Raises AudioTooLargeError (and removes the partial file) if the upload
    exceeds settings.audio_max_file_size_bytes.
    """

    output_dir = settings.audio_temp_dir
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"{uuid.uuid4().hex}.{extension}")
    max_bytes = settings.audio_max_file_size_bytes
    written = 0

    with open(output_path, "wb") as out_file:
        while chunk := await file.read(_UPLOAD_CHUNK_SIZE):
            written += len(chunk)
            if written > max_bytes:
                out_file.close()
                os.remove(output_path)
                raise AudioTooLargeError(
                    f"Upload exceeds the maximum allowed size of {max_bytes} bytes"
                )
            out_file.write(chunk)

    return output_path


async def probe_audio_duration(path: str) -> float:
    """Return the duration (in seconds) of an audio file using ffprobe.

    Raises AudioProbeError if ffprobe fails or the duration cannot be parsed,
    which typically indicates a corrupt or unreadable file.
    """

    args = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        path,
    ]

    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise AudioProbeError(stderr.decode(errors="replace").strip())

    try:
        return float(json.loads(stdout)["format"]["duration"])
    except (KeyError, ValueError, json.JSONDecodeError) as exc:
        raise AudioProbeError(f"Could not determine audio duration: {exc}") from exc


def convert_to_wav(input_path: str, output_path: str) -> bool:
    """Convert an audio file to 16kHz mono WAV using ffmpeg.

    Returns True if the conversion succeeded and the output file was created,
    False otherwise.
    """

    args = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ar", "16000",
        "-ac", "1",
        output_path,
    ]

    try:
        result = subprocess.run(args, capture_output=True, timeout=600)
    except (OSError, subprocess.TimeoutExpired):
        logger.exception("ffmpeg conversion failed for %s", input_path)
        return False

    if result.returncode != 0:
        logger.error(
            "ffmpeg exited with code %d while converting %s: %s",
            result.returncode,
            input_path,
            result.stderr.decode(errors="replace").strip(),
        )
        return False

    return os.path.exists(output_path)
