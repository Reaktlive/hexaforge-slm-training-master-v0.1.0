#!/usr/bin/env python3
"""Contract eval-harness for hexaforge_slm_training_master_safety_validator_hexa (Forseti-generated).

Fas 2.12a — the harness DOES what the acceptance criteria say: every eval row's
output is validated against the node's OUTPUT CONTRACT (resolved through
io_contract.json's output_schema reference — the single source). Until a model
is bound, this proves the SEED CORPUS itself satisfies criterion 1; bind a
model and re-run to score real model outputs the same way. Fail-closed: a
missing/unreadable contract is CONTRACT_MISSING (exit 1), never a silent pass.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(PACK))
EVAL = os.path.join(PACK, "seed_data", "eval.jsonl")
IO_CONTRACT = os.path.join(PACK, "io_contract.json")

_TYPE_MAP = {
    "string": str, "integer": int, "number": (int, float), "boolean": bool,
    "object": dict, "array": list,
}


def load_eval():
    rows = []
    if not os.path.exists(EVAL):
        return rows
    with open(EVAL) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_output_schema():
    """Resolve the output contract THROUGH io_contract.json (single source)."""
    with open(IO_CONTRACT) as f:
        io = json.load(f)
    ref = io.get("output_schema")
    path = os.path.join(ROOT, ref)
    with open(path) as f:
        doc = json.load(f)
    return ref, (doc.get("schema") or doc)


def validate_output(out, schema):
    """Minimal fail-closed contract check: required fields present, declared
    top-level property types honoured. Mirrors the runtime's enforcement axis
    (presence + type), never weaker than the declared form."""
    if not isinstance(out, dict):
        return False
    for req in (schema.get("required") or []):
        if req not in out:
            return False
    props = schema.get("properties") or {}
    for key, spec in props.items():
        if key not in out or not isinstance(spec, dict):
            continue
        t = spec.get("type")
        expected = _TYPE_MAP.get(t) if isinstance(t, str) else None
        if expected is not None and out[key] is not None and not isinstance(out[key], expected):
            return False
    return True


def main():
    try:
        contract_ref, schema = load_output_schema()
    except (OSError, ValueError) as e:
        report = {
            "node": os.path.basename(PACK),
            "status": "CONTRACT_MISSING",
            "error": str(e),
            "note": "io_contract.json's output_schema reference must resolve — fail-closed, never a silent pass.",
        }
        with open(os.path.join(HERE, "slm_eval.json"), "w") as f:
            json.dump(report, f, indent=2)
        print(json.dumps(report, indent=2))
        sys.exit(1)
    rows = load_eval()
    total = len(rows)
    schema_valid = sum(1 for r in rows if validate_output(r.get("output"), schema))
    report = {
        "node": os.path.basename(PACK),
        "contract": contract_ref,
        "criteria": "required-fields present + declared top-level property types (acceptance.md criterion 1)",
        "eval_count": total,
        "schema_valid": schema_valid,
        "schema_valid_pct": (schema_valid / total) if total else 0.0,
        "status": "CORPUS_OK" if total and schema_valid == total else ("EMPTY" if not total else "CORPUS_FAIL"),
        "note": "No model bound: this proves the seed corpus against the output contract. Bind a model and re-run to score real outputs the same way.",
    }
    with open(os.path.join(HERE, "slm_eval.json"), "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))
    if report["status"] != "CORPUS_OK":
        sys.exit(1)


if __name__ == "__main__":
    main()
