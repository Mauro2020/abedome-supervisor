"""Test ABEDOME product policy."""

from unittest.mock import patch

import pytest

from supervisor.brand import apply_upstream_diagnostics_policy


@pytest.mark.parametrize("requested", [None, False, True])
def test_diagnostics_policy_disabled(requested: bool | None):
    """Test ABEDOME always disables upstream diagnostics."""
    assert apply_upstream_diagnostics_policy(requested) is False


@pytest.mark.parametrize("requested", [None, False, True])
def test_diagnostics_policy_preserves_upstream_value(requested: bool | None):
    """Test enabling the upstream policy preserves its tri-state value."""
    with patch("supervisor.brand.UPSTREAM_ANALYTICS_ENABLED", True):
        assert apply_upstream_diagnostics_policy(requested) is requested
