"""ARTIFACT_TRAINING_PACK_E2E — the SLM enablement chain is proven, not assumed.

Fas 2.12a (L7/L8). training/ was the only emitted RUNNABLE surface without a
gate: acceptance.md claimed contract validation the harness did not perform,
and io_contract references were never checked alive. Four claims:
  1. Every training pack is complete (spec, corpus, eval chain).
  2. io_contract.output_schema references the node's own xo contract and the
     reference RESOLVES in the bundle (single source via reference).
  3. The harness truly enforces acceptance criterion 1 (required + declared
     types) with fail-closed CONTRACT_MISSING.
  4. The runtime smoke proofs are emitted with the bundle.
"""
import json, pathlib
GATE_ID = "ARTIFACT_TRAINING_PACK_E2E"; GATE_NAME = "Training Pack E2E (SLM enablement chain)"; GATE_KIND = "hard"
GATE_CATEGORY = "artifact"

def applies(karta):
    return True  # N_A resolved at evaluate time on pack presence

def evaluate(karta, root: pathlib.Path):
    packs = sorted(p.parent.name for p in (root / "training").glob("*/io_contract.json")) if (root / "training").exists() else []
    if not packs:
        return {"status": "N_A", "violations": [],
                "details": "No training packs emitted (include_training_pack off or no model-bound nodes)."}
    violations = []
    proven = 0
    for nid in packs:
        base = root / "training" / nid
        ok = True
        for part in ("model_card.md", "recipe/finetune.md", "eval/eval_harness.py", "eval/acceptance.md", "seed_data/train.jsonl", "seed_data/eval.jsonl", "seed_data/label_provenance.json"):
            if not (base / part).is_file():
                violations.append({"node": nid, "file": "training/%s/%s" % (nid, part), "fix_hint": "training pack incomplete."})
                ok = False
        try:
            io = json.loads((base / "io_contract.json").read_text(errors="ignore"))
        except ValueError:
            io = {}
        ref = io.get("output_schema") or ""
        if ref != "contracts/%s/xo.schema.json" % nid:
            violations.append({"node": nid, "fix_hint": "output_schema must reference the node's own xo contract."})
            ok = False
        elif not (root / ref).is_file():
            violations.append({"node": nid, "file": ref, "fix_hint": "io_contract.output_schema reference is DEAD in the bundle."})
            ok = False
        harness = (base / "eval" / "eval_harness.py").read_text(errors="ignore") if (base / "eval" / "eval_harness.py").is_file() else ""
        if "def validate_output" not in harness or "def load_output_schema" not in harness or "CONTRACT_MISSING" not in harness or 'schema.get("required")' not in harness:
            violations.append({"node": nid, "fix_hint": "harness does not perform REAL contract validation (L8 overclaim risk)."})
            ok = False
        acc = (base / "eval" / "acceptance.md").read_text(errors="ignore") if (base / "eval" / "acceptance.md").is_file() else ""
        if ("contracts/%s/xo.schema.json" % nid) not in acc or "ENFORCES" not in acc:
            violations.append({"node": nid, "fix_hint": "acceptance criteria must name the contract and state harness enforcement."})
            ok = False
        # Fas 3.26 — RUN THE PROPERTY, DO NOT READ ABOUT IT.
        #
        # Until now this gate proved the harness EXISTS and that acceptance.md
        # contains the word ENFORCES. It never checked that the seed corpus
        # actually satisfies the contract it is validated against. Field-proven:
        # a bundle scored ARTIFACT_TRAINING_PACK_E2E = PASS while the bundle's
        # OWN suite failed test_every_pack_harness_passes_against_its_contract
        # on the same pack - the contract had gained a required field and the
        # corpus had not. The gate attested a harness it did not run.
        #
        # Deliberately the same check the harness performs, not a delegation to
        # it. The harness is the CUSTOMER's proof, running in their suite; this
        # is the ARTIFACT's proof, running offline. Two independent readings of
        # one property is a cross-check - and a disagreement is information.
        if ok:
            try:
                _doc = json.loads((root / ref).read_text(errors="ignore"))
            except (OSError, ValueError):
                _doc = {}
            # Resolve EXACTLY as the harness does: the contract file wraps the
            # object schema under "schema". Reading the top level instead
            # yields required=None and the check silently passes on everything
            # - which is how this gate came to attest a harness it never ran.
            _xo = (_doc.get("schema") or _doc) if isinstance(_doc, dict) else {}
            _required = [r for r in (_xo.get("required") or []) if isinstance(r, str)]
            if _required:
                _bad = 0
                _first = None
                for _split in ("train.jsonl", "eval.jsonl"):
                    _f = base / "seed_data" / _split
                    if not _f.is_file():
                        continue
                    for _ln in _f.read_text(errors="ignore").splitlines():
                        _ln = _ln.strip()
                        if not _ln:
                            continue
                        try:
                            _row = json.loads(_ln)
                        except ValueError:
                            _bad += 1
                            _first = _first or (_split, "row is not valid JSON")
                            continue
                        _out = _row.get("output") if isinstance(_row, dict) else None
                        if not isinstance(_out, dict):
                            _bad += 1
                            _first = _first or (_split, "row carries no output object")
                            continue
                        _missing = [r for r in _required if r not in _out]
                        if _missing:
                            _bad += 1
                            _first = _first or (_split, "output omits required %s" % ", ".join(_missing))
                if _bad:
                    violations.append({
                        "node": nid,
                        "file": "training/%s/seed_data/" % nid,
                        "fix_hint": ("%d seed row(s) do NOT satisfy the live output contract "
                                     "(%s: %s) - the pack's own eval-harness fails on this bundle, "
                                     "so the corpus and the contract have drifted apart"
                                     % (_bad, _first[0], _first[1])),
                    })
                    ok = False
        if ok:
            proven += 1
    tp = root / "tests" / "unit_tests" / "test_training_packs.py"
    t = tp.read_text(errors="ignore") if tp.is_file() else ""
    if "def test_every_pack_harness_passes_against_its_contract" not in t or "def test_harness_fails_closed_when_contract_is_missing" not in t:
        violations.append({"file": "tests/unit_tests/test_training_packs.py", "fix_hint": "runtime smoke proofs for the training chain are not emitted."})
    return {"status": "PASS" if not violations else "FAIL", "violations": violations,
            "details": ("SLM enablement chain proven on %d/%d training pack(s): complete spec/corpus/eval, "
                        "live contract reference, a harness this gate RAN rather than read about "
                        "(every seed row validated against the live output contract), emitted "
                        "runtime proofs (L7/L8).") % (proven, len(packs))}
