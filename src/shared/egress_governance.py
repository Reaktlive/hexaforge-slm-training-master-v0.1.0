"""Egress governance — real governance_metadata + egress-policy enforcement (T-04-018).

This is the GOVERNANCE + AUDIT brain of the egress OctaBox. Per the
HexaBox/regelverk doctrine the egress node is the *boundary* OctaBox: nothing
leaves the system without (a) being bound to the tamper-evident HexaRecord audit
chain and (b) clearing the egress policy. Two cooperating concerns live here:

1. ``build_governance_metadata`` — emits a REAL governance_metadata object,
   replacing the carry-over placeholder ``{}``:
     * ``audit_chain_hash`` — the latest HexaRecord ``entry_hash`` bound to this
       event. We read the tamper-evident chain (``read_chain``) filtered to the
       egress node's audit entries and, when the event payload is known, to the
       entry whose ``payload_sha256`` matches it; the last matching entry's
       ``entry_hash`` is the binding. Falls back to the chain head for the node,
       then to GENESIS when the chain is empty. This is the HexaRecord
       doctrine: the egress is welded to the tamper-evident chain.
     * ``doctrine_score`` — a REAL number (never a literal), sourced in order:
       the inbound pipeline verdict if present (PASS->100, FAIL/blocked->0),
       else the committed CEVE validator score (reports/ceve_validation.json),
       else a conservative default. ``doctrine_score_source`` records which.
     * ``chain_verified`` — ``verify_chain()`` over the event's chain (a live
       tamper check at egress time).
   The object is run through the universal PII doctrine floor so the governance
   metadata can NEVER carry a FORBIDDEN_PII_KEY.

2. ``evaluate_egress_policy`` — config-driven egress enforcement (env):
     * ``EGRESS_ALLOWED_RECIPIENTS`` (comma-separated allowlist; empty/unset =
       allow-all, dev default).
     * ``EGRESS_REQUIRE_ENCRYPTION`` (truthy => encryption_required flag).
     * ``data_classification`` passthrough from the inbound payload.
   A recipient that is set but NOT on a configured allowlist is BLOCKED: the
   caller marks ``report_status="blocked_by_policy"`` and withholds the report
   body. Governance metadata is still emitted (audit must record the block).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from src.shared.anonymization import FORBIDDEN_PII_KEYS
from src.shared.hexa_record import GENESIS, read_chain, verify_chain

NODE_ID = os.environ.get("EGRESS_NODE_ID", "egress")  # generalised for the core shelf (was SOC-hardcoded)


class SovereigntyViolationError(RuntimeError):
    """Raised when incident/cohort data is about to egress to a HexaBox/Studio-owned
    endpoint (FIX-03 — sovereignty by construction: HexaBox is the licensor, not a
    data processor)."""


# Built-in markers that classify a recipient as HexaBox/Studio-owned (FIX-03).
# Operational incident/cohort data must NEVER egress to these endpoints —
# HexaBox is the licensor, not a data processor. Only build/validation telemetry
# may reach Studio, and only from CI.
_HEXABOX_OWNED_HOST_MARKERS = (
    "zlznmlcrolxppxwckfao.supabase.co",  # Studio DevTracker project
    "hexabox.one",
    "doable.app",
)


def _hexabox_owned_hosts() -> tuple:
    """Built-in markers + env-extendable denylist (HEXABOX_OWNED_HOSTS)."""
    extra = tuple(
        h.strip().lower()
        for h in os.environ.get("HEXABOX_OWNED_HOSTS", "").split(",")
        if h.strip()
    )
    return _HEXABOX_OWNED_HOST_MARKERS + extra


def _is_hexabox_owned(target: Any) -> bool:
    t = str(target or "").lower()
    return any(marker in t for marker in _hexabox_owned_hosts())


def assert_tenant_owned(target: Any, payload_kind: str = "cohort") -> None:
    """Hard guard: raise when an incident/cohort destination is HexaBox-owned."""
    if _is_hexabox_owned(target):
        raise SovereigntyViolationError(
            f"{payload_kind} data may not egress to a HexaBox-owned endpoint: {target!r} "
            "(FIX-03: HexaBox is the licensor, not a data processor — only "
            "build/validation telemetry may reach Studio, and only from CI)"
        )


# The MO cohort's durable destination — the deployment tenant's own store.
def resolve_cohort_egress_target() -> str:
    target = os.environ.get("COHORT_EGRESS_TARGET", "").strip()
    if target:
        assert_tenant_owned(target, payload_kind="cohort")
    return target

# Conservative default when no verdict and no committed validator score exist.
# Not a "pass" — a neutral floor that signals "unscored" without faking 100.
DEFAULT_DOCTRINE_SCORE = 50.0

# Where the CEVE validator commits its score (repo-root relative).
_CEVE_REPORT = Path(__file__).resolve().parents[2] / "reports" / "ceve_validation.json"


# ── audit-chain binding (HexaRecord doctrine) ───────────────────────────────

def _sha256_payload(payload: Any) -> str:
    """Recompute the HexaRecord payload hash for a candidate event payload.

    Mirrors hexa_record._sha256 so we can match a chain entry's payload_sha256
    to the event being egressed (per-event binding when the payload is known).
    """
    import hashlib

    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, default=str).encode()
    ).hexdigest()


def latest_audit_chain_hash(
    event_payload: Optional[Any] = None,
    *,
    node_id: str = NODE_ID,
    path: Optional[str] = None,
) -> str:
    """Latest HexaRecord entry_hash bound to this egress event.

    Filter the tamper-evident chain to this node's audit entries. If ``event_payload``
    is supplied and an entry's ``payload_sha256`` matches it, prefer the LAST
    such matching entry (genuine per-event binding). Otherwise fall back to the
    LAST entry for the node (the node's current chain head). If the chain holds
    no entry for the node, fall back to GENESIS (empty/uninitialised chain).
    """
    chain = read_chain(path)
    node_entries = [e for e in chain if e.get("node_id") == node_id]
    if event_payload is not None:
        target = _sha256_payload(event_payload)
        matched = [e for e in node_entries if e.get("payload_sha256") == target]
        if matched:
            return str(matched[-1].get("entry_hash") or GENESIS)
    if node_entries:
        return str(node_entries[-1].get("entry_hash") or GENESIS)
    return GENESIS


# ── doctrine score (real number, documented source) ─────────────────────────

def _verdict_to_score(verdict: Any) -> Optional[float]:
    """Map a pipeline verdict to a doctrine score, or None if not a verdict."""
    if verdict is None:
        return None
    if isinstance(verdict, bool):
        return 100.0 if verdict else 0.0
    v = str(verdict).strip().lower()
    if v in ("pass", "passed", "ok", "approved", "allow", "allowed", "clean"):
        return 100.0
    if v in ("fail", "failed", "blocked", "deny", "denied", "reject", "rejected"):
        return 0.0
    return None


def _ceve_score() -> Optional[float]:
    """The committed CEVE validator score, if the report is present + numeric."""
    try:
        data = json.loads(_CEVE_REPORT.read_text())
    except (OSError, ValueError):
        return None
    score = data.get("score")
    return float(score) if isinstance(score, (int, float)) else None


def resolve_doctrine_score(src: Dict[str, Any]) -> tuple[float, str]:
    """Resolve the event's doctrine score and the source it came from.

    Order: inbound pipeline verdict -> committed CEVE validator score ->
    conservative default. Always returns a real float plus a source label.
    """
    for key in ("doctrine_verdict", "pipeline_verdict", "verdict", "validation_verdict"):
        score = _verdict_to_score(src.get(key))
        if score is not None:
            return score, f"pipeline_verdict:{key}"
    # An explicit numeric doctrine_score on the inbound payload wins next.
    explicit = src.get("doctrine_score")
    if isinstance(explicit, (int, float)) and not isinstance(explicit, bool):
        return float(explicit), "inbound_doctrine_score"
    ceve = _ceve_score()
    if ceve is not None:
        return ceve, "ceve_validation_report"
    return DEFAULT_DOCTRINE_SCORE, "default"


# ── governance_metadata builder ─────────────────────────────────────────────

def _strip_pii(obj: Dict[str, Any]) -> Dict[str, Any]:
    """Universal PII floor: drop any FORBIDDEN_PII_KEY from the governance object."""
    return {k: v for k, v in obj.items() if k not in FORBIDDEN_PII_KEYS}


def build_governance_metadata(
    src: Dict[str, Any],
    *,
    event_payload: Optional[Any] = None,
    path: Optional[str] = None,
) -> Dict[str, Any]:
    """Build the REAL governance_metadata for an egress event.

    Binds to the HexaRecord chain (audit_chain_hash + chain_verified) and
    carries the real doctrine_score (+ its source). PII-floored.
    """
    payload_for_binding = event_payload if event_payload is not None else src
    audit_chain_hash = latest_audit_chain_hash(payload_for_binding, path=path)
    doctrine_score, source = resolve_doctrine_score(src)
    gov = {
        "doctrine_score": doctrine_score,
        "doctrine_score_source": source,
        "audit_chain_hash": audit_chain_hash,
        "chain_verified": verify_chain(path),
        "policy_version": "T-04-018",
    }
    return _strip_pii(gov)


# ── egress policy enforcement ───────────────────────────────────────────────

def _env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def _allowlist() -> list[str]:
    raw = os.environ.get("EGRESS_ALLOWED_RECIPIENTS", "")
    return [r.strip() for r in raw.split(",") if r.strip()]


def _channel_encrypted(src: Dict[str, Any]) -> bool:
    """Resolve whether the egress channel is encrypted.

    Doctrine: encryption is a transport property of the channel/recipient, so it
    is read from the egress input (default **False** when absent — fail-closed,
    so an unsignalled channel is treated as unencrypted). Either a boolean on the
    recipient descriptor / src (``transport_encrypted`` or ``channel_encrypted``)
    or an explicit env override ``EGRESS_CHANNEL_ENCRYPTED`` (for deployments
    where TLS is terminated at a trusted proxy and the app cannot observe the
    transport — see docs/deployment.md) marks the channel encrypted.
    """
    for key in ("transport_encrypted", "channel_encrypted"):
        val = src.get(key)
        if isinstance(val, bool):
            return val
        if isinstance(val, str) and val.strip().lower() in ("1", "true", "yes", "on"):
            return True
    recipient = src.get("recipient_descriptor")
    if isinstance(recipient, dict):
        for key in ("transport_encrypted", "channel_encrypted"):
            val = recipient.get(key)
            if isinstance(val, bool):
                return val
    if _env_truthy("EGRESS_CHANNEL_ENCRYPTED"):
        return True
    return False


def evaluate_egress_policy(src: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the egress policy for an outbound event.

    Returns a decision dict::

        {
          "allowed": bool,                # False => blocked_by_policy
          "reason": str,                  # human-readable
          "recipient": Optional[str],
          "data_classification": Optional[str],
          "encryption_required": bool,
        }

    Allowlist semantics: an empty/unset ``EGRESS_ALLOWED_RECIPIENTS`` is
    allow-all (dev). If the allowlist IS configured and a recipient is set but
    not on it, the egress is blocked (``blocked_by_policy``).

    Encryption semantics (T-04-025): when ``EGRESS_REQUIRE_ENCRYPTION`` is truthy
    AND the channel is not encrypted, the egress is blocked
    (``blocked_unencrypted``) — distinguishable from a recipient block. When
    encryption is not required, behavior is unchanged (flag surfaced, allowed).
    The recipient-allowlist block takes precedence in the ``status`` field; the
    ``encryption`` sub-dict always records the independent encryption verdict.

    Decision dict additionally carries ``status`` ("allowed" |
    "blocked_by_policy" | "blocked_unencrypted") and an ``encryption`` sub-dict
    ``{"required", "channel_encrypted", "enforced", "allowed"}``.
    """
    recipient = src.get("recipient_system") or src.get("recipient")
    recipient = str(recipient) if recipient not in (None, "") else None

    # FIX-03 sovereignty gate (highest precedence): incident/cohort data may
    # never leave for a HexaBox/Studio-owned endpoint — regardless of
    # allowlist configuration (an allow-all dev config cannot waive this).
    data_classification = (
        src.get("data_classification") or src.get("data_classification_level")
    )
    encryption_required = _env_truthy("EGRESS_REQUIRE_ENCRYPTION")
    channel_encrypted = _channel_encrypted(src)
    if recipient is not None and _is_hexabox_owned(recipient):
        return {
            "allowed": False,
            "reason": (
                f"recipient {recipient!r} is a HexaBox-owned endpoint — "
                "operational data never leaves the deployment tenant (FIX-03)"
            ),
            "status": "blocked_sovereignty",
            "recipient": recipient,
            "data_classification": data_classification,
            "encryption_required": encryption_required,
            "encryption": {
                "required": encryption_required,
                "channel_encrypted": channel_encrypted,
                "enforced": False,
                "allowed": True,
            },
        }
    allowlist = _allowlist()

    # Recipient-allowlist gate (existing behavior).
    recipient_allowed = True
    reason = "no policy restriction"
    if allowlist and recipient is not None and recipient not in allowlist:
        recipient_allowed = False
        reason = f"recipient '{recipient}' not in EGRESS_ALLOWED_RECIPIENTS"
    elif allowlist and recipient is not None:
        reason = f"recipient '{recipient}' on allowlist"
    elif not allowlist:
        reason = "allow-all (no allowlist configured)"

    # Encryption gate (T-04-025): enforced only when required.
    encryption_enforced = bool(encryption_required and not channel_encrypted)
    encryption_allowed = not encryption_enforced
    encryption = {
        "required": encryption_required,
        "channel_encrypted": channel_encrypted,
        "enforced": encryption_enforced,
        "allowed": encryption_allowed,
    }

    # Combine both gates. Recipient block takes precedence in the status label
    # (back-compat with existing blocked_by_policy callers); either gate failing
    # withholds the body.
    allowed = recipient_allowed and encryption_allowed
    if not recipient_allowed:
        status = "blocked_by_policy"
    elif not encryption_allowed:
        status = "blocked_unencrypted"
        reason = (
            "EGRESS_REQUIRE_ENCRYPTION is set but the egress channel is not "
            "encrypted (transport_encrypted/channel_encrypted false and "
            "EGRESS_CHANNEL_ENCRYPTED unset)"
        )
    else:
        status = "allowed"

    return {
        "allowed": allowed,
        "reason": reason,
        "status": status,
        "recipient": recipient,
        "data_classification": data_classification,
        "encryption_required": encryption_required,
        "encryption": encryption,
    }
