"""ARTIFACT_STRICT_CONTRACT_E2E — strict mode enforces BOTH payload and envelope.

blocker2: under DOER_STRICT_CONTRACTS every XO-emitting node step must (1) build
its canonical envelope, (2) enforce_payload the inner payload against the per-node
{Node}Xo sub-schema, (3) enforce_envelope the WHOLE envelope against the shared
CanonicalEnvelope, and (4) forward that EXACT validated envelope. This gate proves
the EMITTED runtime does all four statically: a node that only checks the payload
(the pre-split bug that validated the payload against an envelope schema), or that
validates one object and forwards another, FAILS.
"""
import re, pathlib
GATE_ID = "ARTIFACT_STRICT_CONTRACT_E2E"; GATE_NAME = "Strict Contract E2E"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"

def _py_alias(node_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "_", node_id)

def _xo_nodes(karta):
    out = []
    for n in karta.get("topology", {}).get("nodes", []):
        if "XO" in [str(p).upper() for p in (n.get("ports") or [])]:
            out.append(n["id"])
    return out

def applies(karta):
    return len(_xo_nodes(karta)) > 0

def evaluate(karta, root: pathlib.Path):
    api = root / "runtime" / "api_server.py"
    if not api.exists():
        return {"status": "FAIL",
                "violations": [{"file": "runtime/api_server.py",
                                "fix_hint": "runtime/api_server.py missing — cannot prove strict-contract enforcement."}],
                "details": "No runtime to inspect."}
    text = api.read_text(errors="ignore")
    violations = []
    # The split machinery itself must be wired into the runtime.
    if "enforce_payload(" not in text:
        violations.append({"file": "runtime/api_server.py",
                           "fix_hint": "runtime never calls enforce_payload() — strict payload validation is absent."})
    if "enforce_envelope(" not in text:
        violations.append({"file": "runtime/api_server.py",
                           "fix_hint": "runtime never calls enforce_envelope() — strict envelope validation is absent."})
    # The pre-split single check (enforce_output) was the bug site — it must be gone.
    if re.search(r"\benforce_output\s*\(", text):
        violations.append({"file": "runtime/api_server.py",
                           "fix_hint": "legacy enforce_output( call still present — migrate to enforce_payload + enforce_envelope."})
    # Every SCHEDULED XO node step must enforce BOTH, and hand the validated
    # envelope (env_<alias>) onward — never validate one object and emit another.
    xo = _xo_nodes(karta)
    for node_id in xo:
        alias = _py_alias(node_id)
        if ('env_%s = {"event_id"' % alias) not in text:
            continue  # not scheduled as an XO step in this linearisation — nothing to prove
        if ('enforce_payload("%s", "xo"' % node_id) not in text:
            violations.append({"node": node_id,
                               "fix_hint": "XO node step does not enforce_payload its emitted payload under strict mode."})
        if ('enforce_envelope("%s", "xo", env_%s' % (node_id, alias)) not in text:
            violations.append({"node": node_id,
                               "fix_hint": "XO node step does not enforce_envelope the EXACT env_%s it forwards (validate-one-emit-another)." % alias})
    # Fas 2.24d — the static wiring above proves the calls are WRITTEN; it cannot
    # tell a call that rejects bad data from one that does nothing. So the gate
    # now ALSO requires an emitted RUNTIME proof with teeth: a test that runs
    # under the suite (and CI, where DOER_STRICT_CONTRACTS is pinned) and asserts
    # a contract violation actually RAISES. Presence is not enough — a proof that
    # never expects a rejection would pass a static check while proving nothing.
    proof_rel = "tests/unit_tests/test_ceve_runtime.py"
    proof = root / "tests" / "unit_tests" / "test_ceve_runtime.py"
    ptext = proof.read_text(errors="ignore") if proof.exists() else ""
    if not ptext:
        violations.append({"file": proof_rel,
                           "fix_hint": "no emitted runtime proof for strict enforcement — the gate would be a static text check only."})
    else:
        if "pytest.raises(ContractViolation)" not in ptext:
            violations.append({"file": proof_rel,
                               "fix_hint": "the strict-enforcement proof never asserts that a violation RAISES — it proves wiring, not enforcement."})
        if "enforce_payload(" not in ptext or "enforce_envelope(" not in ptext:
            violations.append({"file": proof_rel,
                               "fix_hint": "the runtime proof must exercise BOTH enforce_payload and enforce_envelope (the split is the point)."})
        if "schemas.json" not in ptext:
            violations.append({"file": proof_rel,
                               "fix_hint": "the runtime proof must derive its subject from the bundle's OWN contracts (agent-agnostic), not a hardcoded node."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": ("Strict payload+envelope enforcement verified across %d XO-emitting node(s): "
                        "static wiring in the emitted runtime PLUS an emitted runtime proof that a "
                        "contract violation actually RAISES (self-derived subject, runs in the suite "
                        "and in CI where the flag is pinned). Proves ENFORCEMENT COMPLETENESS "
                        "(declared contracts are enforced end-to-end at runtime) — "
                        "not semantic maturity of the contract contents; "
                        "see ARTIFACT_CONTRACT_COMPLETENESS for the declared-form measurement.") % len(xo)}
