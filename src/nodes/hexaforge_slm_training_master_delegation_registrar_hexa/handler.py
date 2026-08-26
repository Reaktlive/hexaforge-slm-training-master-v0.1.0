"""hexaforge_slm_training_master_delegation_registrar_hexa — competency baseline: validate (delegation_registrar).

Intent: Issues, verifies, and revokes delegation grants for specific actions, incorporating grant references into the audit chain.

Forseti factory-generated BASELINE logic — this is REAL, executable,
contract-valid logic, NOT a static CUSTOMER_SLOT envelope. It reads named
numeric signals out of the validated XI payload, combines them into a
documented, deterministic weighted score in [0, 1], and emits a verb-
appropriate decision on a contract-valid XO envelope.

HONEST SCOPE: this is a transparent, deterministic heuristic baseline — NOT a
trained production model. It exists so the node SHIPS FUNCTIONAL. Swap in your
proprietary model at the narrow, clearly-marked seam:

    def _delegation_registrar_impl(features: dict) -> float:   # <- override this one function

`_delegation_registrar_impl` lives BELOW the AUTOGEN-END marker (re-generation-safe). The
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
# FORSETI-AUTOGEN-START: hexaforge_slm_training_master_delegation_registrar_hexa-handler
# Content between AUTOGEN markers is owned by the Forseti generator and
# will be REPLACED on re-generation. To add customer logic that survives
# re-generation, place it BELOW the END marker.
# ─────────────────────────────────────────────────────────────────────
import math
from typing import Any

from src.shared.contracts import HexaforgeSlmTrainingMasterDelegationRegistrarHexaXoSchema
from src.shared.hexa_record import log_event

# Decision threshold for this competency (verb_kind=validate). Documented and
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
    for _name, _f in HexaforgeSlmTrainingMasterDelegationRegistrarHexaXoSchema.model_fields.items():
        if _f.is_required() and _name not in out:
            out[_name] = _xo_default(_f)
    return out


def _xo_validate(_p):
    """Defence-in-depth: validate the (backfilled) payload against the XO payload
    contract, passing only model-known fields (extras are forwarded, not validated)."""
    _body = _xo_backfill(_p)
    HexaforgeSlmTrainingMasterDelegationRegistrarHexaXoSchema(**{_k: _v for _k, _v in _body.items() if _k in HexaforgeSlmTrainingMasterDelegationRegistrarHexaXoSchema.model_fields})
    return _body


def _extract_features(body: Any) -> dict:
    """Pull the named numeric signals this competency scores over.

    Doctrine: a competency reads the DECLARED input fields from the validated
    XI payload. We take every finite numeric field (int/float, excluding bools)
    as a named feature. Non-numeric fields are ignored by the baseline; a
    customer model overriding _delegation_registrar_impl may read the full body instead.
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
    """hexaforge_slm_training_master_delegation_registrar_hexa.xi — validate the inbound event over its numeric features.

    1. Coerce to dict; pull the normalised body ({event_id, ts, source,
       payload} or a raw event).
    2. Extract named numeric features from the body.
    3. Score them via _delegation_registrar_impl (customer seam) -> [0, 1].
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
    score = float(_delegation_registrar_impl(features))
    if score != score:        # NaN guard
        score = 0.0
    score = max(0.0, min(1.0, score))
    decision = "valid" if score >= THRESHOLD else "invalid"

    out_payload = {
        "competency": "delegation_registrar",
        "verb_kind": "validate",
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
    log_event(node_id="hexaforge_slm_training_master_delegation_registrar_hexa", port="xi", payload={
        "event_id": event_id,
        "competency": "delegation_registrar",
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
    emitted = {"event_id": str(event_id), "ts": str(ts), "source": "hexaforge_slm_training_master_delegation_registrar_hexa", "payload": _xo_validate(out_payload)}
    return {
        "node": "hexaforge_slm_training_master_delegation_registrar_hexa",
        "port": "xi",
        "ok": True,
        "ts": emitted["ts"],
        "score": out_payload["score"],
        "decision": decision,
        "payload": emitted,
        "signature": "competency.validate",
    }


async def handle_xo(payload: Any) -> dict:
    """hexaforge_slm_training_master_delegation_registrar_hexa.xo — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_delegation_registrar_hexa", "port": "xo", "ok": True}


async def handle_yi(payload: Any) -> dict:
    """hexaforge_slm_training_master_delegation_registrar_hexa.yi — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_delegation_registrar_hexa", "port": "yi", "ok": True}


async def handle_yo(payload: Any) -> dict:
    """hexaforge_slm_training_master_delegation_registrar_hexa.yo — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_delegation_registrar_hexa", "port": "yo", "ok": True}


async def handle_zi(payload: Any) -> dict:
    """hexaforge_slm_training_master_delegation_registrar_hexa.zi — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_delegation_registrar_hexa", "port": "zi", "ok": True}


async def handle_zo(payload: Any) -> dict:
    """hexaforge_slm_training_master_delegation_registrar_hexa.zo — platform port (no extra logic on this port)."""
    return {"node": "hexaforge_slm_training_master_delegation_registrar_hexa", "port": "zo", "ok": True}
# ─────────────────────────────────────────────────────────────────────
# FORSETI-AUTOGEN-END: hexaforge_slm_training_master_delegation_registrar_hexa-handler
#
# Customer code below is preserved on re-generation. Import handlers
# from this file's auto-generated section above and wrap/extend them
# as needed — DO NOT modify the AUTOGEN block itself, or your changes
# will be lost on the next Forseti re-generation.
# ─────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────
# CUSTOMER_SLOT — proprietary model seam (re-generation-safe).
#
# Replace the body of _delegation_registrar_impl with a call into your trained model. It
# receives the extracted named features and MUST return a float in [0, 1]
# (the node clamps defensively, but your model should be calibrated). The
# node ships FUNCTIONAL with the deterministic default below — this is the
# ONE place customer logic lives; everything above is platform + baseline.
# ─────────────────────────────────────────────────────────────────────
def _delegation_registrar_impl(features: dict) -> float:
    """Deterministic baseline score in [0, 1] over the named features.

    DEFAULT (honest heuristic, NOT a trained model): log-compress each feature's
    magnitude with log1p(|f|) so the score discriminates across ORDERS OF
    MAGNITUDE (a 9000 transaction reads materially higher than a 5 one, instead
    of both saturating), take the equal-weight mean, then squash to [0, 1) with
    z / (1 + z). With no features the score is 0.0 (nothing to go on). Monotone
    in each |feature| and fully explainable. Override this function with your
    model to productionise.
    """
    if not features:
        return 0.0
    total = 0.0
    for value in features.values():
        total += math.log1p(abs(float(value)))
    z = total / float(len(features))
    return z / (1.0 + z)
