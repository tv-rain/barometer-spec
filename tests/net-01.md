# `NET-01` Network state

**Status:** `Draft`
**Version:** `0.1.0`
**Category:** `Network state`

## Overview

This test records the access portion of Barometer's shared [Network Context](../data-formats/network-context.md), using only coarse state exposed by the operating system, and identifies changes that may affect other measurements. It does not generate network traffic or perform egress classification.

A test defines registered measurement behavior. A task references the test by `test_id` and supplies the measurement input, options, execution constraints, schedule, and task-specific safety requirements.

## Purpose

### Measurement Question

What network context was visible to the probe when a measurement run began, and did that context change during the run?

### Non-goals

- The test does not establish that the Internet is reachable.
- The test does not identify a network operator, subscriber, device, or physical location.
- The test does not determine country, region, ASN, provider, mobile operator, or public IP address.
- A detected VPN interface does not establish that traffic is successfully routed through a VPN.

## Measurement Method

### Target

The local operating-system network-state APIs. There is no remote target.

### Operation

The probe reads only the state required to populate the normalized Network Context `access` object: active transport, IPv4/IPv6 availability, detectable VPN state, platform validation state, and network transitions. Values that cannot be determined reliably are reported as `unknown`.

### Procedure

1. Read the current network path or connectivity state from the operating system through the shared Network Context collector.
2. Normalize supported properties into the platform-independent `access` object.
3. Record whether the network generation changed during the snapshot.
4. Release platform callbacks or handles that were created for the run.
5. Do not contact a primary or fallback egress-classification endpoint as part of NET-01.

### Success Condition

The platform returns a coherent snapshot, including explicit `unknown` values for properties it cannot determine.

### Failure Conditions

| Failure class | Required observation |
|---|---|
| `platform_unavailable` | Required network-state APIs are unavailable on the platform. |
| `platform_error` | The platform API returns an error before a coherent snapshot is obtained. |
| `network_changed` | The network generation changes while the snapshot is being collected. |
| `inconclusive` | The returned state is internally inconsistent and cannot be normalized safely. |

## Inputs

The test accepts an empty input object.

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| — | — | — | Additional properties are rejected. | No external measurement subject is required. |

### Input Validation

- `input` must be an empty JSON object.
- The implementation must not accept interface names, local addresses, or device identifiers as task input.
- Invalid input prevents execution and is not a measurement outcome.

## Options

The initial version accepts an empty options object.

| Option | Type | Required | Default | Constraints | Description |
|---|---|:---:|---|---|---|
| — | — | — | — | Additional properties are rejected. | No test-specific options are defined. |

## Preconditions

- The host platform must expose a supported network-state API.
- The host application must grant only the platform capabilities required to read network state.
- The test must not run if the available implementation would require access to interface addresses, SSIDs, BSSIDs, subscriber identifiers, or location.

Task execution constraints and local probe policy may impose stricter preconditions.

## Resource Bounds

| Resource | Baseline limit | Behavior when reached |
|---|---|---|
| Duration | Must complete within the task execution deadline. | Stop and report the applicable execution state. |
| Requests or connections | No network requests or connections. | Any attempted network operation is an implementation error. |
| Data transferred | None. | Any transferred network data is an implementation error. |
| Retries | None within one run. | A later run requires a new execution attempt. |
| Concurrency | May run alongside other tests. | The snapshot must identify a network change rather than silently combining states. |

## Output

The test uses Measurement Result `schema_version: 0.1.0` and `test.result_version: 0.1.0`.

NET-01 omits the common top-level `network_context` object. A successful `measurement` contains the normalized [`access` object](../data-formats/network-context.md#access-object) directly and an empty `observations` array:

```json
{
  "outcome": "snapshot",
  "observations": [],
  "access": {
    "network_type": "wifi",
    "vpn_state": "not_detected",
    "ipv4_available": "yes",
    "ipv6_available": "yes",
    "validated": "yes",
    "network_changed": false
  }
}
```

The test never outputs the shared `egress` object because NET-01 must remain a zero-traffic platform-state measurement.

### Additional Field

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `access` | object | Conditional | Required for `snapshot`; permitted for `inconclusive` only when all required normalized fields can be populated, using `unknown` where defined. | Normalized access-network state. |

### Outcomes

| Outcome | Required data |
|---|---|
| `snapshot` | A complete coherent `access` object with `network_changed: false`. |
| `platform_unavailable` | No access snapshot was available. |
| `platform_error` | Platform collection failed before a coherent snapshot was available. |
| `inconclusive` | The available values could not support another outcome; a complete normalized `access` object may be retained when available. |

A network-generation change during collection produces `execution.state: incomplete` with `execution.reason: network_changed` and no `measurement`. The outer attempt deadline, host cancellation, and platform suspension are represented in the same common execution layer rather than as NET-01 outcomes.

The result must not contain interface names or indexes, local or public addresses, routes, DNS configuration, SSID, BSSID, Wi-Fi scan data, cell identifiers, SIM or subscriber data, carrier name, signal strength, VPN application identity, network generation, platform object descriptions, or raw errors.

## Interpretation

The cross-cutting [Measurement Limitations](../measurement-limitations.md) apply to this result and any derived analysis.

### Supported Interpretation

One execution can establish only the normalized access-network properties exposed by the operating system at that time and whether the network changed during the snapshot. Country, region, ASN, provider, and operator require separate egress or consented context and cannot be inferred from NET-01.

### Alternative Explanations

- Platform APIs may expose incomplete or delayed state.
- A VPN may be present without carrying the measured traffic.
- Dual-stack capability does not establish successful IPv4 or IPv6 Internet reachability.
- Operating-system validation state may be stale.

### Evidence Needed for Stronger Interpretation

- Results from `NET-03` for Internet validation or captive-portal behavior.
- Protocol measurements performed within the same stable network generation.
- Repeated snapshots after a reported network change.

A single result must not be described as definitive proof of censorship.

## Privacy and Safety

### Baseline Risk

| Field | Value |
|---|---|
| Risk level | `low` |
| Requires user consent | `false`, subject to host and local policy |

### Risk Factors

| Type | Level | Rationale and mitigation |
|---|---|---|
| `network_observability` | `low` | The test generates no network traffic. |
| `traffic_distinctiveness` | `low` | No measurement traffic is emitted. |
| `target_sensitivity` | `low` | There is no remote target. |
| `data_sensitivity` | `low` | Output is limited to coarse state classifications; interface and subscriber identifiers are excluded. |
| `legal_or_social_context` | `low` | No participation signal is exposed on the network, but deployment assumptions still require review. |

### Safety Analysis

- **Data minimization:** Record only the normalized access fields necessary to interpret measurements; egress classification and carrier identity are excluded.
- **Traffic distinctiveness:** The test emits no traffic.
- **User-identification risk:** Interface names, addresses, SSIDs, BSSIDs, carrier names, and subscriber identifiers must not be collected.
- **Target risk:** There is no remote target.
- **Repeated-execution risk:** Frequent snapshots can consume resources but do not create a network-visible pattern.
- **Residual risks:** Coarse network-state combinations could contribute to fingerprinting if retained or combined with egress context or unrelated telemetry.

The probe retains final authority to delay, skip, or reject execution. A task may increase the effective risk but must never lower this registered baseline.
