"""H_MACROHUB_STANDALONE MacroHub Standalone — a macrohub is a standalone cross-tenant agent (meta-platform tier only)."""
import pathlib
GATE_ID = "H_MACROHUB_STANDALONE"; GATE_NAME = "MacroHub Standalone"; GATE_KIND = "hard"
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

def _vertical(karta):
    md = (karta or {}).get("metadata", {}) or {}
    im = (karta or {}).get("input_model", {}) or {}
    return str(md.get("vertical") or im.get("vertical") or "").lower()

# Vacuously PASS on a hub-less karta — matches the composition attestation.
def applies(karta): return True

def evaluate(karta, root: pathlib.Path):
    hubs = [n.get("id") for n in _nodes(karta) if _is_macrohub(n)]
    vertical = _vertical(karta)
    violations = []
    if vertical != "meta-platform":
        for nid in hubs:
            violations.append({"node": nid, "vertical": vertical,
                               "fix_hint": "inline MacroHub in a domain agent — a MacroHub is a STANDALONE cross-tenant agent, legitimate only in the platform/hub tier (vertical 'meta-platform')."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": f"Checked {len(hubs)} macrohub node(s) against vertical '{vertical or 'unset'}'."}
