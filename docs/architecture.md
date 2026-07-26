# Architecture

Ignis separates observation, authorization, execution, and evidence.

1. The Machine Twin generator observes hardware, storage, firmware, and network
   state without mutating them.
2. A primitive creates a concrete command plan and supplies execution context
   to the policy engine.
3. Policy checks the primitive allowlist, machine constraints, and explicit
   operator approval.
4. An injected command runner executes fixed argument arrays without a shell.
5. The result and relevant evidence become a canonical signed receipt.

System-facing code accepts a `Runner`, allowing tests to verify exact commands
without changing the host. The default implementation uses Python's
`subprocess` module with `shell=False`.

## Trust boundaries

The recovery kernel, Python runtime, policy file, and operator are trusted.
Attached disks, filenames, firmware variables, network responses, and target
operating systems are untrusted. Receipt verification proves possession of the
shared HMAC key, not which individual operator performed a repair.
