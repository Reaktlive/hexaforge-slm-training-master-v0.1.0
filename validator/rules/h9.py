"""H9 No Orphan Nodes — every node participates in at least one edge."""
import pathlib
GATE_ID = "H9"; GATE_NAME = "No Orphan Nodes"; GATE_KIND = "hard"
GATE_CATEGORY = "doctrine"

def _nodes(karta):
    return (karta or {}).get("topology", {}).get("nodes", []) or []

def _edges(karta):
    return (karta or {}).get("topology", {}).get("edges", []) or []

def _is_routing(e):
    """Fas 3 · Delsteg 1 — an action_selector branch. EXACTLY ONE routing edge
    out of a selector carries data per event, so routing edges are conditional,
    never concurrent: they must stay OUT of barrier fan-in accounting."""
    return str((e or {}).get("kind", "")).lower() == "routing"


def _ports(n):
    p = n.get("ports") or []
    return [str(x).upper() for x in p if isinstance(x, str)]

def _role(n):
    return str(n.get("role") or (n.get("metadata") or {}).get("role") or "").lower()

def _is_macrohub(n):
    # Fas 3.49 — STRUCTURAL classification ONLY, byte-aligned with the authoritative
    # composition-time validator (hbDoctrineValidator: a MacroHub is the coordinator
    # role / MacroHub element type). The old `"macrohub" in id` substring clause
    # mis-fired on a STANDALONE MacroHub AGENT — every node is named
    # macrohub_fleet_command_* — flagging its whole legitimate internal X-chain as an
    # isolation violation. That was a FALSE FAIL the composition attestation never
    # produced, so the shipped 100/100 signed report was not reproducible by this
    # offline verifier (external DD P0). A genuine inline MacroHub node in a DOMAIN
    # agent still carries type MacroHub / role coordinator and is still caught.
    if str(n.get("type") or "").lower() == "macrohub":
        return True
    if _role(n) == "coordinator":
        return True
    if (n.get("metadata") or {}).get("is_macrohub"):
        return True
    return False

def _contracts(karta):
    c = (karta or {}).get("contracts") or {}
    return c if isinstance(c, dict) else {}

def applies(karta): return len(_nodes(karta)) > 1

def evaluate(karta, root: pathlib.Path):
    nodes = _nodes(karta); edges = _edges(karta)
    touched = set()
    for e in edges:
        touched.add(e.get("source_agent") or e.get("from"))
        touched.add(e.get("target_agent") or e.get("to"))
    violations = []
    for n in nodes:
        if n.get("id") not in touched:
            violations.append({"node": n.get("id"),
                               "fix_hint": "node is neither source nor target of any edge — wire it into the karta or remove it."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": f"Checked {len(nodes)} nodes against {len(edges)} edges; {len(nodes) - len(violations)} connected."}
