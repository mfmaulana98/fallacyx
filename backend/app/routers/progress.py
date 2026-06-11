"""SSE endpoint for streaming real-time progress of a fallacy examination job."""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any, AsyncIterator

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/progress", tags=["progress"])

STREAM_TIMEOUT_SECONDS = 5 * 60

job_queues: dict[str, asyncio.Queue[dict[str, Any]]] = {}


def create_job() -> str:
    """Create a new job id with its associated progress queue."""

    job_id = str(uuid.uuid4())
    job_queues[job_id] = asyncio.Queue()
    return job_id


def get_queue(job_id: str) -> asyncio.Queue[dict[str, Any]] | None:
    """Return the progress queue for a job, or ``None`` if it doesn't exist."""

    return job_queues.get(job_id)


def cleanup_job(job_id: str) -> None:
    """Remove a job's queue once the stream is no longer needed."""

    job_queues.pop(job_id, None)


async def push_progress(job_id: str, event: dict[str, Any]) -> None:
    """Push a progress event onto a job's queue, if it still exists."""

    queue = job_queues.get(job_id)
    if queue is not None:
        await queue.put(event)


def _sse_data(event: dict[str, Any]) -> str:
    """Format a single Server-Sent Event using a ``data:`` line."""

    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


async def _stream_progress(job_id: str, request: Request, queue: asyncio.Queue[dict[str, Any]]) -> AsyncIterator[str]:
    try:
        while True:
            if await request.is_disconnected():
                logger.info("Client disconnected from progress stream for job %s", job_id)
                return

            try:
                event = await asyncio.wait_for(queue.get(), timeout=STREAM_TIMEOUT_SECONDS)
            except asyncio.TimeoutError:
                logger.warning("Progress stream for job %s timed out after %ds", job_id, STREAM_TIMEOUT_SECONDS)
                yield _sse_data(
                    {"step": "error", "percent": 0, "message": "Examination timed out. Please try again."}
                )
                return

            yield _sse_data(event)

            if event.get("step") in ("done", "error"):
                return
    finally:
        cleanup_job(job_id)


@router.get(
    "/{job_id}",
    summary="Stream real-time progress for an analysis job",
    description=(
        "Open a Server-Sent Events stream for a previously created job id and "
        "receive each step of the examination pipeline as it completes "
        "(e.g. downloading audio, transcribing, examining for fallacies).\n\n"
        "The stream ends after a `done` or `error` step is emitted, or after "
        f"{STREAM_TIMEOUT_SECONDS} seconds of inactivity.\n\n"
        "**Use case:** poll-free progress bars for long-running examinations — "
        "open this stream alongside the analysis request and update the UI as "
        "events arrive."
    ),
    response_description=(
        "An SSE stream of `data:` events shaped as `{step, percent, message}`, "
        "ending with a `step: \"done\"` or `step: \"error\"` event."
    ),
    responses={
        200: {
            "description": "SSE stream of progress events.",
            "content": {"text/event-stream": {}},
        },
        404: {"description": "No progress stream exists for this job id (it may have already completed or expired)."},
    },
)
async def stream_job_progress(job_id: str, request: Request) -> StreamingResponse:
    queue = get_queue(job_id)
    if queue is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No progress stream exists for this job id.",
        )

    return StreamingResponse(
        _stream_progress(job_id, request, queue),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
