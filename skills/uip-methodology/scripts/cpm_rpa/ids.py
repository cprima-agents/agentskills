"""Stable, deterministic trace IDs for generated artefact data.

ID format: {prefix}_{sha256(canonical)[:6]}

Prefix encoding (abstraction level, not domain subtype):

    obj_   structural object (entity, field)
    rel_   relationship
    dec_   decision
    req_   requirement / constraint
    act_   process step / workflow activity
    est_   estimation record / effort item
    val_   verification / test
    risk_  risk
    obs_   observation / issue / finding
    ref_   external reference

Exceptions where domain-specific prefixes are retained for readability:
    cmp_   component / container  (short, universal in RPA vocabulary)
    ADR-   architecture decision record  (sequential, human-assigned)

The domain subtype is carried separately in the item's 'type' field, not in the ID prefix.
"""

from __future__ import annotations

import hashlib

__all__ = ["assign_ids_if_missing", "gen_id"]


def gen_id(prefix: str, *canonical_parts: str) -> str:
    """Return a stable `{prefix}_{6hex}` identifier.

    prefix          — abstraction-level prefix (obj, cmp, act, dec, val, risk, obs, …)
    canonical_parts — strings that together uniquely identify the item within its type.
                      Order matters: use a fixed convention (see assign_ids_if_missing).

    The ID is stable as long as the canonical parts do not change.
    Renaming 'description', reordering rows, or moving sections does NOT change the ID.
    Renaming the item itself (the canonical name) DOES change the ID.
    """
    canonical = ":".join([prefix] + [p for p in canonical_parts])
    h = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:6]
    return f"{prefix}_{h}"


def assign_ids_if_missing(
    items: list[dict],
    prefix: str,
    *key_fields: str,
) -> None:
    """Populate missing `id` fields in-place.

    Existing 'id' values are preserved without modification (manual override support).
    The canonical name is the concatenation of item[key_field] values joined with ':'.
    Non-string values are coerced via str().
    """
    for item in items:
        if not isinstance(item, dict):
            continue
        if not item.get("id"):
            parts = [str(item.get(f) or "") for f in key_fields]
            item["id"] = gen_id(prefix, *parts)
