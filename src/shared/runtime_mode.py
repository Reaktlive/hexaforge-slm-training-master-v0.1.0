"""Runtime mode (runtime_mode delivery flag) — DISCLOSED capability posture.

The generator stamps the build-selected mode as BUILD_RUNTIME_MODE below;
HEXABOX_RUNTIME_MODE overrides it at runtime (an operator can flip a reference
skeleton to live once real capabilities are bound, or run a live build locally
in reference posture for a dry run). Two modes:

  * "reference" (default) — fail-closed skeleton. Unimplemented CUSTOMER_SLOTs
    stay blocking stubs; the opt-in reference harness (DOER_REFERENCE_MODE,
    posture-gated in src/shared/reference_capability.py) MAY emit contract-
    derived, disclosed-synthetic outputs marked "reference": true. This is
    exactly today's behaviour and never claims to be domain logic.
  * "live" — the build expects REAL capability bindings. The disclosed-synthetic
    reference harness is REFUSED: an unbound capability fails closed rather than
    returning a placeholder, so a "live" agent can never silently look green on
    placeholder work.

This module only DISCLOSES and GATES the posture — it fills no business logic.
"""
from __future__ import annotations

import os

# Stamped by the generator at build time (bundleBuilder.runtimeModePy).
BUILD_RUNTIME_MODE = "reference"

_VALID = ("reference", "live")


def runtime_mode() -> str:
    """The effective runtime mode: HEXABOX_RUNTIME_MODE override, else the
    build-stamped default. An unrecognised override is ignored (we never fall
    silently to 'live')."""
    env = (os.environ.get("HEXABOX_RUNTIME_MODE") or "").strip().lower()
    if env in _VALID:
        return env
    return BUILD_RUNTIME_MODE if BUILD_RUNTIME_MODE in _VALID else "reference"


def is_live() -> bool:
    return runtime_mode() == "live"


def is_reference() -> bool:
    return runtime_mode() == "reference"
