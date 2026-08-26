# SLM model card & training spec — `hexaforge_slm_training_master_retrain_proposer_hexa`

*Auto-derived from this node's own competence + IO contract by Forseti. Dynamic and intent/job-first — not a per-vertical template. The recommended base model and recipe are HexaLearn-resolved (see `../shelf.lock.json`), never hardcoded.*

| | |
|---|---|
| Node | `hexaforge_slm_training_master_retrain_proposer_hexa` |
| Competence | `retrain_proposer` |
| Role | `core` |
| Recommended base | HexaLearn-resolved by competence_signature · `meta-llama/Llama-3.2-3B-Instruct` |
| Determinism | temperature 0 (reproducible JSON) |
| Provenance to stamp | `hexabox.domain / adapter_id / adapter_version / base_model / training_data` |

## What this SLM must do

Consume the node's **input** (`contracts/hexaforge_slm_training_master_retrain_proposer_hexa/xi.schema.json`, fields: ts, payload) and emit the node's **required output** (`contracts/hexaforge_slm_training_master_retrain_proposer_hexa/xo.schema.json`, fields: ts, payload, status). It proposes only — the agent's CCAS gate decides autonomy.

## Gate behaviour

`uncertain ⇒ escalate` (analyst tier). Never propose an auto-tier action above this node's declared CCAS tier. The gate decides; the model never executes.

## How to make it, and how it is trusted

Seed corpus in `seed_data/` (contract-shaped bootstrap). A candidate model is **bind-ready only when it passes** `eval/eval_harness.py` against the output contract — that is the hard gate. Recipe and base-model fetch arrive with the recipe step.

## Honest boundary

The seed corpus is a **synthetic bootstrap** derived from the contract — not real domain data. Production quality needs real, domain-labelled / teacher-enriched data plus a passing eval. Forseti ships the scaffold and the proof, never a fabricated model.
