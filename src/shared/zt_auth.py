"""Transport-layer Zero Trust authentication + authorization (T-04-023).

This module is the pure, network-free core of the /api boundary's Zero Trust
posture. It establishes *caller identity* and *per-request authorization* so the
HTTP transport is no longer implicitly trusted: "never trust, always verify".

Design doctrine
---------------
- ZT **composes with** CCAS; it does not replace it. CCAS gates *actions*
  (approve/deny tiers, PII egress, etc.). ZT gates *the transport*: who is on
  the wire and may they call this route at all. A request must pass ZT first,
  then CCAS still applies downstream exactly as before.
- The authenticated identity IS bound into the audit chain (Fas 2.11a): the
  api-server's zt_guard calls ``hexa_record.set_principal`` after verification,
  and every audit append in that request context carries the principal in its
  HASHED core — a state-changing call is attributable to a verified caller,
  tamper-evidently. The loop between identity and the HexaRecord is closed.
- Continuous verification: credentials carry an optional ``expires_at`` and an
  expired credential is treated as unauthenticated. Verification is performed on
  every request, never cached as a long-lived session.

Extensibility seam
------------------
The default scheme is a **bearer token / API key** resolved against an identity
map (env ``ZT_IDENTITIES``). All credential resolution funnels through the
documented ``verify_credential`` seam. To add OIDC/JWT verification or an mTLS
client-certificate subject mapping later, register an additional verifier with
``register_verifier`` (or replace the default) — callers of ``authenticate`` /
``authorize`` do not change.

No part of this module performs network I/O.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Mapping, Optional

# A verifier takes the resolved credential material (e.g. a bearer token string)
# and returns a normalized auth dict or None. This is the seam an OIDC/JWT or
# mTLS-subject verifier plugs into without touching authenticate()'s callers.
Verifier = Callable[[str, Mapping[str, Any]], Optional[Dict[str, Any]]]

# Env names (kept as module constants so tests + ops reference one source).
ENV_REQUIRE_AUTH = "ZT_REQUIRE_AUTH"
ENV_IDENTITIES = "ZT_IDENTITIES"
# T-06-014 mTLS (off by default; additive). A trusted TLS-terminating proxy
# verifies the client certificate and passes its subject DN in a header; we map
# that subject to a ZT identity. The proxy MUST overwrite this header so a
# client cannot spoof it (see docs/deployment-tls.md).
ENV_MTLS_ENABLED = "ZT_MTLS_ENABLED"
ENV_MTLS_IDENTITIES = "ZT_MTLS_IDENTITIES"
ENV_MTLS_SUBJECT_HEADER = "ZT_MTLS_SUBJECT_HEADER"
DEFAULT_MTLS_SUBJECT_HEADER = "x-client-cert-subject"

_TRUTHY = {"1", "true", "yes", "on"}
# Fas 2.5 — the fail-closed default reads the EXPLICIT opt-out set only.
_FALSEY = {"0", "false", "no", "off"}


def require_auth_enabled() -> bool:
    """True when transport-layer auth must be enforced (env ``ZT_REQUIRE_AUTH``).

    Fas 2.5 (A3) — FAIL-CLOSED DEFAULT: unset/empty means **ON**. A security
    product never boots open by omission. The ONLY way to run without
    transport auth is the explicit, visible dev opt-out ``ZT_REQUIRE_AUTH=0``
    — and src/main.py's serve_guard confines that mode to loopback binds.
    See docs/deployment-tls.md for the production posture.
    """
    return os.environ.get(ENV_REQUIRE_AUTH, "").strip().lower() not in _FALSEY


def _load_identity_map() -> Dict[str, Dict[str, Any]]:
    """Parse the identity map from env ``ZT_IDENTITIES`` (JSON).

    Shape: ``{"<token>": {"identity": str, "scopes": [..], "expires_at": iso|null}}``.
    A malformed or absent value yields an empty map (no identities -> all callers
    are unauthenticated when enforcement is on).
    """
    raw = (os.environ.get(ENV_IDENTITIES))
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return {}
    if not isinstance(data, dict):
        return {}
    out: Dict[str, Dict[str, Any]] = {}
    for token, rec in data.items():
        if isinstance(token, str) and isinstance(rec, dict):
            out[token] = rec
    return out


def _is_expired(expires_at: Any, *, now: Optional[datetime] = None) -> bool:
    """True when ``expires_at`` (ISO 8601 string) is in the past.

    None / missing -> never expires. An unparseable value is treated as expired
    (fail-closed: we cannot prove the credential is still valid).
    """
    if expires_at is None:
        return False
    if not isinstance(expires_at, str):
        return True
    text = expires_at.strip()
    if not text:
        return False
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        exp = datetime.fromisoformat(text)
    except ValueError:
        return True
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return exp <= current


def _normalize_record(identity: str, rec: Mapping[str, Any]) -> Dict[str, Any]:
    scopes = rec.get("scopes")
    if not isinstance(scopes, list):
        scopes = []
    return {
        "identity": identity,
        "scopes": [str(s) for s in scopes],
        "expires_at": rec.get("expires_at"),
    }


def _bearer_token_verifier(credential: str, headers: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    """Default verifier: resolve a bearer token / API key against ``ZT_IDENTITIES``.

    Honors expiry (continuous verification): an entry whose ``expires_at`` is in
    the past resolves to None — the caller is treated as unauthenticated.
    """
    identities = _load_identity_map()
    rec = identities.get(credential)
    if not isinstance(rec, dict):
        return None
    identity = rec.get("identity")
    if not isinstance(identity, str) or not identity:
        return None
    if _is_expired(rec.get("expires_at")):
        return None
    return _normalize_record(identity, rec)


# The active verifier seam. Swap/extend this for OIDC/JWT or mTLS later without
# changing authenticate()'s callers.
_VERIFIER: Verifier = _bearer_token_verifier


def register_verifier(verifier: Verifier) -> None:
    """Replace the active credential verifier (extensibility seam).

    A verifier receives ``(credential, headers)`` and returns a normalized auth
    dict (``{"identity", "scopes", "expires_at"}``) or None. Intended for adding
    OIDC/JWT or mTLS-subject verification without changing public callers.
    """
    global _VERIFIER
    _VERIFIER = verifier


def reset_verifier() -> None:
    """Restore the default bearer-token / API-key verifier (mainly for tests)."""
    global _VERIFIER
    _VERIFIER = _bearer_token_verifier


def _extract_credential(headers: Mapping[str, Any]) -> Optional[str]:
    """Pull the bearer token / API key out of request headers.

    Accepts ``Authorization: Bearer <token>`` (case-insensitive scheme) or an
    ``X-API-Key: <token>`` header. Header lookups are case-insensitive.
    """
    lookup: Dict[str, Any] = {}
    try:
        items = headers.items()
    except AttributeError:
        items = []
    for key, value in items:
        if isinstance(key, str):
            lookup[key.lower()] = value

    auth = lookup.get("authorization")
    if isinstance(auth, str) and auth.strip():
        parts = auth.strip().split(None, 1)
        if len(parts) == 2 and parts[0].lower() == "bearer" and parts[1].strip():
            return parts[1].strip()

    api_key = lookup.get("x-api-key")
    if isinstance(api_key, str) and api_key.strip():
        return api_key.strip()

    return None


def _mtls_enabled() -> bool:
    """True when mTLS subject mapping is enabled (env ``ZT_MTLS_ENABLED``).
    Default False — the bearer path is completely unchanged when off."""
    return os.environ.get(ENV_MTLS_ENABLED, "").strip().lower() in _TRUTHY


def _load_mtls_map() -> Dict[str, Dict[str, Any]]:
    """Parse ``ZT_MTLS_IDENTITIES`` (JSON: subject-DN -> identity record)."""
    raw = (os.environ.get(ENV_MTLS_IDENTITIES))
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: v for k, v in data.items() if isinstance(k, str) and isinstance(v, dict)}


def _mtls_authenticate(headers: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    """Resolve a verified client-cert subject (set by a trusted proxy) to a ZT
    identity. Inert unless ``ZT_MTLS_ENABLED`` is truthy."""
    if not _mtls_enabled():
        return None
    header_name = (os.environ.get(ENV_MTLS_SUBJECT_HEADER, "").strip()
                   or DEFAULT_MTLS_SUBJECT_HEADER).lower()
    subject = None
    try:
        for key, value in headers.items():
            if isinstance(key, str) and key.lower() == header_name:
                subject = value
                break
    except AttributeError:
        return None
    if not isinstance(subject, str) or not subject.strip():
        return None
    subject = subject.strip()
    rec = _load_mtls_map().get(subject)
    if not isinstance(rec, dict):
        return None
    identity = rec.get("identity") if isinstance(rec.get("identity"), str) and rec.get("identity") else subject
    if _is_expired(rec.get("expires_at")):
        return None
    return _normalize_record(identity, rec)


def authenticate(headers: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    """Authenticate a caller from request headers.

    Returns ``{"identity": str, "scopes": [..], "expires_at": iso|None}`` on a
    valid, non-expired credential, or ``None`` when missing / unknown / expired.

    Credential resolution goes through the active ``verify_credential`` seam, so
    the scheme can evolve (JWT, mTLS) without changing this signature.
    """
    credential = _extract_credential(headers)
    if credential:
        auth = verify_credential(credential, headers)
        if auth is not None:
            return auth
    # Additive mTLS fallback (off by default): a verified client-cert subject
    # passed by a trusted proxy maps to a ZT identity. Never reached when
    # ZT_MTLS_ENABLED is unset, so the bearer path is unchanged.
    return _mtls_authenticate(headers)


def verify_credential(credential: str, headers: Optional[Mapping[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Documented seam: verify resolved credential material -> auth dict or None.

    The default implementation is a bearer-token / API-key lookup against the
    identity map. Replace via ``register_verifier`` to add OIDC/JWT or mTLS.
    """
    return _VERIFIER(credential, headers or {})


