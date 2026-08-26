"""ARTIFACT_ADMIN_SURFACE_GUARDED — no unauthenticated mutable admin surface.

Fas 2.13b (external DD, Peter). The default docker-compose started a separate
admin server on 0.0.0.0:8080 with wildcard CORS, no auth, and PUT /api/config +
node-binding edits + a mutable test-run. Now the admin server binds loopback by
default, fail-closes mutations behind ADMIN_API_TOKEN, emits no wildcard CORS,
and docker-compose does not start it by default (profile) and binds only
127.0.0.1. Static checks (the emitted runtime test proves the behaviour).
"""
import pathlib
GATE_ID = "ARTIFACT_ADMIN_SURFACE_GUARDED"; GATE_NAME = "Admin Surface Guarded (loopback default, fail-closed mutations, no wildcard CORS, not default-started)"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"

def applies(karta):
    return True

def _read(root, rel):
    p = root / rel
    return p.read_text(errors="ignore") if p.is_file() else ""

def evaluate(karta, root: pathlib.Path):
    violations = []
    orch = _read(root, "runtime/orchestrator.py")
    if not orch:
        return {"status": "N_A", "violations": [], "details": "No admin server (runtime/orchestrator.py) in this bundle."}
    if 'ADMIN_BIND_HOST = os.environ.get("ADMIN_BIND_HOST", "127.0.0.1")' not in orch:
        violations.append({"file": "runtime/orchestrator.py", "fix_hint": "admin server must default-bind loopback (ADMIN_BIND_HOST=127.0.0.1)."})
    if '("0.0.0.0", PORT)' in orch:
        violations.append({"file": "runtime/orchestrator.py", "fix_hint": "admin server still hard-binds 0.0.0.0 — bind ADMIN_BIND_HOST (loopback default)."})
    if "_require_admin_token" not in orch:
        violations.append({"file": "runtime/orchestrator.py", "fix_hint": "mutating endpoints are not fail-closed behind a token (_require_admin_token)."})
    if '"Access-Control-Allow-Origin", "*"' in orch:
        violations.append({"file": "runtime/orchestrator.py", "fix_hint": "wildcard CORS — lock it down (gated ADMIN_CORS_ORIGIN)."})
    compose = _read(root, "deploy/docker-compose.yml")
    if compose and "admin-ui:" in compose:
        if 'profiles: ["admin"]' not in compose:
            violations.append({"file": "deploy/docker-compose.yml", "fix_hint": "admin-ui must not start by default — profiles: [admin]."})
        if '"8080:8080"' in compose:
            violations.append({"file": "deploy/docker-compose.yml", "fix_hint": "admin-ui publishes 0.0.0.0:8080 — bind loopback (127.0.0.1:8080:8080)."})
    t = _read(root, "tests/unit_tests/test_admin_surface_guarded.py")
    if ("def test_admin_server_binds_loopback_by_default" not in t
            or "def test_unauthenticated_mutation_is_fail_closed" not in t
            or "def test_no_wildcard_cors" not in t):
        violations.append({"file": "tests/unit_tests/test_admin_surface_guarded.py", "fix_hint": "runtime proofs for the admin surface are not emitted."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": "Admin server binds loopback by default, no wildcard CORS, mutations fail-closed behind ADMIN_API_TOKEN; docker-compose does not default-start it and binds only 127.0.0.1 (external DD, L7/L8)."}
