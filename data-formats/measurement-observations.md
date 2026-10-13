# Measurement Observation Formats

**Status:** Draft  
**Version:** 0.1.0

Runtime JSON values follow the shared [strict decoding contract](json-decoding.md) in addition to this document's schema, limits, and validation rules.

## Overview

Measurement observations are ordered, bounded records of protocol or platform operations performed within one [`Measurement Result`](measurement-result.md). Registered tests select the observation types they may emit and define how those observations determine the test-specific outcome.

Observations retain normalized properties needed for interpretation without retaining raw traffic. They are not packet traces, debug logs, or independent censorship classifications.

## Common Structure

```json
{
  "type": "tcp_connect",
  "status": "succeeded",
  "duration_ms": 500,
  "details": {
    "address_family": "ipv4"
  }
}
```

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `type` | string | Yes | Registered observation type. | Selects the `details` schema. |
| `status` | string | Yes | `succeeded`, `failed`, or `incomplete` | Direct completion state of this operation. |
| `duration_ms` | integer | Yes | Non-negative multiple of 250; same quantization as the result time. | Coarse operation duration. |
| `failure` | string | Conditional | Required for `failed`; prohibited for `succeeded`; optional for `incomplete` only when registered. | Normalized operation failure. |
| `details` | object | Yes | Type-specific object. | Bounded retained properties. |

Observation order is execution order. An operation that was never attempted is omitted rather than emitted with a failed status. Unknown common or detail fields are rejected.

The initial observation types are:

- `dns_query`
- `tcp_connect`
- `tls_handshake`
- `http_exchange`

`NET-01` uses its access-only Output object rather than an observation. `NET-03` combines platform validation fields with one `http_exchange`. `NET-05` contains the observations emitted by its primitive steps.

## DNS Query

```json
{
  "type": "dns_query",
  "status": "succeeded",
  "duration_ms": 250,
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
      }
    ]
  }
}
```

### Failures

Initial normalized DNS failures are:

- `nxdomain`
- `no_data`
- `servfail`
- `refused`
- `timeout`
- `resolver_error`
- `malformed_response`
- `unexpected_source`
- `query_mismatch`
- `inconclusive`

DNS response codes such as `NXDOMAIN`, `SERVFAIL`, and `REFUSED` may be represented both as a failed observation with the corresponding normalized failure and, when safely available, as a bounded response. A system resolver that does not expose a response code must not invent one.

### Details

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `engine` | string | Yes | `system`, `udp`, `tcp`, `doh`, or `dot` | Resolver operation used by the registered test. |
| `address_family` | string | No | `ipv4`, `ipv6`, or `unknown` | Family used to reach an explicit resolver; omitted when not observable or not applicable. |
| `query_type` | string | Yes | `A` or `AAAA` in the initial tests. | Requested record type. |
| `responses` | array | Yes | At most 3; empty when no response was safely parsed. | Ordered matching DNS responses. |
| `response_limit_reached` | boolean | No | Present and `true` only when the registered count bound stopped collection. | Indicates that more matching UDP responses may have existed. |

The object does not retain a resolver address, resolver provider, system DNS configuration, raw DNS message, query identifier, flags other than the response code, authority section, additional section, or unrelated answer types.

### DNS Response

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `arrival_index` | integer | Yes | Positive and sequential within the observation. | Preserves matching-response arrival order. |
| `arrival_offset_ms` | integer | Yes | Quantized non-negative duration from operation start. | Coarse relative response timing. |
| `rcode` | string | Yes | Registered uppercase DNS response-code name. | Directly observed response code. |
| `answers` | array | Yes | At most 16 normalized answers, including at most 8 CNAME entries; may be empty. | Relevant answer values from this response. |

### DNS Answer

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `type` | string | Yes | `A`, `AAAA`, or `CNAME` | Normalized answer type. |
| `value` | string | Yes | Canonical public IP address for `A` or `AAAA`; normalized DNS name for `CNAME`. | Answer value required to compare response sets. |

Answers preserve first occurrence order and remove exact duplicates within one response. TTLs are omitted because cache and platform behavior make them inconsistent and they are not required by the initial measurement questions.

Exact answer retention is limited to reviewed, non-sensitive query names, 16 entries per response, and a 16,384-byte encoded DNS observation. Implementations must not enrich answers on-device with ASN, organization, geolocation, reputation, or a censorship verdict.

## TCP Connect

```json
{
  "type": "tcp_connect",
  "status": "failed",
  "duration_ms": 1000,
  "failure": "connection_refused",
  "details": {
    "address_family": "ipv6"
  }
}
```

### Failures

- `timeout`
- `connection_refused`
- `connection_reset`
- `network_unreachable`
- `address_unreachable`
- `permission_denied`
- `socket_error`
- `inconclusive`

Cross-cutting termination such as network change, host cancellation, proxy reconfiguration, or the outer attempt deadline belongs to `execution.reason` rather than this failure list.

### Details

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `address_family` | string | Yes | `ipv4` or `ipv6` | Family of the attempted destination. |

