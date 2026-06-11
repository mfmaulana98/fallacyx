"""Pydantic response models for the analyze endpoints."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class FallacyItem(BaseModel):
    """A single detected logical fallacy."""

    fallacy_type: str
    name_id: str
    name_en: str
    quote: str
    explanation: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    severity: Literal["high", "medium", "low"]
    start_char: Optional[int] = None
    end_char: Optional[int] = None


class AnalysisResponse(BaseModel):
    """Response body for POST /analyze/text."""

    id: str
    input_type: Literal["text"] = "text"
    mode: Literal["quick", "educational"]
    language: Literal["id", "en"]

    fallacies: list[FallacyItem] = Field(default_factory=list)
    overall_assessment: str
    is_clean: bool
    total_fallacies: int

    model_used: str
    analysis_duration_ms: int
    created_at: str


class YouTubeFallacyItem(FallacyItem):
    """A logical fallacy detected within a YouTube video transcript."""

    timestamp_seconds: float = Field(
        ..., ge=0.0, description="Where in the video (in seconds) the quote begins."
    )


class YouTubeAnalysisResponse(BaseModel):
    """Response body for POST /analyze/youtube."""

    id: str
    input_type: Literal["youtube"] = "youtube"
    mode: Literal["quick", "educational"]
    language: Literal["id", "en"]

    video_id: str
    video_title: str
    video_duration_seconds: int
    transcript: str

    fallacies: list[YouTubeFallacyItem] = Field(default_factory=list)
    overall_assessment: str
    is_clean: bool
    total_fallacies: int

    model_used: str
    analysis_duration_ms: int
    created_at: str
    cached: bool = False
