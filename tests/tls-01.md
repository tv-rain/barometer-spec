# `TLS-01` TLS handshake

**Status:** `Draft`
**Version:** `0.1.0`
**Category:** `TLS connectivity`

## Overview

This test performs one normal TLS handshake with a configured IP address, port, and server name and records the first observable handshake outcome.

A test defines registered measurement behavior. A task references the test by `test_id` and supplies the measurement input, options, execution constraints, schedule, and task-specific safety requirements.

## Purpose

### Measurement Question

Can the probe establish an authenticated TLS session with the configured endpoint and server name on the active network path?

### Non-goals

- The test does not perform an HTTP request or validate application content.
- The test does not compare different SNI values within one run.
- A handshake failure does not by itself establish TLS or SNI filtering.

## Measurement Method

### Target

One approved public IP address, TCP port, and DNS server name representing a service expected to present a publicly trusted certificate for that name.

### Operation

The probe opens one TCP connection to the explicit IP address, sends a standards-compliant TLS ClientHello containing the configured server name and registered ALPN list, validates the peer certificate with the implementation's documented trust store, records negotiated properties, and closes without sending application data.

### Procedure

1. Validate the IP address, port, server name, and optional ALPN list.
2. Confirm a stable network generation and compatible address family.
3. Open one TCP connection to the explicit address and port.
4. Perform one TLS handshake with certificate and hostname validation enabled.
5. Record the first failed stage or minimized negotiated properties.
6. Close the session without sending application-protocol payload data.

### Success Condition

The TLS handshake completes, the certificate chain is accepted by the documented trust policy, and the certificate is valid for `server_name`.

### Failure Conditions

| Failure class | Required observation |
|---|---|
| `tcp_timeout` | The underlying TCP connection does not complete within its operation bound. |
| `tcp_refused` | The target explicitly refuses the TCP connection. |
| `tcp_reset` | The connection is reset before or during the handshake. |
| `tls_timeout` | The TLS handshake does not complete within its operation bound. |
| `tls_alert` | A TLS alert is received; only a normalized alert class is retained. |
| `protocol_error` | The peer response is not a valid supported TLS exchange. |
| `certificate_untrusted` | The certificate chain is not accepted by the documented trust policy. |
| `certificate_name_mismatch` | The certificate is not valid for `server_name`. |
| `certificate_time_invalid` | The certificate is not valid at the evaluation time. |
| `alpn_no_overlap` | The endpoint and configured ALPN list do not negotiate a protocol when the test requires one. |
| `network_changed` | The network generation changes during the run. |
| `inconclusive` | Platform error mapping or termination does not support a more specific class. |

## Inputs

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `ip_address` | string | Yes | Canonical public IPv4 or IPv6 address approved by local policy. | TCP destination, avoiding implicit DNS resolution. |
| `port` | integer | Yes | `1` through `65535`; endpoint and port must pass local safety policy. | TLS service port. |
| `server_name` | string | Yes | Valid normalized DNS name, maximum 253 ASCII bytes after IDNA normalization; IP literals and wildcards are not accepted. | TLS SNI and certificate hostname. |

### Input Validation

- The address, port, and server name must form a locally reviewed target.
- Loopback, private, link-local, special-purpose, interpolated, and unknown targets are rejected by default.
- `server_name` must not be silently derived from the address.
- The implementation must not disable certificate or hostname validation.
- Unknown fields are rejected.

Invalid input must prevent measurement execution and must not produce a measurement result that could be interpreted as network interference.

## Options

| Option | Type | Required | Default | Constraints | Description |
|---|---|:---:|---|---|---|
| `alpn_protocols` | array of strings | No | Empty list | At most 8 registered ASCII protocol identifiers of 1–32 bytes; duplicates rejected. | ALPN protocols offered in order. |

Custom cipher lists, TLS-version forcing, invalid certificates, alternate SNI values, client certificates, session resumption, and insecure verification are not supported in this version.

## Preconditions

- A stable network generation and execution deadline must be available.
- The target must be expected to support normal publicly authenticated TLS.
- The implementation trust policy and time source must be documented.
- The test must not run if the target requires client authentication, credentials, or sensitive server names.

Task execution constraints and local probe policy may impose stricter preconditions.

## Resource Bounds

| Resource | Baseline limit | Behavior when reached |
|---|---|---|
| Duration | One TCP connection and one TLS handshake within the task deadline. | Stop at the active stage and close the socket. |
| Requests or connections | One connection and one handshake. | Do not try another address, server name, or TLS profile. |
| Data transferred | TCP and TLS handshake traffic only. | Close before application payload is sent. |
| Retries | None within one run. | A retry requires a new execution attempt. |
| Concurrency | One active run per endpoint and server-name tuple. | Deduplicate or delay equivalent runs. |

## Output

