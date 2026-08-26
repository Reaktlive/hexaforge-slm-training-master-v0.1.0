"""Guarded entrypoint for the pipeline API (runtime/api_server.py).

Fas 2.5 (A3): transport auth is FAIL-CLOSED by default (ZT_REQUIRE_AUTH
unset => ON). The serve-guard (single source: src.shared.zt_auth) refuses
an auth-OFF process on any non-loopback bind — ZT_REQUIRE_AUTH=0 is a dev
convenience on 127.0.0.1, never an internet posture. See
docs/deployment-tls.md.

B1 (closed fleet loop): the runtime can terminate TLS ITSELF — so two fleet
containers speak mutually-authenticated TLS with no proxy in between:
  TLS_CERT_FILE / TLS_KEY_FILE   PEM server certificate + key -> serve https
  TLS_CLIENT_CA_FILE             PEM CA; when set, a client certificate signed
                                 by it is REQUIRED (mutual TLS) — an
                                 unauthenticated TLS client is refused at the
                                 handshake, before any route runs.
Setting one of cert/key without the other is a configuration error and the
process refuses to start (never silently falls back to plaintext).
"""
import os
import ssl
import sys

import uvicorn

from src.shared.zt_auth import serve_guard


def tls_kwargs(env=os.environ) -> dict:
    """uvicorn SSL keyword arguments derived from TLS_* env — {} for plaintext.
    Fail-closed on a half-configured pair."""
    cert = str(env.get("TLS_CERT_FILE", "") or "").strip()
    key = str(env.get("TLS_KEY_FILE", "") or "").strip()
    client_ca = str(env.get("TLS_CLIENT_CA_FILE", "") or "").strip()
    if bool(cert) != bool(key):
        raise SystemExit("serve: TLS_CERT_FILE and TLS_KEY_FILE must be set together (refusing to start)")
    if not cert:
        if client_ca:
            raise SystemExit("serve: TLS_CLIENT_CA_FILE requires TLS_CERT_FILE/TLS_KEY_FILE (refusing to start)")
        return {}
    kw = {"ssl_certfile": cert, "ssl_keyfile": key, "ssl_version": ssl.PROTOCOL_TLS_SERVER}
    if client_ca:
        kw["ssl_ca_certs"] = client_ca
        kw["ssl_cert_reqs"] = ssl.CERT_REQUIRED  # mutual TLS: no client cert, no connection
    return kw


def main() -> None:
    host = os.environ.get("BIND_HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    serve_guard(host)
    kw = tls_kwargs()
    print("serve: %s on %s:%d%s" % ("https" if kw else "http", host, port,
                                     " (mutual TLS: client certificate required)" if kw.get("ssl_ca_certs") else ""),
          file=sys.stderr)
    uvicorn.run("runtime.api_server:app", host=host, port=port, workers=1, **kw)


if __name__ == "__main__":
    main()
