# 🤖 Hari 1 — 10 Juni 2026 | Prompting Guide
## Tema: Orientasi & AMD Cloud Aktif

> **Cara pakai:** Copy setiap prompt ke Claude baru (tab terpisah) atau jalankan via Cursor/VS Code.
> Kerjakan secara paralel — tidak perlu tunggu satu selesai untuk mulai yang lain.
> Simpan semua output ke folder proyek sebelum tutup tab.

---

## Konteks Proyek (Paste di awal setiap sesi Claude baru jika perlu)

```
Proyek: FallacyChecker — fitur baru di platform Revonalar
Stack: SvelteKit + Tailwind CSS + Supabase (frontend), FastAPI + Python (backend), 
       vLLM + Llama-3-70B di AMD MI300X (inference), Qdrant (vector DB)
Deploy: Cloudflare Pages (frontend), AMD Developer Cloud (backend)
Tujuan: Real-time logical fallacy detector untuk teks, URL artikel, YouTube, dan audio
```

---

## TUGAS 1
### Generate struktur folder proyek FallacyChecker lengkap (SvelteKit + API)

**Simpan ke:** `project-structure.md` di root proyek

```
Buatkan struktur folder lengkap untuk proyek FallacyChecker dengan dua bagian utama:

1. FRONTEND: SvelteKit app (akan diintegrasikan ke Revonalar yang sudah ada)
2. BACKEND: FastAPI Python server untuk inference AMD

Requirement frontend (SvelteKit):
- Route /fallacy (halaman utama input)
- Route /fallacy/result/[id] (halaman hasil analisis)
- Route /fallacy/history (riwayat analisis user)
- Route /fallacy/leaderboard (ranking komunitas)
- Folder lib/components/fallacy/ untuk semua komponen
- Folder lib/api/ untuk fungsi fetch ke backend
- Folder lib/types/ untuk TypeScript types
- Folder lib/stores/ untuk Svelte stores

Requirement backend (FastAPI):
- app/main.py (entry point)
- app/routers/ (text, youtube, url, audio, batch, rag)
- app/services/ (vllm_service, whisper_service, qdrant_service, youtube_service)
- app/models/ (pydantic schemas)
- app/core/ (config, security, logging)
- app/utils/ (helpers)
- tests/ (unit dan integration tests)
- docker/ (Dockerfile, docker-compose)
- scripts/ (setup, benchmark, seed)

Tampilkan sebagai tree struktur folder lengkap dengan komentar singkat 
fungsi tiap file/folder penting. Format yang bisa langsung di-copy ke terminal 
sebagai mkdir commands juga.
```

---

## TUGAS 2
### Generate docker-compose.yml untuk vLLM + Qdrant + FastAPI

**Simpan ke:** `docker-compose.yml` di root backend

```
Buatkan docker-compose.yml lengkap untuk stack berikut yang akan dijalankan 
di AMD Developer Cloud (GPU AMD MI300X, ROCm):

Services yang dibutuhkan:
1. vllm — inference server untuk Llama-3-70B atau Qwen-72B
   - Image: vllm/vllm-openai dengan ROCm support
   - GPU: AMD MI300X
   - Port: 8000
   - Model: /models/llama-3-70b (mount dari volume)
   - Environment: tensor_parallel_size=1, max_model_len=8192
   
2. whisper — speech-to-text untuk audio/video
   - Image: python dengan faster-whisper
   - GPU: AMD (shared dengan vllm jika memungkinkan)
   - Port: 8001
   - Model: large-v3
   
3. qdrant — vector database untuk RAG
   - Image: qdrant/qdrant
   - Port: 6333, 6334
   - Volume: ./qdrant_storage:/qdrant/storage
   
4. api — FastAPI backend utama
   - Build dari Dockerfile lokal
   - Port: 8080
   - Depends on: vllm, whisper, qdrant
   - Environment: semua URL service di atas
   
5. redis — caching hasil analisis
   - Image: redis:alpine
   - Port: 6379

6. nginx — reverse proxy
   - Port: 80, 443
   - Proxy ke api:8080

Tambahkan:
- Networks yang tepat antar service
- Volume declarations
- Health checks untuk semua service
- Restart policy: unless-stopped
- Resource limits yang masuk akal untuk MI300X
- Comments penjelasan tiap section

Berikan juga perintah untuk menjalankan: docker-compose up -d
```

---

## TUGAS 3
### Generate requirements.txt semua dependency Python backend

**Simpan ke:** `requirements.txt` di folder backend

