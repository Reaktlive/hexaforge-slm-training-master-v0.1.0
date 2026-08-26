# Customer Extension Points

When HexaBox Studio generates an agent skeleton, it gives you a doctrine-
validated structure plus clearly-marked extension points where YOU plug in:

1. Your trained SLM/LLM (per-node handler)
2. Your domain-specific policy rules (Yi schemas)
3. Your anonymization fields (Mo schemas, k≥5)
4. Your federation/cohort configuration

The platform stays out of the way for everything else.

## 🧠 SLM enablement — what ships, and what does not

The capability strip above says **AI-BOUND 0**, and that is true: no node in this
artifact calls a model. It does NOT mean the model layer is absent — it means it
is *unbound*, and everything needed to bind it ships here.

`training/` carries one enablement pack per model-bindable node, each derived
from that node's OWN competence and IO contract (not a per-vertical template):

| File | What it is |
|---|---|
| `model_card.md` | what this node's SLM must do, derived from its own XI/XO contract |
| `io_contract.json` | the input/output schemas the model must satisfy + the gate rule |
| `seed_data/` | a **synthetic** contract-shaped bootstrap (`train.jsonl`, `eval.jsonl`) with `label_provenance.json` stating exactly that |
| `eval/` | the contract eval-harness and its acceptance thresholds — the hard gate |
| `recipe/` | fine-tune config + Makefile targets (fetch → train → quantize → eval → bind) |

The recommended base model is HexaLearn-resolved by competence signature and
recorded in `training/shelf.lock.json`, where every entry states its own
integrity: `measured` (a real sha256) or `unpinned` (`null` — a candidate, not a
lock, to be pinned and verified at fetch).

**The honest boundary:** this bundle ships the enablement chain, not trained
weights. The seed corpora are synthetic bootstraps, not domain-labelled data.
Binding a model is gated by the eval-harness in `eval/` — bind only when it
passes `acceptance.md`. Nothing here claims a trained, evaluated domain model.

---

## 🔌 Customer extension points

This is your skeleton. The platform leaves these clearly marked for you
to customize without breaking doctrine:

### Code (your business logic)

| Where | What you replace | Doctrine boundary |
|-------|------------------|-------------------|
| `src/nodes/*/handler.py` | LLM/SLM model + your business logic | Inputs/outputs validated by `schemas.json` |
| `src/shared/hexa_learn.py` | Cohort/federated-learning providers (embedding + similarity) | Cross-tenant cohort doctrine |
| `src/shared/anonymization.py` | Your anonymization implementation | ARTIFACT_ANON_CONTRACT verifies output shape |

### Policy contracts (your doctrine)

| Where | What you replace | Doctrine boundary |
|-------|------------------|-------------------|
| `contracts/hexaforge_slm_training_master_intake_octa/yi.schema.json` | Policy rules (constraints.hard) | Doctrine re-verification (`H12`, `H_PORT_CONTRACT_UNIQUE`) on every PR |
| `contracts/hexaforge_slm_training_master_enrichment_hexa/yi.schema.json` | Policy rules (constraints.hard) | Doctrine re-verification (`H12`, `H_PORT_CONTRACT_UNIQUE`) on every PR |
| `contracts/hexaforge_slm_training_master_event_parser_hexa/yi.schema.json` | Policy rules (constraints.hard) | Doctrine re-verification (`H12`, `H_PORT_CONTRACT_UNIQUE`) on every PR |
| `contracts/hexaforge_slm_training_master_campaign_planner_hexa/yi.schema.json` | Policy rules (constraints.hard) | Doctrine re-verification (`H12`, `H_PORT_CONTRACT_UNIQUE`) on every PR |
| `contracts/hexaforge_slm_training_master_job_supervisor_hexa/yi.schema.json` | Policy rules (constraints.hard) | Doctrine re-verification (`H12`, `H_PORT_CONTRACT_UNIQUE`) on every PR |
| `contracts/hexaforge_slm_training_master_intake_octa/mo.schema.json` | Anonymization fields (k≥5) | ARTIFACT_ANON_CONTRACT + H_COHORT_ANONYMITY enforce canonical schema |
| `contracts/hexaforge_slm_training_master_egress_octa/mo.schema.json` | Anonymization fields (k≥5) | ARTIFACT_ANON_CONTRACT + H_COHORT_ANONYMITY enforce canonical schema |

### What's locked

Anything outside the files listed above is **doctrine-locked**. PR template
will warn you if a change crosses the boundary. If you need to modify
locked files, regenerate the skeleton via HexaBox Studio with an updated
agent spec.

---

## Working with the extension points

### 1. Replace the model in a handler

