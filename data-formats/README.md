# Data Formats

Specifications for normalized runtime context and the objects used to define, constrain, schedule, classify, and report Barometer measurements.

## Directory Index

- [`json-decoding.md`](json-decoding.md) — shared strict runtime decoding, representation, schema selection, bounds, and failure contract.
- [`measurement-observations.md`](measurement-observations.md) — bounded reusable DNS, TCP, TLS, and HTTP observation objects and closed normalized-value vocabularies.
- [`measurement-result.md`](measurement-result.md) — common per-attempt result envelope, execution state, timing, and versioning.
- [`network-context.md`](network-context.md) — normalized access and egress metadata shared by execution and measurement results.
- [`result-bundle.md`](result-bundle.md) — bounded packet containing one or more measurement results and optional rotating linkage metadata.
- [`task.md`](task.md) — top-level measurement task structure.
- [`task-execution.md`](task-execution.md) — runtime eligibility, limits, and execution constraints.
- [`task-input.md`](task-input.md) — test-specific measurement subjects and input-validation rules.
- [`task-labels.md`](task-labels.md) — optional non-sensitive task classification metadata.
- [`task-options.md`](task-options.md) — test-specific behavior and option-validation rules.
- [`task-safety.md`](task-safety.md) — declared risk, consent, and safety requirements.
- [`task-schedule.md`](task-schedule.md) — timing, repetition, retry, and run-limit rules.
