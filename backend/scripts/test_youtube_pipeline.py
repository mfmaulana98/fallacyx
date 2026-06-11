"""End-to-end test of the YouTube fallacy pipeline (POST /analyze/youtube).

Runs a fixed set of YouTube videos sequentially (one at a time, so the GPU
is not overloaded), streams the SSE progress events for each one, and times
every pipeline stage:

    - audio download (yt-dlp)
    - Whisper transcription
    - vLLM fallacy analysis

Results are printed as rich tables and exported to
``scripts/results/youtube_test_[timestamp].json``.

Usage:
    python test_youtube_pipeline.py --host http://AMD-IP:8080
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator

import httpx
from rich.console import Console
from rich.table import Table

RESULTS_DIR = Path(__file__).resolve().parent / "results"


@dataclass(frozen=True)
class VideoCase:
    case_id: int
    label: str
    url: str
    mode: str = "quick"


# Fill these in with real YouTube URLs before running the script.
VIDEO_DEBAT_POLITIK = ""  # Video debat politik Indonesia
VIDEO_PIDATO_PEJABAT = ""  # Pidato pejabat publik
VIDEO_PODCAST_EKONOMI = ""  # Podcast diskusi ekonomi
VIDEO_BERITA_TV = ""  # Segmen berita TV
VIDEO_TALKSHOW = ""  # Talkshow/talk show Indonesia

TEST_VIDEOS: list[VideoCase] = [
    VideoCase(1, "Debat Politik Indonesia", VIDEO_DEBAT_POLITIK),
    VideoCase(2, "Pidato Pejabat Publik", VIDEO_PIDATO_PEJABAT),
    VideoCase(3, "Podcast Diskusi Ekonomi", VIDEO_PODCAST_EKONOMI),
    VideoCase(4, "Segmen Berita TV", VIDEO_BERITA_TV),
    VideoCase(5, "Talkshow Indonesia", VIDEO_TALKSHOW),
]


async def _iter_sse_events(response: httpx.Response) -> AsyncIterator[tuple[str, str]]:
    """Yield ``(event, data)`` pairs from a text/event-stream response."""

    event_type = "message"
    data_lines: list[str] = []

    async for line in response.aiter_lines():
        if line == "":
            if data_lines:
                yield event_type, "\n".join(data_lines)
            event_type = "message"
            data_lines = []
            continue

        if line.startswith("event:"):
            event_type = line[len("event:") :].strip()
        elif line.startswith("data:"):
            data_lines.append(line[len("data:") :].strip())


def _new_result(case: VideoCase) -> dict[str, Any]:
    return {
        "case_id": case.case_id,
        "label": case.label,
        "url": case.url,
        "mode": case.mode,
        "status": "skipped",
        "video_title": None,
        "video_duration_seconds": None,
        "download_audio_seconds": None,
        "transcribe_seconds": None,
        "llm_analysis_seconds": None,
        "total_seconds": None,
        "server_duration_ms": None,
        "total_fallacies": None,
        "fallacy_types": [],
        "is_clean": None,
        "error": "",
    }


async def run_video_test(
    client: httpx.AsyncClient, host: str, case: VideoCase, console: Console, timeout: float
) -> dict[str, Any]:
    result = _new_result(case)

    if not case.url:
        result["error"] = "no URL provided"
        console.print(f"[yellow]Skipping case {case.case_id} ({case.label}): no URL provided[/yellow]")
        return result

    console.print(f"\n[bold]Case {case.case_id}: {case.label}[/bold] -> {case.url} (mode={case.mode})")

    url = f"{host.rstrip('/')}/analyze/youtube"
    payload = {"youtube_url": case.url, "mode": case.mode}
    request_timeout = httpx.Timeout(connect=10.0, read=timeout, write=30.0, pool=10.0)

    timestamps: dict[str, float] = {}
    request_start = time.perf_counter()

    try:
        async with client.stream("POST", url, json=payload, timeout=request_timeout) as response:
            if response.status_code != 200:
                body = await response.aread()
                result["status"] = "error"
                result["error"] = f"HTTP {response.status_code}: {body.decode(errors='replace')[:300]}"
                console.print(f"[red]  HTTP error: {result['error']}[/red]")
                return result

            async for event_type, data_raw in _iter_sse_events(response):
                try:
                    data = json.loads(data_raw)
                except json.JSONDecodeError:
                    continue

                now = time.perf_counter()

                if event_type == "progress":
                    stage = data.get("stage", "")
                    timestamps[stage] = now
                    console.print(f"  [dim]{stage}: {data.get('message', '')}[/dim]")

                elif event_type == "error":
                    result["status"] = "error"
                    result["error"] = data.get("detail", "unknown error")
                    console.print(f"[red]  Error: {result['error']}[/red]")
                    return result

                elif event_type == "result":
                    result_time = now
                    result["video_title"] = data.get("video_title")
                    result["video_duration_seconds"] = data.get("video_duration_seconds")
                    result["server_duration_ms"] = data.get("analysis_duration_ms")
                    result["total_fallacies"] = data.get("total_fallacies")
                    result["is_clean"] = data.get("is_clean")
                    result["fallacy_types"] = sorted(
                        {f.get("fallacy_type", "unknown") for f in data.get("fallacies", [])}
                    )
                    result["total_seconds"] = round(result_time - request_start, 2)

                    if data.get("cached"):
                        result["status"] = "cached"
                    else:
                        result["status"] = "ok"
                        download_start = timestamps.get("downloading_audio")
                        transcribe_start = timestamps.get("transcribing")
                        analyze_start = timestamps.get("analyzing")
                        saving_start = timestamps.get("saving")

                        if download_start is not None and transcribe_start is not None:
                            result["download_audio_seconds"] = round(transcribe_start - download_start, 2)
                        if transcribe_start is not None and analyze_start is not None:
                            result["transcribe_seconds"] = round(analyze_start - transcribe_start, 2)
                        if analyze_start is not None:
                            llm_end = saving_start if saving_start is not None else result_time
                            result["llm_analysis_seconds"] = round(llm_end - analyze_start, 2)

                    console.print(
                        f"  [green]Done in {result['total_seconds']}s "
                        f"({result['total_fallacies']} fallacies)[/green]"
                    )

    except httpx.TimeoutException:
        result["status"] = "error"
        result["error"] = "request timed out"
        console.print("[red]  Request timed out[/red]")
    except httpx.HTTPError as exc:
        result["status"] = "error"
        result["error"] = str(exc)
        console.print(f"[red]  HTTP error: {exc}[/red]")

    return result


async def run_all(host: str, timeout: float, cases: list[VideoCase], console: Console) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    async with httpx.AsyncClient() as client:
        for case in cases:
            result = await run_video_test(client, host, case, console, timeout)
            results.append(result)
    return results


def _fmt_seconds(value: float | None) -> str:
    return f"{value:.2f}" if value is not None else "—"


def _fmt_duration(seconds: int | None) -> str:
    if seconds is None:
        return "—"
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes}m{secs:02d}s"


def _status_label(status: str) -> str:
    colors = {"ok": "green", "cached": "cyan", "error": "red", "skipped": "yellow"}
    color = colors.get(status, "white")
    return f"[{color}]{status}[/{color}]"


def print_table(console: Console, results: list[dict[str, Any]]) -> None:
    table = Table(title="YouTube Pipeline Test Results")
    table.add_column("#", justify="right")
    table.add_column("Label")
    table.add_column("Title", overflow="fold", max_width=32)
    table.add_column("Duration", justify="right")
    table.add_column("Download(s)", justify="right")
    table.add_column("Whisper(s)", justify="right")
    table.add_column("LLM(s)", justify="right")
    table.add_column("Total(s)", justify="right")
    table.add_column("Fallacies", justify="right")
    table.add_column("Types", overflow="fold", max_width=32)
    table.add_column("Status")

    for r in results:
        table.add_row(
            str(r["case_id"]),
            r["label"],
            (r["video_title"] or "—")[:60],
            _fmt_duration(r["video_duration_seconds"]),
            _fmt_seconds(r["download_audio_seconds"]),
            _fmt_seconds(r["transcribe_seconds"]),
            _fmt_seconds(r["llm_analysis_seconds"]),
            _fmt_seconds(r["total_seconds"]),
            str(r["total_fallacies"]) if r["total_fallacies"] is not None else "—",
            ", ".join(r["fallacy_types"]) if r["fallacy_types"] else "—",
            _status_label(r["status"]),
        )

        if r["error"]:
            table.add_row("", "", f"[red]{r['error']}[/red]", "", "", "", "", "", "", "", "")

    console.print(table)


def print_summary(console: Console, results: list[dict[str, Any]]) -> None:
    rates = []
    for r in results:
        if r["status"] == "ok" and r["total_seconds"] and r["video_duration_seconds"]:
            minutes = r["video_duration_seconds"] / 60.0
            if minutes > 0:
                rates.append(r["total_seconds"] / minutes)

    if not rates:
        console.print("\n[yellow]No completed (non-cached) runs to compute throughput.[/yellow]")
        return

    summary = Table(title="Throughput Summary (seconds of pipeline time per minute of audio)")
    summary.add_column("Metric")
    summary.add_column("Value", justify="right")
    summary.add_row("Videos analyzed", str(len(rates)))
    summary.add_row("Average", f"{statistics.mean(rates):.2f} s/min")
    summary.add_row("Min", f"{min(rates):.2f} s/min")
    summary.add_row("Max", f"{max(rates):.2f} s/min")

    console.print()
    console.print(summary)


def export_json(results: list[dict[str, Any]]) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = RESULTS_DIR / f"youtube_test_{timestamp}.json"

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="End-to-end test of the YouTube fallacy pipeline")
    parser.add_argument(
        "--host",
        default="http://localhost:8080",
        help="Base URL of the FallacyX backend (default: http://localhost:8080)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=1800.0,
        help="Per-video request timeout in seconds (default: 1800)",
    )
    parser.add_argument(
        "--mode",
        choices=["quick", "educational"],
        default=None,
        help="Override the analysis mode for all videos (default: per-case mode)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    console = Console()

    cases = TEST_VIDEOS
    if args.mode:
        cases = [VideoCase(c.case_id, c.label, c.url, args.mode) for c in cases]

    console.print(
        f"[bold]Running YouTube pipeline test against {args.host} "
        f"({len(cases)} videos, sequential)...[/bold]"
    )

    results = asyncio.run(run_all(args.host, args.timeout, cases, console))

    console.print()
    print_table(console, results)
    print_summary(console, results)

    output_path = export_json(results)
    console.print(f"\nResults exported to [bold]{output_path}[/bold]")


if __name__ == "__main__":
    main()
