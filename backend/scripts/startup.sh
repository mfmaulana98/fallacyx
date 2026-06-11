#!/usr/bin/env bash
#
# startup.sh
#
# Bootstrap script untuk instance baru AMD Developer Cloud (MI300X).
# Dijalankan PERTAMA KALI setelah SSH ke instance yang baru di-provision.
#
# Tugas:
#   1. Cek versi ROCm & GPU (rocm-smi, hipcc --version)
#   2. Install Python 3.11, pip, git, ffmpeg, yt-dlp
#   3. Clone repo FallacyX dari GitHub
#   4. Install requirements dari backend/requirements.txt
#   5. Set environment variables dari file .env di root repo
#   6. Jalankan deploy_vllm.sh
#   7. Jalankan uvicorn app.main:app
#   8. Print IP publik instance
#
# Usage:
#   sudo REPO_URL=https://github.com/<org>/fallacyx.git HF_TOKEN=hf_xxx ./startup.sh
#
set -e

# ==========================================
# KONFIGURASI
# ==========================================
REPO_URL="${REPO_URL:-https://github.com/revonalar/fallacyx.git}"
REPO_BRANCH="${REPO_BRANCH:-main}"
REPO_DIR="${REPO_DIR:-/opt/fallacyx}"
PYTHON_BIN="python3.11"

log() {
	echo -e "\n[$(date '+%Y-%m-%d %H:%M:%S')] [startup] $*\n"
}

if [[ "$(id -u)" -ne 0 ]]; then
	echo "Script ini harus dijalankan sebagai root (gunakan sudo)." >&2
	exit 1
fi

# ==========================================
# 1. CEK ROCm & GPU
# ==========================================
log "1/8 Cek versi ROCm dan GPU..."

if command -v rocm-smi >/dev/null 2>&1; then
	rocm-smi --showproductname --showdriverversion
else
	log "PERINGATAN: rocm-smi tidak ditemukan. Pastikan driver ROCm sudah terpasang di image instance."
fi

if command -v hipcc >/dev/null 2>&1; then
	hipcc --version
else
	log "PERINGATAN: hipcc tidak ditemukan. Pastikan ROCm HIP SDK sudah terpasang di image instance."
fi

# ==========================================
# 2. INSTALL PYTHON 3.11, PIP, GIT, FFMPEG, YT-DLP
# ==========================================
log "2/8 Install Python 3.11, pip, git, ffmpeg, yt-dlp..."

apt-get update -y
apt-get install -y --no-install-recommends \
	software-properties-common \
	ca-certificates \
	curl \
	wget \
	gnupg

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
	add-apt-repository -y ppa:deadsnakes/ppa
	apt-get update -y
fi

apt-get install -y --no-install-recommends \
	"${PYTHON_BIN}" \
	"${PYTHON_BIN}-venv" \
	"${PYTHON_BIN}-dev" \
	python3-pip \
	git \
	ffmpeg

# yt-dlp: install via pip (selalu versi terbaru, tidak bergantung repo apt)
"${PYTHON_BIN}" -m pip install --upgrade pip
"${PYTHON_BIN}" -m pip install --upgrade yt-dlp

# ==========================================
# 3. CLONE REPO FALLACYX
# ==========================================
log "3/8 Clone repo FallacyX dari ${REPO_URL} (branch: ${REPO_BRANCH})..."

if [[ -d "${REPO_DIR}/.git" ]]; then
	log "Repo sudah ada di ${REPO_DIR}, pull update terbaru..."
	git -C "${REPO_DIR}" fetch origin
	git -C "${REPO_DIR}" checkout "${REPO_BRANCH}"
	git -C "${REPO_DIR}" pull origin "${REPO_BRANCH}"
else
	git clone --branch "${REPO_BRANCH}" "${REPO_URL}" "${REPO_DIR}"
fi

cd "${REPO_DIR}/backend"

# ==========================================
# 4. INSTALL REQUIREMENTS BACKEND
# ==========================================
log "4/8 Install dependencies dari requirements.txt..."

if [[ ! -d "venv" ]]; then
	"${PYTHON_BIN}" -m venv venv
fi

# shellcheck disable=SC1091
source venv/bin/activate

pip install --upgrade pip wheel setuptools
pip install -r requirements.txt

deactivate

# ==========================================
# 5. SET ENVIRONMENT VARIABLES DARI .env
# ==========================================
log "5/8 Load environment variables dari .env di root repo..."

ENV_FILE="${REPO_DIR}/.env"

if [[ -f "${ENV_FILE}" ]]; then
	set -o allexport
	# shellcheck disable=SC1090
	source "${ENV_FILE}"
	set +o allexport
	log "Environment variables berhasil di-load dari ${ENV_FILE}."
else
	log "PERINGATAN: ${ENV_FILE} tidak ditemukan, lanjut tanpa env tambahan."
fi

# ==========================================
# 6. JALANKAN deploy_vllm.sh
# ==========================================
log "6/8 Jalankan deploy_vllm.sh..."

bash "${REPO_DIR}/backend/scripts/deploy_vllm.sh"

# ==========================================
# 7. JALANKAN UVICORN
# ==========================================
log "7/8 Jalankan FastAPI server (uvicorn)..."

# shellcheck disable=SC1091
source venv/bin/activate

uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload &
UVICORN_PID=$!

# ==========================================
# 8. PRINT IP PUBLIK INSTANCE
# ==========================================
log "8/8 Mengambil IP publik instance..."

PUBLIC_IP="$(curl -fsSL ifconfig.me || curl -fsSL https://api.ipify.org || echo 'unknown')"

log "Selesai. FastAPI server berjalan dengan PID ${UVICORN_PID}."
log "Akses backend di: http://${PUBLIC_IP}:8080"
log "vLLM server di:    http://${PUBLIC_IP}:${VLLM_PORT:-8000}/v1"

wait "${UVICORN_PID}"
