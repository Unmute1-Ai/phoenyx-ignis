# phoenyx-ignis — Codebase Map

Small, flat Python CLI. Depth-2 overview:

| Path | Type | Purpose |
|---|---|---|
| `ignis/` | package | Core application: CLI, policy engine, receipts, twin, wifi |
| `ignis/cli.py` | module | argparse CLI: `twin`, `wifi`, `repair` subcommands |
| `ignis/policy.py` | module | Policy engine: primitive allowlists, approval requirements |
| `ignis/receipts.py` | module | HMAC-SHA256 signed repair receipts (`ReceiptSigner`) |
| `ignis/twin.py` | module | Machine Twin JSON inventory generator |
| `ignis/wifi.py` | module | Wi-Fi scan/connect/disconnect via Alpine `iwd` |
| `ignis/command.py` | module | `Runner` abstraction over subprocess calls |
| `ignis/repair/` | package | Repair primitives; `windows.py` = UEFI boot manager entry |
| `tests/` | tests | pytest suite (13 tests: twin, policy, receipts, wifi, windows repair, fakes) |
| `packaging/` | assets | Alpine image build: `genapkovl-phoenyx.sh`, `mkimg.phoenyx.sh`, `ignis.start`, `policy.json` |
| `docs/` | docs | `architecture.md`, `policy.md`, `recovery-runbook.md` |
| `.github/workflows/ci.yml` | CI | ruff + pytest on py3.12; Alpine 3.20 install check; bootable ISO build artifact |
| `pyproject.toml` | manifest | Project metadata, dev extras, pytest/ruff config, `ignis` script |
| `build-iso.sh` | script | Bootable Alpine recovery ISO builder (root + Alpine required) |
| `build-alpine.sh` | script | Alpine minirootfs recovery archive builder (root required) |
| `install.sh` | script | On-target Alpine installer for the `ignis` command |
| `README.md` / `CONTRIBUTING.md` / `SECURITY.md` | docs | Quick start, dev workflow, security policy |
| `PRODUCTION_READINESS.md` / `ROADMAP.md` | docs | Status and planning notes |
