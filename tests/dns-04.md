# `DNS-04` DNS-over-TLS resolution

**Status:** `Draft`
**Version:** `0.1.0`
**Category:** `DNS resolution`

## Overview

This test sends one DNS query for a configured, non-sensitive hostname to an explicitly configured DNS-over-TLS resolver and records the stage at which the operation succeeds or fails.

A test defines registered measurement behavior. A task references the test by `test_id` and supplies the measurement input, options, execution constraints, schedule, and task-specific safety requirements.

## Purpose

### Measurement Question

Can the probe establish an authenticated DNS-over-TLS session with the configured resolver and receive a valid response for the configured query?

### Non-goals

<a id="REQ-DNS-04-0001"></a>

**REQ-DNS-04-0001:**

- The test does not configure DoT for the device or host application.

<a id="REQ-DNS-04-0002"></a>

**REQ-DNS-04-0002:**

- The test does not establish that the resolver's answer is authoritative or correct.

<a id="REQ-DNS-04-0003"></a>

**REQ-DNS-04-0003:**

- Failure on the standard DoT port does not prove intentional blocking.

## Measurement Method

### Target

<a id="REQ-DNS-04-0004"></a>

**REQ-DNS-04-0004:**

One explicitly configured DoT resolver, normally reached on TCP port 853, and one reviewed, non-sensitive query name. Non-standard ports require explicit registered support and safety review.

### Operation

<a id="REQ-DNS-04-0005"></a>

**REQ-DNS-04-0005:**

The probe resolves or uses an approved bootstrap address for the resolver, opens one TCP connection, authenticates TLS for the configured resolver name, and exchanges one length-prefixed DNS query and bounded response. It does not fall back to cleartext DNS or another resolver.

### Procedure

<a id="REQ-DNS-04-0006"></a>

**REQ-DNS-04-0006:**

1. Validate the resolver name, port, optional bootstrap address, query name, and record type.
2. Resolve the resolver name with the system resolver unless an approved bootstrap address was supplied.
3. Connect to one selected address on the configured port.
4. Establish TLS and validate the certificate for the resolver name.
5. Send one length-prefixed DNS message and parse one bounded response.
6. Close the session without cleartext fallback or application-layer retry.

### Success Condition

<a id="REQ-DNS-04-0007"></a>

**REQ-DNS-04-0007:**

An authenticated TLS session returns a syntactically valid DNS message that matches the submitted query. The response may still contain `NXDOMAIN`, `SERVFAIL`, `REFUSED`, or an empty answer.

### Failure Conditions

<a id="REQ-DNS-04-0008"></a>

**REQ-DNS-04-0008:**

| Failure class | Required observation |
|---|---|
| `bootstrap_failure` | The resolver name cannot be resolved through the selected bootstrap path. |
| `tcp_timeout` | The TCP connection does not complete within the operation bound. |
| `tcp_refused` | The selected address explicitly refuses the TCP connection. |
| `tcp_reset` | The TCP connection is reset before the TLS exchange completes. |
| `tls_failure` | TLS negotiation or resolver certificate validation fails. |
| `dns_nxdomain` | A valid DNS response reports `NXDOMAIN`. |
| `dns_servfail` | A valid DNS response reports `SERVFAIL`. |
| `dns_refused` | A valid DNS response reports `REFUSED`. |
| `malformed_dns_response` | The received length prefix or DNS message is invalid or exceeds the bound. |
| `query_mismatch` | The response does not correspond to the submitted question. |
| `timeout` | A post-connect TLS or DNS stage reaches its operation bound. |
| `network_changed` | The network generation changes during the run. |
| `inconclusive` | The available observation cannot be assigned safely to another class. |

## Inputs

<a id="REQ-DNS-04-0009"></a>

**REQ-DNS-04-0009:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `resolver_name` | string | Yes | Valid normalized DNS name, maximum 253 ASCII bytes after IDNA normalization, in a locally registered resolver profile. | Name used for bootstrap and TLS authentication. |
| `port` | integer | Yes | Valid TCP port; standard profiles use `853`; non-standard ports require explicit review. | Resolver TCP port. |
| `hostname` | string | Yes | Valid normalized DNS name, maximum 253 ASCII bytes after IDNA normalization, approved by local policy. | Name to query. |
| `record_type` | string | Yes | `A` or `AAAA`. | Requested record type. |
| `bootstrap_ip` | string | No | Canonical public IPv4 or IPv6 address registered for the resolver. | Avoids system-DNS dependency for resolver bootstrap. |

### Input Validation

<a id="REQ-DNS-04-0010"></a>

**REQ-DNS-04-0010:**

- Resolver name, port, and optional bootstrap address must match a locally available, reviewed resolver profile.

<a id="REQ-DNS-04-0011"></a>

**REQ-DNS-04-0011:**

- TLS must authenticate `resolver_name` even when a bootstrap IP is supplied.

<a id="REQ-DNS-04-0012"></a>

