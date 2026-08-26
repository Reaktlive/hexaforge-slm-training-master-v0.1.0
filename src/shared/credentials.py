"""Token-based credential resolver (Zero Trust ZT-1).

CREDENTIAL DOCTRINE: this runtime NEVER ships a static long-lived API key in
code or config. Credentials are resolved at request time and short-lived.

Resolution order (server-side only — never reachable from client code):
  1. <PROVIDER>_TOKEN_ENDPOINT  → mint/refresh a short-lived token from your
     secrets manager / token broker (Vault, cloud secret manager, OIDC
     token-exchange). This is the production path. See CUSTOMER_SLOT below.
  2. <PROVIDER>_API_KEY         → an injected secret (a secrets manager wrote
     this env var at boot). Treated as opaque; rotated out-of-band.
  3. <PROVIDER>_API_KEY_DEV     → LOCAL DEVELOPMENT ONLY fallback. Loud-logged
     so it can never silently reach a deployed environment.

The seam at _fetch_token_from_broker() is intentionally a CUSTOMER_SLOT:
the broker protocol is deployment-specific (different orgs run different
secret managers), so the bundle ships the resolution policy + caching but
leaves the wire call for the operator to bind.
"""
import os
import time
from dataclasses import dataclass
from typing import Optional

import structlog

_log = structlog.get_logger("credentials")


class CredentialUnavailable(RuntimeError):
    """No usable credential for the provider (ZT-1 refuses to fabricate one)."""

    def __init__(self, message: str, *, provider: Optional[str] = None) -> None:
        super().__init__(message)
        self.provider = provider


@dataclass
class _CachedToken:
    value: str
    expires_at: float  # epoch seconds


# Per-provider in-process token cache (refreshed near expiry).
_TOKEN_CACHE: dict[str, _CachedToken] = {}

# Refresh a cached token this many seconds BEFORE it actually expires, so an
# in-flight request never races the expiry boundary.
_REFRESH_SKEW_SECONDS = 30


def _env(provider: str, suffix: str) -> Optional[str]:
    val = os.environ.get(f"{provider.upper()}_{suffix}")
    return val.strip() if val else None


def _fetch_token_from_broker(provider: str, endpoint: str, ttl_seconds: int) -> _CachedToken:
    """Mint/refresh a short-lived credential from the secrets-manager / token
    broker at `endpoint`.

    CUSTOMER_SLOT: implement the broker wire call for your deployment.
    The broker protocol is deployment-specific (Vault, AWS STS / Secrets
    Manager, GCP/Azure, OIDC token-exchange), so the bundle ships the
    resolution policy + caching and leaves the HTTP/SDK call to the operator.

    Contract: return a _CachedToken whose .value is a short-lived bearer
    credential and .expires_at is its epoch-seconds expiry. The default
    implementation raises so a misconfigured production deploy fails loudly
    instead of silently falling back to a static key.
    """
    raise NotImplementedError(
        f"{provider}_TOKEN_ENDPOINT={endpoint!r} is set but the broker call is "
        f"not yet bound. Implement _fetch_token_from_broker() (CUSTOMER_SLOT) "
        f"to exchange it for a short-lived token, or unset the endpoint to use "
        f"an injected {provider.upper()}_API_KEY."
    )


def resolve_credential(provider: str = "anthropic") -> str:
    """Resolve a short-lived credential for `provider` at request time.

    Zero Trust: prefers a brokered short-lived token; falls back to an
    injected secret; uses the dev-only key only when nothing else is set
    (loud-logged). Never returns an empty string — raises instead so callers
    fail fast rather than calling the provider unauthenticated.
    """
    endpoint = _env(provider, "TOKEN_ENDPOINT")
    if endpoint:
        cached = _TOKEN_CACHE.get(provider)
        now = time.time()
        if cached is None or cached.expires_at - _REFRESH_SKEW_SECONDS <= now:
            ttl = int(_env(provider, "TOKEN_TTL_SECONDS") or "900")
            cached = _fetch_token_from_broker(provider, endpoint, ttl)
            _TOKEN_CACHE[provider] = cached
        return cached.value

    injected = _env(provider, "API_KEY")
    if injected:
        return injected

    dev = _env(provider, "API_KEY_DEV")
    if dev:
        _log.warning(
            "credentials_dev_fallback",
            provider=provider,
            note="using *_API_KEY_DEV — LOCAL DEV ONLY; set a token endpoint or "
                 "injected secret before deploying",
        )
        return dev

    raise CredentialUnavailable(
        f"No credential for provider {provider!r}: set {provider.upper()}_TOKEN_ENDPOINT "
        f"(production) or {provider.upper()}_API_KEY (injected secret). "
        f"Static keys in code/config are forbidden by Zero Trust doctrine.",
        provider=provider,
    )
