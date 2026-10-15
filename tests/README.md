# Measurement Tests

Public draft specifications for the bounded network measurements planned for the initial Barometer implementation. A test is not implementation-supported until its status and conformance evidence say so explicitly.

Every test defines its test-specific Output object inside the common [`Measurement Result`](../data-formats/measurement-result.md) envelope and reuses the bounded protocol objects in [`Measurement Observation Formats`](../data-formats/measurement-observations.md).

The cross-cutting [`Measurement Limitations`](../measurement-limitations.md) apply to every test and derived analysis.

The [measurement requirement allocation](../requirements/measurement-allocation.md) records stable IDs, unit boundaries, informative dispositions, and reused contracts for these nine Draft specifications. Allocation is development metadata and does not establish supported behavior.

## Directory Index

- [`dns-01.md`](dns-01.md) — system or direct DNS resolution with bounded response observation.
- [`dns-03.md`](dns-03.md) — DNS-over-HTTPS resolution.
- [`dns-04.md`](dns-04.md) — DNS-over-TLS resolution.
- [`http-01.md`](http-01.md) — bounded HTTPS request and response validation.
- [`net-01.md`](net-01.md) — local network-state snapshot.
- [`net-03.md`](net-03.md) — Internet validation and captive-portal context.
- [`net-05.md`](net-05.md) — sequential execution of an inline reachability profile.
- [`tcp-01.md`](tcp-01.md) — direct TCP connection attempt.
- [`tls-01.md`](tls-01.md) — TLS handshake and certificate validation.

- [`template.md`](template.md) — template for new public test specifications.