**REQ-DNS-04-0012:**

- Cleartext DNS on the configured DoT connection is never permitted.

<a id="REQ-DNS-04-0013"></a>

**REQ-DNS-04-0013:**

- Local, loopback, link-local, private, interpolated, or unknown targets are rejected by default.

<a id="REQ-DNS-04-0014"></a>

**REQ-DNS-04-0014:**

- Unknown fields are rejected.

<a id="REQ-DNS-04-0015"></a>

**REQ-DNS-04-0015:**

Invalid input must prevent measurement execution and must not produce a measurement result that could be interpreted as network interference.

## Options

<a id="REQ-DNS-04-0016"></a>

**REQ-DNS-04-0016:**

| Option | Type | Required | Default | Constraints | Description |
|---|---|:---:|---|---|---|
| `address_family` | string | No | `auto` | `auto`, `ipv4`, or `ipv6`; must be compatible with `bootstrap_ip` when present. | Selects the resolver connection family. |

<a id="REQ-DNS-04-0017"></a>

**REQ-DNS-04-0017:**

Opportunistic authentication, cleartext fallback, connection reuse across runs, and alternate resolver fallback are not supported in this version.

## Preconditions

<a id="REQ-DNS-04-0018"></a>

**REQ-DNS-04-0018:**

- The resolver and query name must have completed technical, privacy, and safety review.

<a id="REQ-DNS-04-0019"></a>

**REQ-DNS-04-0019:**

- The registered resolver profile must be available locally.

<a id="REQ-DNS-04-0020"></a>

**REQ-DNS-04-0020:**

- The test must run only under explicit reviewed host configuration or as an approved anomaly-triggered diagnostic.

<a id="REQ-DNS-04-0021"></a>

**REQ-DNS-04-0021:**

- A stable network generation and execution deadline must be available.

<a id="REQ-DNS-04-0022"></a>

**REQ-DNS-04-0022:**

Task execution constraints and local probe policy may impose stricter preconditions.

## Resource Bounds

<a id="REQ-DNS-04-0023"></a>

**REQ-DNS-04-0023:**

| Resource | Baseline limit | Behavior when reached |
|---|---|---|
| Duration | One bootstrap operation and one DoT exchange within the task deadline. | Stop at the active stage and do not fall back. |
| Requests or connections | At most one resolver connection after bootstrap and one DNS exchange. | Close after the first complete response or failure. |
| Data transferred | One DNS query and one DNS message of at most 65,535 bytes plus TCP/TLS overhead; at most 16 normalized answers are retained. | Stop reading an oversized response and classify it as malformed or unsupported. |
| Retries | None at the test layer. | A retry requires a new execution attempt. |
| Concurrency | One active run per resolver and query tuple. | Deduplicate or delay equivalent runs. |

## Output

<a id="REQ-DNS-04-0024"></a>

**REQ-DNS-04-0024:**

The test uses Measurement Result `schema_version: 0.1.0` and `test.result_version: 0.1.0`.

The result contains the ordered observations that actually began:

<a id="REQ-DNS-04-0025"></a>

**REQ-DNS-04-0025:**

1. a system `dns_query` when bootstrap resolution was required;
2. `tcp_connect`;
3. `tls_handshake`;
4. a `dot` `dns_query` representing the length-prefixed DNS exchange.

<a id="REQ-DNS-04-0026"></a>

**REQ-DNS-04-0026:**

