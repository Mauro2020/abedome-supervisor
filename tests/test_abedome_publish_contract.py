"""Static contract tests for the ABEDOME image release workflow."""

from pathlib import Path


def test_publish_workflow_promotes_verified_digest_without_feed_write() -> None:
    """Keep candidate verification and feed publication as separate gates."""
    workflow = Path(".github/workflows/publish-abedome-supervisor.yml").read_text(
        encoding="utf-8"
    )

    assert "candidate-${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}" in workflow
    assert "platforms: linux/amd64" in workflow
    assert "EXPECTED_DIGEST: ${{ steps.build.outputs.digest }}" in workflow
    assert '"$IMAGE_NAME@$EXPECTED_DIGEST"' in workflow
    assert "Promote the verified digest to the immutable version" in workflow
    assert "git push" not in workflow
    assert "updates/stable.json" not in workflow


def test_publish_workflow_pins_and_verifies_signed_base() -> None:
    """Require the pinned upstream base to be verified before the build."""
    workflow = Path(".github/workflows/publish-abedome-supervisor.yml").read_text(
        encoding="utf-8"
    )

    assert (
        "BASE_IMAGE: ghcr.io/home-assistant/base-python:3.14-alpine3.24-2026.10.3"
    ) in workflow
    assert "cosign verify --output json" in workflow
    assert "BUILD_FROM=${{ steps.base.outputs.ref }}" in workflow
