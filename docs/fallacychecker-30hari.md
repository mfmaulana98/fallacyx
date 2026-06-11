# 🧠 FallacyChecker × Revonalar — Jadwal 30 Hari
### AMD Developer Hackathon: ACT II | 10 Juni – 10 Juli 2026

---

## 🗺️ Peta Proyek

**Yang dibangun:** FallacyChecker — fitur baru di ekosistem Revonalar
- Web app (SvelteKit, terintegrasi penuh dengan Revonalar)
- Chrome Extension dengan side panel real-time
- Backend AMD MI300X: vLLM + Llama-3-70B + Whisper Large-v3 + RAG (Qdrant)
- Pipeline: Teks / URL Artikel / YouTube URL / Audio Upload → Analisis Fallacy → Output terstruktur

**Revonalar yang disajikan ulang (lebih clean):**
TrapEngine, Penilaian, Mindmap, RevoPay, UMKM, Maskot, Inbox, Sosmed Feed

**Metode kerja:**
- 🤖 **PROMPTING** = dikerjakan via Claude/Cursor/VS Code Dispatch, bisa ditinggal
- 🖐️ **MANUAL** = harus turun tangan langsung

---

## FASE 1 — FONDASI & AMD SETUP
### 10–13 Juni 2026 | *"Dapur menyala"*

---

### 📅 Hari 1 — Selasa, 10 Juni 2026
**Tema: Orientasi & AMD Cloud Aktif**

#### 🤖 PROMPTING (15 tugas)
1. Generate struktur folder proyek FallacyChecker lengkap (SvelteKit + API)
2. Generate `docker-compose.yml` untuk vLLM + Qdrant + FastAPI
3. Generate `requirements.txt` semua dependency Python backend
4. Generate script health-check endpoint FastAPI (`GET /health`)
5. Generate schema database Supabase: tabel `fallacy_analyses`, `fallacy_vectors`
6. Generate tabel `user_fallacy_history` dengan RLS policy
7. Generate SvelteKit route struktur: `/fallacy`, `/fallacy/result/[id]`
8. Generate komponen `FallacyInput.svelte` (textarea + URL input + upload)
9. Generate `FallacyResult.svelte` skeleton dengan slot untuk data
10. Generate system prompt awal untuk deteksi fallacy (JSON output)
11. Generate daftar 25 jenis logical fallacy + definisi singkat dalam Bahasa Indonesia
12. Generate script benchmark sederhana: ukur latency endpoint AMD vs dummy
13. Generate `README.md` proyek dengan arsitektur diagram ASCII
14. Generate `.env.example` untuk semua environment variable yang dibutuhkan
15. Generate Cloudflare Pages `_redirects` dan config deployment awal

#### 🖐️ MANUAL (10 tugas)
1. Daftar AMD AI Developer Program → dapatkan $100 credits
2. Setup AMD Developer Cloud account, verifikasi akses MI300X
3. Enroll di lablab.ai AMD Developer Hackathon ACT II
4. Buat repo GitHub baru: `revonalar/fallacychecker`
5. Setup Supabase project baru atau pastikan project Revonalar bisa dipakai
6. Buat Hugging Face account (untuk submit Space nanti)
7. Install ekstensi VS Code: Claude, Cursor, REST Client
8. Screenshot AMD Cloud dashboard sebagai bukti setup (untuk slide nanti)
9. Catat kredensial AMD cloud di password manager
10. Buat channel Discord/Notion khusus tracking progress hackathon

---

### 📅 Hari 2 — Rabu, 11 Juni 2026
**Tema: Deploy vLLM + Model Pertama Berjalan**

#### 🤖 PROMPTING (15 tugas)
1. Generate script deploy vLLM di AMD Developer Cloud (ROCm backend)
2. Generate `startup.sh` untuk spin up instance MI300X otomatis
3. Generate FastAPI endpoint `POST /analyze/text` — terima teks, return JSON fallacy
4. Generate Pydantic model untuk request/response API
5. Generate prompt engineering v2: structured output dengan confidence score
6. Generate unit test untuk endpoint `/analyze/text`
7. Generate script Python: test kirim 10 teks berbeda ke endpoint, catat latency
8. Generate `FallacyBadge.svelte` — komponen kecil untuk tampilkan 1 fallacy
9. Generate `FallacyList.svelte` — list semua fallacy yang terdeteksi
10. Generate halaman `/fallacy` di SvelteKit dengan layout dasar
11. Generate loading skeleton untuk saat analisis sedang berjalan
12. Generate error handling component untuk API timeout/failure
13. Generate TypeScript types untuk semua data fallacy
14. Generate `api.ts` — fungsi fetch ke backend AMD
15. Generate migration SQL untuk tabel fallacy di Supabase

#### 🖐️ MANUAL (10 tugas)
1. SSH ke AMD Developer Cloud, jalankan script deploy vLLM
2. Download/pull model Llama-3-70B atau Qwen-72B ke instance AMD
3. Test endpoint manual via curl: kirim teks, lihat respons
4. Catat latency pertama kali: berapa detik model response?
5. Adjust parameter vLLM jika terlalu lambat (max_tokens, temperature)
6. Push kode awal ke GitHub
7. Verifikasi Supabase migration berhasil
8. Test koneksi SvelteKit → FastAPI → AMD endpoint
9. Screenshot/screen record: model pertama kali deteksi fallacy
10. Catat semua error yang muncul untuk diselesaikan besok

---

### 📅 Hari 3 — Kamis, 12 Juni 2026
**Tema: Pipeline Audio & YouTube**

#### 🤖 PROMPTING (15 tugas)
1. Generate FastAPI endpoint `POST /analyze/youtube` — terima URL, return fallacy
2. Generate script Python: yt-dlp + ffmpeg extract audio dari YouTube URL
3. Generate integrasi Whisper Large-v3 dengan ROCm untuk transkripsi
4. Generate pipeline: YouTube URL → audio → transkripsi → fallacy detection
5. Generate endpoint `POST /analyze/url` — scrape artikel, analisis teks
6. Generate fungsi scraping artikel pakai Jina Reader API (`r.jina.ai/[url]`)
7. Generate endpoint `POST /analyze/audio` — upload file audio, return fallacy
8. Generate progress tracking: SSE (Server-Sent Events) untuk update real-time
9. Generate `ProgressBar.svelte` untuk tampilkan status analisis
10. Generate komponen upload audio di SvelteKit
11. Generate YouTube URL validator dan extractor video ID
12. Generate caching layer: hasil analisis disimpan agar tidak proses ulang URL yang sama
13. Generate Redis config untuk caching (atau pakai Supabase sebagai cache)
14. Generate script test: analisis 5 video YouTube berbeda, ukur waktu
15. Generate dokumentasi API (OpenAPI spec) otomatis dari FastAPI

#### 🖐️ MANUAL (10 tugas)
1. Test pipeline YouTube end-to-end: paste URL → lihat fallacy muncul
2. Pilih 3 video YouTube Indonesia yang kaya fallacy untuk dijadikan demo material
3. Test upload audio MP3: apakah transkripsi akurat?
4. Verifikasi Whisper berjalan di GPU AMD, bukan CPU
5. Monitor GPU memory usage saat kedua model (LLM + Whisper) berjalan bersamaan
6. Test scraping 5 artikel berita berbeda, cek akurasi deteksi
7. Dokumentasikan temuan: jenis fallacy apa yang paling sering terdeteksi?
8. Push update ke GitHub
9. Update `README.md` dengan cara menjalankan pipeline
10. Catat benchmark: latency per pipeline (teks vs YouTube vs audio)

---

### 📅 Hari 4 — Jumat, 13 Juni 2026
**Tema: RAG Setup + Qdrant**

#### 🤖 PROMPTING (15 tugas)
1. Generate script deploy Qdrant di AMD Developer Cloud
2. Generate fungsi embedding: konversi teks fallacy ke vektor
3. Generate pipeline: setiap fallacy terdeteksi → embed → simpan ke Qdrant
4. Generate endpoint `GET /similar?fallacy_id=X` — cari fallacy serupa
5. Generate "memori kolektif" logic: cross-reference dengan analisis sebelumnya
6. Generate komponen `SimilarFallacies.svelte` — tampilkan konten terkait
7. Generate script: bulk import 100 contoh fallacy untuk seed database Qdrant
8. Generate query optimizer untuk Qdrant (filter by type, confidence score)
9. Generate `fallacy_taxonomy.json` — hierarki lengkap 25 jenis fallacy
10. Generate script benchmark Qdrant: search 1 juta vektor, ukur latency
11. Generate fungsi deduplikasi: hindari simpan fallacy yang identik
12. Generate tag otomatis: setiap analisis dapat label topik (politik, sains, dll)
13. Generate komponen `FallacyTimeline.svelte` — history analisis user
14. Generate API endpoint untuk ambil history analisis user dari Supabase
15. Generate integrasi Supabase Auth: analisis tersimpan per user