```
Buatkan requirements.txt lengkap untuk FastAPI backend FallacyChecker dengan 
semua dependency yang dibutuhkan. Kelompokkan dengan komentar kategori:

Kategori yang dibutuhkan:
1. Web Framework: FastAPI, uvicorn, gunicorn
2. AMD/ROCm AI: vllm (ROCm build), torch (ROCm), transformers, accelerate
3. Speech-to-Text: faster-whisper, ffmpeg-python
4. YouTube Processing: yt-dlp, pytube
5. Web Scraping: httpx, beautifulsoup4, jina (atau requests-html)
6. Vector DB: qdrant-client
7. Database: supabase, asyncpg, sqlalchemy
8. Caching: redis, aioredis
9. Queue: celery, flower (monitoring)
10. Utilities: pydantic, python-dotenv, python-jose (JWT), passlib
11. Monitoring: prometheus-client, sentry-sdk
12. Testing: pytest, pytest-asyncio, httpx (test client)
13. Dev tools: black, ruff, mypy

Sertakan versi yang spesifik dan stabil (bukan latest).
Tambahkan juga requirements-dev.txt untuk dependencies development only.
Berikan catatan khusus untuk dependency yang memerlukan build khusus untuk ROCm.
```

---

## TUGAS 4
### Generate script health-check endpoint FastAPI (GET /health)

**Simpan ke:** `app/routers/health.py`

```
Buatkan FastAPI router untuk health check endpoint yang komprehensif.

File: app/routers/health.py

Endpoint yang dibutuhkan:

1. GET /health
   - Response cepat (< 100ms)
   - Return: {"status": "ok", "timestamp": "...", "version": "1.0.0"}

2. GET /health/detailed  
   - Cek semua dependency:
     a. vLLM service: ping ke http://vllm:8000/health
     b. Whisper service: ping ke http://whisper:8001/health
     c. Qdrant: ping ke qdrant_client.get_collections()
     d. Redis: ping ke redis.ping()
     e. Supabase: simple query ke database
   - Return status tiap komponen: "healthy" / "degraded" / "down"
   - Return response time tiap komponen dalam ms
   - Overall status: "healthy" jika semua ok, "degraded" jika ada yang down tapi masih bisa jalan, "critical" jika vLLM atau Supabase down

3. GET /health/gpu
   - Return informasi GPU AMD yang sedang dipakai
   - VRAM total, VRAM used, VRAM free
   - GPU utilization %
   - Temperature (jika accessible)
   - Model yang sedang loaded

Response format semua endpoint harus JSON yang bisa diparsing Prometheus.
Tambahkan proper error handling dan timeout (max 5 detik per check).
Gunakan asyncio untuk concurrent checks.
Sertakan Pydantic models untuk semua response.
```

---

## TUGAS 5
### Generate schema database Supabase: tabel fallacy_analyses dan fallacy_vectors

**Simpan ke:** `supabase/migrations/001_fallacy_tables.sql`

```
Buatkan SQL migration untuk Supabase PostgreSQL dengan tabel berikut:

1. Tabel: fallacy_analyses
   Kolom:
   - id: uuid primary key default gen_random_uuid()
   - user_id: uuid references auth.users(id) on delete cascade
   - input_type: enum ('text', 'url', 'youtube', 'audio') not null
   - input_content: text (teks asli atau URL)
   - input_title: text nullable (judul artikel/video)
   - transcript: text nullable (untuk audio/video)
   - fallacies_found: jsonb not null default '[]'
     Format: [{"type": "ad_hominem", "text": "...", "explanation": "...", 
               "confidence": 0.95, "timestamp_start": 120, "timestamp_end": 145}]
   - total_fallacies: integer default 0
   - analysis_duration_ms: integer (waktu proses)
   - model_used: text (nama model LLM)
   - is_public: boolean default false
   - metadata: jsonb default '{}'
   - created_at: timestamptz default now()
   - updated_at: timestamptz default now()

2. Tabel: fallacy_vectors
   Kolom:
   - id: uuid primary key default gen_random_uuid()
   - analysis_id: uuid references fallacy_analyses(id) on delete cascade
   - fallacy_type: text not null
   - fallacy_text: text not null (teks yang mengandung fallacy)
   - embedding_id: text (ID di Qdrant)
   - created_at: timestamptz default now()

3. Tabel: fallacy_feedback
   Kolom:
   - id: uuid primary key default gen_random_uuid()
   - analysis_id: uuid references fallacy_analyses(id)
   - user_id: uuid references auth.users(id)
   - fallacy_index: integer (index di array fallacies_found)
   - is_correct: boolean (user setuju deteksi tepat?)
   - comment: text nullable
   - created_at: timestamptz default now()
   - unique: (analysis_id, user_id, fallacy_index)

Tambahkan:
- Indexes yang tepat untuk query performance
- Trigger untuk auto-update updated_at
- RLS policies: user hanya bisa baca/tulis data sendiri, kecuali is_public = true
- Function untuk increment total_fallacies otomatis
- View: public_analyses (hanya baris dengan is_public = true)
```

