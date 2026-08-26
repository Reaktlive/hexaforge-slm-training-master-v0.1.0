"""H_PRIVILEGED_ACTION_DECLARED — every privileged action declared + CCAS-gated.

CORE_DOCTRINE_REMINDER §3 (JOB-FIRST). Structural + bidirectional; never reads a
prompt. A privileged action-emitting node (approval_gate / release_gate /
command_generator) must be backed by a declared privileged_action carrying a
CCAS tier, AND its handler must CALL ccas_decide(...) on the side-effect path
(comment-stripped). An ungated {"ok": True} privileged handler FAILs.
"""
import re, pathlib
GATE_ID = "H_PRIVILEGED_ACTION_DECLARED"; GATE_NAME = "Privileged Action Declared + CCAS-Gated"; GATE_KIND = "hard"
GATE_CATEGORY = "doctrine"

PRIVILEGED_ROLES = ("approval_gate", "release_gate", "command_generator")
_ID_RE = re.compile(r"(approval_gate|release_gate|command_generator|cmd_gen|approval_hexa)", re.I)

def _strip_py(text: str) -> str:
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

def _node_is_privileged(n) -> bool:
    er = (n.get("metadata") or {}).get("element_role")
    if isinstance(er, str) and er in PRIVILEGED_ROLES:
        return True
    if er is None:
        return bool(_ID_RE.search(str(n.get("id", ""))))
    return False

def applies(karta): return True

def evaluate(karta, root: pathlib.Path):
    violations = []
    nodes = karta.get("topology", {}).get("nodes", [])
    declared = (karta.get("metadata", {}) or {}).get("privileged_actions") or []
    declared_with_tier = [a for a in declared if isinstance(a, dict) and a.get("tier")]
    privileged_nodes = [n for n in nodes if _node_is_privileged(n)]

    # (A.1) Forward — privileged node requires a declared action+tier.
    if privileged_nodes and not declared_with_tier:
        for n in privileged_nodes:
            violations.append({"node": n["id"],
                "fix_hint": "privileged action-emitting node has NO declared privileged_action with a CCAS tier (CORE_DOCTRINE_REMINDER §3) — declare it in karta.privileged_actions or remove the node."})

    # (A.2) Reverse — declared action requires an executing privileged node.
    if declared_with_tier and not privileged_nodes:
        for a in declared_with_tier:
            violations.append({"node": a.get("name"),
                "fix_hint": f"declared privileged_action '{a.get('name')}' (tier={a.get('tier')}) has NO corresponding privileged node — a declared privileged action must have a gated executor."})

    # (A.3) Fas 3.20 — A DECLARED ACTION MUST NAME WHAT IT ACTS ON.
    # Found by scrutinising a generated agent: it shipped a privileged action
    # called literally "delete" — a bare destructive verb with no object. Such a
    # name cannot be reasoned about by anything downstream: not by the tier
    # ladder deciding how many humans must sign, not by an approver reading the
    # queue and deciding whether to release it, not by the audit chain that is
    # supposed to record WHAT was done. "delete" is not an action, it is a mood.
    #
    # The rule is deliberately mechanical rather than semantic: a declared
    # action name must carry at least a verb and an object (two snake_case
    # tokens). That is a doctrine choice, not a truth about language — but it is
    # checkable, it cannot drift, and every legitimate action in every agent
    # generated so far already satisfies it (isolate_endpoint,
    # restore_production_volume, tag_suspect_snapshots, quarantine_message).
    for a in declared_with_tier:
        name = str(a.get("name") or "").strip()
        if name and len([t for t in name.split("_") if t]) < 2:
            violations.append({"node": name, "tier": a.get("tier"),
                "fix_hint": f"privileged action '{name}' is a bare verb with no object — an approver, the tier ladder and the audit chain must all be able to tell WHAT it acts on; name it '<verb>_<object>'."})

    # (B) SUBSTANCE — handler must CALL ccas_decide on a side-effect handler.
    call_re = re.compile(r"\bccas_decide\s*\(")
    def_re = re.compile(r"(?:async\s+)?def\s+(handle_xo|handle_yo)\s*\(")
    for n in privileged_nodes:
        h = root / "src" / "nodes" / n["id"] / "handler.py"
        if not h.exists():
            violations.append({"node": n["id"], "fix_hint": "handler.py missing for privileged node."}); continue
        code = _strip_py(h.read_text(errors="ignore"))
        # Require ccas_decide somewhere AND a side-effect handler present.
        if not (def_re.search(code) and call_re.search(code)):
            violations.append({"node": n["id"], "file": str(h),
                "fix_hint": "privileged node handler never CALLS ccas_decide() on a side-effect handler (handle_xo/handle_yo) — an ungated {\"ok\": True} privileged handler is forbidden (CORE_DOCTRINE_REMINDER §3)."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": f"Checked {len(privileged_nodes)} privileged node(s) vs {len(declared_with_tier)} declared action(s); executable ccas_decide() required on each privileged handler (comment-stripped)."}
