# `NET-05` Multi-endpoint reachability profile

**Status:** `Draft`
**Version:** `0.1.0`
**Category:** `Network state`

## Overview

This composite test executes a bounded, ordered list of registered DNS, TCP, TLS, and HTTPS primitive measurements defined by a `profile` object embedded in the task's `input`. It preserves the result of every step for later correlated analysis.

A test defines registered measurement behavior. A task references the test by `test_id` and supplies the measurement input, options, execution constraints, schedule, and task-specific safety requirements.

## Purpose

### Measurement Question

What results do the ordered primitive measurement steps produce on one stable network generation?

### Non-goals

- The test does not prove that an allowlist policy exists or identify who operates it.
- The first version does not classify the combined results as a broad restriction, allowlist, or censorship event.
- The test does not test sensitive, political, circumvention, or broad public website lists.
- The test does not replace outage, captive-portal, routing, or independent reference analysis.

## Measurement Method

### Target

One inline, versioned reachability profile supplied as task input. A profile contains one bounded, ordered list of primitive measurement steps. Every step defines its own measurement target through the referenced test's `input`.

### Operation

The probe validates the complete inline profile before making any connection, then executes its `DNS-01`, `TCP-01`, `TLS-01`, and `HTTP-01` steps sequentially in array order.

The outer NET-05 task controls scheduling, execution constraints, safety, and labels. A nested step contains only a primitive test reference, its input, and its options. It cannot contain its own schedule, execution envelope, safety declaration, or labels.

The probe uses `NET-01` to ensure a stable network and may use an available `NET-03` observation to retain validation or captive-portal context. Primitive outcomes remain separate. NET-05 does not derive a censorship or broad-restriction classification in this version.

### Procedure

1. Validate the complete profile structure, bounds, identifiers, primitive test versions, step inputs, and step options.
2. Determine the effective risk from NET-05, every referenced primitive test, the outer task declaration, and local policy. Stop before network execution if the profile is not permitted.
3. Confirm a stable network generation and obtain current `NET-01` context.
4. Obtain or reuse a sufficiently recent `NET-03` observation under local policy.
5. Execute primitive steps sequentially in array order, applying each primitive's registered behavior and bounds.
6. Stop immediately if the network changes, the outer execution limit is reached, or local safety policy withdraws permission.
7. Preserve every per-step observation and the overall completion state.

### Success Condition

The profile attempts all of its primitive operations on one stable network generation, subject to the outer execution envelope, and preserves each completed step result. An individual step may report an unreachable target without making the composite execution invalid.

### Failure Conditions

| Failure class | Required observation |
|---|---|
| `network_not_validated` | Required network validation is absent or indicates a captive portal. |
| `incomplete` | One or more steps cannot run or complete, while the outer execution attempt remains valid. |
| `network_changed` | The network generation changes during the composite run. |
| `resource_limit` | The outer execution bound is reached before required operations complete. |
| `completed` | All steps reach a terminal primitive result on one stable network generation. |
| `inconclusive` | The composite completion state cannot be determined safely. |

Primitive step failures remain primitive results. NET-05 must not translate them automatically into `broad_restriction_suspected`, `allowlist_detected`, or another censorship classification.

Profile validation failure and safety rejection occur before measurement execution. They are task or execution states, not evidence of censorship.

## Inputs

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `profile` | object | Yes | Must satisfy the complete bounded schema below. | Inline reachability profile executed by this task. |

The `profile` object contains:

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `profile_id` | string | Yes | Stable, non-identifying ASCII identifier of 1–64 bytes. | Correlates runs using the same measurement plan. |
| `profile_version` | integer | Yes | Positive and monotonically increasing for a given `profile_id`. | Distinguishes profile revisions. |
| `steps` | array of objects | Yes | 1–8 entries executed sequentially. | Ordered primitive measurements. |

