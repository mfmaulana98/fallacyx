# 🖐️ Hari 0 + Hari 1 — Panduan Manual
## FallacyX | Non-Developer Friendly

> **Konvensi:**
> 🔴 Wajib — tanpa ini tidak bisa lanjut
> 🟡 Penting — sebaiknya diselesaikan hari ini
> 🟢 Opsional — bisa dikerjakan nanti

---

## HARI 0 — Sebelum Mulai Coding
### "Semua akun dan tools aktif"

---

### M0.1 — AMD AI Developer Program 🔴
**Tujuan:** Dapatkan $100 credits untuk AMD Developer Cloud (MI300X)

1. Buka https://developer.amd.com/amd-ai-developer-program/
2. Klik **Join Now** atau **Sign Up**
3. Isi form dengan data lengkap — pilih kategori **Independent Developer**
4. Verifikasi email
5. Setelah approved, cek apakah ada dashboard atau link ke AMD Developer Cloud
6. Catat: **username, password, dan kode credits** yang diberikan

> ⚠️ Approval kadang tidak instan. Daftar sekarang meski belum mulai coding.
> Kalau ada form tentang use case, tulis: *"Building real-time logical fallacy 
> detection system using LLM inference for AMD Developer Hackathon ACT II"*

---

### M0.2 — AMD Developer Cloud — Verifikasi Akses MI300X 🔴
**Tujuan:** Pastikan kamu bisa spin up instance GPU AMD

1. Setelah dapat akses, login ke AMD Developer Cloud
2. Cari menu **Instances** atau **Compute**
3. Coba buat instance baru — pilih yang ada **MI300X**
4. Jangan langsung jalankan kalau belum tahu biayanya — cukup verifikasi pilihan tersedia
5. Cek: apakah $100 credits sudah terapply ke akun?
6. Screenshot halaman dashboard yang menunjukkan credits tersedia

> 💡 AMD Developer Cloud berbeda dengan AMD website biasa.
> Link yang benar biasanya diberikan setelah join developer program.
> Kalau bingung, cek email setelah registrasi — biasanya ada link khusus.

---

### M0.3 — Enroll lablab.ai AMD Hackathon ACT II 🔴
**Tujuan:** Resmi terdaftar sebagai peserta

1. Buka https://lablab.ai/ai-hackathons/amd-developer-hackathon-act-ii
2. Klik **Participate** atau **Join Hackathon**
3. Buat akun lablab.ai jika belum ada (bisa login dengan Google)
4. Pilih **Create Team** → nama tim: **Revonalar** (atau nama lain)
5. Karena solo, tidak perlu invite anggota lain
6. Verifikasi bahwa nama tim dan proyekmu sudah terdaftar
7. Screenshot halaman konfirmasi pendaftaran

---

### M0.4 — Hugging Face Account 🟡
**Tujuan:** Platform wajib untuk submit demo Space (salah satu penilaian hackathon)

1. Buka https://huggingface.co
2. Klik **Sign Up**
3. Username yang disarankan: `revonalar` atau `mfmaulana98`
4. Verifikasi email
5. Setup profil: foto, bio singkat, link ke GitHub
6. Buat **Organization** baru: `revonalar`
   - Settings → Organizations → New Organization
   - Ini agar Space nanti terlihat profesional: `huggingface.co/revonalar/fallacyx`
7. Screenshot halaman profil yang sudah jadi

---

### M0.5 — GitHub Repository Setup 🔴
**Tujuan:** Tempat semua kode FallacyX disimpan

1. Login ke GitHub dengan akun Revonalar (`mfmaulana98` atau akun yang sesuai)
2. Klik **New Repository**
3. Isi:
   - Repository name: `fallacyx`
   - Description: *"Real-time logical fallacy detector powered by AMD MI300X"*
   - Visibility: **Public** (wajib untuk hackathon)
   - ✅ Add README
   - ✅ Add .gitignore → pilih **Node**
   - License: **MIT**
4. Klik **Create Repository**
5. Copy URL repo: `https://github.com/mfmaulana98/fallacyx`

Setelah repo terbuat, setup di laptop:
```powershell
cd F:\Projects
git clone https://github.com/mfmaulana98/fallacyx.git
cd fallacyx
git config --local user.name "mfmaulana98"
git config --local user.email "email-revonalar@gmail.com"
```

> 💡 Clone repo yang sudah ada lebih clean daripada `git init` dari nol,
> karena README dan .gitignore sudah terbuat otomatis di GitHub.

---

### M0.6 — Supabase — Pastikan Project Revonalar Bisa Dipakai 🔴
**Tujuan:** FallacyX share database dengan Revonalar

1. Login ke https://supabase.com/dashboard
2. Buka project Revonalar (`bfhjknbboxhsxbwnmjov`)
3. Cek **Table Editor** — pastikan database masih aktif dan bisa diakses
4. Pergi ke **Settings → API**
5. Catat (simpan di password manager):
   - Project URL: `https://bfhjknbboxhsxbwnmjov.supabase.co`
   - `anon` public key
   - `service_role` secret key ← **jangan share ini ke siapapun**
