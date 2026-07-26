# Policy

Policies are JSON documents:

```json
{
  "allowed_primitives": ["repair.windows.bootmanager_entry"],
  "require_approval": true,
  "constraints": {
    "repair.windows.bootmanager_entry": {"require_uefi": true}
  }
}
```

Primitive names use reverse-scope dot notation. Allowlist entries support shell
wildcards, but production policies should name primitives exactly. The default
policy allows only the Windows Boot Manager entry primitive, requires UEFI, and
requires explicit approval for execution.

Dry runs remain available when approval is absent: the resulting receipt has a
`planned` status and records the denial reasons. A non-dry-run repair fails
closed on every policy denial.
