# Measurement Result Format

**Status:** Draft  
**Version:** 0.1.0

Runtime JSON values follow the shared [strict decoding contract](json-decoding.md) in addition to this document's schema, limits, and validation rules.

## Overview

A Measurement Result records one execution attempt for one scheduled task run. It separates:

- common execution, timing, implementation, and Network Context metadata;
- whether the attempt completed independently of what the network operation observed;
- the test-specific measurement outcome and bounded observations.

<a id="REQ-RESULT-0001"></a>

**REQ-RESULT-0001:**

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

<a id="REQ-RESULT-0002"></a>

**REQ-RESULT-0002:**

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
| `network_context` | object | Conditional | Normalized [`Network Context`](network-context.md). | Context used by a completed or incomplete attempt, under the [Network Context](#network-context) rules. |
| `measurement` | object | Conditional | Must comply with the registered test Output schema. | Test-specific outcome and observations. |

<a id="REQ-RESULT-0003"></a>

**REQ-RESULT-0003:**

Unknown top-level fields are rejected.

<a id="REQ-RESULT-0004"></a>

**REQ-RESULT-0004:**

The complete encoded Measurement Result must not exceed 65,536 bytes. A non-composite result contains at most 16 observations. NET-05 uses its separately bounded step structure and must still fit the encoded-result maximum.

<a id="REQ-RESULT-0005"></a>

**REQ-RESULT-0005:**

Task `input`, `options`, `schedule`, `execution`, `safety`, and `labels` are not copied automatically. A collector resolves them through `task_id` when authorized to do so. Results must not add an input digest as a substitute for this rule because small target spaces make such digests reversible by enumeration.

## Run and Attempt Identity

<a id="REQ-RESULT-0006"></a>

**REQ-RESULT-0006:**

Barometer generates `run_id` from a cryptographically secure random source when a scheduled run is created. A task source, collector, host account, target, or proxy must not supply or influence it.

<a id="REQ-RESULT-0007"></a>

**REQ-RESULT-0007:**

All retry attempts for the same scheduled run retain the same `run_id` and increment `attempt`. A repeated run receives a new random `run_id` and starts again at `attempt: 1`.

<a id="REQ-RESULT-0008"></a>

**REQ-RESULT-0008:**

`run_id` is scoped to one task run. It must not be reused across tasks, repeated runs, or installations and must not be included in measurement traffic, Network Context requests, application analytics, or logs.

<a id="REQ-RESULT-0009"></a>

**REQ-RESULT-0009:**

The tuple of `task_id`, `run_id`, and `attempt` identifies one logical attempt inside submitted results. Bundle retransmission uses the unchanged bundle and does not create another attempt.

## Test Object

<a id="REQ-RESULT-0010"></a>

**REQ-RESULT-0010:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `id` | string | Yes | Registered test identifier. | Test that produced the result. |
| `version` | string | Yes | Exact supported test version. | Version of measurement behavior that executed. |
| `result_version` | string | Yes | Exact supported Output schema version. | Version used to validate `measurement`. |

<a id="REQ-RESULT-0011"></a>

**REQ-RESULT-0011:**

The test behavior version and result version are independent. A compatible implementation may support more than one result version for the same test behavior, but it must emit exactly one registered combination.

<a id="REQ-RESULT-0012"></a>

**REQ-RESULT-0012:**

Unknown test fields are rejected.

## Implementation Object

<a id="REQ-RESULT-0013"></a>

**REQ-RESULT-0013:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `library_version` | string | Yes | Bounded released Barometer version. | Implementation version that produced the result. |
| `platform` | string | Yes | `android` or `ios` in the initial version. | Coarse platform family used to interpret documented platform differences. |

<a id="REQ-RESULT-0014"></a>

**REQ-RESULT-0014:**

The object must not contain the host application version, application identifier, device model, operating-system version, CPU architecture, Go version, source revision, build timestamp, locale, timezone, or a host-supplied annotation.

<a id="REQ-RESULT-0015"></a>

**REQ-RESULT-0015:**

Unknown implementation fields are rejected.

## Time Object

<a id="REQ-RESULT-0016"></a>

**REQ-RESULT-0016:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `started_at` | string | Yes | RFC 3339 UTC timestamp truncated down to the minute. | Coarse time at which attempt evaluation began. |
| `precision` | string | Yes | `minute` | Declares the precision of `started_at`. |
| `duration_ms` | integer | Yes | Non-negative multiple of 250; rounded up except that zero remains zero. | Quantized elapsed attempt time, excluding bundle delivery. |
| `duration_capped` | boolean | No | Present and `true` only when the actual duration exceeded the largest representable or locally retained value. | Indicates that `duration_ms` is a lower bound rather than the quantized duration. |

<a id="REQ-RESULT-0017"></a>

**REQ-RESULT-0017:**

Stage observation durations use the same quantization. The sum of stage durations need not equal the attempt duration because operations may overlap, platform APIs may hide internal work, and quantization rounds each value independently.

<a id="REQ-RESULT-0018"></a>

**REQ-RESULT-0018:**

Implementations must use a monotonic clock for durations. Wall-clock changes during an attempt must not produce a negative or excessively large duration.

## Execution Object

<a id="REQ-RESULT-0019"></a>

**REQ-RESULT-0019:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `state` | string | Yes | `completed`, `incomplete`, or `not_run` | Whether the test reached a terminal measurement outcome. |
| `reason` | string | Conditional | Required for `incomplete` and `not_run`; prohibited for `completed`. | Cross-cutting reason why a terminal measurement outcome was not produced. |

Initial reasons are:

<a id="REQ-RESULT-0020"></a>

**REQ-RESULT-0020:**

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

<a id="REQ-RESULT-0021"></a>

**REQ-RESULT-0021:**

State rules:

- `completed` requires `measurement`.
- `not_run` prohibits `measurement`.
- `incomplete` may contain `measurement` only when the test Output schema explicitly permits bounded partial results.
- a protocol timeout, refused connection, reset, DNS error, TLS validation failure, redirect, unexpected status, or response mismatch is normally a completed measurement outcome;
- `reason` must describe only the first cross-cutting termination condition that prevented completion;
- detailed policy, battery, scheduler, proxy endpoint, platform error text, and stack traces are not retained.

<a id="REQ-RESULT-0022"></a>

**REQ-RESULT-0022:**

Invalid task input, unsupported task versions, and malformed tasks are task-validation failures. They are not Measurement Results and must be reported through a separate bounded operational interface, if one exists.

### State Boundaries

<a id="REQ-RESULT-0051"></a>

**REQ-RESULT-0051:**

An attempt is `not_run` until the test starts. The test starts at the first step of its registered procedure that observes the network for the measurement: its first test-specific network operation or, when that comes first, its own network-state observation, such as `NET-01` collection or the `NET-05` stable-network check. Admission, scheduling, task, profile and input validation, safety and permission checks, access-context capture, path and proxy snapshots, egress-context acquisition, and execution-constraint evaluation do not start the test, even when egress-context acquisition sends traffic to a context endpoint. A cross-cutting termination condition that occurs before the test starts produces `not_run` with that reason. After the test starts, a cross-cutting termination condition produces `incomplete`, unless [REQ-RESULT-0052](#REQ-RESULT-0052) applies. Registered test termination rules apply after the test starts.

<a id="REQ-RESULT-0052"></a>

**REQ-RESULT-0052:**

Once the test records its terminal measurement outcome, the attempt is `completed`. A later cancellation, deadline expiry, network change, platform suspension, proxy change, resource limit, or cleanup failure while connections close and resources are released does not change the state, reason, or `measurement`. Releasing those resources remains subject to the attempt's bounds.

## Network Context

<a id="REQ-RESULT-0023"></a>

**REQ-RESULT-0023:**

Completed and incomplete remote-network tests require the normalized Network Context snapshot used for execution. An unavailable egress classification is represented by `egress.status: unavailable`; it does not justify omitting the whole object.

<a id="REQ-RESULT-0024"></a>

**REQ-RESULT-0024 (retired):**

The historical rule permitted omitting `network_context` only when the attempt reached `not_run` before a context snapshot was captured, or when the registered test defined another representation. [REQ-RESULT-0053](#REQ-RESULT-0053) replaces it: a `not_run` result never contains `network_context`. This text is historical, not a current obligation; historical revisions remain available.

<a id="REQ-RESULT-0053"></a>

**REQ-RESULT-0053:**

A `not_run` result must not contain `network_context`, including when a context snapshot was captured before the attempt stopped. A completed or incomplete result may omit `network_context` only when the registered test explicitly defines another representation, as `NET-01` does for its access-only zero-traffic output. A snapshot captured for an attempt that ends `not_run` is used only for that attempt's eligibility decision and is not retained in its result.

<a id="REQ-RESULT-0025"></a>

**REQ-RESULT-0025:**

The result must not add a public or local IP address, resolver address, proxy endpoint, network generation, interface name, provider name, carrier name, or persistent context identifier.

## Measurement Object

<a id="REQ-RESULT-0026"></a>

**REQ-RESULT-0026:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `outcome` | string | Yes | Value registered by the test Output schema. | Terminal test-specific observation or composite completion class. |
| `observations` | array | Yes | Ordered, bounded, and compliant with [`measurement-observations.md`](measurement-observations.md). | Protocol and platform observations made during the test. |

<a id="REQ-RESULT-0027"></a>

**REQ-RESULT-0027:**

Unknown measurement fields are rejected unless the test Output schema defines additional named fields, as `NET-05` does for profile and step information.

<a id="REQ-RESULT-0028"></a>

**REQ-RESULT-0028:**

`outcome` is not a generic censorship, blocking, anomaly, or success verdict. Its meaning is limited to the applicable test specification. Test Output schemas must define one positive terminal value and every retained negative or inconclusive value.

## Partial Results

<a id="REQ-RESULT-0029"></a>

**REQ-RESULT-0029:**

The initial test set permits a partial `measurement` only for `NET-05`, which can retain terminal results from steps completed before an outer interruption. Other incomplete attempts omit `measurement`; their `execution.reason` and any available Network Context provide the bounded operational record.

<a id="REQ-RESULT-0030"></a>

**REQ-RESULT-0030:**

A future test may permit partial output only when its public Output schema defines:

- which observations are safe and meaningful when incomplete;
- how omitted operations are distinguished from failed operations;
- the maximum retained partial data;
- why retention cannot be misinterpreted as a terminal network outcome.

## Versioning and Extension

<a id="REQ-RESULT-0031"></a>

**REQ-RESULT-0031:**

The envelope and test payloads evolve explicitly:

- `schema_version` versions common fields and execution semantics;
- `test.version` versions measurement behavior;
- `test.result_version` versions the test-specific Output object;
- new adopted tests receive a registered test ID and result schema;
- shared observation types can be reused without copying raw protocol data.

<a id="REQ-RESULT-0032"></a>

**REQ-RESULT-0032:**

Unknown fields are rejected within a known version. Unsupported schema, test, or result versions must not be interpreted best-effort as a known format. A receiver may retain the opaque bounded object in a quarantine path, but it must not silently discard unknown fields and analyze the remainder.

<a id="REQ-RESULT-0033"></a>

**REQ-RESULT-0033:**

The initial format has no arbitrary annotations or extension map. A future extension mechanism requires a new envelope version, registered names, explicit field bounds, and privacy and safety review. Tasks and host applications must not inject result extensions.

## Validation

<a id="REQ-RESULT-0034"></a>

**REQ-RESULT-0034:**

- All required fields and conditional relationships must hold.

<a id="REQ-RESULT-0036"></a>

**REQ-RESULT-0036:**

- `run_id` must decode to exactly 128 bits and must not be all zeroes.

<a id="REQ-RESULT-0037"></a>

**REQ-RESULT-0037:**

- `attempt` must not exceed the accepted task retry bound.

<a id="REQ-RESULT-0038"></a>

**REQ-RESULT-0038:**

- Test and result versions must be supported as an exact registered combination.

<a id="REQ-RESULT-0039"></a>

**REQ-RESULT-0039:**

- `started_at` seconds must be `00` and the timezone must be `Z`.

<a id="REQ-RESULT-0040"></a>

**REQ-RESULT-0040:**

- Durations must use the registered quantization and remain within the execution bound, except when `duration_capped` is present.

<a id="REQ-RESULT-0041"></a>

**REQ-RESULT-0041:**

- Completed results must contain a valid terminal measurement outcome.

<a id="REQ-RESULT-0042"></a>

**REQ-RESULT-0042:**

- Incomplete and not-run results must contain an allowed execution reason.

<a id="REQ-RESULT-0043"></a>

**REQ-RESULT-0043:**

- Every observation must comply with the selected test result schema.

<a id="REQ-RESULT-0044"></a>

**REQ-RESULT-0044:**

- Unknown fields, raw platform errors, and prohibited data invalidate the result before bundling.

## Privacy, Safety, and Interpretation

<a id="REQ-RESULT-0035"></a>

**REQ-RESULT-0035:**

- Results must contain no person, account, application-user, advertising, device, SIM, subscriber, push, or stable installation identifier.

<a id="REQ-RESULT-0045"></a>

**REQ-RESULT-0045:**

- Task inputs and labels are not copied automatically.

<a id="REQ-RESULT-0046"></a>

**REQ-RESULT-0046:**

- Results must not retain raw packets, HTTP bodies, HTTP header values, certificate chains, cookies, credentials, system logs, stack traces, or unrelated resolver state.

<a id="REQ-RESULT-0047"></a>

**REQ-RESULT-0047:**

- Coarse platform, time, Network Context, connection code, task, and run metadata can become identifying in combination and require bounded retention and aggregate reporting.

<a id="REQ-RESULT-0048"></a>

**REQ-RESULT-0048:**

- A matching task or run identifier establishes only measurement workflow membership, not that results belong to one person.

<a id="REQ-RESULT-0049"></a>

**REQ-RESULT-0049:**

- A completed negative outcome is one observation on one path and context. It does not prove censorship or identify intent.

<a id="REQ-RESULT-0050"></a>

**REQ-RESULT-0050:**

- Derived anomaly or interference analysis must remain separate from this source result, identify its method and version, and preserve links to the source observations.
