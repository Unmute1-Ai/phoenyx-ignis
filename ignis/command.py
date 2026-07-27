"""Safe subprocess abstraction used by system-facing components."""

from __future__ import annotations

import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CommandResult:
    argv: tuple[str, ...]
    returncode: int
    stdout: str = ""
    stderr: str = ""


class Runner(Protocol):
    def run(self, argv: Sequence[str], *, check: bool = True) -> CommandResult: ...


class SubprocessRunner:
    """Execute argument arrays without invoking a shell."""

    def run(self, argv: Sequence[str], *, check: bool = True) -> CommandResult:
        if not argv:
            raise ValueError("command cannot be empty")
        completed = subprocess.run(  # noqa: S603 - callers supply fixed executable names
            list(argv), check=False, capture_output=True, text=True
        )
        result = CommandResult(
            tuple(argv), completed.returncode, completed.stdout, completed.stderr
        )
        if check and completed.returncode:
            raise CommandError(result)
        return result


class CommandError(RuntimeError):
    def __init__(self, result: CommandResult):
        super().__init__(
            f"command failed ({result.returncode}): {' '.join(result.argv)}: "
            f"{result.stderr.strip()}"
        )
        self.result = result