def authorize(auth: Optional[Mapping[str, Any]], required_scope: str) -> bool:
    """True when ``auth`` carries ``required_scope``.

    An empty/None ``required_scope`` means the route needs authentication but no
    specific scope. A None ``auth`` is never authorized.
    """
    if auth is None:
        return False
    if not required_scope:
        return True
    scopes = auth.get("scopes") if isinstance(auth, Mapping) else None
    if not isinstance(scopes, (list, tuple, set)):
        return False
    return required_scope in scopes


# ── Fas 2.5 (A3) — serve-guard: auth-OFF får ENDAST binda loopback ────────
_LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


def serve_guard(host: str) -> None:
    """Refuse to serve OPEN (auth-off) on a non-loopback interface.

    ``ZT_REQUIRE_AUTH=0`` is an explicit dev opt-out, never an internet
    posture. Both entrypoints (``python -m src.main`` and
    ``python -m runtime.serve``) call this before binding. /healthz liveness
    is unaffected — it is always open. See docs/deployment-tls.md.
    """
    if require_auth_enabled():
        return
    if str(host).strip().lower() not in _LOOPBACK_HOSTS:
        raise SystemExit(
            "REFUSED: ZT_REQUIRE_AUTH=0 (transport auth off) with non-loopback "
            f"bind host {host!r}. Auth-off is allowed ONLY on loopback. Remove "
            "ZT_REQUIRE_AUTH=0 (the fail-closed default is ON) and provision "
            "ZT_IDENTITIES, or bind 127.0.0.1. See docs/deployment-tls.md."
        )
