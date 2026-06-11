#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════╗
║          FallacyX Backend — Performance Benchmark Suite               ║
║  Compares AMD MI300X 70B endpoint vs Dummy baseline                   ║
║  Supports concurrent load testing, percentile stats & GPU metrics     ║
╚═══════════════════════════════════════════════════════════════════════╝

Usage:
    python scripts/benchmark.py --endpoint http://localhost:8080 --runs 5
    python scripts/benchmark.py --endpoint http://10.0.0.1:8080 --model 70b --runs 3 --concurrent 10
    python scripts/benchmark.py --endpoint http://localhost:8080 --skip-dummy --export-csv

Dependencies (install separately, not in main requirements.txt):
    pip install httpx tqdm rich tabulate colorama
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import math
import os
import re
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ─────────────────────────────────────────────────────────────────────────────
# Optional imports with graceful fallback
# ─────────────────────────────────────────────────────────────────────────────
try:
    import httpx
except ImportError:
    print("[ERROR] 'httpx' is not installed. Run: pip install httpx")
    sys.exit(1)

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("[WARN] 'tqdm' not found. Progress bars disabled. Install: pip install tqdm")

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
    from rich.text import Text
    from rich import box
    HAS_RICH = True
    # Use a string-based buffer then print bytes to stdout to avoid cp1252 on Windows
    import io, sys as _sys
    _buf_console = Console(file=io.StringIO(), highlight=True, emoji=False)
    def _safe_rich_print(renderable):
        """Render via Rich to a string, then write UTF-8 bytes to stdout."""
        buf = io.StringIO()
        tmp = Console(file=buf, highlight=True, emoji=False, width=120)
        tmp.print(renderable)
        _sys.stdout.buffer.write(buf.getvalue().encode("utf-8", errors="replace"))
        _sys.stdout.buffer.flush()
    console = Console(highlight=True, emoji=False, width=120)
except ImportError:
    HAS_RICH = False
    console = None
    _safe_rich_print = None
    print("[WARN] 'rich' not found. Using plain output. Install: pip install rich")

# ─────────────────────────────────────────────────────────────────────────────
# ANSI color helpers (fallback when rich is absent)
# ─────────────────────────────────────────────────────────────────────────────
try:
    import colorama
    colorama.init(autoreset=True)
    GREEN  = colorama.Fore.GREEN
    RED    = colorama.Fore.RED
    YELLOW = colorama.Fore.YELLOW
    CYAN   = colorama.Fore.CYAN
    BOLD   = colorama.Style.BRIGHT
    RESET  = colorama.Style.RESET_ALL
except ImportError:
    GREEN = RED = YELLOW = CYAN = BOLD = RESET = ""


# ─────────────────────────────────────────────────────────────────────────────
# Test Payloads
# ─────────────────────────────────────────────────────────────────────────────

PAYLOAD_SHORT = """
Vaksin menyebabkan autisme. Banyak orang tua yang melaporkan bahwa anak mereka berubah setelah divaksinasi. 
Seorang dokter ternama juga sudah membuktikan hal ini dalam penelitiannya. Kalau kamu pro-vaksin, 
berarti kamu mendukung kerusakan pada anak-anak. Semua yang menentang fakta ini pasti sudah dibayar 
oleh perusahaan farmasi besar. Ilmuwan sejati tidak akan pernah mempertanyakan kebenaran ini karena 
sudah terbukti. Orang-orang yang mendukung vaksin tidak peduli dengan kesehatan anak.
""".strip()

PAYLOAD_MEDIUM = """
Debat Kebijakan Ekonomi Nasional

Pembicara A: "Program subsidi energi harus segera dihapuskan karena hanya merugikan negara."

Pembicara B: "Jika kita menghapus subsidi, rakyat miskin akan menderita. Kamu tidak peduli dengan 
nasib rakyat kecil. Ini sudah terbukti dari rekam jejakmu yang selalu berpihak pada korporasi besar."

Pembicara A: "Tapi data menunjukkan bahwa 70% subsidi justru dinikmati oleh golongan menengah ke atas."

Pembicara B: "Kamu bilang begitu karena kamu sendiri orang kaya yang tidak pernah merasakan 
sulitnya hidup. Setiap ekonom yang mendukung penghapusan subsidi pasti sudah dibeli oleh oligarki. 
Kalau subsidi dihapus, maka semua orang miskin akan kelaparan dan mati di jalan. Tidak ada 
jalan tengah — pilih rakyat atau pilih korporasi."

Pembicara A: "Ada opsi reformasi bertahap dengan jaring pengaman sosial yang lebih tertarget..."

Pembicara B: "Omong kosong! Reformasi bertahap itu cuma alasan untuk menunda. Semua orang tahu 
kalau reformasi itu gagal. Lihat saja negara X yang juga melakukan hal sama dan kacau. 
Berarti di sini juga pasti akan kacau. Sudah ratusan tahun subsidi ada, kenapa harus diubah sekarang? 
Tradisi ini harus dipertahankan."

Moderator: "Baik, kita akan lanjutkan dengan pertanyaan dari audiens."

Audiens: "Apakah ada bukti empiris bahwa reformasi subsidi bisa berhasil di negara berkembang?"

Pembicara B: "Pertanyaan yang bagus! Tentu saja tidak ada, karena semua pakar ekonomi yang 
bilang bisa berhasil sudah terbukti salah berkali-kali. Kalau para ahli tidak bisa memprediksi 
krisis 2008, bagaimana bisa mereka dipercaya soal subsidi? Lebih baik kita ikuti saja kebijakan 
yang sudah terbukti turun-temurun."

Peneliti: "Sebenarnya ada beberapa studi dari Brazil dan Meksiko yang menunjukkan keberhasilan 
reformasi subsidi bertarget dengan dampak positif pada kemiskinan absolut."

Pembicara B: "Itu studi dari luar negeri. Indonesia itu unik, tidak bisa dibandingkan dengan 
negara lain. Lagipula siapa yang membiayai studi itu? Pasti ada kepentingan di baliknya."
""".strip()

