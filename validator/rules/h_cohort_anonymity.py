"""H_COHORT_ANONYMITY Cohort k-Anonymity — every MO port carries an anonymization contract at or above the doctrine k-floor."""
import pathlib
GATE_ID = "H_COHORT_ANONYMITY"; GATE_NAME = "Cohort k-Anonymity"; GATE_KIND = "hard"
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

DOCTRINE_K_FLOOR = 5

def _floor(karta):
    md = (karta or {}).get("metadata", {}) or {}
    try:
        return max(DOCTRINE_K_FLOOR, int(md.get("k_floor")))
    except (TypeError, ValueError):
        return DOCTRINE_K_FLOOR

def applies(karta): return any("MO" in _ports(n) for n in _nodes(karta))

def evaluate(karta, root: pathlib.Path):
    floor = _floor(karta)
    contracts = _contracts(karta)
    mo_nodes = [n for n in _nodes(karta) if "MO" in _ports(n)]
    violations = []
    for n in mo_nodes:
        nid = n.get("id")
        bucket = contracts.get(nid) or {}
        c = bucket.get("MO") if isinstance(bucket, dict) else None
        anon = (c or {}).get("anonymization_contract") if isinstance(c, dict) else None
        if not isinstance(anon, dict):
            violations.append({"node": nid,
                               "fix_hint": "MO (cohort) port has NO anonymization_contract — cross-tenant output must be k-anonymized."})
            continue
        try:
            k = int(anon.get("k_minimum"))
        except (TypeError, ValueError):
            k = -1
        if k < floor:
            violations.append({"node": nid, "k_minimum": anon.get("k_minimum"), "required": floor,
                               "fix_hint": f"MO anonymization_contract k_minimum below the doctrine k-floor ({floor})."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": f"Checked {len(mo_nodes)} MO port(s) against doctrine k-floor {floor}."}
