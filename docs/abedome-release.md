# ABEDOME Supervisor release contract

ABEDOME Supervisor 2026.11.0 is based exactly on Home Assistant Supervisor
commit `c1c6f0a754c0656eb1af189f11009f1cfc4b3e28` (tag `2026.11.0`).
The product overlay is deliberately small: ABEDOME image/feed ownership,
fail-closed privacy, and OCI branding. Home Assistant protocol identifiers are
kept for compatibility.

## Trust boundaries

- The default update feed is
  `https://mauro2020.github.io/abedome-os/updates/{channel}.json`.
- An explicit `SUPERVISOR_VERSION_URL` must be HTTPS, contain exactly one
  `{channel}` placeholder, and contain no credentials, query, or fragment.
  Invalid configuration stops startup instead of falling back upstream.
- A fetched manifest is accepted only when its Core and Supervisor images are
  the ABEDOME repositories. A rejected manifest does not update cached state.
- Upstream diagnostics and Sentry are disabled in persisted configuration, the
  API, and OS-Agent synchronization.
- Core recovery/reinstall uses the user override, the validated ABEDOME feed
  image, or the compiled ABEDOME default in that order. It never falls back to
  the official Core repository when the feed is offline.

## Image publication

The manual image workflow builds a uniquely tagged `linux/amd64` candidate,
verifies the signed pinned upstream base, verifies the candidate by digest and
runtime metadata, then promotes that same digest to the immutable version tag.
It refuses to overwrite an existing version tag and fails closed if GHCR cannot
prove that the tag is free.

This release is intentionally **OVA x86-64 only**. No ABEDOME arm64 Supervisor
artifact is available to validate a multi-architecture manifest. The workflow
does not publish or modify any update feed; stable feed publication is a later,
separately gated operation after image and OVA validation.

Release order:

1. publish and verify immutable ABEDOME Frontend/Core dependencies;
2. publish the Supervisor candidate;
3. verify the candidate digest and runtime policy;
4. promote the exact digest to `2026.11.0`;
5. build and validate the signed OVA/RAUC artifacts;
6. publish the stable feed last, using immutable versions/digests.
