# Versioned Supervisor test images

The **Publish versioned ABEDOME Supervisor test image** workflow produces the
immutable Supervisor image used for controlled update validation.

## Version contract

The manual workflow accepts one test version, for example:

```text
2026.8.0.dev1
```

That exact value is used for both:

- the image tag: `ghcr.io/mauro2020/abedome-supervisor:2026.8.0.dev1`;
- the Supervisor version embedded in the image.

The workflow permits only pre-release test versions in the form
`YYYY.M.P.devN`. It will not publish a mutable `latest` tag.

## Safe use

1. Merge the workflow change through the protected development branch.
2. Run the workflow manually with a new, never-reused test version.
3. Confirm the test suite and published image inspection both succeed.
4. Use the exact image repository and version only in a separately approved
   ABEDOME update-manifest test.

Creating this image alone does **not** change any Home Assistant OS installation,
does **not** publish an update feed, and does **not** enable automatic updates.