---

## TUGAS 6
### Generate tabel user_fallacy_history dengan RLS policy

**Simpan ke:** `supabase/migrations/002_user_history.sql`

```
Buatkan SQL migration untuk Supabase dengan fokus pada user history dan 
gamifikasi FallacyChecker yang terintegrasi dengan sistem Diamond Revonalar.

Tabel yang dibutuhkan:

1. user_fallacy_stats
   - user_id: uuid references auth.users(id) primary key
   - total_analyses: integer default 0
   - total_fallacies_found: integer default 0
   - streak_current: integer default 0 (hari berturut-turut analisis)
   - streak_max: integer default 0
   - last_analysis_date: date nullable
   - fallacy_type_counts: jsonb default '{}'
     Format: {"ad_hominem": 5, "strawman": 3, ...}
   - accuracy_score: numeric(5,2) default 0.00 (% feedback benar dari komunitas)
   - level: integer default 1
   - xp_points: integer default 0
   - updated_at: timestamptz default now()

2. fallacy_achievements
   - id: uuid primary key default gen_random_uuid()
   - user_id: uuid references auth.users(id)
   - achievement_code: text not null
     Contoh: 'first_analysis', 'streak_7', 'found_100_fallacies', 
              'first_ad_hominem', 'accuracy_90', dll
   - unlocked_at: timestamptz default now()
   - diamond_reward: integer default 0
   - unique: (user_id, achievement_code)

3. daily_fallacy_challenges
   - id: uuid primary key default gen_random_uuid()
   - challenge_date: date not null unique
   - content_url: text not null
   - content_type: text not null
   - expected_fallacy_types: text[] 
   - diamond_reward: integer default 10
   - created_at: timestamptz default now()

4. daily_challenge_submissions
   - id: uuid primary key default gen_random_uuid()
   - user_id: uuid references auth.users(id)
   - challenge_id: uuid references daily_fallacy_challenges(id)
   - analysis_id: uuid references fallacy_analyses(id)
   - completed_at: timestamptz default now()
   - unique: (user_id, challenge_id)

RLS Policies yang dibutuhkan:
- user_fallacy_stats: baca semua (untuk leaderboard), tulis hanya milik sendiri
- fallacy_achievements: baca semua, tulis hanya via service role
- daily_fallacy_challenges: baca semua (public)
- daily_challenge_submissions: baca milik sendiri, tulis milik sendiri

Functions yang dibutuhkan:
- update_streak(p_user_id uuid): update streak berdasarkan last_analysis_date
- check_and_award_achievements(p_user_id uuid): cek dan berikan achievement baru
- get_leaderboard(p_limit int): ambil top users dengan stats lengkap

Tambahkan trigger: setiap INSERT ke fallacy_analyses → jalankan update_streak 
dan check_and_award_achievements untuk user tersebut.
```

---

## TUGAS 7
### Generate SvelteKit route struktur: /fallacy, /fallacy/result/[id]

**Simpan ke:** folder `src/routes/(student)/fallacy/`

