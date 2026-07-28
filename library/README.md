# Library

Specifications for Barometer host integration, initialization, shared runtime facilities, private state, and lifecycle behavior that applies across measurement tests.

## Directory Index

- [`network-context.md`](network-context.md) — safe acquisition, caching, and lifecycle of network metadata shared by execution and results.
- [`proxy.md`](proxy.md) — host-configured HTTP CONNECT proxy integration and task path selection.
- [`registered-limits.md`](registered-limits.md) — canonical numeric version `0.1.0` limits for tasks, execution, schedules, measurements, results, bundles, linkage, and retention.
- [`result-linkage.md`](result-linkage.md) — privacy-preserving result bundling linkage, protected platform storage, rotation, and clear-data lifecycle.
- [`task-trust.md`](task-trust.md) — authenticated task provenance, issuer authority, target registration, replay handling, non-targeted delivery, and local-policy lifecycle.
