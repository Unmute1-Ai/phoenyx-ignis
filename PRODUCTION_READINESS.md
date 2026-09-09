# Production Readiness

**Current classification: early-development recovery environment with strong safety defaults.**

Phoenyx Ignis is intentionally not labeled production-ready yet. Recovery software can modify boot state and therefore needs a higher bar than ordinary application software.

## Core quality
- [ ] `pytest` passes from a clean checkout
- [ ] `ruff check .` passes
- [ ] Package builds and installs on Python 3.12
- [ ] CI remains green on every release branch

## Recovery safety
- [ ] Dry-run remains the default
- [ ] Every destructive/privileged primitive is allowlisted
- [ ] Explicit approval required for repair execution
- [ ] Receipt signing key is never stored on persistent recovery media
- [ ] Repair receipts are generated for every attempted effect
- [ ] Unsupported disk/firmware layouts fail closed
- [ ] Idempotency / repeat execution behavior documented

## Image/release
- [ ] Alpine ISO build reproduced from a clean builder
- [ ] SHA-256 published for release artifacts
- [ ] Boot tested on UEFI and legacy BIOS targets
- [ ] Windows boot repair tested on disposable images
- [ ] Rollback/recovery path documented and tested

## Operational boundary
Never market a successful dry-run or synthetic test as proof that a repair is safe on arbitrary user hardware. Production use requires verified backups and operator review.
