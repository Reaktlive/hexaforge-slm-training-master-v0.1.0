# HANDOFF — HexaForge UI (design pass 1)

Surfaces: `Forge Kit.dc.html` (primitives) · `V1 Campaign.dc.html` · `V2 Guided start.dc.html` · `V3 Approval card.dc.html`.
Identity: near-black graphite, one signal green for go-decisions/healthy compute, mono for measured values. No vendor names on surface (GPUs read "GPU 0 · 48 GB"; base reads "slm-2b-instruct + digest").

## Wired vs mock
Everything renders from **dry-run fixtures** (`source: mock · dry-run` badged on all three surfaces). No live endpoints in v1.

- V1: stage counts, jobs, failures/remedies, GPU telemetry — fixture data shaped to campaign status + `run_report` (discovered/valid/registered surfaces in V2 pack cards as d/v/registered). Pause + remedy clicks mutate local state only.
- V2: pack counts follow run_report shape; preflight checks are computed fixtures (batch changes re-evaluate VRAM fit). Start button does not call anything.
- V3: approve/deny/T4 sign mutate local state; chain gains the decision entry locally.

## Fields the UI wants that the spec/report shape does not define (flagged, not invented — rendered as fixtures pending endpoint)
1. `job.eta` per job and campaign-level ETA/throughput — needs agent estimate endpoint.
2. `job.loss_curve` (sparkline) — needs sampled loss series in `job_progress`.
3. GPU free-VRAM-for-preflight (`46.6 GB free`) — needs a preflight endpoint, not raw DCGM.
4. Eval subscores (faithfulness/format/refusals) — run_report defines a single score vs threshold; subscores need harness detail.
5. Approver identities + second-approver directory for T4 — needs auth/identity source.
6. `diff vs previous version` block — needs prior record lookup by adapter lineage.
7. "Last 12 h bound" stat — needs campaign history aggregation.

Degraded rule applied: anything above missing at runtime renders the dashed "not connected in dry-run" state, never a fake zero.

## Tweaks (host panel)
- V1 `scenario`: attention / steady · V2 `preflight`: all clear / vram blocker · V3 `margin`: clear pass / borderline.

---

# Pass 2 additions (all dry-run fixtures, badged)

- **A1 Job detail drawer** (V1): click any active-job row. Loss curve with the agent's diagnosis ON the curve (NaN marker at step 1,116 → lr remedy, restart segment in green); tokens/s, step-time distribution, VRAM headroom; per-job record slice matching V3's chain. Quantizing/eval rows render the honest dashed "no loss series for this stage" state.
- **A2 Autonomy ribbon** (V1, above stage chips): T1 track + T2 spans, 41 ◆ T3 binds + 1 ▲ T4 sign as hoverable points with approver + time.
- **A3 GPU packing lanes** (V1): per-GPU + CPU lanes, quantization beside training, planned blocks ghosted past the now-line, throughput strip (3.1 now · peak 3.8).
- **A4 Adapter economics** (V1, bottom): artifact vs base, VRAM at inference, tokens/s, totals + 138-projection; `?` explainer.
- **A5 Data quality step** (V2, step 4 of 5): own-data verdict card — rows, duplicates, format, PII scan, 500-row floor. PII hit blocks Continue until fixed; below-floor flows through as an amber "will park" preflight warning (fail-closed).

## New flagged fields (fixtures; endpoints do not exist yet)
`job.loss_series` (+ event markers) · `job.tokens_per_s_series` · `job.step_time_series` · `gpu.vram_series` · `campaign.autonomy_segments` (spans + tiered decision points with approver) · `campaign.schedule_lanes` (spans + planned) · `campaign.throughput_series` · `adapter.artifact_bytes` / `adapter.base_bytes` / `adapter.inference_tokens_per_s` · `data_check` (rows/dupes/format/pii/floor verdict).

## Tweaks added
- V1 `divergence`: NaN with remedy / clean run (drawer curve + table loss + record slice follow).
- V2 `data`: clean / below floor / pii hit (only affects the own-data path).

## Open questions
- Real `run_report_*.json` sample still wanted to lock field names 1:1.
- Swedish copy pass pending (English chosen for v1).
- Logo: uploaded SVG was an empty image wrapper — awaiting re-export; flat hexagon remains.
