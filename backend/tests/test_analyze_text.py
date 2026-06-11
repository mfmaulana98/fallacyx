"""Unit tests for POST /analyze/text."""

from __future__ import annotations

import json

import pytest

from app.services.vllm_service import VLLMTimeoutError

ENDPOINT = "/analyze/text"


def _vllm_payload(fallacies: list[dict] | None = None, overall_assessment: str = "", logic_score: int = 100) -> str:
    """Build a raw JSON string mimicking a vLLM completion response."""

    return json.dumps(
        {
            "fallacies": fallacies or [],
            "overall_assessment": overall_assessment,
            "logic_score": logic_score,
        }
    )


def test_text_with_clear_ad_hominem(client, mock_vllm):
    mock_vllm.return_value = _vllm_payload(
        fallacies=[
            {
                "type": "ad_hominem",
                "type_label": "Ad Hominem",
                "text": "Pendapatnya soal ekonomi tidak usah didengar, dia kan cuma lulusan SD yang tidak ngerti apa-apa.",
                "explanation": "Argumen ini menyerang latar belakang pendidikan pembicara, bukan substansi argumennya.",
                "confidence": 0.95,
                "severity": "medium",
                "timestamp_start": None,
                "timestamp_end": None,
            }
        ],
        overall_assessment="Argumen ini menyerang pribadi lawan bicara alih-alih membahas substansinya.",
        logic_score=55,
    )

    response = client.post(
        ENDPOINT,
        json={
            "text": "Pendapatnya soal ekonomi tidak usah didengar, dia kan cuma lulusan SD yang tidak ngerti apa-apa.",
            "mode": "quick",
            "language": "id",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["fallacies"]) == 1
    assert data["fallacies"][0]["type"] == "ad_hominem"


def test_text_with_no_fallacy(client, mock_vllm):
    mock_vllm.return_value = _vllm_payload(
        fallacies=[],
        overall_assessment="Argumen ini logis dan didukung oleh bukti yang relevan.",
        logic_score=100,
    )

    response = client.post(
        ENDPOINT,
        json={
            "text": "Olahraga teratur 30 menit setiap hari terbukti meningkatkan kesehatan jantung berdasarkan studi medis.",
            "mode": "quick",
            "language": "id",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["fallacies"] == []


def test_empty_text_returns_400(client, mock_vllm):
    response = client.post(ENDPOINT, json={"text": "", "mode": "quick", "language": "id"})

    assert response.status_code == 400
    mock_vllm.assert_not_called()


def test_text_too_short_returns_400(client, mock_vllm):
    response = client.post(ENDPOINT, json={"text": "Pendek", "mode": "quick", "language": "id"})

    assert response.status_code == 400
    mock_vllm.assert_not_called()


def test_text_too_long_returns_400(client, mock_vllm):
    long_text = "a" * 10_001

    response = client.post(ENDPOINT, json={"text": long_text, "mode": "quick", "language": "id"})

    assert response.status_code == 400
    mock_vllm.assert_not_called()


def test_vllm_timeout_returns_503(client, mock_vllm):
    mock_vllm.side_effect = VLLMTimeoutError("vLLM did not respond in time")

    response = client.post(
        ENDPOINT,
        json={
            "text": "Ini adalah teks argumen yang cukup panjang untuk diperiksa oleh sistem.",
            "mode": "quick",
            "language": "id",
        },
    )

    assert response.status_code == 503


def test_malformed_json_from_model_retries(client, mock_vllm):
    valid_payload = _vllm_payload(
        fallacies=[],
        overall_assessment="Argumen ini logis tanpa cacat berarti.",
        logic_score=90,
    )
    mock_vllm.side_effect = ["ini bukan json yang valid", valid_payload]

    response = client.post(
        ENDPOINT,
        json={
            "text": "Ini adalah teks argumen yang cukup panjang untuk diperiksa oleh sistem.",
            "mode": "quick",
            "language": "id",
        },
    )

    assert response.status_code == 200
    assert mock_vllm.call_count == 2
    data = response.json()
    assert data["overall_assessment"] == "Argumen ini logis tanpa cacat berarti."


def test_response_structure_is_valid(client, mock_vllm):
    mock_vllm.return_value = _vllm_payload(
        fallacies=[
            {
                "type": "strawman",
                "type_label": "Strawman",
                "text": "Kelompok itu pasti ingin menghapus semua aturan.",
                "explanation": "Pernyataan ini melebih-lebihkan posisi lawan bicara.",
                "confidence": 0.88,
                "severity": "medium",
                "timestamp_start": None,
                "timestamp_end": None,
            }
        ],
        overall_assessment="Argumen ini menyalahartikan posisi lawan bicara.",
        logic_score=60,
    )

    response = client.post(
        ENDPOINT,
        json={
            "text": "Kelompok itu pasti ingin menghapus semua aturan yang ada di masyarakat kita.",
            "mode": "quick",
            "language": "id",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data["id"], str) and data["id"]
    assert data["input_type"] == "text"
    assert data["mode"] == "quick"
    assert data["language"] == "id"
    assert isinstance(data["fallacies"], list)
    assert isinstance(data["overall_assessment"], str)
    assert isinstance(data["logic_score"], int)
    assert data["total_fallacies"] == len(data["fallacies"])
    assert isinstance(data["model_used"], str) and data["model_used"]
    assert isinstance(data["analysis_duration_ms"], int)
    assert isinstance(data["created_at"], str) and data["created_at"]

    fallacy = data["fallacies"][0]
    for field in (
        "type",
        "type_label",
        "text",
        "explanation",
        "confidence",
        "severity",
        "timestamp_start",
        "timestamp_end",
    ):
        assert field in fallacy


def test_confidence_below_threshold_excluded(client, mock_vllm):
    mock_vllm.return_value = _vllm_payload(
        fallacies=[
            {
                "type": "slippery_slope",
                "type_label": "Slippery Slope",
                "text": "Jika ini diizinkan, semuanya akan runtuh.",
                "explanation": "Argumen ini mengasumsikan rangkaian akibat tanpa bukti yang cukup.",
                "confidence": 0.4,
                "severity": "low",
                "timestamp_start": None,
                "timestamp_end": None,
            }
        ],
        overall_assessment="Argumen ini cukup masuk akal secara umum.",
        logic_score=85,
    )

    response = client.post(
        ENDPOINT,
        json={
            "text": "Jika ini diizinkan, semuanya akan runtuh dan tidak akan bisa diperbaiki lagi nantinya.",
            "mode": "quick",
            "language": "id",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["fallacies"] == []
    assert data["total_fallacies"] == 0


def test_bahasa_indonesia_text(client, mock_vllm):
    mock_vllm.return_value = _vllm_payload(
        fallacies=[
            {
                "type": "ad_hominem",
                "type_label": "Ad Hominem",
                "text": "Jangan dengarkan calon itu, dia dulu pernah dipenjara karena kasus pribadi yang tidak ada hubungannya dengan kebijakan.",
                "explanation": "Argumen ini menyerang masa lalu pribadi calon, bukan kebijakan yang diusulkan.",
                "confidence": 0.91,
                "severity": "high",
                "timestamp_start": None,
                "timestamp_end": None,
            }
        ],
        overall_assessment="Argumen ini menyerang karakter pribadi alih-alih membahas kebijakan.",
        logic_score=45,
    )

    response = client.post(
        ENDPOINT,
        json={
            "text": "Jangan dengarkan calon itu, dia dulu pernah dipenjara karena kasus pribadi yang tidak ada hubungannya dengan kebijakan.",
            "mode": "quick",
            "language": "id",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "id"
    assert len(data["fallacies"]) >= 1