```
Buatkan struktur file lengkap untuk SvelteKit routes FallacyChecker.
Proyek ini menggunakan SvelteKit dengan route groups, Supabase untuk auth/data,
dan Tailwind CSS untuk styling.

File yang dibutuhkan:

1. src/routes/(student)/fallacy/+page.svelte
   - Halaman utama FallacyChecker
   - Tab navigation: Teks | URL Artikel | YouTube | Audio
   - Import dan gunakan komponen FallacyInput
   - Handle form submit → redirect ke /fallacy/result/[id]
   - Tampilkan history 5 analisis terakhir user
   - Tampilkan Daily Challenge jika ada

2. src/routes/(student)/fallacy/+page.server.ts
   - Load: ambil history terbaru user dari Supabase
   - Load: ambil daily challenge hari ini
   - Load: ambil user stats (streak, total analyses)
   - Actions: handle submit analisis baru → call backend AMD API
   - Error handling yang proper

3. src/routes/(student)/fallacy/result/[id]/+page.svelte
   - Halaman hasil analisis lengkap
   - Tampilkan semua fallacy yang ditemukan
   - Visualisasi: chart breakdown per type
   - Timeline jika konten video (timestamp per fallacy)
   - Section "Pelajari Lebih Lanjut" → link ke lesson Revonalar
   - Share button
   - Feedback buttons per fallacy (benar/salah)

4. src/routes/(student)/fallacy/result/[id]/+page.server.ts
   - Load: ambil data analisis berdasarkan ID
   - Validasi: user hanya bisa lihat analisis sendiri (kecuali public)
   - Actions: handle feedback dari user

5. src/routes/(student)/fallacy/history/+page.svelte
   - List semua analisis user dengan pagination
   - Filter by type, date range, fallacy type
   - Search

6. src/routes/(student)/fallacy/history/+page.server.ts
   - Load dengan pagination dan filter

7. src/routes/(student)/fallacy/leaderboard/+page.svelte
   - Top 20 user bulan ini
   - Tampilkan nama, avatar, total analisis, fallacy ditemukan

8. src/routes/(student)/fallacy/leaderboard/+page.server.ts
   - Load leaderboard data

Untuk setiap file:
- Berikan kode lengkap yang bisa langsung dipakai
- Gunakan TypeScript
- Gunakan Tailwind CSS untuk styling (minimal, clean)
- Ikuti pattern yang sudah ada di Revonalar (SvelteKit + Supabase pattern)
- Tambahkan loading states dan error handling
```

---

## TUGAS 8
### Generate komponen FallacyInput.svelte

**Simpan ke:** `src/lib/components/fallacy/FallacyInput.svelte`

```
Buatkan komponen Svelte lengkap untuk input FallacyChecker.

Nama file: FallacyInput.svelte
Lokasi: src/lib/components/fallacy/FallacyInput.svelte

Spesifikasi komponen:
- Props: onSubmit (callback function), isLoading (boolean), defaultTab (string)
- 4 tab: "Teks", "URL Artikel", "YouTube", "Audio"
- State management dengan Svelte stores atau reactive vars

TAB 1 — TEKS:
- Textarea besar (min 200px height, auto-resize)
- Placeholder: "Paste teks artikel, caption, speech, atau konten apapun di sini..."
- Character counter (max 10.000 karakter)
- Tombol "Analisis Teks"
- Contoh cepat: 3 tombol quick-fill dengan contoh teks berisi fallacy

TAB 2 — URL ARTIKEL:
- Input text untuk URL
- Validasi URL format (http/https)
- Preview: setelah URL diketik, fetch title artikel (debounced 500ms)
- Tampilkan title + favicon website sebagai preview
- Tombol "Analisis Artikel"

TAB 3 — YOUTUBE:
- Input text untuk YouTube URL
- Support format: youtube.com/watch?v=, youtu.be/, youtube.com/shorts/
- Validasi format YouTube URL
- Preview: embed thumbnail + judul video (fetch via noembed.com API)
- Timestamp range: opsional, analisis dari menit X sampai menit Y
- Tombol "Analisis Video"

TAB 4 — AUDIO:
- Drag & drop area ATAU file browser
- Format yang diterima: MP3, MP4, WAV, M4A, OGG (max 50MB)
- Progress bar saat upload
- Preview: nama file + durasi (jika bisa dibaca)
- Tombol "Analisis Audio"

UI Requirements:
- Tailwind CSS, clean dan modern
- Tab active state yang jelas
- Loading state: tombol disabled + spinner saat isLoading = true
- Error messages yang jelas per field
- Responsive untuk mobile
- Animasi smooth saat ganti tab (Svelte transition)
- TypeScript types untuk semua props dan events

Gunakan dispatch untuk emit events ke parent component.
```

---

## TUGAS 9
### Generate FallacyResult.svelte skeleton

**Simpan ke:** `src/lib/components/fallacy/FallacyResult.svelte`

