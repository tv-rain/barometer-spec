# Schedule Format

**Status:** Draft  
**Version:** 0.1.0

Runtime JSON values follow the shared [strict decoding contract](json-decoding.md) in addition to this document's schema, limits, and validation rules.

The `schedule` object defines when a task becomes eligible for execution, when repeated runs become due, and how execution failures may be retried.

Scheduling does not guarantee exact execution time. Mobile operating systems, application lifecycle, network availability, battery state, and local safety policies may delay or prevent execution.

<a id="REQ-SCHEDULE-0001"></a>

**REQ-SCHEDULE-0001:**

The probe must treat scheduled times as eligibility constraints rather than exact execution deadlines.

Schedule defaults and maxima are defined in [`Registered Initial Limits`](../library/registered-limits.md#schedule-and-retry-limits).

## JSON Structure

```json
{
  "schedule": {
    "not_after": "2026-07-30T00:00:00Z",
    "repeat": {
      "mode": "none"
    },
    "limits": {
      "max_runs": 1
    }
  }
}
```

## Fields

<a id="REQ-SCHEDULE-0002"></a>

**REQ-SCHEDULE-0002:**

| Field | Required | Description |
|---|---:|---|
| `starts_at` | No | Earliest timestamp at which the first run may start. |
| `not_after` | Conditional | Timestamp after which no new run or retry attempt may start; required for every remote task and every repeated task. |
| `time_window` | No | Local time periods during which runs may start. |
| `repeat` | No | Defines whether and when additional runs become due; omitted value is `none`. |
| `retry` | No | Defines retry behavior for execution failures; omitted value permits one attempt only. |
| `limits` | No | Defines task expiration and maximum number of runs. |

## Scheduling Model

<a id="REQ-SCHEDULE-0003"></a>

**REQ-SCHEDULE-0003:**

A schedule creates one or more measurement runs.

<a id="REQ-SCHEDULE-0004"></a>

**REQ-SCHEDULE-0004:**

Each run may contain multiple execution attempts.

```text
Task
 ├── Run #1
 │    ├── Attempt #1
 │    └── Attempt #2
 ├── Run #2
 │    └── Attempt #1
 └── Run #3
      ├── Attempt #1
      └── Attempt #2
```

<a id="REQ-SCHEDULE-0005"></a>

**REQ-SCHEDULE-0005:**

Repetition creates new runs.

<a id="REQ-SCHEDULE-0006"></a>

**REQ-SCHEDULE-0006:**

Retry creates additional attempts for an existing run.

### Start Time

<a id="REQ-SCHEDULE-0007"></a>

**REQ-SCHEDULE-0007:**

The `starts_at` field defines the earliest time at which the task becomes eligible for execution.

```json
{
  "starts_at": "2026-07-24T12:00:00Z"
}
```

<a id="REQ-SCHEDULE-0008"></a>

**REQ-SCHEDULE-0008:**

`starts_at` does not require execution at the exact specified time.

<a id="REQ-SCHEDULE-0009"></a>

**REQ-SCHEDULE-0009:**

When `starts_at` is `null` or omitted, the task becomes eligible immediately after it is accepted by the probe.

### Time Limit

<a id="REQ-SCHEDULE-0010"></a>

**REQ-SCHEDULE-0010:**

`not_after` is an overall task expiration timestamp. It is different from `time_window`, which defines recurring allowed hours within the task lifetime.

<a id="REQ-SCHEDULE-0011"></a>

**REQ-SCHEDULE-0011:**

Every remote task requires `not_after`. It must be later than task acceptance and no more than 604,800 seconds (1 week) after authenticated issuance or acceptance, whichever is earlier. An embedded one-time task may omit it only under the exception defined by the registered limits.

### Time Window

<a id="REQ-SCHEDULE-0012"></a>

**REQ-SCHEDULE-0012:**

The `time_window` object restricts run starts to specified local time ranges.

```json
{
  "time_window": {
    "timezone": "local",
    "ranges": [
      {
        "start": "12:00",
        "end": "18:00"
      }
    ]
  }
}
```

#### Fields

<a id="REQ-SCHEDULE-0013"></a>

**REQ-SCHEDULE-0013:**

| Field | Required | Description |
|---|---:|---|
| `timezone` | No | Timezone used to interpret the ranges, `local` is default. |
| `ranges` | Yes | 1–4 allowed, unique, non-overlapping time ranges. |

<a id="REQ-SCHEDULE-0014"></a>

**REQ-SCHEDULE-0014:**

`local` means the current timezone reported by the device.

<a id="REQ-SCHEDULE-0043"></a>

**REQ-SCHEDULE-0043:**

In this version, `local` is the only defined `timezone` value. A task containing any other `timezone` value must be rejected.

#### Range Fields

<a id="REQ-SCHEDULE-0015"></a>

**REQ-SCHEDULE-0015:**

| Field | Required | Description |
|---|---:|---|
| `start` | Yes | Beginning of the allowed local time range, inclusive. |
| `end` | Yes | End of the allowed local time range, exclusive. |

<a id="REQ-SCHEDULE-0016"></a>

**REQ-SCHEDULE-0016:**

Times use the 24-hour `HH:mm` format.

Example daytime window:

```json
{
  "time_window": {
    "timezone": "local",
    "ranges": [
      {
        "start": "08:00",
        "end": "20:00"
      }
    ]
  }
}
```

Example nighttime window:

```json
{
  "time_window": {
    "timezone": "local",
    "ranges": [
      {
        "start": "22:00",
        "end": "06:00"
      }
    ]
  }
}
```

<a id="REQ-SCHEDULE-0017"></a>

**REQ-SCHEDULE-0017:**

When `end` is earlier than `start`, the range crosses midnight.

A task may define multiple allowed ranges:

### Repeat

The `repeat` object defines whether additional measurement runs become due.

Supported modes in the initial version:

<a id="REQ-SCHEDULE-0018"></a>

**REQ-SCHEDULE-0018:**

| Mode | Description |
|---|---|
| `none` | Create one run only. |
| `interval` | Create runs at a configured interval. |

One-time task:

```json
{
  "repeat": {
    "mode": "none"
  }
}
```

Repeating task:

```json
{
  "repeat": {
    "mode": "interval",
    "interval": 21600,
    "jitter": 1800
  }
}
```

#### Interval Fields

<a id="REQ-SCHEDULE-0019"></a>

**REQ-SCHEDULE-0019:**

| Field | Required | Description |
|---|---:|---|
| `mode` | Yes | Must be `interval`. |
| `interval` | Yes | Integer from 21,600 through 604,800 seconds between scheduled runs. |
| `jitter` | Yes for `interval` | Integer from 300 through the lesser of 1,800 seconds or one quarter of `interval`. |

<a id="REQ-SCHEDULE-0020"></a>

**REQ-SCHEDULE-0020:**

A repeated run becomes due according to the interval, but it may start later because of execution constraints or time-window restrictions.

<a id="REQ-SCHEDULE-0021"></a>

**REQ-SCHEDULE-0021:**

Jitter is generated locally from a cryptographically secure or platform-approved random source independently for each due run. A task source cannot select the realized offset. Jitter must not move a run before `starts_at`, after `not_after`, or outside an allowed time window.

### Retry

<a id="REQ-SCHEDULE-0022"></a>

**REQ-SCHEDULE-0022:**

The `retry` object defines additional attempts for execution failures.

```json
{
  "retry": {
    "max_attempts": 2,
    "retry_on": [
      "platform_suspended",
      "internal_error"
    ],
    "backoff": {
      "mode": "exponential",
      "initial_delay_ms": 30000,
      "multiplier": 2,
      "max_delay_ms": 600000,
      "jitter_ms": 10000
    }
  }
}
```

<a id="REQ-SCHEDULE-0023"></a>

**REQ-SCHEDULE-0023:**

`max_attempts` includes the initial attempt and is an integer from 1 through 2.

<a id="REQ-SCHEDULE-0024"></a>

**REQ-SCHEDULE-0024:**

Retries belong to the same run and do not count toward `max_runs`.

<a id="REQ-SCHEDULE-0025"></a>

**REQ-SCHEDULE-0025:**

A measurement outcome must not automatically be treated as an execution failure. For example, DNS failure, TCP timeout, or TLS failure may be valid measurement results.

#### Retry Fields

<a id="REQ-SCHEDULE-0026"></a>

**REQ-SCHEDULE-0026:**

| Field | Required | Constraints | Description |
|---|:---:|---|---|
| `max_attempts` | Yes | Integer `1` or `2`. | Total attempts including the initial attempt. |
| `retry_on` | Conditional | Required and non-empty when `max_attempts` is `2`; unique registered values. | Cross-cutting execution reasons eligible for retry. |
| `backoff` | Conditional | Required when `max_attempts` is `2`. | Bounded delay before the second attempt. |

<a id="REQ-SCHEDULE-0027"></a>

**REQ-SCHEDULE-0027:**

Initial `retry_on` values are `platform_suspended`, `network_context_unavailable`, `proxy_unavailable`, and `internal_error`. Measurement outcomes, `cancelled_by_host`, policy rejection, unsatisfied constraints, proxy reconfiguration, and attempt resource limits are not retryable in version `0.1.0`.

The `backoff` object fields are:

<a id="REQ-SCHEDULE-0028"></a>

**REQ-SCHEDULE-0028:**

| Field | Required | Constraints |
|---|:---:|---|
| `mode` | Yes | `fixed` or `exponential`; with at most two attempts both produce one bounded delay. |
| `initial_delay_ms` | Yes | Integer from 30,000 through 300,000. |
| `multiplier` | Conditional | Required and exactly `2` for `exponential`; prohibited for `fixed`. |
| `max_delay_ms` | Yes | Integer from `initial_delay_ms` through 600,000. |
| `jitter_ms` | No | Integer from 0 through 60,000; default 10,000. |

<a id="REQ-SCHEDULE-0029"></a>

**REQ-SCHEDULE-0029:**

`retry_on` and `backoff` are prohibited when `max_attempts` is `1`. Retry jitter is generated locally; the realized delay including jitter must not exceed `max_delay_ms` or extend a retry beyond task expiry.

### Limits

The `limits` object defines the overall lifetime of the schedule.

```json
{
  "limits": {
    "max_runs": 28
  }
}
```

#### Fields

<a id="REQ-SCHEDULE-0030"></a>

**REQ-SCHEDULE-0030:**

| Field | Required | Description |
|---|---:|---|
| `max_runs` | No | Integer from 1 through 28; default 1. Required when `repeat.mode` is `interval`. |

<a id="REQ-SCHEDULE-0031"></a>

**REQ-SCHEDULE-0031:**

Retries do not count toward `max_runs`.

<a id="REQ-SCHEDULE-0032"></a>

**REQ-SCHEDULE-0032:**

When multiple limits are configured, the first limit reached terminates the schedule.

## Validation

<a id="REQ-SCHEDULE-0033"></a>

**REQ-SCHEDULE-0033:**

- Unknown schedule, time-window, range, repeat, retry, backoff, and limit fields are rejected.

<a id="REQ-SCHEDULE-0036"></a>

**REQ-SCHEDULE-0036:**

- All timestamps use RFC 3339 UTC and `starts_at` must be earlier than `not_after`.

<a id="REQ-SCHEDULE-0037"></a>

**REQ-SCHEDULE-0037:**

- Time ranges must be unique and non-overlapping after midnight expansion.

<a id="REQ-SCHEDULE-0038"></a>

**REQ-SCHEDULE-0038:**

- `repeat.mode` defaults to `none`; interval-only fields are rejected for `none`.

<a id="REQ-SCHEDULE-0039"></a>

**REQ-SCHEDULE-0039:**

- Repeated tasks require bounded expiry, `max_runs`, and jitter.

<a id="REQ-SCHEDULE-0040"></a>

**REQ-SCHEDULE-0040:**

- Retry fields must satisfy the registered relationships and values.

<a id="REQ-SCHEDULE-0041"></a>

**REQ-SCHEDULE-0041:**

- Exact redelivery must not create another schedule or extend the accepted expiry.

<a id="REQ-SCHEDULE-0042"></a>

**REQ-SCHEDULE-0042:**

- Invalid or expired schedules are task-admission failures, not Measurement Results.

### Eligibility Rules

<a id="REQ-SCHEDULE-0034"></a>

**REQ-SCHEDULE-0034:**

A run or retry attempt may start only when all applicable conditions are satisfied:

```text
task is supported
AND current time >= starts_at
AND current time < not_after
AND current time is inside time_window
AND max_runs has not been reached
AND execution constraints are satisfied
AND safety requirements are satisfied
```

<a id="REQ-SCHEDULE-0035"></a>

**REQ-SCHEDULE-0035:**

The scheduler expresses eligibility, but the probe retains final authority to delay, skip, or reject execution.

### Complete Example

```json
{
  "schedule": {
    "starts_at": "2026-07-24T00:00:00Z",
	"not_after": "2026-07-30T00:00:00Z",

    "time_window": {
      "timezone": "local",
      "ranges": [
        {
          "start": "22:00",
          "end": "06:00"
        }
      ]
    },

    "repeat": {
      "mode": "interval",
      "interval": 21600,
      "jitter": 1800
    },

    "retry": {
      "max_attempts": 2,
      "retry_on": [
        "platform_suspended",
        "internal_error"
      ],
      "backoff": {
        "mode": "exponential",
        "initial_delay_ms": 30000,
        "multiplier": 2,
        "max_delay_ms": 600000,
        "jitter_ms": 10000
      }
    },

    "limits": {
      "max_runs": 28
    }
  }
}
```
