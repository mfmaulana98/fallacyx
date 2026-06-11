"""Pydantic request models for the analyze endpoints."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class TextAnalysisRequest(BaseModel):
    """Body for POST /analyze/text."""

    text: str = Field(..., description="Raw text to examine for logical fallacies.")
    mode: Literal["quick", "educational"] = Field(
        default="quick", description="Analysis depth: quick verdict or full educational breakdown."
    )
    language: Literal["id", "en"] = Field(
        default="id", description="Language for the system prompt, examples, and explanations."
    )


class YouTubeAnalysisRequest(BaseModel):
    """Body for POST /analyze/youtube."""

    youtube_url: str = Field(
        ..., description="A youtube.com/watch, youtu.be, /shorts, or /live URL."
    )
    mode: Literal["quick", "educational"] = Field(
        default="quick", description="Analysis depth: quick verdict or full educational breakdown."
    )
