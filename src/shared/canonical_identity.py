"""The single canonicalisation of an identity used across the bundle.

Fas 3.25 (external DD). Approval binding, the audit chain and the execution
ledger must agree on what "the same tenant" means, byte for byte, or the
guarantees they each provide stop composing:

  * canonical_action_ref() case-folds the tenant into the SIGNED hash.
  * the execution ledger keys reservations on (tenant, action, idempotency_key).

When those disagreed, Tenant-A and tenant-a produced one approval reference and
two execution keys — the same approved action ran twice. This module exists so
there is exactly one answer to the question, imported rather than reimplemented.

NFKC so homoglyph and width variants collapse; strip and whitespace-fold so
padding cannot mint a second identity; casefold because an approver typing
their tenant in title case is the same customer.
"""
import unicodedata
from typing import Any


def canonical_identity(value: Any) -> str:
    """One spelling per identity: NFKC + strip + whitespace-fold + casefold."""
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value)).strip()
    return " ".join(text.split()).casefold()
