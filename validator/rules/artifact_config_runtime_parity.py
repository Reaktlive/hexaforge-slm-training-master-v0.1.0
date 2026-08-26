"""ARTIFACT_CONFIG_RUNTIME_PARITY — generated config does not lie about runtime.

Fas 2.13d (external DD, Peter). (1) BARRIER_TIMEOUT_MS was hardcoded 5000 while
.env.example documented 120000 — the env var was never read. Now it is read from
the environment with a default equal to .env.example. (2) The k8s manifest
defaulted to replicas:2 despite process-local state; it now defaults to a single
replica. Static checks (the emitted runtime test proves the env-read).
"""
import pathlib
GATE_ID = "ARTIFACT_CONFIG_RUNTIME_PARITY"; GATE_NAME = "Config/Runtime Parity (env knobs are read; single-replica default for process-local state)"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"

def applies(karta):
    return True

def _read(root, rel):
    p = root / rel
    return p.read_text(errors="ignore") if p.is_file() else ""

def evaluate(karta, root: pathlib.Path):
    violations = []
    checked = 0
    orch = _read(root, "src/shared/orchestrator.py")
    if "BARRIER_TIMEOUT_MS" in orch:
        checked += 1
        if 'os.environ.get("BARRIER_TIMEOUT_MS"' not in orch:
            violations.append({"file": "src/shared/orchestrator.py", "fix_hint": "BARRIER_TIMEOUT_MS is not read from the environment — the documented knob is inert."})
        # default (from orchestrator) must equal .env.example (no drift)
        env_file = _read(root, ".env.example")
        try:
            runtime_default = orch.split('os.environ.get("BARRIER_TIMEOUT_MS", "')[1].split('"')[0]
        except IndexError:
            runtime_default = None
        doc_val = None
        for line in env_file.splitlines():
            if line.strip().startswith("BARRIER_TIMEOUT_MS="):
                doc_val = line.strip().split("=", 1)[1].strip()
                break
        if runtime_default is not None and doc_val is not None and runtime_default != doc_val:
            violations.append({"file": ".env.example", "fix_hint": "BARRIER_TIMEOUT_MS default %s disagrees with .env.example %s — config/runtime drift." % (runtime_default, doc_val)})
    k8s = _read(root, "deploy/k8s/deployment.yaml")
    if "replicas:" in k8s:
        checked += 1
        rep = None
        for line in k8s.splitlines():
            if line.strip().startswith("replicas:"):
                rep = line.strip().split(":", 1)[1].strip()
                break
        if rep != "1":
            violations.append({"file": "deploy/k8s/deployment.yaml", "fix_hint": "replicas: %s with process-local state — default to 1 or bind external state." % rep})
        if "external state" not in k8s.lower():
            violations.append({"file": "deploy/k8s/deployment.yaml", "fix_hint": "no external-state-binding note for scaling >1."})
    t = _read(root, "tests/unit_tests/test_config_runtime_parity.py")
    if "def test_barrier_timeout_is_read_from_env" not in t:
        violations.append({"file": "tests/unit_tests/test_config_runtime_parity.py", "fix_hint": "runtime proof that BARRIER_TIMEOUT_MS is read from env is not emitted."})
    if checked == 0 and not violations:
        return {"status": "N_A", "violations": [], "details": "No barrier and no k8s manifest — nothing to parity-check."}
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": "BARRIER_TIMEOUT_MS is read from env with a default equal to .env.example; k8s defaults to a single replica (process-local state) — generated config matches runtime (external DD, L8)."}
