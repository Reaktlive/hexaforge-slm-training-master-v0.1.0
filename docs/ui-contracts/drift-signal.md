# UI contract — drift signals (HST-213 · UI B2)

This is the single sync point between the **agent** (this repo) and the **product UI**
(Claude Design, pass-3 B2 "Retraining proposals"). The two are separate artifacts on
separate tracks; this map is how they stay 1:1. When either side changes a field, it
changes **here first**, deliberately — never by accident.

## Source of truth (domain)

`src/shared/drift_policy.evaluate_drift(inputs) -> verdict` is canonical. Shape:

```
verdict = {
  "signals": [ { "name", "status", "urgency", "value", "threshold", "reason" }, ... ],
  "proposal": { "action": "trigger_retrain", "tier": "T2", "auto": false,
                "urgency": "high|medium|low", "reasons": [...] } | null,
  "cannot_assess": [ "<signal name>", ... ]
}
```
- `name` ∈ `eval_regression | input_drift | new_governed_data | age`
- `status` ∈ `fired | marginal | clear | cannot_assess`
- Locked thresholds live in `drift_policy` (EVAL_MARGIN 0.05, PSI 0.20, 500 rows, 90d).

## Node emission (runtime)

`drift_detector_hexa.handle_xi` attaches the verdict verbatim at:

```
response.payload.payload.drift  ==  verdict
```

The XO envelope stays contract-valid — `drift` is an extra field forwarded by
`_xo_validate`, never part of the typed XO schema.

## Binding layer (presentation) — where renames live

The semantic endpoint `GET /campaign/drift` aggregates the per-adapter verdicts into the
UI shape. **The domain keeps its names; the endpoint renames for presentation.** No domain
code is bent to a UI label.

| UI field (`/campaign/drift → signals[]`) | Domain source | Notes |
|---|---|---|
| `adapter` | the bound adapter id the verdict was computed for | added by the aggregator |
| `kind` | `signal.name` | rename only |
| `magnitude` | `signal.value` | raw measured value |
| `threshold` | `signal.threshold` | the line it was tested against |
| `status` | `signal.status` | drives the chip (`fired`/`marginal`/`clear`/`cannot_assess`) |
| `proposed_action` | `proposal.action` (`trigger_retrain`) | only present when `proposal != null` |
| `tier` | `proposal.tier` (`T2`) | renders on the button |
| `urgency` | `proposal.urgency` | chip colour |

## Honesty invariants that MUST survive the boundary

1. `proposal.auto == false` → the UI shows **"propose — never execute"**; the action is a
   button (T2), never an automatic run.
2. `status == "cannot_assess"` → the UI renders **"cannot assess — no baseline"**, never a
   fabricated "no drift" / green.
3. `proposal == null` with no `cannot_assess` → genuinely quiet; UI shows no proposal.
4. `age` never appears as a lone trigger — the domain guarantees it (fires only with a
   co-signal), so the UI never needs special-casing.

## Change protocol

- New signal or threshold → change `drift_policy` + this table + the B2 Claude Design brief, together.
- Field rename → change the binding-layer map row here; domain and UI names both stay stable.
- This file is the contract; `FACTORY_PROMPT` references it for the `/campaign/drift` surface.
