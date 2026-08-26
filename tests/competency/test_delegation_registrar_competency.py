"""HST-216 — delegation_registrar competency logic, against the locked pass-3 §1B spec.

Representative corpus (>=8 cases incl. edge/adversarial). The rule under test is
pure (src/shared/delegation_policy), so these pin the domain behaviour without the
runtime/pydantic stack.
"""
from src.shared.delegation_policy import (
    verify_delegated_bind, required_issuance_tier, delegation_confidence,
    DELEGATED_OK, NEEDS_LIVE_SENIOR,
)

# A healthy, active, single-tenant grant for the "support-*" family in vertical "ops".
GRANT = {
    "grant_id": "g1", "authority": "a.berg", "delegate": "r.akesson",
    "authority_signed": True, "state": "active", "role": "bind_delegate",
    "scope": {"adapter_family": ["support-*", "notes-*"], "vertical": "ops",
              "cohort": "single_tenant_only", "eval_margin": 0.05},
    "validity": {"not_before": 0, "not_after": 10_000, "max_uses": 50,
                 "used_total": 12, "max_uses_per_day": 20, "used_today": 3},
}
# A clean, in-scope, comfortably-above-margin bind.
BIND = {"adapter": "support-summarizer", "vertical": "ops", "cohort": "single_tenant_only",
        "action_tier": "T3", "eval_score": 0.90, "eval_threshold": 0.80,
        "is_first_bind": False, "has_shared_lineage": False, "signer": "r.akesson"}
NOW = 100


def _d(grant=None, bind=None):
    return verify_delegated_bind(grant or GRANT, {**BIND, **(bind or {})}, NOW)


def test_clean_in_scope_bind_is_delegable_both_names_on_record():
    r = _d()
    assert r["decision"] == DELEGATED_OK
    assert r["records"] == ["r.akesson", "a.berg"]   # delegate + authority, always
    assert delegation_confidence({"grant": GRANT, "bind": BIND, "now_epoch": NOW}) == 1.0


def test_t4_action_never_delegable():
    r = _d(bind={"action_tier": "T4"})
    assert r["decision"] == NEEDS_LIVE_SENIOR and r["reason"] == "t4_action_never_delegable"


def test_first_bind_needs_live_senior():
    r = _d(bind={"is_first_bind": True})
    assert r["decision"] == NEEDS_LIVE_SENIOR and r["reason"] == "first_bind_of_new_family"


def test_shared_lineage_needs_live_senior():
    r = _d(bind={"has_shared_lineage": True})
    assert r["decision"] == NEEDS_LIVE_SENIOR and r["reason"] == "shared_or_hexaintel_lineage"


def test_under_margin_eval_needs_live_senior():
    # 0.83 clears the gate (0.80) but is within the 0.05 margin -> not delegable.
    r = _d(bind={"eval_score": 0.83, "eval_threshold": 0.80})
    assert r["decision"] == NEEDS_LIVE_SENIOR and r["reason"] == "eval_within_margin"


def test_clear_margin_eval_is_delegable():
    r = _d(bind={"eval_score": 0.90, "eval_threshold": 0.80})
    assert r["decision"] == DELEGATED_OK


def test_revoked_grant_needs_live_senior():
    r = _d(grant={**GRANT, "state": "revoked"})
    assert r["decision"] == NEEDS_LIVE_SENIOR and r["reason"] == "delegation_revoked"


def test_expired_grant_needs_live_senior():
    r = verify_delegated_bind({**GRANT, "validity": {**GRANT["validity"], "not_after": 50}}, BIND, NOW)
    assert r["decision"] == NEEDS_LIVE_SENIOR and r["reason"] == "delegation_expired"


def test_exhausted_uses_needs_live_senior():
    r = _d(grant={**GRANT, "validity": {**GRANT["validity"], "used_total": 50}})
    assert r["decision"] == NEEDS_LIVE_SENIOR and r["reason"] == "delegation_exhausted_total"


def test_daily_cap_needs_live_senior():
    r = _d(grant={**GRANT, "validity": {**GRANT["validity"], "used_today": 20}})
    assert r["decision"] == NEEDS_LIVE_SENIOR and r["reason"] == "delegation_exhausted_daily"


def test_out_of_scope_family_needs_live_senior():
    r = _d(bind={"adapter": "invoice-extractor"})
    assert r["decision"] == NEEDS_LIVE_SENIOR and r["reason"] == "out_of_scope_adapter_family"


def test_out_of_scope_shared_cohort_needs_live_senior():
    r = _d(bind={"cohort": "hexaintel_shared"})
    assert r["decision"] == NEEDS_LIVE_SENIOR and r["reason"] == "out_of_scope_shared_cohort"


def test_issuance_bare_wildcard_forces_t4():
    assert required_issuance_tier({"adapter_family": ["*"], "cohort": "single_tenant_only"})["required_tier"] == "T4"
    assert required_issuance_tier({"adapter_family": [], "cohort": "single_tenant_only"})["required_tier"] == "T4"


def test_issuance_shared_cohort_forces_t4_else_t3():
    assert required_issuance_tier({"adapter_family": ["doc-*"], "cohort": "hexaintel_shared"})["required_tier"] == "T4"
    assert required_issuance_tier({"adapter_family": ["doc-*"], "cohort": "single_tenant_only"})["required_tier"] == "T3"


def test_determinism():
    assert verify_delegated_bind(GRANT, BIND, NOW) == verify_delegated_bind(dict(GRANT), dict(BIND), NOW)
