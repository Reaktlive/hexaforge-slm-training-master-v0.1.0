# HexaBox DevTracker — CI Integration

HexaBox DevTracker is the digital development-plan module shown on your
agent's Project Page in Studio. Two tabs: Roadmap (all tickets) +
CEVE-trend (line chart of validator score over time).

Without this CI integration, the CEVE-trend graph is empty — you'd have
to manually push results. With it, every PR + push to main automatically
posts the validator outcome, including a red flag when a commit drops
the score below 100/100.

## 1. Get your bearer token

The token is unique per agent and scoped to your agent_id only. Generate
one in **Studio → Project Page → Settings → Generate CI token**, or ask
the Doable team to issue one.

```
DOABLE_DEVTRACKER_TOKEN = <issued-by-doable>
# (secret name kept for backward compatibility with existing CI configs)
AGENT_ID                = a1c20f68-56dc-4dda-b667-7875c42e70d2
ENDPOINT                = https://hexabox-vault.lovable.app/functions/v1/devtracker-ceve-ingest
```

## 2. Payload format (FLAT — not wrapped)

The endpoint accepts a flat JSON payload (all fields on top-level — NOT
`{ "ceve": {...} }`):

```json
{
  "agent_id": "a1c20f68-56dc-4dda-b667-7875c42e70d2",
  "commit": "<git-sha>",
  "triggered_by": "ci",
  "score": 100,
  "verdict": "PASS",
  "gates": [
    { "id": "H9",                 "name": "No Orphan Nodes",    "status": "PASS", "violations": [] },
    { "id": "H_COHORT_ANONYMITY", "name": "Cohort k-Anonymity", "status": "PASS", "violations": [] }
  ],
  "ts": "2026-05-21T19:00:00Z"
}
```

Success response: `HTTP 200` with
`{"ok":true,"run":{"id":"<uuid>",...}}`.

## 3. GitHub Actions

Already wired in `.github/workflows/doctrine-check.yml` shipped with
this bundle. Set the repo secret:

**Settings → Secrets and variables → Actions → New repository secret**

- Name:  `DOABLE_DEVTRACKER_TOKEN`
- Value: `<your token>`

CI runs CEVE-Light on every PR + main-push, posts the report as a PR
comment, and POSTs the flat payload to DevTracker. Workflow continues
even if validator fails (`if: always()`) so red commits still show
in the CEVE-trend graph.

## 4. GitLab CI

Add the variable: **Settings → CI/CD → Variables → Add**

- Type: Variable
- Key:  `DOABLE_DEVTRACKER_TOKEN`
- Mask + Protect: true

In `.gitlab-ci.yml`:

```yaml
ceve:
  image: python:3.11-slim
  variables:
    AGENT_ID: "a1c20f68-56dc-4dda-b667-7875c42e70d2"
    ENDPOINT: "https://hexabox-vault.lovable.app/functions/v1/devtracker-ceve-ingest"
  script:
    - pip install -e .
    - python validator/engine.py
  after_script:
    - apt-get update && apt-get install -y --no-install-recommends curl jq
    - |
      PAYLOAD=$(jq --arg aid "$AGENT_ID" --arg sha "$CI_COMMIT_SHA" \
        '. + {agent_id: $aid, commit: $sha, triggered_by: "ci"}' \
        reports/ceve_validation.json)
      curl -X POST "$ENDPOINT" \
        -H "Authorization: Bearer $DOABLE_DEVTRACKER_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD" \
        --fail-with-body
```

## 5. Verification

After your first merge, you should see:

1. CI logs show `HTTP 200` + JSON `{"ok":true,"run":{"id":"<uuid>",...}}`
2. Within 30 seconds, a new datapoint appears in DevTracker's CEVE-trend
   tab at `/studio/project/a1c20f68-56dc-4dda-b667-7875c42e70d2/dev-tracker`
3. Clicking the datapoint shows: score, verdict, all gate statuses,
   commit SHA, timestamp, triggered_by

## 6. Troubleshooting

| HTTP | Cause | Fix |
|------|-------|-----|
| 400 `missing required fields` | Payload is wrapped (`{"ceve": {...}}`) | Use FLAT form (all fields on top-level) |
| 401 | Token wrong or missing | Verify secret name = `DOABLE_DEVTRACKER_TOKEN` exactly |
| 403 | agent_id doesn't match the token's scope | Contact HexaBox for resolution |
| 429 | Rate-limit (60 req/hour per token) | Run on PR + main-push only, not every commit |
| 500 | Edge function error | Contact HexaBox with timestamp |

## 7. Security

- Token is scoped to this agent's `agent_id` — it can't post for other agents
- Token is READ-ONLY for posting CEVE results — no access to other Doable internals
- On leak: contact Doable for rotation. New token issued, old one revoked within 1 hour
- Never log the token in CI output — always use env-var, never hardcode
- Tokens don't auto-expire; Doable rotates manually 1× per year

---

_See also: `.github/workflows/doctrine-check.yml` (auto-generated with this bundle)_
