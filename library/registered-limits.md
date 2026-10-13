# Registered Initial Limits

**Status:** Draft  
**Version:** 0.1.0

Runtime JSON values follow the shared [strict decoding contract](../data-formats/json-decoding.md) in addition to this document's schema, limits, and validation rules.

## Purpose

This document is the canonical numeric limit registry for Barometer version `0.1.0`. Public schemas and test specifications use these values unless they define a stricter value.

A host or implementation may enforce stricter limits. It must reject a task that requests more than a registered or local limit; it must not silently clamp the task because that would change measurement semantics.

All byte limits refer to UTF-8 or encoded application data as stated. They are not exact on-wire limits: operating-system, DNS, TCP, TLS, HTTP, and proxy layers may transmit or buffer protocol overhead before cancellation takes effect.

## Task and Identifier Limits

| Item | Default | Maximum |
|---|---:|---:|
| Complete serialized Task JSON | — | 65,536 bytes |
| `task_id` | — | 128 ASCII bytes |
| Test-specific `input` JSON | — | 49,152 bytes |
| Test-specific `options` JSON | — | 8,192 bytes |
| Labels | — | 16 entries and 2,048 encoded bytes |
| Generic identifier not otherwise constrained | — | 64 ASCII bytes |

Unknown fields remain rejected and count toward the size limit before rejection. Parsing must stop when the complete-task limit is exceeded.

## Attempt Limits

The `execution.limits` object uses:

| Field | Default | Maximum | Meaning |
|---|---:|---:|---|
| `max_duration_ms` | 30,000 | 60,000 | Wall-clock deadline for the complete attempt, including context acquisition and cleanup. |
| `max_bytes_sent` | 32,768 | 65,536 | Application bytes supplied to network APIs, excluding lower-layer framing. |
| `max_bytes_received` | 131,072 | 262,144 | Application bytes accepted from network APIs before parsing stops. |
| `max_connections` | 8 | 12 | TCP connections or HTTP CONNECT tunnels opened by the attempt. |

Every accepted remote-network task must have effective values for all four fields. Omitted task fields receive the registered defaults before local policy applies. NET-01 emits no network traffic and uses zero for the byte and connection limits.

One protocol operation may use at most 15,000 ms. A test may define a lower timeout. Cleanup after cancellation must stop within 2,000 ms of the attempt deadline; failure to clean up is an internal diagnostic and must not extend network activity intentionally.

## Schedule and Retry Limits

Every remote task requires `not_after`. It must be later than acceptance and no more than 604,800 seconds (7 days) after authenticated issuance or acceptance, whichever is earlier.

Authenticated `issued_at` may be at most 300 seconds later than the trusted device time. A larger future offset or unavailable trusted time fails remote-task admission.

| Item | Minimum | Maximum | Default |
|---|---:|---:|---:|
| Runs per task | 1 | 28 | 1 |
| Local time-window ranges | 1 | 4 | No time window |
| Repeat interval | 21,600 seconds | 604,800 seconds | No repetition |
| Repeat jitter | 300 seconds | Lesser of 1,800 seconds or one quarter of the interval | Required for repeated tasks |
| Attempts per run, including initial | 1 | 2 | 1 |
| Retry initial delay | 30,000 ms | 300,000 ms | 30,000 ms |
| Retry maximum delay | Initial delay | 600,000 ms | Initial delay |
| Retry jitter | 0 ms | 60,000 ms | 10,000 ms |
| Exponential multiplier | 2 | 2 | 2 |

Retries are permitted only for registered cross-cutting execution reasons. Measurement outcomes, including DNS, TCP, TLS, HTTP, validation, and target-unavailable outcomes, are never retry reasons in version `0.1.0`.

An embedded one-time task may omit `not_after` only when release review fixes it to one run and the host does not persist it across application updates. Repeating embedded tasks use the same lifetime, cadence, run, and jitter limits as remote tasks.

## DNS Limits

