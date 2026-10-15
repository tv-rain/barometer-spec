# Network Context Format

**Status:** Draft  
**Version:** 0.1.0

Runtime JSON values follow the shared [strict decoding contract](json-decoding.md) in addition to this document's schema, limits, and validation rules.

## Overview

The Network Context object contains minimized access-network and selected-egress metadata used for execution eligibility and result interpretation. Acquisition and lifecycle behavior are defined in [`library/network-context.md`](../library/network-context.md).

<a id="REQ-CONTEXT-FORMAT-0001"></a>

**REQ-CONTEXT-FORMAT-0001:**

The object represents one stable access-network generation and one selected direct or proxy path. It contains no public or local IP address and no persistent network identifier.

## JSON Structure

```json
{
  "access": {
    "network_type": "cellular",
    "vpn_state": "not_detected",
    "ipv4_available": "yes",
    "ipv6_available": "yes",
    "validated": "yes",
    "network_changed": false
  },
  "egress": {
    "status": "fresh",
    "lookup_source": "primary",
    "network_path": "proxy",
    "connection_code": "outline_mobileproxy",
    "country_code": "NL",
    "region_code": "NL-NH",
    "asn": 64500,
    "classification_version": "0.1.0"
  }
}
```

## Top-level Fields

<a id="REQ-CONTEXT-FORMAT-0002"></a>

**REQ-CONTEXT-FORMAT-0002:**

| Field | Type | Required | Description |
|---|---|:---:|---|
| `access` | object | Yes | Coarse operating-system network snapshot. |
| `egress` | object | Yes | Classification of the selected path's public egress, or an explicit unavailable state. |

<a id="REQ-CONTEXT-FORMAT-0003"></a>

**REQ-CONTEXT-FORMAT-0003:**

Unknown top-level fields are rejected.

## Access Object

<a id="REQ-CONTEXT-FORMAT-0004"></a>

**REQ-CONTEXT-FORMAT-0004:**

| Field | Type | Required | Values | Description |
|---|---|:---:|---|---|
| `network_type` | string | Yes | `wifi`, `cellular`, `ethernet`, `other`, `unknown` | Coarse base transport used by the selected path. |
| `vpn_state` | string | Yes | `detected`, `not_detected`, `unknown` | Whether the platform reports a VPN affecting the application's path. |
| `ipv4_available` | string | Yes | `yes`, `no`, `unknown` | Platform-reported IPv4 path availability, not proven Internet reachability. |
| `ipv6_available` | string | Yes | `yes`, `no`, `unknown` | Platform-reported IPv6 path availability, not proven Internet reachability. |
| `validated` | string | Yes | `yes`, `no`, `unknown` | Coarse platform Internet-validation state. |
| `network_changed` | boolean | Yes | `true`, `false` | Whether the access-network generation changed while the snapshot or attempt was active. |

<a id="REQ-CONTEXT-FORMAT-0005"></a>

**REQ-CONTEXT-FORMAT-0005:**

The access object must not contain interface names, addresses, Wi-Fi identifiers, DNS server addresses, cell information, SIM information, carrier names, subscriber identifiers, or location.

## Egress Object

<a id="REQ-CONTEXT-FORMAT-0006"></a>

**REQ-CONTEXT-FORMAT-0006:**

| Field | Type | Required | Values or constraints | Description |
|---|---|:---:|---|---|
| `status` | string | Yes | `fresh`, `cached`, `unavailable` | Availability and freshness class of the egress classification. |
| `lookup_source` | string | Yes | `primary`, `fallback`, `cache`, `none` | Source that produced the classification without identifying the endpoint. |
| `network_path` | string | Yes | `direct`, `proxy` | Path through which context was obtained and the measurement runs. |
| `connection_code` | string | Conditional | Required only for `proxy`; same constraints as the proxy configuration. | Coarse host-defined proxy connection-path category. |
| `country_code` | string | No | ISO 3166-1 alpha-2 uppercase code. | Country assigned to the observed egress address. |
| `region_code` | string | No | ISO 3166-2 code consistent with `country_code`. | Optional first-level region classification. |
| `asn` | integer | No | Positive 32-bit autonomous system number. | Origin ASN assigned to the observed egress address. |
| `classification_version` | string | Conditional | Required for `fresh` or `cached`; bounded and non-user-specific. | Version of the classification data or rules. |