6. Pergi ke **Authentication → URL Configuration**
7. Tambahkan ke **Redirect URLs**:
   ```
   http://localhost:5174/auth/callback
   https://fallacyx.revonalar.com/auth/callback
   ```
8. Klik **Save**

> ⚠️ Kalau tidak tambahkan redirect URL, login di FallacyX akan error
> meski pakai Supabase yang sama dengan Revonalar.

---

### M0.7 — Password Manager untuk Semua Credentials 🟡
**Tujuan:** Semua credential tersimpan aman, tidak hilang

Buat folder/vault baru di password manager (Bitwarden, 1Password, atau Notion private):

```
📁 FallacyX — AMD Hackathon

AMD Developer Cloud
  - URL: 
  - Username: 
  - Password: 
  - Credits code: 

Supabase (Revonalar project)
  - Project URL: https://bfhjknbboxhsxbwnmjov.supabase.co
  - Anon Key: 
  - Service Role Key: 

GitHub
  - Repo URL: 
  - Username: 

Hugging Face
  - Username: 
  - Token: (generate di HF Settings → Access Tokens)

lablab.ai
  - Email: 
  - Team name: 

Cloudflare
  - Account ID: 
  - API Token: (buat nanti saat setup Pages)
```

---

### M0.8 — Buat Tracking Progress 🟢
**Tujuan:** Tidak kehilangan jejak apa yang sudah dan belum dikerjakan

Pilih salah satu:

**Opsi A — Notion (disarankan):**
1. Buat page baru: "FallacyX — AMD Hackathon 2026"
2. Buat database dengan kolom: Tugas | Status | Tanggal | Catatan
3. Import checklist dari file jadwal 30 hari

**Opsi B — GitHub Issues:**
1. Di repo fallacyx, buka tab **Issues**
2. Buat issue per milestone besar
3. Pakai **Projects** tab untuk kanban board

**Opsi C — File MD di repo:**
1. Buat `PROGRESS.md` di repo
2. Update setiap hari dengan apa yang selesai

---

## HARI 1 — Setup Proyek FallacyX
### "Kerangka proyek berdiri"

---

### M1.1 — Init Proyek SvelteKit 🔴

```powershell
cd F:\Projects\fallacyx

# Jika clone dari GitHub (ada file README), hapus dulu isinya:
# Cukup biarkan, pnpm create akan merge

pnpm create svelte@latest .
```

Saat ditanya pilihan:
```
Which Svelte app template?          → Skeleton project
Add type checking?                  → Yes, using TypeScript syntax
Add ESLint?                         → Yes
Add Prettier?                       → Yes
Add Playwright?                     → No (tidak perlu untuk hackathon)
Add Vitest?                         → No (tidak perlu untuk hackathon)
```

Setelah selesai:
```powershell
pnpm install
```

Test apakah berjalan:
```powershell
pnpm dev --port 5174
```

Buka browser: `http://localhost:5174` — harus muncul halaman SvelteKit default.

---

### M1.2 — Install Dependency Tambahan 🔴

```powershell
# Tailwind CSS
pnpm install -D tailwindcss postcss autoprefixer
pnpm dlx tailwindcss init -p

# Supabase
pnpm install @supabase/supabase-js @supabase/ssr

# Cloudflare adapter
pnpm install -D @sveltejs/adapter-cloudflare

# Utilities
pnpm install clsx date-fns lucide-svelte
```

---

### M1.3 — Buat File .env 🔴

Di root folder `fallacyx`, buat file baru bernama `.env`:

```powershell
# Buat file .env kosong dulu
New-Item .env -ItemType File
```

Buka `.env` di VS Code, isi dengan:
```
PUBLIC_SUPABASE_URL=https://bfhjknbboxhsxbwnmjov.supabase.co
PUBLIC_SUPABASE_ANON_KEY=[copy dari Supabase dashboard]
SUPABASE_SERVICE_ROLE_KEY=[copy dari Supabase dashboard]

PRIVATE_AMD_API_URL=http://localhost:8080
PRIVATE_AMD_API_KEY=

PUBLIC_APP_URL=http://localhost:5174
PUBLIC_APP_NAME=FallacyX
```

Verifikasi `.gitignore` sudah ada baris `.env`:
```powershell
# Cek isi .gitignore
cat .gitignore
# Pastikan ada baris: .env
# Kalau belum ada:
echo ".env" >> .gitignore
```

---

### M1.4 — Verifikasi Supabase Connection 🔴
**Tujuan:** Pastikan FallacyX bisa connect ke database Revonalar

Setelah file Supabase client dibuat (dari tugas prompting), test koneksi:

1. Buka `http://localhost:5174`
2. Coba login dengan akun yang sudah ada di Revonalar
3. Jika berhasil → Supabase connection OK ✅
4. Jika error `invalid redirect` → cek M0.6 langkah 7-8
5. Jika error `invalid API key` → cek nilai di `.env`

---

