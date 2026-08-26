"""Runtime contract enforcement (CEVE-Light).

Blocker2 — strict-contract split: the object that crosses a port is the CANONICAL
ENVELOPE ({event_id, ts, node_id, port, status, payload, ...}); its `payload` is
validated against the SEPARATE per-node payload sub-schema (the generated
{Node}{Port}Schema in src/shared/contracts.py). Two checks, both ON BY DEFAULT
(Fas 2.24b — explicit opt-out via DOER_STRICT_CONTRACTS=0):
  * enforce_payload(node, port, payload)  — payload vs {Node}{Port}Schema
  * enforce_envelope(node, port, envelope) — whole envelope vs CanonicalEnvelope
Neither raises on a None payload (an absent output is an honest degraded/stub
signal, reported by the node status — never a contract violation).
"""
import json
import os
from typing import Any, Optional

from pydantic import BaseModel

_SCHEMA_CACHE: dict[str, dict] = {}


def _load(node_id: str) -> dict:
    if node_id not in _SCHEMA_CACHE:
        path = os.path.join(os.path.dirname(__file__), "..", "nodes", node_id, "schemas.json")
        with open(path) as f:
            _SCHEMA_CACHE[node_id] = json.load(f)
    return _SCHEMA_CACHE[node_id]


def validate_contract(node_id: str, port: str, payload: Any) -> None:
    """Presence check: the node MUST declare a contract for this port.

    This is the cheap structural cross-check. Payload-level enforcement is
    enforce_output() below (strict mode) — validate_contract deliberately does
    NOT claim to have validated the payload.
    """
    schemas = _load(node_id)
    if port not in schemas:
        raise ValueError(f"no schema for {node_id}.{port}")
    return None


# ── A5/A5b — strict runtime contract validation ──────────────────────────
# validate_contract() only proves a contract EXISTS. Under strict mode the
# runtime additionally validates each node's actual OUTPUT payload against
# the generated Pydantic model for that port. Fas 2.24b: strict is the
# DEFAULT everywhere (runtime, CI, release verification) — a declared-but-
# unenforced contract is exactly the claims/reality gap class this factory
# refuses to ship. The explicit opt-out (=0) is for dev/experimentation.
_FALSY = {"0", "false", "no", "off"}

ENV_STRICT_CONTRACTS = "DOER_STRICT_CONTRACTS"


class ContractViolation(ValueError):
    """A node emitted a payload/envelope that does not satisfy its port contract."""


def strict_contracts_enabled() -> bool:
    # Fas 2.24b — strict contract enforcement is the DEFAULT (fail-closed: the
    # typed port contract is ENFORCED, not just declared — consistent with CCAS,
    # audit and ingress auth, which all fail closed by default). Opting OUT is
    # explicit and documented: DOER_STRICT_CONTRACTS=0 (dev/experimentation).
    return os.environ.get(ENV_STRICT_CONTRACTS, "1").strip().lower() not in _FALSY


def _pascal(text: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in str(text).replace("-", "_").split("_"))


class CanonicalEnvelope(BaseModel):
    """The EXACT object that crosses every XO/XI/YO port — the canonical envelope.

    Its `payload` is the free-form body (validated separately, per-node, by
    enforce_payload against {Node}{Port}Schema). Deliberately lenient: the five
    routing fields are required (the runtime always sets them), everything else
    is optional and unknown keys are ignored — so every envelope the runtime
    already builds satisfies it, in every vertical.
    """

    event_id: str
    ts: str
    node_id: str
    port: str
    status: str
    payload: Optional[dict] = None
    provenance: Optional[dict] = None
    degradation: Optional[dict] = None
    trace_id: Optional[str] = None
    tenant_id: Optional[str] = None
    contract_id: Optional[str] = None
    contract_version: Optional[str] = None


def model_for(node_id: str, port: str):
    """The generated per-node payload sub-schema for <node_id>.<port>, or None."""
    try:
        from src.shared import contracts as _contracts
    except Exception:
        return None
    return getattr(_contracts, f"{_pascal(node_id)}{_pascal(port.lower())}Schema", None)


def _model_forbids_extras(model) -> bool:
    """True when the generated model mirrors a closed schema (additionalProperties:false).

    Only a closed contract may be normalized to its validated form — see
    enforce_payload. Read defensively: a model without model_config, or a
    pydantic v1 Config, must never be treated as closed.
    """
    cfg = getattr(model, "model_config", None)
    if isinstance(cfg, dict) and cfg.get("extra") == "forbid":
        return True
    v1 = getattr(model, "Config", None)
    return bool(v1 is not None and getattr(v1, "extra", None) == "forbid")


def _reference_default(_field):
    """Contract-valid, typed placeholder for a REQUIRED field a reference skeleton
    did not itself produce (the bound SLM supplies the real value at deployment)."""
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


