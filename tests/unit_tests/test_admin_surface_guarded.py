"""Admin surface guarded — no unauthenticated mutable control surface.

Fas 2.13b (external DD): the default admin server bound 0.0.0.0:8080 with
wildcard CORS and unauthenticated PUT /api/config. These tests prove the
generated server binds loopback by default, fail-closes mutations, and does not
emit wildcard CORS.
"""
import json
import os
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer


def _load():
    import importlib
    import runtime.orchestrator as o
    importlib.reload(o)
    return o


def _serve(o):
    srv = ThreadingHTTPServer(("127.0.0.1", 0), o.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def _req(method, port, path, headers=None, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request("http://127.0.0.1:%d%s" % (port, path), method=method, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers)


def test_admin_server_binds_loopback_by_default():
    os.environ.pop("ADMIN_BIND_HOST", None)
    o = _load()
    assert o.ADMIN_BIND_HOST == "127.0.0.1", "admin server must default-bind loopback, not a routable address"


def test_unauthenticated_mutation_is_fail_closed():
    os.environ.pop("ADMIN_API_TOKEN", None)
    o = _load()
    srv, port = _serve(o)
    try:
        code, _ = _req("PUT", port, "/api/config", {"Content-Type": "application/json"}, {"shadow_mode": False})
        assert code == 403, "unauthenticated PUT /api/config must be fail-closed (403), got %d" % code
        code2, _ = _req("POST", port, "/api/test-run", {"Content-Type": "application/json"}, {"event": {}})
        assert code2 == 403, "unauthenticated POST /api/test-run must be fail-closed (403), got %d" % code2
        gcode, _ = _req("GET", port, "/api/config")
        assert gcode == 200, "read-only GET /api/config must still work, got %d" % gcode
    finally:
        srv.shutdown()


def test_no_wildcard_cors():
    os.environ.pop("ADMIN_CORS_ORIGIN", None)
    o = _load()
    srv, port = _serve(o)
    try:
        code, headers = _req("GET", port, "/healthz")
        assert code == 200
        assert headers.get("Access-Control-Allow-Origin") != "*", "admin server must not emit wildcard CORS by default"
    finally:
        srv.shutdown()