```
Buatkan komponen Svelte untuk menampilkan hasil analisis fallacy.

Nama file: FallacyResult.svelte
Lokasi: src/lib/components/fallacy/FallacyResult.svelte

Data yang diterima via props:
- analysis: object dengan struktur:
  {
    id: string,
    input_type: 'text' | 'url' | 'youtube' | 'audio',
    input_title: string | null,
    fallacies_found: Array<{
      type: string,           // nama fallacy: "ad_hominem", "strawman", dll
      type_label: string,     // label Indonesia: "Ad Hominem", "Jerami Palsu"
      text: string,           // kalimat yang mengandung fallacy
      explanation: string,    // penjelasan mengapa ini fallacy
      confidence: number,     // 0.0 - 1.0
      timestamp_start: number | null,  // detik (untuk video)
      timestamp_end: number | null
    }>,
    total_fallacies: number,
    analysis_duration_ms: number,
    transcript: string | null,
    created_at: string
  }
- isOwner: boolean (apakah user yang lihat adalah pemilik analisis)
- youtubeVideoId: string | null (untuk embed YouTube player)

Sections yang harus ada:

1. HEADER SUMMARY
   - Judul konten yang dianalisis
   - Badge: jenis input (Teks/URL/YouTube/Audio)
   - Statistik: X fallacy ditemukan, waktu analisis Y detik

2. JIKA TIDAK ADA FALLACY
   - Illustration + pesan positif: "Tidak ditemukan logical fallacy!"
   - Catatan: "Bukan berarti konten ini sepenuhnya benar, tapi argumennya valid"

3. JIKA ADA FALLACY — SUMMARY CHART
   - Simple bar chart atau pill badges per tipe fallacy
   - Contoh: Ad Hominem (3) | Strawman (1) | False Dilemma (2)
   - Warna berbeda per tipe

4. LIST FALLACY (tiap item):
   - Badge nama fallacy (warna sesuai severity)
   - Confidence score (high/medium/low)
   - Quote teks yang bermasalah (di-highlight)
   - Penjelasan mengapa ini fallacy
   - Timestamp link jika video (klik → jump ke momen itu)
   - Feedback buttons: 👍 Tepat | 👎 Tidak Tepat (jika isOwner)

5. TRANSCRIPT SECTION (jika ada)
   - Collapsible
   - Highlight bagian yang mengandung fallacy

6. ACTION BUTTONS
   - Share hasil
   - Download PDF
   - Analisis ulang

Gunakan TypeScript, Tailwind CSS, clean design.
Berikan kode lengkap yang bisa langsung dipakai.
```

---

## TUGAS 10
### Generate system prompt untuk deteksi fallacy (JSON output)

**Simpan ke:** `backend/app/prompts/fallacy_detection.py`

```
Buatkan system prompt dan prompt templates yang optimal untuk deteksi 
logical fallacy menggunakan LLM (Llama-3-70B atau Qwen-72B).

File: app/prompts/fallacy_detection.py

Yang dibutuhkan:

1. SYSTEM_PROMPT — instruksi dasar untuk model
   - Definisikan peran: "Kamu adalah ahli logika dan critical thinking..."
   - Instruksi output: SELALU return valid JSON, tidak ada teks di luar JSON
   - Instruksi jika tidak ada fallacy: return array kosong, bukan null
   - Instruksi confidence: hanya flag sebagai fallacy jika confidence >= 0.7
   - Instruksi bahasa: analisis konten Bahasa Indonesia DAN Inggris
   - Instruksi tone: edukatif, tidak judgmental

2. DETECTION_PROMPT_TEMPLATE — template untuk analisis teks
   - Input: {text} yang akan dianalisis
   - Output format JSON yang strict:
     {
       "fallacies": [
         {
           "type": "snake_case_fallacy_name",
           "type_label": "Nama Fallacy",
           "text": "kalimat persis yang mengandung fallacy",
           "explanation": "penjelasan singkat 2-3 kalimat mengapa ini fallacy",
           "confidence": 0.95,
           "severity": "high|medium|low",
           "timestamp_start": null,
           "timestamp_end": null
         }
       ],
       "overall_assessment": "1-2 kalimat penilaian keseluruhan",
       "logic_score": 75
     }

3. VIDEO_PROMPT_TEMPLATE — untuk transkrip dengan timestamp
   - Input: {transcript_with_timestamps} format [00:01:23] teks kalimat
   - Output: sama dengan di atas tapi timestamp_start dan timestamp_end diisi (dalam detik)

4. FEW_SHOT_EXAMPLES — 3 contoh pasangan input-output untuk few-shot prompting
   - Contoh 1: teks pendek dengan Ad Hominem
   - Contoh 2: teks dengan Strawman + False Dilemma
   - Contoh 3: teks yang TIDAK mengandung fallacy (output array kosong)

5. EDUCATIONAL_PROMPT_TEMPLATE — versi yang lebih panjang dan edukatif
   - Untuk mode "belajar": penjelasan lebih detail per fallacy
   - Sertakan contoh lain yang serupa
   - Sertakan cara menghindari fallacy tersebut

6. Function: build_prompt(text, mode='quick', language='id', timestamps=None)
   - Return prompt string yang siap dikirim ke model

Pastikan prompt dirancang agar:
- Model TIDAK asal-asalan mendeteksi fallacy
- False positive diminimalkan
- Penjelasan mudah dipahami orang awam
- Output JSON selalu valid (tidak pernah malformed)
```