def _reference_backfill(model, payload: dict) -> dict:
    """Fas 3.48 — reference-skeleton XO reconciliation. The LLM contract synthesizer
    may require DOMAIN fields the generic reference scaffold does not itself emit;
    without reconciliation the reference pipeline fail-closes on its own contract on
    the first such node and never completes. Fill ONLY genuinely-missing REQUIRED
    fields with typed placeholders (introspected from the pydantic model, so it can
    never drift from the contract). A value the node DID emit is never overridden;
    wrong-typed / forbidden fields are NOT tolerated (they still reach enforcement
    and fail closed). module_truth + the degraded banner disclose the skeleton
    status — this is structural conformance for the unbound skeleton, never a
    semantic guarantee. Applied only on the live-pipeline path (reference_fill=True);
    the strict-enforcement contract used by the security gate's REJECTS proof is
    unchanged."""
    out = dict(payload)
    for _name, _f in model.model_fields.items():
        try:
            _req = _f.is_required()
        except Exception:
            _req = bool(getattr(_f, "required", False))
        if _req and _name not in out:
            out[_name] = _reference_default(_f)
    return out


def enforce_payload(node_id: str, port: str, payload: Any, reference_fill: bool = False):
    """Fail-closed validation of a node's emitted PAYLOAD, RETURNING the validated form.

    Validates the inner payload against the per-node payload sub-schema
    ({Node}{Port}Schema). A None payload is NOT a violation — an absent output is
    reported by the typed node status / degraded signal (A6), not the contract
    validator. An invalid, non-empty payload is fail-closed: never forwarded.

    Fas 3.37 (external DD, counter-proof) — VALIDATE AND NORMALIZE, NOT JUST CHECK.

    This used to call model(**payload), discard the result, and let the caller
    carry on with the RAW payload. Two consequences, and the second is the
    serious one:

      1. Whatever pydantic dropped (extras, when the model ignored them) stayed
         in the object that actually travelled downstream.
      2. The object the executor received was therefore NOT the object that had
         been validated — and not the object the approval hash bound. An
         undocumented field could ride along past strict enforcement, leave
         canonical_action_ref unchanged, and still reach the side effect.

    The validated model is now dumped back to a dict and RETURNED. Callers must
    forward the returned value; the raw input must not survive validation. When
    strict mode is off, or no model exists for the port, the payload is returned
    unchanged so behaviour is identical to before.
    """
    if not strict_contracts_enabled():
        return payload
    if payload is None:
        return payload
    model = model_for(node_id, port)
    if model is None:
        return payload
    if not isinstance(payload, dict):
        raise ContractViolation(
            f"{node_id}.{port} payload is {type(payload).__name__}, contract expects an object"
        )
    if reference_fill:
        # Live pipeline only: complete a reference skeleton's missing REQUIRED
        # fields so it satisfies its own (LLM-synthesized) XO contract. Gate's
        # REJECTS proof calls enforce_payload WITHOUT this flag, so it is untouched.
        payload = _reference_backfill(model, payload)
    try:
        _validated = model(**payload)
    except Exception as exc:  # pydantic.ValidationError (and anything it raises)
        raise ContractViolation(f"{node_id}.{port} payload violates its contract: {exc}") from exc
    # Normalize ONLY where the contract is closed.
    #
    # A closed contract (schema additionalProperties:false -> model
    # extra="forbid") admits exactly its declared fields, so the validated
    # object and the input are the same set: returning the normalized form is
    # lossless, and it guarantees the object that travels on IS the object that
    # was validated.
    #
    # An OPEN contract must be returned unchanged. Narrowing an open payload to
    # the model's declared fields would silently DELETE data the contract
    # permits — and a model that is incomplete relative to what a node actually
    # emits would empty the payload entirely. Validation may reject; it must
    # never quietly discard.
    if _model_forbids_extras(model):
        try:
            return _validated.model_dump(exclude_unset=True)
        except AttributeError:  # pydantic v1 fallback
            return _validated.dict(exclude_unset=True)
    return payload


def enforce_envelope(node_id: str, port: str, envelope: Any) -> None:
    """Fail-closed validation of the WHOLE envelope vs CanonicalEnvelope (strict only).

    Validates the exact object crossing the port — the canonical envelope — not
    its inner payload (that is enforce_payload's job). A None envelope is not a
    violation (nothing crossed); a non-dict, or a dict missing the required
    routing fields, is fail-closed.
    """
    if not strict_contracts_enabled():
        return
    if envelope is None:
        return
    if not isinstance(envelope, dict):
        raise ContractViolation(
            f"{node_id}.{port} envelope is {type(envelope).__name__}, expected an object"
        )
    try:
        CanonicalEnvelope(**envelope)
    except Exception as exc:  # pydantic.ValidationError (and anything it raises)
        raise ContractViolation(
            f"{node_id}.{port} envelope violates the canonical envelope contract: {exc}"
        ) from exc


# Back-compat alias — pre-split callers/tests that imported enforce_output get the
# payload check (the historical semantics of enforce_output were payload-level).
enforce_output = enforce_payload

