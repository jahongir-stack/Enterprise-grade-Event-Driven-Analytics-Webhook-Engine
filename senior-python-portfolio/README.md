# Senior Python Engineering Portfolio

10 self-contained Python reference projects. Requires Python 3.11+ and no third-party packages.

These are **tested educational/reference implementations**, **not audited production services**.

- **rolling-analytics** — Sliding time-window streaming statistics with ordered event times.
- **job-queue** — Priority-based retry queue with exponential backoff and dead-letter job state.
- **audit-log** — HMAC SHA-256 tamper-evident audit trail with hash-linked entries.
- **secret-vault** — Educational authenticated-encryption construction (not suitable for protecting real secrets).
- **dag-scheduler** — Deterministic topological task ordering with cycle and missing dependency checks.
- **event-store** — Append-only event stream with optimistic-version checks and SHA-256 hash chaining.
- **feature-flags** — Deterministic SHA-256 percentage rollout with explicit allow/deny targeting.
- **circuit-breaker** — Thread-safe circuit breaker with threshold, cooldown and recovery trial.
- **ledger-engine** — Thread-safe double-entry ledger with balanced, idempotent atomic posting.
- **token-bucket** — Concurrent per-tenant token-bucket limiter with deterministic clock injection.

## Running the full test suite

~~~bash
python senior-python-portfolio/run_tests.py
~~~

Each project has independent code, tests and README documentation. Do not use secret-vault for production cryptography; use an audited AEAD library instead.
