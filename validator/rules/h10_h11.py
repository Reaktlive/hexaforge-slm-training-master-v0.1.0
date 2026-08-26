"""H10_H11 Bookend & Single XI — exactly one ingress + one egress; ingress.XI is the sole external entry."""
import pathlib
GATE_ID = "H10_H11"; GATE_NAME = "Bookend & Single XI"; GATE_KIND = "hard"
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

def _kind(n):
    r = _role(n)
    if r in ("ingress", "egress"):
        return r
    # id-substring fallback ONLY for OctaBox bookends — a HexaBox core node
    # whose name contains 'intake'/'egress' (e.g. case_intake_validation,
    # pii_egress_filtering) is NEVER a boundary.
    if str(n.get("type", "")) == "OctaBox":
        nid = str(n.get("id", "")).lower()
        if "ingress" in nid or "intake" in nid:
            return "ingress"
        if "egress" in nid:
            return "egress"
    return ""

def applies(karta): return bool(_nodes(karta))

def evaluate(karta, root: pathlib.Path):
    nodes = _nodes(karta); edges = _edges(karta)
    ingress = [n for n in nodes if _kind(n) == "ingress"]
    egress = [n for n in nodes if _kind(n) == "egress"]
    violations = []
    if len(ingress) != 1:
        violations.append({"count": len(ingress),
                           "fix_hint": "karta must declare EXACTLY one ingress OctaBox (H10)."})
    if len(egress) != 1:
        violations.append({"count": len(egress),
                           "fix_hint": "karta must declare EXACTLY one egress OctaBox (H11)."})
    # Single XI — the ingress OctaBox is the ONLY external entry point. Any
    # other node with an XI port must be reachable from inside the karta (any
    # incoming edge); a node with an XI and NO inbound edge at all is a second
    # external door. Macrohubs are exempt (standalone cross-tenant tier).
    inbound = set()
    for e in edges:
        inbound.add(e.get("target_agent") or e.get("to"))
    ing_id = ingress[0].get("id") if len(ingress) == 1 else None
    # Bookends MUST be OctaBoxes (8 ports incl. M) — a HexaBox bookend cannot
    # carry the cross-tenant M plane.
    for n in ingress + egress:
        if str(n.get("type", "")) != "OctaBox":
            violations.append({"node": n.get("id"), "type": n.get("type"),
                               "fix_hint": "bookend node (ingress/egress) must be of type OctaBox (H10/H11)."})
    # No internal edge may feed the ingress node's XI — that port is reserved
    # for the single EXTERNAL entry point.
    for e in edges:
        ta = e.get("target_agent") or e.get("to")
        tp = str(e.get("target_port", "")).upper()
        if ing_id is not None and ta == ing_id and tp == "XI":
            sa = e.get("source_agent") or e.get("from")
            violations.append({"edge": f"{sa}->{ta}.{tp}",
                               "fix_hint": "internal edge feeds the ingress OctaBox XI — that port is reserved for the single external entry point (H10)."})
    for n in nodes:
        nid = n.get("id")
        if nid == ing_id or "XI" not in _ports(n):
            continue
        if nid not in inbound and not _is_macrohub(n):
            violations.append({"node": nid,
                               "fix_hint": "node exposes an XI with no inbound edge — a second external entry point; external input must enter through the ingress OctaBox only (single-XI doctrine)."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": f"Checked {len(nodes)} nodes: {len(ingress)} ingress, {len(egress)} egress, {len(inbound)} internally-fed node(s)."}
