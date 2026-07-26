"""Windows UEFI boot manager repair primitive."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..command import Runner, SubprocessRunner
from ..policy import Policy
from ..receipts import ReceiptSigner, new_receipt

PRIMITIVE = "repair.windows.bootmanager_entry"
_DEVICE = re.compile(r"^/dev/[A-Za-z0-9._/+:-]+$")


@dataclass(frozen=True)
class BootManagerRequest:
    esp: Path
    disk: str
    partition: int
    label: str = "Windows Boot Manager"
    dry_run: bool = True
    approved: bool = False


class WindowsBootManagerEntry:
    def __init__(
        self,
        policy: Policy,
        runner: Runner | None = None,
        signer: ReceiptSigner | None = None,
    ):
        self.policy = policy
        self.runner = runner or SubprocessRunner()
        self.signer = signer

    def execute(self, request: BootManagerRequest) -> dict[str, Any]:
        self._validate(request)
        loader = request.esp / "EFI" / "Microsoft" / "Boot" / "bootmgfw.efi"
        context = {"uefi": Path("/sys/firmware/efi").exists(), "loader_exists": loader.is_file()}
        if not context["loader_exists"]:
            raise FileNotFoundError(f"Windows EFI loader not found: {loader}")
        decision = self.policy.evaluate(PRIMITIVE, context, approved=request.approved)
        if not decision.allowed and not request.dry_run:
            raise PermissionError("; ".join(decision.reasons))
        if not request.dry_run and self.signer is None:
            raise PermissionError("a receipt signing key is required for live repairs")

        command = [
            "efibootmgr",
            "--create",
            "--disk",
            request.disk,
            "--part",
            str(request.partition),
            "--label",
            request.label,
            "--loader",
            r"\EFI\Microsoft\Boot\bootmgfw.efi",
        ]
        status = "planned"
        if not request.dry_run:
            self.runner.run(command)
            status = "succeeded"

        receipt = new_receipt(
            PRIMITIVE,
            status=status,
            plan=[command],
            evidence={
                "esp": str(request.esp.resolve()),
                "loader_sha256": self._sha256(loader),
                "policy_reasons": list(decision.reasons),
                "approved": request.approved,
            },
        )
        return self.signer.sign(receipt) if self.signer else {"payload": receipt, "signature": None}

    @staticmethod
    def _validate(request: BootManagerRequest):
        if not request.esp.is_dir():
            raise ValueError("ESP must be an existing directory")
        if not _DEVICE.fullmatch(request.disk):
            raise ValueError("disk must be an absolute /dev device path")
        if request.partition < 1:
            raise ValueError("partition must be positive")
        if not request.label or "\n" in request.label:
            raise ValueError("invalid boot entry label")

    @staticmethod
    def _sha256(path: Path) -> str:
        import hashlib

        digest = hashlib.sha256()
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
