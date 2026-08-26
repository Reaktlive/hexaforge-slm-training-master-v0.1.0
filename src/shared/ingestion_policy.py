"""Ingestion policy — the real ingress policy of the intake OctaBox (T-04-019).

Doctrine: the intake OctaBox is the *ingress* boundary box and the single XI
entry of the agent (regelverk I-2 / H11): it is the ONE node in the primary
chain that is authoritative external input — every untrusted event from the
outside world crosses here first. A boundary that only renames fields is not a
boundary; the ingress must *decide what is allowed in*. This module is the pure,
deterministic policy *brain*; since Fas 2.11c the API door (POST /api/events
in runtime/api_server.py) ENFORCES the source allowlist (``check_source`` ->
403) and caller-set event_id dedup (``is_duplicate``/``mark_seen`` -> 409) —
the single composed entry, per the doctrine below. ``classify_event`` /
``evaluate_ingestion`` remain the seam for a customer intake handler that
wants the full verdict inline:

1. ``classify_event`` — malformed rejection. An event with no usable identity
   (not a dict / empty / no event_id AND no usable id) cannot be trusted or
   correlated downstream, so it is rejected at the door (``accepted=False``,
   ``reason="malformed"``). The handler turns this into an ``ok=False`` failure
   envelope, which ``run_pipeline`` already treats as a failed intake — NO fake
   XO is emitted for garbage input.

2. ``check_source`` — source validation against an optional allowlist
   (``INGEST_ALLOWED_SOURCES``, comma-separated). Empty/unset = allow-all (dev
   default). A resolved source that is set but NOT on a configured allowlist is
   blocked (``reason="source_not_allowed"``). This is the ingress deciding which
   upstream emitters it trusts.

3. ``is_duplicate`` / ``mark_seen`` — process-wide dedup by ``event_id``
   (DEPLOYMENT GRADE, Fas 2.11h: ``in_memory`` / ``local_single_process`` —
   resets on restart and is NOT shared across workers/replicas; a persistent
   or distributed backend is a deployment binding, declared machine-readably
   in the module constants below and harvested into module_truth.json). The
   ingress is the natural dedup point (everything enters once here). A repeat
   ``event_id`` is flagged ``duplicate=True`` so downstream can short-circuit
   re-processing. Dedup does NOT reject (the event is still well-formed) — it is
   a *flag*, kept deterministic and simple. ``reset_ingestion_state()`` is the
   test hook to clear the seen-set.

4. ``retention_hint`` / ``rate_hint`` — non-functional ingestion hints surfaced
   in result metadata. ``retention_period_days`` is sourced from the YI
   ingestion-policy payload (the intake YI schema declares it) or env
   ``INGEST_RETENTION_DAYS``, defaulting to 365. ``rate_hint`` is an advisory
   ingest-rate descriptor (documented, non-enforcing).

All logic here is pure (env + explicit args in, dict out) so it is trivially
testable and deterministic. The handler owns the AUTOGEN/contract concerns; this
module owns the *policy*.
"""
from __future__ import annotations

import os
import threading
from typing import Any, Dict, Optional, Set

# Default retention when neither the YI policy nor env supplies one. A real
# number, never None — the hint must always be answerable at the boundary.
DEFAULT_RETENTION_DAYS = 365

# Advisory default ingest-rate descriptor (non-functional hint).
DEFAULT_RATE_HINT = "unbounded_dev"


# -- Fas 2.11h: deployment-grade declaration (MACHINE-READABLE — harvested
# into module_truth.json; external review #6: the dedup guarantee must never
# read as distributed). ------------------------------------------------------
DEDUP_BACKEND = "in_memory"
DEPLOYMENT_GRADE = "local_single_process"
CUSTOMER_BINDING_REQUIRED_FOR = "multi_worker_or_distributed"


# -- process-wide dedup seen-set (the ingress is the single entry point) ------
_SEEN_LOCK = threading.Lock()
_SEEN_EVENT_IDS: Set[str] = set()


def reset_ingestion_state() -> None:
    """Test hook — clear the process-wide dedup seen-set."""
    with _SEEN_LOCK:
        _SEEN_EVENT_IDS.clear()


def _usable_id(src: Dict[str, Any]) -> str:
    """Resolve a usable identity for an inbound event, or '' if none.

    Mirrors the handler's id-carry order: an explicit string event_id wins,
    then incident_id. Numbers are coerced to str (a numeric id is still an id);
    blanks/None are not usable.
    """
    for key in ("event_id", "incident_id", "id"):
        val = src.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
        if isinstance(val, int) and not isinstance(val, bool):
            return str(val)
    return ""


