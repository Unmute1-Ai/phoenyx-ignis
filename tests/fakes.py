from collections.abc import Sequence

from ignis.command import CommandResult


class FakeRunner:
    def __init__(self, responses=None):
        self.responses = responses or {}
        self.calls: list[tuple[str, ...]] = []

    def run(self, argv: Sequence[str], *, check: bool = True) -> CommandResult:
        command = tuple(argv)
        self.calls.append(command)
        stdout = self.responses.get(command, "")
        return CommandResult(command, 0, stdout, "")