---

## TUGAS 11
### Generate daftar 25 jenis logical fallacy dalam Bahasa Indonesia

**Simpan ke:** `src/lib/data/fallacies.ts` DAN `backend/app/data/fallacies.json`

```
Buatkan database lengkap 25 jenis logical fallacy yang paling umum, 
dalam format yang bisa dipakai oleh frontend (TypeScript) dan backend (JSON).

Untuk setiap fallacy sertakan:
- code: string snake_case (contoh: "ad_hominem")
- name_en: nama dalam Bahasa Inggris
- name_id: nama dalam Bahasa Indonesia (terjemahan atau transliterasi)
- short_description: 1 kalimat deskripsi singkat (Bahasa Indonesia)
- full_description: 2-3 paragraf penjelasan lengkap (Bahasa Indonesia)
- example_id: 1-2 contoh dalam konteks Indonesia (politik, sosmed, berita)
- how_to_counter: cara merespons jika seseorang menggunakan fallacy ini
- severity: "high" | "medium" | "low" (seberapa merusak argumen)
- category: "relevance" | "presumption" | "ambiguity" | "emotional" | "causal"
- color_hex: warna representasi untuk UI (pilih warna yang distinct)
- icon_emoji: emoji yang merepresentasikan

25 fallacy yang harus dicover:
1. Ad Hominem
2. Strawman (Jerami Palsu)  
3. False Dilemma (Dilema Palsu)
4. Slippery Slope (Lereng Licin)
5. Appeal to Authority (Argumen Otoritas)
6. Appeal to Emotion (Argumen Emosi)
7. Bandwagon / Ad Populum (Ikut-ikutan)
8. Circular Reasoning (Penalaran Melingkar)
9. Hasty Generalization (Generalisasi Terburu-buru)
10. Post Hoc (Setelah Ini Berarti Karena Ini)
11. Red Herring (Pengalih Perhatian)
12. False Equivalence (Kesetaraan Palsu)
13. Appeal to Ignorance
14. Tu Quoque (Kamupun Juga)
15. Burden of Proof (Beban Pembuktian)
16. Black-or-White Thinking
17. Appeal to Nature
18. Anecdotal Evidence
19. Texas Sharpshooter
20. No True Scotsman
21. Genetic Fallacy
22. Begging the Question
23. Loaded Question
24. Appeal to Tradition
25. Sunk Cost Fallacy

Format output:
1. TypeScript: export const FALLACIES: Fallacy[] = [...] dengan interface Fallacy
2. JSON: array yang sama untuk backend Python
3. Tambahkan juga helper functions di TypeScript:
   - getFallacyByCode(code: string): Fallacy | undefined
   - getFallaciesByCategory(category: string): Fallacy[]
   - getFallacyColor(code: string): string
```

---

## TUGAS 12
### Generate script benchmark latency endpoint AMD vs dummy

**Simpan ke:** `scripts/benchmark.py`

```
Buatkan script Python lengkap untuk benchmark performa FallacyChecker backend.

File: scripts/benchmark.py

Script ini akan membandingkan:
A. AMD MI300X dengan model 70B (endpoint utama)
B. Dummy endpoint (return hardcoded response, untuk baseline)
C. Opsional: model 7B sebagai perbandingan

Fungsi yang dibutuhkan:

1. benchmark_single_request(endpoint_url, payload, label)
   - Kirim 1 request, ukur latency
   - Return: {"label": ..., "latency_ms": ..., "status": ..., "tokens_per_sec": ...}

2. benchmark_concurrent(endpoint_url, payload, n_concurrent, label)
   - Kirim N request bersamaan (asyncio)
   - Ukur: avg latency, p50, p95, p99, max, min
   - Ukur: total throughput (requests/second)

3. benchmark_suite()
   - Test dengan berbagai panjang input: 100 token, 500 token, 2000 token, 8000 token
   - Test dengan 1, 5, 10, 20, 50 concurrent requests
   - Jalankan setiap test 3x, ambil median

4. generate_report(results)
   - Print tabel perbandingan yang rapi ke terminal
   - Simpan ke benchmark_results.json dan benchmark_results.md
   - Tabel format:
     | Test Case | AMD 70B (ms) | Dummy (ms) | Speedup |
     |-----------|-------------|------------|---------|

5. Test payloads yang digunakan:
   - SHORT: teks 100 kata tanpa fallacy
   - MEDIUM: teks 500 kata dengan 2-3 fallacy  
   - LONG: teks 2000 kata (artikel panjang)
   - TRANSCRIPT: transkrip video 10 menit (±1500 kata dengan timestamps)

Tambahkan:
- Argument parser: --endpoint, --model, --runs, --concurrent
- Progress bar dengan tqdm
- Colored output (green = good, red = slow)
- Export ke CSV untuk Excel
- GPU metrics collection jika running di AMD cloud (via rocm-smi)

Jalankan: python scripts/benchmark.py --endpoint http://localhost:8080 --runs 5
```