| Item | Default | Maximum |
|---|---:|---:|
| Normalized hostname | — | 253 ASCII bytes after IDNA normalization |
| Direct UDP DNS message accepted | — | 4,096 bytes |
| TCP, DoT, or DoH DNS message accepted | — | 65,535 bytes |
| Matching response datagrams retained by DNS-01 | 1 | 3 |
| Additional-response observation window | — | 1,000 ms |
| Normalized answer entries per response | — | 16 |
| Intervening CNAME entries within answer limit | — | 8 |
| Encoded normalized DNS observation | — | 16,384 bytes |

Answers beyond the retention limit are not partially appended. The result records the applicable limit outcome. Raw DNS messages, TTLs, unrelated sections, and unrequested record types remain prohibited.

## HTTP and Validation Limits

| Item | Default | Maximum |
|---|---:|---:|
| Normalized URL | — | 2,048 UTF-8 bytes |
| Terminal body bytes processed by HTTP-01 | 4,096 bytes | 65,536 bytes |
| Validation response prefix processed by NET-03 | 1,024 bytes | 4,096 bytes |
| Response header bytes accepted | — | 16,384 bytes |
| Body checks | 0 | 8 |
| Header checks | 0 | 8 |
| Literal matcher value | — | 256 UTF-8 bytes |
| Redirects followed | 0 | 2 |
| Redirect URL length | — | 2,048 UTF-8 bytes |
| ALPN protocol entries | 0 | 8 |
| One ALPN protocol identifier | — | 32 ASCII bytes |

HTTP-01 requests identity encoding. Unsupported encoding, an oversized header block, or a body that reaches its bound before a configured check is decidable produces the registered bounded outcome.

NET-03 never follows redirects. It retains only the minimized redirect class.

## NET-05 Composite Limits

| Item | Maximum |
|---|---:|
| Encoded `profile` object | 49,152 bytes |
| Primitive steps | 8 |
| `profile_id` or `step_id` | 64 ASCII bytes |
| Aggregate connections or tunnels | 12 |
| Aggregate application bytes sent | 65,536 bytes |
| Aggregate application bytes received | 262,144 bytes |
| Composite attempt duration | 60,000 ms |

Every nested primitive must also satisfy its own limit. The complete profile is rejected before network activity if the sum of declared maxima cannot fit within the outer limits.

## Result and Bundle Limits

| Item | Maximum |
|---|---:|
| Encoded Measurement Result | 65,536 bytes |
| Observations in one non-composite result | 16 |
| Encoded Result Bundle | 262,144 bytes |
| Results in one bundle | 16 |
| Locally pending bundles | 32 |
| Aggregate pending bundle storage | 4,194,304 bytes |

When a new valid result cannot fit without exceeding a limit, the library must create another bundle or reject local persistence with a bounded operational error. It must not truncate a valid result or discard fields required for interpretation.

## Context, Linkage, and Retention Limits

| Item | Minimum | Maximum | Default |
|---|---:|---:|---:|
| Network Context endpoint response | — | 4,096 bytes | — |
| Network Context endpoint operation | — | 5,000 ms each | — |
| In-memory Network Context freshness | — | 900 seconds | 300 seconds |
| Linkage rotation period | 86,400 seconds | 604,800 seconds | No linkage |
| Unacknowledged local bundle retention | — | 86,400 seconds | 86,400 seconds |
| Accepted-task replay state | — | Task validity plus 86,400 seconds, capped at 691,200 seconds | — |

Acknowledged bundles are deleted immediately after durable acknowledgement processing. Expired pending bundles are deleted rather than uploaded late. Barometer-owned measurement results must not be retained elsewhere by the library after acknowledgement.

Collector, host analytics, crash reporting, and research-storage retention are deployment concerns and require explicit documented periods. They must not inherit the local maximum as permission to retain data for that duration or longer.

## Limit Handling

- Task, input, option, profile, schedule, and declared execution-limit violations are rejected before measurement traffic.
- A limit reached during execution stops the active operation and produces the registered measurement or common execution state.
- Limit handling must close sockets, bodies, timers, callbacks, and temporary files.
- Limit values and raw counters are not added to results unless the applicable result schema defines them.
- A remote task cannot increase a limit through labels, input, options, schedule, execution, safety, or an unknown field.
- Increasing any maximum requires a new reviewed public specification version and threat-model review.