Each `steps` entry contains:

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `step_id` | string | Yes | Unique within the profile; non-identifying ASCII identifier of 1–64 bytes. | Correlates the primitive result with this step. |
| `test_id` | string | Yes | `DNS-01`, `TCP-01`, `TLS-01`, or `HTTP-01` in this version. | Primitive test to execute. |
| `test_version` | string | Yes | Exact version supported by the probe. | Primitive behavior and schema version. |
| `input` | object | Yes | Must validate against the referenced primitive test. | Primitive measurement subject. |
| `options` | object | Yes | Must validate against the referenced primitive test. | Primitive test-specific behavior; `{}` is valid when supported. |

Example task input:

```json
{
  "profile": {
    "profile_id": "baseline-reachability",
    "profile_version": 1,
    "steps": [
      {
        "step_id": "dns-control",
        "test_id": "DNS-01",
        "test_version": "0.1.0",
        "input": {
          "hostname": "example.org",
          "record_type": "A"
        },
        "options": {}
      },
      {
        "step_id": "application-http",
        "test_id": "HTTP-01",
        "test_version": "0.1.0",
        "input": {
          "url": "https://example.org/health",
          "expected_status": 200
        },
        "options": {}
      },
      {
        "step_id": "external-control",
        "test_id": "HTTP-01",
        "test_version": "0.1.0",
        "input": {
          "url": "https://example.net/health",
          "expected_status": 200
        },
        "options": {}
      }
    ]
  }
}
```

The example identifiers, target, status, and version illustrate structure only. They are not registered defaults or approved production targets.

### Input Validation

- The complete profile must be present in `input`; external profile references and runtime downloads are not supported.
- The entire profile must validate before any primitive step executes. Partial acceptance is prohibited.
- Each target and primitive configuration must independently validate against its registered test version and local safety policy.
- `step_id` values must be unique within the profile.
- Nested `NET-05` steps and all unlisted test IDs are rejected.
- A step cannot contain `schedule`, `execution`, `safety`, `labels`, executable conditions, scripts, or runtime interpolation.
- Profiles containing credentials, user-specific URLs, sensitive content, local-network targets, unbounded lists, or runtime interpolation are rejected.
- Unknown fields are rejected.
- The encoded `profile` must not exceed 49,152 bytes.
- The declared primitive maxima must fit within 60,000 ms, 12 connections or tunnels, 65,536 application bytes sent, and 262,144 application bytes received.

Invalid input must prevent measurement execution and must not produce a measurement result that could be interpreted as network interference.

## Options

The initial version accepts an empty options object.

| Option | Type | Required | Default | Constraints | Description |
|---|---|:---:|---|---|---|
| — | — | — | — | Additional properties are rejected. | Target selection and operation order are defined by the inline profile. |

NET-05 has no composite-level options in this version. Step options remain inside the profile and cannot override the outer task execution envelope, primitive limits, local policy, operation order, or the no-retry rule.

## Preconditions

- The task source and inline profile must be trusted according to host policy, and every target must pass local privacy and safety evaluation.
- The test must be explicitly enabled by reviewed host policy or triggered by repeated baseline anomalies under that policy.
- The network must be stable, and validation or captive-portal context must be available.
- The outer execution envelope must accommodate the complete inline profile without weakening primitive limits.
- The test must not run when profile execution would produce an unusually dense, synchronized, or identifiable traffic pattern.

Task execution constraints and local probe policy may impose stricter preconditions.

## Resource Bounds

| Resource | Baseline limit | Behavior when reached |
|---|---|---|
| Duration | At most 60,000 ms, subject to stricter primitive and task bounds. | Stop remaining operations and classify the profile as incomplete. |
| Requests or connections | 1–8 steps and at most 12 aggregate connections or tunnels. | Never expand the target set or retry failed targets. |
| Data transferred | At most 65,536 application bytes sent and 262,144 received across all steps. | Stop remaining operations when the outer or primitive bound is reached. |
| Retries | None within the composite run. | Repetition requires a separately scheduled execution attempt. |
| Concurrency | Primitive operations execute sequentially; one profile run per network generation. | Delay or reject overlapping profile runs. |

