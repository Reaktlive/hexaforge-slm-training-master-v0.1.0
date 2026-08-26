"""CCAS tier — the karta tells the truth the handlers execute.

Fas 2.12b (external static review of fleet-1): the declared tier was BOUND
(baked into each gate handler's ccas_decide(action, "<tier>") literal and
gated) but the compiled karta alone could not show it. Now every privileged
node's karta entry carries metadata.ccas_tier from the SAME declaration the
literal is generated from. This test proves the two never drift.
"""
import json
import os
import re


def _karta():
    with open("karta.compiled.json") as f:
        return json.load(f)


def test_every_declared_action_is_tiered_in_the_karta():
    k = _karta()
    declared = {a["name"]: a["tier"] for a in k.get("metadata", {}).get("privileged_actions", []) if a.get("name") and a.get("tier")}
    assert declared, "no declared privileged actions in karta metadata"
    nodes = k.get("topology", {}).get("nodes", [])
    tiered = 0
    for name, tier in declared.items():
        matches = [n for n in nodes
                   if (n.get("metadata", {}) or {}).get("element_role") == name
                   or ("_%s_approval_gate" % name) in n.get("id", "")]
        for n in matches:
            assert (n.get("metadata", {}) or {}).get("ccas_tier") == tier, (name, tier, n.get("id"), n.get("metadata"))
            tiered += 1
    assert tiered > 0, "no privileged node carries ccas_tier — the karta is silent again"


def test_karta_tier_matches_the_handler_literal():
    k = _karta()
    nodes = k.get("topology", {}).get("nodes", [])
    checked = 0
    for n in nodes:
        meta = n.get("metadata", {}) or {}
        if "approval_gate" not in n.get("id", "") or not meta.get("ccas_tier"):
            continue
        handler = os.path.join("src", "nodes", n["id"], "handler.py")
        if not os.path.isfile(handler):
            continue
        with open(handler) as f:
            src = f.read()
        m = re.search(r'ccas_decide[(][^,]+, *"([a-z0-9_]+)"', src)
        assert m, (n["id"], "gate handler carries no ccas_decide tier literal")
        assert m.group(1) == meta["ccas_tier"], (n["id"], m.group(1), meta["ccas_tier"])
        checked += 1
    assert checked > 0, "no gate handlers checked — parity test would be vacuous"
