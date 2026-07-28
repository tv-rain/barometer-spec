# Measurement Result Format

**Status:** Draft  
**Version:** 0.1.0

## Overview

A Measurement Result records one execution attempt for one scheduled task run. It separates:

- common execution, timing, implementation, and Network Context metadata;
- whether the attempt completed independently of what the network operation observed;
- the test-specific measurement outcome and bounded observations.

A negative network observation such as DNS `NXDOMAIN`, TCP timeout, TLS certificate failure, or an unexpected HTTP response is a completed measurement outcome. It is not automatically an execution failure and must not be retried unless a future registered test explicitly defines otherwise.

Measurement Results are delivered in the [`Result Bundle`](result-bundle.md). The bundle provides delivery idempotency and optional rotating linkage; the Measurement Result provides attempt and measurement semantics.

The encoded result and observation-count maxima are defined in [`Registered Initial Limits`](../library/registered-limits.md#result-and-bundle-limits).

## JSON Structure

```json
{
  "schema_version": "0.1.0",
  "task_id": "task-1",
  "run_id": "7JfX95yXWZQ2qkr9A2YwTg",
  "attempt": 1,
  "test": {
    "id": "TCP-01",
    "version": "0.1.0",
    "result_version": "0.1.0"
  },
  "implementation": {
    "library_version": "0.1.0",
    "platform": "android"
  },
  "time": {
    "started_at": "2026-07-28T14:32:00Z",
    "precision": "minute",
    "duration_ms": 500
  },
  "execution": {
    "state": "completed"
  },
  "network_context": {
    "access": {
      "network_type": "cellular",
      "vpn_state": "not_detected",
      "ipv4_available": "yes",
      "ipv6_available": "yes",
      "validated": "yes",
      "network_changed": false
    },
    "egress": {
      "status": "fresh",
      "lookup_source": "primary",
      "network_path": "direct",
      "country_code": "NL",
      "asn": 64500,
      "classification_version": "0.1.0"
    }
  },
  "measurement": {
    "outcome": "connected",
    "observations": [
      {
        "type": "tcp_connect",
        "status": "succeeded",
        "duration_ms": 500,
        "details": {
          "address_family": "ipv4"
        }
      }
    ]
  }
}
```

## Top-level Fields

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `schema_version` | string | Yes | `0.1.0` | Version of the common Measurement Result envelope. |
| `task_id` | string | Yes | Exact campaign-scoped, non-user-specific identifier from the accepted task; maximum 128 ASCII bytes. | Associates the result with the validated task without copying its input. |
| `run_id` | string | Yes | Base64url without padding encoding exactly 16 random bytes. | Identifies one scheduled run and its retry attempts. |
| `attempt` | integer | Yes | Positive; `1` for the initial attempt. | Attempt number within `run_id`. |
| `test` | object | Yes | Complete object defined below. | Identifies measurement behavior and result schema. |
| `implementation` | object | Yes | Complete object defined below. | Minimal producer information needed for compatibility analysis. |
| `time` | object | Yes | Complete object defined below. | Coarse start time and quantized attempt duration. |
| `execution` | object | Yes | Complete object defined below. | Attempt completion state independent of measurement outcome. |
| `network_context` | object | Conditional | Normalized [`Network Context`](network-context.md). | Context used by the attempt when one was captured. |
| `measurement` | object | Conditional | Must comply with the registered test Output schema. | Test-specific outcome and observations. |

Unknown top-level fields are rejected.

The complete encoded Measurement Result must not exceed 65,536 bytes. A non-composite result contains at most 16 observations. NET-05 uses its separately bounded step structure and must still fit the encoded-result maximum.

Task `input`, `options`, `schedule`, `execution`, `safety`, and `labels` are not copied automatically. A collector resolves them through `task_id` when authorized to do so. Results must not add an input digest as a substitute for this rule because small target spaces make such digests reversible by enumeration.

## Run and Attempt Identity

Barometer generates `run_id` from a cryptographically secure random source when a scheduled run is created. A task source, collector, host account, target, or proxy must not supply or influence it.

All retry attempts for the same scheduled run retain the same `run_id` and increment `attempt`. A repeated run receives a new random `run_id` and starts again at `attempt: 1`.

`run_id` is scoped to one task run. It must not be reused across tasks, repeated runs, or installations and must not be included in measurement traffic, Network Context requests, application analytics, or logs.

The tuple of `task_id`, `run_id`, and `attempt` identifies one logical attempt inside submitted results. Bundle retransmission uses the unchanged bundle and does not create another attempt.

## Test Object

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `id` | string | Yes | Registered test identifier. | Test that produced the result. |
| `version` | string | Yes | Exact supported test version. | Version of measurement behavior that executed. |
| `result_version` | string | Yes | Exact supported Output schema version. | Version used to validate `measurement`. |

The test behavior version and result version are independent. A compatible implementation may support more than one result version for the same test behavior, but it must emit exactly one registered combination.

Unknown test fields are rejected.

## Implementation Object

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `library_version` | string | Yes | Bounded released Barometer version. | Implementation version that produced the result. |
| `platform` | string | Yes | `android` or `ios` in the initial version. | Coarse platform family used to interpret documented platform differences. |

The object must not contain the host application version, application identifier, device model, operating-system version, CPU architecture, Go version, source revision, build timestamp, locale, timezone, or a host-supplied annotation.

Unknown implementation fields are rejected.

## Time Object

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `started_at` | string | Yes | RFC 3339 UTC timestamp truncated down to the minute. | Coarse time at which attempt evaluation began. |
| `precision` | string | Yes | `minute` | Declares the precision of `started_at`. |
| `duration_ms` | integer | Yes | Non-negative multiple of 250; rounded up except that zero remains zero. | Quantized elapsed attempt time, excluding bundle delivery. |
| `duration_capped` | boolean | No | Present and `true` only when the actual duration exceeded the largest representable or locally retained value. | Indicates that `duration_ms` is a lower bound rather than the quantized duration. |

Stage observation durations use the same quantization. The sum of stage durations need not equal the attempt duration because operations may overlap, platform APIs may hide internal work, and quantization rounds each value independently.

Implementations must use a monotonic clock for durations. Wall-clock changes during an attempt must not produce a negative or excessively large duration.

## Execution Object

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `state` | string | Yes | `completed`, `incomplete`, or `not_run` | Whether the test reached a terminal measurement outcome. |
| `reason` | string | Conditional | Required for `incomplete` and `not_run`; prohibited for `completed`. | Cross-cutting reason why a terminal measurement outcome was not produced. |

Initial reasons are:

| Reason | Meaning |
|---|---|
| `cancelled_by_host` | The host cancelled the attempt. |
| `attempt_deadline_exceeded` | The outer execution deadline expired, distinct from a bounded protocol timeout that is itself a measurement outcome. |
| `resource_limit` | A non-time outer CPU, memory, storage, connection, or data bound stopped the attempt. |
| `network_changed` | The access-network generation changed during the attempt. |
| `platform_suspended` | Mobile lifecycle or operating-system policy interrupted execution. |
| `network_context_unavailable` | A required Network Context field could not be obtained. |
| `constraints_unsatisfied` | Another accepted task execution constraint was not satisfied. |
| `local_policy_rejected` | Trusted local safety or host policy declined execution. |
| `proxy_not_configured` | The selected proxy path was not configured. |
| `proxy_not_permitted` | Local policy did not permit use of the configured proxy. |
| `proxy_path_unsupported` | The complete test configuration was incompatible with the configured proxy capability. |
| `proxy_unavailable` | Barometer could not connect to the configured local proxy. |
| `proxy_connect_failed` | The proxy did not establish the requested tunnel. |
| `proxy_reconfigured` | The host replaced or cleared the proxy during the attempt. |
| `internal_error` | An implementation failure prevented a reliable measurement outcome. |

State rules:

- `completed` requires `measurement`.
- `not_run` prohibits `measurement`.
- `incomplete` may contain `measurement` only when the test Output schema explicitly permits bounded partial results.
- a protocol timeout, refused connection, reset, DNS error, TLS validation failure, redirect, unexpected status, or response mismatch is normally a completed measurement outcome;
- `reason` must describe only the first cross-cutting termination condition that prevented completion;
- detailed policy, battery, scheduler, proxy endpoint, platform error text, and stack traces are not retained.

Invalid task input, unsupported task versions, and malformed tasks are task-validation failures. They are not Measurement Results and must be reported through a separate bounded operational interface, if one exists.

## Network Context

Completed and incomplete remote-network tests require the normalized Network Context snapshot used for execution. An unavailable egress classification is represented by `egress.status: unavailable`; it does not justify omitting the whole object.

`network_context` may be omitted only when:

- the attempt reached `not_run` before a context snapshot was captured; or
- the registered test explicitly defines another representation, as `NET-01` does for its access-only zero-traffic output.

The result must not add a public or local IP address, resolver address, proxy endpoint, network generation, interface name, provider name, carrier name, or persistent context identifier.

## Measurement Object

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `outcome` | string | Yes | Value registered by the test Output schema. | Terminal test-specific observation or composite completion class. |
| `observations` | array | Yes | Ordered, bounded, and compliant with [`measurement-observations.md`](measurement-observations.md). | Protocol and platform observations made during the test. |

Unknown measurement fields are rejected unless the test Output schema defines additional named fields, as `NET-05` does for profile and step information.

`outcome` is not a generic censorship, blocking, anomaly, or success verdict. Its meaning is limited to the applicable test specification. Test Output schemas must define one positive terminal value and every retained negative or inconclusive value.

## Partial Results

The initial test set permits a partial `measurement` only for `NET-05`, which can retain terminal results from steps completed before an outer interruption. Other incomplete attempts omit `measurement`; their `execution.reason` and any available Network Context provide the bounded operational record.

A future test may permit partial output only when its public Output schema defines:

- which observations are safe and meaningful when incomplete;
- how omitted operations are distinguished from failed operations;
- the maximum retained partial data;
- why retention cannot be misinterpreted as a terminal network outcome.

## Versioning and Extension

The envelope and test payloads evolve explicitly:

- `schema_version` versions common fields and execution semantics;
- `test.version` versions measurement behavior;
- `test.result_version` versions the test-specific Output object;
- new adopted tests receive a registered test ID and result schema;
- shared observation types can be reused without copying raw protocol data.

Unknown fields are rejected within a known version. Unsupported schema, test, or result versions must not be interpreted best-effort as a known format. A receiver may retain the opaque bounded object in a quarantine path, but it must not silently discard unknown fields and analyze the remainder.

The initial format has no arbitrary annotations or extension map. A future extension mechanism requires a new envelope version, registered names, explicit field bounds, and privacy and safety review. Tasks and host applications must not inject result extensions.

## Validation

- All required fields and conditional relationships must hold.
- `run_id` must decode to exactly 128 bits and must not be all zeroes.
- `attempt` must not exceed the accepted task retry bound.
- Test and result versions must be supported as an exact registered combination.
- `started_at` seconds must be `00` and the timezone must be `Z`.
- Durations must use the registered quantization and remain within the execution bound, except when `duration_capped` is present.
- Completed results must contain a valid terminal measurement outcome.
- Incomplete and not-run results must contain an allowed execution reason.
- Every observation must comply with the selected test result schema.
- Unknown fields, raw platform errors, and prohibited data invalidate the result before bundling.

## Privacy, Safety, and Interpretation

- Results must contain no person, account, application-user, advertising, device, SIM, subscriber, push, or stable installation identifier.
- Task inputs and labels are not copied automatically.
- Results must not retain raw packets, HTTP bodies, HTTP header values, certificate chains, cookies, credentials, system logs, stack traces, or unrelated resolver state.
- Coarse platform, time, Network Context, connection code, task, and run metadata can become identifying in combination and require bounded retention and aggregate reporting.
- A matching task or run identifier establishes only measurement workflow membership, not that results belong to one person.
- A completed negative outcome is one observation on one path and context. It does not prove censorship or identify intent.
- Derived anomaly or interference analysis must remain separate from this source result, identify its method and version, and preserve links to the source observations.
