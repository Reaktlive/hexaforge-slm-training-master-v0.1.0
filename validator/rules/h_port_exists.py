"""H_PORT_EXISTS Port Existence (karta) — every edge endpoint port is declared on its node."""
import pathlib
GATE_ID = "H_PORT_EXISTS"; GATE_NAME = "Port Existence (karta)"; GATE_KIND = "hard"
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

def applies(karta): return bool(_edges(karta))

def evaluate(karta, root: pathlib.Path):
    ports = {n.get("id"): _ports(n) for n in _nodes(karta)}
    violations = []
    for e in _edges(karta):
        for node_key, port_key, side in (("source_agent", "source_port", "source"), ("target_agent", "target_port", "target")):
            nid = e.get(node_key) or e.get("from" if side == "source" else "to")
            p = str(e.get(port_key, "")).upper()
            if nid not in ports:
                violations.append({"edge": f"{e.get('source_agent')}.{e.get('source_port')}->{e.get('target_agent')}.{e.get('target_port')}",
                                   "fix_hint": f"edge references unknown node '{nid}'."})
            elif p not in ports[nid]:
                violations.append({"node": nid, "port": p,
                                   "fix_hint": f"node '{nid}' does not declare port '{p}' — declare it or re-wire the edge."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": f"Checked {2 * len(_edges(karta))} edge endpoint(s) against {len(ports)} node port declaration(s)."}
