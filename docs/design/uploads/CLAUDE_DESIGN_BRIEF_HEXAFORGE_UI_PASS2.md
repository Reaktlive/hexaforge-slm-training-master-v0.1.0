# Instruction to Claude Design — HexaForge UI, design pass 2 (binding brief)

Base: design pass 1 (**approved** — Forge Kit + V1 Campaign + V2 Guided start + V3 Approval
card). Same identity (graphite, one signal green, mono for everything measured), same rules
(honesty labels, sentence case, tier on every action, T3/T4 never auto, degraded states never
hidden, mock is dashed and says so). Pass 2 does not restyle pass 1 — it **deepens** it with
five additions. The audience to impress is a hands-on large-scale-training expert: every wow
must be a real signal rendered honestly, never decoration.

## A1 — Job detail drawer (opens from any V1 job row)
The centrepiece. A full-width drawer with:
- **The loss curve, with the agent's diagnosis drawn ON the curve**: a marker at the exact
  step where something happened, annotated in plain language — e.g. a divergence marker at
  step 1.1k: "loss went NaN here → proposed lr 2e-4 → 1e-4 (T2)". Applied remedies show as a
  second curve segment after the restart point, visually distinct.
- Sub-panels (mono, measured): tokens/s over time, step-time distribution, VRAM headroom over
  time on its GPU.
- The job's slice of the training record (pack → started → events → current), consistent with
  V3's chain rendering.
Empty/degraded: if no loss series exists, the dashed "not connected in dry-run" state — never
an invented curve shape presented as data.

## A2 — Autonomy ribbon (V1, above the stage chips)
One horizontal timeline strip for the whole campaign run: continuous segments where the agent
acted alone (T1/T2 — colour-coded, with a count: "6 h autonomous · 41 decisions"), and
**discrete human moments** (T3 binds, T4 signs) as marked points carrying the approver and
action on hover/tap. One glance says: the machine orchestrates, the human owns the moments
that count. This is the thesis as a component — treat it with kit-primitive care (it will be
reused).

## A3 — GPU packing lanes (V1, replaces or extends the telemetry card)
A Gantt-style lane per GPU (+ a CPU lane for eval): which jobs ran/run where and when,
training beside quantization, planned next sequence ghosted ahead of "now". A throughput
line: adapters/h over the campaign with the current 3.1 figure in context. Shows the
planner's brain — the difference between "a queue" and "an orchestrator".

## A4 — Efficiency panel (V1 or a small dedicated view)
The adapter economics, measured: per adapter — artifact size (e.g. 1.9 GB q4_k_m) vs base
model size, VRAM footprint, inference tokens/s; campaign total — "138 skills · 2 GPUs ·
N GB total". Plain-language one-liner per row via the `?` pattern (why small adapters
matter). No marketing copy — numbers with units, mono.

## A5 — Data quality step (V2, between data source and preflight)
When the user picks their own data: an immediate verdict card in plain language — rows,
duplicates removed, format check, **PII scan result**, and the floor rule ("312 rows — below
the 500-row floor for this pack → would be parked, not trained"). Green/amber/red states.
The non-expert's guardrail; the fail-closed posture made visible before anything runs.

## Flagged fields (render as fixtures, list in HANDOFF — do not invent endpoints)
Pass 1's flags all still stand. New in pass 2: `job.loss_series` (sampled step/loss + event
markers) · `job.tokens_per_s_series` · `job.step_time_series` · `gpu.vram_series` ·
`campaign.autonomy_segments` (spans + tiered decision points with approver) ·
`campaign.schedule_lanes` (per-GPU job spans + planned) · `campaign.throughput_series` ·
`adapter.artifact_bytes` / `adapter.base_bytes` / `adapter.inference_tokens_per_s` ·
`data_check` (rows/dupes/format/pii/floor verdict). All rendered from dry-run fixtures,
badged exactly like pass 1.

## Process
Same as pass 1: phased PRs (`feat/forge-detail-drawer`, `feat/forge-autonomy-ribbon`,
`feat/forge-lanes-efficiency`, `feat/forge-data-quality`), screenshots per PR, HANDOFF.md
updated with wired-vs-mock + the flag list above. Tweaks panel: add a `divergence` scenario
(clean run / NaN-with-remedy) for A1 and a `data` scenario (clean / below-floor / pii-hit)
for A5.