#### 🖐️ MANUAL (10 tugas)
1. Deploy Qdrant, verifikasi berjalan di AMD cloud
2. Test embedding: kirim teks, cek vektor tersimpan di Qdrant
3. Test cross-reference: analisis video baru, apakah sistem temukan kesamaan?
4. Monitor total GPU memory: vLLM + Whisper + embedding model bersamaan
5. Catat total VRAM usage — ini angka kunci untuk slide "kenapa AMD"
6. Test search Qdrant: seberapa cepat menemukan fallacy serupa?
7. Seed 50 contoh fallacy manual ke Qdrant untuk demo
8. Push semua update ke GitHub
9. Review kualitas deteksi: apakah 70B lebih akurat dari 7B? Dokumentasikan
10. Buat catatan: fitur RAG mana yang paling impressive untuk demo

---

## FASE 2 — CHROME EXTENSION & UI REVONALAR
### 14–17 Juni 2026 | *"Jendela ke dunia nyata"*

---

### 📅 Hari 5 — Sabtu, 14 Juni 2026
**Tema: Chrome Extension — Fondasi**

#### 🤖 PROMPTING (15 tugas)
1. Generate `manifest.json` v3 untuk Chrome Extension dengan side panel
2. Generate `background.js` — service worker untuk extension
3. Generate `sidepanel.html` + `sidepanel.js` — UI panel kanan
4. Generate `content.js` — script yang jalan di halaman YouTube
5. Generate logic: deteksi subtitle YouTube setiap 5 detik via MutationObserver
6. Generate fungsi: kirim subtitle chunk ke AMD backend API
7. Generate fungsi: terima hasil fallacy, tampilkan di side panel
8. Generate `sidepanel.css` — desain panel yang clean dan modern
9. Generate komponen notifikasi: badge merah kecil saat fallacy terdeteksi
10. Generate popup saat klik icon extension (status + quick stats)
11. Generate settings page: pilih sensitivitas deteksi, bahasa, notifikasi
12. Generate `utils.js` — helper functions untuk extension
13. Generate script build extension (webpack/vite config)
14. Generate README khusus untuk instalasi extension
15. Generate unit test untuk content script logic

#### 🖐️ MANUAL (10 tugas)
1. Load extension di Chrome (`chrome://extensions` → developer mode)
2. Buka video YouTube, verifikasi content script berjalan
3. Test: apakah subtitle berhasil di-capture tiap 5 detik?
4. Verifikasi koneksi extension → AMD backend API
5. Lihat side panel: apakah muncul dengan benar di samping YouTube?
6. Test notifikasi: apakah badge muncul saat fallacy terdeteksi?
7. Coba di beberapa video berbeda: berita, debat, podcast
8. Catat bug yang ditemukan
9. Screenshot extension dalam aksi untuk dokumentasi
10. Push kode extension ke GitHub

---

### 📅 Hari 6 — Minggu, 15 Juni 2026
**Tema: Chrome Extension — Polish + Non-YouTube**

#### 🤖 PROMPTING (15 tugas)
1. Generate logic: deteksi teks di halaman web arbitrary (bukan hanya YouTube)
2. Generate right-click context menu: "Cek Fallacy di teks ini"
3. Generate highlight overlay: teks yang mengandung fallacy di-highlight warna
4. Generate tooltip: hover di highlight → lihat nama fallacy + penjelasan
5. Generate animasi smooth saat fallacy baru muncul di side panel
6. Generate dark mode untuk side panel
7. Generate komponen `FallacyCard` di side panel — tiap fallacy 1 card
8. Generate timestamp link: klik timestamp di side panel → video jump ke momen itu
9. Generate share button: bagikan hasil analisis ke feed Revonalar
10. Generate counter badge di icon extension: "3 fallacy ditemukan"
11. Generate auto-pause option: video otomatis pause saat fallacy kritis terdeteksi
12. Generate keyboard shortcut: `Alt+F` untuk toggle side panel
13. Generate onboarding flow: pertama kali install → tutorial singkat
14. Generate analytics tracker: kirim anonymous usage data ke Supabase
15. Generate komponen feedback: user bisa mark deteksi sebagai "tepat" atau "salah"

#### 🖐️ MANUAL (10 tugas)
1. Test highlight overlay di artikel berita online
2. Test context menu: select teks → klik kanan → "Cek Fallacy"
3. Test di beberapa website berbeda (Kompas, CNN Indonesia, Medium)
4. Verifikasi dark mode bekerja
5. Test keyboard shortcut
6. Record screen: demo extension di artikel berita (calon konten demo video)
7. Ukur: berapa lama dari klik "Cek Fallacy" sampai hasil muncul?
8. Test feedback mechanism: apakah data tersimpan di Supabase?
9. Tunjukkan ke 1-2 orang, minta feedback pertama
10. Push update + tag versi `v0.1.0` di GitHub

---

### 📅 Hari 7 — Senin, 16 Juni 2026
**Tema: Revonalar Integration — FallacyChecker Page**

#### 🤖 PROMPTING (15 tugas)
1. Generate halaman `/fallacy` di Revonalar — layout utama FallacyChecker
2. Generate tab navigation: Teks | URL | YouTube | Audio
3. Generate form submit dengan validasi untuk masing-masing input type
4. Generate animasi loading: "Sedang menganalisis..." dengan progress step
5. Generate halaman hasil `/fallacy/result/[id]` — tampilan lengkap analisis
6. Generate visualisasi: pie chart breakdown jenis fallacy yang ditemukan
7. Generate timeline view: fallacy per menit untuk konten video
8. Generate "Confidence Score" indicator per fallacy yang terdeteksi
9. Generate section "Pelajari Lebih Lanjut" — link ke lesson Revonalar yang relevan
10. Generate gamifikasi: dapat Diamond setiap analisis pertama per hari
11. Generate share card: hasil analisis bisa di-share sebagai gambar
12. Generate halaman `/fallacy/leaderboard` — siapa paling banyak analisis bulan ini
13. Generate notifikasi in-app: "Kamu baru mendeteksi Ad Hominem pertamamu!"
14. Generate komponen "Fallacy of the Day" untuk dashboard Revonalar
15. Generate integrasi: hasil analisis muncul di feed sosmed Revonalar

#### 🖐️ MANUAL (10 tugas)
1. Test flow lengkap: login Revonalar → buka /fallacy → analisis → lihat hasil
2. Verifikasi Diamond reward masuk ke akun user setelah analisis
3. Test share card: apakah gambar ter-generate dengan benar?
4. Cek tampilan di mobile (Revonalar punya mobile view?)
5. Test leaderboard: apakah data ter-update real-time?
6. Verifikasi "Pelajari Lebih Lanjut" link ke lesson yang tepat
7. Test notifikasi in-app
8. Review keseluruhan UI: apakah konsisten dengan desain Revonalar?
9. Minta feedback dari 2-3 user Revonalar yang sudah ada
10. Dokumentasikan semua issue UI yang perlu diperbaiki

---

### 📅 Hari 8 — Selasa, 17 Juni 2026
**Tema: Revonalar Existing Features — Clean Presentation**

#### 🤖 PROMPTING (15 tugas)
1. Generate landing section baru di homepage Revonalar: showcase FallacyChecker
2. Generate `FallacyCheckerPromo.svelte` — banner di dashboard student
3. Generate integrasi TrapEngine: soal tentang fallacy yang baru dianalisis user
4. Generate koneksi Mindmap: fallacy taxonomy jadi mindmap interaktif
5. Generate RevoPay flow untuk unlock fitur premium FallacyChecker
6. Generate UMKM banner placement di halaman /fallacy (subsidi silang)
7. Generate Maskot reaction: maskot bereaksi saat fallacy berhasil ditemukan
8. Generate notifikasi Inbox: "Analisismu viral di feed!" 
9. Generate sosmed feed post otomatis saat user selesai analisis
10. Generate achievement/trophy baru: "Fallacy Hunter", "Logic Guardian", dll
11. Generate onboarding popup: perkenalkan FallacyChecker ke user lama Revonalar
12. Generate komponen statistik global: "Komunitas Revonalar sudah deteksi X fallacy"
13. Generate weekly digest email: ringkasan fallacy terpopuler minggu ini
14. Generate API endpoint untuk data statistik publik (untuk embed di landing page)
15. Generate `robots.txt` dan sitemap update untuk halaman baru

