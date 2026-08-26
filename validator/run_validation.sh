#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo "Studio CEVE-Light validator"
echo "Baseline rules version: $(cat rules/baseline_version.txt)"
exec python3 engine.py
