# `DNS-01` DNS resolution

**Status:** `Draft`
**Version:** `0.1.0`
**Category:** `DNS resolution`

## Overview

This test resolves one configured, non-sensitive hostname through either the device's normal system resolver or one explicitly configured DNS server. In direct UDP mode, it can retain multiple response datagrams matching the same query during a bounded observation window.

A test defines registered measurement behavior. A task references the test by `test_id` and supplies the measurement input, options, execution constraints, schedule, and task-specific safety requirements.

## Purpose

### Measurement Question

What result does the selected system or direct DNS path return for the configured hostname and record type, and does direct UDP receive conflicting responses for the same query?

### Non-goals

<a id="REQ-DNS-01-0001"></a>

**REQ-DNS-01-0001:**

- The test does not determine whether an unexpected answer was introduced intentionally.

<a id="REQ-DNS-01-0002"></a>

**REQ-DNS-01-0002:**

- The test does not establish that a returned address is reachable.

<a id="REQ-DNS-01-0003"></a>

**REQ-DNS-01-0003:**

- The test does not compare against an authoritative ground truth within the same run.

<a id="REQ-DNS-01-0004"></a>

**REQ-DNS-01-0004:**

- The test does not automatically classify the first or a later response as spoofed, injected, legitimate, or authoritative.

## Measurement Method

### Target

<a id="REQ-DNS-01-0005"></a>

**REQ-DNS-01-0005:**

One configured hostname approved by local safety policy.

<a id="REQ-DNS-01-0006"></a>

**REQ-DNS-01-0006:**

In `system` mode, the operating system and active network select the resolver. In `direct` mode, the task selects one explicitly configured, safety-reviewed DNS server address and port.

### Operation

<a id="REQ-DNS-01-0007"></a>

**REQ-DNS-01-0007:**

In `system` mode, the probe invokes the platform's ordinary name-resolution path and normalizes the result exposed by that API.

<a id="REQ-DNS-01-0008"></a>

**REQ-DNS-01-0008:**

In `direct` mode, the Go core sends one DNS query over UDP or TCP to the configured server. Direct UDP may keep the socket open after the first matching response and collect additional matching datagrams until the configured observation window or response-count bound is reached.

<a id="REQ-DNS-01-0009"></a>

**REQ-DNS-01-0009:**

The test must not change system resolver configuration, query additional names, or fall back silently between system and direct modes or between transports.

### Procedure

<a id="REQ-DNS-01-0010"></a>

**REQ-DNS-01-0010:**

1. Validate and normalize the hostname, record type, resolver mode, and mode-specific configuration.
2. Record the current network generation.
3. In `system` mode, resolve the hostname using the system resolver.
4. In `direct` mode, send one DNS query to the configured server using the selected transport.
5. In direct UDP mode, validate the response source, transaction ID, and question. When additional-response collection is enabled, continue reading matching response datagrams within the configured bounds.
6. Preserve response arrival order, coarse relative timing, response code, and normalized answer properties.
7. Discard unrelated datagrams and resolver metadata and stop if the network changes.

### Success Condition

<a id="REQ-DNS-01-0011"></a>

**REQ-DNS-01-0011:**

The selected resolver path returns at least one syntactically valid result for the requested record type. A valid `NXDOMAIN` or empty answer is an observed DNS outcome, not a successful address resolution.

<a id="REQ-DNS-01-0012"></a>

**REQ-DNS-01-0012:**

In direct UDP mode, receiving multiple matching responses is a valid measurement outcome. Conflicting answers are retained as conflicting observations without deciding which response is correct.

### Failure Conditions

<a id="REQ-DNS-01-0013"></a>

**REQ-DNS-01-0013:**

| Failure class | Required observation |
|---|---|
| `nxdomain` | The selected resolver path reports that the queried name does not exist. |
| `no_data` | The name exists but no answer of the requested type is returned. |
| `servfail` | The selected resolver reports a server failure when that distinction is observable. |
| `refused` | The selected resolver refuses the query when that distinction is observable. |
| `timeout` | Resolution does not complete within the operation bound. |
| `resolver_error` | The platform reports another resolver failure. |
| `malformed_response` | A response cannot be normalized or parsed safely. |
| `unexpected_source` | A direct UDP datagram purporting to match the query arrives from an unexpected source. |
| `query_mismatch` | A direct response does not match the transaction ID or question. |
| `conflicting_responses` | Two or more matching direct UDP responses contain materially different response codes or normalized answer sets. |
| `response_limit_reached` | The direct UDP response-count bound is reached before the observation window ends. |
| `network_changed` | The network generation changes during resolution. |
| `inconclusive` | Platform error mapping is too coarse to select another class. |

