"""Delegation policy — capability-based signing authority for delegation_registrar (HST-216).

CUSTOMER competency logic (pass-3 addendum §1B), re-generation-safe: lives in
src/shared/ (a declared customer extension point), imported by the node's
CUSTOMER_SLOT seam. PURE — no I/O, no heavy deps, deterministic for a given
(grant, bind, now).

A delegation grant is a CAPABILITY, never a role flag: signed, scope-bounded,
time-bounded, revocable. It lets a delegate sign *individual* binds that fall
strictly inside its scope; it NEVER makes the gate cheaper. Every hard exclusion
routes back to a live senior signature (T3), and no grant can ever pre-satisfy a
T4 (dual-approval) action.

Grant scope is a CONJUNCTION (AND) of typed constraints — a bare `*` adapter
family or a shared/HexaIntel cohort is not delegable and forces the GRANT ITSELF
to be issued at T4.

    scope = {adapter_family: [globs], vertical, cohort: "single_tenant_only",
             eval_margin: 0.05}
    validity = {not_before, not_after, max_uses, max_uses_per_day, used_total, used_today}
"""
from __future__ import annotations

from typing import Any, Optional

DEFAULT_EVAL_MARGIN = 0.05

DELEGATED_OK = "delegated_ok"
NEEDS_LIVE_SENIOR = "needs_live_senior"

# Reasons that ALWAYS route to a live senior, regardless of the grant.
HARD_T4 = "t4_action_never_delegable"
HARD_FIRST_BIND = "first_bind_of_new_family"
HARD_SHARED_LINEAGE = "shared_or_hexaintel_lineage"
HARD_UNDER_MARGIN = "eval_within_margin"


def _is_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x == x


def _is_bare_wildcard(patterns: Any) -> bool:
    """A family list is a bare wildcard iff it is empty, missing, or contains a
    literal '*' (matches everything). Prefix globs like 'doc-*' are fine."""
    if not patterns:
        return True
    if isinstance(patterns, str):
        patterns = [patterns]
    return any(str(p).strip() == "*" for p in patterns)


def _family_matches(patterns: Any, adapter: Any) -> bool:
    if adapter is None:
        return False
    if isinstance(patterns, str):
        patterns = [patterns]
    name = str(adapter)
    for p in patterns or []:
        p = str(p)
        if p == "*":
            return True
        if p.endswith("*"):
            if name.startswith(p[:-1]):
                return True
        elif name == p:
            return True
    return False


def required_issuance_tier(scope: dict) -> dict:
    """The tier a delegation GRANT must be issued at. Broad scope escalates to
    T4 (dual): a bare-wildcard adapter family, or any cohort that is not
    single_tenant_only. Otherwise T3."""
    scope = scope or {}
    bare = _is_bare_wildcard(scope.get("adapter_family"))
    shared = str(scope.get("cohort", "")) != "single_tenant_only"
    tier = "T4" if (bare or shared) else "T3"
    return {"required_tier": tier, "bare_wildcard": bare, "shared_cohort": shared}


def _grant_state(grant: dict, now_epoch: Optional[float]) -> Optional[str]:
    """Return a reason string if the grant is not currently usable, else None."""
    if not grant.get("authority_signed"):
        return "grant_not_authority_signed"
    if str(grant.get("state", "active")) == "revoked":
        return "delegation_revoked"
    val = grant.get("validity", {}) or {}
    if _is_number(now_epoch):
        nb, na = val.get("not_before"), val.get("not_after")
        if _is_number(nb) and now_epoch < nb:
            return "delegation_not_yet_valid"
        if _is_number(na) and now_epoch > na:
            return "delegation_expired"
    used_total, max_uses = val.get("used_total", 0), val.get("max_uses")
    if _is_number(max_uses) and _is_number(used_total) and used_total >= max_uses:
        return "delegation_exhausted_total"
    used_today, max_day = val.get("used_today", 0), val.get("max_uses_per_day")
    if _is_number(max_day) and _is_number(used_today) and used_today >= max_day:
        return "delegation_exhausted_daily"
    return None


