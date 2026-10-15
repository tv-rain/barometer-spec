# Network Context

**Status:** Draft  
**Version:** 0.1.0

Runtime JSON values follow the shared [strict decoding contract](../data-formats/json-decoding.md) in addition to this document's schema, limits, and validation rules.

## Overview

Barometer maintains a bounded Network Context snapshot that can be used to evaluate execution eligibility and interpret measurement results. The snapshot separates information safely exposed by the operating system from coarse information derived from the public egress observed on the selected network path.

<a id="REQ-CONTEXT-0001"></a>

**REQ-CONTEXT-0001:**

Network Context is a shared library facility, not an operation independently repeated by every test. The normalized representation is defined in [`data-formats/network-context.md`](../data-formats/network-context.md).

## Context Layers

### Access Context

<a id="REQ-CONTEXT-0002"></a>

**REQ-CONTEXT-0002:**

Access context describes the underlying device network using coarse operating-system signals:

- network type;
- VPN state;
- IPv4 and IPv6 availability;
- validation state;
- whether the network generation changed.

<a id="REQ-CONTEXT-0003"></a>

**REQ-CONTEXT-0003:**

Access context must not contain interface names, local addresses, DNS server addresses, SSIDs, BSSIDs, cell identifiers, SIM information, subscriber identifiers, carrier account information, or physical location.

### Egress Context

<a id="REQ-CONTEXT-0004"></a>

**REQ-CONTEXT-0004:**

Egress context describes the public egress observed through the selected `direct` or `proxy` path:

- country code;
- optional first-level region code;
- ASN;
- classification-data version;
- lookup status and source;
- `connection_code` when the selected path is `proxy`.

<a id="REQ-CONTEXT-0005"></a>

**REQ-CONTEXT-0005:**

The egress endpoint inevitably observes the request's source IP while serving the request. The endpoint must classify the address without returning it to Barometer, and the endpoint operator must minimize or avoid retaining it.

<a id="REQ-CONTEXT-0006"></a>

**REQ-CONTEXT-0006:**

Country and region describe an IP classification, not the user's physical location. ASN describes the observed egress network and may not identify the user's access operator, especially when a VPN, proxy, carrier-grade NAT, or circumvention path is present.

## Host Initialization

The host configures egress classification during library initialization using a serializable object suitable for Flutter bindings:

```json
{
  "network_context": {
    "primary_endpoint": "https://context.example/network-context",
    "fallback_endpoint": "https://backup.example/network-context"
  }
}
```

<a id="REQ-CONTEXT-0007"></a>

**REQ-CONTEXT-0007:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `primary_endpoint` | string | Yes | Absolute public `https` URL without credentials, fragment, or user-specific query parameters. | Preferred egress-classification endpoint. |
| `fallback_endpoint` | string | No | Same constraints as `primary_endpoint`; must be independently approved. | One optional endpoint used when the primary is unavailable or invalid. |

<a id="REQ-CONTEXT-0008"></a>

**REQ-CONTEXT-0008:**

If `network_context` is absent, Barometer collects access context only and reports egress context as `unavailable`. A task cannot add or change either endpoint.

<a id="REQ-CONTEXT-0009"></a>

**REQ-CONTEXT-0009:**

The endpoint configuration is immutable for one initialized library instance in the first version. Changing it requires a new library initialization so cached classifications cannot cross configurations accidentally.

<a id="REQ-CONTEXT-0010"></a>

**REQ-CONTEXT-0010:**

Unknown configuration fields are rejected. Redirects, endpoint discovery, task-supplied endpoints, per-user URLs, cookies, credentials, and more than one fallback endpoint are not supported.

## Endpoint Contract

<a id="REQ-CONTEXT-0011"></a>

**REQ-CONTEXT-0011:**

Barometer sends one ordinary HTTPS `GET` request to the configured fixed URL:

```http
GET /network-context HTTP/1.1
Accept: application/json
```

<a id="REQ-CONTEXT-0012"></a>

**REQ-CONTEXT-0012:**

The request must not include:

- an installation, account, device, session, task, test, or measurement identifier;
- the local or public IP address in a header, query, or body;
- cookies, authorization, application telemetry, or user-specific headers;
- the measurement target or `connection_code`.

The endpoint returns a bounded JSON object:

```json
{
  "country_code": "NL",
  "region_code": "NL-NH",
  "asn": 64500,
  "classification_version": "0.1.0"
}
```

