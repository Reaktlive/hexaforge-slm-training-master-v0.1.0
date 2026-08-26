# SLM Enablement Pack

For every model-bound node, Forseti emits the spec, the seed corpus, and the
eval needed to **produce** and **prove** that node's specialist SLM. The
intelligence and your real data stay yours — this is the scaffold and the proof,
never a fabricated model.

Per node (`training/<node_id>/`):
- `model_card.md` — what the SLM must do, derived from the node's own contract.
- `io_contract.json` — input/output schema references + gate rule.
- `seed_data/` — contract-shaped **synthetic bootstrap** (train/eval). Replace/enrich with real, domain-labelled data.
- `eval/` — the contract eval-harness (the hard gate) + acceptance thresholds.

`shelf.lock.json` is HexaLearn's promoted base/recipe memory (dynamic, by
competence_signature — not a static map). The recommended base is resolved from
it, never hardcoded per vertical. Every entry states its own integrity:
`measured` (`sha256` is the real, verified digest) or `unpinned`
(`sha256` is `null` — a candidate, NOT a lock). A placeholder digest is
never shipped; an absent measurement is stated as `null` and the fetch step
must record + verify the digest before training (red-team A8).

**Honest boundary:** synthetic seed bootstraps; production quality needs real
data + a passing eval. The eval-harness is the truth.
