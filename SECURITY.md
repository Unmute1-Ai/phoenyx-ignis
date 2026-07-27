# Security Policy

## Supported versions

Phoenyx Ignis is pre-release software. Security fixes are applied to `main`.

## Reporting a vulnerability

Do not open a public issue for a vulnerability. Use GitHub's private
vulnerability reporting feature for this repository. Include reproduction
steps, impact, affected versions, and any proposed mitigation. Please allow a
reasonable remediation window before disclosure.

## Threat model

Ignis assumes physical access and root privileges in a recovery environment.
It protects against accidental or unauthorized repair execution through
allowlisted policy, explicit approval, dry-run plans, strict argument arrays,
and signed receipts. It does not protect a machine already controlled by a
malicious firmware, kernel, root user, or compromised signing key.

Receipt keys must be at least 32 random bytes, stored outside the image, and
provided through `IGNIS_RECEIPT_KEY_FILE`. HMAC receipts provide authenticity
to parties sharing the key; they are not public-key signatures. Rotate a key
after suspected exposure.
