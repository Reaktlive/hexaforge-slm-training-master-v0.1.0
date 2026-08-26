# Doctrine

This agent passes 11/11 hard doctrine gates with score 100/100.

## Why it matters

HexaBox Studio's job is to make agent skeletons that are **auditable** by
default. Doctrine gates are non-negotiable hard checks that run:

1. At Studio generation time (composer + bundleBuilder)
2. On every PR via CI (`.github/workflows/doctrine-check.yml`)
3. At runtime as part of CEVE validation

A FAIL on any hard gate blocks deployment. WARN is acceptable in
pre-production but must be resolved before customer handoff.

## See also

- [`customer-extensions.md`](./customer-extensions.md) — full doctrine table + extension points
- [`architecture.md`](./architecture.md) — node-by-node topology walkthrough
- [HexaBox Studio](https://hexabox.one) — the platform that generated this
