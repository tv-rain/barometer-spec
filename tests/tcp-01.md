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

<a id="REQ-TCP-01-0002"></a>

**REQ-TCP-01-0002:**

- The test does not perform DNS resolution.

<a id="REQ-TCP-01-0003"></a>

**REQ-TCP-01-0003:**

- The test does not establish that TLS, HTTP, or another application protocol is usable.

<a id="REQ-TCP-01-0004"></a>

**REQ-TCP-01-0004:**

- A timeout or reset does not by itself establish intentional filtering.

## Measurement Method

### Target

<a id="REQ-TCP-01-0005"></a>

**REQ-TCP-01-0005:**

One canonical public IPv4 or IPv6 address and one TCP port approved by local safety policy.

### Operation

<a id="REQ-TCP-01-0006"></a>

**REQ-TCP-01-0006:**

The probe opens one TCP socket on the active network, attempts one connection, records a normalized result and coarse timing, and closes the socket without sending application data.

### Procedure

<a id="REQ-TCP-01-0007"></a>

**REQ-TCP-01-0007:**

1. Validate the canonical IP address and port.
2. Confirm a stable network generation and compatible address family.
3. Start one TCP connection attempt with an operation deadline.
4. Record success or the first directly observed socket outcome.
5. Close the socket immediately without sending application payload data.

### Success Condition

<a id="REQ-TCP-01-0008"></a>

**REQ-TCP-01-0008:**

The operating system reports that the TCP connection completed to the exact configured address and port on the same network generation.

### Failure Conditions

<a id="REQ-TCP-01-0009"></a>

**REQ-TCP-01-0009:**

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

<a id="REQ-TCP-01-0010"></a>

**REQ-TCP-01-0010:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `ip_address` | string | Yes | Canonical public IPv4 or IPv6 address; local and special-purpose ranges are rejected by default. | Destination address. |
| `port` | integer | Yes | `1` through `65535`; target and port must pass local safety policy. | Destination TCP port. |

### Input Validation

<a id="REQ-TCP-01-0011"></a>

**REQ-TCP-01-0011:**

- Hostnames are not accepted; DNS resolution is measured separately.

<a id="REQ-TCP-01-0012"></a>

**REQ-TCP-01-0012:**

- Loopback, unspecified, multicast, link-local, private, documentation, benchmarking, and other special-purpose ranges are rejected unless a future test version explicitly supports them.

<a id="REQ-TCP-01-0013"></a>

**REQ-TCP-01-0013:**

- Broad port ranges, arrays, and runtime interpolation are not accepted.

<a id="REQ-TCP-01-0014"></a>

**REQ-TCP-01-0014:**

- Unknown fields are rejected.

<a id="REQ-TCP-01-0001"></a>

**REQ-TCP-01-0001:**

Invalid input must prevent measurement execution and must not produce a measurement result that could be interpreted as network interference.

## Options

<a id="REQ-TCP-01-0015"></a>

**REQ-TCP-01-0015:**

The initial version accepts an empty options object.

<a id="REQ-TCP-01-0016"></a>

**REQ-TCP-01-0016:**

| Option | Type | Required | Default | Constraints | Description |
|---|---|:---:|---|---|---|
| — | — | — | — | Additional properties are rejected. | The address family is determined by `ip_address`. |

## Preconditions

<a id="REQ-TCP-01-0017"></a>

**REQ-TCP-01-0017:**

- The active network must support the target address family.

<a id="REQ-TCP-01-0018"></a>

**REQ-TCP-01-0018:**

- The target address and port must be approved by local safety policy.

<a id="REQ-TCP-01-0019"></a>

**REQ-TCP-01-0019:**

- A stable network generation and execution deadline must be available.

<a id="REQ-TCP-01-0020"></a>

**REQ-TCP-01-0020:**

- The test must not run when platform policy would route it through an unintended network path.

<a id="REQ-TCP-01-0021"></a>

**REQ-TCP-01-0021:**

Task execution constraints and local probe policy may impose stricter preconditions.

## Resource Bounds

<a id="REQ-TCP-01-0022"></a>

**REQ-TCP-01-0022:**

| Resource | Baseline limit | Behavior when reached |
|---|---|---|
| Duration | One connect attempt within the task execution deadline. | Stop the socket operation and retain the observed stage. |
| Requests or connections | One TCP connection attempt. | Do not try another address or port. |
| Data transferred | TCP handshake traffic only; no application payload. | Close if application data would be sent. |
| Retries | None within one run. | A retry requires a new execution attempt. |
| Concurrency | One active run per address and port tuple. | Deduplicate or delay equivalent concurrent runs. |

