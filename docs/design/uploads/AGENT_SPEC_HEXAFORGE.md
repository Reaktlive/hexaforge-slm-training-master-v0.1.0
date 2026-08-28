# Fabriksunderlag — HexaForge (SLM Training Master)

**Arbetsnamn:** HexaForge · byt fritt. Fristående agent — INTE en del av Eihwaz-flottan.
**Syfte med dokumentet:** allt Studio-wizarden behöver för att generera agenten. Skapas i
fabriken (Forseti), hand-editeras aldrig. UI:t byggs separat av Claude Design
(se `CLAUDE_DESIGN_BRIEF_HEXAFORGE_UI.md`).

## Studio-inputs

| Fält | Värde |
|---|---|
| **name** | HexaForge — SLM Training Master |
| **vertical** | ai-infrastructure (ny) alt. meta-platform |
| **purpose** | Autonomously operate an SLM adapter training campaign on local NVIDIA GPU hardware: schedule and supervise per-node LoRA training jobs, monitor GPU telemetry, drive quantization and the contract eval gate, and stop at a tiered authorization gate for every consequential action — model promotion/binding is always a human-approved, signed decision. Guided operation: a non-expert can run the machine; every field explained, every failure diagnosed with a proposed (tiered) remedy. |
| **desired_output** | A hash-chained training record per adapter (base model, seed data hash, hyperparameters, eval score vs threshold, quantization, approver) — the model's verifiable birth certificate — plus campaign status and bind manifests. |

## architecture_answers

- **k_floor:** n/a (ingen kunddata i v1 — single-tenant, lokala artefakter). Sätt 1/off.
- **vertical_derivation:** MLOps/training-domänen behandlas som styrd infrastrukturdrift:
  jobb är händelser, promotering är en privilegierad handling, proveniens är audit.
- **policy_implications:** modellvikter/träningsdata lämnar aldrig maskinen; inga externa
  anrop utom (valfritt) bas-modellhämtning med digest-verifiering; eval-grinden är
  fail-closed — obunden adapter är default.

## Topologi — kognitiva noder (kompetenser)

| Nod | Roll |
|---|---|
| `campaign_planner` | discovery av träningspaket → jobbplan (prioritet, GPU-passning, ordning) |
| `job_supervisor` | följer körande jobb: framsteg, loss-kurva, hängning, OOM |
| `gpu_telemetry_normalizer` | DCGM/nvidia-smi-metrics → kanonisk jobbhälsa |
| `failure_diagnoser` | fel → orsaksklass + föreslagen åtgärd (retry/sänk batch/parkera) |
| `eval_gatekeeper` | kör paketets eval-harness, jämför mot tröskel — fail-closed |
| `provenance_recorder` | födelseattesten: bas+digest, seed-hash, hyperparametrar, poäng |
| `bind_proposer` | föreslår promotering av godkänd adapter (aldrig auto) |
| `explainer` | klarspråksförklaringar till operatören (fältet `?`, "varför föll jobb 47?") |

## Privilegierade actions (deklareras i kartan, CCAS-tier per action)

| Action | Tier | Reversibel |
|---|---|---|
| `start_training_job` | T1 (inom godkänd kampanjplan) | ja (kill) |
| `requeue_job` / `retry_with_adjustment` | T2 | ja |
| `kill_job` | T2 | ja (requeue) |
| `pause_campaign` / `resume_campaign` | T2 | ja |
| `promote_and_bind_adapter` | **T3 — människa** | ja (rollback) |
| `rollback_binding` | T3 | ja |
| `delete_artifact` | **T4 — dual** | **nej** |

## Ingress / egress

- **Ingress-kinds:** `training_pack_discovered`, `job_progress`, `job_failed`, `gpu_anomaly`,
  `eval_completed` — från körmiljöns harness/telemetri. I v1 matas agenten med
  **dry-run-data** (`slm_build/run_report_*.json`-formen är redan definierad).
- **Egress:** kampanjstatus, godkännande-kort (bind-förslag med bevis), födelseattester.
  Inga externa mottagare.

## CUSTOMER_SLOT / ärlighet

Exekverings-handlarna (faktiskt starta/döda GPU-jobb) är **medvetna slots** i v1 — agenten
genereras och drivs mot dry-run-läget tills bindning sker i körmiljön. UI:t och
godkännande-flödet är fullt körbara mot dry-run. Märks `reference mode` precis som
flottans agenter.

## Uttryckligen UTANFÖR scope (v1)

Ingen koppling till 7secsl03/GPU-servern · ingen SaaS/kontrollplans-arkitektur · ingen
Eihwaz-integration · inga andra leverantörsconnectors. En agent, ett UI.
