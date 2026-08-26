# Verifying the HexaBox root fingerprint (out-of-band trust anchor)

`verify_identity.py` proves this bundle's identity is Ed25519-signed by a
generator key, and that the generator key is in turn signed by the HexaBox
**root** key (`root.pub`). But `root.pub` ships *inside this bundle*, so on its
own it only proves the bundle is internally consistent — NOT that it came from
HexaBox. A tamperer who re-signed the whole bundle with their OWN root key would
also pass `verify_identity.py`.

The real trust anchor is the root key's **fingerprint**, which you must obtain
through a channel OTHER than this bundle (Forseti/Studio, a published release
note, or directly from HexaBox) and compare.

## Compute the fingerprint of the shipped root key

    python3 -c "import hashlib,pathlib; print(hashlib.sha256(pathlib.Path('root.pub').read_text().strip().encode()).hexdigest())"

This prints the sha256 of the base64 root public key exactly as shipped.

## Compare — or let the verifier enforce it

Match that value against the HexaBox root fingerprint published out-of-band. If
they differ, do NOT trust the bundle — its identity chain is anchored to an
unknown root. `verify_identity.py` passing is necessary but NOT sufficient
without this out-of-band check. The same applies to this verifier's own sha256:
obtain it out-of-band too (see README.md) so the verifier itself cannot be
swapped.

Machine-enforced compare (B9): pass the fingerprint you obtained out-of-band and
the verifier FAILS on any other root, even if the bundle's internal chain is
consistent:

    python3 verify_identity.py . --trusted-root <64-hex fingerprint from the public channel>

Without `--trusted-root` the verifier prints the shipped root's fingerprint
marked *unanchored* so you can compare it by hand. The HexaBox root fingerprint,
the standalone verifiers and the fleet/delivery pins are published on the
HexaBox trust channel (a public repository, referenced in the Technical
Reference); the root private key is generated in a witnessed ceremony and held
offline — it signs only generator public keys.