## Output

<a id="REQ-TCP-01-0023"></a>

**REQ-TCP-01-0023:**

The test uses Measurement Result `schema_version: 0.1.0` and `test.result_version: 0.1.0`.

<a id="REQ-TCP-01-0024"></a>

**REQ-TCP-01-0024:**

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

<a id="REQ-TCP-01-0025"></a>

**REQ-TCP-01-0025:**

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

<a id="REQ-TCP-01-0026"></a>

**REQ-TCP-01-0026:**

`network_changed`, cancellation, the outer attempt deadline, proxy failure, and platform suspension produce an incomplete common execution state and no `measurement` object. They are not TCP outcomes.

<a id="REQ-TCP-01-0027"></a>

**REQ-TCP-01-0027:**

The result retains only the selected address family, normalized outcome, and quantized duration. It must not contain a socket error string or number, destination address or port, local address or port, TCP flags, packet counts, payload data, or retry metadata.

## Interpretation

The cross-cutting [Measurement Limitations](../measurement-limitations.md) apply to this result and any derived analysis.

### Supported Interpretation

<a id="REQ-TCP-01-0028"></a>

**REQ-TCP-01-0028:**

One execution can establish only whether a TCP connection to the configured address and port completed or produced a particular observable socket outcome.

### Alternative Explanations

- The target service may be offline, overloaded, or not listening.

- A firewall may reject or silently drop the connection for operational reasons.

- Routing, peering, NAT, carrier-grade NAT, VPN, or local network failure.

- IPv4/IPv6 path differences.

- Transient packet loss or mobile-network handover.

- Incorrect or stale target configuration.

### Evidence Needed for Stronger Interpretation

<a id="REQ-TCP-01-0029"></a>

**REQ-TCP-01-0029:**

- Repeated attempts under a stable network generation and conservative schedule.
- Successful connections to suitable control endpoints on the same port.
- DNS, TLS, and HTTPS observations for related approved targets.
- Independent measurements from comparable times and network contexts.

<a id="REQ-TCP-01-0030"></a>

**REQ-TCP-01-0030:**

A single connection result must not be described as definitive proof of censorship.

## Privacy and Safety

### Baseline Risk

<a id="REQ-TCP-01-0031"></a>

**REQ-TCP-01-0031:**

| Field | Value |
|---|---|
| Risk level | `low` |
| Requires user consent | `false`, subject to host and local policy |

### Risk Factors

<a id="REQ-TCP-01-0032"></a>

**REQ-TCP-01-0032:**

| Type | Level | Rationale and mitigation |
|---|---|---|
| `network_observability` | `low` | The destination address and port are visible to the network. |
| `traffic_distinctiveness` | `low` | One TCP handshake to an approved service is ordinary, though repeated bare handshakes may become distinctive. |
| `target_sensitivity` | `low` | Only reviewed public endpoints and ports are permitted. |
| `data_sensitivity` | `low` | Output contains a minimized outcome and coarse timing. |
| `legal_or_social_context` | `low` | Target selection can change risk and must be reviewed per task. |

### Safety Analysis

<a id="REQ-TCP-01-0033"></a>

**REQ-TCP-01-0033:**

- **Data minimization:** Retain only normalized connection outcome, selected family, and coarse timing required for interpretation.

<a id="REQ-TCP-01-0034"></a>

**REQ-TCP-01-0034:**

- **Traffic distinctiveness:** Avoid repeated connections, port sequences, and synchronized schedules.

<a id="REQ-TCP-01-0035"></a>

**REQ-TCP-01-0035:**

- **User-identification risk:** Do not attach identifiers or send application data.

<a id="REQ-TCP-01-0036"></a>

**REQ-TCP-01-0036:**

- **Target risk:** Reject unreviewed, local, private, or sensitive endpoints.

- **Repeated-execution risk:** Bare repeated connections can resemble scanning.

- **Residual risks:** The destination and network can observe the source address and connection attempt.

<a id="REQ-TCP-01-0037"></a>

**REQ-TCP-01-0037:**

The probe retains final authority to delay, skip, or reject execution. A task may increase the effective risk but must never lower this registered baseline.
