"""Security schemes shared across routers.

FallacyX accepts an optional Supabase-issued JWT (``Authorization: Bearer <token>``)
to attribute examinations to a signed-in user and apply per-tier rate limits.
The scheme is declared with ``auto_error=False`` so anonymous requests continue
to work; routes that need an authenticated user should validate the credential
themselves.
"""

from __future__ import annotations

from fastapi.security import HTTPBearer

bearer_scheme = HTTPBearer(
    scheme_name="SupabaseJWT",
    description=(
        "Supabase access token issued after sign-in. Pass it as "
        "`Authorization: Bearer <token>`. Optional for most endpoints; "
        "anonymous requests are subject to the free-tier rate limit."
    ),
    auto_error=False,
)