The test uses Measurement Result `schema_version: 0.1.0` and `test.result_version: 0.1.0`.

A completed result contains one [`tcp_connect` observation](../data-formats/measurement-observations.md#tcp-connect) and, when TLS activity began, one [`tls_handshake` observation](../data-formats/measurement-observations.md#tls-handshake). Observations appear in execution order.

Example:

```json
{
  "outcome": "handshake_succeeded",
  "observations": [
    {
      "type": "tcp_connect",
      "status": "succeeded",
      "duration_ms": 250,
      "details": {
        "address_family": "ipv4"
      }
    },
    {
      "type": "tls_handshake",
      "status": "succeeded",
      "duration_ms": 500,
      "details": {
        "address_family": "ipv4",
        "tls_version": "TLS1.3",
        "alpn": "h2",
        "certificate_validation": "trusted"
      }
    }
  ]
}
```

### Outcomes

| Outcome | Required terminal observation |
|---|---|
| `handshake_succeeded` | TLS succeeded with `certificate_validation: trusted`. |
| `tcp_timeout` | TCP failed with `timeout`. |
| `tcp_refused` | TCP failed with `connection_refused`. |
| `tcp_reset` | TCP failed with `connection_reset`, or TLS failed with `connection_reset` after the TCP connect completed. |
| `tls_timeout` | TLS failed with `timeout`. |
| `tls_alert` | TLS failed with `alert`; a registered coarse alert class may be present. |
| `protocol_error` | TLS failed with `protocol_error`. |
| `certificate_untrusted` | TLS failed with `certificate_untrusted` and validation is `untrusted`. |
| `certificate_name_mismatch` | TLS failed with `certificate_name_mismatch` and validation is `name_mismatch`. |
| `certificate_time_invalid` | TLS failed with `certificate_time_invalid` and validation is `time_invalid`. |
| `alpn_no_overlap` | TLS failed with `alpn_no_overlap`. |
| `inconclusive` | The terminal TCP or TLS observation failed with `inconclusive`. |

`network_changed`, cancellation, the outer attempt deadline, proxy failure or reconfiguration, and platform suspension produce an incomplete common execution state. They are not TLS outcomes.

The result must not contain the destination address or port, `server_name`, certificate or certificate-chain data, certificate names or fingerprints, raw alerts, ClientHello or ServerHello fields, offered cipher suites, negotiated cipher suite, session identifiers, TLS secrets, or raw library errors.

## Interpretation

The cross-cutting [Measurement Limitations](../measurement-limitations.md) apply to this result and any derived analysis.

### Supported Interpretation

One execution can establish whether TCP and normal authenticated TLS completed for the configured address, port, server name, and ALPN offer.

### Alternative Explanations

- Target, load balancer, CDN, certificate, or trust-store misconfiguration.
- Expired certificate or incorrect device time.
- Routing, packet loss, mobile handover, VPN, firewall, or proxy behavior.
- Unsupported TLS version, algorithm, or ALPN configuration.
- Stale address-to-name mapping.
- Server-side rate limiting or overload.

### Evidence Needed for Stronger Interpretation

- A `TCP-01` result for the same address and port.
- Repeated TLS observations under a stable network generation.
- Successful control handshakes using comparable infrastructure.
- `HTTP-01` results and independent observations from comparable contexts.

Comparison of different SNI values is outside this test and would require a separately reviewed measurement because it changes traffic distinctiveness and interpretation.

## Privacy and Safety

### Baseline Risk

| Field | Value |
|---|---|
| Risk level | `low` |
| Requires user consent | `false`, subject to host and local policy |

### Risk Factors

| Type | Level | Rationale and mitigation |
|---|---|---|
| `network_observability` | `low` | The destination and some handshake metadata, including plaintext SNI where applicable, may be visible. |
| `traffic_distinctiveness` | `low` | One normal TLS handshake resembles ordinary application traffic. |
| `target_sensitivity` | `low` | Only reviewed, non-sensitive services are permitted. |
| `data_sensitivity` | `low` | Output is limited to validation and negotiated-property classifications. |
| `legal_or_social_context` | `low` | Server-name sensitivity varies by deployment and requires target review. |

### Safety Analysis

- **Data minimization:** Do not retain full certificate chains, raw ClientHello/ServerHello messages, session keys, or packet traces.
- **Traffic distinctiveness:** Use platform-typical TLS behavior and avoid malformed or comparative handshakes.
- **User-identification risk:** Do not send client certificates, identifiers, cookies, or application data.
- **Target risk:** Permit only reviewed address, port, and server-name tuples.
- **Repeated-execution risk:** Repeated bare handshakes can form a recognizable pattern.
- **Residual risks:** Network observers may see the destination and SNI; platform TLS fingerprints may differ from the host application's traffic.

The probe retains final authority to delay, skip, or reject execution. A task may increase the effective risk but must never lower this registered baseline.
