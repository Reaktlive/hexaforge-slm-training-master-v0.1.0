# Fleet transport — the closed fleet loop (blocker B1)

**What this bundle does over the wire.** A fleet-managed member (its SIGNED
identity carries `owner.fleet_id`) refuses every privileged action until it
holds a coordinator-signed capability lease. That lease is obtained over a real
network, in the running container:

```
member (this runtime)                                  coordinator (MacroHub)
egress.handle_mo -> k-anonymous release, SIGNED with FLEET_MEMBER_KEY
   -- POST https://<coordinator>/fleet_coordinator/port-xi -->   verify_envelope
      (TLS 1.2+, PINNED CA, client certificate, bearer identity)  -> attest_conformance
                                                                  -> diff_drift -> renew
   <-- {accepted, attestation, decision, lease} ------------------ -> mint_lease (PRIVATE key)
install_lease: verified with the coordinator PUBLIC key from the SIGNED registry
  (manifest-anchored under the EXTERNAL pin), subject == THIS member, unexpired,
  right fleet + epoch, non-empty scope -> written atomically to FLEET_LEASE_PATH
ccas_decide(action) -> require_fleet_lease(capability) -> admits ONLY with it
```

Every outcome is a named, machine-readable transport record (`composite.fleet`
on the event that produced the release, `fleet_transport/v1`) and a HexaRecord
entry bound to that event (`GET /api/audit/{event_id}` shows it, `payload_sha256`
= canonical hash of the record). Below the k floor there is no release and no
transport (`cohort.release_ready: false`).

**Fail-closed, and never in the event path.** No coordinator URL, `http://`
without the explicit dev opt-out, `https://` without a pinned CA, a missing
token, an unsigned release, a coordinator rejection, a lease for another member,
a bad coordinator signature, a wrong fleet/epoch, an expired or empty-scope
lease, a timeout, a non-JSON answer — each is recorded with its reason and
installs NOTHING. A previously installed lease is left untouched unless a NEW
valid one replaces it; expiry is enforced by `require_fleet_lease` on every
action. `dispatch_release` never raises: the cohort is intelligence, not the
incident pipeline.

## Wiring (env)

Member (every specialist) — see `.env.example` for the full block:
`FLEET_MEMBER_KEY`, `FLEET_MEMBER_REGISTRY`, `FLEET_MANIFEST_PATH`,
`FLEET_MANIFEST_PUBKEY` (external pin), `FLEET_SEQ_PATH`, `FLEET_LEASE_PATH`,
`FLEET_COORDINATOR_URL`, `FLEET_COORDINATOR_TOKEN`, `FLEET_TLS_CA_FILE`,
`FLEET_TLS_CLIENT_CERT_FILE` / `FLEET_TLS_CLIENT_KEY_FILE`,
`FLEET_TRANSPORT_TIMEOUT_S`, `FLEET_TRANSPORT_ALLOW_PLAINTEXT` (dev only).

Coordinator (MacroHub) additionally: `FLEET_LEASE_SIGNING_KEY` (private,
coordinator ONLY), `FLEET_REPLAY_PATH`, `FLEET_POSTURE`, and a `ZT_IDENTITIES`
entry mapping each member's `FLEET_COORDINATOR_TOKEN` to an identity with
`events:write`.

Both sides serve TLS themselves: `TLS_CERT_FILE` + `TLS_KEY_FILE`, and
`TLS_CLIENT_CA_FILE` to REQUIRE client certificates (mutual TLS). Mount the
signed manifest, the registry, the pin and the certificates read-only (e.g.
`/fleet`); keep `/app/state/fleet/` on the durable state volume (sequence,
replay, lease).

## Hardened posture (WS-1)

* **Mandatory pin.** A fleet-managed runtime loads its member registry ONLY
  when `FLEET_MANIFEST_PATH` and the external `FLEET_MANIFEST_PUBKEY` are both
  present and the manifest signature and registry anchor verify — no pin = no
  registry, never opt-in. Standalone (non-fleet) runtimes may load a plain
  registry (reference/dev).
* **Durable replay/sequence state (B2).** A fleet-managed member refuses to sign
  without `FLEET_SEQ_PATH` (the sequence never restarts at 1); a fleet-managed
  consumer refuses every signal without durable `FLEET_REPLAY_PATH`; a
  persistence write failure refuses the signal; a corrupt state file is a hard
  error at start (never "empty"). The image defaults both paths under
  `/app/state/fleet`.
* **Cohort semantics.** The coordinator's trusted cohort is a time-windowed
  buffer (one current row per member, TTL eviction, silence evaluated on the
  clock — `sweep_fleet()` is the explicit tick); k counts DISTINCT tenants
  bound in the signed registry (`tenant_id` per member) — never agent ids; a
  member without a bound tenant is recorded but does not count toward k.
* **Signed k-policy.** The manifest's `k_policy` travels into the registry and
  is the runtime authority: floor = max(code constant, signed floor) for both the
  coordinator (`fleet_floor`) and every member cohort store (`member_floor`).
  A raised signed floor changes behaviour; an unsigned edit is refused at load.
* Tests: `pytest -q tests/unit_tests/test_fleet_hardening.py` (16 cases, every
  negative with its positive control).

## Verify it (receiver walk)

* In this bundle: `pytest -q tests/unit_tests/test_fleet_transport.py` — the
  wire and the return path against a loopback fake coordinator, every
  fail-closed branch with a positive control, plus the source guard proving the
  runtime hands the signed release to the transport instead of discarding it.
* Across containers: the fleet package ships `run_fleet_transport_e2e.py`
  (coordinator bundle + one specialist bundle → two containers on a private
  network, mTLS both ways, signed manifest under an external pin). It records
  signal → verify → attest → lease → CCAS-gated action, with replay / tamper /
  unsigned / forged-lease / removed-lease negatives, in a sha256-bound run
  record. Because a specialist SKELETON holds every event at its fail-closed
  `CUSTOMER_SLOT` stubs, that E2E enables the factory's opt-in reference
  harness on the specialist (`DOER_REFERENCE_MODE=1` + explicit
  `DOER_REFERENCE_ACK`, Zero-Trust auth ON) so the chassis reaches egress —
  disclosed in the run record; the trust plane, transport, lease and CCAS gate
  are the shipped code paths, unmodified.
