# Acceptance — `hexaforge_slm_training_master_data_provenance_recorder_hexa` SLM

A candidate model is **bind-ready** only when, run at temperature 0 on `seed_data/eval.jsonl`:

1. **Schema-valid** — every output is validated against `contracts/hexaforge_slm_training_master_data_provenance_recorder_hexa/xo.schema.json`
   (required fields + declared top-level types; target ≥ 99%). `eval/eval_harness.py`
   ENFORCES this criterion: until a model is bound it proves the seed corpus itself
   against the contract (fail-closed — a missing contract is an error, never a pass).
2. **Label agreement** — meets the agreed threshold on the held-out eval set (set with real data).
3. **Gate behaviour** — `uncertain ⇒ escalate`; never proposes an action above the node's declared CCAS tier.
4. **Deterministic** — same input yields the same output.

Below threshold ⇒ **not** bind-ready. `eval/eval_harness.py` emits `eval/slm_eval.json`; bound models stamp `hexabox.*` provenance into HexaRecord / HexaSource.
