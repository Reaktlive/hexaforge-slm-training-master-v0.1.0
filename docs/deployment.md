# Deployment

## Docker Compose
```bash
cp .env.example .env
docker compose -f deploy/docker-compose.yml up --build
```

Readiness is `/readyz` (proves the state dir is writable), liveness is
`/healthz`. Compose waits for `/readyz` before reporting the stack healthy.

Note: this is Compose v2 syntax (`docker compose`, no hyphen). The v1
`docker-compose` binary reached end of life in June 2023 and is not present in
current Docker installations.

## Kubernetes

**The image reference is a placeholder and MUST be replaced before this
applies successfully.** `deploy/k8s/deployment.yaml` ships:

```yaml
image: ghcr.io/OWNER/REPO:0.1.0
```

`OWNER/REPO` is not resolvable — the emitted build workflow
(`.github/workflows/build-image.yml`) publishes to your own registry, and the
manifest cannot know that path at generation time. Substitute the image you
actually pushed:

```bash
# 1. Point the deployment at your image
sed -i.bak "s|ghcr.io/OWNER/REPO:0.1.0|<your-registry>/<your-image>:<tag>|" \
  deploy/k8s/deployment.yaml

# 2. Apply
kubectl apply -f deploy/k8s/

# 3. Wait for readiness (the probe hits /readyz, so this only goes green when
#    the state volume is actually writable)
kubectl rollout status deploy/<agent-name>
```

The ConfigMap binds every state path (`HEXA_RECORD_PATH`,
`HEXA_SOURCE_PATH`, `CCAS_LEDGER_PATH`, `EXECUTION_LEDGER_PATH`) to
`/app/state`, so the audit chain, the approvals ledger and the execution
ledger all land on the mounted volume rather than the root-owned WORKDIR.