PAYLOAD_LONG = """
ARTIKEL PANJANG: Analisis Mendalam Kualitas Demokrasi dan Sistem Politik Indonesia di Era Digital

Pendahuluan

Demokrasi Indonesia telah mengalami transformasi signifikan sejak era Reformasi 1998. Namun, berbagai 
persoalan fundamental masih menghantui kualitas demokrasi kita, mulai dari polarisasi politik yang 
semakin dalam, hingga maraknya disinformasi di ruang digital. Tulisan ini mencoba menganalisis 
secara kritis berbagai argumen yang beredar dalam wacana publik tentang kondisi demokrasi Indonesia.

Bagian I: Tentang Kualitas Kepemimpinan

Banyak analis politik yang mengklaim bahwa kualitas pemimpin Indonesia saat ini jauh lebih buruk 
dibandingkan era sebelumnya. Argumen mereka sering kali berbunyi: "Pemimpin dulu lebih berwibawa 
dan bijaksana karena mereka lahir dari perjuangan nyata." Pernyataan ini mengandung masalah logika 
yang serius. Pertama, ia mengidealisasi masa lalu secara berlebihan tanpa mempertimbangkan konteks 
historis yang berbeda. Kedua, ia mengasumsikan bahwa pengalaman berjuang secara otomatis menghasilkan 
kepemimpinan yang lebih baik — padahal banyak pemimpin era perjuangan juga melakukan kesalahan fatal.

Kemudian ada argumen lain: "Kalau kamu tidak setuju dengan kebijakan presiden, berarti kamu tidak 
cinta negara dan ingin menghancurkan Indonesia." Ini adalah contoh klasik false dilemma sekaligus 
red herring — menyerang motif pengkritik, bukan substansi kritikannya. Dalam demokrasi yang sehat, 
kritik terhadap kebijakan adalah hak dan kewajiban warga negara yang bertanggung jawab.

Bagian II: Dinamika Partai Politik

Para pendukung sistem multipartai ekstrem sering berargumen: "Semakin banyak partai, semakin 
demokratis suatu negara." Sementara pendukung penyederhanaan partai berpendapat: "Jika jumlah 
partai tidak dikurangi, Indonesia pasti akan hancur seperti negara-negara gagal di Afrika."

Kedua argumen ini sama-sama cacat secara logika. Yang pertama melakukan over-simplifikasi 
(kualitas demokrasi tidak bisa diukur hanya dari kuantitas partai). Yang kedua menggunakan 
slippery slope dan generalisasi berlebih — banyak negara dengan sistem multipartai berjalan 
dengan sangat baik, dan banyak faktor lain yang menentukan keberhasilan sebuah negara.

Dalam konteks pemilu, sering terdengar argumen: "Semua partai sama saja korupnya, jadi tidak 
ada gunanya memilih." Argumen ini, meski dapat dipahami secara emosional, merupakan generalisasi 
berlebih yang berbahaya. Ia juga mengandung slippery slope — ketidakpercayaan pada semua partai 
bisa berujung pada apatisme politik yang justru menguntungkan status quo yang ingin diubah.

Bagian III: Peran Media dan Jurnalisme

Debat tentang peran media dalam demokrasi kerap diwarnai argumen-argumen problematik. Sebagian 
pihak berkata: "Media mainstream sudah tidak bisa dipercaya karena semua dikontrol oleh oligarki." 
Pihak lain membalas: "Media independen itu hanya portal buzzer yang menyebarkan hoaks."

Kedua posisi ekstrem ini sama-sama tidak membantu. Yang pertama melakukan sweeping generalization — 
tidak semua media mainstream bisa dikategorikan sebagai alat oligarki, dan banyak jurnalis 
profesional yang tetap menjunjung standar etika tinggi. Yang kedua juga sama — tidak semua 
media digital independen adalah portal hoaks; banyak di antaranya melakukan jurnalisme investigatif 
berkualitas tinggi.

Ada pula argumen menarik dari seorang pejabat publik yang pernah berkata dalam forum publik: 
"Saya tidak perlu memberi klarifikasi kepada media karena media tidak pernah memberitakan 
kebenaran tentang saya." Ini adalah contoh argumentum ad ignorantiam sekaligus circular reasoning 
— menggunakan ketidakpercayaan terhadap media sebagai alasan untuk tidak berinteraksi dengan media, 
yang kemudian memperkuat narrative bahwa media tidak bisa dipercaya.

Bagian IV: Isu Hak Asasi Manusia

Perdebatan tentang HAM di Indonesia sering menghasilkan argumen-argumen yang secara logika bermasalah. 
Salah satu yang paling umum adalah: "Bicara soal pelanggaran HAM masa lalu hanya akan membuka luka 
lama dan memecah belah bangsa. Lebih baik kita fokus ke depan." 

Argumen ini menggunakan appeal to emotion (takut perpecahan) untuk menghindari akuntabilitas historis. 
Ia juga mengandung false dilemma — seolah tidak mungkin untuk memproses sejarah kelam sekaligus 
membangun masa depan yang lebih baik. Kenyataannya, banyak negara yang berhasil melakukan rekonsiliasi 
nasional justru karena mereka berani menghadapi kebenaran historis, bukan menutup-nutupinya.

Di sisi lain, ada yang berargumen: "Siapapun yang mempertanyakan kebijakan keamanan nasional adalah 
simpatisan teroris dan musuh negara." Ini adalah ad hominem sekaligus guilt by association yang 
sangat berbahaya — menyerang motif pengkritik daripada merespons substansi kekhawatiran mereka.

Bagian V: Ekonomi dan Kesejahteraan

Debat ekonomi-politik di Indonesia juga penuh dengan cacat logika. Sering terdengar: "Investasi 
asing harus ditolak karena akan menjajah kita kembali secara ekonomi." Di sisi berlawanan: 
"Siapapun yang mempertanyakan investasi asing adalah anti-pembangunan dan komunis."

Kedua posisi ini menggunakan scare tactics dan label pejoratif untuk menghindari diskusi substantif. 
Kenyataannya, manfaat atau kerugian investasi asing tergantung pada desain kebijakan, negosiasi 
kontrak, dan kapasitas pengawasan — bukan pada ideologi yang disematkan kepada penanya.

Ada juga argumen populer: "Kemiskinan akan hilang jika korupsi diberantas." Meskipun korupsi 
memang berdampak buruk pada pembangunan, argumen ini terlalu menyederhanakan masalah kemiskinan 
yang multidimensional dan dipengaruhi oleh banyak faktor struktural lainnya.

Penutup

Kualitas demokrasi suatu bangsa sangat ditentukan oleh kualitas diskursus publik yang terjadi. 
Ketika argumentasi yang beredar dipenuhi oleh cacat logika — baik berupa ad hominem, false dilemma, 
slippery slope, strawman, atau appeal to emotion — maka kemampuan masyarakat untuk membuat 
keputusan kolektif yang rasional akan terganggu. Pendidikan berpikir kritis bukan kemewahan, 
melainkan kebutuhan mendasar bagi keberlangsungan demokrasi yang berkualitas.
""".strip()

