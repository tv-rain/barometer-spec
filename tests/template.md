# `<Test ID: stable identifier, for example NET-01>` `<human-readable name>`

**Status:** `<Draft | Experimental | Current | Deprecated | Obsolete>`
**Version:** `0.1.0`
**Category:** `<DNS resolution | TCP reachability | TLS connectivity | HTTPS connectivity | CDN access | domain rotation | other>`

## Overview

`<Briefly describe the measurement and the network property it observes.>`

A test defines registered measurement behavior. A task references the test by `test_id` and supplies the measurement input, options, execution constraints, schedule, and task-specific safety requirements.

## Purpose

### Measurement Question

`<State the single, narrowly defined question that the test is intended to answer.>`

### Non-goals

- `<State what the test does not measure.>`
- `<State conclusions that must not be inferred from the result.>`

## Measurement Method

### Target

`<Describe the type of measurement target, such as a domain name, IP address, URL, or service. Define target requirements without specifying a particular task input.>`

### Operation

`<Describe the bounded network operation performed by the probe. Include protocol behavior that affects compatibility, safety, or interpretation.>`

### Procedure

1. `<Describe the first operation.>`
2. `<Describe subsequent operations in execution order.>`
3. `<Define when the operation stops.>`
4. `<Describe cleanup, if required.>`

### Success Condition

`<Define success using directly observable evidence.>`

### Failure Conditions

| Failure class | Required observation |
|---|---|
| `<stable failure value>` | `<Directly observed condition>` |
| `inconclusive` | `<Condition that prevents reliable classification>` |

## Inputs

Describe the input object accepted from the task.

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `<field>` | `<type>` | `<Yes \| No>` | `<allowed values or validation rules>` | `<meaning>` |

### Input Validation

- `<Define relationships between input fields.>`
- `<Define invalid or unsupported inputs.>`
- `<Define whether redirects, aliases, or derived targets are permitted.>`

Invalid input must prevent measurement execution and must not produce a measurement result that could be interpreted as network interference.

## Options

Describe test-specific behavior accepted from the task's `options` object. Scheduling, device state, network eligibility, and general runtime constraints belong to the task rather than the test options.

| Option | Type | Required | Default | Constraints | Description |
|---|---|:---:|---|---|---|
| `<option>` | `<type>` | `<Yes \| No>` | `<conservative default>` | `<allowed values or range>` | `<meaning>` |

## Preconditions

- `<Required platform capability or permission.>`
- `<Required state of the target or reference service.>`
- `<Condition under which the test must not run.>`

Task execution constraints and local probe policy may impose stricter preconditions.

## Resource Bounds

Define intrinsic limits required for the test to remain bounded. A task or local probe policy may impose stricter limits.

| Resource | Baseline limit | Behavior when reached |
|---|---|---|
| Duration | `<maximum>` | `<stop and classify>` |
| Requests or connections | `<maximum>` | `<stop and classify>` |
| Data transferred | `<maximum>` | `<stop and classify>` |
| Retries | `<maximum or none>` | `<stop and classify>` |
| Concurrency | `<intrinsic restriction, if any>` | `<reject, delay, or serialize>` |

## Output

State the supported common Measurement Result and test result versions, then define the complete test-specific `measurement` object.

Reference reusable observation types from [`data-formats/measurement-observations.md`](../data-formats/measurement-observations.md) rather than defining raw protocol traces.

Include:

- one positive terminal outcome and every negative or inconclusive outcome;
- the required terminal observation for each outcome;
- any test-specific fields and conditional-field rules;
- whether incomplete common execution may retain a partial `measurement`;
- which cross-cutting conditions use common `execution.reason` instead of a test outcome;
- retained timing, protocol, response, or comparison properties;
- an explicit list of data that must not be retained;
- at least one schema-valid minimized example.

Do not define a generic `blocked`, `censored`, or anomaly boolean as a source measurement outcome. Derived analysis belongs in a separate versioned format.

## Interpretation

Link the cross-cutting [Measurement Limitations](../measurement-limitations.md) and add or update its test-specific matrix entry before publishing the test.

### Supported Interpretation

`<State what one execution can establish, limited to the directly observed network behavior.>`

### Alternative Explanations

Consider applicable non-censorship explanations, including:

- target, origin, or CDN outage;
- congestion, packet loss, or transient mobile-network behavior;
- DNS or routing failure;
- TLS or certificate configuration failure;
- local network restrictions;
- platform-specific behavior;
- invalid or stale test configuration.

### Evidence Needed for Stronger Interpretation

- `<Repeated observations over an appropriate period.>`
- `<Related measurements at other network layers.>`
- `<Comparison with suitable control targets.>`
- `<Independent reference signals from comparable times and network or geographic contexts.>`

A single result must not be described as definitive proof of censorship. External measurements may support triangulation but must not be treated as ground truth.

## Privacy and Safety

### Baseline Risk

| Field | Value |
|---|---|
| Risk level | `<low \| medium \| high \| unknown>` |
| Requires user consent | `<true \| false, subject to host and local policy>` |

### Risk Factors

| Type | Level | Rationale and mitigation |
|---|---|---|
| `network_observability` | `<level>` | `<Assessment>` |
| `traffic_distinctiveness` | `<level>` | `<Assessment>` |
| `target_sensitivity` | `<level>` | `<Assessment>` |
| `data_sensitivity` | `<level>` | `<Assessment>` |
| `legal_or_social_context` | `<level>` | `<Assessment>` |

The overall baseline risk must be at least as restrictive as every known risk factor. Document additional factors when relevant.

### Safety Analysis

- **Data minimization:** `<Explain why every output field is necessary.>`
- **Traffic distinctiveness:** `<Assess whether the operation differs from ordinary application traffic.>`
- **User-identification risk:** `<Assess potential linking or fingerprinting risks.>`
- **Target risk:** `<Assess risks created by contacting the target.>`
- **Repeated-execution risk:** `<Assess whether repetition could create a recognizable pattern.>`
- **Residual risks:** `<Document risks that remain after mitigation.>`

The probe retains final authority to delay, skip, or reject execution. A task may increase the effective risk but must never lower this registered baseline.
