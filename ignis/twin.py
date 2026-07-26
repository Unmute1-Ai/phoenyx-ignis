"""Machine Twin generator for portable recovery diagnostics."""

from __future__ import annotations

import json
import platform
import socket
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .command import Runner, SubprocessRunner


class MachineTwinGenerator:
    SCHEMA = "dev.phoenyx.ignis.machine-twin/v1"

    def __init__(self, runner: Runner | None = None):
        self.runner = runner or SubprocessRunner()

    def generate(self) -> dict[str, Any]:
        return {
            "schema": self.SCHEMA,
            "id": str(uuid.uuid4()),
            "captured_at": datetime.now(UTC).isoformat(),
            "host": {
                "hostname": socket.gethostname(),
                "platform": platform.system(),
                "release": platform.release(),
                "machine": platform.machine(),
            },
            "firmware": self._firmware(),
            "block_devices": self._json_command(
                [
                    "lsblk",
                    "--json",
                    "--output",
                    "NAME,PATH,TYPE,SIZE,FSTYPE,LABEL,UUID,MOUNTPOINTS",
                ],
                "blockdevices",
                [],
            ),
            "network": self._json_command(["ip", "-json", "address"], None, []),
        }

    def write(self, destination: str | Path) -> dict[str, Any]:
        twin = self.generate()
        Path(destination).write_text(json.dumps(twin, indent=2, sort_keys=True) + "\n")
        return twin

    def _firmware(self) -> dict[str, Any]:
        root = Path("/sys/class/dmi/id")
        fields = {}
        for name in ("sys_vendor", "product_name", "product_uuid", "bios_vendor", "bios_version"):
            try:
                fields[name] = (root / name).read_text(errors="replace").strip()
            except OSError:
                fields[name] = None
        fields["uefi"] = Path("/sys/firmware/efi").exists()
        return fields

    def _json_command(self, argv: list[str], key: str | None, fallback: Any) -> Any:
        try:
            result = json.loads(self.runner.run(argv).stdout)
            return result.get(key, fallback) if key else result
        except (OSError, RuntimeError, json.JSONDecodeError):
            return fallback
