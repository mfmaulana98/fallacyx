from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TextAnalysisRequest(BaseModel):
    """Request payload for analyzing a raw text input."""

    model_config = ConfigDict(str_strip_whitespace=True)

    text: str = Field(..., min_length=10, max_length=10_000)
    mode: Literal["quick", "educational"] = "quick"
    language: Literal["id", "en"] = "id"


class FallacyItem(BaseModel):
    """A single logical fallacy detected within the analyzed text."""

    fallacy_type: str
    name_id: str
    name_en: str
    quote: str
    explanation: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    severity: Literal["low", "medium", "high"]
    start_char: int | None = None
    end_char: int | None = None


class AnalysisResponse(BaseModel):
    """Result of running fallacy detection on a given input."""

    analysis_id: str
    input_type: Literal["text", "url", "youtube", "audio"]
    fallacies: list[FallacyItem]
    total_count: int
    overall_severity: Literal["clean", "low", "medium", "high"]
    processing_time_ms: int
    model_version: str
    created_at: datetime


class ErrorResponse(BaseModel):
    """Standard error response shape returned by the API."""

    error: str
    detail: str
    code: int
