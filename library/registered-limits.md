# Registered Initial Limits

**Status:** Draft  
**Version:** 0.1.0

Runtime JSON values follow the shared [strict decoding contract](../data-formats/json-decoding.md) in addition to this document's schema, limits, and validation rules.

## Purpose

<a id="REQ-LIMIT-0001"></a>

**REQ-LIMIT-0001:**

This document is the canonical numeric limit registry for Barometer version `0.1.0`. Public schemas and test specifications use these values unless they define a stricter value.

<a id="REQ-LIMIT-0002"></a>

**REQ-LIMIT-0002:**

A host or implementation may enforce stricter limits. It must reject a task that requests more than a registered or local limit; it must not silently clamp the task because that would change measurement semantics.

<a id="REQ-LIMIT-0003"></a>

**REQ-LIMIT-0003 (retired):**

The historical rule said that all byte limits refer to UTF-8 or encoded application data and are not exact on-wire limits because operating-system, DNS, TCP, TLS, HTTP, and proxy layers may transmit or buffer protocol overhead, without saying whether HTTP headers and DNS messages are counted application data. [REQ-LIMIT-0033](#REQ-LIMIT-0033) and [REQ-LIMIT-0034](#REQ-LIMIT-0034) replace it. This text is historical, not a current obligation; historical revisions remain available.

<a id="REQ-LIMIT-0033"></a>

**REQ-LIMIT-0033:**

All byte limits refer to UTF-8 or encoded data as stated. Attempt byte limits count bytes at the boundary defined in [REQ-LIMIT-0034](#REQ-LIMIT-0034). No byte limit is an exact on-wire limit: TLS records, TCP/IP and UDP/IP headers, operating-system retransmissions and buffering, and proxy transport framing below the counted boundary are not counted and may be transmitted or buffered before cancellation takes effect.

## Task and Identifier Limits

<a id="REQ-LIMIT-0004"></a>

**REQ-LIMIT-0004:**

| Item | Default | Maximum |
|---|---:|---:|
| Complete serialized Task JSON | — | 65,536 bytes |
| `task_id` | — | 128 ASCII bytes |
| Test-specific `input` JSON | — | 49,152 bytes |
| Test-specific `options` JSON | — | 8,192 bytes |
| Labels | — | 16 entries and 2,048 encoded bytes |
| Generic identifier not otherwise constrained | — | 64 ASCII bytes |

<a id="REQ-LIMIT-0005"></a>

**REQ-LIMIT-0005:**

Unknown fields remain rejected and count toward the size limit before rejection. Parsing must stop when the complete-task limit is exceeded.

## Signed Remote Task and Trusted Key Limits

<a id="REQ-LIMIT-0032"></a>

**REQ-LIMIT-0032:**

| Item | Default | Maximum |
|---|---:|---:|
| Complete [signed remote task package](task-trust.md#REQ-TRUST-0048) | — | 98,304 bytes |
| `key_id` | — | 64 ASCII bytes |
| Trusted issuer keys per issuer in one local policy | — | 4 |
| Trusted issuer keys in one local policy | — | 32 |
| Trusted issuer key validity period (`not_after` minus `not_before`) | — | 31,536,000 seconds (365 days) |

The package maximum admits a complete task at its 65,536-byte maximum, which encodes to 87,382 base64url characters, together with the other package members. The decoded task remains subject to the complete-task limit. Four keys per issuer allow old and new keys to overlap while installations update to a release that rotates them. The validity maximum permits annual rotation through application releases; a shorter period would require more frequent releases and stop remote tasks on slowly updating installations sooner, and a longer one would extend the use of a compromised key and of installations that never update.

## Attempt Limits

The `execution.limits` object uses:

<a id="REQ-LIMIT-0006"></a>

**REQ-LIMIT-0006:**

| Field | Default | Maximum | Meaning |
|---|---:|---:|---|
| `max_duration_ms` | 30,000 | 60,000 | Wall-clock deadline for the complete attempt, including context acquisition and cleanup. |
| `max_bytes_sent` | 32,768 | 65,536 | Bytes sent by the attempt, counted under [REQ-LIMIT-0034](#REQ-LIMIT-0034). |
| `max_bytes_received` | 131,072 | 262,144 | Bytes received by the attempt, counted under [REQ-LIMIT-0034](#REQ-LIMIT-0034). |
| `max_connections` | 8 | 12 | TCP connections or HTTP CONNECT tunnels opened by the attempt. |

<a id="REQ-LIMIT-0034"></a>

**REQ-LIMIT-0034:**

`max_bytes_sent`, `max_bytes_received`, and the NET-05 aggregate byte limits in [REQ-LIMIT-0019](#REQ-LIMIT-0019) count the attempt's test traffic where Barometer exchanges it with a transport: a TCP stream, the plaintext side of a TLS session, or a UDP datagram payload.

- **Sent:** every byte Barometer writes to such a transport for the test, including HTTP request lines, headers, and bodies; HTTP/2 frames and encoded header blocks; DNS messages, including each retransmission Barometer sends; DNS-over-TCP and DoT two-byte length prefixes; and the complete DoH HTTP exchange.
- **Received:** every byte returned to Barometer by a read from such a transport, including HTTP status lines, response headers, chunked or HTTP/2 framing, and bodies; DNS messages and length prefixes; and bytes read ahead into a buffer before parsing stops. Each read requests no more than the remaining received budget.
- **Not counted:** TLS handshake and record bytes; TCP/IP and UDP/IP headers and operating-system retransmissions; proxy transport framing; the HTTP `CONNECT` request and response exchanged with the loopback proxy endpoint under [REQ-PROXY-0017](proxy.md#REQ-PROXY-0017), after which bytes in the tunnel are counted as on a direct path; hostname resolution delegated to a platform or system resolver API that does not expose its messages to Barometer; and Network Context acquisition, which [REQ-CONTEXT-0015](network-context.md#REQ-CONTEXT-0015) and the attempt deadline bound separately.
- Every exchange in the attempt counts, including followed redirects and each NET-05 primitive step toward the aggregate limits.
- A write that would exceed the remaining sent budget is not issued. Reaching either limit stops the active operation under [REQ-LIMIT-0027](#REQ-LIMIT-0027).
- Bytes subject to a narrower bound, such as the response-header and body bounds in [REQ-LIMIT-0016](#REQ-LIMIT-0016) or the DNS message bounds in [REQ-LIMIT-0014](#REQ-LIMIT-0014), also count toward the attempt limits; the narrower bound does not exempt them.

<a id="REQ-LIMIT-0007"></a>

**REQ-LIMIT-0007:**

Every accepted remote-network task must have effective values for all four fields. Omitted task fields receive the registered defaults before local policy applies. NET-01 emits no network traffic and uses zero for the byte and connection limits.

<a id="REQ-LIMIT-0008"></a>

**REQ-LIMIT-0008:**

One protocol operation may use at most 15,000 ms. A test may define a lower timeout. Cleanup after cancellation must stop within 2,000 ms of the attempt deadline; failure to clean up is an internal diagnostic and must not extend network activity intentionally.

## Schedule and Retry Limits

<a id="REQ-LIMIT-0009"></a>

**REQ-LIMIT-0009:**

Every remote task requires `not_after`. It must be later than acceptance and no more than 604,800 seconds (7 days) after authenticated issuance or acceptance, whichever is earlier.

<a id="REQ-LIMIT-0010"></a>

**REQ-LIMIT-0010:**

Authenticated `issued_at` may be at most 300 seconds later than the trusted device time. A larger future offset or unavailable trusted time fails remote-task admission.

<a id="REQ-LIMIT-0011"></a>

**REQ-LIMIT-0011:**

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

<a id="REQ-LIMIT-0012"></a>

**REQ-LIMIT-0012:**

Retries are permitted only for registered cross-cutting execution reasons. Measurement outcomes, including DNS, TCP, TLS, HTTP, validation, and target-unavailable outcomes, are never retry reasons in version `0.1.0`.

<a id="REQ-LIMIT-0013"></a>

**REQ-LIMIT-0013:**

An embedded one-time task may omit `not_after` only when release review fixes it to one run and the host does not persist it across application updates. Repeating embedded tasks use the same lifetime, cadence, run, and jitter limits as remote tasks.

## DNS Limits

<a id="REQ-LIMIT-0014"></a>

**REQ-LIMIT-0014:**

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

<a id="REQ-LIMIT-0015"></a>

**REQ-LIMIT-0015:**

Answers beyond the retention limit are not partially appended. The result records the applicable limit outcome. Raw DNS messages, TTLs, unrelated sections, and unrequested record types remain prohibited.

## HTTP and Validation Limits

<a id="REQ-LIMIT-0016"></a>

**REQ-LIMIT-0016:**

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

<a id="REQ-LIMIT-0017"></a>

**REQ-LIMIT-0017:**

HTTP-01 requests identity encoding. Unsupported encoding, an oversized header block, or a body that reaches its bound before a configured check is decidable produces the registered bounded outcome.

<a id="REQ-LIMIT-0018"></a>

**REQ-LIMIT-0018:**

NET-03 never follows redirects. It retains only the minimized redirect class.

## NET-05 Composite Limits

<a id="REQ-LIMIT-0019"></a>

**REQ-LIMIT-0019:**

| Item | Maximum |
|---|---:|
| Encoded `profile` object | 49,152 bytes |
| Primitive steps | 8 |
| `profile_id` or `step_id` | 64 ASCII bytes |
| Aggregate connections or tunnels | 12 |
| Aggregate application bytes sent | 65,536 bytes |
| Aggregate application bytes received | 262,144 bytes |
| Composite attempt duration | 60,000 ms |

<a id="REQ-LIMIT-0020"></a>

**REQ-LIMIT-0020:**

Every nested primitive must also satisfy its own limit. The complete profile is rejected before network activity if the sum of declared maxima cannot fit within the outer limits.

## Result and Bundle Limits

<a id="REQ-LIMIT-0021"></a>

**REQ-LIMIT-0021:**

| Item | Maximum |
|---|---:|
| Encoded Measurement Result | 65,536 bytes |
| Observations in one non-composite result | 16 |
| Encoded Result Bundle | 262,144 bytes |
| Results in one bundle | 16 |
| Locally pending bundles | 32 |
| Aggregate pending bundle storage | 4,194,304 bytes |

<a id="REQ-LIMIT-0022"></a>

**REQ-LIMIT-0022:**

When a new valid result cannot fit without exceeding a limit, the library must create another bundle or reject local persistence with a bounded operational error. It must not truncate a valid result or discard fields required for interpretation.

## Context, Linkage, and Retention Limits

<a id="REQ-LIMIT-0023"></a>

**REQ-LIMIT-0023:**

| Item | Minimum | Maximum | Default |
|---|---:|---:|---:|
| Network Context endpoint response | — | 4,096 bytes | — |
| Network Context endpoint operation | — | 5,000 ms each | — |
| In-memory Network Context freshness | — | 900 seconds | 300 seconds |
| Linkage rotation period | 86,400 seconds | 604,800 seconds | No linkage |
| Unacknowledged local bundle retention | — | 86,400 seconds | 86,400 seconds |
| Accepted-task replay state | — | Task validity plus 86,400 seconds, capped at 691,200 seconds | — |

<a id="REQ-LIMIT-0024"></a>

**REQ-LIMIT-0024:**

Acknowledged bundles are deleted immediately after durable acknowledgement processing. Expired pending bundles are deleted rather than uploaded late. Barometer-owned measurement results must not be retained elsewhere by the library after acknowledgement.

<a id="REQ-LIMIT-0025"></a>

**REQ-LIMIT-0025:**

Collector, host analytics, crash reporting, and research-storage retention are deployment concerns and require explicit documented periods. They must not inherit the local maximum as permission to retain data for that duration or longer.

## Limit Handling

<a id="REQ-LIMIT-0026"></a>

**REQ-LIMIT-0026:**

- Task, input, option, profile, schedule, and declared execution-limit violations are rejected before measurement traffic.

<a id="REQ-LIMIT-0027"></a>

**REQ-LIMIT-0027:**

- A limit reached during execution stops the active operation and produces the registered measurement or common execution state.

<a id="REQ-LIMIT-0028"></a>

**REQ-LIMIT-0028:**

- Limit handling must close sockets, bodies, timers, callbacks, and temporary files.

<a id="REQ-LIMIT-0029"></a>

**REQ-LIMIT-0029:**

- Limit values and raw counters are not added to results unless the applicable result schema defines them.

<a id="REQ-LIMIT-0030"></a>

**REQ-LIMIT-0030:**

- A remote task cannot increase a limit through labels, input, options, schedule, execution, safety, or an unknown field.

<a id="REQ-LIMIT-0031"></a>

**REQ-LIMIT-0031:**

- Increasing any maximum requires a new reviewed public specification version and threat-model review.