<a id="REQ-CONTEXT-FORMAT-0007"></a>

**REQ-CONTEXT-FORMAT-0007:**

When `status` is `unavailable`, `lookup_source` must be `none`, classification fields must be absent, and `network_path` still records the requested path. `connection_code` remains present for a configured proxy path because it comes from trusted local configuration rather than the failed endpoint.

<a id="REQ-CONTEXT-FORMAT-0008"></a>

**REQ-CONTEXT-FORMAT-0008:**

When `status` is `fresh`, `lookup_source` must be `primary` or `fallback`. When `status` is `cached`, `lookup_source` must be `cache`.

<a id="REQ-CONTEXT-FORMAT-0009"></a>

**REQ-CONTEXT-FORMAT-0009:**

A successful endpoint response may produce `fresh` or `cached` context with no country, region, or ASN. Missing classification fields mean unknown and must not be inferred.

## Provider and Operator

<a id="REQ-CONTEXT-FORMAT-0010"></a>

**REQ-CONTEXT-FORMAT-0010:**

The initial format does not contain free-form `provider` or `operator` fields.

<a id="REQ-CONTEXT-FORMAT-0011"></a>

**REQ-CONTEXT-FORMAT-0011:**

Provider organization may be derived during analysis from `asn` and a documented mapping dataset. The mapping is contextual and must not be presented as a verified access-provider identity.

<a id="REQ-CONTEXT-FORMAT-0012"></a>

**REQ-CONTEXT-FORMAT-0012:**

Mobile operator information is outside the baseline format. It requires a separate consent, platform, privacy, safety, and legal review.

## Use in Execution

<a id="REQ-CONTEXT-FORMAT-0013"></a>

**REQ-CONTEXT-FORMAT-0013:**

Execution requirements reference normalized field names rather than endpoint-specific response fields. A task may require `country_code`, `region_code`, or `asn` to be available and may use a broad country allowlist as defined in [`task-execution.md`](task-execution.md#network-context-requirements).

<a id="REQ-CONTEXT-FORMAT-0014"></a>

**REQ-CONTEXT-FORMAT-0014:**

The initial task format does not support region, ASN, provider, or operator allowlists. Local deployment policy may impose stricter context eligibility after review.

## Use in Results

<a id="REQ-CONTEXT-FORMAT-0015"></a>

**REQ-CONTEXT-FORMAT-0015:**

Each [`Measurement Result`](measurement-result.md) carries the context snapshot used for its execution when required by that format. Implementations may deduplicate identical context objects within one result batch only when doing so does not introduce a persistent cross-batch identifier.

<a id="REQ-CONTEXT-FORMAT-0016"></a>

**REQ-CONTEXT-FORMAT-0016:**

Results must not add:

- public or local IP addresses;
- endpoint URLs;
- proxy host or port;
- network or proxy generation numbers;
- exact geolocation;
- free-form provider or carrier names;
- a persistent context identifier.

## Validation

<a id="REQ-CONTEXT-FORMAT-0017"></a>

**REQ-CONTEXT-FORMAT-0017:**

- Unknown fields and enum values are rejected.

<a id="REQ-CONTEXT-FORMAT-0018"></a>

**REQ-CONTEXT-FORMAT-0018:**

- Country and region codes must be normalized before use.

<a id="REQ-CONTEXT-FORMAT-0019"></a>

**REQ-CONTEXT-FORMAT-0019:**

- `region_code` requires a matching `country_code`.

<a id="REQ-CONTEXT-FORMAT-0020"></a>

**REQ-CONTEXT-FORMAT-0020:**

- `connection_code` is rejected for `direct`.

<a id="REQ-CONTEXT-FORMAT-0021"></a>

**REQ-CONTEXT-FORMAT-0021:**

- A proxy context without `connection_code` is invalid.

<a id="REQ-CONTEXT-FORMAT-0022"></a>

**REQ-CONTEXT-FORMAT-0022:**

- Classification fields are rejected when `status` is `unavailable`.

<a id="REQ-CONTEXT-FORMAT-0023"></a>

**REQ-CONTEXT-FORMAT-0023:**

- Invalid context cannot satisfy an execution requirement and must not be attached as if it were a valid measurement context.
