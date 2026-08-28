# How HexaBox actually works — an engineer's walkthrough

*How a HexaBox agent works, traced in one real agent — the HexaForge SLM Training Master. Every claim below points to a file in the repo you can open and check. No diagrams to trust; the code is the source.*

Repo: `github.com/Reaktlive/hexaforge-slm-training-master-v0.1.0` · signed build: release `v0.1.0`

---

## The whole shape, in one paragraph

An agent is a **directed graph of nodes**. Each node is a typed unit of work reachable **only through ports** (typed HTTP endpoints). An action with real-world consequences leaves a node through its **Yo port**, and that port hands it to a deterministic **gate** (CCAS) *before* any side effect runs — approved → proceed, otherwise → held. The whole graph is compiled to one file (`karta.compiled.json`); the whole bundle is Ed25519-signed and SHA-256-manifested; and a receiver re-verifies it offline against a published root. Everything else is detail on those five things: **node · port · gate · graph · signature.**

---

## 1 · What is a node?

**Plain:** one small, self-contained worker — like a microservice, or one station on an assembly line. It does exactly one job and has a fixed set of typed doors.

**Precise:** a directory under `src/nodes/<node_id>/` containing `handler.py` (the logic), six port modules, and `schemas.json` (the typed I/O contracts). In the compiled graph, each node carries an `id`, a `type` (`HexaBox` = 6 ports; `OctaBox` = 8, adding the M-plane for cross-tenant cohort signals), a `role`, and its `ports`.

**Open:** `src/nodes/hexaforge_slm_training_master_decision_hexa/` — one node. Its files:
```
handler.py   port_xi.py  port_xo.py  port_yi.py
port_yo.py   port_zi.py  port_zo.py  schemas.json
```
And its entry in `karta.compiled.json` → `topology.nodes[]`:
```json
{ "id": "hexaforge_slm_training_master_intake_octa", "type": "OctaBox",
  "ports": ["XI","XO","YI","YO","ZI","ZO","MI","MO"], "role": "ingress" }
```

## 2 · What is a port? (the six-port cell)

**Plain:** a door on a node. Every node has exactly six — three pairs, in and out. Nothing enters or leaves except through a door, and every door has a fixed shape. No side entrances.

**Precise:** three planes × in/out — `xi/xo` (X), `yi/yo` (Y), `zi/zo` (Z). Each `port_*.py` is a FastAPI endpoint that validates its Pydantic schema before anything else runs. The Y-plane out (`port_yo.py`) is where **side effects** leave — and it is the port wired to the gate. (An OctaBox adds `MI/MO`, the M-plane, for k-anonymous cross-tenant signals.)

**Open:** `src/nodes/…decision_hexa/port_yo.py`, top line: *"side effects out (privileged actions, gated by CCAS)."*

## 3 · "The rule decides, the gate enforces" — in literal code

**Plain:** before a node does anything consequential, a separate gate checks whether it's allowed. The node cannot skip it — the check is on the way out.

**Precise:** open `port_yo.py`. The flow is exactly this — the side effect (`handle_yo`) is **unreachable** unless the gate returns approved:
```python
validated = YoSchema(**payload)              # 1. typed contract or 422
validate_contract(node_id, port="yo", ...)   # 2. CEVE contract check
decision = ccas_decide(action, tier="auto")  # 3. the GATE decides
if decision["status"] != "approved":
    return {"status": "pending", "decision": decision}   # side effect NEVER runs
return await handle_yo(...)                   # 4. only past the gate
```
This is not a wrapper you can bypass from inside the node: the *port* calls the gate, then chooses whether to call the handler at all. The model that produced the action has no vote here.

**Open:** `src/nodes/…decision_hexa/port_yo.py` and `src/nodes/…decision_hexa/handler.py`.

## 4 · Platform plumbing vs. customer logic — the AUTOGEN seam

**Plain:** the governance parts are generated identically for every agent; the domain-specific parts are written below a marker and are the only editable bits.

