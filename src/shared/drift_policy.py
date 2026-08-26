"""Drift policy — the four-signal retrain-proposal rule for drift_detector (HST-213).

CUSTOMER competency logic (pass-3 addendum §B), re-generation-safe: this module
lives in src/shared/ (a declared customer extension point) and is imported by the
node's CUSTOMER_SLOT seam. It is PURE — no I/O, no heavy deps — so it is unit-
testable in isolation and deterministic for a given input.

The rule (locked): monitor a bound adapter on FOUR orthogonal signals; any one
crossing its threshold emits a TIERED retrain PROPOSAL (trigger_retrain = T2) —
never an auto-execution. A signal whose inputs are missing returns
`cannot_assess` ("no baseline"), NEVER a fabricated `clear`/"no drift".

    signal              trigger                                             urgency
    ----------------    -----------------------------------------------    -------
    eval_regression     score < threshold + 0.05  OR                       high
                        score <= promotion_score - 0.03
    input_drift         PSI >= 0.20  (>= 0.25 -> high)                      medium/high
    new_governed_data   >= 500 new k-anon rows the generation never saw     low
    age                 age_days > 90 AND another signal is marginal        low
                        (age ALONE never triggers)

`marginal` = close to but not over the line, so `age` can co-fire without any
single signal having crossed. Bands are documented per signal below.
"""
from __future__ import annotations

from typing import Any, Optional

# ── Locked thresholds (pass-3 addendum §B / §C) ──────────────────────────
EVAL_MARGIN = 0.05           # score must clear threshold by this to be "safe"
EVAL_REGRESSION_DROP = 0.03  # absolute drop from the promotion score that fires
PSI_TRIGGER = 0.20
PSI_HIGH = 0.25
NEW_ROWS_TRIGGER = 500
AGE_DAYS_TRIGGER = 90

# Marginal bands — "close to the line but not over it".
EVAL_MARGINAL_BAND = 0.02    # score in [thr+0.05, thr+0.07) is marginal
PSI_MARGINAL_LOW = 0.15      # PSI in [0.15, 0.20) is marginal
NEW_ROWS_MARGINAL = 400      # rows in [400, 500) is marginal

FIRED = "fired"
CLEAR = "clear"
MARGINAL = "marginal"
CANNOT_ASSESS = "cannot_assess"

_URGENCY_RANK = {None: 0, "low": 1, "medium": 2, "high": 3}


def _is_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x == x  # not NaN


def _signal(name: str, status: str, *, urgency: Optional[str] = None,
            value: Any = None, threshold: Any = None, reason: str = "") -> dict:
    return {
        "name": name,
        "status": status,
        "urgency": urgency if status == FIRED else None,
        "value": value,
        "threshold": threshold,
        "reason": reason,
    }


def _eval_regression(inp: dict) -> dict:
    score = inp.get("eval_score")
    thr = inp.get("eval_threshold")
    if not _is_number(score) or not _is_number(thr):
        return _signal("eval_regression", CANNOT_ASSESS,
                       reason="no baseline: eval_score/eval_threshold not measured")
    fired = score < thr + EVAL_MARGIN
    promo = inp.get("promotion_score")
    if not fired and _is_number(promo) and score <= promo - EVAL_REGRESSION_DROP:
        fired = True
    if fired:
        return _signal("eval_regression", FIRED, urgency="high", value=score,
                       threshold=thr + EVAL_MARGIN,
                       reason="score below (threshold + 0.05) or >=0.03 under promotion score")
    marginal = score < thr + EVAL_MARGIN + EVAL_MARGINAL_BAND
    return _signal("eval_regression", MARGINAL if marginal else CLEAR, value=score,
                   threshold=thr + EVAL_MARGIN)


