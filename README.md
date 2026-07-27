# Phoenyx Ignis

Phoenyx Ignis is a small, auditable recovery environment built on Alpine Linux.
It inventories a machine, connects to Wi-Fi, evaluates repair policy, performs
explicit recovery primitives, and writes signed repair receipts.

> **Status:** early development. Always keep a verified backup. Ignis defaults
> to dry-run behavior and does not make a repair unless policy allows it.

## Features

- Alpine Linux recovery image builder
- Python 3.12 application with no required runtime dependencies
- Wi-Fi discovery and connection through Alpine's `iwd`
- Machine Twin JSON inventory for reproducible diagnostics
- Policy engine with primitive allowlists and approval requirements
- `repair.windows.bootmanager_entry` UEFI repair primitive
- Canonical, HMAC-SHA256 signed repair receipts
- Unit tests and GitHub Actions CI

## Quick start

On Alpine Linux:

```sh
./install.sh
ignis twin --output machine-twin.json
ignis wifi scan
ignis wifi connect "My Network"
```

Build a bootable Alpine recovery ISO (requires root, Alpine, and network
access):

```sh
sudo ./build-iso.sh
```

The ISO and its SHA-256 checksum are written to `dist/`. It supports UEFI and
legacy BIOS boot and installs the `ignis` command during startup.
CI also publishes both files as the `phoenyx-ignis-iso` workflow artifact.

Build an Alpine minirootfs recovery archive instead:

```sh
sudo ./build-alpine.sh
```

Build outputs are written to `dist/`. Set `ALPINE_VERSION`, `ALPINE_MIRROR`,
or `TARGET_ARCH` to customize a build.

## Repair workflow

First inspect the intended operation:

```sh
ignis repair windows-bootmanager-entry \
  --esp /mnt/esp --disk /dev/sda --part 1 --dry-run
```

Then provide explicit approval and a receipt signing key:

```sh
export IGNIS_RECEIPT_KEY_FILE=/run/secrets/receipt.key
ignis repair windows-bootmanager-entry \
  --esp /mnt/esp --disk /dev/sda --part 1 --approve
```

The EFI System Partition must contain
`EFI/Microsoft/Boot/bootmgfw.efi`. The primitive uses `efibootmgr` and refuses
to proceed if the loader is missing, policy denies the operation, or approval
is absent.

Generate a key with restrictive permissions:

```sh
umask 077
head -c 32 /dev/urandom > /run/secrets/receipt.key
```

See [docs/architecture.md](docs/architecture.md),
[docs/recovery-runbook.md](docs/recovery-runbook.md), and
[docs/policy.md](docs/policy.md) for details.

## Development

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
ruff check .
```

## Security

Please read [SECURITY.md](SECURITY.md). Repairs are privileged operations;
review the generated plan and keep receipt keys off persistent recovery media.

## License

MIT — see [LICENSE](LICENSE).
