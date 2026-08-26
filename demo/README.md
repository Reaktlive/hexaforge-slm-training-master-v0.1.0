# Demo

Synthetic data is fed through the same Xi endpoint used in production:

```bash
docker compose -f docker-compose.demo.yml up --build
python demo_runner.py
```

ZT auth stays ON in the demo (fail-closed platform default). The compose
file provisions a LOCAL demo identity (`demo-token`, scope
`events:write`) and `demo_runner.py` sends it as a bearer token — the
demo proves the auth path, it never bypasses it. This identity is
demo config only; real deployments define their own `ZT_IDENTITIES`.