#### 🖐️ MANUAL (10 tugas)
1. Audit semua fitur Revonalar yang ada: mana yang perlu di-refresh visual
2. Test TrapEngine dengan soal fallacy baru
3. Verifikasi Mindmap fallacy taxonomy bisa di-render
4. Test RevoPay flow untuk FallacyChecker premium
5. Cek UMKM banner placement: tidak mengganggu tapi visible
6. Test Maskot reaction animasi
7. Verifikasi trophy/achievement tersimpan di database
8. Review statistik global: apakah angka akurat?
9. Push semua update
10. Screenshot setiap fitur yang sudah terintegrasi untuk slide presentasi

---

## FASE 3 — INTENSIF BUILD
### 18–20 Juni 2026 | *"Semua sistem aktif"*

---

### 📅 Hari 9 — Rabu, 18 Juni 2026
**Tema: Prompt Engineering & Akurasi Model**

#### 🤖 PROMPTING (15 tugas)
1. Generate 50 test case: teks dengan fallacy yang sudah dilabeli manual
2. Generate script evaluasi otomatis: bandingkan output model vs label manual
3. Generate prompt v3: few-shot examples untuk tiap kategori fallacy
4. Generate chain-of-thought prompt: model jelaskan reasoning sebelum conclude
5. Generate prompt khusus Bahasa Indonesia: deteksi fallacy dalam konteks budaya lokal
6. Generate prompt untuk konten campuran Bahasa Indonesia-Inggris (codeswitching)
7. Generate script A/B test: bandingkan akurasi 70B vs 7B model
8. Generate output formatter: pastikan JSON selalu valid, tidak pernah malformed
9. Generate fallback handler: jika model tidak yakin, return "tidak terdeteksi" bukan asal tebak
10. Generate prompt untuk mode "educational": output lebih panjang + contoh
11. Generate prompt untuk mode "quick": output minimal, hanya nama fallacy
12. Generate sistem rating akurasi: user vote apakah deteksi tepat
13. Generate script agregasi feedback: update prompt berdasarkan vote user
14. Generate dokumentasi: panduan prompt engineering untuk model selanjutnya
15. Generate benchmark report template untuk diisi hasil pengujian

#### 🖐️ MANUAL (10 tugas)
1. Jalankan 50 test case, catat akurasi manual
2. Bandingkan hasil 70B vs 7B — apakah 70B significantly lebih baik?
3. Test prompt Bahasa Indonesia dengan artikel Kompas/Detik
4. Test prompt codeswitching dengan konten YouTube Indonesia
5. Identifikasi 3 jenis fallacy yang paling sering salah terdeteksi
6. Perbaiki prompt secara manual berdasarkan temuan
7. Ukur ulang akurasi setelah perbaikan prompt
8. Dokumentasikan: "Dengan prompt v3, akurasi naik dari X% ke Y%"
9. Rekam video singkat: demo akurasi deteksi yang impressive
10. Push semua prompt dan benchmark ke GitHub

---

### 📅 Hari 10 — Kamis, 19 Juni 2026
**Tema: Performance Benchmark & Optimasi**

#### 🤖 PROMPTING (15 tugas)
1. Generate script benchmark lengkap: ukur latency, throughput, VRAM usage
2. Generate load test: simulasi 50 user concurrent kirim request bersamaan
3. Generate monitoring dashboard: Grafana config untuk AMD GPU metrics
4. Generate auto-scaling config: tambah instance jika load tinggi
5. Generate caching strategy: response cache untuk URL yang sudah dianalisis
6. Generate script: bandingkan performa AMD MI300X vs estimasi GPU lain (H100, T4)
7. Generate laporan benchmark dalam format tabel markdown
8. Generate optimasi vLLM: tensor parallelism, continuous batching config
9. Generate script profile memory: track VRAM per model component
10. Generate alert system: notifikasi jika latency > 3 detik
11. Generate retry logic: jika AMD API timeout, retry 3x dengan backoff
12. Generate circuit breaker: jika backend down, tampilkan pesan yang informatif
13. Generate script stress test: 1000 request dalam 1 menit
14. Generate cost calculator: estimasi biaya per 1000 analisis di AMD cloud
15. Generate slide teknis: visualisasi arsitektur + benchmark (untuk presentasi)

#### 🖐️ MANUAL (10 tugas)
1. Jalankan benchmark lengkap, catat semua angka
2. Jalankan load test 50 concurrent users, monitor GPU
3. Screenshot GPU utilization saat peak load (untuk slide)
4. Identifikasi bottleneck: di mana pipeline paling lambat?
5. Apply optimasi, ukur ulang performa
6. Verifikasi angka benchmark yang akan diklaim di presentasi
7. Setup Grafana monitoring (atau tool alternatif yang lebih simple)
8. Test caching: analisis URL yang sama 2x, apakah 2x lebih cepat?
9. Dokumentasikan semua angka benchmark di `BENCHMARK.md`
10. Push update + tag `v0.2.0`

---

### 📅 Hari 11 — Jumat, 20 Juni 2026
**Tema: Polish UI + Mobile Responsiveness**

#### 🤖 PROMPTING (15 tugas)
1. Generate responsive CSS untuk semua komponen FallacyChecker
2. Generate mobile-optimized layout untuk /fallacy page
3. Generate PWA manifest: FallacyChecker bisa di-install di mobile
4. Generate service worker untuk offline capability (cache hasil analisis)
5. Generate animasi micro-interaction: setiap fallacy card muncul dengan animasi
6. Generate empty state: ilustrasi saat belum ada analisis
7. Generate onboarding tour: highlight fitur-fitur utama untuk user baru
8. Generate skeleton loading yang lebih polished
9. Generate dark/light mode toggle untuk web app
10. Generate komponen "Fakta Menarik": tampilkan statistik fallacy yang engaging
11. Generate 404 dan error page yang on-brand dengan Revonalar
12. Generate print/export PDF: hasil analisis bisa di-download
13. Generate accessibility: ARIA labels, keyboard navigation
14. Generate SEO meta tags untuk halaman /fallacy
15. Generate Open Graph image generator untuk share di sosmed

#### 🖐️ MANUAL (10 tugas)
1. Review semua halaman di mobile (iPhone + Android)
2. Test PWA installation di Android
3. Verifikasi animasi berjalan smooth, tidak janky
4. Test dark mode: apakah semua elemen terbaca?
5. Jalankan Lighthouse audit, catat skor performance
6. Test export PDF: apakah layout rapi?
7. Test accessibility dengan screen reader
8. Review keseluruhan UX: apakah flow terasa natural?
9. Minta 3 orang test pakai, catat feedback
10. List semua polish items untuk dikerjakan di fase berikutnya

---

## FASE 4 — INTENSIF SPRINT
### 21–30 Juni 2026 | *"Full throttle"* (min. 30 tugas/hari)

---

### 📅 Hari 12 — Sabtu, 21 Juni 2026
**Tema: Demo Video Preparation**

