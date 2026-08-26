"""H13 Barrier-Sync (karta) — every multi-source XI fan-in declares a barrier with the right branch count."""
import pathlib
GATE_ID = "H13"; GATE_NAME = "Barrier-Sync (karta)"; GATE_KIND = "hard"
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

def _fan_in(karta):
    # MIRROR of the studio's shared derivation (src/lib/studio/bundle/barrierJoins.ts,
    # locked by barrierJoins.test.ts). Semantics: DISTINCT non-routing X-plane
    # sources into <node>.XI; source port must be XO (or absent in node-only edge
    # refs); duplicate edges count once; MacroHub/coordinator XI exempt.
    hubs = {n.get("id") for n in _nodes(karta) if _is_macrohub(n)}
    known = {n.get("id") for n in _nodes(karta)}
    sources = {}
    for e in _edges(karta):
        if str(e.get("target_port", "")).upper() != "XI":
            continue
        if _is_routing(e):
            continue
        sp = str(e.get("source_port", "") or "").upper()
        if sp not in ("", "XO"):
            continue  # X-plane only — a YO/ZO -> XI wiring is never a barrier
        s = e.get("source_agent") or e.get("source_node") or e.get("from")
        t = e.get("target_agent") or e.get("target_node") or e.get("to")
        if known and (s not in known or t not in known):
            continue
        # A MacroHub coordinator's XI is the anonymized cohort funnel: N members'
        # OctaBox.MO feeds converge there and are aggregated per cycle_id/window
        # ASYNCHRONOUSLY (silence is itself a drift signal — the hub can never
        # block waiting for every member). That is windowed aggregation, NOT a
        # synchronous X-compute barrier join, so the coordinator XI is exempt from
        # H13. A genuine X-compute fan-in (two core.XO -> decision.XI) still
        # requires a declared barrier.
        if t in hubs:
            continue
        sources.setdefault(t, set()).add(s)
    return {k: len(v) for k, v in sources.items() if len(v) >= 2}

def applies(karta): return bool(_edges(karta))

def evaluate(karta, root: pathlib.Path):
    sync = (karta or {}).get("sync") or {}
    joins = _fan_in(karta)
    violations = []
    for node_id, fan in sorted(joins.items()):
        decl = sync.get(f"{node_id}.XI")
        if not isinstance(decl, dict) or decl.get("strategy") != "barrier":
            violations.append({"node": node_id, "fan_in": fan,
                               "fix_hint": "multi-source XI fan-in without a declared sync barrier — declare sync['<node>.XI'] with strategy 'barrier'."})
            continue
        if decl.get("expected_branches") != fan:
            violations.append({"node": node_id, "fan_in": fan, "expected_branches": decl.get("expected_branches"),
                               "fix_hint": "barrier expected_branches does not match the number of incoming XI edges."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": f"Checked {len(joins)} multi-source XI join(s) against {len(sync)} declared barrier(s)."}