When `bootstrap_ip` is used, the first observation is omitted. The final DNS observation retains bounded normalized answers as defined by the common [DNS Query](../data-formats/measurement-observations.md#dns-query) format.

Example:

```json
{
  "outcome": "dns_refused",
  "observations": [
    {
      "type": "tcp_connect",
      "status": "succeeded",
      "duration_ms": 500,
      "details": {
        "address_family": "ipv6"
      }
    },
    {
      "type": "tls_handshake",
      "status": "succeeded",
      "duration_ms": 500,
      "details": {
        "address_family": "ipv6",
        "tls_version": "TLS1.3",
        "certificate_validation": "trusted"
      }
    },
    {
      "type": "dns_query",
      "status": "failed",
      "duration_ms": 250,
      "failure": "refused",
      "details": {
        "engine": "dot",
        "address_family": "ipv6",
        "query_type": "AAAA",
        "responses": [
          {
            "arrival_index": 1,
            "arrival_offset_ms": 250,
            "rcode": "REFUSED",
            "answers": []
          }
        ]
      }
    }
  ]
}
```

### Outcomes

<a id="REQ-DNS-04-0027"></a>

**REQ-DNS-04-0027:**

| Outcome | Required terminal observation |
|---|---|
| `response` | The DoT DNS observation succeeded with a matching valid response and no DNS failure code. |
| `bootstrap_failure` | Bootstrap DNS failed; its normalized failure is retained. |
| `tcp_timeout` | TCP failed with `timeout`. |
| `tcp_refused` | TCP failed with `connection_refused`. |
| `tcp_reset` | TCP failed with `connection_reset`, or TLS failed with `connection_reset` after the TCP connect completed. |
| `tls_failure` | TLS failed; its normalized failure and certificate-validation class are retained. |
| `dns_nxdomain` | The DoT DNS observation failed with `nxdomain` and retains `rcode: NXDOMAIN`. |
| `dns_servfail` | The DoT DNS observation failed with `servfail` and retains `rcode: SERVFAIL`. |
| `dns_refused` | The DoT DNS observation failed with `refused` and retains `rcode: REFUSED`. |
| `malformed_dns_response` | The DoT DNS observation failed with `malformed_response`. |
| `query_mismatch` | The DoT DNS observation failed with `query_mismatch`. |
| `timeout` | A post-connect TLS or DNS observation failed with `timeout`; observation order identifies the stage. |
| `inconclusive` | The terminal observation failed with `inconclusive`. |

<a id="REQ-DNS-04-0028"></a>

**REQ-DNS-04-0028:**

`network_changed`, cancellation, the outer attempt deadline, proxy failure or reconfiguration, and platform suspension produce an incomplete common execution state and no `measurement` object.

<a id="REQ-DNS-04-0029"></a>

**REQ-DNS-04-0029:**

The result must not contain `resolver_name`, resolver address or port, `bootstrap_ip`, query hostname, raw DNS message, TLS certificate data, query framing bytes, or raw errors.

## Interpretation

The cross-cutting [Measurement Limitations](../measurement-limitations.md) apply to this result and any derived analysis.

### Supported Interpretation

<a id="REQ-DNS-04-0030"></a>

**REQ-DNS-04-0030:**

One execution can establish whether each observed bootstrap, TCP, TLS, and DNS stage completed for the configured resolver and query.

### Alternative Explanations

- Resolver, authoritative DNS, certificate, or routing outage.

- Bootstrap DNS failure unrelated to the DoT service.

- Resolver rate limiting, policy refusal, overload, or maintenance.

- Port-specific firewall behavior unrelated to censorship.

- VPN, captive portal, enterprise policy, or local security software.

- IPv4/IPv6 path differences or stale resolver configuration.

### Evidence Needed for Stronger Interpretation

<a id="REQ-DNS-04-0031"></a>

**REQ-DNS-04-0031:**

- Repeated DoT results on a stable network without aggressive retries.
- `DNS-01` and `DNS-03` results for the same safe query.
- A `TCP-01` and `TLS-01` observation for the approved resolver endpoint.
- Independent observations from comparable times and network contexts.

<a id="REQ-DNS-04-0032"></a>

**REQ-DNS-04-0032:**

A difference between DNS transports supports a transport-specific observation, not a conclusion about censor intent.

## Privacy and Safety

### Baseline Risk

<a id="REQ-DNS-04-0033"></a>

**REQ-DNS-04-0033:**

| Field | Value |
|---|---|
| Risk level | `medium` |
| Requires user consent | `false`, subject to host and local policy |

`medium` reflects the recognizable resolver destination and dedicated DoT transport.

### Risk Factors

<a id="REQ-DNS-04-0034"></a>

**REQ-DNS-04-0034:**

| Type | Level | Rationale and mitigation |
|---|---|---|
| `network_observability` | `medium` | The resolver destination and dedicated TCP port are visible to the network. |
| `traffic_distinctiveness` | `medium` | A connection to a known DoT endpoint is readily distinguishable from ordinary HTTPS. |
| `target_sensitivity` | `medium` | Encrypted DNS resolvers may be treated as circumvention infrastructure. |
| `data_sensitivity` | `low` | Only one reviewed query and minimized result are permitted. |
| `legal_or_social_context` | `medium` | Encrypted DNS use may carry additional risk in restrictive environments. |

### Safety Analysis

<a id="REQ-DNS-04-0035"></a>

**REQ-DNS-04-0035:**

- **Data minimization:** Retain only stage outcomes, coarse timing, and the minimal DNS properties required for interpretation.

<a id="REQ-DNS-04-0036"></a>

**REQ-DNS-04-0036:**

- **Traffic distinctiveness:** Perform one standard exchange without probing port ranges, TLS variants, or fallback behavior.

<a id="REQ-DNS-04-0037"></a>

**REQ-DNS-04-0037:**

- **User-identification risk:** Do not send identifiers, authentication, or unrelated application data.

<a id="REQ-DNS-04-0038"></a>

**REQ-DNS-04-0038:**

- **Target risk:** Resolver endpoints and query names must be locally registered and reviewed.

- **Repeated-execution risk:** Repeated use of a dedicated port can create a recognizable pattern.

- **Residual risks:** The resolver sees the query and source network; the access network sees the resolver destination and transport.

<a id="REQ-DNS-04-0039"></a>

**REQ-DNS-04-0039:**

The probe retains final authority to delay, skip, or reject execution. A task may increase the effective risk but must never lower this registered baseline.
