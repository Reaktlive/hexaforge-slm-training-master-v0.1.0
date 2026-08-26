## DevTracker

<!-- The tracker matches this line (or the branch name / PR title) to check the ticket off on merge. -->
DevTracker: <TICKET-ID>

## Doctrine impact

- [ ] No `karta.yaml` changes (skeleton unchanged)
- [ ] `karta.yaml` changes — composer re-run required
- [ ] Port contract changes — H1 / H2 / H4 will re-run
- [ ] Customer extension point only (`handler.py` / `shared/`)

## Validator output

```
Paste CI output here, e.g.:
doctrine: 10/10 re-verified PASS
artifact-conformance: 8 PASS · 1 N/A · 0 FAIL
Score: 100/100
```

## HexaBox Studio link

If this PR relates to a Studio-managed agent, paste the Project Page URL:

[Open agent in Studio →](https://hexabox-vault.lovable.app/studio/project/<id>)

## Checklist

- [ ] Doctrine validator passes locally
- [ ] Demo scenario still produces expected output
- [ ] Customer extension points documented if changed
- [ ] No locked files modified (see `docs/customer-extensions.md`)