**Precise:** every `handler.py` has a `FORSETI-AUTOGEN-START … END` block. Content between the markers is generator-owned doctrine — the tier router, the gate call — and is **byte-identical across every vertical**; it is replaced on re-generation. Customer/domain logic lives **below** the `AUTOGEN-END` marker and survives re-generation. That is why the same gate shows up in every agent (it's generated, not hand-written per agent) and why domain competence is cleanly separable.

**Open:** the header comment in `src/nodes/…decision_hexa/handler.py`.

## 5 · The gate itself: CCAS tiers

**Plain:** every consequential action gets a risk tier; higher tiers need more authority; the decision is deterministic, not a model judgement.

**Precise:** `classify_action(action)` assigns a tier — explicit `ccas_tier` if present, else signals (`scope=fleet` → tier_3; `reversible` + `single_host` → tier_1; default tier_2, the manual gate). `ccas_decide(action, tier)` returns the posture: approved → proceed · pending → human approval · higher → multi-party. For a fleet member it additionally requires a valid, signature-verified **capability lease** at this one choke point — missing/expired/invalid **denies**. The trust posture is stamped on *every* return path on purpose, so no branch can silently release.

**Open:** `src/shared/ccas_gate.py` — `classify_action` (~L713), `ccas_decide` (~L506).

## 6 · The graph: what the agent is even allowed to do

**Plain:** the agent's whole wiring diagram is a single file — it can only do what the diagram declares.

**Precise:** `karta.compiled.json` — for this agent, **45 nodes, 83 edges**, plus the contracts, the sync model and the input model. Nodes are typed; edges are the only permitted connections; there is no code path outside the declared graph.

**Open:** `karta.compiled.json`.

## 7 · Identity, manifest, signature

**Plain:** the agent carries a tamper-proof birth certificate and a checksum of every file.

**Precise:** `identity.json` is Ed25519-signed over the entire identity (minus the signature field); the generator key that signed it is *itself* signed by an offline **root** key (`generator_pubkey_signed_by_root_b64`). `MANIFEST.json` binds every file by SHA-256. Change any byte of any listed file → the manifest check fails.

**Open:** `identity.json`, `MANIFEST.json`, `GENESIS.md`.

## 8 · Verify it yourself — offline, no trust in us

**Plain:** you can prove all of the above on your own machine, trusting nothing we say.

**Precise:** the `v0.1.0` release is the signed build.
```
python3 verify_identity.py .                     # Ed25519 sig + root chain + re-hash every file
python3 verify_identity.py . --trusted-root <fp> # anchor to our published root; a forged root FAILS
bash verify_release.sh                           # re-run the doctrine + artifact gates and the tests
```
The root fingerprint is published **out-of-band** at `github.com/Reaktlive/hexabox-trust` (`b5569d76…405d6`), so you compare it against a channel other than the agent itself. Change one byte and re-run — it fails closed.

---

## Trace one action end-to-end

A request enters the **intake OctaBox** (ingress) → flows along declared edges through the pipeline nodes → reaches the **decision node** → its **Yo port** validates the contract and calls `ccas_decide` → tier_2 returns `pending` (parked for approval, no side effect) *or* approved → `handle_yo` runs the customer-bound effect. Every hop is a typed port; the gate sits exactly on the effect boundary.

## Where to look — a 20-minute self-trace

| To see… | Open |
|---|---|
| what a node is | `src/nodes/…_decision_hexa/` |
| the six ports | the `port_*.py` files in that node |
| the gate on the path | `src/nodes/…_decision_hexa/port_yo.py` |
| the gate logic | `src/shared/ccas_gate.py` |
| the whole graph | `karta.compiled.json` |
| the signed identity | `identity.json` + `MANIFEST.json` |
| verify it end-to-end | release `v0.1.0` → `verify_identity.py` |

*This repo is the editable **handoff** (honestly unsigned — it says so). The signed, offline-verifiable artifact is the `v0.1.0` release. See `STATUS.md` for what's built vs. in progress.*
