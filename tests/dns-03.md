# `DNS-03` DNS-over-HTTPS resolution

**Status:** `Draft`
**Version:** `0.1.0`
**Category:** `DNS resolution`

## Overview

This test sends one standards-compliant DNS query for a configured, non-sensitive hostname to an explicitly configured DNS-over-HTTPS resolver and records the stage at which the operation succeeds or fails.

A test defines registered measurement behavior. A task references the test by `test_id` and supplies the measurement input, options, execution constraints, schedule, and task-specific safety requirements.

## Purpose

### Measurement Question

Can the probe complete a DNS-over-HTTPS exchange with the configured resolver, and what DNS result does that resolver return?

### Non-goals

- The test does not configure DoH for the device or host application.
- The test does not establish that a DoH result is authoritative or correct.
- A difference from system DNS does not by itself establish interference.

## Measurement Method

### Target

One explicitly configured HTTPS resolver endpoint and one reviewed, non-sensitive query name. The resolver and query name must independently pass local safety policy.

### Operation

The probe resolves or uses an approved bootstrap address for the resolver, establishes TCP and authenticated TLS, and sends one RFC 8484 DNS wire-format query using HTTPS `POST`.

### Procedure

1. Validate the resolver URL, optional bootstrap address, query name, and record type.
2. Resolve the resolver hostname with the system resolver, unless an approved bootstrap address was supplied.
3. Connect to one selected resolver address and authenticate TLS for the resolver hostname.
4. Send one HTTPS `POST` request with media type `application/dns-message`.
5. Validate the HTTP response and parse one bounded DNS response.
6. Stop without fallback, redirect following, or application-layer retry.

### Success Condition

An authenticated HTTPS exchange returns a syntactically valid DNS message that matches the query identifier, name, and record type. The DNS response code and answer may still represent `NXDOMAIN`, `SERVFAIL`, or another DNS outcome.

### Failure Conditions

| Failure class | Required observation |
|---|---|
| `bootstrap_failure` | The resolver hostname cannot be resolved through the selected bootstrap path. |
| `tcp_failure` | TCP connection to the selected resolver address fails. |
| `tls_failure` | TLS negotiation or resolver certificate validation fails. |
| `http_failure` | The HTTPS exchange fails or returns a non-success status that does not contain a DNS response. |
| `unexpected_content_type` | The response is not a supported DNS message media type. |
| `dns_nxdomain` | A valid DNS response reports `NXDOMAIN`. |
| `dns_servfail` | A valid DNS response reports `SERVFAIL`. |
| `dns_refused` | A valid DNS response reports `REFUSED`. |
| `malformed_dns_response` | The response body cannot be parsed as the expected bounded DNS message. |
| `query_mismatch` | The response does not correspond to the submitted question. |
| `timeout` | The active protocol stage reaches its operation bound. |
| `network_changed` | The network generation changes during the run. |
| `inconclusive` | The available observation cannot be assigned safely to another class. |

## Inputs

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `resolver_url` | string | Yes | Absolute `https` URL, maximum 2,048 UTF-8 bytes; no credentials, fragment, or user-specific query parameters. | Approved RFC 8484 resolver endpoint. |
| `hostname` | string | Yes | Valid normalized DNS name, maximum 253 ASCII bytes after IDNA normalization, approved by local policy. | Name to query. |
| `record_type` | string | Yes | `A` or `AAAA`. | Requested record type. |
| `bootstrap_ip` | string | No | Canonical public IPv4 or IPv6 address approved for the resolver endpoint. | Avoids dependency on system DNS for resolver bootstrap. |

### Input Validation

- The resolver URL and optional bootstrap address must match a locally registered resolver configuration.
- The resolver certificate must be authenticated for the URL hostname even when `bootstrap_ip` is used.
- Redirect targets must not be contacted.
- Local, loopback, link-local, private, credential-bearing, or interpolated targets are rejected by default.
- Unknown fields are rejected.

Invalid input must prevent measurement execution and must not produce a measurement result that could be interpreted as network interference.

## Options

| Option | Type | Required | Default | Constraints | Description |
|---|---|:---:|---|---|---|
| `address_family` | string | No | `auto` | `auto`, `ipv4`, or `ipv6`; must be compatible with `bootstrap_ip` when present. | Selects the resolver connection family. |

GET requests, HTTP redirects, alternate endpoints, custom headers, credentials, cookies, and proxy configuration are not supported in this version.

## Preconditions

- The resolver and query name must have completed technical, privacy, and safety review.
- The configured resolver profile must be locally available; execution must not depend on downloading configuration.
- The test must run only under explicit reviewed host configuration or as an approved anomaly-triggered diagnostic.
- A stable network generation and an execution deadline must be available.

Task execution constraints and local probe policy may impose stricter preconditions.

## Resource Bounds

| Resource | Baseline limit | Behavior when reached |
|---|---|---|
| Duration | One bootstrap operation and one DoH exchange within the task deadline. | Stop at the active stage and do not fall back. |
| Requests or connections | At most one resolver connection and one HTTP request after bootstrap. | Stop after the first complete response or failure. |
| Data transferred | One DNS query and one DNS message of at most 65,535 bytes plus protocol overhead; at most 16 normalized answers are retained. | Stop reading an oversized response and classify it as malformed or unsupported. |
| Retries | None at the test layer. | A retry requires a new execution attempt. |
| Concurrency | One active run per resolver and query tuple. | Deduplicate or delay equivalent runs. |

## Output

The test uses Measurement Result `schema_version: 0.1.0` and `test.result_version: 0.1.0`.

The result contains the ordered observations that actually began:

