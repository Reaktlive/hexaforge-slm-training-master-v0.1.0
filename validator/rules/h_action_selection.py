"""H_ACTION_SELECTION — a privileged gate is REACHABLE via a typed proposal,
INVOKED only when the proposal selects it.

Fas 3 · Delsteg 2b doctrine gate. Offline re-verifiable: reads
karta.compiled.json + runtime/api_server.py (comment-stripped) and asserts, when
the karta composed an action_selector:

  (i)   run_pipeline routes through the selector — the module-level
        _ACTION_ROUTES table is present and non-empty AND the selector step
        (_sel_route) exists in run_pipeline;
  (ii)  NO privileged gate's handle_xi is invoked UNCONDITIONALLY — every
        `await <gate>.handle_xi(` must live inside the selector routing block,
        guarded by `if _sel_route == "<gate>":`, never at the unconditional
        main-flow indentation;
  (iii) an unknown selection is FAIL-CLOSED (unroutable_action).

Vacuous PASS when the karta declares no action_selector.
"""
import re, pathlib
GATE_ID = "H_ACTION_SELECTION"; GATE_NAME = "Action Selection (typed proposal routes exactly one gate)"; GATE_KIND = "hard"
GATE_CATEGORY = "doctrine"

PRIVILEGED_ROLES = ("approval_gate", "release_gate", "command_generator")
SELECTOR_ROLE = "action_selector"


def _strip_comments(text: str) -> str:
    """Remove `#` comments, preserve every newline and all indentation.

    String literals are KEPT (the guard we look for embeds the gate id as a
    string), but a comment can never satisfy this gate.
    """
    out = []
    i, n = 0, len(text)
    in_str = None
    while i < n:
        c = text[i]
        if in_str:
            if c == "\\":
                out.append(c)
                if i + 1 < n:
                    out.append(text[i + 1])
                i += 2
                continue
            if text.startswith(in_str, i):
                out.append(in_str)
                i += len(in_str)
                in_str = None
                continue
            out.append(c)
            i += 1
            continue
        if c == "#":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c in ('"', "'"):
            in_str = c * 3 if text[i + 1 : i + 3] == c * 2 else c
            out.append(in_str)
            i += len(in_str)
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _role(n) -> str:
    return str((n.get("metadata") or {}).get("element_role") or "").lower()


def _run_pipeline_body(src: str):
    lines = src.split("\n")
    start = None
    for idx, ln in enumerate(lines):
        if re.match(r"\s*(async\s+)?def\s+run_pipeline\s*\(", ln):
            start = idx
            break
    if start is None:
        return None
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        ln = lines[idx]
        if ln.strip() and not ln[0].isspace() and not ln.lstrip().startswith(")"):
            end = idx
            break
    return lines[start:end]


def _indent(ln: str) -> int:
    return len(ln) - len(ln.lstrip(" "))


def applies(karta): return True


def evaluate(karta, root: pathlib.Path):
    violations = []
    nodes = karta.get("topology", {}).get("nodes", [])
    selectors = [n for n in nodes if _role(n) == SELECTOR_ROLE]
    gates = [n for n in nodes if _role(n) in PRIVILEGED_ROLES]

    if not selectors or not gates:
        return {"status": "PASS", "violations": [],
                "details": "Vacuous PASS — karta declares no action_selector and/or no privileged gates."}

    api = root / "runtime" / "api_server.py"
    if not api.exists():
        return {"status": "FAIL",
                "violations": [{"fix_hint": "runtime/api_server.py missing — selector routing cannot be re-verified."}],
                "details": "runtime/api_server.py missing."}

    src = _strip_comments(api.read_text(errors="ignore"))

    # (i) module-level routing table present and non-empty.
    m = re.search(r"_ACTION_ROUTES[^=\n]*=\s*\{([^}]*)\}", src)
    if not m or ":" not in m.group(1):
        violations.append({"fix_hint": "_ACTION_ROUTES routing table missing or empty — the selector cannot route a typed proposal to any gate."})

    body_lines = _run_pipeline_body(src)
    if body_lines is None:
        return {"status": "FAIL",
                "violations": [{"fix_hint": "run_pipeline not found in runtime/api_server.py."}],
                "details": "run_pipeline missing."}
    body = "\n".join(body_lines)

    if "_sel_route" not in body:
        violations.append({"fix_hint": "run_pipeline contains no selector step (_sel_route) — privileged gates are not routed through the ActionProposal selector."})

    # (iii) fail-closed on an unknown selection.
    if "unroutable_action" not in body:
        violations.append({"fix_hint": "run_pipeline has no fail-closed branch for an unroutable action — an unknown selection must abort, never bypass its gate."})

    # (ii) every privileged handle_xi call must be GUARDED by the selector.
    for g in gates:
        gid = g["id"]
        call_re = re.compile(r"await\s+" + re.escape(gid) + r"\s*\.handle_xi\s*\(")
        guard_re = re.compile(r"^\s*if\s+_sel_route\s*==\s*[\"']" + re.escape(gid) + r"[\"']\s*:")
        found = False
        for idx, ln in enumerate(body_lines):
            if not call_re.search(ln):
                continue
            found = True
            ind = _indent(ln)
            if ind <= 8:
                violations.append({"node": gid, "file": "runtime/api_server.py",
                                   "fix_hint": "privileged gate '%s' handle_xi is invoked UNCONDITIONALLY in run_pipeline (main-flow indentation) — it must only run when the ActionProposal selects it." % gid})
                continue
            guarded = False
            for back in range(idx - 1, -1, -1):
                prev = body_lines[back]
                if not prev.strip():
                    continue
                if _indent(prev) < ind:
                    guarded = bool(guard_re.match(prev))
                    break
            if not guarded:
                violations.append({"node": gid, "file": "runtime/api_server.py",
                                   "fix_hint": "privileged gate '%s' handle_xi is not guarded by `if _sel_route == \"%s\":` — no privileged gate may be called without a matching proposal." % (gid, gid)})
        if not found:
            violations.append({"node": gid, "file": "runtime/api_server.py",
                               "fix_hint": "privileged gate '%s' is never invoked in run_pipeline — it must be REACHABLE via the selector." % gid})

    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": "Checked %d privileged gate(s) behind %d action_selector(s): routed via _ACTION_ROUTES, guarded by _sel_route, fail-closed on unknown selection." % (len(gates), len(selectors))}
