"""NIS2 Article 23 incident-reporting clock — pure, no-I/O regulatory layer.

T-04-022 (Closes #51).

NIS2 Art 23 obliges essential/important entities to notify the competent
authority / CSIRT of a *significant* incident on a three-stage clock:

  1. early warning   — within 24 hours of becoming aware;
  2. notification    — within 72 hours of becoming aware;
  3. final report    — within 1 month of the notification.

This module is the deterministic core of that clock. It is intentionally
PURE — no clock reads, no network, no state — so the whole thing is unit
testable by feeding a fixed ``detected_at`` and a synthetic ``now``. The
runtime (runtime/state.py + runtime/api_server.py) layers persistence,
the HexaRecord audit trail, and the HTTP surface on top.

Doctrine ties:
  * Only *significant* incidents create an obligation (``is_significant``),
    so the clock never fires on noise.
  * The dispatch seam (``dispatch_report``) is PII-clean by construction:
    it refuses to dispatch any payload that carries a canonical
    ``FORBIDDEN_PII_KEY`` (regelverk §11 PII-doctrine), and is INERT in
    dev (no webhook configured) so tests never make a real network call.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from urllib import error as _urlerror
from urllib import request as _urlrequest

from src.shared.anonymization import collect_pii_paths
from src.shared import reporting_profiles as _rp
from src.shared.reporting_profiles import (  # re-export profile machinery
    ReportingProfile, NIS2_PROFILE, DORA_PROFILE, PROFILES, active_profile,
)

# ──────────────────────────────────────────────────────────────
# Clock constants — NIS2 Art 23 deadlines, relative to detection.
# ──────────────────────────────────────────────────────────────
EARLY_WARNING_HOURS = 24
NOTIFICATION_HOURS = 72
FINAL_REPORT_DAYS = 30

# The three filing stages, in order. Anything outside this set is invalid.
STAGES: tuple = ("early_warning", "notification", "final_report")

# Ordered severity ladder (low → high). ``is_significant`` compares an
# incident's severity_level against the configured threshold on this ladder.
SEVERITY_LADDER: tuple = ("info", "low", "medium", "high", "critical")

# Stage → which deadline key gates it, in clock order.
_STAGE_DEADLINE = {
    "early_warning": "early_warning",
    "notification": "notification",
    "final_report": "final_report",
}


# ──────────────────────────────────────────────────────────────
# Time helpers
# ──────────────────────────────────────────────────────────────
def _parse_iso(value: str) -> datetime:
    """Parse an ISO-8601 timestamp robustly into an aware UTC datetime.

    Accepts a trailing ``Z`` (Zulu) as well as explicit offsets. Naive
    timestamps (no tz) are *treated as UTC* — the regulatory clock must
    never silently shift by the host's local zone.
    """
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"nis2_reporting: invalid ISO timestamp {value!r}")
    raw = value.strip()
    if raw.endswith("Z") or raw.endswith("z"):
        raw = raw[:-1] + "+00:00"
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _iso(dt: datetime) -> str:
    """Render an aware datetime as a UTC ISO-8601 string."""
    return dt.astimezone(timezone.utc).isoformat()


# ──────────────────────────────────────────────────────────────
# 1. Deadlines
# ──────────────────────────────────────────────────────────────
def compute_deadlines(detected_at_iso: str) -> Dict[str, str]:
    """NIS2 Art 23 deadlines from detection (delegates to the NIS2 reporting
    profile). Returns ISO-8601 (UTC): early_warning +24h, notification +72h,
    final_report +30d. Behaviour unchanged; the engine now backs it so the
    same clock can run other regimes (see reporting_profiles / DORA_PROFILE)."""
    return {k: v for k, v in _rp.compute_deadlines(_rp.NIS2_PROFILE, detected_at_iso).items()}


# ──────────────────────────────────────────────────────────────
# 2. Reporting state machine
# ──────────────────────────────────────────────────────────────
def reporting_state(record: Dict[str, Any], now_iso: str) -> Dict[str, Any]:
    """Live NIS2 reporting state for a record (delegates to the engine bound
    to the NIS2 profile). Returns the earliest unfiled stage
    (pending_early_warning | pending_notification | pending_final), its
    next_due deadline, and whether it is overdue; complete when all filed."""
    return _rp.reporting_state(_rp.NIS2_PROFILE, record, now_iso)


# ──────────────────────────────────────────────────────────────
# 3. Significance gate
# ──────────────────────────────────────────────────────────────
def _ladder_index(level: Any) -> int:
    """Index of a severity_level on SEVERITY_LADDER, or -1 if unknown."""
    if not isinstance(level, str):
        return -1
    try:
        return SEVERITY_LADDER.index(level.strip().lower())
    except ValueError:
        return -1


def is_significant(incident: Dict[str, Any], threshold: Optional[str] = None) -> bool:
    """True when the incident's severity_level meets/exceeds the threshold.

    The threshold defaults to env ``NIS2_SIGNIFICANCE_THRESHOLD`` or
    ``"high"``. Only significant incidents create a NIS2 reporting
    obligation, so the clock never fires on below-threshold noise. An
    unknown/missing severity_level is treated as NOT significant.
    """
    if threshold is None:
        threshold = os.environ.get("NIS2_SIGNIFICANCE_THRESHOLD") or "high"
    threshold_idx = _ladder_index(threshold)
    if threshold_idx < 0:
        threshold_idx = SEVERITY_LADDER.index("high")
    sev = (incident or {}).get("severity_level")
    sev_idx = _ladder_index(sev)
    if sev_idx < 0:
        return False
    return sev_idx >= threshold_idx


# ──────────────────────────────────────────────────────────────
# 4. Reporting record factory
# ──────────────────────────────────────────────────────────────
def build_reporting_record(incident: Dict[str, Any], detected_at_iso: str) -> Dict[str, Any]:
    """Build the per-incident reporting record stamped at detection time.

    Returns::

        {"deadlines": {...}, "filed": [], "dispatch_log": []}

    ``incident`` is accepted for symmetry / future use (e.g. carrying the
    severity onto the record) but no PII is copied out of it.
    """
    return {
        "deadlines": compute_deadlines(detected_at_iso),
        "filed": [],
        "dispatch_log": [],
    }


# ──────────────────────────────────────────────────────────────
# 5. Dispatch seam (pluggable, PII-clean, inert by default)
# ──────────────────────────────────────────────────────────────
def dispatch_report(stage: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Pluggable dispatch seam for a filed report stage.

    Contract:
      * The payload is FIRST scrubbed against the canonical
        ``FORBIDDEN_PII_KEYS`` floor via ``collect_pii_paths``. If any
        forbidden key is present the dispatch is REFUSED — nothing leaves
        the process — and the leaked key-paths are returned. This is the
        doctrine floor: a regulatory filing must never carry PII.
      * If env ``NIS2_DISPATCH_WEBHOOK`` is unset the seam is INERT (dev
        default) — it returns ``dispatched=False`` with reason
        ``no_webhook_configured`` and makes NO network call. Tests run
        against this default, so the suite never touches the network.
      * Only when a webhook IS configured AND the payload is PII-clean does
        an actual HTTP POST occur.
    """
    leaked = collect_pii_paths(payload)
    if leaked:
        return {
            "dispatched": False,
            "reason": "pii_blocked",
            "leaked_keys": leaked,
            "stage": stage,
        }

    webhook = (os.environ.get("NIS2_DISPATCH_WEBHOOK"))
    if not webhook:
        return {
            "dispatched": False,
            "reason": "no_webhook_configured",
            "stage": stage,
        }

    # Real dispatch path — only reached with a configured webhook AND a
    # PII-clean payload. Kept behind the webhook check so it is fully inert
    # in dev / under test.
    body = json.dumps({"stage": stage, "payload": payload}).encode("utf-8")
    req = _urlrequest.Request(
        webhook,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with _urlrequest.urlopen(req, timeout=10) as resp:  # nosec B310 - env-configured webhook
            status = getattr(resp, "status", None) or resp.getcode()
        return {"dispatched": True, "reason": "ok", "status": status, "stage": stage}
    except _urlerror.URLError as exc:  # pragma: no cover - network failure path
        return {
            "dispatched": False,
            "reason": "dispatch_error",
            "error": str(exc),
            "stage": stage,
        }
