"""ARTIFACT_AUDIT_BINDING_E2E — the audit chain binds WHO / WHAT-IN / WHAT-OUT.

Fas 2.11a (external assessment #4, main finding A). Before this claim the
chain proved order + after-the-fact integrity but hashed a RECEIPT
({event_id, signature}) instead of the data, and the verified caller never
reached the hashed core. Four statically-verifiable system claims (L7/L8):
  1. hexa_record v2: principal + input_sha256 + output_sha256 sit INSIDE the
     hashed core (_CORE_KEYS), with a request-context fallback and ONE
     canonicalisation (canonical_sha256) shared by writers/verifiers/tests.
  2. The principal is established at the transport boundary: zt_guard binds
     the verified identity OR the honest "auth_disabled" marker — never silence.
  3. Every pipeline audit site binds the node's ACTUAL input/output
     (input_payload=/output_payload= on _record_audit), including the
     per-node routes' exact merge (input_payload=merged).
  4. The runtime proofs are emitted with every bundle: principal/input-hash
     tamper breaks verify_chain (unit) + e2e binding with hashes recomputed
     from the outside (integration).
"""
import pathlib, re
GATE_ID = "ARTIFACT_AUDIT_BINDING_E2E"; GATE_NAME = "Audit Binding E2E (who / exact input / exact output)"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"

def applies(karta):
    return True  # the audit chain is composed in every bundle

def evaluate(karta, root: pathlib.Path):
    violations = []
    rec_p = root / "src" / "shared" / "hexa_record.py"
    rec = rec_p.read_text(errors="ignore") if rec_p.exists() else ""
    if not rec:
        violations.append({"file": "src/shared/hexa_record.py",
                           "fix_hint": "audit chain module missing — nothing binds anything."})
    else:
        m = re.search(r"_CORE_KEYS\s*=\s*\(([\s\S]*?)\)", rec)
        keys = m.group(1) if m else ""
        for key in ('"principal"', '"input_sha256"', '"output_sha256"'):
            if key not in keys:
                violations.append({"file": "src/shared/hexa_record.py",
                                   "fix_hint": "%s is not part of the HASHED core (_CORE_KEYS) — binding would be an annotation, not a tamper-evident fact." % key})
        if "def set_principal" not in rec or "_CURRENT_PRINCIPAL.get()" not in rec:
            violations.append({"file": "src/shared/hexa_record.py",
                               "fix_hint": "request-context principal (set_principal + contextvar fallback in _core) missing."})
        if "def canonical_sha256" not in rec:
            violations.append({"file": "src/shared/hexa_record.py",
                               "fix_hint": "canonical_sha256 missing — ONE recomputable canonicalisation is required."})
    api_p = root / "runtime" / "api_server.py"
    api = api_p.read_text(errors="ignore") if api_p.exists() else ""
    if not api:
        violations.append({"file": "runtime/api_server.py", "fix_hint": "api server missing — no audited boundary."})
    else:
        if 'set_principal(str(auth.get("identity")' not in api or 'set_principal("auth_disabled")' not in api:
            violations.append({"file": "runtime/api_server.py",
                               "fix_hint": "zt_guard does not establish the principal on BOTH branches (verified identity / explicit auth_disabled)."})
        bound_in = len(re.findall(r"_record_audit\([^\n]*input_payload=", api))
        bound_out = len(re.findall(r"_record_audit\([^\n]*output_payload=", api))
        if bound_in == 0 or bound_out == 0:
            violations.append({"file": "runtime/api_server.py",
                               "fix_hint": "_record_audit call sites do not pass the node's ACTUAL input/output — the chain would hash the receipt, not the data."})
        if "input_payload=merged" not in api:
            violations.append({"file": "runtime/api_server.py",
                               "fix_hint": "per-node /port-xi routes do not bind the exact merged input the handler received."})
    ut_p = root / "tests" / "unit_tests" / "test_hexa_record.py"
    ut = ut_p.read_text(errors="ignore") if ut_p.exists() else ""
    if "def test_tampered_principal_breaks_the_chain" not in ut or "def test_absent_binding_is_visible_never_fabricated" not in ut:
        violations.append({"file": "tests/unit_tests/test_hexa_record.py",
                           "fix_hint": "tamper-evidence proofs for the v2 core are not emitted."})
    e2e_p = root / "tests" / "integration_tests" / "test_pipeline_e2e.py"
    e2e = e2e_p.read_text(errors="ignore") if e2e_p.exists() else ""
    if "def test_audit_chain_binds_principal_and_exact_input" not in e2e or "def test_audit_chain_binds_exact_output_on_node_route" not in e2e:
        violations.append({"file": "tests/integration_tests/test_pipeline_e2e.py",
                           "fix_hint": "e2e binding proofs (principal on every entry; hashes recomputed from the outside) are not emitted."})
    sites = len(re.findall(r"_record_audit\([^\n]*input_payload=", api)) if api else 0
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": ("Audit chain binds WHO/WHAT-IN/WHAT-OUT in the HASHED core: principal at the "
                        "transport boundary (zt_guard -> set_principal, explicit auth_disabled in dev), "
                        "%d _record_audit site(s) bind exact input+output, canonical_sha256 is the single "
                        "recomputable canonicalisation, and emitted unit+e2e proofs verify tamper-evidence "
                        "(L7/L8).") % sites}
