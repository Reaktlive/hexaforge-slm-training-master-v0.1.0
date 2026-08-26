# hexaforge_slm_training_master_enrichment_hexa

**Type:** `HexaBox` · **Ports:** XI, XO, YI, YO, ZI, ZO

_executing_

## Ports

| Port | Direction | Handler | Schema |
|------|-----------|---------|--------|
| `XI` | in | `port_xi.py` | `xi.schema.json` |
| `XO` | out | `port_xo.py` | `xo.schema.json` |
| `YI` | in | `port_yi.py` | `yi.schema.json` |
| `YO` | out | `port_yo.py` | `yo.schema.json` |
| `ZI` | in | `port_zi.py` | `zi.schema.json` |
| `ZO` | out | `port_zo.py` | `zo.schema.json` |

## Wiring

**Receives from:**
_(none — this is a source node)_

**Sends to:**
_(none — this is a sink node)_

## Customizing

- **`handler.py`** — your business logic / LLM call goes here
- **`port_*.py`** — port-specific I/O. Don't add domain logic here; keep it in handler.py
- **`*.schema.json`** — port contracts. Editing these may trigger doctrine FAIL on PR. Open HexaBox Studio to author safely.

## Vertical

`ai-ml-ops` — skin colors and visual identity derive from this.
