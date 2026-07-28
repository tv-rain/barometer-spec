# Safety Format

**Status:** Draft  
**Version:** 0.1.0

The `safety` object declares the user risks associated with a configured task and whether the task requires explicit user consent.

Safety declarations are evaluated before every execution attempt. They provide input to the probe's local safety policy but do not authorize execution by themselves.

The probe always retains final authority to delay, skip, or reject a task.

The declaration is untrusted task input. Task provenance, issuer authorization, target registration, and policy lifecycle are defined in [`Task Trust and Local Policy`](../library/task-trust.md).

## Safety Model

A measurement has a baseline risk defined by its registered test.

A task may introduce additional risk through its inputs, options, schedule, or deployment context. The task's safety declaration must describe the risk of the configured task and must never reduce the registered test's baseline risk.

Safety evaluation does not create new runs or execution attempts.

## JSON Structure

```json
{
  "safety": {
    "risk_level": "medium",
    "risk_factors": [
      {
        "type": "traffic_distinctiveness",
        "level": "medium"
      },
      {
        "type": "target_sensitivity",
        "level": "low"
      }
    ],
    "requires_user_consent": true
  }
}
```

## Fields

| Field | Required | Description |
|---|:---:|---|
| `risk_level` | Yes | Overall user-risk classification for the configured task. |
| `risk_factors` | Conditional | Structured factors contributing to the overall risk level. |
| `requires_user_consent` | Yes | Whether the task requires explicit user consent before execution. |

## Risk Level

`risk_level` describes the overall potential risk to the user if the configured task is executed.

Supported values:

| Value | Description |
|---|---|
| `low` | Execution presents limited known risk under the assessed deployment assumptions. |
| `medium` | Execution presents meaningful risk that requires additional local evaluation or safeguards. |
| `high` | Execution may expose the user to serious harm and should normally be rejected unless explicitly permitted by a reviewed local policy. |
| `unknown` | Risk has not been adequately evaluated. |

There is no `none` value. Network measurement must never be represented as risk-free.

`unknown` must fail closed by default. A task with unknown risk may run only when an explicit, reviewed local policy permits it.

Risk levels are conservative classifications, not guarantees. A `low` risk level does not mean that execution is safe in every environment.

## Risk Factors

`risk_factors` provides a machine-readable explanation of the conditions contributing to the overall risk level.

```json
{
  "risk_factors": [
    {
      "type": "network_observability",
      "level": "low"
    },
    {
      "type": "traffic_distinctiveness",
      "level": "medium"
    }
  ]
}
```

`risk_factors` is required when `risk_level` is `medium`, `high`, or `unknown`. It may be omitted for a `low`-risk task.

### Risk Factor Fields

| Field | Required | Description |
|---|:---:|---|
| `type` | Yes | Category of user risk. |
| `level` | Yes | Risk level for this factor. |

Factor `level` supports the same values as the overall `risk_level`: `low`, `medium`, `high`, and `unknown`.

### Initial Risk Factor Types

| Type | Description |
|---|---|
| `network_observability` | Risk that network operators or intermediaries can observe the measurement activity. |
| `traffic_distinctiveness` | Risk that measurement traffic is distinguishable from ordinary application traffic. |
| `target_sensitivity` | Risk associated with contacting the configured measurement target. |
| `data_sensitivity` | Risk associated with data produced or retained by the measurement. |
| `legal_or_social_context` | Known potential for legal, social, or personal harm in the deployment context. |

Bandwidth, battery, runtime, network availability, and device-state requirements belong in the [`execution`](task-execution.md) object rather than `safety`.

An implementation receiving an unknown factor type must not silently ignore it. It must reject the task as unsupported or conservatively treat its safety risk as `unknown`.

### Risk Consistency

The overall `risk_level` must be at least as restrictive as every known risk factor.

```text
low < medium < high
```

For example, a task containing a `high` risk factor cannot declare an overall risk level of `low` or `medium`.

`unknown` is not lower or higher than the other levels. If any factor is `unknown`, the overall risk level must be `unknown` unless the probe can resolve the factor through a trusted local safety assessment.

## User Consent

`requires_user_consent` declares whether the task imposes an explicit user-consent requirement.

```json
{
  "requires_user_consent": true
}
```

When `requires_user_consent` is `true`, the probe must not execute the task unless the host application can establish that valid consent covers the measurement.

Those requirements belong to the host application's consent and safety policy.

When `requires_user_consent` is `false`, the field means only that the task adds no explicit consent requirement.

The host application or local policy may require consent regardless of the task value.

## Effective Risk

The probe must determine the effective risk using all available trusted inputs:

```text
effective risk = most restrictive of:
    registered test risk
    task-declared risk
    locally determined risk
```

The task-declared `risk_level` must never lower the baseline risk registered for `test_id`.

For example, if a registered test has a baseline risk of `medium`, a task declaring `low` must be rejected as invalid or evaluated as at least `medium`.

A task may declare a higher risk than the registered baseline when its inputs, options, frequency, targets, or deployment context increase potential harm.

## Safety Evaluation

An execution attempt may start only when all applicable safety conditions are satisfied:

```text
safety declaration is valid
AND all risk factors are supported
AND effective risk is permitted by local policy
AND required consent is valid
AND host and device safety restrictions permit execution
```

The task cannot weaken local privacy, consent, or safety requirements.

If safety cannot be evaluated reliably, the probe should fail closed and must not treat missing information as evidence that execution is safe.

Safety rejection is not a measurement result and must not be interpreted as evidence of censorship.

## Complete Example

```json
{
  "safety": {
    "risk_level": "medium",
    "risk_factors": [
      {
        "type": "network_observability",
        "level": "low"
      },
      {
        "type": "traffic_distinctiveness",
        "level": "medium"
      },
      {
        "type": "target_sensitivity",
        "level": "medium"
      }
    ],
    "requires_user_consent": true
  }
}
```
