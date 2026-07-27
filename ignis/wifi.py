"""Wi-Fi management through iwd's non-interactive iwctl interface."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .command import Runner, SubprocessRunner

_ANSI = re.compile(r"\x1b\[[0-9;]*m")


@dataclass(frozen=True)
class Network:
    ssid: str
    security: str
    signal: str
    connected: bool = False


class WifiManager:
    def __init__(self, runner: Runner | None = None):
        self.runner = runner or SubprocessRunner()

    def devices(self) -> list[str]:
        output = self.runner.run(["iwctl", "device", "list"]).stdout
        devices: list[str] = []
        for line in self._clean(output).splitlines():
            fields = line.split()
            if len(fields) >= 2 and fields[1] in {"station", "ap", "ad-hoc"}:
                devices.append(fields[0].lstrip(">"))
        return devices

    def scan(self, device: str | None = None) -> list[Network]:
        device = device or self._single_device()
        self.runner.run(["iwctl", "station", device, "scan"])
        output = self.runner.run(["iwctl", "station", device, "get-networks"]).stdout
        networks: list[Network] = []
        for raw in self._clean(output).splitlines():
            connected = raw.lstrip().startswith(">")
            line = raw.lstrip().lstrip(">").strip()
            fields = re.split(r"\s{2,}", line)
            if len(fields) >= 3 and fields[0].lower() not in {"network name", "name"}:
                networks.append(Network(fields[0], fields[1], fields[2], connected))
        return networks

    def connect(self, ssid: str, *, device: str | None = None, passphrase: str | None = None):
        if not ssid or "\n" in ssid:
            raise ValueError("invalid SSID")
        device = device or self._single_device()
        argv = ["iwctl", "--dont-ask"]
        if passphrase is not None:
            argv.extend(["--passphrase", passphrase])
        argv.extend(["station", device, "connect", ssid])
        self.runner.run(argv)

    def disconnect(self, device: str | None = None):
        self.runner.run(["iwctl", "station", device or self._single_device(), "disconnect"])

    def _single_device(self) -> str:
        devices = self.devices()
        if len(devices) != 1:
            raise RuntimeError(f"expected one Wi-Fi device, found {len(devices)}; specify --device")
        return devices[0]

    @staticmethod
    def _clean(value: str) -> str:
        return _ANSI.sub("", value).replace("\u001b[1;90m", "")