1. 🤖 Generate storyboard demo video: scene by scene, durasi 3 menit
2. 🤖 Generate script narasi untuk demo video (Bahasa Inggris, karena juri internasional)
3. 🤖 Generate talking points: 5 angka kunci yang harus disebut dalam demo
4. 🤖 Generate komponen "Live Counter" untuk demo: fallacy terdeteksi real-time
5. 🤖 Generate "WOW moment" screen: visualisasi 1000 fallacy tersimpan di RAG
6. 🤖 Generate komponen khusus demo: tampilan yang lebih dramatis dari produksi
7. 🤖 Generate script setup: cara reset state sebelum rekam ulang demo
8. 🤖 Generate caption/subtitle template untuk video demo
9. 🤖 Generate thumbnail design (brief untuk Canva/Figma)
10. 🤖 Generate fallback plan: jika live demo gagal, pre-recorded backup
11. 🖐️ Pilih video YouTube Indonesia untuk scene utama demo
12. 🖐️ Rekam dry run pertama demo video
13. 🖐️ Review dry run, catat bagian yang kurang wow
14. 🖐️ Test koneksi internet untuk rekam demo — pastikan tidak lag
15. 🤖 Generate script untuk narasi scene "kenapa AMD"
16. 🤖 Generate lower-third graphics brief untuk video
17. 🤖 Generate end card CTA: "Coba di Revonalar sekarang"
18. 🖐️ Pilih musik background untuk video (bebas royalti)
19. 🤖 Generate checklist pre-demo: semua yang harus dicek sebelum rekam
20. 🤖 Generate daftar "sound bytes" yang paling quotable untuk juri
21. 🖐️ Setup screen recording software (OBS atau Loom)
22. 🖐️ Atur resolusi layar untuk recording yang clean (1920x1080)
23. 🤖 Generate komponen animasi "AMD MI300X powered" badge untuk overlay video
24. 🤖 Generate data visualization: graph yang menunjukkan performa AMD
25. 🖐️ Rekam footage: AMD Dashboard sebagai proof of GPU usage
26. 🤖 Generate script Python: generate fake (tapi realistis) load test visual untuk demo
27. 🖐️ Test semua scene demo end-to-end tanpa henti
28. 🖐️ Catat timing tiap scene: total harus 2-3 menit
29. 🤖 Generate subtitle/caption untuk demo video (SRT format)
30. 🖐️ Rekam dry run kedua, bandingkan dengan pertama

---

### 📅 Hari 13 — Minggu, 22 Juni 2026
**Tema: Slide Deck Pitching**

1. 🤖 Generate outline slide deck: 12 slide, tiap slide 1 pesan utama
2. 🤖 Generate konten Slide 1: Problem — era misinformasi, statistik mengejutkan
3. 🤖 Generate konten Slide 2: Solution — FallacyChecker di Revonalar
4. 🤖 Generate konten Slide 3: Demo (placeholder, isi setelah video jadi)
5. 🤖 Generate konten Slide 4: Arsitektur teknis — diagram AMD MI300X
6. 🤖 Generate konten Slide 5: Kenapa AMD — 1 GPU vs 4 H100, VRAM 192GB
7. 🤖 Generate konten Slide 6: Benchmark — tabel performa dengan angka nyata
8. 🤖 Generate konten Slide 7: Revonalar ecosystem — TrapEngine, Mindmap, UMKM, dll
9. 🤖 Generate konten Slide 8: Traction — user existing, fitur yang sudah live
10. 🤖 Generate konten Slide 9: Network Effect — RAG memori kolektif
11. 🤖 Generate konten Slide 10: Business Model — RevoPay, UMKM subsidi silang
12. 🤖 Generate konten Slide 11: Roadmap — sosmed integration, mobile app
13. 🤖 Generate konten Slide 12: Call to Action — coba sekarang, join komunitas
14. 🖐️ Review semua konten slide: ada yang perlu diubah?
15. 🤖 Generate speaker notes untuk tiap slide
16. 🤖 Generate versi ringkas: slide deck 5 slide untuk pitch 2 menit
17. 🤖 Generate quote-worthy one-liner untuk tiap slide
18. 🖐️ Buat slide deck di Canva/Google Slides berdasarkan brief
19. 🤖 Generate desain brief: warna, font, style yang konsisten dengan Revonalar
20. 🤖 Generate infographic: "Journey konten dari YouTube ke Fallacy Report"
21. 🤖 Generate diagram: "Bagaimana RAG memori kolektif bekerja"
22. 🖐️ Masukkan angka benchmark nyata ke slide
23. 🖐️ Masukkan screenshot produk yang paling impressive
24. 🤖 Generate FAQ: 10 pertanyaan yang mungkin ditanya juri + jawabannya
25. 🤖 Generate jawaban untuk: "Kenapa tidak pakai OpenAI API saja?"
26. 🤖 Generate jawaban untuk: "Bagaimana monetisasinya?"
27. 🤖 Generate jawaban untuk: "Apa yang membedakan dari fact-checker lain?"
28. 🖐️ Review slide deck dari perspektif juri non-teknis
29. 🖐️ Review slide deck dari perspektif juri teknis AMD
30. 🤖 Generate checklist: semua yang harus ada di submission lablab.ai

---

### 📅 Hari 14 — Senin, 23 Juni 2026
**Tema: Batch Processing & Demo Masif**

1. 🤖 Generate endpoint `POST /analyze/batch` — terima list URL, proses paralel
2. 🤖 Generate job queue system (Celery atau ARQ) untuk batch processing
3. 🤖 Generate progress tracker untuk batch job: X dari 100 selesai
4. 🤖 Generate UI: halaman `/fallacy/batch` untuk upload banyak URL sekaligus
5. 🤖 Generate hasil batch: dashboard ringkasan semua analisis dalam 1 batch
6. 🤖 Generate export batch result: CSV + JSON download
7. 🤖 Generate script: proses 100 video YouTube dalam < 30 detik (demo killer)
8. 🤖 Generate visualisasi batch: heatmap fallacy per video
9. 🤖 Generate "Playlist Analyzer": analisis semua video dalam 1 playlist YouTube
10. 🤖 Generate script benchmark batch: ukur waktu, bandingkan dengan CPU
11. 🖐️ Test batch processing dengan 10 URL dulu
12. 🖐️ Scale ke 50 URL: apakah sistem stable?
13. 🖐️ Scale ke 100 URL: catat waktu total
14. 🖐️ Monitor GPU saat batch 100 URL: screenshot untuk slide
15. 🤖 Generate laporan otomatis setelah batch selesai
16. 🤖 Generate notifikasi: email/in-app saat batch selesai
17. 🤖 Generate visualisasi "trending fallacy": fallacy apa yang paling banyak minggu ini
18. 🤖 Generate komponen global stats: counter animasi untuk landing page
19. 🖐️ Test playlist YouTube: analisis 1 playlist penuh, lihat hasilnya
20. 🤖 Generate "channel analyzer": analisis pattern fallacy dari 1 channel YouTube
21. 🤖 Generate webhook: notifikasi ke Discord/Slack saat batch selesai
22. 🖐️ Rekam footage batch processing untuk demo video
23. 🤖 Generate thumbnail batch result yang shareable
24. 🤖 Generate API rate limiting agar tidak abuse AMD credits
25. 🖐️ Verifikasi cost: berapa AMD credits habis untuk 100 video?
26. 🤖 Generate cost optimization: caching agar video yang sama tidak diproses ulang
27. 🤖 Generate "free tier" logic: user non-premium dapat 5 analisis/hari
28. 🖐️ Test free tier vs premium tier
29. 🤖 Generate upgrade prompt: tampilkan saat user habis kuota free
30. 🖐️ Push semua update + dokumentasikan angka batch benchmark

---

### 📅 Hari 15 — Selasa, 24 Juni 2026
**Tema: Revonalar Deep Integration**

1. 🤖 Generate course baru di Revonalar: "Kenali Logical Fallacy" — 5 chapter
2. 🤖 Generate soal TrapEngine berbasis real fallacy yang terdeteksi komunitas
3. 🤖 Generate sistem: fallacy yang sering ditemukan user → jadi soal TrapEngine otomatis
4. 🤖 Generate Mindmap: peta visual semua 25 jenis fallacy dengan contoh
5. 🤖 Generate koneksi Mindmap → /fallacy: klik node → lihat contoh real dari komunitas
6. 🤖 Generate "Daily Challenge": analisis 1 konten per hari, dapat Diamond
7. 🤖 Generate streak system: streak harian untuk FallacyChecker
8. 🤖 Generate level progression: dari "Pemula Logika" sampai "Master Argumen"
9. 🤖 Generate koleksi maskot baru: 5 maskot bertema logical fallacy
10. 🤖 Generate trophy baru: "Pertama Kali Temukan Strawman", "100 Analisis", dll
11. 🤖 Generate feed sosmed: post otomatis saat user temukan fallacy langka
12. 🤖 Generate weekly report untuk user: "Minggu ini kamu temukan X fallacy"
13. 🤖 Generate leaderboard khusus FallacyChecker bulan ini
14. 🤖 Generate "Hall of Fame": analisis paling banyak di-share komunitas
15. 🤖 Generate notifikasi push (PWA): "Ada video viral baru yang perlu dicek!"
16. 🖐️ Test course baru: apakah lesson flow logis?
17. 🖐️ Verifikasi TrapEngine soal fallacy bisa di-generate dari data komunitas
18. 🖐️ Test Mindmap fallacy: apakah semua 25 node terhubung dengan benar?
19. 🖐️ Test Daily Challenge + Diamond reward
20. 🖐️ Verifikasi streak system bekerja
21. 🖐️ Review maskot baru: apakah desain konsisten?
22. 🖐️ Test trophy unlock: apakah muncul di profil user?
23. 🖐️ Test feed sosmed: apakah post auto-generate terlihat bagus?
24. 🤖 Generate integrasi inbox: notifikasi jika konten yang dianalisis mendapat komentar
25. 🤖 Generate "Collaborative Analysis": dua user analisis konten yang sama, bandingkan
26. 🖐️ Test collaborative analysis feature
27. 🤖 Generate "Expert Badge": badge khusus untuk user yang feedback-nya paling akurat
28. 🤖 Generate class/group feature: guru bisa assign konten untuk dianalisis murid
29. 🖐️ Test class feature: buat class dummy, assign konten, lihat hasil murid
30. 🖐️ Push semua update + screenshot semua fitur baru untuk slide

