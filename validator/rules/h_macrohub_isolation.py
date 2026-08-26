"""H_MACROHUB_ISOLATION MacroHub Isolation — a macrohub never sits on the primary X chain."""
import pathlib
GATE_ID = "H_MACROHUB_ISOLATION"; GATE_NAME = "MacroHub Isolation"; GATE_KIND = "hard"
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

# Vacuously PASS on a hub-less karta — the composition attestation records a
# PASS (0 violations), so offline re-verification must match, not report N_A.
def applies(karta): return True

def evaluate(karta, root: pathlib.Path):
    hubs = {n.get("id") for n in _nodes(karta) if _is_macrohub(n)}
    violations = []; checked = 0
    for e in _edges(karta):
        sa = e.get("source_agent") or e.get("from"); ta = e.get("target_agent") or e.get("to")
        sp = str(e.get("source_port", "")).upper(); tp = str(e.get("target_port", "")).upper()
        if sa not in hubs and ta not in hubs:
            continue
        checked += 1
        # A MacroHub couples to the fleet ONLY through its OWN XI (inbound) / XO
        # (outbound) — the N6 protocol ports. The anonymized cohort plane is the
        # OctaBox.MO -> hub.XI / hub.XO -> OctaBox.MI wiring: the hub side is X,
        # the OctaBox side is M. Byte-aligned with the composition-time validator
        # (hbDoctrineValidator.checkH_MacroHubIsolation): an edge INTO a hub MUST
        # target XI, an edge OUT OF a hub MUST source XO. The old check forbade
        # ANY X port on a hub-incident edge — but a coordinator (MacroHub, 6-port
        # HexaBox: no MI/MO) has NOTHING BUT X/Y/Z ports, so its own doctrine-legal
        # XI/XO coupling was mis-flagged. That false FAIL never surfaced because no
        # real coordinator had been emitted + offline-verified before the fixed
        # Fleet-Command template; it is now aligned with the authoritative TS gate.
        if ta in hubs and tp != "XI":
            violations.append({"edge": f"{sa}.{sp}->{ta}.{tp}",
                               "fix_hint": f"edge into MacroHub {ta} uses port {tp}, only XI allowed — a MacroHub receives the anonymized cohort plane on XI only (N6 isolation)."})
        if sa in hubs and sp != "XO":
            violations.append({"edge": f"{sa}.{sp}->{ta}.{tp}",
                               "fix_hint": f"edge out of MacroHub {sa} uses port {sp}, only XO allowed — a MacroHub redistributes on XO only (N6 isolation)."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": f"Checked {checked} macrohub-incident edge(s) across {len(hubs)} macrohub node(s)."}