The complete profile and every primitive must fit these registered limits before execution. Mobile validation may impose stricter limits but must not raise them.

## Output

The test uses Measurement Result `schema_version: 0.1.0` and `test.result_version: 0.1.0`.

NET-05 retains one outer Network Context and ordered primitive step results. It does not duplicate Network Context inside steps and does not derive a censorship, allowlist, anomaly, or broad-restriction classification.

Example partial result:

```json
{
  "outcome": "incomplete",
  "observations": [],
  "profile": {
    "profile_id": "baseline-reachability",
    "profile_version": 1
  },
  "network_validation": {
    "state": "validated",
    "source": "cached"
  },
  "steps": [
    {
      "step_id": "dns-control",
      "test": {
        "id": "DNS-01",
        "version": "0.1.0",
        "result_version": "0.1.0"
      },
      "state": "completed",
      "measurement": {
        "outcome": "resolved",
        "observations": [
          {
            "type": "dns_query",
            "status": "succeeded",
            "duration_ms": 250,
            "details": {
              "engine": "system",
              "query_type": "A",
              "responses": [
                {
                  "arrival_index": 1,
                  "arrival_offset_ms": 250,
                  "rcode": "NOERROR",
                  "answers": [
                    {
                      "type": "A",
                      "value": "1.1.1.1"
                    }
                  ]
                }
              ]
            }
          }
        ]
      }
    },
    {
      "step_id": "application-http",
      "test": {
        "id": "HTTP-01",
        "version": "0.1.0",
        "result_version": "0.1.0"
      },
      "state": "completed",
      "measurement": {
        "outcome": "tls_failure",
        "observations": [
          {
            "type": "tcp_connect",
            "status": "succeeded",
            "duration_ms": 500,
            "details": {
              "address_family": "ipv4"
            }
          },
          {
            "type": "tls_handshake",
            "status": "failed",
            "duration_ms": 500,
            "failure": "certificate_untrusted",
            "details": {
              "address_family": "ipv4",
              "certificate_validation": "untrusted"
            }
          }
        ]
      }
    }
  ],
  "stopped_before_step": "external-control"
}
```

For this partial example, the common envelope has `execution.state: incomplete` and the applicable common reason, such as `attempt_deadline_exceeded`.

### Additional Fields

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `profile` | object | Yes | Exact accepted profile identity. | Identifies the inline plan without copying its targets. |
| `network_validation` | object | Yes | Complete normalized object below. | Validation or captive-portal context used for admission or interpretation. |
| `steps` | array | Yes | Ordered, bounded, and no longer than the validated profile. | Primitive step results that began. |
| `stopped_before_step` | string | Conditional | Required when execution stopped before a remaining step; must match the next profile `step_id`. | Identifies the first unstarted step without emitting placeholder results. |

The `profile` object contains:

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `profile_id` | string | Yes | Exact validated task value. | Stable non-identifying plan identifier. |
| `profile_version` | integer | Yes | Exact validated task value. | Profile revision. |

The `network_validation` object contains:

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `state` | string | Yes | `validated`, `not_validated`, `captive_portal_suspected`, or `unknown` | Normalized validation state. |
| `source` | string | Yes | `fresh`, `cached`, or `platform` | Whether the state came from the current run, an allowed recent NET-03 result, or platform state only. |

Each `steps` entry contains:

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `step_id` | string | Yes | Exact unique identifier from the profile. | Links output to the inline step. |
| `test` | object | Yes | Exact primitive ID, behavior version, and registered result version. | Selects the primitive Output schema. |
| `state` | string | Yes | `completed` or `incomplete` | Whether the primitive reached a terminal measurement outcome. |
| `measurement` | object | Conditional | Required for `completed`; prohibited for an interrupted `incomplete` step in the initial version. | Primitive Output object without another common envelope or Network Context. |

Only one final step may be `incomplete`. Unstarted steps are not emitted. Their absence plus `stopped_before_step` distinguishes them from failed primitive measurements.

### Outcomes

