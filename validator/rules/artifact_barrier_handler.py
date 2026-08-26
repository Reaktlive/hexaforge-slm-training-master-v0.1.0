"""H5 Barrier-Sync — SUBSTANCE: verify run_pipeline really coordinates each declared barrier join.

Strips comments + string literals from runtime/api_server.py before any text
analysis, so a word in a comment can never count as coordination (the old
keyword grep was gameable by emitting '# barrier' in a comment).
"""
import re, pathlib
GATE_ID = "ARTIFACT_BARRIER_HANDLER"; GATE_NAME = "Barrier-Sync"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"

def _strip_py(text: str) -> str:
    """Remove # comments + (triple/single/double) string literals, replacing
    each removed span with a space so call tokens like 'run_branches(' survive.
    Single-pass scanner — correct for the constructs generated code emits."""
    out = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "#":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c == '"' or c == "'":
            q = c
            triple = text[i + 1 : i + 3] == q * 2
            closer = q * 3 if triple else q
            i += len(closer)
            while i < n:
                if text[i] == "\\":
                    i += 2
                    continue
                if text.startswith(closer, i):
                    i += len(closer)
                    break
                i += 1
            out.append(" ")
            continue
        out.append(c)
        i += 1
    return "".join(out)

def _py_alias(node_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "_", node_id)

def applies(karta):
    sync = karta.get("sync", {}) or {}
    return any(isinstance(v, dict) and v.get("strategy") == "barrier" for v in sync.values())

def evaluate(karta, root: pathlib.Path):
    violations = []
    api = root / "runtime" / "api_server.py"
    api_code = _strip_py(api.read_text(errors="ignore")) if api.exists() else ""
    runs_branches = bool(re.search(r"\brun_branches\s*\(", api_code))
    for key, spec in (karta.get("sync", {}) or {}).items():
        if not (isinstance(spec, dict) and spec.get("strategy") == "barrier"):
            continue
        node_id, port = key.split(".") if "." in key else (key, "xi")
        edges_in = [e for e in karta["topology"]["edges"]
                    if e["target_agent"] == node_id and e["target_port"].lower() == port.lower()
                    and str(e.get("kind", "")).lower() != "routing"]

        if spec.get("expected_branches") and spec["expected_branches"] != len(edges_in):
            violations.append({"sync": key, "fix_hint": f"expected_branches={spec['expected_branches']} but {len(edges_in)} edges in."})
        if not api_code:
            violations.append({"sync": key, "node": node_id, "file": "runtime/api_server.py",
                               "fix_hint": "runtime/api_server.py missing — cannot prove barrier coordination."})
            continue
        if not runs_branches:
            violations.append({"sync": key, "node": node_id, "file": "runtime/api_server.py",
                               "fix_hint": "run_pipeline never CALLS run_branches() — barrier declared but not coordinated (keyword theatre)."})
            continue
        alias = _py_alias(node_id)
        merge_re = re.compile(r"env_join_" + re.escape(alias) + r"\s*=")
        call_re = re.compile(r"\b" + re.escape(alias) + r"\.handle_xi\s*\(\s*env_join_" + re.escape(alias))
        if not (merge_re.search(api_code) and call_re.search(api_code)):
            violations.append({"sync": key, "node": node_id, "file": "runtime/api_server.py",
                               "fix_hint": f"run_pipeline does not feed the merged barrier envelope into {node_id}.handle_xi — declared barrier, not coordinated as a fan-in join."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": "Barrier coordination verified against comment-stripped run_pipeline."}
