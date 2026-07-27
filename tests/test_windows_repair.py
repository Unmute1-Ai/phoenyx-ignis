from pathlib import Path

import pytest

from ignis.policy import Policy
from ignis.receipts import ReceiptSigner
from ignis.repair.windows import BootManagerRequest, WindowsBootManagerEntry

from .fakes import FakeRunner


def make_esp(tmp_path: Path) -> Path:
    loader = tmp_path / "EFI" / "Microsoft" / "Boot" / "bootmgfw.efi"
    loader.parent.mkdir(parents=True)
    loader.write_bytes(b"test-loader")
    return tmp_path


def permissive_policy() -> Policy:
    return Policy(
        allowed_primitives=["repair.windows.bootmanager_entry"],
        require_approval=True,
        constraints={},
    )


def test_dry_run_returns_plan_without_execution(tmp_path):
    runner = FakeRunner()
    primitive = WindowsBootManagerEntry(permissive_policy(), runner)
    result = primitive.execute(BootManagerRequest(make_esp(tmp_path), "/dev/sda", 1))
    assert result["payload"]["status"] == "planned"
    assert result["signature"] is None
    assert runner.calls == []


def test_approved_repair_executes_exact_efibootmgr_command(tmp_path):
    runner = FakeRunner()
    signer = ReceiptSigner(b"x" * 32)
    primitive = WindowsBootManagerEntry(permissive_policy(), runner, signer)
    request = BootManagerRequest(
        make_esp(tmp_path), "/dev/nvme0n1", 2, dry_run=False, approved=True
    )
    result = primitive.execute(request)
    assert runner.calls[0][:6] == (
        "efibootmgr",
        "--create",
        "--disk",
        "/dev/nvme0n1",
        "--part",
        "2",
    )
    assert result["payload"]["status"] == "succeeded"
    assert signer.verify(result)


def test_execution_without_approval_is_denied(tmp_path):
    primitive = WindowsBootManagerEntry(permissive_policy(), FakeRunner())
    request = BootManagerRequest(make_esp(tmp_path), "/dev/sda", 1, dry_run=False)
    with pytest.raises(PermissionError, match="approval"):
        primitive.execute(request)


def test_execution_without_signer_is_denied(tmp_path):
    primitive = WindowsBootManagerEntry(permissive_policy(), FakeRunner())
    request = BootManagerRequest(
        make_esp(tmp_path), "/dev/sda", 1, dry_run=False, approved=True
    )
    with pytest.raises(PermissionError, match="signing key"):
        primitive.execute(request)


def test_missing_loader_is_rejected(tmp_path):
    primitive = WindowsBootManagerEntry(permissive_policy(), FakeRunner())
    with pytest.raises(FileNotFoundError):
        primitive.execute(BootManagerRequest(tmp_path, "/dev/sda", 1))
