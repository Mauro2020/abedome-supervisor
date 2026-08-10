"""ABEDOME product policy."""

from typing import Final, overload

UPSTREAM_ANALYTICS_ENABLED: Final = False


@overload
def apply_upstream_diagnostics_policy(requested: bool) -> bool: ...


@overload
def apply_upstream_diagnostics_policy(requested: None) -> bool | None: ...


def apply_upstream_diagnostics_policy(requested: bool | None) -> bool | None:
    """Apply ABEDOME policy while preserving upstream tri-state semantics."""
    if not UPSTREAM_ANALYTICS_ENABLED:
        return False
    return requested
