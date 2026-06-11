# CLAUDE.md — FallacyX Blueprint & Visual Branding Guide

Proyek: FallacyX — fitur baru di platform Revonalar
Stack: SvelteKit + Tailwind CSS + Supabase (frontend), FastAPI + Python (backend),
vLLM + Llama-3-70B di AMD MI300X (inference), Qdrant (vector DB)
Deploy: Cloudflare Pages (frontend), AMD Developer Cloud (backend)
Tujuan: Real-time logical fallacy detector untuk teks, URL artikel, YouTube, dan audio
Bahasa: Inggris

Ini adalah panduan visual yang harus selalu diikuti ketika membuat,
memodifikasi, atau mengevaluasi komponen UI apapun di proyek ini.
Tidak ada pengecualian kecuali ada instruksi eksplisit dari user.

---

## IDENTITAS VISUAL

FallacyX memiliki gaya yang sangat spesifik: **Glassmorphism + Classical Editorial**.
Bukan salah satu, tapi keduanya digabung dengan cara yang tidak lazim.

Referensi utama di F:\Projects\fallacyx\docs\visual-branding\FallacyChecker.html

- Classical = tipografi broadsheet, numbering Latin, tone serius seperti dokumen hukum
- Glassmorphism = nav transparan dengan backdrop-blur, dark sections dengan radial glow, floating chips

Jangan pernah membuat komponen yang terasa "modern SaaS biasa" (biru indigo, rounded corners besar, gradient pastel).
Jangan pernah membuat komponen yang terasa "koran lama saja" tanpa elemen glass/blur/glow.
Keduanya harus hadir.

---

## COLOR PALETTE — WAJIB PAKAI CSS VARIABLES INI

```css
:root {
	/* Backgrounds */
	--bg: #f5f4f0; /* Krem hangat — background utama seluruh halaman */
	--surface: #ffffff; /* Putih bersih — card, console, panel */
	--surface-2: #efede7; /* Krem lebih gelap — input bg, nested card */

	/* Text */
	--ink: #15141a; /* Hampir hitam — teks utama, heading */
	--ink-2: #46444e; /* Abu gelap — body text, deskripsi */
	--muted: #8c8a93; /* Abu muted — label, meta, placeholder */

	/* Borders */
	--line: rgba(21, 20, 26, 0.1); /* Border tipis, subtle */
	--line-2: rgba(21, 20, 26, 0.16); /* Border sedikit lebih tegas */

	/* Brand */
	--red: #da2b22; /* Merah utama — CTA, accent, fallacy badge */
	--red-deep: #a4161a; /* Merah gelap — hover state, blockquote border */
	--red-soft: rgba(218, 43, 34, 0.1); /* Merah transparan — pill bg, highlight */
	--green: #159a5b; /* Hijau — "tidak ada fallacy", success state */

	/* Dark sections */
	--dark: #121016; /* Background section gelap */
	--dark-2: #1b1822; /* Alternatif dark lebih terang */
	--on-dark: #f4f2ee; /* Teks di atas dark bg */
	--on-dark-mut: rgba(244, 242, 238, 0.62); /* Teks muted di atas dark bg */

	/* Shadows */
	--shadow: 0 1px 2px rgba(21, 20, 26, 0.04), 0 24px 50px -30px rgba(21, 20, 26, 0.3);
	--shadow-lg: 0 2px 4px rgba(21, 20, 26, 0.05), 0 40px 80px -40px rgba(21, 20, 26, 0.4);

	/* Radius */
	--r: 22px; /* Border radius standar untuk card */
}
```

**Larangan:**

