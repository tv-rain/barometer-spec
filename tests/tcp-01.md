# `TCP-01` TCP connect

**Status:** `Draft`
**Version:** `0.1.0`
**Category:** `TCP reachability`

## Overview

This test attempts one bounded TCP connection to a configured IP address and port and records the directly observed connection outcome.

A test defines registered measurement behavior. A task references the test by `test_id` and supplies the measurement input, options, execution constraints, schedule, and task-specific safety requirements.

## Purpose

### Measurement Question

Can the probe complete a TCP connection to the configured IP address and port on the active network path?

### Non-goals

- The test does not perform DNS resolution.
- The test does not establish that TLS, HTTP, or another application protocol is usable.
- A timeout or reset does not by itself establish intentional filtering.

## Measurement Method

### Target

One canonical public IPv4 or IPv6 address and one TCP port approved by local safety policy.

### Operation

The probe opens one TCP socket on the active network, attempts one connection, records a normalized result and coarse timing, and closes the socket without sending application data.

### Procedure

1. Validate the canonical IP address and port.
2. Confirm a stable network generation and compatible address family.
3. Start one TCP connection attempt with an operation deadline.
4. Record success or the first directly observed socket outcome.
5. Close the socket immediately without sending application payload data.

### Success Condition

The operating system reports that the TCP connection completed to the exact configured address and port on the same network generation.

### Failure Conditions

| Failure class | Required observation |
|---|---|
| `timeout` | The connect operation does not complete within its bound. |
| `connection_refused` | The remote path explicitly refuses the connection. |
| `connection_reset` | The connection is reset during establishment or immediately after completion and before application data. |
| `network_unreachable` | The operating system reports no route or network reachability. |
| `address_unreachable` | The operating system reports the destination address as unreachable. |
| `permission_denied` | Local platform or policy prevents the socket operation. |
| `network_changed` | The network generation changes during the attempt. |
| `socket_error` | Another socket error is reported and preserved in a normalized class. |
| `inconclusive` | Platform error mapping is too coarse to select another class safely. |

## Inputs

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `ip_address` | string | Yes | Canonical public IPv4 or IPv6 address; local and special-purpose ranges are rejected by default. | Destination address. |
| `port` | integer | Yes | `1` through `65535`; target and port must pass local safety policy. | Destination TCP port. |

### Input Validation

- Hostnames are not accepted; DNS resolution is measured separately.
- Loopback, unspecified, multicast, link-local, private, documentation, benchmarking, and other special-purpose ranges are rejected unless a future test version explicitly supports them.
- Broad port ranges, arrays, and runtime interpolation are not accepted.
- Unknown fields are rejected.

<a id="REQ-TCP-01-0001"></a>

**REQ-TCP-01-0001:**

Invalid input must prevent measurement execution and must not produce a measurement result that could be interpreted as network interference.

## Options

The initial version accepts an empty options object.

| Option | Type | Required | Default | Constraints | Description |
|---|---|:---:|---|---|---|
| — | — | — | — | Additional properties are rejected. | The address family is determined by `ip_address`. |

## Preconditions

- The active network must support the target address family.
- The target address and port must be approved by local safety policy.
- A stable network generation and execution deadline must be available.
- The test must not run when platform policy would route it through an unintended network path.

Task execution constraints and local probe policy may impose stricter preconditions.

## Resource Bounds

| Resource | Baseline limit | Behavior when reached |
|---|---|---|
| Duration | One connect attempt within the task execution deadline. | Stop the socket operation and retain the observed stage. |
| Requests or connections | One TCP connection attempt. | Do not try another address or port. |
| Data transferred | TCP handshake traffic only; no application payload. | Close if application data would be sent. |
| Retries | None within one run. | A retry requires a new execution attempt. |
| Concurrency | One active run per address and port tuple. | Deduplicate or delay equivalent concurrent runs. |

## Output

The test uses Measurement Result `schema_version: 0.1.0` and `test.result_version: 0.1.0`.

A completed result contains exactly one [`tcp_connect` observation](../data-formats/measurement-observations.md#tcp-connect). The observation repeats neither `ip_address` nor `port`; the collector resolves the validated target through `task_id`.

Example:

```json
{
  "outcome": "connection_refused",
  "observations": [
    {
      "type": "tcp_connect",
      "status": "failed",
      "duration_ms": 500,
      "failure": "connection_refused",
      "details": {
        "address_family": "ipv4"
      }
    }
  ]
}
```

### Outcomes

| Outcome | Required observation |
|---|---|
| `connected` | The `tcp_connect` observation succeeded. |
| `timeout` | The observation failed with `timeout`. |
| `connection_refused` | The observation failed with `connection_refused`. |
| `connection_reset` | The observation failed with `connection_reset`. |
| `network_unreachable` | The observation failed with `network_unreachable`. |
| `address_unreachable` | The observation failed with `address_unreachable`. |
| `permission_denied` | The observation failed with `permission_denied`. |
| `socket_error` | The observation failed with `socket_error`. |
| `inconclusive` | The observation failed with `inconclusive`. |

`network_changed`, cancellation, the outer attempt deadline, proxy failure, and platform suspension produce an incomplete common execution state and no `measurement` object. They are not TCP outcomes.

The result retains only the selected address family, normalized outcome, and quantized duration. It must not contain a socket error string or number, destination address or port, local address or port, TCP flags, packet counts, payload data, or retry metadata.

## Interpretation

The cross-cutting [Measurement Limitations](../measurement-limitations.md) apply to this result and any derived analysis.

### Supported Interpretation

One execution can establish only whether a TCP connection to the configured address and port completed or produced a particular observable socket outcome.

### Alternative Explanations

- The target service may be offline, overloaded, or not listening.
- A firewall may reject or silently drop the connection for operational reasons.
- Routing, peering, NAT, carrier-grade NAT, VPN, or local network failure.
- IPv4/IPv6 path differences.
- Transient packet loss or mobile-network handover.
- Incorrect or stale target configuration.

### Evidence Needed for Stronger Interpretation

- Repeated attempts under a stable network generation and conservative schedule.
- Successful connections to suitable control endpoints on the same port.
- DNS, TLS, and HTTPS observations for related approved targets.
- Independent measurements from comparable times and network contexts.

A single connection result must not be described as definitive proof of censorship.

## Privacy and Safety

### Baseline Risk

| Field | Value |
|---|---|
| Risk level | `low` |
| Requires user consent | `false`, subject to host and local policy |

### Risk Factors

| Type | Level | Rationale and mitigation |
|---|---|---|
| `network_observability` | `low` | The destination address and port are visible to the network. |
| `traffic_distinctiveness` | `low` | One TCP handshake to an approved service is ordinary, though repeated bare handshakes may become distinctive. |
| `target_sensitivity` | `low` | Only reviewed public endpoints and ports are permitted. |
| `data_sensitivity` | `low` | Output contains a minimized outcome and coarse timing. |
| `legal_or_social_context` | `low` | Target selection can change risk and must be reviewed per task. |

### Safety Analysis

- **Data minimization:** Retain only normalized connection outcome, selected family, and coarse timing required for interpretation.
- **Traffic distinctiveness:** Avoid repeated connections, port sequences, and synchronized schedules.
- **User-identification risk:** Do not attach identifiers or send application data.
- **Target risk:** Reject unreviewed, local, private, or sensitive endpoints.
- **Repeated-execution risk:** Bare repeated connections can resemble scanning.
- **Residual risks:** The destination and network can observe the source address and connection attempt.

The probe retains final authority to delay, skip, or reject execution. A task may increase the effective risk but must never lower this registered baseline.
