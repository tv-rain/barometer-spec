# Measurement Observation Formats

**Status:** Draft  
**Version:** 0.1.0

Runtime JSON values follow the shared [strict decoding contract](json-decoding.md) in addition to this document's schema, limits, and validation rules.

## Overview

<a id="REQ-OBS-0001"></a>

**REQ-OBS-0001:**

Measurement observations are ordered, bounded records of protocol or platform operations performed within one [`Measurement Result`](measurement-result.md). Registered tests select the observation types they may emit and define how those observations determine the test-specific outcome.

<a id="REQ-OBS-0002"></a>

**REQ-OBS-0002:**

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

<a id="REQ-OBS-0003"></a>

**REQ-OBS-0003:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `type` | string | Yes | Registered observation type. | Selects the `details` schema. |
| `status` | string | Yes | `succeeded`, `failed`, or `incomplete` | Direct completion state of this operation. |
| `duration_ms` | integer | Yes | Non-negative multiple of 250; same quantization as the result time. | Coarse operation duration. |
| `failure` | string | Conditional | Required for `failed`; prohibited for `succeeded`; optional for `incomplete` only when registered. | Normalized operation failure. |
| `details` | object | Yes | Type-specific object. | Bounded retained properties. |

<a id="REQ-OBS-0004"></a>

**REQ-OBS-0004:**

Observation order is execution order. An operation that was never attempted is omitted rather than emitted with a failed status. Unknown common or detail fields are rejected.

<a id="REQ-OBS-0005"></a>

**REQ-OBS-0005:**

The initial observation types are:

- `dns_query`
- `tcp_connect`
- `tls_handshake`
- `http_exchange`

<a id="REQ-OBS-0006"></a>

**REQ-OBS-0006:**

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

<a id="REQ-OBS-0007"></a>

**REQ-OBS-0007:**

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

<a id="REQ-OBS-0008"></a>

**REQ-OBS-0008:**

DNS response codes such as `NXDOMAIN`, `SERVFAIL`, and `REFUSED` may be represented both as a failed observation with the corresponding normalized failure and, when safely available, as a bounded response. A system resolver that does not expose a response code must not invent one.

### Details

<a id="REQ-OBS-0009"></a>

**REQ-OBS-0009:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `engine` | string | Yes | `system`, `udp`, `tcp`, `doh`, or `dot` | Resolver operation used by the registered test. |
| `address_family` | string | No | `ipv4`, `ipv6`, or `unknown` | Family used to reach an explicit resolver; omitted when not observable or not applicable. |
| `query_type` | string | Yes | `A` or `AAAA` in the initial tests. | Requested record type. |
| `responses` | array | Yes | At most 3; empty when no response was safely parsed. | Ordered matching DNS responses. |
| `response_limit_reached` | boolean | No | Present and `true` only when the registered count bound stopped collection. | Indicates that more matching UDP responses may have existed. |

<a id="REQ-OBS-0010"></a>

**REQ-OBS-0010:**

The object does not retain a resolver address, resolver provider, system DNS configuration, raw DNS message, query identifier, flags other than the response code, authority section, additional section, or unrelated answer types.

### DNS Response

<a id="REQ-OBS-0011"></a>

**REQ-OBS-0011 (retired):**

