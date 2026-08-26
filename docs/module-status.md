# Module status

Generated from the SAME measurement as `module_truth.json` (import-scan
over every emitted runtime surface) — this table can never drift from it.
`active` = imported by the runtime; `generated_unbound` = shipped but not
wired (visible by design, never active-looking). Deployment-grade rows are
HARVESTED from constants declared in the module source itself.

| Module | Status | Runtime importers | Notes |
|--------|--------|-------------------|-------|
| `anonymization` | active | 5 |  |
| `approval_ledger` | active | 1 |  |
| `canonical_identity` | active | 2 |  |
| `ccas_gate` | active | 66 |  |
| `ceve_runtime` | active | 276 |  |
| `cohort_store` | active | 1 |  |
| `contracts` | active | 281 |  |
| `credentials` | active | 1 |  |
| `degraded` | generated_unbound | 0 | **Why unbound:** degraded-mode signalling (truth over green) is invoked by the LLM/SLM binding path — this build has 0 ai_bound nodes, so no caller is wired. **Binding:** bind a model (llm_binding / model_bootstrap path) — the cognitive nodes then raise the degraded signal instead of running silently green. |
| `ed25519_verify` | active | 2 |  |
| `egress_governance` | active | 1 |  |
| `embedding_providers` | active | 1 |  |
| `execution_ledger` | active | 19 |  |
| `fleet_core` | active | 3 |  |
| `fleet_transport` | active | 1 |  |
| `fleet_trust` | active | 3 |  |
| `hexa_learn` | active | 1 |  |
| `hexa_record` | active | 282 |  |
| `hexa_source` | active | 1 |  |
| `ingestion_policy` | active | 1 | dedup_backend: `in_memory` · deployment_grade: `local_single_process` · customer_binding_required_for: `multi_worker_or_distributed` |
| `llm_binding` | active | 2 |  |
| `model_bootstrap` | generated_unbound | 0 | **Why unbound:** binds the distilled SLM client from env; fail-closed by design — with SLM_ENDPOINT unset nothing is bound and the agent stays on the deterministic stub. **Binding:** set SLM_ENDPOINT (deployment binding) and invoke bootstrap at the entrypoint — the module then binds via llm_binding.set_slm_client. |
| `nis2_reporting` | generated_unbound | 0 | **Why unbound:** the NIS2 Art 23 filing clock is a pure regulatory layer; the incident-filing/dispatch step it clocks is a business-flow binding not composed in this skeleton. **Binding:** wire the reporting step (REPORTING_PROFILE env selects the regime; NIS2_DISPATCH_WEBHOOK for real dispatch) from the incident flow that files reports. |
| `orchestrator` | active | 2 |  |
| `reference_capability` | active | 37 |  |
| `reporting_profiles` | active | 1 |  |
| `runtime_mode` | active | 1 |  |
| `slm_client` | active | 1 |  |
| `state_paths` | active | 4 |  |
| `zt_auth` | active | 3 |  |

**Totals:** 27 active · 3 generated_unbound of 30.
