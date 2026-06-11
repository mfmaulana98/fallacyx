"""Client for the Jina AI Reader API used to extract clean article text from URLs."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

JINA_READER_BASE_URL = "https://r.jina.ai/"
JINA_REQUEST_TIMEOUT_SECONDS = 20.0

_TITLE_PATTERN = re.compile(r"^Title:\s*(.*)$", re.MULTILINE)
_MARKDOWN_CONTENT_PATTERN = re.compile(r"Markdown Content:\s*\n(.*)", re.DOTALL)


class JinaReaderError(Exception):
    """Base class for Jina Reader extraction failures."""


class JinaReaderTimeoutError(JinaReaderError):
    """Raised when the Jina Reader API does not respond in time."""


class JinaReaderUnavailableError(JinaReaderError):
    """Raised when the target URL could not be reached or the Reader API failed."""


class JinaReaderUnsupportedContentError(JinaReaderError):
    """Raised when the target URL does not contain extractable article text."""


@dataclass(frozen=True)
class ExtractedArticle:
    """Clean article content extracted from a URL via Jina Reader."""

    title: str
    text: str
    word_count: int


async def extract_article(url: str) -> ExtractedArticle:
    """Fetch ``url`` through the Jina Reader API and return its clean article text."""

    reader_url = f"{JINA_READER_BASE_URL}{url}"

    try:
        async with httpx.AsyncClient(timeout=JINA_REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get(reader_url, headers={"Accept": "text/plain"})
    except httpx.TimeoutException as exc:
        logger.error("Jina Reader request timed out for %s", url)
        raise JinaReaderTimeoutError(f"Jina Reader did not respond within {JINA_REQUEST_TIMEOUT_SECONDS:.0f}s") from exc
    except httpx.HTTPError as exc:
        logger.error("Jina Reader request failed for %s: %s", url, exc)
        raise JinaReaderUnavailableError(str(exc)) from exc

    if response.status_code == 404:
        raise JinaReaderUnavailableError(f"Jina Reader could not reach {url} (404)")

    if response.status_code >= 400:
        logger.error("Jina Reader returned HTTP %s for %s", response.status_code, url)
        raise JinaReaderUnavailableError(f"Jina Reader returned HTTP {response.status_code}")

    body = response.text.strip()
    if not body:
        raise JinaReaderUnsupportedContentError("Jina Reader returned an empty response")

    title_match = _TITLE_PATTERN.search(body)
    title = title_match.group(1).strip() if title_match else ""

    content_match = _MARKDOWN_CONTENT_PATTERN.search(body)
    content = content_match.group(1).strip() if content_match else body

    if not content:
        raise JinaReaderUnsupportedContentError("No readable article content found at this URL")

    word_count = len(content.split())

    return ExtractedArticle(title=title, text=content, word_count=word_count)