<a id="REQ-CONTEXT-0013"></a>

**REQ-CONTEXT-0013:**

| Field | Required | Constraints | Description |
|---|:---:|---|---|
| `country_code` | No | ISO 3166-1 alpha-2 uppercase code. | Country assigned to the observed egress address. |
| `region_code` | No | ISO 3166-2 code consistent with `country_code`. | Optional first-level region classification; omitted when unavailable or insufficiently reliable. |
| `asn` | No | Positive 32-bit autonomous system number. | Origin ASN assigned to the observed egress address. |
| `classification_version` | Yes | Bounded, non-user-specific string. | Identifies the server-side classification dataset or rules. |

<a id="REQ-CONTEXT-0014"></a>

**REQ-CONTEXT-0014:**

The response must not contain the observed IP address, coordinates, city, postal code, ISP account data, free-form operator name, or request identifier. Unknown fields are rejected.

<a id="REQ-CONTEXT-0015"></a>

**REQ-CONTEXT-0015:**

The endpoint response is limited to 4,096 bytes and each primary or fallback operation is limited to 5,000 ms. Parsing stops and the response is invalid when the byte limit is exceeded.

<a id="REQ-CONTEXT-0016"></a>

**REQ-CONTEXT-0016:**

A syntactically valid response may omit every optional classification. Barometer must preserve unknown values rather than contacting another endpoint merely to obtain a more specific answer.

## Path Consistency

<a id="REQ-CONTEXT-0017"></a>

**REQ-CONTEXT-0017:**

Egress context must be obtained through the same path snapshot used by the measurement:

- a `direct` attempt uses the direct path;
- a `proxy` attempt uses the same proxy generation as the measurement;
- a proxy-only attempt must never emit a direct context request;
- all NET-05 steps share one context and path snapshot.

<a id="REQ-CONTEXT-0018"></a>

**REQ-CONTEXT-0018:**

Access context may be captured without network traffic before path selection. Direct and proxy egress contexts are separate and must never overwrite or substitute for one another.

<a id="REQ-CONTEXT-0019"></a>

**REQ-CONTEXT-0019:**

If a cached direct egress context is not valid for the current access-network generation, a proxy attempt reports direct egress as unknown rather than refreshing it outside the selected proxy path.

## Acquisition and Fallback

<a id="REQ-CONTEXT-0020"></a>

**REQ-CONTEXT-0020:**

For one access-network generation and selected-path generation, Barometer uses this bounded order:

1. Use a still-valid cached context for the exact same access-network generation, `network_path`, and proxy generation where applicable.
2. Otherwise make one request to `primary_endpoint` through the selected path.
3. If the primary cannot be reached, fails TLS or HTTP validation, exceeds its bound, or returns invalid data, make one request to the optional `fallback_endpoint` through the same selected path.
4. If no endpoint produces a valid response, return egress status `unavailable`.

<a id="REQ-CONTEXT-0021"></a>

**REQ-CONTEXT-0021:**

There is no retry of the same endpoint within one acquisition and no fallback to a different network path. A valid primary response containing unknown optional values is successful and must not trigger the fallback endpoint.

<a id="REQ-CONTEXT-0022"></a>

**REQ-CONTEXT-0022:**

The registered in-memory freshness default is 300 seconds and the maximum is 900 seconds. Cached data expires at the earliest of:

<a id="REQ-CONTEXT-0023"></a>

**REQ-CONTEXT-0023:**

- the registered maximum freshness bound;
- an access-network generation change;
- a direct/proxy path change;
- a proxy generation change;
- library shutdown or reinitialization.

<a id="REQ-CONTEXT-0024"></a>

**REQ-CONTEXT-0024:**

The cache key must not contain a public IP address or persistent user identifier. Cache entries must not survive application storage unless a future privacy-reviewed version explicitly defines encrypted persistent caching.

## Execution Integration

The execution flow is:

```text
Task becomes due
  → capture access context and network generation
  → snapshot direct or proxy path
  → acquire or reuse egress context through that path
  → evaluate execution context requirements
  → execute the measurement on the same generation and path
  → attach the normalized context to the result
```

<a id="REQ-CONTEXT-0025"></a>

**REQ-CONTEXT-0025:**

Context acquisition is part of the bounded execution attempt and must respect the attempt deadline, cancellation, network-change detection, background policy, and local safety policy.

<a id="REQ-CONTEXT-0026"></a>

