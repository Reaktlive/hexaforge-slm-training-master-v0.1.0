"""ARTIFACT_SINGLE_GUARDED_ENTRYPOINT — the deploy default has no open route.

Fas 2.13a (external DD P0). start.sh served src.main:app, which build_app()
assembled as a SECOND unauthenticated app (214 raw node routers incl. YO
side-effects). Now build_app() returns the guarded runtime/api_server.py app;
no raw router is served. Static checks (the emitted runtime test proves the
behaviour dynamically):
  1. build_app() returns the guarded app and mounts no per-node routers.
  2. src/main.py serves build_app().
  3. the guarded app carries Depends(zt_guard) routes.
  4. deploy entrypoints resolve to a guarded app.
  5. the 401-every-route runtime test is emitted.
"""
import pathlib, re
GATE_ID = "ARTIFACT_SINGLE_GUARDED_ENTRYPOINT"; GATE_NAME = "Single Guarded Entrypoint (no unauthenticated route surface)"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"

def applies(karta):
    return True

def _read(root, rel):
    p = root / rel
    return p.read_text(errors="ignore") if p.is_file() else ""

def evaluate(karta, root: pathlib.Path):
    violations = []
    orch = _read(root, "src/shared/orchestrator.py")
    if not orch:
        violations.append({"file": "src/shared/orchestrator.py", "fix_hint": "orchestrator missing."})
    else:
        if "from runtime.api_server import app" not in orch:
            violations.append({"file": "src/shared/orchestrator.py", "fix_hint": "build_app() does not return the guarded app (deferred import of runtime.api_server)."})
        if "app.include_router(" in orch or re.search(r"from src\.nodes\.[^\n]+import router", orch):
            violations.append({"file": "src/shared/orchestrator.py", "fix_hint": "build_app() still mounts raw per-node routers — the unauthenticated bypass surface."})
    main = _read(root, "src/main.py")
    if not main:
        violations.append({"file": "src/main.py", "fix_hint": "src/main.py missing."})
    elif "build_app()" not in main:
        violations.append({"file": "src/main.py", "fix_hint": "src/main.py must serve build_app() (the guarded app)."})
    api = _read(root, "runtime/api_server.py")
    if "Depends(zt_guard(" not in api:
        violations.append({"file": "runtime/api_server.py", "fix_hint": "guarded app carries no Depends(zt_guard) routes."})
    if "ENABLE_API_DOCS" not in api:
        violations.append({"file": "runtime/api_server.py", "fix_hint": "OpenAPI docs/schema not gated (ENABLE_API_DOCS) — unauthenticated route-map leak."})
    start = _read(root, "deploy/start.sh")
    if start and not re.search(r"python -m (src\.main|runtime\.serve)", start):
        violations.append({"file": "deploy/start.sh", "fix_hint": "start.sh must launch a guarded entrypoint."})
    serve = _read(root, "runtime/serve.py")
    if serve and "runtime.api_server:app" not in serve:
        violations.append({"file": "runtime/serve.py", "fix_hint": "runtime.serve must serve the guarded api_server app."})
    t = _read(root, "tests/unit_tests/test_single_guarded_entrypoint.py")
    if ("def test_deploy_entrypoint_is_the_guarded_app" not in t
            or "def test_every_served_route_rejects_unauthenticated_caller" not in t
            or "def test_no_raw_side_effect_routes_are_served" not in t):
        violations.append({"file": "tests/unit_tests/test_single_guarded_entrypoint.py", "fix_hint": "runtime proofs for the single guarded entrypoint are not emitted."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": "One guarded app: build_app() -> runtime/api_server.py, no raw per-node router served, deploy entrypoints converge on it, emitted runtime test proves every served route rejects an unauthenticated caller (P0 closed by construction, L7/L8)."}