## Inputs

<a id="REQ-DNS-01-0014"></a>

**REQ-DNS-01-0014:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `hostname` | string | Yes | Valid normalized DNS name, maximum 253 ASCII bytes after IDNA normalization; no URL, credentials, wildcard, or runtime interpolation. | Name to resolve. |
| `record_type` | string | Yes | `A` or `AAAA`. | Requested address record type. |
| `resolver` | object | Conditional | Required only in `direct` mode; must match a locally registered server. | Direct resolver configuration containing `ip_address` and optional `port`. |

The `resolver` object has the following fields:

<a id="REQ-DNS-01-0015"></a>

**REQ-DNS-01-0015:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `ip_address` | string | Yes | Canonical public IPv4 or IPv6 address approved by local safety policy. | Direct DNS server address. |
| `port` | integer | No | `1` through `65535`; omitted value uses the versioned DNS default. | Direct DNS server port. |

### Input Validation

<a id="REQ-DNS-01-0016"></a>

**REQ-DNS-01-0016:**

- Internationalized names must use a deterministic, documented normalization compatible with the implementation version.

<a id="REQ-DNS-01-0017"></a>

**REQ-DNS-01-0017:**

- Root, single-label, local-search, `.local`, loopback, and private namespace targets require explicit support and are rejected by default.

<a id="REQ-DNS-01-0018"></a>

**REQ-DNS-01-0018:**

- The hostname must pass local target-safety policy.

<a id="REQ-DNS-01-0019"></a>

**REQ-DNS-01-0019:**

- `resolver` must be absent in `system` mode and present in `direct` mode.

<a id="REQ-DNS-01-0020"></a>

**REQ-DNS-01-0020:**

- A direct resolver address and port must match a locally available, safety-reviewed resolver registration.

<a id="REQ-DNS-01-0021"></a>

**REQ-DNS-01-0021:**

- Loopback, link-local, private, multicast, unspecified, and other prohibited resolver addresses are rejected by default.

<a id="REQ-DNS-01-0022"></a>

**REQ-DNS-01-0022:**

- CNAMEs returned by the resolver may be observed, but the test must not start additional application connections.

<a id="REQ-DNS-01-0023"></a>

**REQ-DNS-01-0023:**

- Unknown fields are rejected.

<a id="REQ-DNS-01-0024"></a>

**REQ-DNS-01-0024:**

Invalid input must prevent measurement execution and must not produce a measurement result that could be interpreted as network interference.

## Options

<a id="REQ-DNS-01-0025"></a>

**REQ-DNS-01-0025:**

| Option | Type | Required | Default | Constraints | Description |
|---|---|:---:|---|---|---|
| `resolver_mode` | string | No | `system` | `system` or `direct`. | Selects the ordinary system resolver or an explicitly configured server. |
| `transport` | string | No | `udp` | `udp` or `tcp`; valid only in `direct` mode. | Direct DNS transport. |
| `collect_additional_responses` | boolean | No | `false` | May be `true` only in direct UDP mode. | Continue receiving matching datagrams after the first response. |
| `additional_response_window_ms` | integer | Conditional | — | Required when additional-response collection is enabled; `1` through `10,000`. | Time to continue reading after the first matching response. |

<a id="REQ-DNS-01-0026"></a>

**REQ-DNS-01-0026:**

Unknown options are rejected. Direct mode must never fall back silently to the system resolver, another server, or another transport.

## Preconditions

<a id="REQ-DNS-01-0027"></a>

**REQ-DNS-01-0027:**

- The network generation must be stable enough to associate the result with one path.

<a id="REQ-DNS-01-0028"></a>

**REQ-DNS-01-0028:**

- The configured hostname must be approved and expected to have known operational ownership.

<a id="REQ-DNS-01-0029"></a>

**REQ-DNS-01-0029:**

- A direct resolver must be locally registered and approved for the deployment context.

<a id="REQ-DNS-01-0030"></a>

**REQ-DNS-01-0030:**

- The test must not run when the only available resolver API would expose or retain unrelated system DNS activity.

<a id="REQ-DNS-01-0031"></a>

**REQ-DNS-01-0031:**

- Direct UDP collection must have explicit observation-window and response-count bounds when additional responses are enabled.

