"""Fail closed when an immutable GHCR tag is already in use."""

from __future__ import annotations

import argparse
from collections.abc import Callable
import json
import os
import re
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

API_VERSION = "2022-11-28"
MAX_PAGES = 10_000
PAGE_SIZE = 100
TAG_PATTERN = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}\Z")


class GhcrTagCheckError(RuntimeError):
    """Raised when GHCR cannot prove that a tag is available."""


def _validate_identifier(value: str, label: str) -> str:
    value = value.strip()
    if not value:
        raise GhcrTagCheckError(f"{label} must not be empty")
    return value


def validate_tag(tag: str) -> str:
    """Validate a tag using Docker's portable tag grammar."""
    tag = _validate_identifier(tag, "tag")
    if TAG_PATTERN.fullmatch(tag) is None:
        raise GhcrTagCheckError(f"invalid container tag: {tag!r}")
    return tag


def _read_page(
    *, url: str, token: str, opener: Callable[..., Any]
) -> list[dict[str, Any]]:
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "abedome-supervisor-immutable-tag-guard",
        },
    )
    try:
        with opener(request, timeout=30) as response:
            status = getattr(response, "status", 200)
            if status != 200:
                raise GhcrTagCheckError(
                    f"GitHub Packages returned unexpected HTTP status {status}"
                )
            body = response.read()
    except HTTPError as err:
        raise GhcrTagCheckError(
            f"GitHub Packages returned HTTP {err.code}; tag availability is unknown"
        ) from err
    except (TimeoutError, URLError, OSError) as err:
        raise GhcrTagCheckError(
            f"GitHub Packages could not be reached; tag availability is unknown: {err}"
        ) from err

    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as err:
        raise GhcrTagCheckError("GitHub Packages returned invalid JSON") from err
    if not isinstance(payload, list) or len(payload) > PAGE_SIZE:
        raise GhcrTagCheckError("GitHub Packages returned an invalid page")
    if not all(isinstance(item, dict) for item in payload):
        raise GhcrTagCheckError("GitHub Packages returned an invalid version entry")
    return payload


def tag_exists(
    *,
    owner: str,
    package: str,
    tag: str,
    token: str,
    api_url: str = "https://api.github.com",
    opener: Callable[..., Any] = urlopen,
) -> bool:
    """Return whether ``tag`` exists, raising unless absence is proven."""
    owner = _validate_identifier(owner, "owner")
    package = _validate_identifier(package, "package")
    tag = validate_tag(tag)
    token = _validate_identifier(token, "token")
    api_url = _validate_identifier(api_url, "API URL").rstrip("/")
    path = (
        f"{api_url}/users/{quote(owner, safe='')}/packages/container/"
        f"{quote(package, safe='')}/versions"
    )
    for page in range(1, MAX_PAGES + 1):
        query = urlencode({"state": "active", "per_page": PAGE_SIZE, "page": page})
        versions = _read_page(url=f"{path}?{query}", token=token, opener=opener)
        for version in versions:
            metadata = version.get("metadata")
            container = (
                metadata.get("container") if isinstance(metadata, dict) else None
            )
            tags = container.get("tags") if isinstance(container, dict) else None
            if not isinstance(tags, list) or not all(
                isinstance(item, str) for item in tags
            ):
                raise GhcrTagCheckError(
                    "GitHub Packages container tag metadata is missing or malformed"
                )
            if tag in tags:
                return True
        if len(versions) < PAGE_SIZE:
            return False
    raise GhcrTagCheckError(f"GitHub Packages pagination exceeded {MAX_PAGES} pages")


def main() -> int:
    """Run the immutable-tag guard."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument(
        "--api-url", default=os.environ.get("GITHUB_API_URL", "https://api.github.com")
    )
    args = parser.parse_args()
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
    try:
        exists = tag_exists(
            owner=args.owner,
            package=args.package,
            tag=args.tag,
            token=token,
            api_url=args.api_url,
        )
    except GhcrTagCheckError as err:
        sys.stderr.write(f"::error::Immutable GHCR tag check failed: {err}\n")
        return 2
    if exists:
        sys.stderr.write(
            f"::error::Refusing to overwrite existing GHCR tag: {args.tag}\n"
        )
        return 3
    sys.stdout.write(f"GHCR tag is available for first publication: {args.tag}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