---

## TUGAS 13
### Generate README.md proyek dengan arsitektur diagram ASCII

**Simpan ke:** `README.md` di root proyek GitHub

```
Buatkan README.md profesional dan lengkap untuk proyek FallacyChecker 
yang akan disubmit ke AMD Developer Hackathon ACT II di lablab.ai.

README ini akan dilihat oleh juri hackathon, jadi harus impressive.

Sections yang dibutuhkan:

1. HEADER
   - Badge: AMD Developer Hackathon ACT II, MIT License, SvelteKit, FastAPI
   - Tagline yang kuat (1 baris)
   - GIF atau screenshot hero (placeholder untuk sekarang)

2. OVERVIEW (3-4 paragraf)
   - Apa masalah yang diselesaikan
   - Bagaimana FallacyChecker menyelesaikannya
   - Koneksi ke platform Revonalar
   - Mengapa AMD MI300X adalah pilihan yang tepat

3. ARSITEKTUR DIAGRAM (ASCII art)
   Buat diagram ASCII yang menunjukkan:
   
   User Browser/Extension
          |
          v
   [Revonalar SvelteKit Frontend]
          |
          v  REST API
   [FastAPI Backend]
      |        |        |
      v        v        v
   [vLLM   [Whisper] [Qdrant]
   Llama-70B]  ASR    Vector DB
      |
      v
   [AMD MI300X GPU - 192GB VRAM]
   
   Buat diagram ini lebih detail dan informatif dengan ASCII art.
   Tambahkan juga flow diagram untuk pipeline analisis.

4. FEATURES
   - List semua fitur dengan emoji
   - Kelompokkan: Core Features, AMD Features, Revonalar Integration

5. TECH STACK TABLE
   | Category | Technology | Why |
   |----------|-----------|-----|

6. WHY AMD MI300X section
   - Poin-poin teknis yang kuat
   - Perbandingan VRAM dengan GPU lain
   - Benchmark numbers (placeholder)

7. QUICK START
   - Prerequisites
   - Installation (step by step)
   - Configuration (.env setup)
   - Running locally vs AMD cloud

8. API DOCUMENTATION PREVIEW
   - Endpoint utama dengan contoh request/response

9. INTEGRATION WITH REVONALAR
   - Penjelasan ekosistem

10. ROADMAP
    - Table dengan status emoji ✅ 🚧 📋

11. LICENSE + ACKNOWLEDGMENTS
    - AMD, lablab.ai, Hugging Face

Tulis dalam Bahasa Inggris. Tone: profesional, technical, confident.
```

---

## TUGAS 14
### Generate .env.example

**Simpan ke:** `.env.example` di root proyek

```
Buatkan file .env.example lengkap untuk proyek FallacyChecker (frontend + backend).

Bagi menjadi dua file:

FILE 1: .env.example (untuk SvelteKit frontend)
Kelompokkan dengan komentar:

# ==========================================
# SUPABASE
# ==========================================
PUBLIC_SUPABASE_URL=
PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# ==========================================
# BACKEND API (AMD Developer Cloud)
# ==========================================
PRIVATE_API_URL=
PRIVATE_API_KEY=
PUBLIC_API_URL_CLIENT=

# ==========================================
# CLOUDFLARE
# ==========================================
CF_ACCOUNT_ID=
CF_API_TOKEN=

# ==========================================
# APP CONFIG
# ==========================================
PUBLIC_APP_URL=
PUBLIC_APP_NAME=FallacyChecker

FILE 2: backend/.env.example (untuk FastAPI backend)
Kelompokkan:

# ==========================================
# APP
# ==========================================
APP_ENV=development
APP_VERSION=1.0.0
SECRET_KEY=
API_KEY=

# ==========================================
# AMD / vLLM
# ==========================================
VLLM_HOST=
VLLM_PORT=8000
VLLM_MODEL_NAME=
VLLM_MAX_TOKENS=2048
VLLM_TEMPERATURE=0.1

# ==========================================
# WHISPER
# ==========================================
WHISPER_HOST=
WHISPER_PORT=8001
WHISPER_MODEL=large-v3

# ==========================================
# QDRANT
# ==========================================
QDRANT_HOST=
QDRANT_PORT=6333
QDRANT_API_KEY=
QDRANT_COLLECTION_NAME=fallacy_vectors

# ==========================================
# SUPABASE
# ==========================================
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=

# ==========================================
# REDIS
# ==========================================
REDIS_URL=

# ==========================================
# EXTERNAL SERVICES
# ==========================================
YOUTUBE_API_KEY=
JINA_API_KEY=
SENTRY_DSN=

# ==========================================
# RATE LIMITING
# ==========================================
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_DAILY_FREE=5
RATE_LIMIT_DAILY_PREMIUM=100

Untuk setiap variable, tambahkan:
- Komentar singkat menjelaskan fungsinya
- Contoh nilai atau format yang expected
- Tanda apakah ini WAJIB atau OPSIONAL
- Cara mendapatkan nilai ini (link atau instruksi singkat)
```

