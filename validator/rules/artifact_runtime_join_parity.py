"""ARTIFACT_RUNTIME_JOIN_PARITY — the runtime join must match the declared barrier.

For every barrier in karta.sync, runtime/api_server.py must build
env_join_<alias> merging EXACTLY expected_branches predecessors, with no
commented-out "not schedulable" predecessor, and feed it into <alias>.handle_xi.
"""
import re, pathlib
GATE_ID = "ARTIFACT_RUNTIME_JOIN_PARITY"; GATE_NAME = "Runtime Join Parity"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"

def _py_alias(node_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "_", node_id)

def applies(karta):
    sync = karta.get("sync", {}) or {}
    return any(isinstance(v, dict) and v.get("strategy") == "barrier" for v in sync.values())

def evaluate(karta, root: pathlib.Path):
    violations = []
    sync = karta.get("sync", {}) or {}
    barriers = [(k, v) for k, v in sync.items() if isinstance(v, dict) and v.get("strategy") == "barrier"]
    api = root / "runtime" / "api_server.py"
    if not api.exists():
        return {"status": "FAIL",
                "violations": [{"file": "runtime/api_server.py",
                                "fix_hint": "runtime/api_server.py missing — cannot prove join parity."}],
                "details": "No runtime to inspect."}
    text = api.read_text(errors="ignore")

    for key, spec in barriers:
        node_id = key.split(".", 1)[0]
        alias = _py_alias(node_id)
        expected = spec.get("expected_branches")
        start = text.find("env_join_%s = {" % alias)
        if start < 0:
            violations.append({"sync": key, "node": node_id,
                               "fix_hint": "No env_join_%s merge emitted for a declared barrier." % alias})
            continue
        end = text.find("}},", start)
        block = text[start:end if end >= 0 else len(text)]
        stale = [l for l in block.split("\n") if "not schedulable" in l]
        if stale:
            violations.append({"sync": key, "node": node_id,
                               "fix_hint": "env_join_%s comments out %d declared predecessor(s) as 'not schedulable'." % (alias, len(stale))})
        merged = len(re.findall(r'^\s+"[^"]+":\s*\(', block, re.M))
        if isinstance(expected, int) and merged != expected:
            violations.append({"sync": key, "node": node_id,
                               "fix_hint": "env_join_%s merges %d branch(es) but karta declares expected_branches=%s." % (alias, merged, expected)})
        if not re.search(r"\b%s\.handle_xi\s*\(\s*env_join_%s" % (alias, alias), text):
            violations.append({"sync": key, "node": node_id,
                               "fix_hint": "env_join_%s is never fed into %s.handle_xi." % (alias, node_id)})

    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": "Runtime join parity verified for %d declared barrier(s)." % len(barriers)}