---

### 📅 Hari 16 — Rabu, 25 Juni 2026
**Tema: UMKM & RevoPay Integration**

1. 🤖 Generate UMKM placement strategy untuk FallacyChecker
2. 🤖 Generate komponen `UmkmBanner.svelte` yang contextual (iklan relevan dengan konten yang dianalisis)
3. 🤖 Generate "Sponsored Analysis": UMKM bisa sponsor analisis konten tertentu
4. 🤖 Generate RevoPay flow: user beli premium FallacyChecker pakai RevoPay
5. 🤖 Generate pricing page: Free vs Premium vs Education tier
6. 🤖 Generate Diamond earning dari FallacyChecker: tugas, streak, kontribusi feedback
7. 🤖 Generate Diamond spending: unlock advanced analysis, export PDF, dll
8. 🤖 Generate "Education Subsidi": UMKM yang beriklan subisidi Diamond untuk pelajar
9. 🤖 Generate dashboard UMKM: lihat berapa banyak pelajar terekspos iklan mereka
10. 🤖 Generate impact report: "Iklan kamu membantu X pelajar belajar logika hari ini"
11. 🖐️ Review model bisnis keseluruhan: apakah sustainable?
12. 🖐️ Test RevoPay flow end-to-end
13. 🖐️ Verifikasi Diamond earning dari FallacyChecker masuk ke wallet user
14. 🤖 Generate komponen wallet: tampilkan Diamond + RevoPay balance di FallacyChecker page
15. 🤖 Generate "Referral Program": ajak teman, dapat Diamond bonus
16. 🖐️ Test referral link generation dan tracking
17. 🤖 Generate invoice otomatis untuk transaksi RevoPay
18. 🤖 Generate laporan keuangan sederhana untuk dashboard UMKM
19. 🤖 Generate compliance note: disclaimer untuk konten analisis
20. 🤖 Generate terms of service tambahan untuk FallacyChecker
21. 🤖 Generate privacy policy update: bagaimana data analisis disimpan
22. 🖐️ Review legal aspects: apakah ada risiko analisis konten milik orang lain?
23. 🤖 Generate safe harbor disclaimer di setiap hasil analisis
24. 🤖 Generate "Report Error" button: jika user merasa analisis tidak akurat
25. 🖐️ Test report error flow
26. 🤖 Generate moderation queue: review laporan yang masuk
27. 🤖 Generate auto-moderation: filter hasil analisis yang mungkin ofensif
28. 🖐️ Test auto-moderation dengan beberapa edge case
29. 🤖 Generate audit log: semua analisis tercatat dengan timestamp + user ID
30. 🖐️ Push semua update

---

### 📅 Hari 17 — Kamis, 26 Juni 2026
**Tema: Public Landing Page & SEO**

1. 🤖 Generate landing page baru: `fallacychecker.revonalar.com` atau subdomain
2. 🤖 Generate hero section: tagline kuat + CTA langsung ke demo
3. 🤖 Generate "How it Works" section: 3 langkah simple dengan animasi
4. 🤖 Generate "Live Demo" embed: iframe atau komponen interaktif di landing
5. 🤖 Generate social proof section: statistik komunitas real-time
6. 🤖 Generate feature comparison table: Free vs Premium
7. 🤖 Generate testimonial section (isi dengan quotes dari tester awal)
8. 🤖 Generate FAQ section untuk landing page
9. 🤖 Generate footer dengan semua link penting
10. 🤖 Generate blog post: "Apa itu Logical Fallacy dan Mengapa Penting?"
11. 🤖 Generate blog post: "5 Fallacy Paling Sering di Media Sosial Indonesia"
12. 🤖 Generate blog post teknis: "Bagaimana Kami Membangun FallacyChecker di AMD MI300X"
13. 🤖 Generate sitemap XML untuk semua halaman
14. 🤖 Generate structured data (schema.org) untuk SEO
15. 🤖 Generate meta description untuk semua halaman penting
16. 🖐️ Review landing page: apakah value proposition jelas dalam 5 detik?
17. 🖐️ Test live demo di landing: apakah berfungsi tanpa login?
18. 🖐️ Test di mobile: apakah landing page responsive?
19. 🤖 Generate OG image untuk tiap halaman (untuk Twitter/WhatsApp preview)
20. 🤖 Generate email capture form: "Dapatkan update FallacyChecker"
21. 🖐️ Setup Cloudflare Analytics untuk landing page
22. 🤖 Generate A/B test variant untuk hero tagline
23. 🤖 Generate heatmap setup: Hotjar atau Microsoft Clarity config
24. 🖐️ Submit sitemap ke Google Search Console
25. 🤖 Generate press kit: deskripsi singkat, logo, screenshot untuk media
26. 🤖 Generate Product Hunt draft: deskripsi, tagline, media untuk future launch
27. 🤖 Generate Hugging Face Space: deploy demo ke HF untuk hackathon requirement
28. 🖐️ Deploy dan test Hugging Face Space
29. 🖐️ Share HF Space ke komunitas untuk "likes" (Hugging Face prize)
30. 🤖 Generate social media caption untuk announce ke komunitas

---

### 📅 Hari 18 — Jumat, 27 Juni 2026
**Tema: Bug Hunt & Stabilitas**

1. 🤖 Generate comprehensive test suite: semua endpoint API
2. 🤖 Generate E2E test: flow lengkap dari input sampai hasil tampil
3. 🤖 Generate test untuk edge case: URL invalid, teks kosong, audio rusak
4. 🤖 Generate test untuk rate limiting
5. 🤖 Generate test untuk concurrent users
6. 🤖 Generate monitoring alert rules: latency, error rate, GPU temp
7. 🤖 Generate error logging: semua error ke Sentry atau LogTail
8. 🤖 Generate graceful degradation: jika AMD backend down, fallback ke model kecil
9. 🤖 Generate retry mechanism dengan exponential backoff
10. 🤖 Generate health check dashboard: status semua komponen real-time
11. 🖐️ Jalankan semua test: catat yang fail
12. 🖐️ Fix 5 bug teratas yang ditemukan
13. 🖐️ Test edge case manual: apa yang terjadi jika YouTube video privat?
14. 🖐️ Test dengan koneksi internet lambat (throttle di DevTools)
15. 🤖 Generate fix untuk setiap bug yang ditemukan
16. 🤖 Generate regression test untuk setiap bug yang diperbaiki
17. 🖐️ Test fallback mode: matikan AMD backend, apakah error message informatif?
18. 🖐️ Load test ulang setelah semua fix
19. 🤖 Generate changelog: semua yang berubah dari v0.1 ke v1.0
20. 🤖 Generate release notes yang bisa dibaca user
21. 🖐️ Review semua error message: apakah user-friendly?
22. 🤖 Generate komponen error boundary di SvelteKit
23. 🤖 Generate offline detection: notifikasi jika user offline
24. 🖐️ Test offline behavior: apa yang terjadi jika koneksi putus saat analisis?
25. 🤖 Generate auto-save: simpan hasil analisis di localStorage sebagai backup
26. 🖐️ Verifikasi auto-save bekerja
27. 🤖 Generate database backup strategy untuk Supabase
28. 🖐️ Setup automated backup Supabase
29. 🤖 Generate security audit checklist: SQL injection, XSS, CSRF
30. 🖐️ Jalankan security audit manual, catat temuan

