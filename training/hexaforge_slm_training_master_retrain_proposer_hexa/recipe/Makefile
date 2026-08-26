# Forseti SLM recipe — hexaforge_slm_training_master_retrain_proposer_hexa (targets are placeholders for the customer's training stack)
ADAPTER := hexabox-hexaforge_slm_training_master_retrain_proposer_hexa-v1
BASE := meta-llama/Llama-3.2-3B-Instruct
.PHONY: fetch train quantize eval bind
fetch:
	@echo "Resolve $(BASE) via ../shelf.lock.json, download, then VERIFY its sha256 (integrity=measured) or RECORD it (integrity=unpinned) before training"
train:
	@echo "LoRA fine-tune $(BASE) on ../seed_data/train.jsonl -> $(ADAPTER)"
quantize:
	@echo "Merge + export Q4_K_M GGUF, stamp hexabox.* metadata"
eval:
	python3 ../eval/eval_harness.py
bind:
	@echo "Write SLM_ENDPOINT + MODEL_ROUTING for hexaforge_slm_training_master_retrain_proposer_hexa"
