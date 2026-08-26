"""H_PORT_CONTRACT_UNIQUE Port-Contract Uniqueness (karta) — unique node ids and unique (node_id, port_id) contracts."""
import pathlib
GATE_ID = "H_PORT_CONTRACT_UNIQUE"; GATE_NAME = "Port-Contract Uniqueness (karta)"; GATE_KIND = "hard"
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

def applies(karta): return bool(_nodes(karta))

def evaluate(karta, root: pathlib.Path):
    violations = []
    seen = set()
    for n in _nodes(karta):
        nid = n.get("id")
        if nid in seen:
            violations.append({"node": nid, "fix_hint": "duplicate node id — node ids must be unique in the karta."})
        seen.add(nid)
        dup_ports = [p for p in set(_ports(n)) if _ports(n).count(p) > 1]
        for p in sorted(dup_ports):
            violations.append({"node": nid, "port": p, "fix_hint": "duplicate port declaration on the same node."})
    pairs = 0
    for nid, bucket in _contracts(karta).items():
        if not isinstance(bucket, dict):
            continue
        norm = {}
        for port_id in bucket.keys():
            key = str(port_id).upper()
            if key in norm:
                violations.append({"node": nid, "port": key,
                                   "fix_hint": "two contracts resolve to the same (node_id, port_id) — keep exactly one."})
            norm[key] = True
            pairs += 1
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": f"Checked {len(seen)} node id(s) and {pairs} (node_id, port_id) contract pair(s) for uniqueness."}