def classify_event(payload: Any) -> Dict[str, Any]:
    """Malformed rejection. Returns {accepted, reason, event_id}.

    Rejected (accepted=False, reason='malformed') when the payload is not a
    non-empty dict, or carries no usable identity. Accepted events carry the
    resolved ``event_id`` for downstream dedup.
    """
    if not isinstance(payload, dict) or not payload:
        return {"accepted": False, "reason": "malformed", "event_id": ""}
    eid = _usable_id(payload)
    if not eid:
        return {"accepted": False, "reason": "malformed", "event_id": ""}
    return {"accepted": True, "reason": None, "event_id": eid}


def _allowed_sources() -> Optional[Set[str]]:
    """Parse INGEST_ALLOWED_SOURCES. None => allow-all (empty/unset, dev)."""
    raw = (os.environ.get("INGEST_ALLOWED_SOURCES", ""))
    parts = {p.strip() for p in raw.split(",") if p.strip()}
    return parts or None


def check_source(source: Any) -> Dict[str, Any]:
    """Source validation against the optional allowlist.

    Returns {allowed, reason}. Allowlist unset/empty => allow-all. A source that
    is set but not on a configured allowlist => allowed=False,
    reason='source_not_allowed'.
    """
    allow = _allowed_sources()
    if allow is None:
        return {"allowed": True, "reason": None}
    src = source if isinstance(source, str) else str(source or "")
    if src in allow:
        return {"allowed": True, "reason": None}
    return {"allowed": False, "reason": "source_not_allowed"}


def is_duplicate(event_id: str) -> bool:
    """True if this event_id has already been seen this process."""
    if not event_id:
        return False
    with _SEEN_LOCK:
        return event_id in _SEEN_EVENT_IDS


def mark_seen(event_id: str) -> None:
    """Record an event_id in the process-wide seen-set."""
    if not event_id:
        return
    with _SEEN_LOCK:
        _SEEN_EVENT_IDS.add(event_id)


def retention_hint(src: Dict[str, Any]) -> int:
    """Resolve retention_period_days from YI policy, then env, then default.

    The intake YI schema declares ``retention_period_days``; honour it when the
    inbound src carries the policy. Otherwise env ``INGEST_RETENTION_DAYS``,
    otherwise DEFAULT_RETENTION_DAYS. Always a real, positive int.
    """
    val = src.get("retention_period_days")
    if isinstance(val, int) and not isinstance(val, bool) and val > 0:
        return val
    env = (os.environ.get("INGEST_RETENTION_DAYS"))
    if env:
        try:
            n = int(env)
            if n > 0:
                return n
        except (TypeError, ValueError):
            pass
    return DEFAULT_RETENTION_DAYS


def rate_hint(src: Dict[str, Any]) -> str:
    """Advisory (non-enforcing) ingest-rate descriptor for result metadata."""
    val = src.get("rate_hint")
    if isinstance(val, str) and val.strip():
        return val.strip()
    env = (os.environ.get("INGEST_RATE_HINT"))
    if env and env.strip():
        return env.strip()
    return DEFAULT_RATE_HINT


def evaluate_ingestion(payload: Any, resolved_source: Any, src: Dict[str, Any]) -> Dict[str, Any]:
    """Run the full ingress policy and return a single verdict dict.

    Order: malformed rejection -> source validation -> dedup flag. Marks the
    event_id as seen on first acceptance so a later repeat flags duplicate.

    Returns:
      {accepted, reason, event_id, duplicate, retention_period_days, rate_hint}
    - accepted=False with reason in {'malformed','source_not_allowed'} => the
      handler emits an ok=False failure envelope (no fake XO).
    - accepted=True, duplicate=True => well-formed repeat; handler returns ok
      with a duplicate flag (downstream may short-circuit).
    """
    cls = classify_event(payload)
    if not cls["accepted"]:
        return {
            "accepted": False,
            "reason": cls["reason"],
            "event_id": cls["event_id"],
            "duplicate": False,
            "retention_period_days": retention_hint(src),
            "rate_hint": rate_hint(src),
        }

    eid = cls["event_id"]
    srcchk = check_source(resolved_source)
    if not srcchk["allowed"]:
        return {
            "accepted": False,
            "reason": srcchk["reason"],
            "event_id": eid,
            "duplicate": False,
            "retention_period_days": retention_hint(src),
            "rate_hint": rate_hint(src),
        }

    dup = is_duplicate(eid)
    if not dup:
        mark_seen(eid)

    return {
        "accepted": True,
        "reason": None,
        "event_id": eid,
        "duplicate": dup,
        "retention_period_days": retention_hint(src),
        "rate_hint": rate_hint(src),
    }