- Jangan pakai warna biru, ungu, atau indigo untuk apapun
- Jangan pakai warna-warna di luar palette ini kecuali varian opacity dari warna yang sudah ada
- Jangan pakai white (#fff) sebagai background halaman — selalu gunakan `--bg`

---

## TIPOGRAFI — TIGA FONT, TIGA PERAN

### 1. Archivo — Font Utama

```css
font-family: 'Archivo', system-ui, sans-serif;
```

- Dipakai untuk: body text, navigation, button, label, semua teks UI
- Heading weight: 800–900
- Body weight: 400–500
- Letter spacing heading: `-0.025em` sampai `-0.04em` (ketat, bukan renggang)
- Line height heading: `1.02`

### 2. Playfair Display — Aksen Serif Italic

```css
font-family: 'Playfair Display', serif;
font-style: italic;
font-weight: 600;
```

- Dipakai untuk: kata/frasa yang ingin di-emphasize di heading, blockquote, pull quote, loading message
- TIDAK dipakai untuk: body text panjang, label, button
- Selalu italic, tidak pernah upright
- Contoh penggunaan: `Every tyranny began as a sentence <em class="serif">nobody questioned.</em>`

### 3. Space Mono — Font Data & Label

```css
font-family: 'Space Mono', monospace;
```

- Dipakai untuk: kicker/label di atas heading, metadata, confidence score, nomor statistik, timestamp, tag teknikal
- Selalu uppercase dengan letter-spacing lebar: `letter-spacing: .16em` sampai `.24em`
- Font size: 9px–13px, tidak pernah lebih besar (9px–10px hanya untuk label kecil seperti subtitle brand/logo)
- Contoh penggunaan: `CONFIDENCE 0.93`, `CASE NO. RVN-2026-0609`, `FREE COURSE · I`

**Aturan font yang tidak boleh dilanggar:**

- Jangan pakai Playfair Display untuk teks yang bukan aksen/emphasis
- Jangan pakai Space Mono untuk kalimat panjang
- Jangan pakai font lain selain ketiga ini

---

## KOMPONEN KUNCI & CARA MEMBUATNYA

### Navbar

```
- Sticky, top-0
- Background: rgba(245,244,240,.78) — semi-transparan, BUKAN putih solid
- backdrop-filter: blur(18px) — ini glassmorphism-nya
- Border bottom: 1px solid var(--line)
- Tinggi: 74px
- Logo: kotak hitam kecil dengan titik merah di pojok kanan bawah
- CTA button: background var(--red), rounded pill
```

### Card

```
- Background: var(--surface)
- Border: 1px solid var(--line)
- Border-radius: var(--r) = 22px
- Box-shadow: var(--shadow)
- Hover: translateY(-4px) + shadow-lg
- JANGAN pakai gradient di card biasa
```

### Dark Section (glassmorphism touch)

```
- Background: var(--dark)
- Border-radius: 34px — lebih besar dari card biasa
- Margin horizontal: 32px — mengambang, tidak full-width
- Radial glow merah di sudut: rgba(218,43,34,.34)
- Elemen di dalamnya pakai .glass class:
  background: rgba(244,242,238,.05)
  border: 1px solid rgba(244,242,238,.12)
  backdrop-filter: blur(8px)
```

### Button

```
Primary (red):
  background: var(--red)
  border-radius: 100px (pill)
  box-shadow: 0 8px 22px -8px rgba(218,43,34,.7)
  hover: translateY(-2px)

Secondary (dark):
  background: var(--ink)
  hover: background #000

Ghost:
  border: 1.5px solid var(--line-2)
  hover: background var(--ink), color white

Ghost on dark bg:
  border: rgba(244,242,238,.28)
  hover: background var(--on-dark), color var(--ink)
```

### Kicker / Label di Atas Heading

```
font-family: Space Mono
font-size: 12px
letter-spacing: .24em
text-transform: uppercase
color: var(--red)
```

Contoh: `THE MANIFESTO OF CLEAR THINKING`, `SECTION IV · THE EXAMINATION`

### Fallacy Card (hasil deteksi)

```
- Card itu sendiri: border-bottom 1px solid var(--line) (bukan border kiri)
- Nomor urut dengan Space Mono: "01 · Ad Hominem"
- Quote teks (excerpt) dalam Playfair italic, background var(--surface-2),
  border-left: 3px solid var(--red), border-radius 0 12px 12px 0
- Confidence score dengan Space Mono merah + bar merah
- Label "WHY IT BREAKS" dengan Space Mono uppercase muted
- Box "fix" (saran perbaikan): background var(--red-soft), border-radius 14px
```

### Input / Textarea

```
- Background: var(--surface-2)
- Border: 1.5px solid var(--line)
- Border-radius: 16px
- Focus: border-color var(--red), background #fff
- Font: Archivo, 1.06rem
```

### Tab Navigation (di dalam console/card)

```
- Default: warna muted, background transparent
- Active: warna ink, background surface-2, box-shadow inset bottom merah
- Border radius: 14px 14px 0 0
- Icon SVG (bukan dot) di depan label setiap tab
```

---

## ELEMEN GLASSMORPHISM YANG HARUS ADA

Glassmorphism di FallacyX bukan "semua pakai glass" — hanya pada elemen tertentu:

1. **Navbar** — selalu semi-transparan dengan blur
2. **Dark sections** — floating dengan corner glow
3. **Nested cards di dark section** — glass effect dengan low-opacity border
4. **Floating chips** — shadow + border tipis, terasa mengambang
5. **Radial glow di background** — merah transparan di hero dan dark section

Yang TIDAK boleh pakai glass: card biasa, button, input, tabel, list item.

---

## ELEMEN CLASSICAL EDITORIAL YANG HARUS ADA

1. **Kicker text** — Space Mono uppercase sebelum heading utama
2. **Playfair italic** — pada kata kunci di heading besar
3. **Numbering Latin** — "01 · 02 · 03" bukan bullet points
4. **Divider lines** — `border-bottom: 1px solid var(--line)` antara section
5. **Pull quotes** — Playfair italic besar dengan border kiri merah
6. **Broadsheet layout feel** — grid kolom dengan gutter, bukan card penuh lebar
7. **Tone bahasa UI** — serius, seperti dokumen hukum atau koran
   - Bukan: "Analyze your text"
   - Iya: "Submit an argument. Receive a verdict."
   - Bukan: "3 errors found"
   - Iya: "3 Fallacies Found · SUBSTANTIAL"

---

## ANIMASI & MOTION

```css
/* Hover card */
transition: transform .2s, box-shadow .2s;
hover: translateY(-4px)

/* Hover button */
transition: transform .15s ease, box-shadow .2s;
hover: translateY(-2px)

/* Page in */
@keyframes pagein {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: none; }
}

/* Pulse (live indicator) */
@keyframes pulse {
  0%   { box-shadow: 0 0 0 0 rgba(218,43,34,.5); }
  70%  { box-shadow: 0 0 0 9px rgba(218,43,34,0); }
  100% { box-shadow: 0 0 0 0 rgba(218,43,34,0); }
}

/* Floating chips */
@keyframes float1 {
  0%,100% { transform: rotate(-5deg) translateY(0); }
  50%      { transform: rotate(-5deg) translateY(-9px); }
}
```

Selalu wrap animasi dalam `@media (prefers-reduced-motion: no-preference)`.

---

## LAYOUT & SPACING

```
Max width: 1240px, center dengan margin: 0 auto
Padding horizontal: 32px
Section padding: 88px 0
Gap grid: 22px (standar), 54px (hero/manifesto)
Border radius: 22px (card), 34px (dark section), 100px (pill/button), 16px (input/textarea), 14px (tab atas)
```

---

## TONE BAHASA UI

FallacyX bukan "tool" biasa. Dia adalah **tribunal logika**. Bahasa UI harus mencerminkan ini:

| ❌ Jangan  | ✅ Gunakan                |
| ---------- | ------------------------- |
| Analyze    | Submit for Examination    |
| Results    | The Verdict               |
| Error      | Fallacy Found             |
| Loading... | Examining the argument... |
| 3 issues   | 3 Fallacies · SUBSTANTIAL |
| Submit     | File the Argument         |
| Check      | Examine                   |

Untuk label metadata gunakan format "koran lama":

- `CASE NO. RVN-2026-0609`
- `FILED: 09 JUNE 2026`
- `THE PEOPLE'S TRIBUNAL OF LOGIC`
- `SECTION IV · THE EXAMINATION`

---

## CHECKLIST SEBELUM SUBMIT KODE UI

Sebelum selesai membuat komponen apapun, pastikan:

- [ ] Warna hanya dari palette CSS variables di atas
- [ ] Heading pakai Archivo bold + Playfair italic untuk aksen
- [ ] Label/metadata pakai Space Mono uppercase
- [ ] Card punya border `var(--line)` dan shadow `var(--shadow)`
- [ ] Tidak ada warna biru/ungu/indigo
- [ ] Dark section pakai radial glow merah
- [ ] Nav pakai backdrop-filter blur
- [ ] Animasi dibungkus `prefers-reduced-motion`
- [ ] Tone bahasa serius, editorial, bukan casual SaaS
- [ ] Background halaman `var(--bg)` bukan white

---

## REFERENSI FILE

File HTML referensi yang bisa dilihat untuk contoh implementasi lengkap:

- `FallacyChecker.html` — versi utama dengan glassmorphism penuh
- `FallacyChecker (broadsheet v1).html` — versi editorial klasik
- `screenshots/` — visual reference per section

Ketika ragu, **lihat dulu HTML referensi** sebelum generate kode baru.

---

### Struktur folder lengkap untuk proyek FallacyX dengan dua bagian utama:

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