The historical DNS response table used an undefined registered response-code vocabulary. [REQ-OBS-0042](#REQ-OBS-0042) replaces that table with an explicit normalized value contract; historical revisions remain available.

<a id="REQ-OBS-0042"></a>

**REQ-OBS-0042:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `arrival_index` | integer | Yes | Positive and sequential within the observation. | Preserves matching-response arrival order. |
| `arrival_offset_ms` | integer | Yes | Quantized non-negative duration from operation start. | Coarse relative response timing. |
| `rcode` | string | Yes | One value from [DNS response-code normalization](#dns-response-code-normalization). | Normalized directly observed response code; `OTHER` is a coarse class. |
| `answers` | array | Yes | At most 16 normalized answers, including at most 8 CNAME entries; may be empty. | Relevant answer values from this response. |

### DNS Answer

<a id="REQ-OBS-0012"></a>

**REQ-OBS-0012:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `type` | string | Yes | `A`, `AAAA`, or `CNAME` | Normalized answer type. |
| `value` | string | Yes | Canonical public IP address for `A` or `AAAA`; normalized DNS name for `CNAME`. | Answer value required to compare response sets. |

<a id="REQ-OBS-0013"></a>

**REQ-OBS-0013:**

Answers preserve first occurrence order and remove exact duplicates within one response. TTLs are omitted because cache and platform behavior make them inconsistent and they are not required by the initial measurement questions.

<a id="REQ-OBS-0014"></a>

**REQ-OBS-0014:**

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

<a id="REQ-OBS-0015"></a>

**REQ-OBS-0015:**

- `timeout`
- `connection_refused`
- `connection_reset`
- `network_unreachable`
- `address_unreachable`
- `permission_denied`
- `socket_error`
- `inconclusive`

<a id="REQ-OBS-0016"></a>

**REQ-OBS-0016:**

Cross-cutting termination such as network change, host cancellation, proxy reconfiguration, or the outer attempt deadline belongs to `execution.reason` rather than this failure list.

### Details

<a id="REQ-OBS-0017"></a>

**REQ-OBS-0017:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `address_family` | string | Yes | `ipv4` or `ipv6` | Family of the attempted destination. |

<a id="REQ-OBS-0018"></a>

**REQ-OBS-0018:**

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

<a id="REQ-OBS-0019"></a>

**REQ-OBS-0019:**

- `timeout`
- `connection_reset`
- `alert`
- `protocol_error`
- `certificate_untrusted`
- `certificate_name_mismatch`
- `certificate_time_invalid`
- `alpn_no_overlap`
- `inconclusive`

<a id="REQ-OBS-0020"></a>

**REQ-OBS-0020:**

An underlying TCP failure is emitted as a preceding `tcp_connect` observation. A TLS observation is emitted only when TLS activity began.

### Details

<a id="REQ-OBS-0021"></a>

**REQ-OBS-0021 (retired):**

The historical TLS detail table referenced undefined registered vocabularies. [REQ-OBS-0043](#REQ-OBS-0043) replaces it with explicit negotiated-property and alert vocabularies; historical revisions remain available.

<a id="REQ-OBS-0043"></a>

**REQ-OBS-0043:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `address_family` | string | Yes | `ipv4` or `ipv6` | Family of the established TCP stream. |
| `tls_version` | string | No | `TLS1.2`, `TLS1.3`, or `unknown`, using [negotiated-property normalization](#tls-negotiated-properties). | Present only when negotiation produced a version. |
| `alpn` | string | No | `http/1.1`, `h2`, `dot`, or `unknown`, using [negotiated-property normalization](#tls-negotiated-properties). | Present only when a protocol was negotiated; `unknown` is a coarse marker, not an ALPN identifier. |
| `certificate_validation` | string | Yes | `trusted`, `untrusted`, `name_mismatch`, `time_invalid`, `not_completed`, or `inconclusive` | Minimized certificate-validation outcome. |
| `alert` | string | No | One class from [TLS peer-alert normalization](#tls-peer-alert-normalization). | Present only when needed to support an `alert` failure. |

<a id="REQ-OBS-0022"></a>

**REQ-OBS-0022:**

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

<a id="REQ-OBS-0023"></a>

**REQ-OBS-0023:**

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

<a id="REQ-OBS-0024"></a>

**REQ-OBS-0024:**

DNS, TCP, and TLS failures are emitted using their respective preceding observation types. An HTTP observation is emitted only after HTTP activity began.

### Details

<a id="REQ-OBS-0025"></a>

**REQ-OBS-0025:**

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

<a id="REQ-OBS-0026"></a>

**REQ-OBS-0026:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `followed_count` | integer | Yes | Integer from 0 through 2. | Number of approved redirect targets contacted. |
| `terminal_location_class` | string | Yes | `registered_https`, `unregistered_https`, `non_https`, `credentials`, `prohibited_host`, or `invalid` | Minimized class of the last observed redirect target. |

<a id="REQ-OBS-0027"></a>

**REQ-OBS-0027:**

The full redirect URL, hostname, path, query, and fragment are not retained. A redirect that is not contacted may still be classified after bounded safe parsing.

### Body

<a id="REQ-OBS-0028"></a>

**REQ-OBS-0028:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `bytes_processed` | integer | Yes | Non-negative and no greater than the configured bound. | Application body bytes evaluated by the test. |
| `truncated` | boolean | Yes | — | Whether the byte bound stopped processing before the body completed. |

<a id="REQ-OBS-0029"></a>

**REQ-OBS-0029:**

The body content and computed body digest are not retained. A configured expected digest remains in the task and only its check outcome is reported.

### Check

<a id="REQ-OBS-0030"></a>

**REQ-OBS-0030:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `kind` | string | Yes | `status`, `header`, or `body` | Kind of configured check. |
| `index` | integer | Yes | Zero-based index in the applicable task input list; status uses `0`. | Links the result to a configured check without copying its value. |
| `matched` | boolean | Yes | — | Whether the check matched. |

<a id="REQ-OBS-0031"></a>

**REQ-OBS-0031:**

Header names, header values, expected strings, expected digests, actual body bytes, and actual digests are not retained.

## Registered Normalized Vocabularies

### Contract Selection and Producer Boundary

<a id="REQ-OBS-0044"></a>

**REQ-OBS-0044:**

The vocabularies below are closed Barometer `0.1.0` vocabularies selected by the containing result/test contract. External registries and library upgrades do not expand them automatically; no runtime registry lookup is permitted. Adding a value requires public specification review and an explicit compatibility/version disposition. These definitions do not add serialized version fields or change permitted network operations, handshake profiles, targets, retries, or fallback paths.

<a id="REQ-OBS-0045"></a>

**REQ-OBS-0045:**

Normalization applies to safely observed protocol/platform data before constructing an observation. Decoders of serialized observations must reject values outside the closed vocabulary, including aliases, incorrect case, numeric strings and raw library messages; they must not repair them into `OTHER`, `other`, `unknown` or `inconclusive`. A coarse marker is valid only where explicitly listed. Missing evidence, malformed protocol data and a directly observed value outside the retained subset are distinct cases.

### DNS Response-Code Normalization

The numeric meanings of the initial six codes follow the [IANA DNS RCODE registry](https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml#dns-parameters-6). Barometer's retained subset and the `OTHER` marker are project choices, not an automatic adoption of that external registry.

<a id="REQ-OBS-0046"></a>

**REQ-OBS-0046:**

For a safely parsed, matching DNS response with a reliable effective response code, producers must use this exact mapping:

| Observed effective code | Retained `rcode` |
|---|---|
| 0 | `NOERROR` |
| 1 | `FORMERR` |
| 2 | `SERVFAIL` |
| 3 | `NXDOMAIN` |
| 4 | `NOTIMP` |
| 5 | `REFUSED` |
| Any other valid effective code | `OTHER` |

The effective code includes safely parsed extended response-code bits when present; producers must not misreport the low header bits as the complete code. If the resolver API does not expose a reliable code, omit that response record rather than inventing a code or using `OTHER`. Malformed or nonmatching messages do not become valid responses through this mapping. Raw numeric codes, private-use labels and additional diagnostic strings must not be retained.

<a id="REQ-OBS-0047"></a>

**REQ-OBS-0047:**

`OTHER` records a directly observed code outside the retained subset; it does not mean success, no response, malformed response or censorship. Existing `NXDOMAIN`, `SERVFAIL`, `REFUSED` and no-data outcome rules remain applicable. A valid nonzero code without a more specific registered failure maps conservatively to `inconclusive`; it must not be converted to `NOERROR` or `no_data`. This mapping does not change response order, answer retention, collection bounds or test-specific outcome precedence.

### TLS Negotiated Properties

TLS 1.2 and 1.3 are defined by [RFC 5246](https://www.rfc-editor.org/rfc/rfc5246.html) and [RFC 8446](https://www.rfc-editor.org/rfc/rfc8446.html). The selected ALPN identifiers appear in the [IANA ALPN registry](https://www.iana.org/assignments/tls-extensiontype-values/tls-extensiontype-values.xhtml#alpn-protocol-ids); Barometer deliberately retains a fixed subset.

<a id="REQ-OBS-0048"></a>

**REQ-OBS-0048:**

When negotiation produced a reliably exposed version, producers must retain `TLS1.2` for negotiated version `0x0303`, `TLS1.3` for `0x0304`, and `unknown` for another safely established negotiated version. When no version was negotiated or the API does not expose a reliable negotiated value, `tls_version` must be absent. A record-layer legacy version or offered version is not evidence of the negotiated version. Retaining `unknown` does not authorize offering obsolete versions, insecure verification, version forcing or a retry with another handshake profile.

<a id="REQ-OBS-0049"></a>

**REQ-OBS-0049:**

The initial registered offered ALPN identifiers are exactly the case-sensitive ASCII strings `http/1.1`, `h2` and `dot`. Tasks must not offer `unknown`, `h2c`, arbitrary application-specific identifiers or other external registry entries. The existing eight-entry and 32-byte ceilings remain upper bounds; duplicate rejection and stricter test/target/local-policy rules still apply. This registration permits no application payload, additional test, QUIC operation or implicit ALPN offer.

When a protocol was actually negotiated, the retained `alpn` is its exact identifier if it is one of those three, or `unknown` for another safely exposed negotiated identifier. If none was negotiated, `alpn` must be absent, including when a platform cannot expose the value. A peer selecting an unoffered identifier is not a successful valid negotiation; a coarse retained marker must not override protocol validation or a registered failure. Do not copy the original unregistered identifier into another field or diagnostic.

### TLS Peer-Alert Normalization

The protocol alert descriptions are specified in [RFC 8446, section 6](https://www.rfc-editor.org/rfc/rfc8446.html#section-6). The following groups are Barometer classifications; they are not raw TLS alert names or locally generated error classes.

<a id="REQ-OBS-0050"></a>

**REQ-OBS-0050:**

When a directly received peer alert is the evidence for `status: failed`, `failure: alert`, a producer that safely exposes its description code must use this exact coarse mapping if it retains `details.alert`:

| Peer description codes | Retained class |
|---|---|
| 40, 71, 86, 120 | `handshake_failure` |
| 42, 43, 44, 45, 46, 48, 113, 116 | `certificate_error` |
| 10, 20, 22, 47, 50, 51, 70, 109, 110 | `protocol_error` |
| 49, 112, 115 | `access_denied` |
| 80 | `internal_error` |
| Any other directly received description code | `other` |

If alert reception is known but the description is unavailable, omit `details.alert`; do not guess a class. Absence of evidence that a peer alert was received does not establish `failure: alert`. Raw bytes, numeric codes, severity levels and raw library error text must not be serialized. A normal closure after successful handshake does not retroactively make the handshake fail. A local cancellation, deadline, certificate-validation failure or locally sent alert is not a received peer alert. A peer's certificate-related alert does not establish the local `certificate_validation` result; preserve that separate local observation. A more specific registered failure such as `alpn_no_overlap` follows the test's outcome rules and does not carry `details.alert` under this format.

### Incomplete Observations

<a id="REQ-OBS-0051"></a>

**REQ-OBS-0051:**

Version `0.1.0` registers no `failure` value for `status: incomplete` for any of its four observation types. Producers must omit that field and decoders must reject its presence, including `null`, an empty string or an otherwise registered failed-operation value. Cross-cutting termination remains in `execution.reason`, and registered-test rules still determine whether partial observations may be retained at all.

## Validation and Bounds

<a id="REQ-OBS-0032"></a>

**REQ-OBS-0032:**

- A test may emit only observation types listed by its Output schema.

<a id="REQ-OBS-0034"></a>

**REQ-OBS-0034:**

- Observations must appear in execution order.

<a id="REQ-OBS-0035"></a>

**REQ-OBS-0035:**

- At most one terminal failed or incomplete observation may appear in one primitive test result.

<a id="REQ-OBS-0036"></a>

**REQ-OBS-0036:**

- A succeeded observation must not contain `failure`.

<a id="REQ-OBS-0037"></a>

**REQ-OBS-0037:**

- A failed observation must contain a failure registered for its type.

<a id="REQ-OBS-0038"></a>

**REQ-OBS-0038:**

- Detail fields must be consistent with status and failure.

<a id="REQ-OBS-0039"></a>

**REQ-OBS-0039:**

- Counts, strings, response arrays, answer arrays, redirects, checks, and total encoded size must satisfy [`Registered Initial Limits`](../library/registered-limits.md).

<a id="REQ-OBS-0040"></a>

**REQ-OBS-0040:**

- A target, resolver, or redirect address must not be added merely because a lower-level networking API exposed it.

<a id="REQ-OBS-0041"></a>

**REQ-OBS-0041:**

- Raw errors must map conservatively to registered values; otherwise use `inconclusive`.

## Privacy and Interpretation

These formats intentionally retain less information than a general network event log. They omit raw bytes and identifiers that are unnecessary for the initial measurement questions.

<a id="REQ-OBS-0033"></a>

**REQ-OBS-0033:**

Observation order and stage failure can support layer-specific analysis, but they do not establish intent. A failed TLS observation following a successful TCP observation establishes only that the observed TCP stage completed and the TLS stage did not complete normally under that test configuration.