def _input_drift(inp: dict) -> dict:
    psi = inp.get("psi")
    if not _is_number(psi) or psi < 0:
        return _signal("input_drift", CANNOT_ASSESS,
                       reason="no baseline: PSI not measurable")
    if psi >= PSI_TRIGGER:
        urg = "high" if psi >= PSI_HIGH else "medium"
        return _signal("input_drift", FIRED, urgency=urg, value=psi, threshold=PSI_TRIGGER,
                       reason="PSI at/over 0.20 (>=0.25 escalates)")
    marginal = psi >= PSI_MARGINAL_LOW
    return _signal("input_drift", MARGINAL if marginal else CLEAR, value=psi, threshold=PSI_TRIGGER)


def _new_governed_data(inp: dict) -> dict:
    rows = inp.get("new_rows")
    if not _is_number(rows):
        return _signal("new_governed_data", CANNOT_ASSESS,
                       reason="no baseline: new-row count not available")
    rows = int(rows)
    if rows >= NEW_ROWS_TRIGGER:
        return _signal("new_governed_data", FIRED, urgency="low", value=rows,
                       threshold=NEW_ROWS_TRIGGER, reason=">=500 new k-anon rows unseen by this generation")
    marginal = rows >= NEW_ROWS_MARGINAL
    return _signal("new_governed_data", MARGINAL if marginal else CLEAR, value=rows,
                   threshold=NEW_ROWS_TRIGGER)


def _age(inp: dict, others: list) -> dict:
    age_days = inp.get("age_days")
    if not _is_number(age_days):
        return _signal("age", CANNOT_ASSESS, reason="no baseline: generation age unknown")
    over = age_days > AGE_DAYS_TRIGGER
    # Age NEVER triggers on its own — only when another signal has fired OR is marginal.
    co_signal = any(s["status"] in (FIRED, MARGINAL) for s in others)
    if over and co_signal:
        return _signal("age", FIRED, urgency="low", value=age_days, threshold=AGE_DAYS_TRIGGER,
                       reason=">90d AND another signal marginal/fired (age alone never triggers)")
    return _signal("age", CLEAR, value=age_days, threshold=AGE_DAYS_TRIGGER)


def evaluate_drift(inputs: dict) -> dict:
    """Evaluate the four drift signals for one bound adapter.

    inputs (all optional; a missing input yields `cannot_assess` for that signal):
        eval_score, eval_threshold, promotion_score  -> eval_regression
        psi                                           -> input_drift
        new_rows                                      -> new_governed_data
        age_days                                      -> age

    Returns a deterministic verdict:
        {
          "signals": [ {name, status, urgency, value, threshold, reason}, ... ],
          "proposal": {"action": "trigger_retrain", "tier": "T2",
                       "urgency": <max fired urgency>, "reasons": [...]} | None,
          "cannot_assess": [names],   # signals with no baseline — never counted as clear
        }
    """
    if not isinstance(inputs, dict):
        inputs = {}
    ev = _eval_regression(inputs)
    idr = _input_drift(inputs)
    ngd = _new_governed_data(inputs)
    age = _age(inputs, [ev, idr, ngd])   # age depends on the other three
    signals = [ev, idr, ngd, age]

    fired = [s for s in signals if s["status"] == FIRED]
    cannot = [s["name"] for s in signals if s["status"] == CANNOT_ASSESS]

    proposal = None
    if fired:
        top = max((s["urgency"] for s in fired), key=lambda u: _URGENCY_RANK[u])
        proposal = {
            "action": "trigger_retrain",
            "tier": "T2",                       # tiered PROPOSAL — never auto-execute
            "auto": False,
            "urgency": top,
            "reasons": [f"{s['name']}: {s['reason']}" for s in fired],
        }
    return {"signals": signals, "proposal": proposal, "cannot_assess": cannot}


def drift_urgency_score(inputs: dict) -> float:
    """Map the verdict to a [0,1] urgency for the node's classify envelope score.
    fired high=0.9 / medium=0.6 / low=0.35; nothing fired = 0.0. Deterministic."""
    verdict = evaluate_drift(inputs)
    p = verdict["proposal"]
    if not p:
        return 0.0
    return {"high": 0.9, "medium": 0.6, "low": 0.35}.get(p["urgency"], 0.0)
