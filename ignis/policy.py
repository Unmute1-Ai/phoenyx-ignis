"""Minimal policy engine for recovery primitives."""

from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reasons: tuple[str, ...] = ()
    require_approval: bool = True


@dataclass
class Policy:
    allowed_primitives: list[str] = field(default_factory=list)
    require_approval: bool = True
    constraints: dict[str, dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def safe_default(cls) -> Policy:
        return cls(
            allowed_primitives=["repair.windows.bootmanager_entry"],
            require_approval=True,
            constraints={"repair.windows.bootmanager_entry": {"require_uefi": True}},
        )

    @classmethod
    def load(cls, path: str | Path) -> Policy:
        data = json.loads(Path(path).read_text())
        return cls(
            allowed_primitives=list(data.get("allowed_primitives", [])),
            require_approval=bool(data.get("require_approval", True)),
            constraints=dict(data.get("constraints", {})),
        )

    def evaluate(
        self, primitive: str, context: dict[str, Any], *, approved: bool = False
    ) -> PolicyDecision:
        reasons: list[str] = []
        if not any(fnmatch.fnmatchcase(primitive, pattern) for pattern in self.allowed_primitives):
            reasons.append("primitive is not allowlisted")
        rules = self.constraints.get(primitive, {})
        if rules.get("require_uefi") and not context.get("uefi", False):
            reasons.append("UEFI firmware is required")
        if self.require_approval and not approved:
            reasons.append("explicit operator approval is required")
        return PolicyDecision(not reasons, tuple(reasons), self.require_approval)