PAYLOAD_TRANSCRIPT = """
[00:00:15] Selamat datang di program diskusi kita hari ini. Kita akan membahas topik yang sangat 
penting: apakah sistem pendidikan Indonesia sudah siap menghadapi era kecerdasan buatan?

[00:00:45] Narasumber pertama kita, Dr. Ahmad, adalah seorang pengamat pendidikan. Dr. Ahmad, 
pandangan Anda tentang implementasi AI di sekolah?

[00:01:10] Dr. Ahmad: Saya rasa kita perlu sangat hati-hati. Kita tidak perlu mendengarkan 
pendapat mereka yang terlalu bersemangat soal AI ini, karena kebanyakan dari mereka adalah 
orang-orang yang bekerja di perusahaan teknologi dan jelas punya kepentingan finansial.

[00:01:45] Host: Anda memiliki sudut pandang yang berbeda, Ibu Sari?

[00:02:00] Ibu Sari: Tentu. Jika kita tidak segera mengintegrasikan AI dalam pendidikan, 
generasi kita akan tertinggal jauh dan tidak akan bisa bersaing di era global. Kita tidak 
punya pilihan lain — AI atau ketinggalan zaman.

[00:02:30] Dr. Ahmad: Itulah yang saya khawatirkan. Kalau AI masuk ke kelas, guru-guru 
akan kehilangan pekerjaan mereka semua. Ini sudah terjadi di industri manufaktur, pasti 
akan terjadi hal yang sama di pendidikan. Selangkah demi selangkah, akhirnya robot yang 
mengajar anak-anak kita, dan nilai-nilai kemanusiaan akan hilang dari pendidikan.

[00:03:15] Ibu Sari: Bukti dari negara-negara maju seperti Finlandia dan Singapura menunjukkan 
bahwa integrasi teknologi justru meningkatkan kualitas mengajar guru, bukan menggantikannya.

[00:03:45] Dr. Ahmad: Finlandia itu negara kecil yang homogen. Tidak relevan dibandingkan 
dengan Indonesia yang memiliki lebih dari 270 juta penduduk dan ribuan pulau. Konteksnya 
sama sekali berbeda. Selain itu, siapa yang membiayai penelitian-penelitian itu? Pasti ada 
kepentingan di baliknya.

[00:04:20] Moderator: Mari kita dengar pertanyaan dari audiens.

[00:04:35] Penanya: Apa yang harus dilakukan untuk memastikan AI diimplementasikan dengan 
baik dan adil, terutama untuk daerah terpencil?

[00:05:00] Ibu Sari: Pertanyaan yang sangat bagus! Kita butuh infrastruktur digital yang 
merata, pelatihan guru yang komprehensif, dan kebijakan yang memastikan tidak ada daerah 
yang tertinggal.

[00:05:30] Dr. Ahmad: Semua itu hanya mimpi. Pemerintah kita tidak pernah bisa 
mengimplementasikan program pendidikan dengan baik. Ingat program laptop untuk siswa yang 
gagal? Atau program internet masuk desa yang tidak berjalan? Pasti AI juga akan sama saja.

[00:06:10] Host: Apakah ada model hybrid yang bisa menjadi solusi tengah?

[00:06:25] Ibu Sari: Tentu, model hybrid adalah pendekatan yang paling realistis. Kita 
menggunakan AI untuk tugas-tugas yang repetitif dan analitis, sementara guru fokus pada 
pengembangan karakter, kreativitas, dan kemampuan berpikir kritis siswa.

[00:07:00] Dr. Ahmad: Saya tidak percaya itu bisa berhasil. Guru-guru kita tidak terlatih 
untuk itu, dan tidak mau belajar hal baru. Generasi guru tua sudah terlalu nyaman dengan 
cara lama. Mereka semua akan menolak perubahan ini.

[00:07:45] Host: Bagaimana pendapat para ahli tentang dampak AI pada prestasi belajar siswa?

[00:08:00] Ibu Sari: Ada beberapa studi longitudinal yang menunjukkan peningkatan 15-25% 
pada pemahaman konseptual ketika AI digunakan sebagai alat bantu pembelajaran yang tepat.

[00:08:30] Dr. Ahmad: Studi-studi itu pasti disponsori oleh perusahaan AI. Tidak ada 
penelitian independen yang benar-benar membuktikan manfaat AI dalam pendidikan. Para 
ilmuwan yang mendukung AI di pendidikan pasti tidak pernah mengajar di kelas sungguhan.

[00:09:15] Moderator: Kita sudah mendekati akhir sesi. Ada pesan penutup?

[00:09:30] Ibu Sari: Transformasi digital dalam pendidikan adalah keniscayaan. Pertanyaannya 
bukan "apakah" tapi "bagaimana" kita melakukannya dengan bijak dan inklusif untuk semua siswa Indonesia.

[00:09:58] Dr. Ahmad: Saya tegaskan: jika kita melanjutkan jalur ini tanpa kehati-hatian maksimal, 
kita sedang mempertaruhkan masa depan seluruh generasi anak Indonesia. Lebih baik tidak sama sekali 
daripada melakukan kesalahan yang tidak bisa diperbaiki.
""".strip()

TEST_PAYLOADS = {
    "SHORT":      {"text": PAYLOAD_SHORT,      "label": "Short (~100 words, clear fallacies)"},
    "MEDIUM":     {"text": PAYLOAD_MEDIUM,     "label": "Medium (~400 words, multiple fallacies)"},
    "LONG":       {"text": PAYLOAD_LONG,       "label": "Long (~1500 words, dense analysis)"},
    "TRANSCRIPT": {"text": PAYLOAD_TRANSCRIPT, "label": "Transcript (~700 words, with timestamps)"},
}

# ─────────────────────────────────────────────────────────────────────────────
# Dummy HTTP Server (in-process, for baseline)
# ─────────────────────────────────────────────────────────────────────────────

DUMMY_RESPONSE = {
    "fallacies": [
        {
            "type": "ad_hominem",
            "type_label": "Ad Hominem",
            "text": "[dummy] Benchmark placeholder text",
            "explanation": "This is a hardcoded dummy response for benchmarking baseline.",
            "confidence": 0.95,
            "severity": "medium",
            "timestamp_start": None,
            "timestamp_end": None,
        }
    ],
    "overall_assessment": "Dummy response for performance baseline.",
    "logic_score": 50,
}

# ─────────────────────────────────────────────────────────────────────────────
# GPU Metrics (AMD ROCm)
# ─────────────────────────────────────────────────────────────────────────────