The observation does not repeat the destination address or port. Those values are resolved through the validated task or enclosing `NET-05` step.

## TLS Handshake

```json
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
```

### Failures

- `timeout`
- `connection_reset`
- `alert`
- `protocol_error`
- `certificate_untrusted`
- `certificate_name_mismatch`
- `certificate_time_invalid`
- `alpn_no_overlap`
- `inconclusive`

An underlying TCP failure is emitted as a preceding `tcp_connect` observation. A TLS observation is emitted only when TLS activity began.

### Details

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `address_family` | string | Yes | `ipv4` or `ipv6` | Family of the established TCP stream. |
| `tls_version` | string | No | Registered normalized negotiated version. | Present only when negotiation produced a version. |
| `alpn` | string | No | Registered ASCII ALPN value of 1–32 bytes. | Present only when a protocol was negotiated. |
| `certificate_validation` | string | Yes | `trusted`, `untrusted`, `name_mismatch`, `time_invalid`, `not_completed`, or `inconclusive` | Minimized certificate-validation outcome. |
| `alert` | string | No | Registered coarse TLS alert class. | Present only when needed to support an `alert` failure. |

The observation must not retain a certificate, certificate-chain element, issuer or subject name, serial number, key, signature, fingerprint, ClientHello, ServerHello, cipher list, session identifier, or TLS secret.

## HTTP Exchange

```json
{
  "type": "http_exchange",
  "status": "succeeded",
  "duration_ms": 1000,
  "details": {
    "address_family": "ipv6",
    "protocol": "h2",
    "status_code": 200,
    "body": {
      "bytes_processed": 512,
      "truncated": false
    },
    "checks": [
      {
        "kind": "status",
        "index": 0,
        "matched": true
      }
    ]
  }
}
```

### Failures

- `timeout`
- `protocol_error`
- `redirect_rejected`
- `redirect_limit_reached`
- `unexpected_status`
- `header_check_failed`
- `body_check_failed`
- `body_limit_reached`
- `unsupported_content_encoding`
- `unexpected_content_type`
- `unexpected_response`
- `inconclusive`

DNS, TCP, and TLS failures are emitted using their respective preceding observation types. An HTTP observation is emitted only after HTTP activity began.

### Details

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `address_family` | string | Yes | `ipv4`, `ipv6`, or `unknown` | Selected endpoint family when observable. |
| `protocol` | string | Yes | `http/1.1`, `h2`, or `unknown` | Negotiated application protocol. |
| `status_code` | integer | No | Valid HTTP status code. | Present when a valid response status was received. |
| `redirect` | object | No | Complete minimized redirect object. | Present when at least one redirect was observed. |
| `body` | object | No | Complete bounded body-processing summary. | Present when body processing began. |
| `checks` | array | No | At most 17 results: one status, 8 header, and 8 body checks. | Present when checks were configured and evaluated. |
| `content_encoding` | string | No | `identity`, `unsupported`, or `unknown` | Retained only when needed to interpret body-check handling. |

### Redirect

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `followed_count` | integer | Yes | Integer from 0 through 2. | Number of approved redirect targets contacted. |
| `terminal_location_class` | string | Yes | `registered_https`, `unregistered_https`, `non_https`, `credentials`, `prohibited_host`, or `invalid` | Minimized class of the last observed redirect target. |

The full redirect URL, hostname, path, query, and fragment are not retained. A redirect that is not contacted may still be classified after bounded safe parsing.

### Body

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `bytes_processed` | integer | Yes | Non-negative and no greater than the configured bound. | Application body bytes evaluated by the test. |
| `truncated` | boolean | Yes | — | Whether the byte bound stopped processing before the body completed. |

The body content and computed body digest are not retained. A configured expected digest remains in the task and only its check outcome is reported.

### Check

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `kind` | string | Yes | `status`, `header`, or `body` | Kind of configured check. |
| `index` | integer | Yes | Zero-based index in the applicable task input list; status uses `0`. | Links the result to a configured check without copying its value. |
| `matched` | boolean | Yes | — | Whether the check matched. |

Header names, header values, expected strings, expected digests, actual body bytes, and actual digests are not retained.

## Validation and Bounds

- A test may emit only observation types listed by its Output schema.
- Observations must appear in execution order.
- At most one terminal failed or incomplete observation may appear in one primitive test result.
- A succeeded observation must not contain `failure`.
- A failed observation must contain a failure registered for its type.
- Detail fields must be consistent with status and failure.
- Counts, strings, response arrays, answer arrays, redirects, checks, and total encoded size must satisfy [`Registered Initial Limits`](../library/registered-limits.md).
- A target, resolver, or redirect address must not be added merely because a lower-level networking API exposed it.
- Raw errors must map conservatively to registered values; otherwise use `inconclusive`.

## Privacy and Interpretation

These formats intentionally retain less information than a general network event log. They omit raw bytes and identifiers that are unnecessary for the initial measurement questions.

Observation order and stage failure can support layer-specific analysis, but they do not establish intent. A failed TLS observation following a successful TCP observation establishes only that the observed TCP stage completed and the TLS stage did not complete normally under that test configuration.
