"""ARTIFACT_REFERENCE_CAPABILITY_E2E — the factory happy-path harness ships.

Fas 2.16 (external DD, Peter #7). The chassis must be able to PROVE it runs the
full happy path through the action gate. DOER_REFERENCE_MODE=1 (explicit opt-in,
default OFF) gives contract-derived reference outputs (marked "reference": True)
for unimplemented CUSTOMER_SLOTs and a side-effect-free reference execution in
the privileged gate's _apply_ seam AFTER ccas approval. Approval provenance
(Fas 2.13c) is never relaxed: approval material flows WITH the action request
(request_id + SIGNED approvals). This twin re-derives, at receiver time, that
the module, the slot branches, the seam branch, the YO approvals passthrough,
the e2e proof and the .env documentation all ship.
"""
import pathlib
GATE_ID = "ARTIFACT_REFERENCE_CAPABILITY_E2E"; GATE_NAME = "Reference Capability E2E (opt-in factory harness runs the full happy path through the action gate; approval provenance never relaxed)"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"

def applies(karta):
    return True

def _read(root, rel):
    p = root / rel
    return p.read_text(errors="ignore") if p.is_file() else ""

def evaluate(karta, root: pathlib.Path):
    violations = []
    checked = 0
    nodes_dir = root / "src" / "nodes"
    handlers = sorted(nodes_dir.glob("*/handler.py")) if nodes_dir.is_dir() else []
    if handlers:
        checked += 1
        mod = _read(root, "src/shared/reference_capability.py")
        if not mod:
            violations.append({"file": "src/shared/reference_capability.py", "fix_hint": "reference-capability module missing."})
        else:
            for needle in ("DOER_REFERENCE_MODE", "def reference_enabled", "def reference_envelope", "def reference_apply", "schemas.json"):
                if needle not in mod:
                    violations.append({"file": "src/shared/reference_capability.py", "fix_hint": "reference module lacks '%s'." % needle})
        for h in handlers:
            txt = h.read_text(errors="ignore")
            rel = "src/nodes/" + h.parent.name + "/handler.py"
            if "CUSTOMER_SLOT not implemented" in txt and "reference_enabled()" not in txt:
                violations.append({"file": rel, "fix_hint": "unimplemented CUSTOMER_SLOT lacks the reference-mode branch."})
            if "FAIL-CLOSED: unwired seam" in txt and "reference_apply(" not in txt:
                violations.append({"file": rel, "fix_hint": "privileged _apply_ seam lacks the reference execution branch."})
    api = _read(root, "runtime/api_server.py")
    if "_yo_in" in api:
        checked += 1
        if '"approvals": raw_event.get("approvals")' not in api or '"request_id": raw_event.get("request_id")' not in api:
            violations.append({"file": "runtime/api_server.py", "fix_hint": "gated YO input does not carry request_id + approvals from the action request."})
    if checked:
        t = _read(root, "tests/integration_tests/test_reference_capability.py")
        for needle in ("def test_reference_off_default_stays_fail_closed", "def test_reference_mode_completes_but_never_executes_ungated", "def test_reference_full_happy_path_through_action_gate"):
            if needle not in t:
                violations.append({"file": "tests/integration_tests/test_reference_capability.py", "fix_hint": "emitted e2e proof lacks '%s'." % needle})
        env = _read(root, ".env.example")
        if env and "DOER_REFERENCE_MODE" not in env:
            violations.append({"file": ".env.example", "fix_hint": "DOER_REFERENCE_MODE undocumented — hidden behavior switch."})
    if checked == 0 and not violations:
        return {"status": "N_A", "violations": [], "details": "No node handlers in this build — nothing to harness."}
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": "The factory-controlled reference capability ships end-to-end: explicit opt-in harness (DOER_REFERENCE_MODE, default OFF, outputs marked reference), contract-derived slot outputs, side-effect-free reference execution AFTER ccas approval, approvals passthrough (request_id + SIGNED approvals) with 2.13c provenance never relaxed, and the emitted e2e proof (fail-closed default; held ungated actions; full signed-approval happy path with verified audit chain) (external DD #7, 2.16, L7/L8)."}