<a id="REQ-DNS-01-0032"></a>

**REQ-DNS-01-0032:**

Task execution constraints and local probe policy may impose stricter preconditions.

## Resource Bounds

<a id="REQ-DNS-01-0033"></a>

**REQ-DNS-01-0033:**

| Resource | Baseline limit | Behavior when reached |
|---|---|---|
| Duration | One resolution plus an optional bounded direct UDP observation window within the task execution deadline. | Stop reading when the applicable bound is reached. |
| Requests or connections | One logical system lookup or one direct DNS query. | Do not query another name, server, or transport. |
| Data transferred | Resolver-controlled traffic in system mode; one query and at most three matching responses in direct UDP mode; 4,096-byte UDP or 65,535-byte TCP message maximum. | Stop retaining at three responses or reject an oversized message. |
| Retries | None at the test layer. | Internal resolver behavior may be opaque and must be documented as a limitation. |
| Concurrency | One run per hostname, record type, mode, and resolver tuple on a network generation. | Deduplicate or delay equivalent concurrent runs. |

## Output

<a id="REQ-DNS-01-0034"></a>

**REQ-DNS-01-0034:**

The test uses Measurement Result `schema_version: 0.1.0` and `test.result_version: 0.1.0`.

<a id="REQ-DNS-01-0035"></a>

**REQ-DNS-01-0035:**

