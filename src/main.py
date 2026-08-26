"""Entry point (Fas 2.13a — the deploy default serves the GUARDED app).

deploy/start.sh runs `python -m src.main`; `app` below is build_app(), which
since 2.13a returns runtime/api_server.py — the single authenticated app where
every route requires a verified caller (Depends(zt_guard)) and only /healthz is
open. This entrypoint and the Dockerfile CMD (runtime.serve) serve the SAME
app object; there is no unauthenticated route surface (a P0 auth-bypass — the
raw per-node routers served here before — is closed by construction).
"""
import os

import uvicorn
import yaml
from src.shared.orchestrator import build_app
from src.shared.zt_auth import serve_guard


def load_karta(path: str = "karta.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


app = build_app()


if __name__ == "__main__":
    host = os.environ.get("BIND_HOST", "0.0.0.0")
    karta = load_karta()
    print(f"loaded karta: {karta.get('metadata', {}).get('doer_id')}")
    # Fas 2.5 (A3) — serve-guard: an auth-OFF (ZT_REQUIRE_AUTH=0) process may
    # bind ONLY loopback. Single source: src.shared.zt_auth.serve_guard.
    serve_guard(host)
    # B1: same TLS/mTLS posture as runtime.serve (TLS_CERT_FILE / TLS_KEY_FILE /
    # TLS_CLIENT_CA_FILE) — the two entrypoints never diverge on transport.
    from runtime.serve import tls_kwargs
    uvicorn.run(app, host=host, port=int(os.environ.get("PORT", "8000")), **tls_kwargs())
