"""Article scraping via the Jina Reader API, plus source metadata and text cleanup."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)

_JINA_READER_BASE_URL = "https://r.jina.ai/"
_SCRAPE_TIMEOUT_SECONDS = 15.0
_MIN_WORD_COUNT = 100

KNOWN_INDONESIAN_SOURCES = [
    "kompas.com",
    "detik.com",
    "tempo.co",
    "cnnindonesia.com",
    "cnbcindonesia.com",
    "liputan6.com",
    "tribunnews.com",
    "antaranews.com",
    "republika.co.id",
    "kumparan.com",
    "suara.com",
    "viva.co.id",
    "sindonews.com",
    "merdeka.com",
    "jpnn.com",
    "bisnis.com",
    "tirto.id",
    "mediaindonesia.com",
    "katadata.co.id",
    "okezone.com",
]

_NOISE_LINE_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"^baca juga\b.*$",
        r"^simak juga\b.*$",
        r"^lihat juga\b.*$",
        r"^baca:.*$",
        r"^©.*$",
        r"^copyright\b.*$",
        r"^hak cipta\b.*$",
        r"^all rights reserved\b.*$",
        r"^advertisement$",
        r"^iklan$",
        r"^scroll to continue.*$",
        r"^scroll to resume.*$",
        r"^share\s*:.*$",
        r"^follow us on\b.*$",
        r"^tag\s*:.*$",
    )
]


class ArticleScrapeError(Exception):
    """Raised when the Jina Reader API fails or returns an unexpected response."""


class ArticleScrapeTimeoutError(ArticleScrapeError):
    """Raised when the Jina Reader API does not respond within the configured timeout."""


class ArticleTooShortError(ArticleScrapeError):
    """Raised when the cleaned article text falls below the minimum word count."""


@dataclass(frozen=True)
class ArticleContent:
    url: str
    title: str
    text: str
    word_count: int
    domain: str
    scraped_at: datetime


@dataclass(frozen=True)
class ArticleMetadata:
    domain: str
    is_known_source: bool
    language_guess: str


def _extract_domain(url: str) -> str:
    candidate = url if "://" in url else f"https://{url}"
    domain = urlparse(candidate).netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def extract_article_metadata(url: str) -> ArticleMetadata:
    """Derive the domain, known-source flag, and a rough language guess from ``url``."""

    domain = _extract_domain(url)
    is_known_source = any(
        domain == source or domain.endswith(f".{source}") for source in KNOWN_INDONESIAN_SOURCES
    )
    language_guess = "id" if is_known_source else "en"

    return ArticleMetadata(
        domain=domain,
        is_known_source=is_known_source,
        language_guess=language_guess,
    )


def clean_article_text(raw_text: str) -> str:
    """Strip blank lines and common header/footer noise, enforcing a minimum word count."""

    cleaned_lines = []
    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if any(pattern.match(stripped) for pattern in _NOISE_LINE_PATTERNS):
            continue
        cleaned_lines.append(stripped)

    cleaned_text = "\n\n".join(cleaned_lines)
    word_count = len(cleaned_text.split())
    if word_count < _MIN_WORD_COUNT:
        raise ArticleTooShortError(
            f"Article text has only {word_count} words after cleaning "
            f"(minimum {_MIN_WORD_COUNT} required)"
        )

    return cleaned_text


async def scrape_article(url: str) -> ArticleContent:
    """Fetch and clean an article's content via the Jina Reader API."""

    jina_url = f"{_JINA_READER_BASE_URL}{url}"
    headers = {"X-Return-Format": "json", "Accept": "application/json"}

    logger.info("Scraping article via Jina Reader: %s", url)

    try:
        async with httpx.AsyncClient(timeout=_SCRAPE_TIMEOUT_SECONDS) as client:
            response = await client.get(jina_url, headers=headers)
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        logger.error("Jina Reader request timed out after %.0fs for %s", _SCRAPE_TIMEOUT_SECONDS, url)
        raise ArticleScrapeTimeoutError(
            f"Jina Reader did not respond within {_SCRAPE_TIMEOUT_SECONDS:.0f}s"
        ) from exc
    except httpx.HTTPStatusError as exc:
        logger.error(
            "Jina Reader returned HTTP %s for %s: %s",
            exc.response.status_code,
            url,
            exc.response.text[:500],
        )
        raise ArticleScrapeError(f"Jina Reader returned HTTP {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        logger.error("Jina Reader request failed for %s: %s", url, exc)
        raise ArticleScrapeError(str(exc)) from exc

    body = response.json()
    try:
        payload = body["data"]
        title = (payload.get("title") or "Untitled").strip()
        raw_text = payload.get("content") or ""
    except (KeyError, TypeError) as exc:
        logger.error("Unexpected Jina Reader response shape for %s: %s", url, body)
        raise ArticleScrapeError("Unexpected response structure from Jina Reader") from exc

    text = clean_article_text(raw_text)

    return ArticleContent(
        url=url,
        title=title,
        text=text,
        word_count=len(text.split()),
        domain=_extract_domain(url),
        scraped_at=datetime.now(timezone.utc),
    )
