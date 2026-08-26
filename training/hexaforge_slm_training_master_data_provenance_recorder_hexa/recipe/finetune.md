# Fine-tune recipe — `hexaforge_slm_training_master_data_provenance_recorder_hexa`

Produces the specialist SLM for this node, then proves it against the node's output contract.

1. **Fetch the base** — `make fetch` resolves `meta-llama/Llama-3.2-3B-Instruct` via `../shelf.lock.json`. If that entry is `integrity: "measured"`, verify the download against its `sha256`; if it is `"unpinned"` (sha256 null), record the digest you obtained INTO the shelf and verify it before training — never fetch-and-trust.
2. **Train** — `make train` LoRA-tunes it on `../seed_data/train.jsonl` to emit the output schema in `../io_contract.json` (temperature 0, reproducible JSON).
3. **Quantize** — `make quantize` merges and exports a `Q4_K_M` GGUF, stamping `hexabox.*` provenance.
4. **Eval (the gate)** — `make eval` runs `../eval/eval_harness.py`; bind only if it passes `../eval/acceptance.md`.
5. **Bind** — `make bind` writes `SLM_ENDPOINT` + `MODEL_ROUTING` for this node.

**Honest boundary:** the seed corpus is a synthetic bootstrap. Replace/enrich `../seed_data/` with real, domain-labelled data before training a production model. The eval-harness is the truth.
