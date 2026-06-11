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

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": (
                        "Everyone I know agrees that this policy is a disaster, "
                        "so it must be true that it will fail."
                    ),
                    "mode": "educational",
                    "language": "en",
                }
            ]
        }
    }


class UrlAnalysisRequest(BaseModel):
    """Body for POST /analyze/url."""

    url: str = Field(..., description="HTTP/HTTPS URL of the article to examine.")
    mode: Literal["quick", "educational"] = Field(
        default="quick", description="Analysis depth: quick verdict or full educational breakdown."
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "url": "https://www.example.com/news/opinion-piece",
                    "mode": "quick",
                }
            ]
        }
    }


class YouTubeAnalysisRequest(BaseModel):
    """Body for POST /analyze/youtube."""

    youtube_url: str = Field(
        ..., description="A youtube.com/watch, youtu.be, /shorts, or /live URL."
    )
    mode: Literal["quick", "educational"] = Field(
        default="quick", description="Analysis depth: quick verdict or full educational breakdown."
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    "mode": "educational",
                }
            ]
        }
    }