---

### 📅 Hari 19 — Sabtu, 28 Juni 2026
**Tema: Demo Video — Rekam Final**

1. 🤖 Generate shot list final: setiap detik dari 180 detik video
2. 🤖 Generate script narasi final (Bahasa Inggris, energetik, confident)
3. 🤖 Generate B-roll list: footage tambahan yang dibutuhkan
4. 🖐️ Setup recording environment: clean desktop, font besar, kontras tinggi
5. 🖐️ Rekam Scene 1: hook — statistik misinformasi mengejutkan (15 detik)
6. 🖐️ Rekam Scene 2: demo web app — paste teks, lihat fallacy muncul (30 detik)
7. 🖐️ Rekam Scene 3: demo URL artikel berita — analisis otomatis (20 detik)
8. 🖐️ Rekam Scene 4: demo YouTube URL — transkripsi + timeline fallacy (30 detik)
9. 🖐️ Rekam Scene 5: Chrome extension side panel — real-time saat nonton (30 detik)
10. 🖐️ Rekam Scene 6: RAG memori kolektif — "fallacy ini sudah ditemukan 47x" (15 detik)
11. 🖐️ Rekam Scene 7: Revonalar ecosystem — gamifikasi, diamond, komunitas (20 detik)
12. 🖐️ Rekam Scene 8: AMD Dashboard — GPU utilization, 1 MI300X (10 detik)
13. 🤖 Generate transition brief untuk video editor
14. 🖐️ Review semua footage: ada yang perlu direkam ulang?
15. 🖐️ Rekam ulang scene yang kurang bagus
16. 🤖 Generate caption teks untuk tiap scene (Bahasa Inggris)
17. 🖐️ Edit video: gabungkan semua scene, tambah musik, caption
18. 🖐️ Export video 1080p, max 5 menit
19. 🖐️ Review final video: apakah alur logis dan exciting?
20. 🤖 Generate thumbnail untuk video: desain yang click-worthy
21. 🖐️ Buat thumbnail di Canva
22. 🖐️ Upload video ke YouTube sebagai unlisted (untuk submission link)
23. 🤖 Generate deskripsi YouTube: SEO-optimized, include semua keyword penting
24. 🖐️ Minta 2-3 orang tonton video, catat feedback
25. 🤖 Generate revisi berdasarkan feedback
26. 🖐️ Lakukan revisi minor jika diperlukan
27. 🖐️ Final review video
28. 🤖 Generate tweet thread untuk announce video
29. 🤖 Generate LinkedIn post untuk announce project
30. 🖐️ Push semua update + tag `v1.0.0` di GitHub

---

### 📅 Hari 20 — Minggu, 29 Juni 2026
**Tema: Submission Preparation**

1. 🤖 Generate project description singkat (max 150 karakter) untuk lablab.ai
2. 🤖 Generate project description panjang (max 500 kata) untuk submission
3. 🤖 Generate daftar semua teknologi yang dipakai (tag di lablab.ai)
4. 🤖 Generate GitHub README final: profesional, lengkap, impressive
5. 🤖 Generate CONTRIBUTING.md: panduan kontribusi open source
6. 🤖 Generate LICENSE.md: MIT license
7. 🤖 Generate ARCHITECTURE.md: penjelasan teknis lengkap
8. 🤖 Generate installation guide: cara setup dari nol
9. 🤖 Generate API documentation lengkap
10. 🤖 Generate CHANGELOG.md dari awal sampai v1.0
11. 🖐️ Review GitHub repo: apakah terlihat profesional?
12. 🖐️ Pastikan semua file penting ada di repo
13. 🤖 Generate HF Space description + model card
14. 🖐️ Update HF Space dengan versi terbaru
15. 🖐️ Share HF Space ke semua channel untuk collect likes
16. 🤖 Generate cover image untuk submission lablab.ai (1200x630px brief)
17. 🖐️ Buat cover image di Canva
18. 🖐️ Upload cover image, video, slide ke lablab.ai draft submission
19. 🤖 Generate checklist submission: semua yang wajib ada
20. 🖐️ Verifikasi semua link submission bekerja
21. 🤖 Generate "Build in Public" tweet #1 (Ship It Challenge)
22. 🤖 Generate "Build in Public" tweet #2 dengan technical insight
23. 🖐️ Post keduanya di X, tag @lablab dan @AIatAMD
24. 🤖 Generate LinkedIn post technical walkthrough
25. 🖐️ Post di LinkedIn
26. 🤖 Generate Medium article draft: "How I Built FallacyChecker in 30 Days"
27. 🤖 Generate open-source announcement: post di Reddit r/MachineLearning
28. 🖐️ Review semua submission materials satu kali lagi
29. 🖐️ Submit draft ke lablab.ai (belum final, cek semua section)
30. 🖐️ Istirahat — besok final polish

---

### 📅 Hari 21 — Senin, 30 Juni 2026
**Tema: Final Polish & Submit**

1. 🤖 Generate final proofreading semua teks submission
2. 🤖 Generate spell check + grammar check script untuk semua konten Bahasa Inggris
3. 🖐️ Review submission di lablab.ai: baca dari perspektif juri
4. 🖐️ Perbaiki typo atau kalimat yang tidak jelas
5. 🤖 Generate updated demo script berdasarkan feedback hari 19
6. 🖐️ Final test semua URL yang di-submit: apakah masih bekerja?
7. 🖐️ Final test Hugging Face Space: apakah demo masih berjalan?
8. 🖐️ Final test GitHub repo: clone dari awal, ikuti README, apakah berjalan?
9. 🤖 Generate thank you post untuk komunitas yang membantu testing
10. 🖐️ **SUBMIT FINAL ke lablab.ai**
11. 🖐️ Screenshot konfirmasi submission
12. 🤖 Generate post-submission social media announcement
13. 🖐️ Post di semua channel: X, LinkedIn, Discord lablab.ai
14. 🤖 Generate email draft untuk reach out ke juri (Joseph Spence, Rahul Gupta)
15. 🖐️ Connect dengan juri di LinkedIn dengan pesan personal

---

## FASE 5 — POST-SUBMISSION & FINALISASI
### 1–10 Juli 2026 | *"Tunggu dan persiapkan presentasi"*

---

### 📅 Hari 22 — Selasa, 1 Juli 2026
**Tema: Presentasi & Public Engagement**

#### 🤖 PROMPTING (15 tugas)
1. Generate pitch deck versi presentasi lisan (berbeda dari slide submission)
2. Generate pembukaan yang powerful: 30 detik pertama yang memorable
3. Generate transisi antar slide yang smooth
4. Generate visualisasi data yang lebih dramatis dari slide submission
5. Generate "Demo Live" script: langkah demi langkah saat demo di depan juri
6. Generate Q&A preparation: 20 pertanyaan toughest + jawaban
7. Generate backup slides: jika internet mati saat demo, ada pre-recorded backup
8. Generate executive summary: 1 halaman PDF tentang FallacyChecker
9. Generate investor one-pager: format standar untuk fundraising
10. Generate press release draft: untuk announcement jika menang
11. Generate product roadmap 6 bulan ke depan
12. Generate competitive analysis: bandingkan dengan tools serupa yang ada
13. Generate go-to-market strategy Indonesia + global
14. Generate user acquisition strategy: bagaimana dapat 1000 user pertama
15. Generate community building plan: bagaimana tumbuhkan komunitas FallacyChecker

#### 🖐️ MANUAL (10 tugas)
1. Latihan pitch 3 menit: rekam, tonton, perbaiki
2. Latihan Q&A dengan simulasi pertanyaan juri
3. Setup backup internet (hotspot) untuk hari presentasi
4. Verifikasi jadwal presentasi final dari lablab.ai
5. Join Discord lablab.ai: engage dengan komunitas, vote proyek lain
6. Share Hugging Face Space ke forum-forum AI Indonesia
7. Post di Reddit r/indonesia tentang proyek
8. Reach out ke komunitas debat/logika Indonesia untuk feedback
9. Dokumentasikan semua feedback yang diterima
10. Update fitur minor berdasarkan feedback paling valid

---

### 📅 Hari 23 — Rabu, 2 Juli 2026