def _hard_exclusion(bind: dict, eval_margin: float) -> Optional[str]:
    """A bind that ALWAYS needs a live senior, regardless of any grant."""
    if str(bind.get("action_tier", "")).upper() in ("T4", "DUAL", "DUAL_APPROVAL"):
        return HARD_T4
    if bind.get("is_first_bind"):
        return HARD_FIRST_BIND
    if bind.get("has_shared_lineage"):
        return HARD_SHARED_LINEAGE
    score, thr = bind.get("eval_score"), bind.get("eval_threshold")
    # Delegate may sign only binds that clear the threshold BY the margin.
    if _is_number(score) and _is_number(thr) and score < thr + eval_margin:
        return HARD_UNDER_MARGIN
    return None


def verify_delegated_bind(grant: dict, bind: dict, now_epoch: Optional[float] = None) -> dict:
    """Decide whether a delegate's single signature may release this bind.

    Returns:
        {
          "decision": "delegated_ok" | "needs_live_senior",
          "reason": "<machine reason>",
          "detail": "<human sentence>",
          "records": [delegate, authority],   # BOTH names, always, for the chain
        }

    `delegated_ok` means the delegate signs individually AND the audit chain
    records both the delegate and the authority who granted the capability.
    Every other path needs a live senior (T3) — the gate never gets cheaper.
    """
    grant = grant or {}
    bind = bind or {}
    scope = grant.get("scope", {}) or {}
    eval_margin = scope.get("eval_margin", DEFAULT_EVAL_MARGIN)
    if not _is_number(eval_margin):
        eval_margin = DEFAULT_EVAL_MARGIN
    delegate = grant.get("delegate")
    authority = grant.get("authority")

    def out(reason: str, detail: str) -> dict:
        return {"decision": NEEDS_LIVE_SENIOR, "reason": reason, "detail": detail,
                "records": [delegate, authority]}

    # 1. Hard exclusions — always a live senior, regardless of the grant.
    hard = _hard_exclusion(bind, eval_margin)
    if hard == HARD_T4:
        return out(hard, "T4 (dual-approval) action — no grant can pre-satisfy it")
    if hard == HARD_FIRST_BIND:
        return out(hard, "first bind of a new adapter family — needs a live senior signature")
    if hard == HARD_SHARED_LINEAGE:
        return out(hard, "shared / HexaIntel lineage — needs a live senior signature")
    if hard == HARD_UNDER_MARGIN:
        return out(hard, "eval within the delegation's margin (thin) — needs a live senior signature")

    # 2. Grant must be usable.
    bad = _grant_state(grant, now_epoch)
    if bad:
        return out(bad, "delegation not usable (%s) — needs a live senior signature" % bad)

    # 3. Scope predicate (conjunction).
    if not _family_matches(scope.get("adapter_family"), bind.get("adapter")):
        return out("out_of_scope_adapter_family", "bind outside the grant's adapter family")
    if scope.get("vertical") is not None and str(scope.get("vertical")) != str(bind.get("vertical")):
        return out("out_of_scope_vertical", "bind outside the grant's vertical")
    if str(scope.get("cohort", "single_tenant_only")) == "single_tenant_only" \
            and str(bind.get("cohort", "single_tenant_only")) != "single_tenant_only":
        return out("out_of_scope_shared_cohort", "bind touches a shared cohort — outside a single-tenant grant")

    # 4. All constraints satisfied — the delegate signs, both names on the record.
    return {
        "decision": DELEGATED_OK,
        "reason": "within_delegation_scope",
        "detail": "within delegation scope; delegate signs, both delegate and authority on the record",
        "records": [delegate, authority],
    }


def delegation_confidence(inputs: dict) -> float:
    """Scalar seam value in [0,1]: 1.0 when a bind is cleanly delegable, 0.0 when
    it needs a live senior. Deterministic. (The node's classify envelope carries
    this scalar; the full decision is verify_delegated_bind.)"""
    if not isinstance(inputs, dict):
        return 0.0
    grant = inputs.get("grant", {})
    bind = inputs.get("bind", inputs)
    now = inputs.get("now_epoch")
    return 1.0 if verify_delegated_bind(grant, bind, now)["decision"] == DELEGATED_OK else 0.0
