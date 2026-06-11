"""FastAPI application entry point for the FallacyX backend.

Wires up app metadata (for the Swagger UI / ReDoc documentation), CORS,
and the API routers.
"""

from __future__ import annotations

from fastapi import FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.security import bearer_scheme
from app.routers import analyze, health, progress

DESCRIPTION = """
**FallacyX** is a real-time logical fallacy detector built for the Revonalar platform.

Submit raw text, an article URL, a YouTube video, or an audio recording, and the
tribunal — **Llama-3-70B-Instruct served via vLLM on an AMD Instinct MI300X** —
returns a verdict: every fallacy found, where it occurs, how confident the model
is, and why the reasoning breaks down.

### Pipeline overview

| Input    | Pipeline                                                              |
|----------|------------------------------------------------------------------------|
| Text     | Prompted directly against the Llama-3-70B model                        |
| URL      | Article extracted via Jina Reader, then examined as text               |
| YouTube  | Audio extracted (yt-dlp) → transcribed (Whisper Large-v3) → examined   |
| Audio    | Uploaded file converted to WAV (ffmpeg) → transcribed → examined       |

The YouTube and audio pipelines stream progress as Server-Sent Events so the
client can render each stage ("Extracting audio...", "Transcribing...",
"Examining the argument...") as it happens.

### Authentication

Most endpoints work anonymously. Pass a Supabase-issued JWT as
`Authorization: Bearer <token>` to attribute an examination to a signed-in
user, unlock examination history, and apply premium-tier rate limits.
"""

tags_metadata = [
    {
        "name": "analyze",
        "description": (
            "Submit text, article URLs, YouTube videos, or audio recordings to "
            "the fallacy examination pipeline and receive a verdict."
        ),
    },
    {
        "name": "progress",
        "description": (
            "Stream real-time progress updates for long-running examination jobs "
            "(YouTube and audio pipelines) over Server-Sent Events."
        ),
    },
    {
        "name": "history",
        "description": (
            "Retrieve a signed-in user's past examinations and verdicts, backed "
            "by Supabase. Reserved for upcoming endpoints."
        ),
    },
    {
        "name": "health",
        "description": (
            "Liveness, downstream dependency, and AMD GPU telemetry checks for "
            "monitoring the FallacyX inference stack."
        ),
    },
]

app = FastAPI(
    title="FallacyX API",
    description=DESCRIPTION,
    version=settings.app_version,
    contact={
        "name": "FallacyX Team — Revonalar",
        "email": "fadli.mln98@gmail.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(analyze.router, dependencies=[Security(bearer_scheme)])
app.include_router(progress.router, dependencies=[Security(bearer_scheme)])