#### 🤖 PROMPTING (15 tugas)
1. Generate feature: "Trending Fallacies Indonesia" — widget publik
2. Generate integrasi notifikasi browser (Web Push API)
3. Generate komponen "Share ke WhatsApp" — paling relevan untuk user Indonesia
4. Generate fitur "Kirim ke Guru": murid bisa kirim hasil analisis ke guru
5. Generate mode "Classroom": guru monitor semua analisis murid real-time
6. Generate sertifikat digital: selesaikan 10 analisis → dapat sertifikat
7. Generate QR code untuk tiap hasil analisis (bisa discan untuk lihat di mobile)
8. Generate komponen "Verifikasi Komunitas": 10 user setuju → fallacy confirmed
9. Generate API publik dokumentasi: agar developer lain bisa pakai FallacyChecker
10. Generate webhook system: developer bisa terima notifikasi real-time
11. Generate SDK JavaScript sederhana untuk embed FallacyChecker
12. Generate embed widget: `<fallacy-checker>` web component
13. Generate plugin WordPress: situs berita bisa pasang FallacyChecker
14. Generate browser bookmarklet sebagai alternatif extension
15. Generate mobile deep link: buka hasil analisis langsung di app

#### 🖐️ MANUAL (15 tugas)
1. Test fitur share ke WhatsApp
2. Test classroom mode: buat kelas dummy, isi dengan akun murid test
3. Verifikasi sertifikat digital ter-generate dengan benar
4. Test QR code: scan dari HP, apakah buka halaman yang benar?
5. Test community verification flow
6. Review API publik dokumentasi: apakah jelas untuk developer lain?
7. Test embed widget di halaman HTML kosong
8. Test bookmarklet di beberapa website
9. Latihan pitch ulang dengan materi terbaru
10. Monitor HF Space: berapa likes sekarang?
11. Post update Build in Public #3 di X
12. Balas semua komentar dan feedback di sosmed
13. Dokumentasikan fitur baru yang ditambah
14. Push semua update
15. Ukur: berapa total analisis yang sudah dilakukan sejak launch?

---

### 📅 Hari 24 — Kamis, 3 Juli 2026

#### 🤖 PROMPTING (15 tugas)
1. Generate script final demo video jika ada request dari juri
2. Generate "Case Study": analisis fallacy di 1 debat politik Indonesia terkenal
3. Generate laporan mendalam: 10 halaman tentang logical fallacy di media Indonesia
4. Generate infographic: "Peta Logical Fallacy Indonesia 2026"
5. Generate script untuk podcast/interview tentang proyek
6. Generate FAQ update berdasarkan pertanyaan yang masuk dari komunitas
7. Generate changelog v1.1: semua update setelah submission
8. Generate roadmap visual: timeline fitur 2026-2027
9. Generate pitch untuk partnership: sekolah, universitas, media
10. Generate email template untuk outreach ke institusi pendidikan
11. Generate proposal untuk Kemendikbud: program literasi digital
12. Generate model business plan: revenue projection 3 tahun
13. Generate investor pitch (format Y Combinator)
14. Generate technical blog post untuk dev.to / Hashnode
15. Generate documentation update: semua perubahan setelah v1.0

#### 🖐️ MANUAL (15 tugas)
1. Tulis Case Study fallacy di debat politik (manual, butuh insight)
2. Review infographic sebelum publish
3. Post Case Study di Medium/LinkedIn
4. Latihan pitch dengan seseorang yang kritis
5. Rekam pitch versi terbaru
6. Tonton ulang, catat 3 hal yang perlu diperbaiki
7. Perbaiki dan rekam ulang
8. Monitor engagement social media: post mana yang paling viral?
9. Reply semua DM dan komentar
10. Join diskusi di Discord lablab.ai tentang submissions
11. Vote dan comment untuk proyek lain yang bagus
12. Screen record jika ada bug baru yang ditemukan user
13. Fix bug critical jika ada
14. Update HF Space jika ada perubahan signifikan
15. Dokumentasikan progress harian

---

### 📅 Hari 25 — Jumat, 4 Juli 2026

#### 🤖 PROMPTING (15 tugas)
1. Generate stress test script: simulasi 1000 concurrent users
2. Generate auto-scaling config yang lebih robust
3. Generate CDN setup: Cloudflare cache untuk static assets
4. Generate database optimization: index yang tepat untuk query cepat
5. Generate query optimizer untuk Qdrant vector search
6. Generate monitoring dashboard yang lebih lengkap
7. Generate alert system yang lebih granular
8. Generate disaster recovery plan: jika instance AMD crash
9. Generate backup strategy untuk Qdrant vectors
10. Generate script: restore dari backup dalam < 5 menit
11. Generate performance profiling report
12. Generate optimization recommendations dari profiling
13. Generate load balancer config untuk multiple AMD instances
14. Generate API versioning strategy: v1, v2 endpoint
15. Generate deprecation notice system untuk old API

#### 🖐️ MANUAL (15 tugas)
1. Jalankan stress test 1000 users: catat hasil
2. Identifikasi breaking point: di berapa user sistem mulai lambat?
3. Apply auto-scaling fix
4. Test disaster recovery: matikan instance, restore dari backup
5. Ukur waktu recovery
6. Review monitoring dashboard: apakah semua metrik penting ada?
7. Test alert: trigger alert manual, verifikasi notifikasi diterima
8. Verifikasi CDN bekerja: assets di-serve dari cache
9. Benchmark database query sebelum dan sesudah optimasi
10. Dokumentasikan semua angka performa terbaru
11. Update slide benchmark dengan angka terbaru
12. Push semua update
13. Post Build in Public #4 dengan technical insight
14. Review feedback dari komunitas yang sudah coba produk
15. Prioritaskan fitur yang paling banyak diminta user

---

### 📅 Hari 26 — Sabtu, 5 Juli 2026

#### 🤖 PROMPTING (15 tugas)
1. Generate fitur: "Fallacy Duel" — dua user debat, AI tentukan siapa yang pakai fallacy lebih banyak
2. Generate gamifikasi lanjutan: ranking nasional Indonesia
3. Generate komponen "Indonesia vs Dunia": bandingkan pola fallacy
4. Generate analisis temporal: fallacy meningkat saat pemilu/isu panas?
5. Generate API untuk researcher: akses anonymized data untuk penelitian
6. Generate academic citation format untuk hasil analisis
7. Generate integrasi Zotero/Mendeley: simpan analisis sebagai referensi
8. Generate "Fallacy Report Card": laporan bulanan per user
9. Generate komponen "Improvement Track": progres user dari waktu ke waktu
10. Generate machine learning feedback loop: akurasi makin baik dari feedback user
11. Generate A/B test untuk UI: versi mana yang lebih banyak convert?
12. Generate analytics dashboard untuk Revonalar admin
13. Generate revenue dashboard: track RevoPay, Diamond, UMKM
14. Generate churn analysis: user mana yang berhenti menggunakan?
15. Generate retention strategy: notifikasi, challenge, reward untuk user yang inaktif

#### 🖐️ MANUAL (15 tugas)
1. Test "Fallacy Duel" dengan 2 akun berbeda
2. Verifikasi ranking nasional akurat
3. Review analisis temporal: apakah data cukup untuk insight menarik?
4. Test integrasi Zotero
5. Review report card bulanan
6. Analisis A/B test result: versi mana yang menang?
7. Review revenue dashboard: apakah angka masuk akal?
8. Identifikasi user yang sudah tidak aktif, test retensi notification
9. Latihan pitch dengan materi final
10. Rekam versi pitch terbaru
11. Share ke mentor/teman untuk feedback akhir
12. Dokumentasikan semua fitur yang sudah live
13. Update README dengan semua fitur terbaru
14. Push final update
15. Istirahat — preservasi energi untuk hari-hari terakhir

---

### 📅 Hari 27 — Minggu, 6 Juli 2026

#### 🤖 PROMPTING (15 tugas)
1. Generate final QA checklist: 50 poin yang harus dicek sebelum hari H
2. Generate regression test suite lengkap
3. Generate script otomatis: jalankan semua test sekali klik
4. Generate monitoring playbook: apa yang dilakukan jika X terjadi
5. Generate "day of presentation" checklist
6. Generate backup plan untuk setiap kemungkinan failure
7. Generate talking points update berdasarkan semua feedback yang diterima
8. Generate "so what" statement: dalam 1 kalimat, mengapa FallacyChecker penting?
9. Generate elevator pitch: 30 detik, 1 menit, 3 menit versi
10. Generate visual summary: 1 gambar yang merangkum keseluruhan proyek
11. Generate email follow-up template untuk post-presentasi
12. Generate LinkedIn connection message untuk semua juri
13. Generate thank you note template untuk organizer
14. Generate post-hackathon roadmap: apa yang akan dibangun bulan depan?
15. Generate "lessons learned" document

