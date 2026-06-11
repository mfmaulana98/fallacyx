"""Pydantic response models for the analyze endpoints."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

_EXAMPLE_FALLACY = {
    "fallacy_type": "ad_populum",
    "name_id": "Argumentum ad Populum",
    "name_en": "Appeal to Popularity",
    "quote": "Everyone I know agrees that this policy is a disaster",
    "explanation": (
        "The argument treats widespread agreement among the speaker's acquaintances "
        "as evidence that the policy will fail, without offering independent evidence."
    ),
    "confidence": 0.87,
    "severity": "high",
    "start_char": 0,
    "end_char": 53,
}


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

    model_config = {"json_schema_extra": {"examples": [_EXAMPLE_FALLACY]}}


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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "3f2e9c4a-7b1d-4e6f-9c2a-1d8e7f6b5a4c",
                    "input_type": "text",
                    "mode": "educational",
                    "language": "en",
                    "fallacies": [_EXAMPLE_FALLACY],
                    "overall_assessment": (
                        "The argument relies on popular opinion rather than evidence. "
                        "1 Fallacy Found · SUBSTANTIAL"
                    ),
                    "is_clean": False,
                    "total_fallacies": 1,
                    "model_used": "meta-llama/Llama-3-70b-instruct",
                    "analysis_duration_ms": 1840,
                    "created_at": "2026-06-11T08:30:00+00:00",
                }
            ]
        }
    }


class UrlAnalysisResponse(BaseModel):
    """Response body for POST /analyze/url."""

    id: str
    input_type: Literal["url"] = "url"
    mode: Literal["quick", "educational"]
    language: Literal["id", "en"]

    article_title: str
    article_url: str
    word_count: int

    fallacies: list[FallacyItem] = Field(default_factory=list)
    overall_assessment: str
    is_clean: bool
    total_fallacies: int

    model_used: str
    analysis_duration_ms: int
    created_at: str
    cached: bool = False

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "3f2e9c4a-7b1d-4e6f-9c2a-1d8e7f6b5a4c",
                    "input_type": "url",
                    "mode": "quick",
                    "language": "en",
                    "article_title": "Why This Policy Will Fail",
                    "article_url": "https://www.example.com/news/opinion-piece",
                    "word_count": 842,
                    "fallacies": [_EXAMPLE_FALLACY],
                    "overall_assessment": "1 Fallacy Found · SUBSTANTIAL",
                    "is_clean": False,
                    "total_fallacies": 1,
                    "model_used": "meta-llama/Llama-3-70b-instruct",
                    "analysis_duration_ms": 2310,
                    "created_at": "2026-06-11T08:30:00+00:00",
                    "cached": False,
                }
            ]
        }
    }


class AudioAnalysisResponse(BaseModel):
    """Response body for POST /analyze/audio."""

    id: str
    input_type: Literal["audio"] = "audio"
    mode: Literal["quick", "educational"]
    language: Literal["id", "en"]

    filename: str
    duration_seconds: float
    transcript: str

    fallacies: list[FallacyItem] = Field(default_factory=list)
    overall_assessment: str
    is_clean: bool
    total_fallacies: int

    model_used: str
    analysis_duration_ms: int
    created_at: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "3f2e9c4a-7b1d-4e6f-9c2a-1d8e7f6b5a4c",
                    "input_type": "audio",
                    "mode": "quick",
                    "language": "en",
                    "filename": "speech.mp3",
                    "duration_seconds": 184.5,
                    "transcript": "Everyone I know agrees that this policy is a disaster...",
                    "fallacies": [_EXAMPLE_FALLACY],
                    "overall_assessment": "1 Fallacy Found · SUBSTANTIAL",
                    "is_clean": False,
                    "total_fallacies": 1,
                    "model_used": "meta-llama/Llama-3-70b-instruct",
                    "analysis_duration_ms": 15230,
                    "created_at": "2026-06-11T08:30:00+00:00",
                }
            ]
        }
    }


class YouTubeFallacyItem(FallacyItem):
    """A logical fallacy detected within a YouTube video transcript."""

    timestamp_seconds: float = Field(
        ..., ge=0.0, description="Where in the video (in seconds) the quote begins."
    )

    model_config = {
        "json_schema_extra": {"examples": [{**_EXAMPLE_FALLACY, "timestamp_seconds": 42.5}]}
    }


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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "3f2e9c4a-7b1d-4e6f-9c2a-1d8e7f6b5a4c",
                    "input_type": "youtube",
                    "mode": "educational",
                    "language": "en",
                    "video_id": "dQw4w9WgXcQ",
                    "video_title": "A Heated Debate on Policy",
                    "video_duration_seconds": 612,
                    "transcript": "Everyone I know agrees that this policy is a disaster...",
                    "fallacies": [{**_EXAMPLE_FALLACY, "timestamp_seconds": 42.5}],
                    "overall_assessment": "1 Fallacy Found · SUBSTANTIAL",
                    "is_clean": False,
                    "total_fallacies": 1,
                    "model_used": "meta-llama/Llama-3-70b-instruct",
                    "analysis_duration_ms": 48210,
                    "created_at": "2026-06-11T08:30:00+00:00",
                    "cached": False,
                }
            ]
        }
    }
