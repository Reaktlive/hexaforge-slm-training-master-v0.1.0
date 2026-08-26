# UI contract — delegated signing (HST-216 · UI B3)

Sync point between the **agent** (this repo) and the **product UI** (Claude Design,
pass-3 B3 "Delegated signing"). Domain names stay canonical in `delegation_policy`;
the binding layer renames for `/delegations` and the approval decision endpoint.

## Source of truth (domain)

`src/shared/delegation_policy.py` is canonical:

- `required_issuance_tier(scope) -> {required_tier, bare_wildcard, shared_cohort}`
  — a **bare `*`** adapter family or a **non-single-tenant cohort** forces the grant
  to be issued at **T4** (dual); otherwise **T3**.
- `verify_delegated_bind(grant, bind, now) -> {decision, reason, detail, records}`
  — `decision ∈ {delegated_ok, needs_live_senior}`; `records = [delegate, authority]`
  **always** (both names on the chain).

A grant is a conjunction (AND): `scope.adapter_family` (globs, no bare `*`),
`scope.vertical`, `scope.cohort` (`single_tenant_only`), `scope.eval_margin`
(`>= threshold + 0.05`), `validity {not_before, not_after, max_uses, max_uses_per_day,
used_total, used_today}`, `state {active|revoked|expired}`.

## Node emission (runtime)

`delegation_registrar_hexa.handle_xi` attaches the decision at
`response.payload.payload.delegation` (an extra field, forwarded by `_xo_validate`;
never part of the typed XO schema). `/delegations` serves the stored grants.

## Binding layer (presentation)

| UI (B3 card) | Domain source | Notes |
|---|---|---|
| `delegate` · `authority` (granted-by) · `sig` | `grant.delegate` · `grant.authority` · `grant.authority_signed` | both shown; the record carries both |
| `scope.adapter_family` | `grant.scope.adapter_family` | rendered as-is; a bare `*` cannot exist here (issued at T4) |
| `scope.vertical` · `scope.cohort` | `grant.scope.*` | `cohort = single_tenant_only` for a delegable grant |
| `scope.eval_margin` | `grant.scope.eval_margin` (`≥ threshold + 0.05`) | the visible boundary |
| `validity` (uses `used_total/max_uses`, `used_today/max_uses_per_day`, remaining) | `grant.validity.*` | remaining = max − used |
| `state` chip | `grant.state` | active / revoked / expired |
| **Sign button state** | `verify_delegated_bind(...).decision` | `delegated_ok` → "Sign under delegation" enabled; `needs_live_senior` → disabled + the live-senior banner |
| out-of-scope banner text | `verify_delegated_bind(...).reason` | machine reason → human sentence (table below) |

### reason → UI banner ("needs a live senior signature (T3): …")

| `reason` | UI sentence |
|---|---|
| `t4_action_never_delegable` | T4 (dual-approval) action — no delegation can pre-satisfy it |
| `first_bind_of_new_family` | first bind of a new adapter family |
| `shared_or_hexaintel_lineage` | shared / HexaIntel lineage |
| `eval_within_margin` | eval within the delegation's margin (thin) |
| `delegation_revoked` / `delegation_expired` / `delegation_exhausted_total` / `delegation_exhausted_daily` | delegation not usable (revoked / expired / used up) |
| `out_of_scope_adapter_family` / `out_of_scope_vertical` / `out_of_scope_shared_cohort` | outside this delegation's scope |

## Honesty invariants that MUST survive the boundary

1. **No grant pre-satisfies T4.** A T4 action always routes to a live senior — the gate never gets cheaper.
2. **Both names, always.** Every delegated sign records `delegate` AND `authority`; the UI shows both.
3. **Hard exclusions win over the predicate.** first-bind / shared-lineage / under-margin / T4 route to a live senior *regardless* of an otherwise-valid grant.
4. **Broad scope self-escalates.** A bare-wildcard family or a shared cohort makes the *grant issuance itself* T4 — the UI issues it as dual, never T3.

## Change protocol
- New scope dimension or exclusion → change `delegation_policy` + this table + the B3 brief together.
- Field rename → change the binding-layer row here; domain and UI names both stay stable.
