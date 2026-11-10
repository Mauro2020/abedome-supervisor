"""Tests for the immutable GHCR tag guard."""

import json
from typing import Self
from urllib.error import HTTPError, URLError

import pytest

from script.abedome.check_ghcr_tag import GhcrTagCheckError, tag_exists, validate_tag


def _version(*tags: str) -> dict[str, object]:
    return {"metadata": {"container": {"tags": list(tags)}}}


class _Response:
    def __init__(
        self,
        payload: object | None = None,
        *,
        status: int = 200,
        raw_body: bytes | None = None,
    ) -> None:
        self.status = status
        self._body = raw_body if raw_body is not None else json.dumps(payload).encode()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return self._body


class _Opener:
    def __init__(self, *pages_or_errors: object) -> None:
        self._pages_or_errors = list(pages_or_errors)
        self.requests: list[object] = []

    def __call__(self, request: object, *, timeout: int) -> _Response:
        self.requests.append(request)
        assert timeout == 30
        if not self._pages_or_errors:
            raise AssertionError("unexpected extra request")
        item = self._pages_or_errors.pop(0)
        if isinstance(item, BaseException):
            raise item
        if isinstance(item, _Response):
            return item
        return _Response(item)


def _call(opener: _Opener, tag: str = "2026.11.0") -> bool:
    return tag_exists(
        owner="Mauro2020",
        package="abedome-supervisor",
        tag=tag,
        token="test-token",
        opener=opener,
    )


def test_exact_existing_tag_is_refused() -> None:
    """Refuse an exact existing tag."""
    assert _call(_Opener([_version("2026.11.0")]))


def test_similar_or_missing_tag_is_available() -> None:
    """Do not confuse a similar tag with an exact match."""
    assert not _call(_Opener([_version("2026.11.0.1")]))


def test_all_pages_are_scanned() -> None:
    """Scan every returned page for an exact match."""
    opener = _Opener([_version() for _ in range(100)], [_version("2026.11.0")])
    assert _call(opener)
    assert len(opener.requests) == 2


@pytest.mark.parametrize(
    "error",
    [
        HTTPError("https://api.github.test", 403, "Forbidden", {}, None),
        URLError("offline"),
    ],
)
def test_transport_errors_fail_closed(error: Exception) -> None:
    """Fail closed when tag availability cannot be established."""
    with pytest.raises(GhcrTagCheckError):
        _call(_Opener(error))


def test_malformed_response_fails_closed() -> None:
    """Fail closed on malformed metadata and JSON."""
    with pytest.raises(GhcrTagCheckError, match="metadata"):
        _call(_Opener([{"metadata": {}}]))
    with pytest.raises(GhcrTagCheckError, match="invalid JSON"):
        _call(_Opener(_Response(raw_body=b"not-json")))


def test_missing_token_and_invalid_tag_fail_before_network() -> None:
    """Validate credentials and tag syntax before a request."""
    opener = _Opener()
    with pytest.raises(GhcrTagCheckError, match="token"):
        tag_exists(
            owner="Mauro2020",
            package="abedome-supervisor",
            tag="2026.11.0",
            token="",
            opener=opener,
        )
    assert not opener.requests
    with pytest.raises(GhcrTagCheckError, match="invalid container tag"):
        validate_tag("not a tag")
