<div align="center">

<!-- BADGES -->
<p>
  <img src="https://img.shields.io/badge/AMD%20Developer%20Hackathon-ACT%20II-ED1C24?style=for-the-badge&logo=amd&logoColor=white" alt="AMD Developer Hackathon ACT II"/>
  <img src="https://img.shields.io/badge/lablab.ai-Hackathon-6C47FF?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIxMiIgY3k9IjEyIiByPSIxMiIgZmlsbD0id2hpdGUiLz48L3N2Zz4=&logoColor=white" alt="lablab.ai"/>
  <img src="https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge" alt="MIT License"/>
  <img src="https://img.shields.io/badge/SvelteKit-5.x-FF3E00?style=for-the-badge&logo=svelte&logoColor=white" alt="SvelteKit"/>
  <img src="https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/AMD%20MI300X-192GB%20VRAM-ED1C24?style=for-the-badge&logo=amd&logoColor=white" alt="AMD MI300X"/>
  <img src="https://img.shields.io/badge/vLLM-Llama--3--70B-F59E0B?style=for-the-badge" alt="vLLM Llama-3-70B"/>
</p>

<br/>

# ⚖️ FallacyChecker

### *Submit an argument. Receive a verdict.*

**Real-time logical fallacy detection for text, articles, YouTube videos, and audio — powered by Llama-3-70B on AMD MI300X.**

