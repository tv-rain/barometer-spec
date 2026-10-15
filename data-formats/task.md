# Task Description Format

**Status:** Draft  
**Version:** 0.1.0

Runtime JSON values follow the shared [strict decoding contract](json-decoding.md) in addition to this document's schema, limits, and validation rules.

## Overview

A **Task** is a concrete instruction sent to a probe to execute a specific measurement.

A task references a registered measurement (`test_id`) and provides the input, execution constraints, scheduling policy, and safety requirements needed to perform one or more measurement runs.

<a id="REQ-TASK-0002"></a>

**REQ-TASK-0002:**

A task does not contain measurement results. Results are produced separately after execution.

Task provenance, issuer authorization, replay protection, target registration, and local-policy lifecycle are defined in [`library/task-trust.md`](../library/task-trust.md). Numeric bounds are defined in [`library/registered-limits.md`](../library/registered-limits.md).

## JSON Structure

```json
{
  "schema_version": "0.1.0",
  "task_id": "network-state-baseline",
  "test_id": "NET-01",
  "test_version": "0.1.0",
  "input": {},
  "options": {},
  "schedule": {
    "not_after": "2026-07-30T00:00:00Z",
    "repeat": {
      "mode": "none"
    },
    "limits": {
      "max_runs": 1
    }
  },
  "execution": {
    "limits": {
      "max_duration_ms": 30000
    }
  },
  "safety": {
    "risk_level": "low",
    "requires_user_consent": false
  },
  "labels": {
    "campaign": "network-state-baseline"
  }
}
```

# Top-level Fields

<a id="REQ-TASK-0003"></a>

**REQ-TASK-0003:**

| Field | Required | Description |
|--------|----------|-------------|
| `schema_version` | Yes | Version of the Task schema. |
| `task_id` | Yes | Campaign-scoped, non-user-specific identifier unique within the authenticated issuer namespace. |
| `test_id` | Yes | Identifier of the registered measurement to execute. |
| `test_version` | Yes | Version of the measurement implementation expected by the scheduler. |
| [`input`](task-input.md) | Yes | Test-specific measurement subject, validated against the test's input schema. |
| [`options`](task-options.md) | Yes | Test-specific configuration interpreted by the test implementation. |
| [`schedule`](task-schedule.md) | Yes | Scheduling policy describing when and how often the task should execute. |
| [`execution`](task-execution.md) | Yes | Execution constraints applied to every measurement run. |
| [`safety`](task-safety.md) | Yes | Declares task risk and consent requirements evaluated before execution. |
| [`labels`](task-labels.md) | No | Bounded metadata used for grouping, filtering, or analytics. |

<a id="REQ-TASK-0001"></a>

**REQ-TASK-0001:**

Unknown top-level fields are rejected.

<a id="REQ-TASK-0004"></a>

**REQ-TASK-0004:**

`task_id` is 1–128 bytes matching `^[a-z0-9][a-z0-9._-]{0,127}$`. It must be identical for every installation receiving the same task definition and must not contain or derive from a person, account, installation, device, advertising ID, push token, linkage token, IP address, or other participant-specific value.

<a id="REQ-TASK-0005"></a>

**REQ-TASK-0005:**

The complete serialized task must not exceed 65,536 UTF-8 bytes.

## Design Principles

### Stable Structure

<a id="REQ-TASK-0006"></a>

**REQ-TASK-0006:**

The top-level schema should change rarely. Most future extensions should be added inside nested objects instead of introducing new top-level fields.
