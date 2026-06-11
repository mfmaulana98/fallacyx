"""Latency benchmark for POST /analyze/text.

Sends 10 varied test texts concurrently (asyncio + aiohttp), records
per-request latency, and prints/exports the results.

Usage:
    python test_latency.py --host http://localhost:8080
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import statistics
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import aiohttp
from rich.console import Console
from rich.table import Table

RESULTS_DIR = Path(__file__).resolve().parent / "results"


@dataclass(frozen=True)
class TestCase:
    case_id: int
    category: str
    language: str
    mode: str
    text: str


TEST_CASES: list[TestCase] = [
    TestCase(
        case_id=1,
        category="No Fallacy (sound argument)",
        language="en",
        mode="quick",
        text=(
            "If a city wants to reduce traffic congestion, it should invest in "
            "reliable public transit, because commuters tend to switch away from "
            "cars when buses and trains are frequent, affordable, and on time. "
            "Several cities that expanded their transit networks saw measurable "
            "drops in average commute times within two years."
        ),
    ),
    TestCase(
        case_id=2,
        category="Ad Hominem",
        language="en",
        mode="quick",
        text=(
            "You can't trust Senator Lee's plan to fix the budget. He dropped out "
            "of college and got divorced twice, so why would anyone listen to his "
            "ideas about fiscal policy?"
        ),
    ),
    TestCase(
        case_id=3,
        category="Strawman",
        language="en",
        mode="quick",
        text=(
            "My opponent says we should add a few new bike lanes downtown. So "
            "apparently he wants to ban every car from the city and force "
            "everyone, including elderly and disabled residents, to bike to work "
            "in the snow. That's a reckless plan that would destroy the local "
            "economy."
        ),
    ),
    TestCase(
        case_id=4,
        category="False Dilemma",
        language="en",
        mode="quick",
        text=(
            "Either we cut the entire arts education budget completely, or the "
            "school district will go bankrupt within a year. There is no other "
            "option, so we have to choose: art classes or financial ruin."
        ),
    ),
    TestCase(
        case_id=5,
        category="Appeal to Emotion",
        language="en",
        mode="quick",
        text=(
            "Think of the children who will go hungry tonight while you sit "
            "comfortably in your warm home. How can you possibly vote against "
            "this bill? Only someone heartless and cruel would say no to feeding "
            "starving kids."
        ),
    ),
    TestCase(
        case_id=6,
        category="Slippery Slope",
        language="en",
        mode="quick",
        text=(
            "If we allow students to retake one failed exam, soon they'll demand "
            "to retake every exam, then they'll expect to pass without studying "
            "at all, and eventually our diplomas will become completely "
            "worthless."
        ),
    ),
    TestCase(
        case_id=7,
        category="Circular Reasoning",
        language="en",
        mode="quick",
        text=(
            "The new policy is fair because it treats everyone equally, and we "
            "know it treats everyone equally because the policy itself is fair "
            "by design."
        ),
    ),
    TestCase(
        case_id=8,
        category="Bandwagon",
        language="en",
        mode="quick",
        text=(
            "Everyone in the office is already using this productivity app, so "
            "obviously it's the best one out there. Millions of people can't be "
            "wrong, which is why you should switch to it immediately too."
        ),
    ),
    TestCase(
        case_id=9,
        category="Long text, 3 fallacies (educational mode)",
        language="en",
        mode="educational",
        text=(
            "Last week, the city council debated whether to approve funding for "
            "a new community health clinic in the eastern district. The proposal "
            "would allocate two million dollars over three years to staff a "
            "clinic offering primary care, vaccinations, and mental health "
            "counseling to roughly fifteen thousand residents who currently live "
            "more than an hour from the nearest hospital. "
            "Councilman Avery, who has opposed the plan from the start, argued "
            "that the project should be rejected outright. He claimed that "
            "Councilwoman Reyes, who proposed the clinic, 'has never run a "
            "business in her life and spent most of her twenties traveling "
            "instead of working,' and therefore her judgment on budget matters "
            "cannot be trusted. This personal attack ignored the actual budget "
            "figures she presented, which were independently reviewed by the "
            "city's finance office. "
            "Avery then went further, telling the audience that Reyes wants to "
            "'open the floodgates' to unlimited spending, claiming that 'first "
            "it's a clinic, then it'll be a hospital, then a research campus, "
            "and before anyone realizes it the entire city budget will be "
            "consumed by healthcare projects with no end in sight.' Nothing in "
            "the actual proposal mentioned expanding beyond the single clinic, "
            "and the funding was explicitly capped at three years. "
            "Finally, Avery closed his remarks by telling the council, 'Almost "
            "every other neighboring town has already cut similar programs, so "
            "if we're the only ones still funding something like this, we must "
            "be doing something wrong. We should follow what everyone else is "
            "doing and scrap it too.' He did not provide any evidence about why "
            "those other towns made their decisions, nor did he address whether "
            "the eastern district's situation was comparable. "
            "Despite these arguments, several residents spoke in favor of the "
            "clinic, citing long wait times at the regional hospital and the "
            "difficulty of arranging transportation for routine checkups. The "
            "council ultimately postponed the vote to gather more data, "
            "including a cost-benefit analysis from an independent auditor and "
            "a survey of resident needs in the affected neighborhoods. "
            "Both sides agreed that any final decision should rest on verifiable "
            "numbers rather than speculation, and the council scheduled a "
            "follow-up session for next month to review the auditor's findings "
            "before voting."
        ),
    ),
    TestCase(
        case_id=10,
        category="Code-switching ID-EN",
        language="id",
        mode="quick",
        text=(
            "Menurut gue, kebijakan ini gak masuk akal banget deh. Coba liat, "
            "yang ngusulin aja background-nya cuma anak kuliahan yang belum "
            "pernah kerja kantoran, jadi gimana dia bisa ngerti soal manajemen "
            "perusahaan? Lagian, kalau kita approve proposal ini sekarang, next "
            "thing you know semua divisi bakal minta budget tambahan, terus "
            "perusahaan bakal bangkrut dalam setahun. Either kita tolak proposal "
            "ini sekarang, or kita siap-siap gulung tikar. Udah jelas banget "
            "kan pilihannya cuma dua itu doang."
        ),
    ),
]


async def run_test_case(
    session: aiohttp.ClientSession, host: str, case: TestCase, timeout: float
) -> dict:
    url = f"{host.rstrip('/')}/analyze/text"
    payload = {"text": case.text, "mode": case.mode, "language": case.language}

    started_at = datetime.now(timezone.utc)
    perf_start = time.perf_counter()
    status_code: int | None = None
    fallacies_found: int | None = None
    server_duration_ms: int | None = None
    error: str = ""

    try:
        async with session.post(
            url, json=payload, timeout=aiohttp.ClientTimeout(total=timeout)
        ) as response:
            status_code = response.status
            body = await response.json()
            if status_code == 200:
                fallacies_found = body.get("total_fallacies")
                server_duration_ms = body.get("analysis_duration_ms")
            else:
                error = str(body.get("detail", body))
    except asyncio.TimeoutError:
        error = "request timed out"
    except aiohttp.ClientError as exc:
        error = str(exc)

    perf_end = time.perf_counter()
    finished_at = datetime.now(timezone.utc)
    latency_ms = (perf_end - perf_start) * 1000

    return {
        "case_id": case.case_id,
        "category": case.category,
        "language": case.language,
        "mode": case.mode,
        "started_at": started_at.isoformat(),
        "finished_at": finished_at.isoformat(),
        "latency_ms": round(latency_ms, 2),
        "server_duration_ms": server_duration_ms,
        "status_code": status_code,
        "fallacies_found": fallacies_found,
        "error": error,
    }


async def run_all(host: str, timeout: float) -> list[dict]:
    async with aiohttp.ClientSession() as session:
        tasks = [run_test_case(session, host, case, timeout) for case in TEST_CASES]
        results = await asyncio.gather(*tasks)
    return sorted(results, key=lambda r: r["case_id"])


def print_table(console: Console, results: list[dict]) -> None:
    table = Table(title="Latency Test - POST /analyze/text")
    table.add_column("#", justify="right")
    table.add_column("Category")
    table.add_column("Lang", justify="center")
    table.add_column("Status", justify="center")
    table.add_column("Latency (ms)", justify="right")
    table.add_column("Server (ms)", justify="right")
    table.add_column("Fallacies", justify="right")
    table.add_column("Error")

    for r in results:
        status = str(r["status_code"]) if r["status_code"] is not None else "—"
        status_style = "green" if r["status_code"] == 200 else "red"
        table.add_row(
            str(r["case_id"]),
            r["category"],
            r["language"],
            f"[{status_style}]{status}[/{status_style}]",
            f"{r['latency_ms']:.2f}",
            str(r["server_duration_ms"]) if r["server_duration_ms"] is not None else "—",
            str(r["fallacies_found"]) if r["fallacies_found"] is not None else "—",
            r["error"],
        )

    console.print(table)


def print_summary(console: Console, results: list[dict]) -> None:
    latencies = [r["latency_ms"] for r in results if r["status_code"] == 200]

    if not latencies:
        console.print("[red]No successful requests - cannot compute summary stats.[/red]")
        return

    latencies_sorted = sorted(latencies)
    p95_index = max(0, int(round(0.95 * (len(latencies_sorted) - 1))))

    summary = Table(title="Summary (successful requests only)")
    summary.add_column("Metric")
    summary.add_column("Latency (ms)", justify="right")
    summary.add_row("Min", f"{min(latencies):.2f}")
    summary.add_row("Max", f"{max(latencies):.2f}")
    summary.add_row("Avg", f"{statistics.mean(latencies):.2f}")
    summary.add_row("P95", f"{latencies_sorted[p95_index]:.2f}")
    summary.add_row("Success", f"{len(latencies)}/{len(results)}")

    console.print(summary)


def export_csv(results: list[dict]) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = RESULTS_DIR / f"latency_test_{timestamp}.csv"

    fieldnames = [
        "case_id",
        "category",
        "language",
        "mode",
        "started_at",
        "finished_at",
        "latency_ms",
        "server_duration_ms",
        "status_code",
        "fallacies_found",
        "error",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Latency test for POST /analyze/text")
    parser.add_argument(
        "--host",
        default="http://localhost:8080",
        help="Base URL of the FallacyX backend (default: http://localhost:8080)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="Per-request timeout in seconds (default: 120)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    console = Console()

    console.print(f"[bold]Running {len(TEST_CASES)} requests against {args.host}/analyze/text ...[/bold]")
    results = asyncio.run(run_all(args.host, args.timeout))

    print_table(console, results)
    print_summary(console, results)

    output_path = export_csv(results)
    console.print(f"\nResults exported to [bold]{output_path}[/bold]")


if __name__ == "__main__":
    main()