**REQ-CONTEXT-0026:**

If a task requires a context field and the field remains unavailable after bounded fallback, the execution constraint is unsatisfied. The scheduler may delay or skip according to the task schedule. Barometer must not guess a value.

<a id="REQ-CONTEXT-0027"></a>

**REQ-CONTEXT-0027:**

When no task requirement depends on egress context, endpoint failure does not convert the measurement into a network failure. The test may continue with `egress.status: unavailable` if local policy permits.

<a id="REQ-CONTEXT-0028"></a>

**REQ-CONTEXT-0028:**

An attempt that cannot satisfy a required context field records `network_context_unavailable`. A context that is available but does not match an allowlist is an unsatisfied execution constraint, not a measurement result.

## Provider and Operator Interpretation

<a id="REQ-CONTEXT-0029"></a>

**REQ-CONTEXT-0029:**

Barometer stores ASN rather than a redundant free-form provider name. Analysis may map ASN to an organization using the recorded `classification_version` or another documented dataset.

<a id="REQ-CONTEXT-0030"></a>

**REQ-CONTEXT-0030:**

The baseline context does not collect a mobile operator or SIM carrier. Such values are unavailable for Wi-Fi, ambiguous during roaming or dual-SIM operation, inconsistent across platforms, and can increase fingerprinting risk. A future optional consented profile may define a normalized serving-network code after platform, privacy, safety, and legal review.

<a id="REQ-CONTEXT-0031"></a>

**REQ-CONTEXT-0031:**

No provider or operator value may be inferred from device locale, timezone, language, SIM country, application store, or user profile.

## Privacy and Safety Requirements

<a id="REQ-CONTEXT-0032"></a>

**REQ-CONTEXT-0032:**

- The host must use only privacy-reviewed primary and fallback endpoints.

<a id="REQ-CONTEXT-0035"></a>

**REQ-CONTEXT-0035:**

- Endpoint operators should disable or minimize raw access logs and must not combine source IP and request time with unrelated user or application data.

<a id="REQ-CONTEXT-0036"></a>

**REQ-CONTEXT-0036:**

- The library must not send identifiers, cookies, task details, measurement targets, or `connection_code` to the endpoint.

<a id="REQ-CONTEXT-0037"></a>

**REQ-CONTEXT-0037:**

- The endpoint must return only coarse classifications and must never return the observed IP address.

<a id="REQ-CONTEXT-0038"></a>

**REQ-CONTEXT-0038:**

- Barometer must not collect GPS location, Wi-Fi identifiers, interface names, cell identifiers, SIM identifiers, phone numbers, subscriber identifiers, or carrier account data.

<a id="REQ-CONTEXT-0039"></a>

**REQ-CONTEXT-0039:**

- Region is optional and must be omitted when its necessity or reliability is not established.

<a id="REQ-CONTEXT-0040"></a>

**REQ-CONTEXT-0040:**

- Results should avoid redundant provider names when ASN is present.

<a id="REQ-CONTEXT-0041"></a>

**REQ-CONTEXT-0041:**

- Public reporting must aggregate context into sufficiently broad groups; raw combinations of region, ASN, network type, connection code, and time can become identifying.

<a id="REQ-CONTEXT-0042"></a>

**REQ-CONTEXT-0042:**

- Endpoint or classification failure is not evidence of censorship.

## Platform Collection

<a id="REQ-CONTEXT-0033"></a>

**REQ-CONTEXT-0033:**

The Flutter-facing Barometer package may use native platform channels internally and pass only normalized access values to the Go core. The host application does not provide platform objects or Barometer test identifiers.

<a id="REQ-CONTEXT-0034"></a>

**REQ-CONTEXT-0034:**

On Android, use coarse `NetworkCapabilities` and exclude location-sensitive transport information. On Apple platforms, use coarse Network-framework path properties. Unsupported values remain `unknown`.

## Known Limitations

- IP geolocation can be stale, imprecise, or incorrect and must not be treated as physical location.
- ASN classification may be ambiguous for multi-origin prefixes, anycast, resellers, VPNs, or carrier-grade NAT.
- The endpoint sees the source IP and request timing even though Barometer does not retain the address.
- A fallback endpoint improves availability but exposes the selected egress to another reviewed service when the primary fails.
- Some mobile networks change public egress without an observable operating-system network-generation change.
- Proxy software may change its upstream strategy without changing the local proxy generation or `connection_code`.