`src/nodes/<node_id>/handler.py` is a stub that calls a placeholder model.
Replace it with your actual model invocation. Keep input/output shapes
consistent with `schemas.json` in the same folder — if you drift, H4
(Schema Compatibility) will fail in CI.

### 2. Add policy rules

`contracts/<node_id>/yi.schema.json` carries your hard + soft policy
constraints. Format follows Eihwaz's pattern:

```json
{
  "port_id": "YI",
  "constraints": {
    "hard": [
      { "id": "no_pii_in_xo", "rule": "@policy.gdpr.no_pii_in_telemetry" }
    ],
    "soft": [
      { "id": "minimize_latency", "rule": "@policy.perf.p99_under(20ms)", "penalty_weight": 1.5 }
    ]
  }
}
```

Reading and applying `constraints.hard` / `constraints.soft` inside your
handler is your responsibility in this vertical — the YI contract shapes
the policy payload, and the CI doctrine re-run keeps the contract itself
consistent (`H12` schema compatibility, `H_PORT_CONTRACT_UNIQUE`).
Optional but strongly recommended.

### 3. Author anonymization

`contracts/<node_id>/mo.schema.json` must carry the anonymization
contract. THIS bundle's actual cohort-boundary contract (generated from the
shipped egress MO contract — never a hand-written example):

```json
{
  "anonymization_contract": {
    "k_minimum": 5,
    "geographic_scope": {
      "regions": [
        "EU"
      ],
      "data_residency": "eu-west",
      "cross_border_transfer": false
    },
    "retention_policy": {
      "duration_days": 90,
      "deletion_method": "logical_purge_on_write",
      "archive_required": false
    },
    "aggregated_fields": [
      "vertical",
      "event_type"
    ],
    "k_anonymized_fields": [
      "vertical",
      "event_type"
    ]
  }
}
```

ARTIFACT_ANON_CONTRACT (offline artifact check) and H_COHORT_ANONYMITY
(doctrine) enforce this on every MO port. `k_minimum` must be ≥ the doctrine
floor; this bundle ships with `k_minimum: 5` (deterministic policy floor — see karta metadata k_floor/k_floor_source).

### 4. Cohort configuration

`src/shared/hexa_learn.py` is where federated learning + cross-tenant
intelligence flow. Default is single-tenant; configure
`COHORT_FEDERATION_ENABLED=true` in `.env` to opt in.

---

## What's locked

These files are doctrine-locked. Modify them at your own risk — CI will
flag drift, and we can't guarantee the agent still validates:

- `karta.yaml` — the topology. Use Studio's "Generate New Version" to
  emit a new doctrine-valid karta from an updated spec.
- `PROVENANCE.json` — generator metadata. Regenerated each build.
- `src/nodes/*/port_*.py` — port shells. The handler.py is yours;
  the port_*.py is generated and rewritten on each build.

---

## Where the doctrine lives

Doctrine gates (ruleset-14i) — 11 re-verified offline by `validator/`:

| Gate | Layer | What it checks |
|------|-------|----------------|
| H9 | Topology | No orphan nodes (every node wired in/out) |
| H10_H11 | Topology | OctaBox bookends — exactly one ingress + one egress, single external XI |
| H12 | Topology | Schema-version compatibility across every edge |
| H13 | Topology | Barrier-sync declared on multi-source fan-in |
| H_PORT_EXISTS | Topology | Edge endpoints exist on their nodes |
| H_PORT_CONTRACT_UNIQUE | Topology | Unique node ids + (node, port) contracts |
| H_MACROHUB_ISOLATION | Topology | Macro hub isolated from the primary chain |
| H_MACROHUB_STANDALONE | Topology | Macro hub standalone, meta-platform only |
| H_COHORT_ANONYMITY | Contracts | anonymization_contract with k ≥ 5 on every MO |
| H_PRIVILEGED_ACTION_DECLARED | Code | Declared privileged actions ↔ executable ccas_decide() |

8 further doctrine gates (H1, H2, H4, H5, H6, H7, H8, H_K_FLOOR_DRIFT) are
enforced as a hard gate at composition; their count is signed in
`identity.json.conformance` (not re-verifiable offline — C26).

Artifact conformance (9 `ARTIFACT_*` checks — proves the emitted code
implements the karta; re-runnable anywhere, never scored, never `H_`):
port handlers exist · port independence · MO anonymization present ·
edge schema compat · barrier handler · macro-hub handler · HexaRecord
`log_event()` on every YO · HexaSource provenance on AI paths · CCAS
tier runtime coverage.

Each PR's CI re-runs this entire matrix. Doctrine is non-negotiable.
