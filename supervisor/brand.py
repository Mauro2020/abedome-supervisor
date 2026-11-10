"""ABEDOME product policy."""

from typing import Final, overload
from urllib.parse import urlsplit

ABEDOME_CORE_IMAGE: Final = "ghcr.io/mauro2020/abedome-core"
ABEDOME_SUPERVISOR_IMAGE: Final = "ghcr.io/mauro2020/abedome-supervisor"
ABEDOME_UPDATE_FEED: Final = (
    "https://mauro2020.github.io/abedome-os/updates/{channel}.json"
)
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


def validate_update_feed_template(value: str | None) -> str:
    """Return a safe ABEDOME update-feed template or raise ``ValueError``."""
    template = ABEDOME_UPDATE_FEED if value is None else value
    parsed = urlsplit(template)
    if any(
        (
            parsed.scheme != "https",
            not parsed.hostname,
            parsed.username is not None,
            parsed.password is not None,
            bool(parsed.query),
            bool(parsed.fragment),
            template.count("{channel}") != 1,
        )
    ):
        raise ValueError(
            "SUPERVISOR_VERSION_URL must be an HTTPS URL with exactly one "
            "{channel} placeholder and no credentials, query, or fragment"
        )
    return template


def is_managed_core_image(image: str | None, feed_image: str | None) -> bool:
    """Return whether an image is managed by ABEDOME."""
    return image is not None and image in {ABEDOME_CORE_IMAGE, feed_image}
