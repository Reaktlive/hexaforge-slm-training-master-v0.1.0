"""hexaforge_slm_training_master_drift_detector_hexa — competency baseline: classify (drift_detector).

Intent: Monitors bound adapters for drift signals (eval regression, input drift, new governed data, age) and proposes retrains.

Forseti factory-generated BASELINE logic — this is REAL, executable,
contract-valid logic, NOT a static CUSTOMER_SLOT envelope. It reads named
numeric signals out of the validated XI payload, combines them into a
documented, deterministic weighted score in [0, 1], and emits a verb-
appropriate decision on a contract-valid XO envelope.

HONEST SCOPE: this is a transparent, deterministic heuristic baseline — NOT a
trained production model. It exists so the node SHIPS FUNCTIONAL. Swap in your
proprietary model at the narrow, clearly-marked seam:

    def _drift_detector_impl(features: dict) -> float:   # <- override this one function

`_drift_detector_impl` lives BELOW the AUTOGEN-END marker (re-generation-safe). The
default implementation log-compresses each feature's magnitude (so it
discriminates across orders of magnitude, not just 0-vs-nonzero), takes the
equal-weight mean, and squashes it into [0, 1) — bounded, monotone in each
|feature|, and fully explainable. The node works out of the box; your model
replaces exactly one function.

GENERIC BASELINE — WHAT THIS DOES NOT DO.

External DD: this competency is named after a domain operation, and its stated
intent above describes that operation. The shipped logic does NOT perform it.
It scores whatever named numeric fields it finds on the payload and cuts at a
threshold — a domain-neutral scorer that happens to sit under a domain name.

For a competency whose intent implies an EXTERNAL system (a sandbox, a scanner,
a threat feed, a mailbox API), that gap is the whole capability: nothing is
detonated, queried or fetched here. The baseline is a live, contract-valid
placeholder so the pipeline runs end to end and the seam is testable — it is
not the named operation, and capability_truth.json counts it as heuristic, not
implemented.

Bind the real thing in the CUSTOMER_SLOT below. Until then, read this node's
output as "a score over whatever numbers arrived", never as the intent above.

doctrine-tags: N5-ports (contract-valid XO), N8-audit (H7 log_event on result)
"""
# ─────────────────────────────────────────────────────────────────────
# FORSETI-AUTOGEN-START: hexaforge_slm_training_master_drift_detector_hexa-handler
# Content between AUTOGEN markers is owned by the Forseti generator and
# will be REPLACED on re-generation. To add customer logic that survives
# re-generation, place it BELOW the END marker.
# ─────────────────────────────────────────────────────────────────────
import math
from typing import Any

from src.shared.contracts import HexaforgeSlmTrainingMasterDriftDetectorHexaXoSchema
from src.shared.hexa_record import log_event

# Decision threshold for this competency (verb_kind=classify). Documented and
# overridable; the seam below owns the score, this owns the cut.
THRESHOLD = 0.5


def _xo_default(_field):
    """Contract-valid placeholder for a required XO field the reference baseline
    does not compute (the bound SLM produces the real value at deployment)."""
    import datetime as _dt
    ann = getattr(_field, "annotation", None)
    _origin = getattr(ann, "__origin__", None)
    _args = getattr(ann, "__args__", ())
    if type(None) in _args:            # Optional[X] / Union[X, None] -> sole non-None member
        _inner = [a for a in _args if a is not type(None)]
        if len(_inner) == 1:
            ann = _inner[0]
            _origin = getattr(ann, "__origin__", None)
            _args = getattr(ann, "__args__", ())
    # Literal[...] -> first allowed VALUE (args are values, never types). A
    # parametrised container's args are its element TYPES, so exclude those here.
    _lit = [a for a in _args if isinstance(a, (str, int, float, bool)) and not isinstance(a, type)]
    if _lit:
        return _lit[0]
    # Containers first: dict[str, Any] / list[...] have __origin__ = the builtin,
    # so we must branch on origin BEFORE inspecting element types (the old bug
    # picked a container's KEY type, e.g. str out of dict[str, Any], and returned "").
    if _origin is dict or ann is dict:
        return {}
    if _origin in (list, tuple, set, frozenset) or ann in (list, tuple, set, frozenset):
        return []
    if ann is bool:
        return False
    if ann is int:
        return 0
    if ann is float:
        return 0.0
    if ann is str:
        return ""
    if ann is _dt.datetime:
        return _dt.datetime(1970, 1, 1, tzinfo=_dt.timezone.utc)
    if ann is _dt.date:
        return _dt.date(1970, 1, 1)
    if isinstance(getattr(ann, "model_fields", None), dict):
        return {}                      # nested model -> empty object (structural)
    return ""


