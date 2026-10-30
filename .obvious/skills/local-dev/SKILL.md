---
name: local-dev
description: Verified local-dev procedure for phoenyx-ignis (recorded during onboarding, 2026-10-30)
---

# local-dev — phoenyx-ignis

## Stack facts

- Python >= 3.12, zero runtime dependencies, setuptools + pip, no lockfile.
- No external services: no DB, no cache, no server, no ports. The dev "stack"
  is the venv plus the CLI itself.
- Dev extras: pytest>=8.2, ruff>=0.5.

## Setup

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
```

- Sandbox note: only `python3` (3.13.x) exists — satisfies `requires-python >=3.12`;
  there is no `python3.12` binary.
- No leftover lock files to check; no ports to parse (CLI app, never binds).

## Primary flows (verified)

1. `ignis --help` — usage for twin/wifi/repair. Exit 0.
2. `ignis twin --output /tmp/machine-twin.json` — writes Machine Twin JSON
   (schema `dev.phoenyx.ignis.machine-twin/v1`). Graceful fallbacks when
   `lsblk`/`ip`/DMI data are absent, so it runs fine in a container.
3. Dry-run repair against a stub ESP:
   ```sh
   mkdir -p /tmp/fake-esp/EFI/Microsoft/Boot
   printf 'fake-loader' > /tmp/fake-esp/EFI/Microsoft/Boot/bootmgfw.efi
   ignis repair windows-bootmanager-entry --esp /tmp/fake-esp --disk /dev/sda --part 1 --dry-run
   ```
   Emits receipt (schema `dev.phoenyx.ignis.repair-receipt/v1`) with
   `status: "planned"` and policy reasons; makes no system changes.

## Proof

- `ruff check .` → "All checks passed!"
- `pytest` → 13 passed in 0.03s.

## Validation Summary

| Phase | Result | Notes |
|---|---|---|
| Install deps | pass | pip install -e '.[dev]' clean |
| Infra bring-up | n/a | No services required |
| App start | pass | `ignis --help`, exit 0 |
| Primary flow | pass | twin generation + dry-run repair receipt (above) |
| Lint | pass | ruff clean |
| Tests | pass | 13/13 |

## Gotchas

- `ignis wifi ...` needs Alpine `iwd` (`iwctl`); unavailable in sandbox — treat
  as unverified here. TODO(confirm) on target hardware.
- `build-iso.sh` / `build-alpine.sh` need root + Alpine; exercised only in CI.
- Live (`--approve`) repairs additionally require `IGNIS_RECEIPT_KEY_FILE` and
  policy approval; never needed for local dev verification.
