"""Shared pytest fixtures for the FallacyX backend test suite."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers import analyze as analyze_module


@pytest.fixture()
def app() -> FastAPI:
    """Minimal FastAPI app exposing only the /analyze routes under test."""

    application = FastAPI()
    application.include_router(analyze_module.router)
    return application


@pytest.fixture()
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_save_analysis(mocker):
    """Prevent tests from making real Supabase persistence calls."""

    return mocker.patch.object(analyze_module, "save_fallacy_analysis", new_callable=AsyncMock)


@pytest.fixture()
def mock_vllm(mocker):
    """Patch the vLLM completion call used by the /analyze/text endpoint."""

    return mocker.patch.object(analyze_module, "generate_completion", new_callable=AsyncMock)
