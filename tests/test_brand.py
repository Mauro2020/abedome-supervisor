"""Test ABEDOME product policy."""

from unittest.mock import patch

import pytest

from supervisor.brand import (
    ABEDOME_CORE_IMAGE,
    ABEDOME_UPDATE_FEED,
    apply_upstream_diagnostics_policy,
    is_managed_core_image,
    validate_update_feed_template,
)


@pytest.mark.parametrize("requested", [None, False, True])
def test_diagnostics_policy_disabled(requested: bool | None) -> None:
    """Test ABEDOME always disables upstream diagnostics."""
    assert apply_upstream_diagnostics_policy(requested) is False


@pytest.mark.parametrize("requested", [None, False, True])
def test_diagnostics_policy_preserves_upstream_value(requested: bool | None) -> None:
    """Test enabling upstream policy preserves the tri-state value."""
    with patch("supervisor.brand.UPSTREAM_ANALYTICS_ENABLED", True):
        assert apply_upstream_diagnostics_policy(requested) is requested


def test_update_feed_defaults_to_abedome() -> None:
    """Test missing configuration remains in the ABEDOME trust domain."""
    assert validate_update_feed_template(None) == ABEDOME_UPDATE_FEED


@pytest.mark.parametrize(
    "template",
    [
        "http://updates.example/{channel}.json",
        "https://updates.example/stable.json",
        "https://updates.example/{channel}/{channel}.json",
        "https://user:pass@updates.example/{channel}.json",
        "https://updates.example/{channel}.json?fallback=1",
        "https://updates.example/{channel}.json#fragment",
        "",
    ],
)
def test_update_feed_rejects_unsafe_template(template: str) -> None:
    """Test unsafe or ambiguous update-feed templates are rejected."""
    with pytest.raises(ValueError, match="must be an HTTPS URL"):
        validate_update_feed_template(template)


def test_managed_core_image() -> None:
    """Test only ABEDOME and the current feed image are managed."""
    assert is_managed_core_image(ABEDOME_CORE_IMAGE, ABEDOME_CORE_IMAGE)
    assert not is_managed_core_image(None, None)
    assert not is_managed_core_image(
        "ghcr.io/home-assistant/qemux86-64-homeassistant", ABEDOME_CORE_IMAGE
    )
