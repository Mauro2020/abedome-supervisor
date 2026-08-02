# PVE Supervisor image

This workflow publishes a **test-only x86-64 image** of the ABEDOME Supervisor
fork for the next Proxmox validation build.

## Publishing

Run **Publish ABEDOME Supervisor PVE image** manually from
`abedome/develop`. Supply a new immutable tag tied to the selected commit, for
example:

```text
pve-7a80dabad258
```

The workflow first runs the Supervisor test suite, then publishes:

```text
ghcr.io/mauro2020/abedome-supervisor:<tag>
```

The package must be publicly readable before an ABEDOME OS build can preload it:
the HAOS build container retrieves initial images with Skopeo and has no GitHub
Package credential. This is acceptable only for this public-source,
non-production validation image.

## Boundaries

- This image targets only `linux/amd64` and the Proxmox x86-64 validation path.
- It is not a production release and is not an OTA artifact.
- It does not enable `SUPERVISOR_VERSION_URL`; runtime updates still use the
  official Home Assistant version manifest.
- The next ABEDOME OS change will reference one explicit image tag, and the
  build will resolve and embed its digest.

Do not publish a `latest` tag or reuse a test tag for a different commit.
