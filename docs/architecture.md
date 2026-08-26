# Architecture

**Pattern:** OctaBox (8-port) chain with EXTERNAL MacroHub uplink

```text
[hexaforge_slm_training_master_intake_octa]  type=OctaBox  ports=XI,XO,YI,YO,ZI,ZO,MI,MO
[hexaforge_slm_training_master_enrichment_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_event_parser_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_campaign_planner_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_job_supervisor_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_failure_diagnoser_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_eval_gatekeeper_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_provenance_recorder_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_bind_proposer_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_explainer_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_data_quality_checker_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_decision_ledger_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_artifact_meter_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_data_provenance_recorder_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_drift_detector_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_retrain_proposer_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_fleet_binder_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_delegation_registrar_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_decision_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_model_freshness_validator_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_safety_validator_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_packager_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_egress_octa]  type=OctaBox  ports=XI,XO,YI,YO,ZI,ZO,MI,MO
[hexaforge_slm_training_master_learning_store_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_start_training_job_approval_gate_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_requeue_job_approval_gate_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_retry_with_adjustment_approval_gate_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_kill_job_approval_gate_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_pause_campaign_approval_gate_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_resume_campaign_approval_gate_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_park_job_approval_gate_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_keep_parked_approval_gate_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_remove_flagged_rows_and_recheck_approval_gate_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_promote_and_bind_adapter_approval_gate_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_deny_bind_approval_gate_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_rollback_binding_approval_gate_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_delete_artifact_approval_gate_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_trigger_retrain_approval_gate_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_bind_adapter_to_fleet_agent_approval_gate_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_rollback_fleet_binding_approval_gate_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_grant_shared_adapter_training_approval_gate_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_issue_delegation_grant_approval_gate_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_revoke_delegation_grant_approval_gate_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
[hexaforge_slm_training_master_action_selector_hexa]  type=HexaBox  ports=XI,XO,YI,YO,ZI,ZO
```

## Data flow

hexaforge_slm_training_master_intake_octa.XI → 4 parallel branches (below, from the compiled edge set) → barrier join at hexaforge_slm_training_master_decision_hexa, hexaforge_slm_training_master_egress_octa → egress emits the primary result.

Branch flows (derived from the compiled XO→XI edge set — approval gates and
chained steps appear DOWNSTREAM of their parents, exactly as wired):

1. hexaforge_slm_training_master_enrichment_hexa → (fans out to hexaforge_slm_training_master_artifact_meter_hexa, hexaforge_slm_training_master_bind_proposer_hexa, hexaforge_slm_training_master_campaign_planner_hexa, hexaforge_slm_training_master_data_provenance_recorder_hexa, hexaforge_slm_training_master_data_quality_checker_hexa, hexaforge_slm_training_master_decision_ledger_hexa, hexaforge_slm_training_master_delegation_registrar_hexa, hexaforge_slm_training_master_drift_detector_hexa, hexaforge_slm_training_master_eval_gatekeeper_hexa, hexaforge_slm_training_master_event_parser_hexa, hexaforge_slm_training_master_explainer_hexa, hexaforge_slm_training_master_failure_diagnoser_hexa, hexaforge_slm_training_master_fleet_binder_hexa, hexaforge_slm_training_master_gpu_telemetry_normalizer_hexa, hexaforge_slm_training_master_job_supervisor_hexa, hexaforge_slm_training_master_provenance_recorder_hexa, hexaforge_slm_training_master_retrain_proposer_hexa)
2. hexaforge_slm_training_master_model_freshness_validator_hexa → hexaforge_slm_training_master_egress_octa
3. hexaforge_slm_training_master_packager_hexa → hexaforge_slm_training_master_egress_octa
4. hexaforge_slm_training_master_safety_validator_hexa → hexaforge_slm_training_master_egress_octa

Side-feeds (non-primary ports, from the same compiled edge set):

- hexaforge_slm_training_master_egress_octa.ZO → hexaforge_slm_training_master_learning_store_hexa.ZI
- hexaforge_slm_training_master_learning_store_hexa.ZO → hexaforge_slm_training_master_intake_octa.ZI


Mo signals are anonymized per `anonymization_contract` and emitted on the MO port for an **EXTERNAL MacroHub** — the fleet-level hub is its own agent and is **not part of this bundle** (the MacroHub artifact gate is N_A here by design). The k-anonymity floor (`k_minimum`) is enforced by the MO contract at this boundary.
