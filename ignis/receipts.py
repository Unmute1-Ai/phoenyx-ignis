"""Canonical signed receipts for repair audit trails."""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


class ReceiptSigner:
    ALGORITHM = "HMAC-SHA256"

    def __init__(self, key: bytes, *, key_id: str = "local-recovery-key"):
        if len(key) < 32:
            raise ValueError("receipt signing key must contain at least 32 bytes")
        self.key = key
        self.key_id = key_id

    @classmethod
    def from_file(cls, path: str | Path, *, key_id: str = "local-recovery-key"):
        return cls(Path(path).read_bytes(), key_id=key_id)

    def sign(self, payload: dict[str, Any]) -> dict[str, Any]:
        envelope = {
            "payload": payload,
            "signature": {
                "algorithm": self.ALGORITHM,
                "key_id": self.key_id,
                "value": hmac.new(self.key, canonical_json(payload), hashlib.sha256).hexdigest(),
            },
        }
        return envelope

    def verify(self, envelope: dict[str, Any]) -> bool:
        signature = envelope.get("signature", {})
        if signature.get("algorithm") != self.ALGORITHM:
            return False
        expected = hmac.new(
            self.key, canonical_json(envelope.get("payload")), hashlib.sha256
        ).hexdigest()
        return secrets.compare_digest(expected, str(signature.get("value", "")))


def new_receipt(
    primitive: str,
    *,
    status: str,
    plan: list[list[str]],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema": "dev.phoenyx.ignis.repair-receipt/v1",
        "receipt_id": secrets.token_hex(16),
        "created_at": datetime.now(UTC).isoformat(),
        "primitive": primitive,
        "status": status,
        "plan": plan,
        "evidence": evidence,
    }