def collect_gpu_metrics() -> dict[str, Any]:
    """Collect AMD GPU metrics via rocm-smi. Returns empty dict if unavailable."""
    try:
        result = subprocess.run(
            ["rocm-smi", "--showmeminfo", "vram", "--showuse", "--showtemp", "--showproductname", "--json"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return {"available": False, "error": result.stderr.strip()}

        raw = json.loads(result.stdout)
        card_key = next(iter(raw.keys()))
        card = raw[card_key]

        vram_total = float(card.get("VRAM Total Memory (B)", 0))
        vram_used  = float(card.get("VRAM Total Used Memory (B)", 0))

        return {
            "available":       True,
            "gpu_name":        card.get("Card series") or card.get("Card Series", "Unknown"),
            "vram_total_gb":   round(vram_total / (1024 ** 3), 2) if vram_total else None,
            "vram_used_gb":    round(vram_used  / (1024 ** 3), 2) if vram_used  else None,
            "vram_free_gb":    round((vram_total - vram_used) / (1024 ** 3), 2) if vram_total else None,
            "gpu_util_pct":    _safe_float(card.get("GPU use (%)")),
            "temp_celsius":    _safe_float(card.get("Temperature (Sensor edge) (C)")),
        }
    except FileNotFoundError:
        return {"available": False, "error": "rocm-smi not found (not on AMD GPU host)"}
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "error": str(exc)}


def _safe_float(value) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(str(value).replace("%", "").strip())
    except (ValueError, TypeError):
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Core Benchmark Functions
# ─────────────────────────────────────────────────────────────────────────────

async def benchmark_single_request(
    client: httpx.AsyncClient,
    endpoint_url: str,
    payload: dict,
    label: str,
    timeout: float = 300.0,
) -> dict[str, Any]:
    """
    Send a single request to the endpoint and measure latency.

    Returns:
        {
          "label":           str,
          "latency_ms":      float,
          "status":          "ok" | "error" | "timeout",
          "tokens_per_sec":  float | None,
          "http_status":     int | None,
          "error":           str | None,
          "response_size_b": int,
        }
    """
    t_start = time.perf_counter()
    try:
        resp = await client.post(endpoint_url, json=payload, timeout=timeout)
        latency_ms = (time.perf_counter() - t_start) * 1000

        body = resp.json()
        body_raw = resp.content

        # Rough token estimation: count words in input + output JSON
        input_words  = len(payload.get("text", "").split())
        output_words = len(json.dumps(body).split())
        total_tokens  = (input_words + output_words) * 1.3  # ~1.3 tokens/word avg
        tokens_per_sec = (total_tokens / (latency_ms / 1000)) if latency_ms > 0 else None

        status = "ok" if resp.is_success else "error"
        return {
            "label":           label,
            "latency_ms":      latency_ms,
            "status":          status,
            "tokens_per_sec":  round(tokens_per_sec, 1) if tokens_per_sec else None,
            "http_status":     resp.status_code,
            "error":           None if resp.is_success else body.get("detail", str(resp.status_code)),
            "response_size_b": len(body_raw),
        }

    except httpx.TimeoutException:
        latency_ms = (time.perf_counter() - t_start) * 1000
        return {
            "label":           label,
            "latency_ms":      latency_ms,
            "status":          "timeout",
            "tokens_per_sec":  None,
            "http_status":     None,
            "error":           f"Request timed out after {timeout}s",
            "response_size_b": 0,
        }
    except Exception as exc:  # noqa: BLE001
        latency_ms = (time.perf_counter() - t_start) * 1000
        return {
            "label":           label,
            "latency_ms":      latency_ms,
            "status":          "error",
            "tokens_per_sec":  None,
            "http_status":     None,
            "error":           str(exc),
            "response_size_b": 0,
        }


async def benchmark_concurrent(
    endpoint_url: str,
    payload: dict,
    n_concurrent: int,
    label: str,
    timeout: float = 300.0,
) -> dict[str, Any]:
    """
    Fire `n_concurrent` requests simultaneously and collect aggregate stats.

    Returns:
        {
          "label":            str,
          "n_concurrent":     int,
          "success_count":    int,
          "error_count":      int,
          "timeout_count":    int,
          "avg_latency_ms":   float,
          "min_latency_ms":   float,
          "max_latency_ms":   float,
          "p50_ms":           float,
          "p95_ms":           float,
          "p99_ms":           float,
          "stddev_ms":        float,
          "total_duration_s": float,
          "throughput_rps":   float,
          "avg_tokens_per_sec": float | None,
        }
    """
    async with httpx.AsyncClient(timeout=timeout, limits=httpx.Limits(
        max_connections=n_concurrent + 10,
        max_keepalive_connections=n_concurrent,
    )) as client:
        t_wall_start = time.perf_counter()
        tasks = [
            benchmark_single_request(client, endpoint_url, payload, f"{label}[{i}]", timeout)
            for i in range(n_concurrent)
        ]
        results = await asyncio.gather(*tasks)
        total_duration_s = time.perf_counter() - t_wall_start

    latencies = [r["latency_ms"] for r in results if r["status"] == "ok"]
    tokens    = [r["tokens_per_sec"] for r in results if r.get("tokens_per_sec") is not None]

    success_count = sum(1 for r in results if r["status"] == "ok")
    error_count   = sum(1 for r in results if r["status"] == "error")
    timeout_count = sum(1 for r in results if r["status"] == "timeout")

    def percentile(data: list[float], p: float) -> float:
        if not data:
            return float("nan")
        sorted_data = sorted(data)
        idx = (p / 100) * (len(sorted_data) - 1)
        lo, hi = int(idx), min(int(idx) + 1, len(sorted_data) - 1)
        frac = idx - lo
        return sorted_data[lo] + frac * (sorted_data[hi] - sorted_data[lo])

    return {
        "label":              label,
        "n_concurrent":       n_concurrent,
        "success_count":      success_count,
        "error_count":        error_count,
        "timeout_count":      timeout_count,
        "avg_latency_ms":     statistics.mean(latencies)   if latencies else float("nan"),
        "min_latency_ms":     min(latencies)               if latencies else float("nan"),
        "max_latency_ms":     max(latencies)               if latencies else float("nan"),
        "p50_ms":             percentile(latencies, 50)    if latencies else float("nan"),
        "p95_ms":             percentile(latencies, 95)    if latencies else float("nan"),
        "p99_ms":             percentile(latencies, 99)    if latencies else float("nan"),
        "stddev_ms":          statistics.stdev(latencies)  if len(latencies) > 1 else 0.0,
        "total_duration_s":   round(total_duration_s, 3),
        "throughput_rps":     round(success_count / total_duration_s, 2) if total_duration_s > 0 else 0.0,
        "avg_tokens_per_sec": round(statistics.mean(tokens), 1) if tokens else None,
    }


async def _run_with_retries(
    fn,
    n_runs: int,
    *,
    run_label: str,
    progress_callback=None,
) -> list[dict]:
    """Run an async coroutine `n_runs` times and return all results."""
    results = []
    for i in range(n_runs):
        if progress_callback:
            progress_callback(run_label, i + 1, n_runs)
        res = await fn()
        results.append(res)
    return results


def _median_result(results: list[dict]) -> dict:
    """Given N benchmark result dicts, return the one closest to the median latency."""
    if not results:
        return {}
    if len(results) == 1:
        return results[0]

    key = "avg_latency_ms" if "avg_latency_ms" in results[0] else "latency_ms"
    latencies = [r.get(key, float("inf")) for r in results]
    median_val = statistics.median(latencies)
    closest = min(results, key=lambda r: abs(r.get(key, float("inf")) - median_val))
    return closest


# ─────────────────────────────────────────────────────────────────────────────
# Benchmark Suite Orchestration
# ─────────────────────────────────────────────────────────────────────────────

async def benchmark_suite(
    primary_endpoint: str,
    dummy_endpoint: Optional[str],
    secondary_endpoint: Optional[str],
    n_runs: int,
    concurrent_levels: list[int],
    timeout: float,
    payload_names: Optional[list[str]] = None,
) -> dict[str, Any]:
    """
    Full benchmark suite: all payloads × all concurrency levels × n_runs each.

    Returns a structured results dict.
    """
    payloads_to_test = {
        k: v for k, v in TEST_PAYLOADS.items()
        if payload_names is None or k in payload_names
    }

    all_results = {
        "metadata": {
            "timestamp":       datetime.now(timezone.utc).isoformat(),
            "primary_endpoint": primary_endpoint,
            "dummy_endpoint":   dummy_endpoint,
            "secondary_endpoint": secondary_endpoint,
            "n_runs":          n_runs,
            "concurrent_levels": concurrent_levels,
        },
        "gpu_metrics_before": collect_gpu_metrics(),
        "single_request":    {},  # payload_name -> {endpoint_label -> result}
        "concurrent":        {},  # payload_name -> {n_concurrent -> {endpoint_label -> result}}
        "gpu_metrics_after":  {},
    }

    endpoints: dict[str, str] = {"AMD 70B": primary_endpoint}
    if dummy_endpoint:
        endpoints["Dummy"] = dummy_endpoint
    if secondary_endpoint:
        endpoints["7B Model"] = secondary_endpoint

    total_tests = len(payloads_to_test) * len(endpoints) * (1 + len(concurrent_levels)) * n_runs

    _print_header(f"FallacyX Benchmark Suite — {total_tests} total requests")
    _print_info(f"Endpoints: {', '.join(f'{k}={v}' for k, v in endpoints.items())}")
    _print_info(f"Runs per test: {n_runs}  |  Payloads: {list(payloads_to_test.keys())}")

    async with httpx.AsyncClient(
        timeout=timeout,
        limits=httpx.Limits(max_connections=200, max_keepalive_connections=100),
    ) as shared_client:

        # ── Phase 1: Single Request Tests ────────────────────────────────────
        _print_section("Phase 1: Single Request Latency")
        for payload_name, payload_info in payloads_to_test.items():
            all_results["single_request"][payload_name] = {}
            word_count = len(payload_info["text"].split())
            _print_info(f"  Payload: {payload_name} — {payload_info['label']} ({word_count} words)")

            for ep_label, ep_url in endpoints.items():
                endpoint_path = _build_analyze_url(ep_url, payload_name)
                request_payload = _build_payload(payload_info["text"])

                runs = []
                for run_i in range(1, n_runs + 1):
                    _print_dot(f"    [{ep_label}] run {run_i}/{n_runs}")
                    r = await benchmark_single_request(
                        shared_client, endpoint_path, request_payload, ep_label, timeout
                    )
                    runs.append(r)

                median_r = _median_result(runs)
                all_results["single_request"][payload_name][ep_label] = median_r
                _print_result(ep_label, median_r)

        # ── Phase 2: Concurrent Tests ─────────────────────────────────────────
        _print_section("Phase 2: Concurrent Load Tests")
        for payload_name, payload_info in payloads_to_test.items():
            all_results["concurrent"][payload_name] = {}
            word_count = len(payload_info["text"].split())
            _print_info(f"  Payload: {payload_name} ({word_count} words)")

            for n_conc in concurrent_levels:
                all_results["concurrent"][payload_name][n_conc] = {}
                _print_info(f"    Concurrency: {n_conc}")

                for ep_label, ep_url in endpoints.items():
                    endpoint_path = _build_analyze_url(ep_url, payload_name)
                    request_payload = _build_payload(payload_info["text"])

                    runs = []
                    for run_i in range(1, n_runs + 1):
                        _print_dot(f"      [{ep_label}] concurrent={n_conc}, run {run_i}/{n_runs}")
                        r = await benchmark_concurrent(
                            endpoint_path, request_payload, n_conc, ep_label, timeout
                        )
                        runs.append(r)

                    median_r = _median_result(runs)
                    all_results["concurrent"][payload_name][n_conc][ep_label] = median_r
                    _print_concurrent_result(ep_label, n_conc, median_r)

    all_results["gpu_metrics_after"] = collect_gpu_metrics()
    return all_results


def _build_analyze_url(base_url: str, payload_name: str) -> str:
    """Build the correct API path for the analyze endpoint."""
    base = base_url.rstrip("/")
    # Transcripts use video mode endpoint
    if payload_name == "TRANSCRIPT":
        return f"{base}/api/v1/analyze"
    return f"{base}/api/v1/analyze"


def _build_payload(text: str) -> dict:
    """Build the API request payload matching FallacyX's AnalyzeRequest model."""
    has_timestamps = bool(re.search(r'\[\d{1,2}:\d{2}(:\d{2})?\]', text))
    return {
        "text":     text,
        "mode":     "quick",
        "language": "id",
        "timestamps": has_timestamps,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Dummy Endpoint Server (started in background thread)
# ─────────────────────────────────────────────────────────────────────────────

def _start_dummy_server(port: int = 9999) -> str:
    """
    Start a minimal asyncio HTTP server that returns DUMMY_RESPONSE immediately.
    Returns the base URL.
    """
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class DummyHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            # Read body (required to flush socket)
            content_len = int(self.headers.get("Content-Length", 0))
            self.rfile.read(content_len)

            response_bytes = json.dumps(DUMMY_RESPONSE).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response_bytes)))
            self.end_headers()
            self.wfile.write(response_bytes)

        def log_message(self, *args):
            pass  # Suppress log noise

    server = HTTPServer(("127.0.0.1", port), DummyHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return f"http://127.0.0.1:{port}"


# ─────────────────────────────────────────────────────────────────────────────
# Reporting
# ─────────────────────────────────────────────────────────────────────────────

def generate_report(results: dict, output_dir: Path) -> None:
    """
    Generate terminal table, benchmark_results.json, benchmark_results.md, and benchmark_results.csv.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Terminal report ───────────────────────────────────────────────────────
    _print_header("Benchmark Results Summary")

    _print_single_request_table(results)
    _print_concurrent_table(results)
    _print_gpu_summary(results)

    # ── JSON export ───────────────────────────────────────────────────────────
    json_path = output_dir / "benchmark_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    _print_info(f"  JSON saved to: {json_path}")

    # ── Markdown export ───────────────────────────────────────────────────────
    md_path = output_dir / "benchmark_results.md"
    _write_markdown_report(results, md_path)
    _print_info(f"  Markdown saved to: {md_path}")

    # ── CSV export ────────────────────────────────────────────────────────────
    csv_path = output_dir / "benchmark_results.csv"
    _write_csv_report(results, csv_path)
    _print_info(f"  CSV saved to: {csv_path}")


def _latency_color(ms: float) -> str:
    """Return ANSI color based on latency thresholds."""
    if math.isnan(ms):
        return RED
    if ms < 2000:
        return GREEN
    if ms < 8000:
        return YELLOW
    return RED


def _speedup_str(primary_ms: float, baseline_ms: float) -> str:
    if math.isnan(primary_ms) or math.isnan(baseline_ms) or baseline_ms == 0:
        return "N/A"
    ratio = baseline_ms / primary_ms
    color = GREEN if ratio >= 1.0 else RED
    return f"{color}{ratio:.1f}x{RESET}"


def _fmt_ms(ms: float) -> str:
    if math.isnan(ms):
        return f"{RED}ERROR{RESET}"
    color = _latency_color(ms)
    if ms >= 1000:
        return f"{color}{ms / 1000:.2f}s{RESET}"
    return f"{color}{ms:.0f}ms{RESET}"


def _print_single_request_table(results: dict) -> None:
    single = results.get("single_request", {})
    if not single:
        return

    _print_section("Single Request Latency (Median of N runs)")

    # Gather all endpoint labels
    ep_labels = []
    for payload_data in single.values():
        for lbl in payload_data.keys():
            if lbl not in ep_labels:
                ep_labels.append(lbl)

    if HAS_RICH:
        table = Table(title="Single Request Benchmark", box=box.ROUNDED, highlight=True)
        table.add_column("Payload",     style="cyan",   no_wrap=True)
        table.add_column("Words",       justify="right")
        for lbl in ep_labels:
            table.add_column(f"{lbl} (ms)", justify="right")
        if "AMD 70B" in ep_labels and "Dummy" in ep_labels:
            table.add_column("Speedup vs Dummy", justify="right")
        table.add_column("Status", justify="center")

        for payload_name, payload_data in single.items():
            word_count = len(TEST_PAYLOADS.get(payload_name, {}).get("text", "").split())
            row = [payload_name, str(word_count)]

            latencies_by_ep = {}
            for lbl in ep_labels:
                r = payload_data.get(lbl, {})
                lat = r.get("latency_ms", float("nan"))
                latencies_by_ep[lbl] = lat
                color = "green" if lat < 2000 else ("yellow" if lat < 8000 else "red")
                row.append(f"[{color}]{lat:.0f}[/{color}]" if not math.isnan(lat) else "[red]ERROR[/red]")

            if "AMD 70B" in ep_labels and "Dummy" in ep_labels:
                ratio = latencies_by_ep.get("Dummy", float("nan")) / latencies_by_ep.get("AMD 70B", float("nan") or 1)
                row.append(f"{ratio:.1f}x" if not math.isnan(ratio) else "N/A")

            statuses = [payload_data.get(lbl, {}).get("status", "?") for lbl in ep_labels]
            all_ok = all(s == "ok" for s in statuses)
            row.append("[green]✓[/green]" if all_ok else "[red]✗[/red]")
            table.add_row(*row)

        _safe_rich_print(table)
    else:
        # Plain text table
        header = f"{'Payload':<14} {'Words':>6}"
        for lbl in ep_labels:
            header += f"  {lbl:>14}"
        if "AMD 70B" in ep_labels and "Dummy" in ep_labels:
            header += f"  {'Speedup':>8}"
        print(f"\n{BOLD}{header}{RESET}")
        print("─" * len(header))

        for payload_name, payload_data in single.items():
            word_count = len(TEST_PAYLOADS.get(payload_name, {}).get("text", "").split())
            row = f"{payload_name:<14} {word_count:>6}"
            latencies_by_ep = {}
            for lbl in ep_labels:
                lat = payload_data.get(lbl, {}).get("latency_ms", float("nan"))
                latencies_by_ep[lbl] = lat
                row += f"  {_fmt_ms(lat):>14}"
            if "AMD 70B" in ep_labels and "Dummy" in ep_labels:
                row += f"  {_speedup_str(latencies_by_ep.get('AMD 70B', float('nan')), latencies_by_ep.get('Dummy', float('nan'))):>8}"
            print(row)


def _print_concurrent_table(results: dict) -> None:
    concurrent = results.get("concurrent", {})
    if not concurrent:
        return

    _print_section("Concurrent Load Test Results")

    for payload_name, conc_data in concurrent.items():
        print(f"\n  {BOLD}{CYAN}Payload: {payload_name}{RESET}")

        ep_labels = []
        for n_conc, ep_data in conc_data.items():
            for lbl in ep_data.keys():
                if lbl not in ep_labels:
                    ep_labels.append(lbl)

        if HAS_RICH:
            table = Table(title=f"Concurrent — {payload_name}", box=box.SIMPLE_HEAD)
            table.add_column("Conc.", justify="right", style="cyan")
            for lbl in ep_labels:
                table.add_column(f"{lbl} avg", justify="right")
                table.add_column(f"{lbl} p95", justify="right")
                table.add_column(f"{lbl} RPS", justify="right")
            table.add_column("Success%", justify="right")

            for n_conc in sorted(conc_data.keys(), key=int):
                ep_data = conc_data[n_conc]
                row = [str(n_conc)]
                success_rates = []
                for lbl in ep_labels:
                    r = ep_data.get(lbl, {})
                    avg = r.get("avg_latency_ms", float("nan"))
                    p95 = r.get("p95_ms", float("nan"))
                    rps = r.get("throughput_rps", 0)
                    n   = r.get("n_concurrent", 1)
                    ok  = r.get("success_count", 0)
                    success_rates.append(ok / n * 100 if n > 0 else 0)

                    avg_color = "green" if avg < 5000 else ("yellow" if avg < 15000 else "red")
                    row.append(f"[{avg_color}]{avg:.0f}ms[/{avg_color}]" if not math.isnan(avg) else "[red]N/A[/red]")
                    row.append(f"{p95:.0f}ms" if not math.isnan(p95) else "N/A")
                    row.append(f"{rps:.1f}")

                avg_success = statistics.mean(success_rates) if success_rates else 0
                success_color = "green" if avg_success >= 99 else ("yellow" if avg_success >= 90 else "red")
                row.append(f"[{success_color}]{avg_success:.0f}%[/{success_color}]")
                table.add_row(*row)

            _safe_rich_print(table)
        else:
            header = f"  {'Conc':>5}"
            for lbl in ep_labels:
                header += f"  {lbl+' avg':>14}  {lbl+' p95':>12}  {lbl+' RPS':>8}"
            print(f"  {BOLD}{header}{RESET}")
            print("  " + "─" * (len(header) - 2))

            for n_conc in sorted(conc_data.keys(), key=int):
                ep_data = conc_data[n_conc]
                row = f"  {n_conc:>5}"
                for lbl in ep_labels:
                    r = ep_data.get(lbl, {})
                    avg = r.get("avg_latency_ms", float("nan"))
                    p95 = r.get("p95_ms", float("nan"))
                    rps = r.get("throughput_rps", 0)
                    row += f"  {_fmt_ms(avg):>14}  {_fmt_ms(p95):>12}  {rps:>8.1f}"
                print(row)


def _print_gpu_summary(results: dict) -> None:
    before = results.get("gpu_metrics_before", {})
    after  = results.get("gpu_metrics_after", {})

    if not before.get("available") and not after.get("available"):
        _print_info("  GPU metrics not available (not on AMD ROCm host)")
        return

    _print_section("GPU Metrics (AMD ROCm)")
    for phase, gpu in [("Before", before), ("After", after)]:
        if gpu.get("available"):
            print(
                f"  {BOLD}{phase}{RESET}: {gpu.get('gpu_name', '?')} | "
                f"VRAM {gpu.get('vram_used_gb','?')}/{gpu.get('vram_total_gb','?')} GB | "
                f"Util: {gpu.get('gpu_util_pct','?')}% | "
                f"Temp: {gpu.get('temp_celsius','?')}°C"
            )
        else:
            print(f"  {phase}: {gpu.get('error', 'unavailable')}")


def _write_markdown_report(results: dict, path: Path) -> None:
    meta = results.get("metadata", {})
    lines = [
        "# FallacyX Backend Benchmark Results",
        "",
        f"**Generated:** {meta.get('timestamp', 'N/A')}  ",
        f"**Primary Endpoint:** `{meta.get('primary_endpoint', 'N/A')}`  ",
        f"**Dummy Endpoint:** `{meta.get('dummy_endpoint', 'N/A')}`  ",
        f"**Runs per test:** {meta.get('n_runs', 'N/A')}  ",
        "",
        "---",
        "",
        "## Single Request Latency",
        "",
    ]

    single = results.get("single_request", {})
    ep_labels = []
    for pd in single.values():
        for lbl in pd.keys():
            if lbl not in ep_labels:
                ep_labels.append(lbl)

    # Table header
    header_cols = ["Payload", "Words"] + ep_labels
    if "AMD 70B" in ep_labels and "Dummy" in ep_labels:
        header_cols.append("Speedup vs Dummy")
    lines.append("| " + " | ".join(header_cols) + " |")
    lines.append("| " + " | ".join(["---"] * len(header_cols)) + " |")

    for payload_name, payload_data in single.items():
        word_count = len(TEST_PAYLOADS.get(payload_name, {}).get("text", "").split())
        row = [payload_name, str(word_count)]
        latencies = {}
        for lbl in ep_labels:
            lat = payload_data.get(lbl, {}).get("latency_ms", float("nan"))
            latencies[lbl] = lat
            row.append(f"{lat:.0f}ms" if not math.isnan(lat) else "ERROR")
        if "AMD 70B" in ep_labels and "Dummy" in ep_labels:
            amd = latencies.get("AMD 70B", float("nan"))
            dum = latencies.get("Dummy", float("nan"))
            if not math.isnan(amd) and not math.isnan(dum) and amd > 0:
                row.append(f"{dum / amd:.1f}x")
            else:
                row.append("N/A")
        lines.append("| " + " | ".join(row) + " |")

    # Concurrent tables per payload
    lines += ["", "---", "", "## Concurrent Load Tests", ""]
    concurrent = results.get("concurrent", {})
    for payload_name, conc_data in concurrent.items():
        lines.append(f"### Payload: {payload_name}")
        lines.append("")
        ep_labels_c: list[str] = []
        for ep_data in conc_data.values():
            for lbl in ep_data.keys():
                if lbl not in ep_labels_c:
                    ep_labels_c.append(lbl)

        header_cols_c = ["Concurrent"]
        for lbl in ep_labels_c:
            header_cols_c += [f"{lbl} avg", f"{lbl} p50", f"{lbl} p95", f"{lbl} p99", f"{lbl} RPS"]
        header_cols_c.append("Success%")

        lines.append("| " + " | ".join(header_cols_c) + " |")
        lines.append("| " + " | ".join(["---"] * len(header_cols_c)) + " |")

        for n_conc in sorted(conc_data.keys(), key=int):
            ep_data = conc_data[n_conc]
            row_c = [str(n_conc)]
            total_ok = total_n = 0
            for lbl in ep_labels_c:
                r = ep_data.get(lbl, {})
                row_c += [
                    f"{r.get('avg_latency_ms', float('nan')):.0f}ms",
                    f"{r.get('p50_ms', float('nan')):.0f}ms",
                    f"{r.get('p95_ms', float('nan')):.0f}ms",
                    f"{r.get('p99_ms', float('nan')):.0f}ms",
                    f"{r.get('throughput_rps', 0):.1f}",
                ]
                total_ok += r.get("success_count", 0)
                total_n  += r.get("n_concurrent", 0)
            success_pct = (total_ok / total_n * 100) if total_n > 0 else 0
            row_c.append(f"{success_pct:.0f}%")
            lines.append("| " + " | ".join(row_c) + " |")

        lines.append("")

    # GPU
    before = results.get("gpu_metrics_before", {})
    after  = results.get("gpu_metrics_after", {})
    if before.get("available") or after.get("available"):
        lines += ["---", "", "## GPU Metrics (AMD ROCm)", ""]
        for phase, gpu in [("Before", before), ("After", after)]:
            if gpu.get("available"):
                lines.append(
                    f"**{phase}:** {gpu.get('gpu_name','?')} | "
                    f"VRAM {gpu.get('vram_used_gb','?')}/{gpu.get('vram_total_gb','?')} GB | "
                    f"Util: {gpu.get('gpu_util_pct','?')}% | "
                    f"Temp: {gpu.get('temp_celsius','?')}°C  "
                )

    path.write_text("\n".join(lines), encoding="utf-8")


def _write_csv_report(results: dict, path: Path) -> None:
    rows = []

    # Single request rows
    for payload_name, payload_data in results.get("single_request", {}).items():
        for ep_label, r in payload_data.items():
            rows.append({
                "test_type":        "single",
                "payload":          payload_name,
                "endpoint":         ep_label,
                "n_concurrent":     1,
                "latency_ms":       r.get("latency_ms", ""),
                "avg_latency_ms":   r.get("latency_ms", ""),
                "p50_ms":           r.get("latency_ms", ""),
                "p95_ms":           "",
                "p99_ms":           "",
                "min_ms":           "",
                "max_ms":           "",
                "stddev_ms":        "",
                "throughput_rps":   "",
                "success_count":    1 if r.get("status") == "ok" else 0,
                "error_count":      1 if r.get("status") == "error" else 0,
                "timeout_count":    1 if r.get("status") == "timeout" else 0,
                "tokens_per_sec":   r.get("tokens_per_sec", ""),
                "status":           r.get("status", ""),
            })

    # Concurrent rows
    for payload_name, conc_data in results.get("concurrent", {}).items():
        for n_conc, ep_data in conc_data.items():
            for ep_label, r in ep_data.items():
                rows.append({
                    "test_type":        "concurrent",
                    "payload":          payload_name,
                    "endpoint":         ep_label,
                    "n_concurrent":     n_conc,
                    "latency_ms":       "",
                    "avg_latency_ms":   r.get("avg_latency_ms", ""),
                    "p50_ms":           r.get("p50_ms", ""),
                    "p95_ms":           r.get("p95_ms", ""),
                    "p99_ms":           r.get("p99_ms", ""),
                    "min_ms":           r.get("min_latency_ms", ""),
                    "max_ms":           r.get("max_latency_ms", ""),
                    "stddev_ms":        r.get("stddev_ms", ""),
                    "throughput_rps":   r.get("throughput_rps", ""),
                    "success_count":    r.get("success_count", ""),
                    "error_count":      r.get("error_count", ""),
                    "timeout_count":    r.get("timeout_count", ""),
                    "tokens_per_sec":   r.get("avg_tokens_per_sec", ""),
                    "status":           "ok" if r.get("success_count", 0) == r.get("n_concurrent", 0) else "partial",
                })

    if not rows:
        return

    fieldnames = [
        "test_type", "payload", "endpoint", "n_concurrent",
        "latency_ms", "avg_latency_ms", "p50_ms", "p95_ms", "p99_ms",
        "min_ms", "max_ms", "stddev_ms", "throughput_rps",
        "success_count", "error_count", "timeout_count",
        "tokens_per_sec", "status",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# ─────────────────────────────────────────────────────────────────────────────
# Console Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _print_header(text: str) -> None:
    if HAS_RICH:
        try:
            console.rule(f"[bold cyan]{text}[/bold cyan]")
        except Exception:
            _safe_rich_print(f"[bold cyan]{'=' * 4} {text} {'=' * 4}[/bold cyan]")
    else:
        border = "=" * (len(text) + 4)
        print(f"\n{BOLD}{CYAN}+{border}+{RESET}")
        print(f"{BOLD}{CYAN}|  {text}  |{RESET}")
        print(f"{BOLD}{CYAN}+{border}+{RESET}\n")


def _print_section(text: str) -> None:
    if HAS_RICH:
        _safe_rich_print(f"\n[bold yellow]>> {text}[/bold yellow]")
    else:
        print(f"\n{BOLD}{YELLOW}>> {text}{RESET}")


def _print_info(text: str) -> None:
    if HAS_RICH:
        _safe_rich_print(f"  [dim]{text}[/dim]")
    else:
        print(f"  {text}")


def _print_dot(text: str) -> None:
    """Print in-progress indicator."""
    if HAS_RICH:
        _safe_rich_print(f"    [dim]. {text}[/dim]")
    else:
        print(f"    . {text}")


def _print_result(label: str, result: dict) -> None:
    lat = result.get("latency_ms", float("nan"))
    status = result.get("status", "?")
    tps = result.get("tokens_per_sec")

    color = GREEN if status == "ok" else RED
    tps_str = f" | {tps:.0f} tok/s" if tps else ""

    if HAS_RICH:
        status_color = "green" if status == "ok" else "red"
        lat_str = f"{lat:.0f}ms" if not math.isnan(lat) else "ERROR"
        try:
            _safe_rich_print(f"      [{status_color}]{label}: {lat_str}{tps_str}[/{status_color}]")
        except Exception:
            print(f"      {label}: {lat_str}{tps_str}")
    else:
        lat_str = f"{lat:.0f}ms" if not math.isnan(lat) else "ERROR"
        print(f"      {color}{label}: {lat_str}{tps_str}{RESET}")


def _print_concurrent_result(label: str, n_conc: int, result: dict) -> None:
    avg = result.get("avg_latency_ms", float("nan"))
    p95 = result.get("p95_ms", float("nan"))
    rps = result.get("throughput_rps", 0)
    ok  = result.get("success_count", 0)

    color = GREEN if ok == n_conc else (YELLOW if ok > 0 else RED)
    if HAS_RICH:
        c = "green" if ok == n_conc else ("yellow" if ok > 0 else "red")
        avg_s = f"{avg:.0f}ms" if not math.isnan(avg) else "N/A"
        p95_s = f"{p95:.0f}ms" if not math.isnan(p95) else "N/A"
        try:
            _safe_rich_print(
                f"        [{c}]{label}: avg={avg_s} p95={p95_s} rps={rps:.1f} ({ok}/{n_conc} ok)[/{c}]"
            )
        except Exception:
            print(f"        {label}: avg={avg_s} p95={p95_s} rps={rps:.1f} ({ok}/{n_conc} ok)")
    else:
        avg_s = f"{avg:.0f}ms" if not math.isnan(avg) else "N/A"
        p95_s = f"{p95:.0f}ms" if not math.isnan(p95) else "N/A"
        print(f"        {color}{label}: avg={avg_s} p95={p95_s} rps={rps:.1f} ({ok}/{n_conc} ok){RESET}")


# ─────────────────────────────────────────────────────────────────────────────
# Argument Parser & Main
# ─────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="FallacyX Backend Performance Benchmark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/benchmark.py --endpoint http://localhost:8080
  python scripts/benchmark.py --endpoint http://10.0.0.1:8080 --runs 5 --concurrent 1,5,10,20
  python scripts/benchmark.py --endpoint http://localhost:8080 --model 7b --secondary http://localhost:8081
  python scripts/benchmark.py --endpoint http://localhost:8080 --payloads SHORT,MEDIUM --skip-dummy
  python scripts/benchmark.py --endpoint http://localhost:8080 --timeout 600 --output-dir ./my_results
        """,
    )

    parser.add_argument(
        "--endpoint", "-e",
        default="http://localhost:8080",
        help="Primary endpoint base URL (AMD 70B model). Default: http://localhost:8080",
    )
    parser.add_argument(
        "--model", "-m",
        default="70b",
        choices=["70b", "7b", "72b", "8b"],
        help="Model size label for the primary endpoint. Default: 70b",
    )
    parser.add_argument(
        "--secondary",
        default=None,
        help="Optional secondary endpoint URL for comparison (e.g. 7B model).",
    )
    parser.add_argument(
        "--runs", "-r",
        type=int,
        default=3,
        help="Number of runs per test. Median is taken. Default: 3",
    )
    parser.add_argument(
        "--concurrent", "-c",
        default="1,5,10,20,50",
        help="Comma-separated concurrency levels. Default: 1,5,10,20,50",
    )
    parser.add_argument(
        "--payloads", "-p",
        default=None,
        help="Comma-separated subset of payloads to test: SHORT,MEDIUM,LONG,TRANSCRIPT. Default: all",
    )
    parser.add_argument(
        "--skip-dummy",
        action="store_true",
        help="Skip the dummy baseline endpoint.",
    )
    parser.add_argument(
        "--dummy-port",
        type=int,
        default=9999,
        help="Port for the in-process dummy HTTP server. Default: 9999",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=300.0,
        help="Per-request timeout in seconds. Default: 300",
    )
    parser.add_argument(
        "--output-dir",
        default="./benchmark_results",
        help="Directory to save result files. Default: ./benchmark_results",
    )
    parser.add_argument(
        "--no-concurrent",
        action="store_true",
        help="Skip concurrent load tests (only run single request tests).",
    )

    return parser.parse_args()


