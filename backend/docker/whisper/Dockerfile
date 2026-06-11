# =============================================================================
# FallacyX — Whisper (faster-whisper) speech-to-text service for ROCm
# =============================================================================
FROM rocm/pytorch:latest

WORKDIR /app

RUN pip install --no-cache-dir \
    faster-whisper \
    fastapi \
    "uvicorn[standard]"

COPY app/ /app/

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
