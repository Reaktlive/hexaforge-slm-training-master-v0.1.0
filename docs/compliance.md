# Compliance — what this skeleton gives you, and what you must complete

> **This agent is a skeleton.** Its **governance plane** is enforced *by construction* and
> re-verifiable offline. Its **domain plane** is an honest stub — the real work is completed
> in your environment. This document is the map: what you already have, and the exact steps
> to meet the regulatory requirements before you make any compliance claim.
>
> Nothing here says "certified" or "compliant". Certification is an accredited third-party
> audit; this skeleton makes the evidence **audit-ready**, it does not certify.

*Generated from `compliance_map.json` — scope: **ai-ml-ops**. Capability truth: **23/45 nodes implemented**, 18 stubs.*

---

## 1 · Enforced by construction — you already have this

Every agent this factory emits ships the same governance plane, and it fails closed:

| Control | Mechanism (in this bundle) | Re-verifiable offline |
|---|---|---|
| Privileged-action authority | CCAS tier ladder `T1 auto · T2 confirm · T3 human · T4 dual-approval` — every declared action gated by `ccas_decide`; T3/T4 park until a provenance-verified (signed, action-bound, role-scoped, unexpired, not-yet-consumed) approval; releasing approvals are consumed in a persistent anti-replay ledger (`ccas_approvals.jsonl`) BEFORE release; fail-closed until the approval backend (`CCAS_APPROVAL_KEY`) is bound | ✓ |
| No undeclared action | `H_PRIVILEGED_ACTION_DECLARED` — an action-emitting node cannot exist without a declared, gated tier | ✓ |
| Immutable audit call | `HexaRecord` logging present on every port (`H7`) | ✓ |
| Signed identity + provenance | Ed25519-signed identity + tamper-evident provenance + signed file manifest (every delivered file hash-bound); `verify_identity.py` re-checks offline before any code runs | ✓ |
| Supply chain | GitHub Actions commit-pinned (40-hex SHA) + Dependabot; the transitive hash-locked requirements + CycloneDX SBOM are **measured by the factory and born in this bundle, SIGNED** in the manifest (measured before export); base image digest-pinned + born-in SIGNED (MEASURED_AND_LOCKED) or tag-based pending the factory-CI digest measurement (MEASUREMENT_READY) — never invented | ✓ |
| Built-image provenance | the emitted build chain bakes the signed bundle identity into the image as labels (resolved from the SIGNED files at build time) and Sigstore-attests the pushed digest; re-verify per `docs/verify_built_image.md`. Tamper-evident, NOT externally anchored — `ARTIFACT_IMAGE_PROVENANCE_BOUND` is **N/A** until an external trust anchor is configured (root fingerprint out-of-band) | ⚠ N/A |
| Data minimisation shape | k-anonymity contract on every MO port (`H_COHORT_ANONYMITY`, k ≥ derived floor) | ✓ |
| Component isolation | port independence + MacroHub isolation | ✓ |

**This maps to the cross-cutting standards** shown in the governance strip: AIUC-1, EU AI Act, ISO/IEC 42001, ISO/IEC 27001, Zero Trust (NIST 800-207), GDPR. See `compliance_map.json` for the per-control evidence pointers.

---

## 2 · What you must complete to meet the regulatory requirements

The gate is **structural** (the skeleton is internally consistent). Meeting the actual
regulatory requirements needs the domain substance below. Nothing downstream should claim
compliance until these are done.

### Cross-cutting (every deployment)

1. **Domain logic** — replace each `src/nodes/*/handler.py` stub with your real model/business logic. The port `schemas.json` already validate I/O; your logic must be correct *within* them. → the domain correctness every standard presumes.
2. **Anonymisation** — implement `src/shared/anonymization.py` to your real k-anon / pseudonymisation policy (the contract shape and k-floor are enforced; the *implementation* is yours). → GDPR minimisation substance (never "GDPR compliant" until your DPO signs the lawful basis).
3. **Durable audit store** — wire `HexaRecord` to a durable, access-controlled, retention-bounded store (the audit *call* is gated; the *store* is a deployment concern). → Accountability / audit-trail retention.
4. **CCAS tiers = your risk policy** — set each action's tier from *your* ground-truth reversibility and blast radius, not the decomposer's default. An irreversible, high-consequence action must be T3/T4. → Safety escalation is only as true as the tier you assign.
5. **Fail-closed governance config** — supply the audit backend, egress config, model allowlist and tier map the runtime refuses to start without. → no fail-open path to production.
6. **Accredited adversarial testing** — run the security / safety / reliability adversarial test suite through an accredited assessor, and keep the **quarterly re-test** cadence. → this, not the skeleton, is what an AIUC-1 **certificate** requires.
7. **Risk classification** — classify the deployed system's risk tier (EU AI Act) and record the human-oversight measures. → provider obligation; the skeleton operationalises Art 14, it does not classify your system.

### Domain-specific — ai-ml-ops

*These rows are generated from the agent's declared policy implications + vertical(s). Each names what triggered it, so a cross-vertical agent shows every domain's obligations.*

- **GDPR Ch. V** — international transfer  *(triggered by: cross border transfer)* — select the transfer mechanism (SCC / adequacy) and complete the transfer-impact assessment. → the agent records the transfer event; the mechanism and TIA are yours.
- **Schrems II** — SCC / transfer-impact assessment  *(triggered by: cross border transfer)* — complete the transfer-impact assessment and any supplementary measures behind the SCCs. → documentation obligation; the skeleton records the transfer, it does not assess it.
- **PCI-DSS** — cardholder data  *(triggered by: pci dss handling)* — scope the cardholder-data environment; do not persist PAN in a node unless the deployment requires it, and wire the anonymisation extension point. → the k-anon shape is enforced; CDE scoping and QSA validation are yours.

---

## 3 · What "done" means

When every completion item above is met **and** an accredited assessor has run the adversarial
tests, you hold audit-ready evidence for the standards in the strip — and only then may you make
the corresponding certified claims. Until then the honest statement is exactly the one the panel
shows: *"maps to / audit-ready evidence for"*, never *"certified"* or *"compliant"*.

The score `100/100` on the doctrine gates means the **structure** holds. It is not, and never
claims to be, a statement about domain correctness or regulatory certification.
