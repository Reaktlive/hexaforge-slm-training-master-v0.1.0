"""H12 Schema Compatibility (karta) — both endpoints of every edge carry a contract on the same major version."""
import pathlib, re
GATE_ID = "H12"; GATE_NAME = "Schema Compatibility (karta)"; GATE_KIND = "hard"
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

def _contract(karta, node_id, port):
    b = _contracts(karta).get(node_id) or {}
    if not isinstance(b, dict):
        return None
    for key in (str(port).upper(), str(port).lower()):
        c = b.get(key)
        if isinstance(c, dict):
            return c
    return None

def _major(c):
    v = c.get("schema_version") or c.get("_contract_version") or c.get("version")
    m = re.match(r"^\s*v?(\d+)", str(v or ""))
    return m.group(1) if m else None

def applies(karta): return bool(_contracts(karta)) and bool(_edges(karta))

def evaluate(karta, root: pathlib.Path):
    violations = []; checked = 0
    for e in _edges(karta):
        sa = e.get("source_agent") or e.get("from"); sp = e.get("source_port")
        ta = e.get("target_agent") or e.get("to"); tp = e.get("target_port")
        sc = _contract(karta, sa, sp); tc = _contract(karta, ta, tp)
        label = f"{sa}.{sp}->{ta}.{tp}"
        if sc is None or tc is None:
            violations.append({"edge": label, "fix_hint": "missing port contract on one or both edge endpoints — every wired port must carry a contract."})
            continue
        checked += 1
        smaj, tmaj = _major(sc), _major(tc)
        if smaj is not None and tmaj is not None and smaj != tmaj:
            violations.append({"edge": label, "source_major": smaj, "target_major": tmaj,
                               "fix_hint": "incompatible contract major versions across an edge — re-pin both endpoints to the same major."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": f"Checked {len(_edges(karta))} edge(s); {checked} with contracts on both endpoints."}
