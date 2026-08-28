# HexaForge SLM Training Master — build status

**Agent:** HexaForge SLM Training Master · vertical `ai-ml-ops` · 45 nodes / 83 edges
**Conformance (from `identity.json`):** doctrine **11/11** re-verified · artifact **22/24** PASS (2 N/A, **0 FAIL**) · build **3/3** · validator **100/100** · build-purity 86/100
**Release class:** `STRUCTURALLY_RELEASABLE_SKELETON`

> **What this repo is.** The *editable development handoff* of the agent, emitted by HexaBox Studio and developed here. It is honestly **unsigned** (`HANDOFF — not attested`). The **signed, offline-verifiable** build is the [v0.1.0 release](../../releases) — see *Verify* below.

## What is real today
Governance is real and **structural**, not a runtime wrapper: the CCAS execution gate, the six-port cell contracts, the Ed25519 identity + SHA-256 manifest, and the doctrine gates all sit in the agent as emitted. Domain competencies are typed, **fail-closed** `CUSTOMER_SLOT`s — nothing claims a capability it does not have.

## Competencies developed (merged)
| Ticket | Competency | What it adds | PR |
|---|---|---|---|
| HST-213 | `drift_detector` | Four-signal retrain policy — eval-regression, input-drift (PSI), new-governed-data, age — plus `drift_urgency_score`; seam-wired; UI contract | #10 |
| HST-216 | `delegation_registrar` | Capability grants (signed, scope- and time-bounded, revocable) + `verify_delegated_bind`; `required_issuance_tier` (broad scope self-escalates to T4) ; UI contract | #11 |

Shared domain modules: `src/shared/drift_policy.py`, `src/shared/delegation_policy.py`, `src/shared/ingestion_policy.py`.
UI contracts (agent ↔ product UI sync points): `docs/ui-contracts/drift-signal.md`, `docs/ui-contracts/delegation.md`.

## In progress / by design not done
- **Remaining domain competencies** — typed fail-closed `CUSTOMER_SLOT` stubs, filled by SLM binding.
- **SLM adapters** — training on the GPU server; not yet bound. Reference mode is **default-OFF**, posture-gated, and every reference output is marked `"reference": true` (never domain logic).
- **Customer connections** — data sources and execution binding: the integration phase.

## Design
`docs/design/` — the HexaForge UI design brief from Claude Design: the campaign view, guided start, the approval card, and the Forge Kit, plus the agent spec and UI brief under `docs/design/uploads/`.

## Verify the signed build (verify, don't believe)
This repo is the editable handoff. The signed artifact is the **v0.1.0 release**. Download it, unzip, then:
```
python3 verify_identity.py .
python3 verify_identity.py . --trusted-root b5569d76d434123dc2f42c9dc54c13fdde0540c0143d2c68bdb6e877372405d6
bash verify_release.sh          # re-runs the doctrine + artifact gates and the tests
```
Expect `genuine ✓ / doctrine 11/11 / root-chained ✓ / ANCHORED ✓`. Change **one byte** of any manifested file and re-run — it fails closed. The root fingerprint is published **out-of-band** at [`Reaktlive/hexabox-trust`](https://github.com/Reaktlive/hexabox-trust), so you compare it against a channel other than the artifact itself.