def _xo_backfill(_p):
    """Backfill every XO-required field the baseline did not compute so the
    reference payload satisfies its own XO contract by construction. Computed
    fields always win; only genuinely-missing required fields get a placeholder."""
    out = dict(_p)
    for _name, _f in HexaforgeSlmTrainingMasterDriftDetectorHexaXoSchema.model_fields.items():
        if _f.is_required() and _name not in out:
            out[_name] = _xo_default(_f)
    return out


def _xo_validate(_p):
    """Defence-in-depth: validate the (backfilled) payload against the XO payload
    contract, passing only model-known fields (extras are forwarded, not validated)."""
    _body = _xo_backfill(_p)
    HexaforgeSlmTrainingMasterDriftDetectorHexaXoSchema(**{_k: _v for _k, _v in _body.items() if _k in HexaforgeSlmTrainingMasterDriftDetectorHexaXoSchema.model_fields})
    return _body


def _extract_features(body: Any) -> dict:
    """Pull the named numeric signals this competency scores over.

    Doctrine: a competency reads the DECLARED input fields from the validated
    XI payload. We take every finite numeric field (int/float, excluding bools)
    as a named feature. Non-numeric fields are ignored by the baseline; a
    customer model overriding _drift_detector_impl may read the full body instead.
    PII keys are never persisted by this node (only feature MAGNITUDES feed the
    score; the raw body is not logged).
    """
    if not isinstance(body, dict):
        return {}
    feats: dict = {}
    for key, val in body.items():
        if isinstance(val, bool):
            continue
        if isinstance(val, (int, float)):
            try:
                f = float(val)
            except (TypeError, ValueError):
                continue
            if f == f and f not in (float("inf"), float("-inf")):  # not NaN/inf
                feats[str(key)] = f
    return feats


async def handle_xi(payload: Any) -> dict:
    """hexaforge_slm_training_master_drift_detector_hexa.xi — classify the inbound event over its numeric features.

    1. Coerce to dict; pull the normalised body ({event_id, ts, source,
       payload} or a raw event).
    2. Extract named numeric features from the body.
    3. Score them via _drift_detector_impl (customer seam) -> [0, 1].
    4. Derive the verb-appropriate decision at THRESHOLD.
    5. Emit a contract-valid XO envelope; audit the computed result (H7).
    """
    if not isinstance(payload, dict):
        payload = {"payload": payload}
    event_id = payload.get("event_id") or "unknown"
    ts = payload.get("ts") or "1970-01-01T00:00:00Z"
    body = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    features = _extract_features(body)
    # Customer seam — proprietary model goes here; default is the documented
    # equal-weight magnitude mean. Always clamped to [0, 1] for contract safety.
    score = float(_drift_detector_impl(features))
    if score != score:        # NaN guard
        score = 0.0
    score = max(0.0, min(1.0, score))
    decision = "positive" if score >= THRESHOLD else "negative"

    out_payload = {
        "competency": "drift_detector",
        "verb_kind": "classify",
        "score": round(score, 6),
        "decision": decision,
        "threshold": THRESHOLD,
        "feature_names": sorted(features.keys()),
        "feature_count": len(features),
        "baseline": "deterministic-heuristic",
        "source_event_id": event_id,
    }
    # H7 audit — append the computed RESULT (not the raw body / PII) to the
    # HexaRecord append-only chain so the decision is forensically replayable.
    log_event(node_id="hexaforge_slm_training_master_drift_detector_hexa", port="xi", payload={
        "event_id": event_id,
        "competency": "drift_detector",
        "score": out_payload["score"],
        "decision": decision,
    })
    # Defence in depth — the emitted envelope must satisfy the XO contract
    # (event_id / ts / source + payload) before it leaves the node.
    # Fas 3.48 — defence-in-depth against the XO PAYLOAD contract. _xo_validate
    # backfills any XO-required domain field the baseline didn't compute with a
    # contract-valid placeholder (the bound SLM supplies the real value), then
    # validates only model-known fields. The forwarded body carries the backfill
    # so downstream contract checks see a contract-valid payload by construction.
    emitted = {"event_id": str(event_id), "ts": str(ts), "source": "hexaforge_slm_training_master_drift_detector_hexa", "payload": _xo_validate(out_payload)}
    return {
        "node": "hexaforge_slm_training_master_drift_detector_hexa",
        "port": "xi",
        "ok": True,
        "ts": emitted["ts"],
        "score": out_payload["score"],
        "decision": decision,
        "payload": emitted,
        "signature": "competency.classify",
    }


