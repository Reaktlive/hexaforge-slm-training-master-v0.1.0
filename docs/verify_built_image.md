# Verify the built image against this signed bundle (Fas 2.20)

The factory signs the SOURCE bundle (every delivered file hash-bound in
`MANIFEST.json`, Ed25519-signed in `identity.json`). The container image is
built later, in YOUR CI, by `.github/workflows/build-image.yml` — so the image
itself cannot be pre-signed by the factory. Instead the emitted build chain
binds the image to this bundle at build time, and this document is the
re-verification procedure. The full chain:

    signed source bundle -> digest-pinned base image -> hash-locked dependencies
      -> built container -> Sigstore-attested image digest

## 1. The image points back to this bundle (identity labels)

`build-image.yml` resolves these OCI labels from the bundle's own SIGNED files
at build time and bakes them into the image:

| Label | Source |
|---|---|
| `org.hexabox.agent-id` | `identity.json .agent_id` |
| `org.hexabox.identity-sha256` | `sha256sum identity.json` (covers the Ed25519 signature) |
| `org.hexabox.manifest-sha256` | `MANIFEST.json .manifest_sha256` (hash-binds every delivered file) |
| `org.hexabox.karta-sha256` | `PROVENANCE.json .karta_sha256` |

Verify a pulled image against your local bundle checkout:

```bash
docker inspect --format '{{ json .Config.Labels }}' <image> | jq .
# compare, from the bundle root:
jq -r .manifest_sha256 MANIFEST.json          # == org.hexabox.manifest-sha256
sha256sum identity.json                        # == org.hexabox.identity-sha256
jq -r .agent_id identity.json                  # == org.hexabox.agent-id
jq -r .karta_sha256 PROVENANCE.json            # == org.hexabox.karta-sha256
```

A label mismatch means the image was NOT built from this signed bundle. Run
`python3 verify_identity.py .` first to prove the local checkout itself is
genuine — then the label comparison extends that trust to the image.

## 2. The digest is Sigstore-attested (build provenance)

On every non-PR build the workflow runs `actions/attest-build-provenance`
(SHA-pinned): GitHub's OIDC identity signs a SLSA provenance statement binding
the pushed image digest to the exact repository, commit and workflow run, and
pushes the attestation to the registry alongside the image. Verify:

```bash
gh attestation verify oci://ghcr.io/<owner>/<repo>@<digest> --repo <owner>/<repo>
```

The run summary of each build publishes the binding record (image digest +
agent id + identity/manifest/karta sha256) for human audit.

## 3. Honesty boundary

The factory ships and GATES this mechanism (`ARTIFACT_IMAGE_PROVENANCE_BOUND`:
labels resolved from signed files, pinned attestation step, permissions, this
document). The attestation itself is produced in YOUR CI at build time — the
factory never invents an image digest at generation time. Until you have run a
build, no image (and no attestation) exists yet.
