#!/usr/bin/env bash
# HexaBox — full receiver re-verification in ONE command (Fas 1.4).
#
#   bash verify_release.sh
#
# Runs, in order:
#   1/3 verify_identity.py  — Ed25519 signature, root chain, and report
#                             cross-pinning (doctrine/artifact/build/release
#                             dimensions are SIGNED; a tampered report fails).
#   2/3 validator/engine.py — offline doctrine + artifact conformance
#                             (identical gate register to composition-time
#                             CEVE, derived from one source).
#   3/3 pytest tests/       — the bundle's own behavioral test suite
#                             (runtime proof; signed identity declares
#                             runtime_tests: deferred_to_bundle_ci — THIS
#                             is where that deferral is discharged).
#
# Prereqs: pip install -e .   (pytest + httpx are declared in pyproject.toml)
set -euo pipefail
cd "$(dirname "$0")"

if ! python3 -c "import pytest" 2>/dev/null; then
  echo "verify_release: pytest missing — run: pip install -e ." >&2
  exit 2
fi

# delivery_mode HANDOFF — a customer-owned, UNSIGNED, editable build. It carries
# no Ed25519 signature and no signed file manifest, so the signature/manifest
# verification (steps 0 + 1 below) is VOID by construction. Detect it up-front and
# SKIP those steps with a clear "handoff (unsigned)" note instead of hard-failing
# on the absent signature. The doctrine/artifact validator and the behavioral test
# suite still run as quality checks — but they attest nothing (the build is not
# signed). A SEALED build never carries delivery_mode == "handoff", so the strict
# signature path below is unchanged for it.
HEXABOX_DELIVERY_MODE="$(python3 - <<'PYMODE'
import json
try:
    print((json.load(open("identity.json")).get("delivery_mode") or "sealed"))
except Exception:
    print("sealed")
PYMODE
)"

if [ "$HEXABOX_DELIVERY_MODE" = "handoff" ]; then
  echo "== HANDOFF BUILD (unsigned, customer-owned, editable — NOT attested) =="
  echo "   identity.json carries no signature and no signed manifest: signature +"
  echo "   manifest verification are SKIPPED (handoff makes no attestation claim)."
  echo "   Doctrine/artifact validation and the behavioral test suite still run"
  echo "   below as quality checks, but they attest nothing on an unsigned build."
  echo ""
  echo "== 1/2 offline validator (doctrine + artifact) =="
  python3 validator/engine.py
  echo "== 2/2 behavioral test suite (pytest, strict contracts EXPLICIT) =="
  PYTHONPATH=. DOER_STRICT_CONTRACTS=1 python3 -m pytest tests/ -q
  echo ""
  echo "HANDOFF VERIFICATION COMPLETE — doctrine/artifact + runtime tests ran."
  echo "This build is UNSIGNED and NOT attested; it is customer-owned and editable."
  exit 0
fi

# Fas 3.8 - WHO VERIFIES THE VERIFIER? verify_identity.py lives inside this
# bundle and is what checks the manifest that covers verify_identity.py. Replace
# it with a single print statement and it will happily report "genuine". The
# circle can only be broken from OUTSIDE, so step 0 prints the verifier's own
# digest and the value the SIGNED manifest records for it. If those two differ,
# stop. If they agree, you still hold only the bundle's word: compare this digest
# with the one Forseti/Studio gives you through a DIFFERENT channel before you
# believe anything below it (docs/verify_root_fingerprint.md).
echo "== 0/3 verifier self-digest (compare OUT-OF-BAND before trusting the rest) =="
python3 - <<'PYVERIFIER'
import hashlib, json, sys
on_disk = hashlib.sha256(open("verify_identity.py", "rb").read()).hexdigest()
recorded = None
try:
    for entry in (json.load(open("MANIFEST.json")).get("files") or []):
        if entry.get("path") == "verify_identity.py":
            recorded = entry.get("sha256")
            break
except (OSError, ValueError):
    pass
print("   verify_identity.py sha256 (on disk): " + on_disk)
print("   verify_identity.py sha256 (signed manifest): " + str(recorded))
if recorded is not None and recorded != on_disk:
    print("::error:: the verifier on disk is NOT the one the signed manifest records - refusing")
    sys.exit(1)
PYVERIFIER

echo "== 1/3 verify_identity (signature + report cross-pin) =="
python3 verify_identity.py .

echo "== 2/3 offline validator (doctrine + artifact) =="
python3 validator/engine.py

echo "== 3/3 behavioral test suite (pytest, strict contracts EXPLICIT) =="
# Fas 2.24b — strict is the runtime default; release verification pins it
# explicitly so the gate cannot silently weaken if a future default changes.
PYTHONPATH=. DOER_STRICT_CONTRACTS=1 python3 -m pytest tests/ -q

echo "ALL VERIFICATIONS PASSED — identity, doctrine/artifact, and runtime tests."
# Fas 2.11f (L8) — the green suite's HONEST BOUNDARY, in the release overview
# itself: skipped tests are CUSTOMER_SLOT-blocked steps. Until the blocking
# capabilities are implemented, the following are NOT dynamically proven in
# this skeleton configuration (they are structurally enforced + fail-closed):
# full passage to egress on the happy path, a selected privileged action
# executing through its approval gate, and the complete business flow.
echo ""
echo "HONEST BOUNDARY: any SKIPPED tests above are CUSTOMER_SLOT-blocked steps —"
echo "full egress passage / executed privileged actions are structurally enforced"
echo "(fail-closed hold) but NOT dynamically proven until those slots are implemented."
