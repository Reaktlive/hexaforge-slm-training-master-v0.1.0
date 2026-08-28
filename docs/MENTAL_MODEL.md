# HexaBox — the mental model

How a HexaBox agent works, in plain terms. The file-by-file proof is in *How It Works*; a single action followed through the code is in *The Gate, Traced*.

---

## Five words

**Node** — one small, self-contained worker; think a microservice, or one station on an assembly line. It does exactly one job and has a fixed set of typed doors. An agent is a graph of these wired together.

**Port** — a door on a node. Six per node — three pairs, in and out. Nothing enters or leaves except through a door, and every door has a fixed shape (a schema). There are no side entrances an action can slip through.

**Gate** — before a node does anything with real-world consequences, its output door hands the action to a separate gate. The gate checks the risk tier and whether the authority is actually present, and only then lets it through. The node can't skip it — the check is on the way out. Anything short of approved is held; fail-closed is the default.

**Graph (karta)** — the agent's whole wiring diagram is a single file. It can do only what the diagram declares; there is no path that isn't drawn.

**Signature** — the agent carries a tamper-proof birth certificate and a checksum of every file. Change one byte and it fails verification — which the receiver checks themselves, offline.

---

## The questions that matter

**How is this different from just telling the model to behave?**
The model never gets to be the final authority. It *proposes*; the gate — plain deterministic code, not the model — *decides*. Prompt it however you like; if the gate's conditions aren't met, the action doesn't run. Behaviour is a request; enforcement is code.

**Isn't the gate just in-process code you could bypass if you owned the process?**
Within the process, yes — the gate is *semantic*: it decides whether a declared action is allowed. Process isolation is the OS's job — a hypervisor, gVisor, a vendor sandbox — and that is where HexaBox complements it: the gate inside, the sandbox outside. It does not claim to replace OS-level isolation.

**Is any of this real?**
You don't have to take anyone's word for it. Clone a signed agent, run the verifier offline, change one byte — it fails closed. Try to make a running agent do something off-contract and watch it refuse, then re-verify the record yourself. You verify; you don't trust the sender.

---

## Why this is the point

Governance is a property of the artifact — decided at construction, carried in the signed bundle, and re-checkable by whoever receives it. Not a runtime promise, not a prompt the model might ignore, not a wrapper taken on faith. *The model reasons; the rule decides; the gate enforces.*
