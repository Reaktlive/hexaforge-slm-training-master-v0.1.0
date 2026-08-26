"""Single guarded entrypoint — the deploy default has no open route.

Fas 2.13a (external DD P0): deploy/start.sh serves src.main:app. Before this
round that was a SECOND, unauthenticated app (build_app mounted 214 raw node
routers incl. YO side-effects). This test proves, dynamically, that:
  1. the deploy entrypoint (src.main.app) IS the guarded app (runtime.api_server.app);
  2. EVERY served route rejects a request with no credential (401/403) when
     ZT_REQUIRE_AUTH is on — /healthz is the only open liveness route;
  3. no raw per-node side-effect route (port-yo/xo/zi/zo) is served at all.
Route list is read from the app itself, so a newly-mounted open route fails here.
"""
import os

import pytest
from fastapi.testclient import TestClient


def test_deploy_entrypoint_is_the_guarded_app():
    import src.main as _main
    import runtime.api_server as _api
    # The object served by 'python -m src.main' must be the guarded app itself.
    assert _main.app is _api.app, "src.main serves a different app than the guarded api_server"


def _served_paths(app):
    return [r for r in app.routes if getattr(r, "path", None)]


def test_no_raw_side_effect_routes_are_served():
    import src.main as _main
    bad = [r.path for r in _served_paths(_main.app)
           if any(r.path.endswith(sfx) for sfx in ("/port-yo", "/port-xo", "/port-zi", "/port-zo", "/port-yi"))]
    assert bad == [], f"raw per-node side-effect routes are served (the bypass surface): {bad}"


def test_every_served_route_rejects_unauthenticated_caller():
    import src.main as _main
    os.environ["ZT_REQUIRE_AUTH"] = "1"
    os.environ.pop("ZT_IDENTITIES", None)  # no identities: every credentialed check also fails closed
    try:
        client = TestClient(_main.app)
        checked = 0
        for route in _served_paths(_main.app):
            path = route.path
            methods = (getattr(route, "methods", None) or set()) - {"HEAD", "OPTIONS"}
            if not methods:
                continue
            # Intentionally-open routes: /healthz (liveness), /readyz (readiness
            # probe — Fas 2.25) + / (public name/version banner). Everything else
            # must require a credential.
            if path == "/healthz":
                assert client.get("/healthz").status_code == 200
                continue
            if path == "/readyz":
                # Readiness is a probe surface (no data), open like /healthz. It
                # returns 200 (state writable) or 503 (not) — never auth-gated.
                assert client.get("/readyz").status_code in (200, 503)
                continue
            if path == "/":
                continue
            # OpenAPI docs are OFF by default (ENABLE_API_DOCS unset) — if a dev
            # enabled them they are schema, not data; skip from the auth sweep.
            if path.startswith("/docs") or path.startswith("/redoc") or path == "/openapi.json":
                continue
            # Path params can't be resolved generically — substitute a literal.
            concrete = path
            while "{" in concrete:
                a = concrete.index("{"); b = concrete.index("}")
                concrete = concrete[:a] + "x" + concrete[b + 1:]
            for method in methods:
                resp = client.request(method, concrete, json={})
                assert resp.status_code in (401, 403), (
                    f"{method} {concrete} returned {resp.status_code} without a credential "
                    f"(expected 401/403 — an open route is a P0 auth bypass)")
                checked += 1
        assert checked > 0, "no non-health routes were checked — the test would be vacuous"
    finally:
        os.environ["ZT_REQUIRE_AUTH"] = "0"


def test_openapi_schema_is_off_by_default():
    """A security agent must not expose its full route map unauthenticated.
    With ENABLE_API_DOCS unset, /openapi.json and /docs are disabled (404)."""
    import src.main as _main
    os.environ.pop("ENABLE_API_DOCS", None)
    client = TestClient(_main.app)
    assert client.get("/openapi.json").status_code == 404
    assert client.get("/docs").status_code == 404


def test_ccas_decide_never_runs_for_unauthenticated_caller():
    """The exact P0 repro: an unauthenticated POST to a gate's YO port (the
    side-effect surface) must be rejected at the transport, before any
    ccas_decide/handle_yo runs. With no YO route served (Option 1) this is a
    404/401/403 — never a 200 'approved' with principal=None."""
    import src.main as _main
    os.environ["ZT_REQUIRE_AUTH"] = "1"
    os.environ.pop("ZT_IDENTITIES", None)
    try:
        client = TestClient(_main.app)
        gate_yo = [r.path for r in _served_paths(_main.app)
                   if "approval_gate" in r.path and r.path.endswith("/port-yo")]
        # Option 1: no YO route is served at all. If any ever is, it must 401/403.
        for path in gate_yo:
            resp = client.post(path, json={"event_id": "evt-p0", "ts": "2026-01-01T00:00:00Z"})
            assert resp.status_code in (401, 403), (path, resp.status_code)
    finally:
        os.environ["ZT_REQUIRE_AUTH"] = "0"
