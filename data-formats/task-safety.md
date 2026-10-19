# Safety Format

**Status:** Draft  
**Version:** 0.1.0

Runtime JSON values follow the shared [strict decoding contract](json-decoding.md) in addition to this document's schema, limits, and validation rules.

The `safety` object declares the user risks associated with a configured task and whether the task requires explicit user consent.

<a id="REQ-SAFETY-0001"></a>

**REQ-SAFETY-0001:**

Safety declarations are evaluated before every execution attempt. They provide input to the probe's local safety policy but do not authorize execution by themselves.

<a id="REQ-SAFETY-0002"></a>

**REQ-SAFETY-0002:**

The probe always retains final authority to delay, skip, or reject a task.

<a id="REQ-SAFETY-0003"></a>

**REQ-SAFETY-0003:**

The declaration is untrusted task input. Task provenance, issuer authorization, target registration, and policy lifecycle are defined in [`Task Trust and Local Policy`](../library/task-trust.md).

## Safety Model

<a id="REQ-SAFETY-0004"></a>

**REQ-SAFETY-0004:**

A measurement has a baseline risk defined by its registered test.

<a id="REQ-SAFETY-0005"></a>

**REQ-SAFETY-0005:**

A task may introduce additional risk through its inputs, options, schedule, or deployment context. The task's safety declaration must describe the risk of the configured task and must never reduce the registered test's baseline risk.

<a id="REQ-SAFETY-0006"></a>

**REQ-SAFETY-0006:**

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

<a id="REQ-SAFETY-0007"></a>

**REQ-SAFETY-0007:**

| Field | Required | Description |
|---|:---:|---|
| `risk_level` | Yes | Overall user-risk classification for the configured task. |
| `risk_factors` | Conditional | Structured factors contributing to the overall risk level. |
| `requires_user_consent` | Yes | Whether the task requires explicit user consent before execution. |

## Risk Level

`risk_level` describes the overall potential risk to the user if the configured task is executed.

Supported values:

<a id="REQ-SAFETY-0008"></a>

**REQ-SAFETY-0008:**

| Value | Description |
|---|---|
| `low` | Execution presents limited known risk under the assessed deployment assumptions. |
| `medium` | Execution presents meaningful risk that requires additional local evaluation or safeguards. |
| `high` | Execution may expose the user to serious harm and should normally be rejected unless explicitly permitted by a reviewed local policy. |
| `unknown` | Risk has not been adequately evaluated. |

<a id="REQ-SAFETY-0009"></a>

**REQ-SAFETY-0009:**

There is no `none` value. Network measurement must never be represented as risk-free.

<a id="REQ-SAFETY-0010"></a>

**REQ-SAFETY-0010:**

`unknown` must fail closed by default. A task with unknown risk may run only when an explicit, reviewed local policy permits it.

<a id="REQ-SAFETY-0011"></a>

**REQ-SAFETY-0011:**

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

<a id="REQ-SAFETY-0012"></a>

**REQ-SAFETY-0012:**

`risk_factors` is required when `risk_level` is `medium`, `high`, or `unknown`. It may be omitted for a `low`-risk task.

<a id="REQ-SAFETY-0031"></a>

**REQ-SAFETY-0031:**

When `risk_level` is `medium`, `high`, or `unknown`, `risk_factors` must contain at least one risk factor. An empty array does not satisfy this requirement, and the task must be rejected.

### Risk Factor Fields

<a id="REQ-SAFETY-0013"></a>

**REQ-SAFETY-0013:**

| Field | Required | Description |
|---|:---:|---|
| `type` | Yes | Category of user risk. |
| `level` | Yes | Risk level for this factor. |

<a id="REQ-SAFETY-0014"></a>

**REQ-SAFETY-0014:**

Factor `level` supports the same values as the overall `risk_level`: `low`, `medium`, `high`, and `unknown`.

### Initial Risk Factor Types

<a id="REQ-SAFETY-0015"></a>

