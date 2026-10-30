# phoenyx-ignis — Agent Guide

Policy-controlled Alpine Linux recovery environment: inventories a machine,
manages Wi-Fi via iwd, evaluates repair policy, performs explicit recovery
primitives, and writes signed repair receipts. Python CLI (`ignis`), no
runtime dependencies, defaults to dry-run.

## Stack

- **Language:** Python >= 3.12 (verified on 3.13.14; sandbox has no `python3.12` binary)
- **Packaging:** setuptools via `pyproject.toml`; console script `ignis` (entry point `ignis.cli:main`)
- **Package manager:** pip (no lockfile)
- **Dev tools:** pytest>=8.2, ruff>=0.5 (`[project.optional-dependencies].dev`)
- **Services:** none required — no database, no message broker, no web server, no ports

## Commands

```sh
# setup (one time)
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'

# verify (all three must pass)
pytest            # 13 tests, ~0.1s
ruff check .

# run the app
ignis --help
ignis twin --output machine-twin.json
ignis repair windows-bootmanager-entry --esp /path/to/esp --disk /dev/sda --part 1 --dry-run
```

## Environment

- No `.env` file and no required environment variables for development.
- `IGNIS_RECEIPT_KEY_FILE` — optional; HMAC-SHA256 key file, only needed for
  live (`--approve`) repairs. Generate with `umask 077; head -c 32 /dev/urandom > key`.
- `ALPINE_VERSION`, `ALPINE_MIRROR`, `TARGET_ARCH` — only consumed by
  `build-alpine.sh` / `build-iso.sh`, which require root, Alpine, and network.

## Codebase map

See [codebase-map.md](codebase-map.md).

## Local Verification Summary

Validated 2026-10-30 during onboarding (dev_stack_healthy: true):

| Check | Result | Evidence |
|---|---|---|
| Install `.[dev]` | pass | pip installed phoenyx-ignis 0.1.0 + pytest 9.2.0 + ruff 0.17.3 |
| CLI help flow | pass | `ignis --help` prints usage for twin/wifi/repair |
| Primary flow: Machine Twin | pass | `ignis twin --output /tmp/machine-twin.json` wrote schema `dev.phoenyx.ignis.machine-twin/v1` with host/firmware/block/network data |
| Primary flow: dry-run repair | pass | `ignis repair windows-bootmanager-entry ... --dry-run` against a stub ESP emitted receipt schema `dev.phoenyx.ignis.repair-receipt/v1`, status `planned`, policy reasons recorded, no side effects |
| Tests | pass | pytest: 13 passed |
| Lint | pass | ruff check: All checks passed |

## Sandbox snapshot

- **Snapshot ID:** `58y8jwc036m6gk4mpk08:default`
- **Captured:** 2026-10-30T16:07:06.212Z (sandbox `i25pr91a2bbtci95gsr7r`)
- State includes the `.venv` with dev dependencies installed.

## Known limits (do not assume these work in the sandbox)

- `ignis wifi scan/connect` requires Alpine's `iwd` (`iwctl`) — not present here,
  unverified live. TODO(confirm) on real hardware.
- `build-iso.sh` / `build-alpine.sh` require root + Alpine and are CI-only here.
