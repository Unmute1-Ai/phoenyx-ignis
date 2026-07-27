"""Command line interface for Phoenyx Ignis."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .policy import Policy
from .receipts import ReceiptSigner
from .repair.windows import BootManagerRequest, WindowsBootManagerEntry
from .twin import MachineTwinGenerator
from .wifi import WifiManager


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ignis", description="Policy-controlled recovery tools")
    command = parser.add_subparsers(dest="command", required=True)

    twin = command.add_parser("twin", help="generate a Machine Twin")
    twin.add_argument("--output", "-o", default="machine-twin.json")

    wifi = command.add_parser("wifi", help="manage Wi-Fi through iwd")
    wifi_command = wifi.add_subparsers(dest="wifi_command", required=True)
    scan = wifi_command.add_parser("scan")
    scan.add_argument("--device")
    connect = wifi_command.add_parser("connect")
    connect.add_argument("ssid")
    connect.add_argument("--device")
    connect.add_argument("--passphrase")
    disconnect = wifi_command.add_parser("disconnect")
    disconnect.add_argument("--device")

    repair = command.add_parser("repair", help="run a repair primitive")
    repair_command = repair.add_subparsers(dest="repair_command", required=True)
    boot = repair_command.add_parser("windows-bootmanager-entry")
    boot.add_argument("--esp", type=Path, required=True)
    boot.add_argument("--disk", required=True)
    boot.add_argument("--part", type=int, required=True)
    boot.add_argument("--label", default="Windows Boot Manager")
    mode = boot.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--approve", action="store_true")
    boot.add_argument("--policy", type=Path)
    boot.add_argument("--receipt", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "twin":
        twin = MachineTwinGenerator().write(args.output)
        print(json.dumps(twin, indent=2, sort_keys=True))
        return 0
    if args.command == "wifi":
        manager = WifiManager()
        if args.wifi_command == "scan":
            print(json.dumps([network.__dict__ for network in manager.scan(args.device)], indent=2))
        elif args.wifi_command == "connect":
            manager.connect(args.ssid, device=args.device, passphrase=args.passphrase)
        else:
            manager.disconnect(args.device)
        return 0
    if args.command == "repair":
        policy = Policy.load(args.policy) if args.policy else Policy.safe_default()
        key_file = os.environ.get("IGNIS_RECEIPT_KEY_FILE")
        signer = ReceiptSigner.from_file(key_file) if key_file else None
        request = BootManagerRequest(
            args.esp,
            args.disk,
            args.part,
            label=args.label,
            dry_run=args.dry_run,
            approved=args.approve,
        )
        receipt = WindowsBootManagerEntry(policy, signer=signer).execute(request)
        rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        if args.receipt:
            args.receipt.write_text(rendered)
        print(rendered, end="")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