#### 🖐️ MANUAL (15 tugas)
1. Jalankan full QA checklist
2. Fix semua issue yang ditemukan
3. Final test semua submission links
4. Latihan pitch 5x berturut-turut
5. Rekam versi final pitch
6. Tonton ulang dengan kritis
7. Identifikasi 1-2 improvement terakhir
8. Implementasikan improvement tersebut
9. Rekam ulang jika perlu
10. Siapkan environment demo: browser, tab, akun sudah login
11. Simpan semua credential yang dibutuhkan saat demo
12. Setup backup hotspot internet
13. Catat contact semua juri untuk follow-up
14. Tidur cukup — persiapan mental
15. Visualisasikan presentasi yang sukses

---

### 📅 Hari 28 — Senin, 7 Juli 2026

#### 🤖 PROMPTING (15 tugas)
1. Generate last-minute bug fix untuk issue yang ditemukan QA
2. Generate hotfix deployment script: push fix tanpa downtime
3. Generate status page: `status.revonalar.com` untuk transparansi
4. Generate update tweet: "FallacyChecker live dan siap dicoba!"
5. Generate Product Hunt post draft (untuk launch setelah hackathon)
6. Generate press kit final: semua aset dalam 1 folder
7. Generate media brief: penjelasan untuk jurnalis non-teknis
8. Generate video teaser 30 detik untuk sosmed
9. Generate Instagram carousel: "5 Fallacy yang Paling Sering di YouTube"
10. Generate TikTok script: konten edukasi tentang logical fallacy
11. Generate partnership proposal untuk Zenius/Ruangguru
12. Generate proposal untuk Google for Startups / AWS Activate
13. Generate pitch untuk angel investor Indonesia
14. Generate financial model sederhana: break-even point
15. Generate 3-year vision document: Revonalar + FallacyChecker global

#### 🖐️ MANUAL (15 tugas)
1. Deploy semua hotfix
2. Verifikasi status page berfungsi
3. Post update sosmed: proyek live!
4. Monitor traffic: apakah ada lonjakan user?
5. Monitor AMD cloud: apakah resource cukup untuk traffic?
6. Balas semua komentar dari post
7. Compile semua angka final: user, analisis, uptime, benchmark
8. Siapkan slide untuk kemungkinan presentasi hari ini
9. Cek email untuk update dari lablab.ai
10. Engage di Discord lablab.ai: tunjukkan antusiasme
11. Screenshot semua statistik terkini
12. Update slide dengan angka terbaru
13. Final dress rehearsal pitch
14. Siapkan tempat presentasi yang nyaman dan tenang
15. Charge semua perangkat

---

### 📅 Hari 29 — Selasa, 8 Juli 2026

#### 🤖 PROMPTING (15 tugas)
1. Generate emergency hotfix jika ada bug terakhir
2. Generate presentasi versi 5 menit (jika dapat slot lebih panjang)
3. Generate presentasi versi 1 menit (lightning pitch)
4. Generate one-page summary PDF untuk dikirim ke juri via email
5. Generate follow-up email untuk setelah presentasi
6. Generate social proof update: kumpulkan semua feedback positif
7. Generate "traction update": angka growth sejak submission
8. Generate comparison: FallacyChecker vs solusi yang ada di pasar
9. Generate unique insight: sesuatu yang hanya FallacyChecker di AMD yang bisa
10. Generate final investor deck update
11. Generate post-hackathon blog post draft
12. Generate Twitter thread recap: 30 hari membangun FallacyChecker
13. Generate LinkedIn article: refleksi membangun AI product solo
14. Generate case study format: untuk website Revonalar
15. Generate thank you post untuk AMD dan lablab.ai

#### 🖐️ MANUAL (15 tugas)
1. Final check semua submission links
2. Final test demo environment
3. Latihan pitch 3x
4. Presentasi (jika hari ini jadwalnya)
5. Jika ada Q&A, catat semua pertanyaan dan jawaban
6. Screenshot/record semua momen presentasi
7. Follow up dengan juri di LinkedIn langsung setelah presentasi
8. Post real-time update di sosmed saat/setelah presentasi
9. Dokumentasikan pengalaman: catat semua yang dipelajari hari ini
10. Kirim one-page summary ke semua juri via email
11. Engage di Discord: share pengalaman
12. Tonton presentasi tim lain: beri komentar positif
13. Vote untuk proyek lain yang impressive
14. Istirahat sejenak — kamu sudah kerja keras
15. Rayakan progress yang sudah dicapai

---

### 📅 Hari 30 — Rabu, 10 Juli 2026
**Tema: Refleksi & Launch**

#### 🤖 PROMPTING (15 tugas)
1. Generate retrospektif dokumen: apa yang berjalan baik, apa yang tidak
2. Generate "next sprint" planning: fitur apa yang dibangun bulan depan
3. Generate technical debt list: semua yang perlu di-refactor
4. Generate user research questions: untuk wawancara user pertama
5. Generate growth hacking ideas: cara dapat 1000 user tanpa iklan
6. Generate content calendar: 30 hari konten sosmed post-hackathon
7. Generate newsletter template: update mingguan untuk subscriber
8. Generate community guidelines untuk forum FallacyChecker
9. Generate moderation workflow untuk konten yang dilaporkan
10. Generate internship brief: jika ingin rekrut developer muda
11. Generate academic paper outline: tentang FallacyChecker dan deteksi misinformasi
12. Generate grant application draft: untuk Kominfo atau lembaga riset
13. Generate KPI dashboard: metrik yang ditrack setiap minggu
14. Generate OKR untuk Q3 2026: objective dan key results
15. Generate celebration post: terima kasih kepada semua yang support

#### 🖐️ MANUAL (10 tugas)
1. Baca dan refleksikan 30 hari perjalanan ini
2. Tulis jurnal pribadi: apa yang paling berharga dipelajari?
3. Kirim pesan terima kasih ke semua orang yang membantu test
4. Post Twitter thread: "30 hari membangun FallacyChecker" (thread panjang)
5. Post LinkedIn article: refleksi mendalam
6. Setup monitoring untuk minggu pertama post-launch
7. Jadwalkan sesi user interview dengan 3 user pertama
8. Buat roadmap visual untuk bulan Juli-Agustus
9. Commit untuk bangun 1 fitur baru per minggu
10. 🎉 **Rayakan — kamu sudah selesaikan proyek serius pertama di hackathon internasional**

---

## 📊 Ringkasan Total Pekerjaan

| Periode | Hari | Prompting | Manual | Total |
|---|---|---|---|---|
| Fase 1: Fondasi | 10-13 Juni (4 hari) | 60 | 40 | 100 |
| Fase 2: Extension & UI | 14-17 Juni (4 hari) | 60 | 40 | 100 |
| Fase 3: Intensif Build | 18-20 Juni (3 hari) | 45 | 30 | 75 |
| Fase 4: Sprint | 21-30 Juni (10 hari) | 210+ | 90+ | 300 |
| Fase 5: Finalisasi | 1-10 Juli (10 hari) | 150 | 100 | 250 |
| **TOTAL** | **31 hari** | **525+** | **300+** | **825+** |

---

## 🏁 Kriteria Sukses

**Minimum untuk submit yang kuat:**
- [ ] FallacyChecker web app berjalan di AMD MI300X
- [ ] Model 70B+ deployed dengan vLLM
- [ ] Chrome Extension side panel berfungsi
- [ ] Pipeline YouTube URL → Fallacy terdeteksi
- [ ] Integrasi Revonalar: login, Diamond, history
- [ ] Demo video 2-3 menit yang clean
- [ ] Benchmark AMD yang bisa diklaim

**Bonus yang bikin menang:**
- [ ] RAG memori kolektif dengan Qdrant
- [ ] Batch processing 100 video < 30 detik
- [ ] Hugging Face Space dengan banyak likes
- [ ] Traction: user nyata yang sudah pakai

---

*Jadwal ini adalah panduan, bukan penjara. Fleksibel sesuai kebutuhan, tapi pastikan milestone utama tercapai.*

*Good luck, Bibong. Ini bukan sekadar hackathon — ini proof bahwa visi besar bisa dieksekusi dengan AI sebagai partner.*