| Outcome | Required evidence |
|---|---|
| `completed` | Every profile step is present with `state: completed`, and the outer common execution state is `completed`. Primitive negative outcomes do not change this composite outcome. |
| `network_not_validated` | `network_validation.state` is `not_validated` or `captive_portal_suspected`, no primitive step ran, and local policy required validation. |
| `incomplete` | One or more steps did not reach a terminal primitive result or did not start. The outer common execution state and reason explain why. |
| `inconclusive` | The profile completion state or retained validation context cannot be normalized safely. |

The failure classes `network_changed` and `resource_limit` are represented as `outcome: incomplete` plus the matching common `execution.reason`. This keeps cross-cutting termination separate from primitive network observations.

The result must not contain nested task envelopes, schedules, safety declarations, labels, duplicated targets, target URLs or IP addresses beyond bounded DNS answer values, profile contents, response bodies, HTTP headers, certificate data, platform errors, or a locally derived combined restriction verdict.

## Interpretation

The cross-cutting [Measurement Limitations](../measurement-limitations.md) apply to this result and any derived analysis.

### Supported Interpretation

One complete execution can establish the ordered primitive results produced by the inline profile on one network generation.

The profile author or a separate analysis component may correlate these results with knowledge of the targets, repeated runs, controls, and independent signals. That analysis is outside NET-05 version `0.1.0`.

### Alternative Explanations

- Simultaneous outage or misconfiguration affecting external profile targets.
- Shared hidden infrastructure, CDN, DNS, routing, or certificate dependencies among supposedly independent targets.
- International transit failure, routing isolation, congestion, or packet loss.
- Captive portal, subscription state, VPN, enterprise policy, or local firewall.
- Stale inline profile definitions or changed endpoint behavior.
- Address-family-specific failure or mobile-network handover.

### Evidence Needed for Stronger Interpretation

- Repeated complete profiles separated by a conservative schedule on stable network generations.
- Consistent failure across independently operated targets and multiple protocol layers.
- Continued reachability of suitable local or host-application controls.
- No captive-portal or obvious local-network explanation.
- Independent reference signals from comparable times and network or geographic contexts.

Even correlated observations cannot establish censor intent or policy with certainty. External datasets are supporting reference signals, not ground truth.

## Privacy and Safety

### Baseline Risk

| Field | Value |
|---|---|
| Risk level | `medium` |
| Requires user consent | `false`, subject to host and local policy |

`medium` reflects the recognizable multi-target pattern and the increased risk created by contacting several independently operated endpoints.

### Risk Factors

| Type | Level | Rationale and mitigation |
|---|---|---|
| `network_observability` | `medium` | Multiple destinations and protocol layers are visible to the network. |
| `traffic_distinctiveness` | `medium` | A fixed sequence of multi-endpoint checks can be recognizable. |
| `target_sensitivity` | `low` | Only benign reviewed endpoints are permitted, but target composition still requires review. |
| `data_sensitivity` | `medium` | Combined reachability patterns may reveal aspects of the user's network environment. |
| `legal_or_social_context` | `medium` | Coordinated measurement behavior can carry risk even when individual targets are benign. |

### Safety Analysis

- **Data minimization:** Retain primitive classifications and safe step identifiers, not duplicated raw target lists, response bodies, full addresses, or detailed network identity.
- **Traffic distinctiveness:** Execute sequentially, without synchronized fleet-wide cadence, automatic retries, port variation, or broad lists.
- **User-identification risk:** Do not add per-installation identifiers or combine the profile with unrelated device or application telemetry.
- **Target risk:** Every inline target must pass schema and local safety policy; profiles should use benign endpoints with documented ownership and operational expectations.
- **Repeated-execution risk:** Repetition materially increases distinctiveness; host and local policy must impose conservative scheduling.
- **Residual risks:** A network observer may correlate the destination sequence, and combined results may characterize a user's access environment.

The probe retains final authority to delay, skip, or reject execution. A task may increase the effective risk but must never lower this registered baseline.
