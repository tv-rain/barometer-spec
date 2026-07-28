# Schedule Format

**Status:** Draft  
**Version:** 0.1.0

The `schedule` object defines when a task becomes eligible for execution, when repeated runs become due, and how execution failures may be retried.

Scheduling does not guarantee exact execution time. Mobile operating systems, application lifecycle, network availability, battery state, and local safety policies may delay or prevent execution.

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

| Field | Required | Description |
|---|---:|---|
| `starts_at` | No | Earliest timestamp at which the first run may start. |
| `not_after` | Conditional | Timestamp after which no new run or retry attempt may start; required for every remote task and every repeated task. |
| `time_window` | No | Local time periods during which runs may start. |
| `repeat` | No | Defines whether and when additional runs become due; omitted value is `none`. |
| `retry` | No | Defines retry behavior for execution failures; omitted value permits one attempt only. |
| `limits` | No | Defines task expiration and maximum number of runs. |

## Scheduling Model

A schedule creates one or more measurement runs.

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

Repetition creates new runs.

Retry creates additional attempts for an existing run.

### Start Time

The `starts_at` field defines the earliest time at which the task becomes eligible for execution.

```json
{
  "starts_at": "2026-07-24T12:00:00Z"
}
```

`starts_at` does not require execution at the exact specified time.

When `starts_at` is `null` or omitted, the task becomes eligible immediately after it is accepted by the probe.

### Time Limit

`not_after` is an overall task expiration timestamp. It is different from `time_window`, which defines recurring allowed hours within the task lifetime.

Every remote task requires `not_after`. It must be later than task acceptance and no more than 604,800 seconds (1 week) after authenticated issuance or acceptance, whichever is earlier. An embedded one-time task may omit it only under the exception defined by the registered limits.

### Time Window

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

| Field | Required | Description |
|---|---:|---|
| `timezone` | No | Timezone used to interpret the ranges, `local` is default. |
| `ranges` | Yes | 1–4 allowed, unique, non-overlapping time ranges. |

`local` means the current timezone reported by the device.

#### Range Fields

| Field | Required | Description |
|---|---:|---|
| `start` | Yes | Beginning of the allowed local time range, inclusive. |
| `end` | Yes | End of the allowed local time range, exclusive. |

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

When `end` is earlier than `start`, the range crosses midnight.

A task may define multiple allowed ranges:

### Repeat

The `repeat` object defines whether additional measurement runs become due.

Supported modes in the initial version:

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

| Field | Required | Description |
|---|---:|---|
| `mode` | Yes | Must be `interval`. |
| `interval` | Yes | Integer from 21,600 through 604,800 seconds between scheduled runs. |
| `jitter` | Yes for `interval` | Integer from 300 through the lesser of 1,800 seconds or one quarter of `interval`. |

A repeated run becomes due according to the interval, but it may start later because of execution constraints or time-window restrictions.

Jitter is generated locally from a cryptographically secure or platform-approved random source independently for each due run. A task source cannot select the realized offset. Jitter must not move a run before `starts_at`, after `not_after`, or outside an allowed time window.

### Retry

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

`max_attempts` includes the initial attempt and is an integer from 1 through 2.

Retries belong to the same run and do not count toward `max_runs`.

A measurement outcome must not automatically be treated as an execution failure. For example, DNS failure, TCP timeout, or TLS failure may be valid measurement results.

#### Retry Fields

| Field | Required | Constraints | Description |
|---|:---:|---|---|
| `max_attempts` | Yes | Integer `1` or `2`. | Total attempts including the initial attempt. |
| `retry_on` | Conditional | Required and non-empty when `max_attempts` is `2`; unique registered values. | Cross-cutting execution reasons eligible for retry. |
| `backoff` | Conditional | Required when `max_attempts` is `2`. | Bounded delay before the second attempt. |

Initial `retry_on` values are `platform_suspended`, `network_context_unavailable`, `proxy_unavailable`, and `internal_error`. Measurement outcomes, `cancelled_by_host`, policy rejection, unsatisfied constraints, proxy reconfiguration, and attempt resource limits are not retryable in version `0.1.0`.

The `backoff` object fields are:

| Field | Required | Constraints |
|---|:---:|---|
| `mode` | Yes | `fixed` or `exponential`; with at most two attempts both produce one bounded delay. |
| `initial_delay_ms` | Yes | Integer from 30,000 through 300,000. |
| `multiplier` | Conditional | Required and exactly `2` for `exponential`; prohibited for `fixed`. |
| `max_delay_ms` | Yes | Integer from `initial_delay_ms` through 600,000. |
| `jitter_ms` | No | Integer from 0 through 60,000; default 10,000. |

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

| Field | Required | Description |
|---|---:|---|
| `max_runs` | No | Integer from 1 through 28; default 1. Required when `repeat.mode` is `interval`. |

Retries do not count toward `max_runs`.

When multiple limits are configured, the first limit reached terminates the schedule.

## Validation

- Unknown schedule, time-window, range, repeat, retry, backoff, and limit fields are rejected.
- All timestamps use RFC 3339 UTC and `starts_at` must be earlier than `not_after`.
- Time ranges must be unique and non-overlapping after midnight expansion.
- `repeat.mode` defaults to `none`; interval-only fields are rejected for `none`.
- Repeated tasks require bounded expiry, `max_runs`, and jitter.
- Retry fields must satisfy the registered relationships and values.
- Exact redelivery must not create another schedule or extend the accepted expiry.
- Invalid or expired schedules are task-admission failures, not Measurement Results.

### Eligibility Rules

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
