#!/usr/bin/env bash
#
# deploy_vllm.sh
#
# Deploy vLLM (ROCm backend) untuk Llama-3-70B-Instruct di AMD MI300X.
# Idempotent: aman dijalankan berulang kali tanpa merusak state yang sudah ada.
#
# Usage:
#   sudo HF_TOKEN=hf_xxx ./deploy_vllm.sh
#
set -euo pipefail

# ==========================================
# KONFIGURASI
# ==========================================
MODEL_NAME="${VLLM_MODEL_NAME:-meta-llama/Meta-Llama-3-70B-Instruct}"
MODEL_DIR="/models/${MODEL_NAME}"
VENV_DIR="${VLLM_VENV_DIR:-/opt/vllm-venv}"
SERVICE_USER="${VLLM_SERVICE_USER:-vllm}"
SERVICE_NAME="vllm"
VLLM_PORT="${VLLM_PORT:-8000}"
HF_TOKEN="${HF_TOKEN:-}"

# Konfigurasi runtime vLLM, dioptimalkan untuk MI300X 192GB VRAM
VLLM_TENSOR_PARALLEL_SIZE=1
VLLM_MAX_MODEL_LEN=8192
VLLM_GPU_MEMORY_UTILIZATION=0.85
VLLM_DTYPE="bfloat16"

log() {
	echo -e "\n[deploy_vllm] $*\n"
}

if [[ "$(id -u)" -ne 0 ]]; then
	echo "Script ini harus dijalankan sebagai root (gunakan sudo)." >&2
	exit 1
fi

# ==========================================
# 1. UPDATE SISTEM & INSTALL ROCm DEPENDENCIES
# ==========================================
log "1/5 Update sistem dan install ROCm dependencies..."

apt-get update -y
apt-get upgrade -y

# Paket dasar yang dibutuhkan untuk build & download
apt-get install -y --no-install-recommends \
	build-essential \
	curl \
	wget \
	git \
	python3 \
	python3-venv \
	python3-pip \
	ca-certificates \
	gnupg

# Install ROCm hanya jika belum terpasang (cek via rocminfo)
if ! command -v rocminfo >/dev/null 2>&1; then
	log "ROCm belum terdeteksi, menginstall ROCm..."

	ROCM_VERSION="${ROCM_VERSION:-6.1}"
	UBUNTU_CODENAME="$(. /etc/os-release && echo "${UBUNTU_CODENAME:-${VERSION_CODENAME}}")"

	# Tambahkan ROCm apt repo (idempotent: overwrite key & list file)
	mkdir -p /etc/apt/keyrings
	curl -fsSL https://repo.radeon.com/rocm/rocm.gpg.key \
		| gpg --dearmor --yes -o /etc/apt/keyrings/rocm.gpg

	echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/rocm.gpg] https://repo.radeon.com/rocm/apt/${ROCM_VERSION} ${UBUNTU_CODENAME} main" \
		> /etc/apt/sources.list.d/rocm.list

	apt-get update -y
	apt-get install -y --no-install-recommends rocm-hip-sdk rocm-utils

	# Tambahkan service user ke group render & video agar bisa akses GPU
	usermod -a -G render,video "$(logname 2>/dev/null || echo "${SUDO_USER:-root}")" || true
else
	log "ROCm sudah terpasang, skip instalasi."
fi

# ==========================================
# 2. INSTALL vLLM DENGAN ROCm BACKEND
# ==========================================
log "2/5 Install vLLM dengan ROCm backend..."

# Buat virtualenv khusus jika belum ada
if [[ ! -d "${VENV_DIR}" ]]; then
	python3 -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

pip install --upgrade pip wheel setuptools

# Install PyTorch build untuk ROCm jika belum ada / belum versi ROCm
if ! python -c "import torch; assert 'rocm' in torch.__version__ or torch.version.hip is not None" >/dev/null 2>&1; then
	pip install --index-url https://download.pytorch.org/whl/rocm6.1 \
		torch torchvision torchaudio
fi

# Install vLLM dengan ROCm backend jika belum ada
if ! python -c "import vllm" >/dev/null 2>&1; then
	pip install "vllm[rocm]" --extra-index-url https://download.pytorch.org/whl/rocm6.1
else
	log "vLLM sudah terpasang, skip instalasi."
fi

deactivate

# ==========================================
# 3. PULL MODEL LLAMA-3-70B-INSTRUCT KE /models/
# ==========================================
log "3/5 Download model ${MODEL_NAME} ke ${MODEL_DIR}..."

mkdir -p /models

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

# Pastikan huggingface_hub tersedia untuk download model
if ! python -c "import huggingface_hub" >/dev/null 2>&1; then
	pip install -U "huggingface_hub[cli]"
fi

if [[ -n "${HF_TOKEN}" ]]; then
	huggingface-cli login --token "${HF_TOKEN}" --add-to-git-credential || true
fi

# Skip download jika model sudah lengkap (idempotent)
if [[ -d "${MODEL_DIR}" ]] && find "${MODEL_DIR}" -name "*.safetensors" -print -quit | grep -q .; then
	log "Model sudah ada di ${MODEL_DIR}, skip download."
else
	huggingface-cli download "${MODEL_NAME}" \
		--local-dir "${MODEL_DIR}" \
		--local-dir-use-symlinks False
fi

deactivate

# ==========================================
# 4. SETUP SYSTEMD SERVICE UNTUK vLLM SERVER
# ==========================================
log "4/5 Setup systemd service untuk vLLM server..."

# Buat service user khusus jika belum ada
if ! id "${SERVICE_USER}" >/dev/null 2>&1; then
	useradd --system --no-create-home --shell /usr/sbin/nologin \
		-G render,video "${SERVICE_USER}"
fi

chown -R "${SERVICE_USER}":"${SERVICE_USER}" "${MODEL_DIR}"

cat > "/etc/systemd/system/${SERVICE_NAME}.service" <<EOF
[Unit]
Description=vLLM OpenAI-compatible inference server (${MODEL_NAME})
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${SERVICE_USER}
Group=${SERVICE_USER}
Environment="HIP_VISIBLE_DEVICES=0"
Environment="VLLM_LOGGING_LEVEL=INFO"
ExecStart=${VENV_DIR}/bin/python -m vllm.entrypoints.openai.api_server \\
	--model ${MODEL_DIR} \\
	--served-model-name ${MODEL_NAME} \\
	--host 0.0.0.0 \\
	--port ${VLLM_PORT} \\
	--tensor-parallel-size ${VLLM_TENSOR_PARALLEL_SIZE} \\
	--max-model-len ${VLLM_MAX_MODEL_LEN} \\
	--gpu-memory-utilization ${VLLM_GPU_MEMORY_UTILIZATION} \\
	--dtype ${VLLM_DTYPE}

# Restart otomatis jika crash
Restart=always
RestartSec=10
StartLimitIntervalSec=0

# Hardening dasar
NoNewPrivileges=true
ProtectSystem=full

[Install]
WantedBy=multi-user.target
EOF

# ==========================================
# 5. ENABLE & START SERVICE
# ==========================================
log "5/5 Enable dan start service ${SERVICE_NAME}..."

systemctl daemon-reload
systemctl enable "${SERVICE_NAME}"
systemctl restart "${SERVICE_NAME}"

log "Selesai. Cek status dengan: systemctl status ${SERVICE_NAME}"
log "Cek log dengan: journalctl -u ${SERVICE_NAME} -f"
log "Server vLLM akan tersedia di http://0.0.0.0:${VLLM_PORT}/v1"
