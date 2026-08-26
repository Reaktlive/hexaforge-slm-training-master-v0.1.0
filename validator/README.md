# Validator — CEVE-Light structural validation

Run:
```bash
./run_validation.sh
```
The script attempts to fetch fresh rules from validator.doable.com, falls back
to local baseline (`rules/baseline_version.txt`).

What this does NOT validate: business logic correctness, AI output quality,
runtime security, GDPR compliance.
