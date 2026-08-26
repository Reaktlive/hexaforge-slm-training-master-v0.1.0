"""Reporting profiles — framework-agnostic regulatory incident-reporting clock.

Harvest generalization of the NIS2 Art 23 clock into a reusable core-shelf
module. A *profile* declares the ordered filing stages and, per stage, a
deadline rule: an offset and an ANCHOR. Two anchor kinds cover the real
regimes:

  * ``detection``        — offset measured from when the entity became aware
                           (NIS2 anchors every stage here).
  * ``after:<stage>``    — offset measured from when an earlier stage was
                           actually FILED (DORA anchors its later stages to
                           the previous submission, not to detection).

The module is PURE — no clock reads, no network, no state — so a profile's
deadlines and stage machine are fully unit-testable with fixed timestamps.

Shipped profiles:
  * NIS2  (Dir. (EU) 2022/2555 Art 23): early_warning +24h, notification
    +72h, final_report +30d — all from detection.
  * DORA  (Reg. (EU) 2022/2554; Commission Delegated Reg. (EU) 2025/301):
    initial_notification ≤24h from awareness; intermediate_report ≤72h after
    the initial notification was filed; final_report ≤1 month after the
    (latest) intermediate report was filed.

Selection: ``active_profile()`` reads env ``REPORTING_PROFILE`` (default
``nis2``), so an operator/karta can flip the regime with config — no code
change. ``nis2_reporting`` binds this engine to the NIS2 profile and keeps
its existing public API for the runtime.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

_ANCHOR_DETECTION = "detection"
_ANCHOR_AFTER = "after:"  # prefix; remainder is the prior stage name


@dataclass(frozen=True)
class DeadlineRule:
    offset: timedelta
    anchor: str  # _ANCHOR_DETECTION or f"{_ANCHOR_AFTER}{stage}"


@dataclass(frozen=True)
class ReportingProfile:
    name: str
    stages: Tuple[str, ...]            # ordered, clock order
    rules: Dict[str, DeadlineRule]     # stage -> rule
    pending_labels: Dict[str, str]     # stage -> reporting_state label
    significance_threshold: str = "high"


# Severity ladder (low → high) shared by the significance gate.
SEVERITY_LADDER: Tuple[str, ...] = ("info", "low", "medium", "high", "critical")


# ── Time helpers (self-contained; mirror nis2_reporting's parsing) ──────────
def parse_iso(value: str) -> datetime:
    """Parse ISO-8601 into aware UTC. Trailing Z accepted; naive treated UTC."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"reporting_profiles: invalid ISO timestamp {value!r}")
    raw = value.strip()
    if raw.endswith(("Z", "z")):
        raw = raw[:-1] + "+00:00"
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


# ── Shipped profiles ────────────────────────────────────────────────────────
NIS2_PROFILE = ReportingProfile(
    name="nis2",
    stages=("early_warning", "notification", "final_report"),
    rules={
        "early_warning": DeadlineRule(timedelta(hours=24), _ANCHOR_DETECTION),
        "notification": DeadlineRule(timedelta(hours=72), _ANCHOR_DETECTION),
        "final_report": DeadlineRule(timedelta(days=30), _ANCHOR_DETECTION),
    },
    pending_labels={
        "early_warning": "pending_early_warning",
        "notification": "pending_notification",
        "final_report": "pending_final",
    },
)

DORA_PROFILE = ReportingProfile(
    name="dora",
    stages=("initial_notification", "intermediate_report", "final_report"),
    rules={
        # ≤24h from becoming aware (the no-later-than outer bound; the tighter
        # 4h-from-classification clock needs a classification timestamp and is
        # enforced at filing time, not here).
        "initial_notification": DeadlineRule(timedelta(hours=24), _ANCHOR_DETECTION),
        # ≤72h after the initial notification was FILED.
        "intermediate_report": DeadlineRule(timedelta(hours=72), f"{_ANCHOR_AFTER}initial_notification"),
        # ≤1 month after the (latest) intermediate report was FILED. 30 days is
        # the deterministic core; calendar-month precision is a filing-time
        # refinement.
        "final_report": DeadlineRule(timedelta(days=30), f"{_ANCHOR_AFTER}intermediate_report"),
    },
    pending_labels={
        "initial_notification": "pending_initial_notification",
        "intermediate_report": "pending_intermediate_report",
        "final_report": "pending_final_report",
    },
)