A completed result contains exactly one [`dns_query` observation](../data-formats/measurement-observations.md#dns-query). System mode retains only information exposed by the selected resolver API and must not synthesize response datagrams, response codes, or timing that the API did not expose.

<a id="REQ-DNS-01-0036"></a>

**REQ-DNS-01-0036:**

Direct UDP mode may retain at most three matching responses in arrival order. Each response retains at most 16 normalized `A`, `AAAA`, and intervening `CNAME` entries, including at most eight CNAME entries. The encoded DNS observation must not exceed 16,384 bytes. Raw DNS messages, unrelated records, TTLs, and resolver addresses are prohibited.

Example conflicting direct UDP result:

```json
{
  "outcome": "conflicting_responses",
  "observations": [
    {
      "type": "dns_query",
      "status": "succeeded",
      "duration_ms": 500,
      "details": {
        "engine": "udp",
        "address_family": "ipv4",
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
          },
          {
            "arrival_index": 2,
            "arrival_offset_ms": 500,
            "rcode": "NOERROR",
            "answers": [
              {
                "type": "A",
                "value": "8.8.8.8"
              }
            ]
          }
        ]
      }
    }
  ]
}
```

### Outcomes

<a id="REQ-DNS-01-0037"></a>

**REQ-DNS-01-0037:**

| Outcome | Required observation |
|---|---|
| `resolved` | At least one response or system result contains an answer of the requested type and no higher-priority bounded collection condition applies. |
| `nxdomain` | DNS failed with `nxdomain`; a response with `rcode: NXDOMAIN` is retained when observable. |
| `no_data` | DNS failed with `no_data`, or a valid response has no requested-type answer. |
| `servfail` | DNS failed with `servfail`; a response with `rcode: SERVFAIL` is retained when observable. |
| `refused` | DNS failed with `refused`; a response with `rcode: REFUSED` is retained when observable. |
| `timeout` | DNS failed with `timeout`. |
| `resolver_error` | DNS failed with `resolver_error`. |
| `malformed_response` | DNS failed with `malformed_response`. |
| `unexpected_source` | No usable matching result was obtained and direct UDP terminated with `unexpected_source`. |
| `query_mismatch` | No usable matching result was obtained and direct resolution terminated with `query_mismatch`. |
| `conflicting_responses` | Two or more retained matching direct UDP responses have different response codes or normalized answer sets. |
| `response_limit_reached` | The direct UDP count bound ended collection; `response_limit_reached: true` is present. Retained responses remain ordered and uninterpreted. |
| `inconclusive` | DNS failed with `inconclusive`. |

<a id="REQ-DNS-01-0038"></a>

**REQ-DNS-01-0038:**

When valid matching responses and unrelated or mismatched datagrams are both observed, unrelated datagrams are discarded and do not override a usable terminal outcome. `conflicting_responses` takes precedence over `resolved`; `response_limit_reached` takes precedence when the count bound prevents determining whether later responses would conflict.

<a id="REQ-DNS-01-0039"></a>

**REQ-DNS-01-0039:**

`network_changed`, cancellation, the outer attempt deadline, proxy failure or reconfiguration, and platform suspension produce an incomplete common execution state and no `measurement` object.

<a id="REQ-DNS-01-0040"></a>

**REQ-DNS-01-0040:**

The result must not contain the queried hostname, direct resolver address or port, system resolver configuration, query identifier, raw message, authority or additional sections, TTL, answer ASN or organization, local address, or platform error text.

## Interpretation

The cross-cutting [Measurement Limitations](../measurement-limitations.md) apply to this result and any derived analysis.

### Supported Interpretation

<a id="REQ-DNS-01-0041"></a>

**REQ-DNS-01-0041:**

One execution can establish only the result exposed by the selected resolver path for the configured name, record type, time, and network generation.

<a id="REQ-DNS-01-0042"></a>

**REQ-DNS-01-0042:**

In direct UDP mode, it can additionally establish that multiple matching response datagrams arrived and whether their normalized contents differed. It cannot establish automatically which response was injected or correct.

### Alternative Explanations

- Authoritative DNS or recursive resolver outage.

- DNSSEC validation failure, stale cache, negative caching, split-horizon DNS, or DNS64 behavior.

- Misconfigured, expired, or recently changed DNS records.

- Captive portal, VPN, enterprise resolver, or local filtering.

- Platform-specific error collapsing.

- Direct resolver outage, filtering, rate limiting, or routing failure.

- A legitimate resolver retransmission or anycast change that produces different observations.

### Evidence Needed for Stronger Interpretation

<a id="REQ-DNS-01-0043"></a>

**REQ-DNS-01-0043:**

- Repeated system and direct results on a stable network.
- Comparison of direct responses with authoritative information under a separately reviewed method.
- `DNS-03` and `DNS-04` observations for the same safe query where permitted.
- TCP, TLS, or HTTPS measurements to approved expected endpoints.
- Independent observations from comparable times and network contexts.

<a id="REQ-DNS-01-0044"></a>

**REQ-DNS-01-0044:**

A difference between resolvers is evidence of differing observations, not proof that either resolver is correct or that censorship occurred.

## Privacy and Safety

### Baseline Risk

<a id="REQ-DNS-01-0045"></a>

**REQ-DNS-01-0045:**

| Field | Value |
|---|---|
| Risk level | `low` |
| Requires user consent | `false`, subject to host and local policy |

### Risk Factors

<a id="REQ-DNS-01-0046"></a>

**REQ-DNS-01-0046:**

| Type | Level | Rationale and mitigation |
|---|---|---|
| `network_observability` | `low` | The configured query and selected resolver destination are visible to the active network path. |
| `traffic_distinctiveness` | `low` | One ordinary lookup is low-volume; direct use of a fixed resolver may still be recognizable. |
| `target_sensitivity` | `low` | Only reviewed, non-sensitive names and approved resolvers are permitted. |
| `data_sensitivity` | `low` | Results are minimized and must not include unrelated resolver state. |
| `legal_or_social_context` | `low` | Query names can still be sensitive in some environments, so deployment review remains required. |

### Safety Analysis

<a id="REQ-DNS-01-0047"></a>

**REQ-DNS-01-0047:**

- **Data minimization:** Retain only the requested type, coarse outcome, timing, and normalized answer properties required for interpretation.

<a id="REQ-DNS-01-0048"></a>

**REQ-DNS-01-0048:**

- **Traffic distinctiveness:** Use ordinary DNS messages without unusual flags or record types. Direct resolver use and repeated collection must be scheduled conservatively.

<a id="REQ-DNS-01-0049"></a>

**REQ-DNS-01-0049:**

- **User-identification risk:** Do not attach installation identifiers or copy unrelated DNS cache contents.

<a id="REQ-DNS-01-0050"></a>

**REQ-DNS-01-0050:**

- **Target risk:** Permit only non-sensitive, reviewed hostnames and direct resolvers.

<a id="REQ-DNS-01-0051"></a>

**REQ-DNS-01-0051:**

- **Repeated-execution risk:** Repeated queries for a fixed name can form a recognizable pattern and must be host-scheduled conservatively.

- **Residual risks:** The selected resolver and network can observe the queried hostname; direct resolver use may be treated differently by the network, and answer information may indirectly reveal network configuration.

<a id="REQ-DNS-01-0052"></a>

**REQ-DNS-01-0052:**

The probe retains final authority to delay, skip, or reject execution. A task may increase the effective risk but must never lower this registered baseline.