1. a system `dns_query` when bootstrap resolution was required;
2. `tcp_connect`;
3. `tls_handshake`;
4. `http_exchange`;
5. a `doh` `dns_query` representing the DNS message returned by the authenticated HTTPS exchange.

When `bootstrap_ip` is used, the first observation is omitted. The final DNS observation retains bounded normalized answers as defined by the common [DNS Query](../data-formats/measurement-observations.md#dns-query) format.

Example:

```json
{
  "outcome": "response",
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
      "status": "succeeded",
      "duration_ms": 500,
      "details": {
        "address_family": "ipv4",
        "tls_version": "TLS1.3",
        "alpn": "h2",
        "certificate_validation": "trusted"
      }
    },
    {
      "type": "http_exchange",
      "status": "succeeded",
      "duration_ms": 500,
      "details": {
        "address_family": "ipv4",
        "protocol": "h2",
        "status_code": 200,
        "content_encoding": "identity",
        "body": {
          "bytes_processed": 45,
          "truncated": false
        }
      }
    },
    {
      "type": "dns_query",
      "status": "succeeded",
      "duration_ms": 250,
      "details": {
        "engine": "doh",
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
          }
        ]
      }
    }
  ]
}
```

### Outcomes

| Outcome | Required terminal observation |
|---|---|
| `response` | The DoH DNS observation succeeded with a matching valid response and no DNS failure code. |
| `bootstrap_failure` | The bootstrap DNS observation failed; its normalized DNS failure is retained. |
| `tcp_failure` | TCP failed; its normalized failure is retained. |
| `tls_failure` | TLS failed; its normalized failure and certificate-validation class are retained. |
| `http_failure` | HTTP failed with a normalized HTTP failure or returned a non-success status; the status is retained when available. |
| `unexpected_content_type` | HTTP failed with `unexpected_content_type`; the status may be retained, but the media-type header value is not. |
| `dns_nxdomain` | The DoH DNS observation failed with `nxdomain` and retains `rcode: NXDOMAIN`. |
| `dns_servfail` | The DoH DNS observation failed with `servfail` and retains `rcode: SERVFAIL`. |
| `dns_refused` | The DoH DNS observation failed with `refused` and retains `rcode: REFUSED`. |
| `malformed_dns_response` | The DoH DNS observation failed with `malformed_response`. |
| `query_mismatch` | The DoH DNS observation failed with `query_mismatch`. |
| `timeout` | The terminal DNS, TCP, TLS, or HTTP observation failed with its registered timeout; observation order identifies the stage. |
| `inconclusive` | The terminal observation failed with `inconclusive`. |

`network_changed`, cancellation, the outer attempt deadline, proxy failure or reconfiguration, and platform suspension produce an incomplete common execution state and no `measurement` object.

The result must not contain `resolver_url`, resolver hostname or address, `bootstrap_ip`, query hostname, raw DNS message, HTTP headers or body, certificate data, cookies, or raw errors.

## Interpretation

The cross-cutting [Measurement Limitations](../measurement-limitations.md) apply to this result and any derived analysis.

### Supported Interpretation

One execution can establish whether each observed bootstrap, TCP, TLS, HTTP, and DNS stage completed for the configured resolver and query.

### Alternative Explanations

- Resolver, authoritative DNS, CDN, or certificate outage.
- Bootstrap DNS failure unrelated to the DoH service.
- Resolver rate limiting, policy refusal, maintenance, or overload.
- VPN, proxy, captive portal, enterprise policy, or local firewall behavior.
- IPv4/IPv6 routing differences or transient packet loss.
- Stale or incorrect registered resolver configuration.

### Evidence Needed for Stronger Interpretation

- Repeated DoH results on a stable network without aggressive retries.
- `DNS-01` and `DNS-04` results for the same safe query.
- Layer-specific TCP, TLS, and HTTPS checks against approved endpoints.
- Independent observations from comparable times and network contexts.

DoH is built on several layers; a failure must be attributed to the directly observed stage rather than summarized automatically as “DoH blocking.”

## Privacy and Safety

### Baseline Risk

| Field | Value |
|---|---|
| Risk level | `medium` |
| Requires user consent | `false`, subject to host and local policy |

`medium` reflects the recognizable resolver destination and the possibility that encrypted DNS use is sensitive in the deployment environment.

### Risk Factors

| Type | Level | Rationale and mitigation |
|---|---|---|
| `network_observability` | `medium` | The resolver destination and TLS metadata remain observable even though the DNS message is encrypted. |
| `traffic_distinctiveness` | `medium` | The endpoint and fixed query pattern may identify DoH measurement traffic. |
| `target_sensitivity` | `medium` | Encrypted DNS resolvers may be blocked or treated as circumvention infrastructure. |
| `data_sensitivity` | `low` | Only one reviewed query and minimized result are permitted. |
| `legal_or_social_context` | `medium` | Contacting encrypted DNS infrastructure may carry additional risk in restrictive environments. |

### Safety Analysis

- **Data minimization:** Do not retain response bodies, full headers, resolver cookies, or address lists beyond the minimized result need.
- **Traffic distinctiveness:** Use one ordinary RFC 8484 exchange and avoid unusual headers, padding experiments, or synchronized repetition.
- **User-identification risk:** Do not send cookies, authentication, installation identifiers, or application headers.
- **Target risk:** Resolver endpoints and query names must be explicitly reviewed and locally registered.
- **Repeated-execution risk:** Repeated connections to a recognizable resolver can form a strong participation signal.
- **Residual risks:** The resolver operator sees the query and source network; the access network sees the resolver destination.

The probe retains final authority to delay, skip, or reject execution. A task may increase the effective risk but must never lower this registered baseline.