async def handle_xo(payload: Any) -> dict:
    """hexaforge_slm_training_master_drift_detector_hexa.xo — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_drift_detector_hexa", "port": "xo", "ok": True}


async def handle_yi(payload: Any) -> dict:
    """hexaforge_slm_training_master_drift_detector_hexa.yi — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_drift_detector_hexa", "port": "yi", "ok": True}


async def handle_yo(payload: Any) -> dict:
    """hexaforge_slm_training_master_drift_detector_hexa.yo — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_drift_detector_hexa", "port": "yo", "ok": True}


async def handle_zi(payload: Any) -> dict:
    """hexaforge_slm_training_master_drift_detector_hexa.zi — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_drift_detector_hexa", "port": "zi", "ok": True}


async def handle_zo(payload: Any) -> dict:
    """hexaforge_slm_training_master_drift_detector_hexa.zo — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_drift_detector_hexa", "port": "zo", "ok": True}
# ─────────────────────────────────────────────────────────────────────
# FORSETI-AUTOGEN-END: hexaforge_slm_training_master_drift_detector_hexa-handler
#
# Customer code below is preserved on re-generation. Import handlers
# from this file's auto-generated section above and wrap/extend them
# as needed — DO NOT modify the AUTOGEN block itself, or your changes
# will be lost on the next Forseti re-generation.
# ─────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────
# CUSTOMER_SLOT — proprietary model seam (re-generation-safe).
#
# Replace the body of _drift_detector_impl with a call into your trained model. It
# receives the extracted named features and MUST return a float in [0, 1]
# (the node clamps defensively, but your model should be calibrated). The
# node ships FUNCTIONAL with the deterministic default below — this is the
# ONE place customer logic lives; everything above is platform + baseline.
# ─────────────────────────────────────────────────────────────────────
def _drift_detector_impl(features: dict) -> float:
    """Drift urgency in [0, 1] from the locked four-signal policy (HST-213).

    Competency logic (pass-3 addendum §B). Delegates to
    src.shared.drift_policy.evaluate_drift: the returned score is the urgency of
    the highest FIRED signal (high 0.9 / medium 0.6 / low 0.35), and 0.0 when
    nothing fired. Signals: eval_regression (score < threshold+0.05 or -0.03 from
    the promotion score), input_drift (PSI >= 0.20), new_governed_data (>= 500
    unseen k-anon rows), age (>90d AND another signal marginal — never alone).
    The FULL verdict — the four per-signal statuses, the honest
    `cannot_assess` ("no baseline") states, and the tiered trigger_retrain = T2
    proposal (never auto) — is available via drift_policy.evaluate_drift for the
    runtime/UI; this seam exposes the scalar the classify envelope carries.
    Pure and deterministic. Reads named signal fields off `features`; unmeasured
    signals never fabricate drift.
    """
    from src.shared.drift_policy import drift_urgency_score
    return drift_urgency_score(features)


# ─────────────────────────────────────────────────────────────────────
# XO enrichment — surface the FULL four-signal drift verdict (HST-213).
#
# Re-generation-safe: we capture the AUTOGEN handle_xi as _baseline_handle_xi
# and redefine handle_xi below the marker (the documented wrap pattern). The
# baseline still runs — schema validation, THRESHOLD cut, H7 audit, XO backfill
# are untouched — and we then attach the structured verdict under the XO
# payload's `drift` key. `_xo_validate` forwards unknown fields, so the extra
# `drift` object rides the contract-valid envelope without violating it. The
# scalar `score` above and this structured `drift` are two views of one rule.
# ─────────────────────────────────────────────────────────────────────
_baseline_handle_xi = handle_xi  # the AUTOGEN classify handler, captured before override


async def handle_xi(payload: Any) -> dict:  # noqa: F811 — intentional re-gen-safe override
    """drift_detector.xi — baseline classify + the full drift verdict on XO.

    Runs the factory baseline handler unchanged, then attaches the deterministic
    four-signal verdict (evaluate_drift) to the emitted XO payload as `drift`:
    per-signal statuses, the honest `cannot_assess` states, and the tiered
    trigger_retrain=T2 proposal (never auto). Downstream / the /campaign/drift
    binding layer reads `payload.payload.drift`.
    """
    from src.shared.drift_policy import evaluate_drift

    result = await _baseline_handle_xi(payload)
    body = payload.get("payload") if isinstance(payload, dict) and isinstance(payload.get("payload"), dict) else (payload if isinstance(payload, dict) else {})
    try:
        envelope = result.get("payload")
        if isinstance(envelope, dict) and isinstance(envelope.get("payload"), dict):
            envelope["payload"]["drift"] = evaluate_drift(body)
    except Exception:
        # Enrichment must never break the contract-valid baseline result.
        pass
    return result
