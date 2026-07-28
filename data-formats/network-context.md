# Network Context Format

**Status:** Draft  
**Version:** 0.1.0

## Overview

The Network Context object contains minimized access-network and selected-egress metadata used for execution eligibility and result interpretation. Acquisition and lifecycle behavior are defined in [`library/network-context.md`](../library/network-context.md).

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

| Field | Type | Required | Description |
|---|---|:---:|---|
| `access` | object | Yes | Coarse operating-system network snapshot. |
| `egress` | object | Yes | Classification of the selected path's public egress, or an explicit unavailable state. |

Unknown top-level fields are rejected.

## Access Object

| Field | Type | Required | Values | Description |
|---|---|:---:|---|---|
| `network_type` | string | Yes | `wifi`, `cellular`, `ethernet`, `other`, `unknown` | Coarse base transport used by the selected path. |
| `vpn_state` | string | Yes | `detected`, `not_detected`, `unknown` | Whether the platform reports a VPN affecting the application's path. |
| `ipv4_available` | string | Yes | `yes`, `no`, `unknown` | Platform-reported IPv4 path availability, not proven Internet reachability. |
| `ipv6_available` | string | Yes | `yes`, `no`, `unknown` | Platform-reported IPv6 path availability, not proven Internet reachability. |
| `validated` | string | Yes | `yes`, `no`, `unknown` | Coarse platform Internet-validation state. |
| `network_changed` | boolean | Yes | `true`, `false` | Whether the access-network generation changed while the snapshot or attempt was active. |

The access object must not contain interface names, addresses, Wi-Fi identifiers, DNS server addresses, cell information, SIM information, carrier names, subscriber identifiers, or location.

## Egress Object

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

When `status` is `unavailable`, `lookup_source` must be `none`, classification fields must be absent, and `network_path` still records the requested path. `connection_code` remains present for a configured proxy path because it comes from trusted local configuration rather than the failed endpoint.

When `status` is `fresh`, `lookup_source` must be `primary` or `fallback`. When `status` is `cached`, `lookup_source` must be `cache`.

A successful endpoint response may produce `fresh` or `cached` context with no country, region, or ASN. Missing classification fields mean unknown and must not be inferred.

## Provider and Operator

The initial format does not contain free-form `provider` or `operator` fields.

Provider organization may be derived during analysis from `asn` and a documented mapping dataset. The mapping is contextual and must not be presented as a verified access-provider identity.

Mobile operator information is outside the baseline format. It requires a separate consent, platform, privacy, safety, and legal review.

## Use in Execution

Execution requirements reference normalized field names rather than endpoint-specific response fields. A task may require `country_code`, `region_code`, or `asn` to be available and may use a broad country allowlist as defined in [`task-execution.md`](task-execution.md#network-context-requirements).

The initial task format does not support region, ASN, provider, or operator allowlists. Local deployment policy may impose stricter context eligibility after review.

## Use in Results

Each [`Measurement Result`](measurement-result.md) carries the context snapshot used for its execution when required by that format. Implementations may deduplicate identical context objects within one result batch only when doing so does not introduce a persistent cross-batch identifier.

Results must not add:

- public or local IP addresses;
- endpoint URLs;
- proxy host or port;
- network or proxy generation numbers;
- exact geolocation;
- free-form provider or carrier names;
- a persistent context identifier.

## Validation

- Unknown fields and enum values are rejected.
- Country and region codes must be normalized before use.
- `region_code` requires a matching `country_code`.
- `connection_code` is rejected for `direct`.
- A proxy context without `connection_code` is invalid.
- Classification fields are rejected when `status` is `unavailable`.
- Invalid context cannot satisfy an execution requirement and must not be attached as if it were a valid measurement context.