**REQ-SAFETY-0015:**

| Type | Description |
|---|---|
| `network_observability` | Risk that network operators or intermediaries can observe the measurement activity. |
| `traffic_distinctiveness` | Risk that measurement traffic is distinguishable from ordinary application traffic. |
| `target_sensitivity` | Risk associated with contacting the configured measurement target. |
| `data_sensitivity` | Risk associated with data produced or retained by the measurement. |
| `legal_or_social_context` | Known potential for legal, social, or personal harm in the deployment context. |

<a id="REQ-SAFETY-0016"></a>

**REQ-SAFETY-0016:**

Bandwidth, battery, runtime, network availability, and device-state requirements belong in the [`execution`](task-execution.md) object rather than `safety`.

<a id="REQ-SAFETY-0017"></a>

**REQ-SAFETY-0017:**

An implementation receiving an unknown factor type must not silently ignore it. It must reject the task as unsupported or conservatively treat its safety risk as `unknown`.

### Risk Consistency

<a id="REQ-SAFETY-0018"></a>

**REQ-SAFETY-0018:**

The overall `risk_level` must be at least as restrictive as every known risk factor.

```text
low < medium < high
```

For example, a task containing a `high` risk factor cannot declare an overall risk level of `low` or `medium`.

<a id="REQ-SAFETY-0019"></a>

**REQ-SAFETY-0019:**

`unknown` is not lower or higher than the other levels. If any factor is `unknown`, the overall risk level must be `unknown` unless the probe can resolve the factor through a trusted local safety assessment.

## User Consent

`requires_user_consent` declares whether the task imposes an explicit user-consent requirement.

```json
{
  "requires_user_consent": true
}
```

<a id="REQ-SAFETY-0020"></a>

**REQ-SAFETY-0020:**

When `requires_user_consent` is `true`, the probe must not execute the task unless the host application can establish that valid consent covers the measurement.

Those requirements belong to the host application's consent and safety policy.

<a id="REQ-SAFETY-0021"></a>

**REQ-SAFETY-0021:**

When `requires_user_consent` is `false`, the field means only that the task adds no explicit consent requirement.

<a id="REQ-SAFETY-0022"></a>

**REQ-SAFETY-0022:**

The host application or local policy may require consent regardless of the task value.

## Effective Risk

<a id="REQ-SAFETY-0023"></a>

**REQ-SAFETY-0023:**

The probe must determine the effective risk using all available trusted inputs:

```text
effective risk = most restrictive of:
    registered test risk
    task-declared risk
    locally determined risk
```

<a id="REQ-SAFETY-0024"></a>

**REQ-SAFETY-0024:**

The task-declared `risk_level` must never lower the baseline risk registered for `test_id`.

<a id="REQ-SAFETY-0025"></a>

**REQ-SAFETY-0025:**

For example, if a registered test has a baseline risk of `medium`, a task declaring `low` must be rejected as invalid or evaluated as at least `medium`.

<a id="REQ-SAFETY-0026"></a>

**REQ-SAFETY-0026:**

A task may declare a higher risk than the registered baseline when its inputs, options, frequency, targets, or deployment context increase potential harm.

## Safety Evaluation

<a id="REQ-SAFETY-0027"></a>

**REQ-SAFETY-0027:**

An execution attempt may start only when all applicable safety conditions are satisfied:

```text
safety declaration is valid
AND all risk factors are supported
AND effective risk is permitted by local policy
AND required consent is valid
AND host and device safety restrictions permit execution
```

<a id="REQ-SAFETY-0028"></a>

**REQ-SAFETY-0028:**

The task cannot weaken local privacy, consent, or safety requirements.

<a id="REQ-SAFETY-0029"></a>

**REQ-SAFETY-0029:**

If safety cannot be evaluated reliably, the probe should fail closed and must not treat missing information as evidence that execution is safe.

<a id="REQ-SAFETY-0030"></a>

**REQ-SAFETY-0030:**

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