PROFILES: Dict[str, ReportingProfile] = {"nis2": NIS2_PROFILE, "dora": DORA_PROFILE}


def active_profile() -> ReportingProfile:
    """Profile selected by env REPORTING_PROFILE (default nis2)."""
    name = (os.environ.get("REPORTING_PROFILE") or "nis2").strip().lower()
    return PROFILES.get(name, NIS2_PROFILE)


# ── Deadline computation ────────────────────────────────────────────────────
def compute_deadlines(
    profile: ReportingProfile,
    detected_at_iso: str,
    filings: Optional[Dict[str, str]] = None,
) -> Dict[str, Optional[str]]:
    """Deadlines per stage (ISO-8601 UTC).

    detection-anchored stages are fixed at detection. after-filing stages are
    fixed only once the anchor stage's filing time is supplied via ``filings``
    (stage -> ISO); until then the deadline is ``None`` (not yet running).
    """
    detected = parse_iso(detected_at_iso)
    filings = filings or {}
    out: Dict[str, Optional[str]] = {}
    for stage in profile.stages:
        rule = profile.rules[stage]
        if rule.anchor == _ANCHOR_DETECTION:
            out[stage] = iso(detected + rule.offset)
        elif rule.anchor.startswith(_ANCHOR_AFTER):
            prior = rule.anchor[len(_ANCHOR_AFTER):]
            prior_filed = filings.get(prior)
            out[stage] = iso(parse_iso(prior_filed) + rule.offset) if prior_filed else None
        else:  # pragma: no cover - guarded by profile construction
            out[stage] = None
    return out


# ── Reporting state machine ─────────────────────────────────────────────────
def reporting_state(
    profile: ReportingProfile,
    record: Dict[str, Any],
    now_iso: str,
) -> Dict[str, Any]:
    """Earliest unfiled stage, its deadline, and whether it is overdue.

    Uses stored ``record['deadlines']`` for detection-anchored stages. If the
    record carries ``detected_at`` + ``filed_at`` (stage -> ISO), after-filing
    deadlines are recomputed live (DORA). A stage whose anchor has not been
    filed yet has ``next_due=None`` and is never overdue.
    """
    stored = record.get("deadlines") or {}
    filed = set(record.get("filed") or [])
    now = parse_iso(now_iso)

    detected_at = record.get("detected_at")
    filings = record.get("filed_at") or {}
    live = compute_deadlines(profile, detected_at, filings) if detected_at else stored

    for stage in profile.stages:
        if stage in filed:
            continue
        due = live.get(stage)
        if due is None:
            due = stored.get(stage)
        overdue = bool(due) and now > parse_iso(due)
        return {"stage": profile.pending_labels[stage], "next_due": due, "overdue": overdue}

    return {"stage": "complete", "next_due": None, "overdue": False}


# ── Significance gate ───────────────────────────────────────────────────────
def _ladder_index(level: Any) -> int:
    if not isinstance(level, str):
        return -1
    try:
        return SEVERITY_LADDER.index(level.strip().lower())
    except ValueError:
        return -1


def is_significant(
    profile: ReportingProfile,
    incident: Dict[str, Any],
    threshold: Optional[str] = None,
) -> bool:
    """True when incident severity_level meets/exceeds the profile threshold.

    Threshold precedence: explicit arg > env REPORTING_SIGNIFICANCE_THRESHOLD
    > profile default. Unknown/missing severity is NOT significant.
    """
    if threshold is None:
        threshold = os.environ.get("REPORTING_SIGNIFICANCE_THRESHOLD") or profile.significance_threshold
    threshold_idx = _ladder_index(threshold)
    if threshold_idx < 0:
        threshold_idx = SEVERITY_LADDER.index("high")
    sev_idx = _ladder_index((incident or {}).get("severity_level"))
    if sev_idx < 0:
        return False
    return sev_idx >= threshold_idx
