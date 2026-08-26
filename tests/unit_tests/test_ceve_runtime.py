"""Fas 2.24d — DYNAMIC proof that strict contracts actually ENFORCE.

ARTIFACT_STRICT_CONTRACT_E2E proves the runtime is WIRED (static). This proves
the wiring BITES: under strict mode a payload that violates its port contract
raises ContractViolation, a contract-derived payload passes, a malformed
canonical envelope is rejected, and the documented opt-out really disables it.

The subject node is resolved from the bundle's OWN contracts at run time (the
first node whose XO schema declares required fields), so this test is agent-
agnostic: it never names a node, a vertical or a field.
"""
import json
import os
import pathlib

import pytest

from src.shared.ceve_runtime import (
    ContractViolation,
    enforce_envelope,
    enforce_payload,
    strict_contracts_enabled,
)

_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _subject():
    """First node whose XO contract declares required fields (self-derived)."""
    for schema_path in sorted((_ROOT / "src" / "nodes").glob("*/schemas.json")):
        try:
            doc = json.loads(schema_path.read_text())
        except (OSError, ValueError):
            continue
        xo = doc.get("xo") or {}
        required = [r for r in (xo.get("required") or []) if isinstance(r, str)]
        if required:
            return schema_path.parent.name, xo, required
    return None, None, None


def _valid_payload(spec):
    """Contract-derived value for every required field — the same construction
    the reference capability uses, so a PASS here means the contract is
    satisfiable, not that the check is lenient."""
    props = spec.get("properties") or {}
    out = {}
    for key in spec.get("required") or []:
        p = props.get(key) or {}
        t = p.get("type")
        if isinstance(t, list):
            t = t[0] if t else None
        enum = p.get("enum")
        if isinstance(enum, list) and enum:
            out[key] = enum[0]
        elif t == "object":
            out[key] = {}
        elif t == "array":
            out[key] = []
        elif t == "integer":
            out[key] = 0
        elif t == "number":
            out[key] = 0.0
        elif t == "boolean":
            out[key] = False
        else:
            out[key] = "reference"
    return out


@pytest.fixture(autouse=True)
def _strict_on(monkeypatch):
    monkeypatch.setenv("DOER_STRICT_CONTRACTS", "1")


def test_strict_is_the_default_and_optout_is_explicit(monkeypatch):
    monkeypatch.delenv("DOER_STRICT_CONTRACTS", raising=False)
    assert strict_contracts_enabled() is True, "strict must be ON when unset (Fas 2.24b)"
    monkeypatch.setenv("DOER_STRICT_CONTRACTS", "0")
    assert strict_contracts_enabled() is False, "the documented opt-out must work"


def test_strict_payload_enforcement_REJECTS_a_contract_violation():
    node, xo, required = _subject()
    if not node:
        pytest.skip("no XO contract in this agent declares required fields")
    # Drop exactly one required field — the minimum violation.
    bad = _valid_payload(xo)
    bad.pop(required[0])
    with pytest.raises(ContractViolation):
        enforce_payload(node, "xo", bad)


def test_strict_payload_enforcement_ACCEPTS_a_contract_derived_payload():
    node, xo, _ = _subject()
    if not node:
        pytest.skip("no XO contract in this agent declares required fields")
    enforce_payload(node, "xo", _valid_payload(xo))


def _any_node():
    """Any node with a schemas.json. The CANONICAL ENVELOPE is shared and always
    declares its routing fields, so envelope enforcement is testable on EVERY
    agent — including one whose payload sub-schemas are deliberately lenient.
    Binding this test to a strict-payload node made it skip on lenient agents,
    and a skipped test cannot notice a neutered guard (found by the A12 mutation
    matrix: enforce_envelope survived being replaced with a no-op)."""
    for schema_path in sorted((_ROOT / "src" / "nodes").glob("*/schemas.json")):
        return schema_path.parent.name
    return None


def test_strict_envelope_enforcement_REJECTS_a_malformed_envelope():
    node = _any_node()
    if not node:
        pytest.skip("this agent emits no node schemas")
    _, xo, _ = _subject()
    env = {"event_id": "e1", "ts": "2026-01-01T00:00:00Z", "node_id": node,
           "port": "xo", "status": "success", "payload": _valid_payload(xo or {})}
    enforce_envelope(node, "xo", env)  # the canonical shape passes
    broken = dict(env)
    broken.pop("status")  # a routing field the runtime always sets
    with pytest.raises(ContractViolation):
        enforce_envelope(node, "xo", broken)


def test_optout_really_disables_enforcement(monkeypatch):
    node, xo, required = _subject()
    if not node:
        pytest.skip("no XO contract in this agent declares required fields")
    monkeypatch.setenv("DOER_STRICT_CONTRACTS", "0")
    bad = _valid_payload(xo)
    bad.pop(required[0])
    enforce_payload(node, "xo", bad)  # documented dev escape hatch: no raise


def test_none_payload_is_an_honest_degraded_signal_not_a_violation():
    node, _, _ = _subject()
    if not node:
        pytest.skip("no XO contract in this agent declares required fields")
    enforce_payload(node, "xo", None)
