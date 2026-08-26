"""ARTIFACT_MO_CONTRACT_E2E — the cohort boundary (MO) proven as its own claim.

Five statically-verifiable system claims (L7 Portkonformanslagen):
  1. The release is built CONTRACT-DRIVEN (build_release(contract=ac)).
  2. The release is validated against the port's OWN generated model,
     fail-closed (<Node>MoSchema(** + ValidationError + release_error hold).
  3. Below k nothing is emitted (release = None until released).
  4. Store metadata (ts/tenant_cohort_key) never leaves the boundary, and
     k_count counts DISTINCT pseudonymised tenants.
  5. The runtime proofs (release shape + distinct-tenant k) are emitted
     with every MO bundle.
"""
import pathlib, re
GATE_ID = "ARTIFACT_MO_CONTRACT_E2E"; GATE_NAME = "MO Contract E2E (cohort boundary)"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"

def _pascal(s: str) -> str:
    return "".join(p[:1].upper() + p[1:] for p in re.split(r"[_\-]", s) if p)

def _mo_egress_nodes(karta):
    out = []
    for n in karta.get("topology", {}).get("nodes", []):
        ports = [str(p).upper() for p in (n.get("ports") or [])]
        if "MO" in ports and re.search(r"egress", str(n.get("id", "")), re.IGNORECASE):
            out.append(n["id"])
    return out

def applies(karta):
    return len(_mo_egress_nodes(karta)) > 0

def evaluate(karta, root: pathlib.Path):
    api_p = root / "runtime" / "api_server.py"
    api = api_p.read_text(errors="ignore") if api_p.exists() else ""
    nodes = _mo_egress_nodes(karta)
    if not nodes or ".handle_mo(" not in api:
        return {"status": "N_A", "violations": [],
                "details": "No MO-fed egress node scheduled by the runtime — cohort boundary not composed."}
    violations = []
    store_p = root / "src" / "shared" / "cohort_store.py"
    store = store_p.read_text(errors="ignore") if store_p.exists() else ""
    if not store:
        violations.append({"file": "src/shared/cohort_store.py",
                           "fix_hint": "cohort store module missing — the MO boundary has no runtime."})
    else:
        if '("ts", "tenant_cohort_key")' not in store:
            violations.append({"file": "src/shared/cohort_store.py",
                               "fix_hint": "build_release does not exclude store metadata (ts/tenant_cohort_key)."})
        # Fas 3.18 — this used to match ONE SPELLING of the call site
        # ('"k_count": _k_count(live)'), so hoisting the computation into a
        # variable broke a gate whose property was untouched. A gate that
        # checks a spelling is brittle in the direction that matters: it goes
        # red on a refactor and stays green on a rewrite that keeps the words.
        # It now requires the property AND the floor - strictly more than
        # before, never less.
        if "def _k_count" not in store or "k_count = _k_count(live)" not in store:
            violations.append({"file": "src/shared/cohort_store.py",
                               "fix_hint": "k_count is not computed as DISTINCT pseudonymised tenants over live records."})
        if '"k_count": k_count' not in store:
            violations.append({"file": "src/shared/cohort_store.py",
                               "fix_hint": "the MO release does not carry the measured k_count."})
        if "if k_count < k_minimum" not in store:
            violations.append({"file": "src/shared/cohort_store.py",
                               "fix_hint": "build_release does not enforce the k floor ITSELF (Fas 3.18): a sub-k aggregate can be built by any caller that skips the handler's check."})
    proven = 0
    for node_id in nodes:
        hp = root / "src" / "nodes" / node_id / "handler.py"
        handler = hp.read_text(errors="ignore") if hp.exists() else ""
        cls = _pascal(node_id) + "MoSchema"
        if not handler:
            violations.append({"node": node_id, "fix_hint": "MO-fed egress handler missing."})
            continue
        ok = True
        if "build_release(contract=ac)" not in handler:
            violations.append({"node": node_id, "fix_hint": "MO release is not built contract-driven (build_release(contract=ac))."})
            ok = False
        if (cls + "(**") not in handler or "except ValidationError" not in handler or "release_error" not in handler:
            violations.append({"node": node_id, "fix_hint": "MO release is not validated fail-closed against its own generated model (%s)." % cls})
            ok = False
        if "release = None" not in handler or 'if stat["released"]:' not in handler:
            violations.append({"node": node_id, "fix_hint": "MO handler lacks the under-k hold (release = None until released)."})
            ok = False
        if ok:
            proven += 1
    tp = root / "tests" / "integration_tests" / "test_cohort_store.py"
    t = tp.read_text(errors="ignore") if tp.exists() else ""
    if "def test_mo_release_is_contract_shaped_and_validated" not in t or "def test_k_counts_distinct_tenants_not_events" not in t:
        violations.append({"file": "tests/integration_tests/test_cohort_store.py",
                           "fix_hint": "runtime proofs for the MO boundary (release shape + distinct-tenant k) are not emitted."})
    # Fas 2.10c (L8) — INAKTIVA MO-portar (icke-egress) måste vara ärliga:
    # relä-format i schemat (aldrig emissionskraven) + AC-golvet kvar.
    emission_fields = ("event_type", "vertical", "aggregate_payload", "k_count")
    inactive_honest = 0
    for n in karta.get("topology", {}).get("nodes", []):
        ports = [str(p).upper() for p in (n.get("ports") or [])]
        node_id = str(n.get("id", ""))
        if "MO" not in ports or re.search(r"egress", node_id, re.IGNORECASE):
            continue
        cp = root / "contracts" / node_id / "mo.schema.json"
        if not cp.exists():
            continue
        try:
            import json as _json
            doc = _json.loads(cp.read_text(errors="ignore"))
        except ValueError:
            continue
        schema = doc.get("schema") or doc
        required = [str(r) for r in (schema.get("required") or [])]
        if any(f in required for f in emission_fields):
            violations.append({"node": node_id, "file": "contracts/%s/mo.schema.json" % node_id,
                               "fix_hint": "inactive MO port requires the emission shape its relay ack can never satisfy (contract-vs-handler truth, L8)."})
            continue
        ac = doc.get("anonymization_contract") or (doc.get("schema") or {}).get("anonymization_contract") or {}
        if not isinstance(ac.get("k_minimum"), (int, float)):
            violations.append({"node": node_id, "file": "contracts/%s/mo.schema.json" % node_id,
                               "fix_hint": "inactive MO port lost its anonymization_contract — the k-floor applies to EVERY MO port."})
            continue
        inactive_honest += 1
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": ("MO cohort-boundary contract proven end-to-end on %d MO-fed egress node(s) "
                        "(contract-driven release, fail-closed model validation, under-k hold, "
                        "metadata containment, distinct-tenant k, emitted runtime proofs); "
                        "%d inactive MO port(s) verified honest (relay-shaped contract + retained "
                        "k-floor AC) (L7/L8).") % (proven, inactive_honest)}
