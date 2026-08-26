# Claims and their evidence — HexaForge SLM Training Master

Every claim this artifact makes, what proves it, and the command that reproduces
the proof **on this bundle**. Generated from the same measured values as the badges
and `capability_truth.json`, so it cannot drift from the artifact it describes.

_Doctrine 11/11 re-verified · 22 artifact gates PASS (2 N/A) · 3 build-integrity checks · 274 port contracts · generated 2026-08-26T18:11:09.495Z_

## Proven here

| Claim | What proves it | Reproduce it |
|---|---|---|
| Every port carries a typed contract | 274/274 port contracts authored; ARTIFACT_CONTRACT_COMPLETENESS measures the declared form | `cd validator && ./run_validation.sh` |
| Declared contracts are ENFORCED at runtime, not just declared | ARTIFACT_STRICT_CONTRACT_E2E: static wiring PLUS an emitted runtime proof that a violation RAISES; strict mode is the DEFAULT (opt-out DOER_STRICT_CONTRACTS=0) | `python -m pytest tests/unit_tests/test_ceve_runtime.py -q` |
| A privileged action cannot execute above its declared tier | CCAS tier ladder gated per action; 11/11 doctrine gates re-verified offline | `python -m pytest tests/unit_tests/test_ccas_approval_provenance.py -q` |
| An approval is bound to the action CONTENT, its TENANT, and is single-use | canonical_action_ref hashes selected_action/target/params/policy/tenant_id/tier/idempotency_key; the approval ledger consumes it atomically under flock | `python -m pytest tests/unit_tests/test_ccas_approval_provenance.py -q` |
| A replayed action does not execute twice | execution ledger reserves (tenant_id, action, idempotency_key) BEFORE the side effect; a duplicate returns the prior outcome | `python -m pytest tests/unit_tests/test_ccas_approval_provenance.py -q  # + see src/shared/execution_ledger.py` |
| Every delivered file is integrity-bound to a signed identity | MANIFEST.json hashes every file; its canonical hash is Ed25519-signed inside identity.json; the verifier re-checks BEFORE any bundle code runs | `python verify_identity.py .` |
| The built image CARRIES this signed bundle’s identity — tamper-evident, external anchoring is a deployment condition | the emitted build chain bakes the SIGNED files’ hashes into OCI labels and Sigstore-attests the pushed digest; it runs verify_identity in the same job before the build. Honest limit: that verifier and MANIFEST.json live in the same mutable checkout, so the binding is tamper-EVIDENT, not externally anchored. ARTIFACT_IMAGE_PROVENANCE_BOUND is N/A until an external trust anchor is configured (root fingerprint out-of-band) | `see docs/verify_built_image.md and docs/verify_root_fingerprint.md` |
| The SLM enablement chain ships complete for every model-bindable node | ARTIFACT_TRAINING_PACK_E2E: each pack carries a contract-derived model card, IO contract, seed corpus, a truly-enforcing eval harness and a recipe | `ls training/ && python -m pytest tests/unit_tests/test_training_packs.py -q` |
| The whole suite passes with strict contracts on | the emitted behavioural suite runs with strict enforcement as the default | `python -m pytest tests/ -q` |

## Explicitly NOT proven (the honest boundary)

| Limit | Why it is stated this way |
|---|---|
| Domain competence is NOT implemented | 18 of 45 nodes are CUSTOMER_SLOT stubs and 0 nodes are AI-bound; the pipeline fail-closes (disposition hold) at the first blocking stub |
| Single-use and idempotency are SINGLE-HOST grade | both ledgers serialise on an advisory fcntl.flock, which is per host — multi-replica exactly-once needs a shared compare-and-set store, stated in the modules themselves |
| The audit chain is tamper-EVIDENT, not tamper-proof | a local hash chain detects modification of an existing chain; an attacker with file control can rewrite it wholesale — external anchoring/WORM is a deployment binding, not a property of this artifact |
| identity.json is bound by CANONICAL SEMANTIC integrity | the signature covers the canonical JSON of its fields, so reformatting verifies while any change of MEANING fails; manifested files are byte-bound (size + sha256) |
| No trained model is delivered here | 0 nodes are AI-bound; the seed corpora are SYNTHETIC bootstraps (label_provenance.json says so) and binding is gated by each pack's eval acceptance thresholds — the chain ships, the trained weights do not |
| Nothing here is a certification | the gates prove structure against a named doctrine version; regulatory certification is an accredited third-party audit — see docs/compliance.md |

## Independent verification

Run the whole set without trusting this bundle's own validator:

```bash
python verify_identity.py .          # signature + full manifest sweep
python -m pytest tests/ -q           # behavioural suite (strict by default)
cd validator && ./run_validation.sh  # offline doctrine + artifact gates
bash verify_release.sh               # all three, with the honest boundary printed
```

The adversarial harness that attacks these claims lives with the factory
(`tools/redteam/redteam.py`) and runs against this unzipped bundle. Anchor the
trust chain out-of-band: obtain the HexaBox root fingerprint through a channel
other than this bundle (see `docs/verify_root_fingerprint.md`).

## Governed capabilities — and where each one came from

The brief named privileged actions explicitly, so anything marked *factory-derived* below was added by the factory beyond what was asked for. That is reported, not forbidden — but it is exactly the kind of thing a reviewer must be able to see.

| Action | CCAS tier | Origin |
|---|---|---|
| `start_training_job` | auto | requested in the brief |
| `requeue_job` | manual | requested in the brief |
| `retry_with_adjustment` | manual | requested in the brief |
| `kill_job` | manual | requested in the brief |
| `pause_campaign` | manual | requested in the brief |
| `resume_campaign` | manual | requested in the brief |
| `park_job` | manual | requested in the brief |
| `keep_parked` | manual | requested in the brief |
| `remove_flagged_rows_and_recheck` | manual | requested in the brief |
| `promote_and_bind_adapter` | human | requested in the brief |
| `deny_bind` | human | requested in the brief |
| `rollback_binding` | human | requested in the brief |
| `delete_artifact` | dual_approval | requested in the brief |
| `trigger_retrain` | manual | requested in the brief |
| `bind_adapter_to_fleet_agent` | human | requested in the brief |
| `rollback_fleet_binding` | human | requested in the brief |
| `grant_shared_adapter_training` | dual_approval | requested in the brief |
| `issue_delegation_grant` | dual_approval | **factory-derived** |
| `revoke_delegation_grant` | manual | **factory-derived** |

2 capability(ies) here were not named in the brief. Each is still fully gated at its declared tier and its executor seam is unwired until a customer binds it — but nobody asked for it, and that is the reviewer's call to make, not the factory's.