### M1.5 — Jalankan Migration SQL di Supabase 🔴
**Tujuan:** Buat tabel baru untuk FallacyX tanpa merusak tabel Revonalar

1. Login ke https://supabase.com/dashboard
2. Buka project Revonalar
3. Klik **SQL Editor** di sidebar kiri
4. Klik **New Query**
5. Copy-paste isi file `supabase/migrations/001_fallacy_tables.sql`
   (hasil dari tugas prompting M1 Tugas 5)
6. Klik **Run** (atau Ctrl+Enter)
7. Pastikan output: `Success. No rows returned`
8. Ulangi untuk `002_user_history.sql`
9. Verifikasi di **Table Editor**: tabel baru harus muncul:
   - `fallacy_analyses`
   - `fallacy_vectors`
   - `fallacy_feedback`
   - `user_fallacy_stats`
   - `fallacy_achievements`

> ⚠️ Jangan jalankan migration yang sama dua kali — akan error karena
> tabel sudah ada. Kalau perlu ulang, jalankan `DROP TABLE nama_tabel CASCADE` dulu.

---

### M1.6 — Push Kode Pertama ke GitHub 🟡

```powershell
cd F:\Projects\fallacyx

git add .
git commit -m "feat: initial SvelteKit setup with Tailwind + Supabase"
git push origin main
```

Buka GitHub repo, verifikasi semua file sudah terupload.
Pastikan file `.env` **tidak ikut terupload** — cek di GitHub, tidak boleh ada file `.env`.

---

### M1.7 — Screenshot AMD Dashboard 🟢
**Tujuan:** Bukti visual untuk slide presentasi hackathon

Screenshot yang perlu diambil hari ini:
1. AMD Developer Cloud dashboard — tampilkan credits tersisa ($100)
2. Halaman pilihan instance — tunjukkan MI300X tersedia
3. lablab.ai — halaman konfirmasi terdaftar di hackathon
4. GitHub repo fallacyx — tampilkan repo sudah public

Simpan semua screenshot di folder:
```
F:\Projects\fallacyx\assets\hackathon-proof\
```

---

### M1.8 — Setup Hugging Face Space (Placeholder) 🟢
**Tujuan:** Buat Space sekarang meski belum ada konten — biar URL sudah ready

1. Login ke https://huggingface.co
2. Klik **+** → **New Space**
3. Isi:
   - Owner: `revonalar` (organization)
   - Space name: `fallacyx`
   - License: MIT
   - SDK: **Gradio** (paling mudah untuk demo nanti)
   - Visibility: **Public**
4. Klik **Create Space**
5. URL kamu sekarang: `https://huggingface.co/spaces/revonalar/fallacyx`
6. Untuk sekarang biarkan kosong — akan diisi nanti saat demo siap

---

## ✅ Checklist Hari 0 + Hari 1

### Hari 0
- [ ] M0.1 — AMD Developer Program: terdaftar + dapat credits
- [ ] M0.2 — AMD Developer Cloud: bisa akses, verifikasi MI300X tersedia
- [ ] M0.3 — lablab.ai: terdaftar di hackathon
- [ ] M0.4 — Hugging Face: akun + organization `revonalar` aktif
- [ ] M0.5 — GitHub repo `fallacyx` dibuat + di-clone ke laptop
- [ ] M0.6 — Supabase: redirect URL ditambahkan
- [ ] M0.7 — Semua credentials tersimpan di password manager
- [ ] M0.8 — Tracking progress setup (Notion/GitHub Projects)

### Hari 1
- [ ] M1.1 — SvelteKit init berhasil, `pnpm dev` jalan di port 5174
- [ ] M1.2 — Semua dependency terinstall tanpa error
- [ ] M1.3 — File `.env` terisi dan **tidak** masuk `.gitignore`
- [ ] M1.4 — Login Supabase berhasil dari FallacyX
- [ ] M1.5 — 5 tabel baru muncul di Supabase Table Editor
- [ ] M1.6 — Kode pertama berhasil di-push ke GitHub
- [ ] M1.7 — Screenshot AMD dashboard tersimpan
- [ ] M1.8 — Hugging Face Space placeholder aktif

---

## 🚨 Troubleshooting Umum

**`pnpm` tidak dikenali setelah install:**
```powershell
# Restart PowerShell, atau jalankan:
$env:Path += ";$env:APPDATA\npm"
```

**`pnpm dev` error setelah install Tailwind:**
Pastikan `app.css` sudah ada `@tailwind` directives dan
`svelte.config.js` sudah include `vitePreprocess()`.

**Supabase login redirect error:**
Pastikan `http://localhost:5174/auth/callback` sudah ditambahkan
di Supabase Dashboard → Authentication → URL Configuration.

**Git push ditolak:**
```powershell
# Jika repo di GitHub sudah ada README (conflict):
git pull origin main --allow-unrelated-histories
git push origin main
```

**AMD Developer Cloud tidak muncul opsi MI300X:**
Credits mungkin belum aktif. Tunggu 1-2 jam setelah registrasi,
atau cek email dari AMD untuk konfirmasi aktivasi.
