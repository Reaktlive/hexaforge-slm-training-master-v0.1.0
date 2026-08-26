# GENESIS — birth declaration

> Every HexaBox agent is born with a verifiable identity and a build record.
> Generated from this agent's own `identity.json`, `PROVENANCE.json` and compiled
> karta — nothing here is fabricated. Verify everything in one command:
> `bash verify_release.sh` (identity + doctrine/artifact + tests), or
> `python verify_identity.py .` for the signed identity alone.

## Identity
| | |
|---|---|
| Agent | HexaForge SLM Training Master |
| Agent ID | `a1c20f68-56dc-4dda-b667-7875c42e70d2` |
| Generator ID | `—` |
| Provenance hash | `23c34de27e9c43170c029727d15fa0693b228f720c9d6cfe9cd66c94f11294f0` |
| Signature | signed · Ed25519 |
| Doctrine version | ruleset-14i-1.0.0 |
| Release | STRUCTURALLY_RELEASABLE_SKELETON · artifact 22/24 PASS (2 N_A) · build 3/3 |

_Release-verdict scope: `STRUCTURALLY_RELEASABLE_SKELETON` means every structural gate (doctrine / artifact conformance / build integrity) passed on the generated SKELETON. It is NOT a claim that the agent is domain-complete or production-releasable — the declared CUSTOMER_SLOTs must be implemented and the approval backend bound first; see Capability Truth in README.md._

## Build
| | |
|---|---|
| Born | 2026-08-26T18:11:09.495Z |
| Build ID | `d9eac7ca-9e09-48ee-803d-8f2ddaf4d156` |
| Generator | studio-1.0.0 |
| Version | 1.0.0 |
| Vertical | ai-ml-ops |
| karta_sha256 | `23c34de27e9c43170c029727d15fa0693b228f720c9d6cfe9cd66c94f11294f0` |

## Composition
| | |
|---|---|
| Nodes | 45 |
| Edges | 83 |
| Critical path | 250 ms |

## Conformance (CEVE)
| | |
|---|---|
| Doctrine gates | 11 of 11 re-verified PASS in this bundle · 11 of 19 total doctrine gates (8 enforced at composition) |
| Doctrine version | ruleset-14i-1.0.0 |
| Build purity | 86/100 |

---
_See `PROVENANCE.json` (full build provenance), `identity.json` + `generator.pub` + `root.pub` (signed identity + root chain), and `.github/workflows/doctrine-check.yml` which runs `verify_identity.py` on every push._