---

## TUGAS 15
### Generate Cloudflare Pages _redirects dan config deployment

**Simpan ke:** `static/_redirects` dan `cloudflare.json`

```
Buatkan konfigurasi deployment Cloudflare Pages untuk SvelteKit app FallacyChecker.

File 1: static/_redirects
Berikan redirect rules yang diperlukan:
- /api/* → https://api.fallacychecker.revonalar.com/:splat (proxy ke AMD backend)
- /fallacy/r/:id → /fallacy/result/:id (URL shortener friendly)
- Redirect non-www ke www atau sebaliknya
- Redirect HTTP ke HTTPS

File 2: wrangler.toml (Cloudflare config)
- name: fallacychecker
- Compatibility date terbaru
- Build command untuk SvelteKit
- Output directory
- Environment variables yang perlu di-set di Cloudflare

File 3: .github/workflows/deploy.yml
GitHub Actions workflow untuk:
- Trigger: push ke branch main
- Steps:
  1. Checkout
  2. Setup Node.js 20
  3. npm install
  4. npm run build
  5. Deploy ke Cloudflare Pages via wrangler action
- Environment secrets yang dibutuhkan

File 4: svelte.config.js update
- Tambahkan adapter-cloudflare
- Config yang tepat untuk Cloudflare Pages

File 5: package.json scripts update
Tambahkan scripts:
- "deploy": wrangler pages deploy
- "deploy:preview": deploy ke preview environment
- "cf:dev": jalankan wrangler pages dev

Berikan juga instruksi setup singkat:
1. Cara hubungkan repo GitHub ke Cloudflare Pages
2. Cara set environment variables di Cloudflare dashboard
3. Custom domain setup
```

---

## 📋 Checklist Hari 1 Prompting

Centang setelah setiap output disimpan ke file yang tepat:

- [ ] Tugas 1 — `project-structure.md`
- [ ] Tugas 2 — `docker-compose.yml`
- [ ] Tugas 3 — `requirements.txt` + `requirements-dev.txt`
- [ ] Tugas 4 — `app/routers/health.py`
- [ ] Tugas 5 — `supabase/migrations/001_fallacy_tables.sql`
- [ ] Tugas 6 — `supabase/migrations/002_user_history.sql`
- [ ] Tugas 7 — semua file route SvelteKit
- [ ] Tugas 8 — `FallacyInput.svelte`
- [ ] Tugas 9 — `FallacyResult.svelte`
- [ ] Tugas 10 — `app/prompts/fallacy_detection.py`
- [ ] Tugas 11 — `fallacies.ts` + `fallacies.json`
- [ ] Tugas 12 — `scripts/benchmark.py`
- [ ] Tugas 13 — `README.md`
- [ ] Tugas 14 — `.env.example` + `backend/.env.example`
- [ ] Tugas 15 — `_redirects` + `wrangler.toml` + GitHub Actions

---

## ⚡ Tips Hari 1

**Urutan yang disarankan:**
Mulai dari Tugas 1 (struktur folder) karena semua tugas lain bergantung pada ini.
Setelah dapat struktur folder, Tugas 2-4 bisa dikerjakan paralel di tab berbeda.

**Jika ada konflik dengan kode Revonalar yang sudah ada:**
Tunjukkan file yang sudah ada ke Claude dan minta disesuaikan, bukan diganti.

**Untuk Tugas 7 (SvelteKit routes):**
Sebelum generate, cek dulu apakah route group `(student)` sudah ada di Revonalar.
Minta Claude lihat struktur folder Revonalar dulu sebelum generate.

**Target akhir hari:**
Semua 15 file sudah tersimpan di lokasi yang tepat.
Struktur folder proyek sudah terbentuk di GitHub.
Siap untuk Hari 2: deploy vLLM ke AMD cloud.
