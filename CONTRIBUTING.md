# Contributing

Thank you for helping make recovery safer.

## Development

1. Fork the repository and create a focused branch.
2. Use Python 3.12 and install `.[dev]`.
3. Add tests for behavioral changes.
4. Run `ruff check .` and `pytest`.
5. Open a pull request describing the failure mode, safety properties, and
   validation performed.

Keep system commands behind the `Runner` interface. New repair primitives must
default to dry-run, validate all inputs, require a policy decision, and produce
a receipt. Never log credentials, Wi-Fi passphrases, signing keys, or recovered
user data.

By contributing, you agree that your contribution is licensed under the MIT
License.