*A feature of the [Revonalar](https://revonalar.com) critical-thinking education platform.*

<br/>

> **🏆 Built for AMD Developer Hackathon ACT II on lablab.ai**

<br/>

<!-- HERO IMAGE PLACEHOLDER -->
<!-- Replace with actual screenshot: -->
<!-- ![FallacyChecker Hero](./docs/screenshots/hero.png) -->

```
╔══════════════════════════════════════════════════════════════════╗
║  [ HERO SCREENSHOT / GIF PLACEHOLDER ]                           ║
║                                                                  ║
║  FallacyChecker UI — Glassmorphism + Classical Editorial Design  ║
║  Screenshot: /fallacy → analysis → verdict                       ║
╚══════════════════════════════════════════════════════════════════╝
```

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Why AMD MI300X](#-why-amd-mi300x)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Integration with Revonalar](#-integration-with-revonalar)
- [Roadmap](#-roadmap)
- [License & Acknowledgments](#-license--acknowledgments)

---

## 🔍 Overview

### The Problem: Rhetoric Is Winning Over Reason

In an era of social media, viral debates, and algorithmically amplified discourse, logical fallacies are weaponized daily. Ad hominem attacks derail policy discussions. Slippery slope arguments shut down nuanced reform proposals. False dilemmas force binary choices on complex issues. The average person encounters dozens of these rhetorical tricks every day — in news articles, YouTube debates, political speeches, and online comment sections — yet rarely has the tools to identify and counter them in real time.

The cost is not merely academic. Decisions about public health, economic policy, civil rights, and democratic participation are shaped by arguments that fail basic logical standards. When rhetoric masquerades as reason, the quality of collective decision-making suffers at scale.

### The Solution: An AI Tribunal for Logic

FallacyChecker is a real-time logical analysis engine that accepts text, URLs, YouTube video links, and audio recordings, then returns a structured **verdict**: a ranked list of detected fallacies, each with the exact excerpt, an explanation of the logical error, a confidence score, and a suggested correction. The system detects **25 categories** of logical fallacies — from the canonical (Ad Hominem, Straw Man, False Dilemma) to the subtle (Modus Tollens violations, Equivocation, Special Pleading) — across both English and Indonesian language content.

Built on **Llama-3-70B** running on **AMD MI300X** via vLLM, the system achieves high reasoning quality that smaller models cannot match. The 70-billion-parameter architecture enables chain-of-thought analysis, nuanced contextual understanding, and structured JSON output in a single forward pass — making it suitable for analyzing complex multi-speaker transcripts and long-form political or academic texts.

### The Revonalar Connection

FallacyChecker is not a standalone product — it is the analytical core of **Revonalar**, an Indonesian critical-thinking education platform. Every analysis users perform contributes to a community knowledge base: a leaderboard of the most fallacious public arguments, a personal history of debates examined, and a growing precedent library stored in Qdrant vector database. This **Retrieval-Augmented Generation (RAG)** layer allows the system to surface similar historical fallacies, enriching each verdict with precedent and improving accuracy over time.

### Why AMD MI300X Is the Right Hardware for This Problem

Analyzing a 1,500-word article for logical fallacies requires sustained, context-aware reasoning — not pattern matching. Llama-3-70B must hold the entire argument in context, identify rhetorical structures, compare claims to each other, and generate structured explanations. This demands a GPU with massive memory bandwidth and sufficient VRAM to run the model comfortably without quantization degradation. The AMD MI300X, with **192 GB of unified HBM3 VRAM** and **5.3 TB/s memory bandwidth**, is the only GPU class that can run Llama-3-70B at full BF16 precision with generous context windows — producing verdicts of significantly higher quality than GPTQ-4bit or AWQ-compressed alternatives on smaller hardware.

---

## 🏗 System Architecture

### High-Level Architecture

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         FALLACYCHECKER SYSTEM ARCHITECTURE                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

  ┌──────────────────────────────────────────────────────────────────────────┐
  │                         CLIENT LAYER                                     │
  │                                                                          │
  │  ┌─────────────────────┐    ┌──────────────────────┐                    │
  │  │  Browser (SvelteKit) │    │  Chrome Extension     │                   │
  │  │  revonalar.com       │    │  (Sidebar Panel)      │                   │
  │  │  /fallacy            │    │  Right-click → Check  │                   │
  │  └──────────┬──────────┘    └──────────┬───────────┘                    │
  └─────────────┼──────────────────────────┼────────────────────────────────┘
                │                          │
                └──────────┬───────────────┘
                           │  HTTPS / REST API
                           ▼
  ┌──────────────────────────────────────────────────────────────────────────┐
  │                    EDGE LAYER (Cloudflare)                               │
  │                                                                          │
  │   ┌─────────────────────────────────────────────────────────────────┐   │
  │   │              Cloudflare Pages (SvelteKit SSR/SSG)               │   │
  │   │  Route: /fallacy         → Analysis input & live results        │   │
  │   │  Route: /fallacy/result  → Full verdict report                  │   │
  │   │  Route: /fallacy/history → Personal analysis archive            │   │
  │   │  Route: /fallacy/leader  → Community fallacy leaderboard        │   │
  │   └─────────────────────────────────────────────────────────────────┘   │
  └─────────────────────────────┬────────────────────────────────────────────┘
                                │  REST API  /api/v1/
                                │  (JSON over HTTPS)
                                ▼
  ┌──────────────────────────────────────────────────────────────────────────┐
  │                    API LAYER (AMD Developer Cloud)                       │
  │                                                                          │
  │   ┌────────────────────┐    ┌──────────────────────────────────────┐    │
  │   │  Nginx (TLS / LB)  │───▶│  FastAPI + Uvicorn (Gunicorn)        │    │
  │   │  Port 443 / 80     │    │  Port 8080                            │    │
  │   └────────────────────┘    │                                       │    │
  │                             │  Routers:                             │    │
  │                             │  POST /api/v1/analyze  (text/url)    │    │
  │                             │  POST /api/v1/analyze/youtube        │    │
  │                             │  POST /api/v1/analyze/audio          │    │
  │                             │  POST /api/v1/analyze/batch          │    │
  │                             │  GET  /api/v1/rag/similar            │    │
  │                             │  GET  /health                        │    │
  │                             └──────────────┬────────────────────────┘   │
  │                                            │                             │
  │         ┌──────────────────────────────────┼──────────────────────────┐ │
  │         │                    SERVICE MESH  │                           │ │
  │         ▼                                  ▼                           │ │
  │  ┌─────────────┐                  ┌────────────────┐                  │ │
  │  │   Redis      │                  │  Celery Workers │                  │ │
  │  │   Port 6379  │                  │  (Async tasks)  │                  │ │
  │  │   Result     │                  │  Batch analysis │                  │ │
  │  │   Cache      │                  └────────────────┘                  │ │
  │  └─────────────┘                                                       │ │
  └────────────────────────────────────────────────────────────────────────┘ │
                                │                                             │
         ┌──────────────────────┼──────────────────────────────────────┐     │
         │                      │      INFERENCE LAYER                 │     │
         ▼                      ▼                           ▼           │     │
  ┌─────────────┐    ┌─────────────────────┐    ┌──────────────────┐  │     │
  │  Whisper    │    │  vLLM               │    │  Qdrant          │  │     │
  │  ASR Engine │    │  OpenAI-compatible  │    │  Vector DB       │  │     │
  │  faster-    │    │  inference server   │    │  Port 6333/6334  │  │     │
  │  whisper    │    │  Port 8000          │    │  Fallacy         │  │     │
  │  large-v3   │    │                     │    │  precedent RAG   │  │     │
  │  Port 8001  │    │  Model: Llama-3-70B │    │                  │  │     │
  └──────┬──────┘    │  BF16, 8192 ctx     │    └──────────────────┘  │     │
         │           │  tensor-parallel=1  │                           │     │
         │           │  mem-util: 85%      │                           │     │
         │           └──────────┬──────────┘                           │     │
         │                      │                                       │     │
         └──────────────────────┘                                       │     │
                                │                                       │     │
                                ▼                                             │
  ┌──────────────────────────────────────────────────────────────────────┐   │
  │                     AMD MI300X GPU                                   │   │
  │                                                                      │   │
  │   Architecture : CDNA3                  VRAM : 192 GB HBM3           │   │
  │   Compute Units: 304 CU                 BW   : 5.3 TB/s              │   │
  │   ROCm Version : 6.1                    TDP  : 750W                  │   │
  │                                                                      │   │
  │   ┌─────────────────────────────────────────────────────────────┐   │   │
  │   │   Llama-3-70B BF16 weights ≈ 140 GB  │  Working memory: 52GB│   │   │
  │   └─────────────────────────────────────────────────────────────┘   │   │
  └──────────────────────────────────────────────────────────────────────┘   │
                                                                              │
  ┌──────────────────────────────────────────────────────────────────────┐   │
  │                     PERSISTENCE LAYER (Supabase)                     │   │
  │   PostgreSQL (analysis history, user data, community leaderboard)    │   │
  │   Shared with Revonalar main platform (Singapore region)             │   │
  └──────────────────────────────────────────────────────────────────────┘
```

### Analysis Pipeline Flow

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │                  FALLACY DETECTION PIPELINE                         │
  └─────────────────────────────────────────────────────────────────────┘

  Input Received
       │
       ├─── TEXT ────────────────────────────────────────┐
       │                                                  │
       ├─── URL ──► [BeautifulSoup Scraper]               │
       │            [readability-lxml]                    │
       │            [Clean article text]                  │
       │                                                  │
       ├─── YOUTUBE ──► [yt-dlp audio extract]            │
       │                [Whisper large-v3 ASR]            │
       │                [Timestamped transcript]          │
       │                                                  │
       └─── AUDIO ──► [FFmpeg preprocess]                 │
                      [Whisper large-v3 ASR]              │
                      [Timestamped transcript]            │
                                                          │
                                 ┌────────────────────────┘
                                 │  Normalized text + metadata
                                 ▼
              ┌──────────────────────────────────────────┐
              │         PROMPT ENGINEERING               │
              │  System prompt (classifier role)         │
              │  Few-shot examples (5 per fallacy type)  │
              │  Structured output schema (JSON)         │
              │  Language detection (EN / ID)            │
              └───────────────────┬──────────────────────┘
                                  │
                                  ▼
              ┌──────────────────────────────────────────┐
              │     vLLM — Llama-3-70B Inference         │
              │   ┌────────────────────────────────────┐ │
              │   │  Chain-of-thought reasoning        │ │
              │   │  Contextual claim comparison       │ │
              │   │  Cross-reference within text       │ │
              │   │  Structured JSON generation        │ │
              │   └────────────────────────────────────┘ │
              └───────────────────┬──────────────────────┘
                                  │
                    ┌─────────────┴──────────────┐
                    │                            │
                    ▼                            ▼
         ┌─────────────────┐         ┌──────────────────────┐
         │   Qdrant RAG    │         │   Response Assembly  │
         │   Embed excerpt │         │   Parse + validate   │
         │   Retrieve top-3│         │   JSON schema        │
         │   precedents    │         │   Confidence scores  │
         │   Enrich result │         │   Severity ratings   │
         └────────┬────────┘         └──────────┬───────────┘
                  │                             │
                  └─────────────┬───────────────┘
                                │
                                ▼
              ┌──────────────────────────────────────────┐
              │              FINAL VERDICT               │
              │  {                                       │
              │    "case_id": "RVN-2026-...",            │
              │    "fallacies": [...],                   │
              │    "logic_score": 0–100,                 │
              │    "overall_assessment": "...",          │
              │    "precedents": [...],                  │
              │    "processing_time_ms": ...            │
              │  }                                       │
              └──────────────────────────────────────────┘
                                │
                  ┌─────────────┴─────────────┐
                  ▼                           ▼
          ┌──────────────┐         ┌────────────────────┐
          │  Redis Cache │         │  Supabase Storage  │
          │  TTL: 1 hour │         │  (history, stats)  │
          └──────────────┘         └────────────────────┘
```

---

## ✨ Features

### 🧠 Core Features

| Feature | Description |
|---------|-------------|
| 📝 **Text Analysis** | Paste any argument, essay, debate excerpt, or political speech for immediate fallacy detection |
| 🌐 **URL Scraping** | Submit any article URL — FallacyChecker extracts clean text via readability-lxml and analyzes it |
| 🎥 **YouTube Analysis** | Enter a YouTube URL to extract audio, transcribe via Whisper, and analyze the full transcript with timestamp-linked fallacies |
| 🎙️ **Audio Upload** | Upload MP3/WAV/M4A recordings of speeches, podcasts, or debates for voice-to-verdict analysis |
| 📊 **Batch Processing** | Submit multiple texts via the batch API for bulk analysis — suitable for academic research workflows |
| 🔍 **25 Fallacy Categories** | Comprehensive detection: Ad Hominem, Straw Man, False Dilemma, Slippery Slope, Appeal to Authority, Hasty Generalization, Circular Reasoning, Red Herring, Bandwagon, and 16 more |
| 🌏 **Bilingual Support** | Native-quality analysis in both **English** and **Indonesian** — critical for the Revonalar user base |
| 📈 **Confidence Scoring** | Each detected fallacy ships with a 0.0–1.0 confidence score and CRITICAL / HIGH / MEDIUM / LOW severity rating |
| 🩹 **Fix Suggestions** | Actionable rewrite suggestions for each fallacious passage — not just a verdict but a path to better argument |

### ⚡ AMD-Specific Features

| Feature | Description |
|---------|-------------|
| 🔴 **ROCm 6.1 Native** | Full ROCm stack integration: vLLM compiled for CDNA3, `rocm-smi` metrics exposure, HIP device management |
| 🧮 **BF16 Full Precision** | 192 GB VRAM enables Llama-3-70B at full BF16 — no quantization, maximum reasoning quality |
| 📡 **GPU Metrics API** | `/health/gpu` endpoint exposes real-time VRAM usage, GPU utilization, and temperature via `rocm-smi` |
| 📋 **Benchmark Suite** | `scripts/benchmark.py` — full async performance benchmark with concurrent load testing, percentile stats, and GPU metric snapshots before/after |
| 🔧 **ROCm Docker Stack** | Production `docker-compose.yml` with `rocm/vllm-dev` base image, `/dev/kfd` + `/dev/dri` device mounts, and group-level GPU access (`video`, `render`) |

### 🔗 Revonalar Integration Features

| Feature | Description |
|---------|-------------|
| 👤 **User Accounts** | Shared Supabase auth with the Revonalar platform — single sign-on, no separate registration |
| 📚 **Analysis History** | Every verdict is stored with full metadata; users can review, share, and compare past analyses |
| 🏆 **Leaderboard** | Community leaderboard ranking the most-analyzed public statements by fallacy density and severity |
| 🔎 **RAG Precedents** | Qdrant vector DB retrieves similar historical fallacies — each verdict is contextualized with precedent |
| 🧩 **Chrome Extension** | Browser sidebar extension: select any text on any webpage and right-click → "Check for Fallacies" |

---

## 🛠 Tech Stack

| Category | Technology | Version | Why |
|----------|------------|---------|-----|
| **Frontend Framework** | SvelteKit | 5.x | Lightweight, fast SSR, excellent TypeScript support; already used by Revonalar |
| **Frontend Styling** | Tailwind CSS | 4.x | Utility-first rapid UI development |
| **Frontend Deploy** | Cloudflare Pages | — | Global CDN, zero-config deployment, Workers integration |
| **Backend Framework** | FastAPI | 0.111 | Async-first, automatic OpenAPI docs, Pydantic v2 validation |
| **Backend Server** | Uvicorn + Gunicorn | 0.30 | ASGI with multi-worker production deployment |
| **LLM Inference** | vLLM | 0.5.4 | OpenAI-compatible server, continuous batching, PagedAttention |
| **LLM Model** | Llama-3-70B | — | Best open-weight reasoning model; 70B parameters necessary for nuanced fallacy detection |
| **GPU Platform** | AMD MI300X + ROCm | 6.1 | 192 GB VRAM — only GPU class that runs Llama-3-70B at full BF16 without quantization |
| **Speech-to-Text** | faster-whisper large-v3 | 1.0.3 | State-of-the-art multilingual ASR; CTranslate2 backend for efficient inference |
| **Vector Database** | Qdrant | 1.10 | High-performance vector search for RAG precedent retrieval; self-hosted |
| **Database** | Supabase (PostgreSQL) | — | Shared instance with Revonalar; handles auth, history, leaderboard data |
| **Cache** | Redis | Alpine | In-memory result caching (TTL: 1 hour); reduces redundant LLM calls |
| **Task Queue** | Celery + Flower | 5.4 | Async batch processing and task monitoring dashboard |
| **Web Scraping** | httpx + BeautifulSoup4 + readability-lxml | — | Robust URL content extraction with main-content isolation |
| **YouTube Processing** | yt-dlp | 2024.8 | Download and extract audio from YouTube videos for transcription |
| **Monitoring** | Prometheus + Sentry | — | Metrics collection and error tracking in production |
| **Containerization** | Docker + Docker Compose | — | Full stack containerization with ROCm GPU device passthrough |
| **Reverse Proxy** | Nginx | Alpine | TLS termination and load balancing in front of the FastAPI app |
| **Auth** | Supabase Auth (JWT) | — | Shared with Revonalar; `python-jose` handles JWT verification in FastAPI |

---

## 🔴 Why AMD MI300X

### The VRAM Problem With Large Language Models

Running Llama-3-70B at full BF16 precision requires approximately **140 GB of VRAM** for model weights alone, plus additional memory for the KV cache during inference. This is a hard constraint that eliminates every GPU except the AMD MI300X from consideration for unquantized deployment:

```
┌─────────────────────────────────────────────────────────────────────────┐
│              GPU VRAM COMPARISON FOR LLAMA-3-70B BF16                   │
├──────────────────────────┬──────────┬───────────────┬───────────────────┤
│ GPU                      │   VRAM   │  Llama-3-70B  │  Context Budget   │
├──────────────────────────┼──────────┼───────────────┼───────────────────┤
│ AMD MI300X               │  192 GB  │  ✅ BF16 Full  │  ~52 GB remaining │
│ NVIDIA H100 SXM (2x)     │  2×80 GB │  ✅ BF16 Full  │  Tensor parallel  │
│ NVIDIA H100 SXM (1x)     │   80 GB  │  ❌ Doesn't fit│  —                │
│ NVIDIA A100 80GB (2x)    │  2×80 GB │  ✅ BF16 Full  │  Tensor parallel  │
│ AMD MI250X               │   128 GB │  ⚠️  GPTQ-4bit │  Quantized only   │
│ NVIDIA RTX 4090          │   24 GB  │  ❌ Doesn't fit│  —                │
│ AMD RX 7900 XTX          │   24 GB  │  ❌ Doesn't fit│  —                │
└──────────────────────────┴──────────┴───────────────┴───────────────────┘

  MI300X advantage: single-card full precision — no tensor parallelism overhead,
  no quantization quality loss, 52 GB free for generous KV cache / long contexts.
```

### Technical Advantages for This Workload

- **🧠 Single-Card Reasoning**: No tensor-parallel split means no inter-GPU communication overhead. The entire Llama-3-70B model fits on one MI300X, reducing latency for sequential reasoning tasks like fallacy chain-of-thought analysis.

- **📏 Long Context Windows**: 52 GB of free VRAM after loading the model supports generous KV cache allocation — enabling 8,192+ token context windows. This is critical for analyzing long-form articles, multi-speaker transcripts, and political speeches that can exceed 3,000 tokens.

- **⚡ Memory Bandwidth**: 5.3 TB/s HBM3 bandwidth — 2.4× the bandwidth of NVIDIA A100 80GB (2 TB/s) — translates directly to higher token-per-second throughput for memory-bandwidth-bound autoregressive generation.

- **🔧 ROCm Ecosystem Maturity**: ROCm 6.1 provides production-grade support for vLLM's PagedAttention kernel, HIP compilation of PyTorch kernels, and `rocm-smi` monitoring integration. The AMD Developer Cloud ships pre-built Docker images with all dependencies resolved.

- **💰 Cost Efficiency**: AMD MI300X on the AMD Developer Cloud provides access to 192 GB VRAM at competitive rates compared to multi-GPU NVIDIA H100 configurations required to match the memory capacity.

### Benchmark Targets

| Metric | Target | Hardware |
|--------|--------|----------|
| Short text (100 words) — P50 latency | < 2.0s | MI300X |
| Medium text (400 words) — P50 latency | < 5.0s | MI300X |
| Long article (1500 words) — P50 latency | < 12.0s | MI300X |
| Throughput at concurrency=10 | > 2.0 req/s | MI300X |
| VRAM headroom at 85% utilization | ~29 GB free | MI300X |

> *Run `python scripts/benchmark.py --help` for actual measured results against your MI300X endpoint.*

---

## 🚀 Quick Start

### Prerequisites

```
Node.js  >= 20.x
pnpm     >= 9.x
Python   >= 3.10
Docker   >= 24.x
Docker Compose >= 2.x

AMD Developer Cloud instance with MI300X (for inference)
OR: Any GPU/CPU with sufficient RAM for smaller model variants
```

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/fallacyx.git
cd fallacyx
```

### 2. Frontend Setup (SvelteKit)

```bash
# Install dependencies
pnpm install

# Copy environment template
cp .env.example .env
```

Edit `.env`:

```env
# Supabase (shared with Revonalar — Singapore region)
PUBLIC_SUPABASE_URL=https://bfhjknbboxhsxbwnmjov.supabase.co
PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here

# Backend API
PUBLIC_API_BASE_URL=http://localhost:8080

# (Optional) Chrome Extension ID for CORS
CHROME_EXTENSION_ID=your_extension_id
```

```bash
# Start development server
pnpm dev
# → http://localhost:5173
```

### 3. Backend Setup (FastAPI)

```bash
cd backend

# Copy backend environment
cp .env.example .env
```

Edit `backend/.env`:

```env
# vLLM endpoint (AMD Developer Cloud or local)
VLLM_BASE_URL=http://localhost:8000/v1
VLLM_MODEL_NAME=llama-3-70b

# Whisper ASR
WHISPER_BASE_URL=http://localhost:8001

# Vector DB
QDRANT_URL=http://localhost:6333

# Cache
REDIS_URL=redis://localhost:6379/0

# Database
SUPABASE_URL=https://bfhjknbboxhsxbwnmjov.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key

# Security
SECRET_KEY=your_jwt_secret_key_minimum_32_chars
```

### 4a. Running Locally (CPU / Small GPU)

For local development without an AMD MI300X, use a smaller model:

```bash
# Install Python dependencies
pip install --no-cache-dir -r requirements-dev.txt

# Start Qdrant and Redis via Docker
docker run -d -p 6333:6333 qdrant/qdrant
docker run -d -p 6379:6379 redis:alpine

# Start a smaller vLLM model (adjust to your VRAM)
pip install vllm
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Meta-Llama-3-8B-Instruct \
  --served-model-name llama-3-70b \
  --host 0.0.0.0 --port 8000

# Start the API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### 4b. Running on AMD Developer Cloud (MI300X)

```bash
cd backend

# Step 1: Install ROCm torch build
pip install --no-cache-dir \
  torch==2.4.0 \
  --index-url https://download.pytorch.org/whl/rocm6.1

# Step 2: Install vLLM with ROCm support
pip install --no-cache-dir vllm==0.5.4 \
  --extra-index-url https://download.pytorch.org/whl/rocm6.1

# Step 3: Install remaining dependencies
pip install -r requirements.txt

# Step 4: Download the model (requires Hugging Face access token)
huggingface-cli login
huggingface-cli download meta-llama/Meta-Llama-3-70B-Instruct \
  --local-dir ./models/llama-3-70b

# Step 5: Launch full stack
docker-compose up -d

# Monitor GPU
watch -n 2 rocm-smi
```

### 5. Run Benchmarks (Optional)

```bash
pip install httpx tqdm rich tabulate colorama

# Quick benchmark against your endpoint
python scripts/benchmark.py \
  --endpoint http://YOUR_AMD_CLOUD_IP:8080 \
  --runs 3 \
  --concurrent 5 \
  --export-csv
```

---

## 📖 API Documentation

The FastAPI backend auto-generates interactive OpenAPI docs at `/docs` (Swagger UI) and `/redoc`.

### Core Endpoints

#### `POST /api/v1/analyze` — Analyze Text

Detects logical fallacies in a text argument.

**Request:**
```json
{
  "text": "Vaccines cause autism. Anyone who supports vaccines is paid by Big Pharma. Real scientists would never question this proven fact.",
  "mode": "full",
  "language": "en",
  "timestamps": false
}
```

**Response:**
```json
{
  "case_id": "RVN-2026-060901",
  "status": "complete",
  "logic_score": 12,
  "verdict": "CRITICAL — Multiple severe fallacies detected",
  "fallacies": [
    {
      "id": "F001",
      "type": "ad_hominem",
      "type_label": "Ad Hominem",
      "excerpt": "Anyone who supports vaccines is paid by Big Pharma",
      "explanation": "This attacks the character and alleged financial motives of vaccine supporters rather than engaging with the scientific evidence for or against vaccine safety.",
      "confidence": 0.97,
      "severity": "high",
      "fix": "Address the evidence for or against vaccine-autism links directly, without speculating about the motives of those who accept the scientific consensus.",
      "timestamp_start": null,
      "timestamp_end": null,
      "precedents": [
        {
          "id": "PREC-0042",
          "summary": "Similar financial-motive ad hominem in 2024 climate debate",
          "similarity": 0.89
        }
      ]
    },
    {
      "id": "F002",
      "type": "appeal_to_authority",
      "type_label": "False Appeal to Authority",
      "excerpt": "Real scientists would never question this proven fact",
      "explanation": "Defines 'real scientists' as only those who agree with the claim — circular reasoning that makes the claim unfalsifiable.",
      "confidence": 0.91,
      "severity": "high",
      "fix": "Cite specific peer-reviewed studies. Allow that disagreement among scientists is itself evidence that warrants further examination.",
      "timestamp_start": null,
      "timestamp_end": null,
      "precedents": []
    }
  ],
  "overall_assessment": "This argument contains two high-severity fallacies. The core claim about vaccines is not supported — it relies entirely on discrediting opponents rather than presenting evidence. Logic Score: 12/100.",
  "processing_time_ms": 3241,
  "model": "llama-3-70b",
  "tokens_used": 847
}
```

---

#### `POST /api/v1/analyze/youtube` — Analyze YouTube Video

```json
{
  "url": "https://www.youtube.com/watch?v=EXAMPLE",
  "mode": "full",
  "language": "auto"
}
```

**Response** includes timestamp-linked fallacies:
```json
{
  "case_id": "RVN-2026-060902",
  "transcript_duration_s": 823,
  "fallacies": [
    {
      "type": "slippery_slope",
      "excerpt": "If we implement this policy, the entire economy will collapse",
      "timestamp_start": "00:03:42",
      "timestamp_end": "00:03:58",
      "confidence": 0.88
    }
  ]
}
```

---

#### `POST /api/v1/analyze/batch` — Batch Analysis

```json
{
  "items": [
    { "id": "item-1", "text": "First argument..." },
    { "id": "item-2", "text": "Second argument..." }
  ],
  "mode": "quick"
}
```

---

#### `GET /health` — System Health

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "vllm": { "status": "healthy", "model": "llama-3-70b", "latency_ms": 12 },
    "whisper": { "status": "healthy", "model": "large-v3" },
    "qdrant": { "status": "healthy", "collections": 1, "vectors": 12840 },
    "redis": { "status": "healthy", "hit_rate": 0.43 }
  },
  "gpu": {
    "name": "AMD Instinct MI300X",
    "vram_total_gb": 192.0,
    "vram_used_gb": 143.2,
    "vram_free_gb": 48.8,
    "gpu_util_pct": 67.4,
    "temp_celsius": 61.0
  }
}
```

---

## 🔗 Integration with Revonalar

FallacyChecker is architected as an embedded feature module within **Revonalar** — an Indonesian platform for critical thinking education. The integration is deep, not superficial:

```
┌─────────────────────────────────────────────────────────────────────┐
│                       REVONALAR ECOSYSTEM                           │
│                                                                     │
│  ┌─────────────────┐   ┌──────────────────┐   ┌─────────────────┐  │
│  │   Courses        │   │  FallacyChecker  │   │  Community      │  │
│  │   (Logic 101,    │──▶│  (This project)  │──▶│  Leaderboard    │  │
│  │    Rhetoric,     │   │                  │   │  Top Fallacies  │  │
│  │    Debate)       │   │  Real-time AI    │   │  Most Analyzed  │  │
│  └─────────────────┘   │  analysis engine │   │  Arguments      │  │
│                         └──────────────────┘   └─────────────────┘  │
│                                  │                                   │
│                    ┌─────────────┴───────────────┐                  │
│                    │  Shared Infrastructure       │                  │
│                    │  • Supabase (Auth + DB)      │                  │
│                    │  • Cloudflare Pages (CDN)    │                  │
│                    │  • Single user account       │                  │
│                    └─────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
```

**Shared Infrastructure**: FallacyChecker uses the same Supabase project (`bfhjknbboxhsxbwnmjov`, Singapore region) as the main Revonalar platform. Users log in once and access both the course content and the fallacy checker with a single account. Analysis history and leaderboard data are stored in Supabase tables alongside all other Revonalar data.

**Educational Context**: When a learner in a Revonalar logic course encounters a real-world argument, they can immediately submit it to FallacyChecker from within the course interface. The analysis results link back to relevant lesson content — each fallacy type detected links to the corresponding lesson explaining that fallacy in depth.

**Community Knowledge**: Every analysis enriches the shared Qdrant vector database. When the same or similar fallacies appear in new content, the RAG layer surfaces these precedents, creating a growing institutional memory of flawed public reasoning.

---

## 🗺 Roadmap

| Feature | Status | Target |
|---------|--------|--------|
| Core fallacy detection (text) | ✅ Complete | v1.0 |
| URL article scraping | ✅ Complete | v1.0 |
| YouTube video analysis | ✅ Complete | v1.0 |
| Audio file upload (ASR) | ✅ Complete | v1.0 |
| Batch analysis API | ✅ Complete | v1.0 |
| 25 fallacy categories + database | ✅ Complete | v1.0 |
| vLLM / ROCm Docker stack | ✅ Complete | v1.0 |
| Chrome browser extension | ✅ Complete | v1.0 |
| Supabase auth integration | ✅ Complete | v1.0 |
| Performance benchmark suite | ✅ Complete | v1.0 |
| Qdrant RAG precedent retrieval | 🚧 In Progress | v1.1 |
| Analysis history (user profile) | 🚧 In Progress | v1.1 |
| Community leaderboard | 🚧 In Progress | v1.1 |
| Whisper real-time streaming | 🚧 In Progress | v1.2 |
| Qwen-72B model variant | 📋 Planned | v1.2 |
| Multi-language expansion (Arabic, Spanish) | 📋 Planned | v1.3 |
| Debate scoring (two-speaker comparison) | 📋 Planned | v1.3 |
| Browser extension: live page highlighting | 📋 Planned | v2.0 |
| Revonalar course integration API | 📋 Planned | v2.0 |
| Public API with rate limiting | 📋 Planned | v2.0 |

> **Legend:** ✅ Complete &nbsp;|&nbsp; 🚧 In Progress &nbsp;|&nbsp; 📋 Planned

---

## 📄 License & Acknowledgments

This project is released under the **MIT License**. See [LICENSE](./LICENSE) for details.

### Acknowledgments

**🔴 AMD** — For providing access to the MI300X Developer Cloud, the ROCm open-source GPU compute stack, and the AMD Developer Hackathon ACT II platform. The MI300X's 192 GB HBM3 unified memory architecture makes unquantized 70B inference a reality for open-source developers.

**🤗 Hugging Face & Meta AI** — For releasing Llama-3-70B under the Meta Llama 3 Community License, democratizing access to frontier-class language model reasoning.

**🌐 lablab.ai** — For creating the AMD Developer Hackathon ACT II, fostering open-source AI development and connecting developers with cutting-edge hardware.

**⚡ vLLM Team** — For the PagedAttention architecture and continuous batching that makes efficient 70B inference accessible.

**🔵 Supabase** — For the open-source Firebase alternative powering the persistence layer shared with Revonalar.

**⬛ Qdrant** — For the high-performance vector search engine enabling the RAG precedent retrieval system.

---

<div align="center">

**Built with ❤️ for the AMD Developer Hackathon ACT II**

*FallacyChecker · Part of the Revonalar Platform · MIT License*

<br/>

[![AMD Developer Hackathon](https://img.shields.io/badge/AMD%20Developer%20Hackathon-ACT%20II-ED1C24?style=flat-square&logo=amd&logoColor=white)](https://lablab.ai)
[![lablab.ai](https://img.shields.io/badge/lablab.ai-Hackathon-6C47FF?style=flat-square)](https://lablab.ai)
[![SvelteKit](https://img.shields.io/badge/SvelteKit-5.x-FF3E00?style=flat-square&logo=svelte&logoColor=white)](https://kit.svelte.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)

</div>