async def async_main() -> None:
    args = parse_args()

    # Parse concurrent levels
    concurrent_levels = [int(x.strip()) for x in args.concurrent.split(",") if x.strip()]
    if args.no_concurrent:
        concurrent_levels = []

    # Parse payload filter
    payload_names = None
    if args.payloads:
        payload_names = [p.strip().upper() for p in args.payloads.split(",")]
        invalid = set(payload_names) - set(TEST_PAYLOADS.keys())
        if invalid:
            print(f"[ERROR] Unknown payload(s): {invalid}. Valid: {list(TEST_PAYLOADS.keys())}")
            sys.exit(1)

    # Start dummy server
    dummy_url: Optional[str] = None
    if not args.skip_dummy:
        try:
            dummy_url = _start_dummy_server(port=args.dummy_port)
            _print_info(f"Dummy server started at {dummy_url}")
            # Give server a moment to be ready
            await asyncio.sleep(0.3)
        except OSError as exc:
            _print_info(f"[WARN] Could not start dummy server on port {args.dummy_port}: {exc}")
            dummy_url = None

    # Label primary endpoint with model size
    model_label = f"AMD {args.model.upper()}"

    # Run suite
    results = await benchmark_suite(
        primary_endpoint=args.endpoint,
        dummy_endpoint=dummy_url,
        secondary_endpoint=args.secondary,
        n_runs=args.runs,
        concurrent_levels=concurrent_levels,
        timeout=args.timeout,
        payload_names=payload_names,
    )

    # Rename "AMD 70B" label if different model was specified
    if args.model.upper() != "70B":
        _relabel_results(results, "AMD 70B", model_label)

    # Generate and save reports
    output_dir = Path(args.output_dir)
    generate_report(results, output_dir)


def _relabel_results(results: dict, old_label: str, new_label: str) -> None:
    """Rename an endpoint label throughout the results dict."""
    for payload_data in results.get("single_request", {}).values():
        if old_label in payload_data:
            payload_data[new_label] = payload_data.pop(old_label)

    for conc_data in results.get("concurrent", {}).values():
        for ep_data in conc_data.values():
            if old_label in ep_data:
                ep_data[new_label] = ep_data.pop(old_label)


def main() -> None:
    _print_header("FallacyX — Backend Benchmark Suite")
    asyncio.run(async_main())
    _print_header("Benchmark Complete")


if __name__ == "__main__":
    main()
