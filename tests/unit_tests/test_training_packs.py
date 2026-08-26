"""Training packs — the eval-harness chain is proven, not assumed.

Fas 2.12a: training/<node>/ ships a runnable eval-harness whose acceptance
prose claims contract validation. This test RUNS every pack's harness:
io_contract.json's output_schema reference must resolve, the synthetic seed
corpus must pass the harness's REAL contract validation (required fields +
declared top-level types), and a missing contract must fail closed.
"""
import glob
import json
import os
import subprocess
import sys

import pytest


def _packs():
    return sorted(p for p in glob.glob("training/*/") if os.path.isfile(os.path.join(p, "eval", "eval_harness.py")))


# Fas 3.48 — a pack-less agent (pure aggregator/coordinator with no model-bound
# cognitive nodes, e.g. MacroHub) legitimately emits ZERO training packs; the
# CEVE engine marks ARTIFACT_TRAINING_PACK_E2E as N_A there. These tests must
# mirror that: skip (not fail) when there is nothing to prove — otherwise the
# bundle's own suite goes red on an agent that is perfectly conformant.
_NO_PACKS_SKIP = "no model-bound nodes -> no training packs (ARTIFACT_TRAINING_PACK_E2E is N_A for this agent)"


def test_every_pack_harness_passes_against_its_contract():
    packs = _packs()
    if not packs:
        pytest.skip(_NO_PACKS_SKIP)
    for pack in packs:
        harness = os.path.join(pack, "eval", "eval_harness.py")
        r = subprocess.run([sys.executable, harness], capture_output=True, text=True)
        assert r.returncode == 0, (pack, r.stdout[-500:], r.stderr[-300:])
        with open(os.path.join(pack, "eval", "slm_eval.json")) as f:
            rep = json.load(f)
        assert rep["status"] == "CORPUS_OK", (pack, rep)
        assert rep["schema_valid_pct"] == 1.0, (pack, rep)
        assert rep["contract"].startswith("contracts/"), rep
        assert os.path.isfile(rep["contract"]), (pack, "output_schema reference must resolve", rep["contract"])


def test_harness_fails_closed_when_contract_is_missing(tmp_path):
    """Point a pack copy's io_contract at a nonexistent path: the harness must
    exit non-zero with CONTRACT_MISSING — never a silent pass (L7)."""
    import shutil

    packs = _packs()
    if not packs:
        pytest.skip(_NO_PACKS_SKIP)
    src = packs[0]
    dst = tmp_path / "pack"
    shutil.copytree(src, dst)
    io_path = dst / "io_contract.json"
    io = json.loads(io_path.read_text())
    io["output_schema"] = "contracts/__does_not_exist__/xo.schema.json"
    io_path.write_text(json.dumps(io))
    r = subprocess.run([sys.executable, str(dst / "eval" / "eval_harness.py")], capture_output=True, text=True)
    assert r.returncode != 0, r.stdout[-400:]
    rep = json.loads((dst / "eval" / "slm_eval.json").read_text())
    assert rep["status"] == "CONTRACT_MISSING", rep
