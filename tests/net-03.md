# `NET-03` Network validation and captive portal

**Status:** `Draft`
**Version:** `0.1.0`
**Category:** `Network state`

## Overview

This test determines whether the active network appears to provide general Internet access or intercepts a bounded validation request with a login, payment, or captive-portal response.

A test defines registered measurement behavior. A task references the test by `test_id` and supplies the measurement input, options, execution constraints, schedule, and task-specific safety requirements.

## Purpose

### Measurement Question

Does a controlled validation request receive its expected response, an intercepted response, or no usable response on the active network?

### Non-goals

<a id="REQ-NET-03-0001"></a>

**REQ-NET-03-0001:**

- The test does not prove that arbitrary Internet destinations are reachable.

<a id="REQ-NET-03-0002"></a>

**REQ-NET-03-0002:**

- The test does not identify the operator or purpose of an intercepted page.

<a id="REQ-NET-03-0003"></a>

**REQ-NET-03-0003:**

- An unvalidated result is not evidence of censorship.

## Measurement Method

### Target

<a id="REQ-NET-03-0004"></a>

**REQ-NET-03-0004:**

One safety-reviewed validation URL with a stable, non-sensitive response. The target must be controlled by the adopter or another explicitly approved operator and must not require authentication, cookies, or user identifiers.

### Operation

<a id="REQ-NET-03-0005"></a>

**REQ-NET-03-0005:**

The probe first reads operating-system validation or captive-portal state when available. It then performs one bounded request without following redirects and compares the response with the registered expected response profile.

### Procedure

<a id="REQ-NET-03-0006"></a>

**REQ-NET-03-0006:**

1. Confirm that the network generation is stable using `NET-01`.
2. Read the platform validation and captive-portal state when supported.
3. Send one request to the configured validation URL without credentials, cookies, or redirect following.
4. Compare the status, redirect location class, and bounded response property with the expected profile.
5. Stop after the first response or failure and close the connection.

### Success Condition

<a id="REQ-NET-03-0007"></a>

**REQ-NET-03-0007:**

The validation endpoint returns its registered expected response on the same network generation on which the run started.

### Failure Conditions

<a id="REQ-NET-03-0008"></a>

**REQ-NET-03-0008:**

| Failure class | Required observation |
|---|---|
| `captive_portal_suspected` | The platform reports a captive portal or the response is a redirect or bounded content mismatch consistent with interception. |
| `not_validated` | The platform reports no validated Internet path and the active request does not establish validation. |
| `dns_failure` | The validation hostname cannot be resolved. |
| `connection_failure` | A connection cannot be established within the operation bound. |
| `tls_failure` | HTTPS negotiation or certificate validation fails. |
| `unexpected_response` | A response is received but does not match the expected profile or a recognized interception class. |
| `network_changed` | The network generation changes during the run. |
| `inconclusive` | Available platform and active observations conflict or are insufficient. |

## Inputs

<a id="REQ-NET-03-0009"></a>

**REQ-NET-03-0009:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `url` | string | Yes | Absolute `http` or `https` URL, maximum 2,048 UTF-8 bytes; no credentials or fragment; target must pass local safety policy. | Registered validation endpoint. |
| `expected_status` | integer | Yes | Valid HTTP status code. | Status expected from an unintercepted response. |
| `expected_body_sha256` | string | No | Lowercase SHA-256 hex digest of the bounded expected body. | Optional exact response-body check. |

### Input Validation

<a id="REQ-NET-03-0010"></a>

**REQ-NET-03-0010:**

- The target must be present in a locally available, safety-reviewed validation target set.

<a id="REQ-NET-03-0011"></a>

**REQ-NET-03-0011:**

- URLs containing credentials, user-specific parameters, loopback, link-local, or private-network targets must be rejected.

<a id="REQ-NET-03-0012"></a>

**REQ-NET-03-0012:**

- A redirect target must not be contacted; its location may only be classified after safe parsing and minimization.

<a id="REQ-NET-03-0013"></a>

**REQ-NET-03-0013:**

- Unknown fields are rejected.

<a id="REQ-NET-03-0014"></a>

**REQ-NET-03-0014:**

Invalid input must prevent measurement execution and must not produce a measurement result that could be interpreted as network interference.

## Options

<a id="REQ-NET-03-0015"></a>

**REQ-NET-03-0015:**

| Option | Type | Required | Default | Constraints | Description |
|---|---|:---:|---|---|---|
| `address_family` | string | No | `auto` | `auto`, `ipv4`, or `ipv6`; selected family must be supported. | Limits the request to one address family. |

<a id="REQ-NET-03-0016"></a>

**REQ-NET-03-0016:**

Redirect following, custom headers, credentials, and request bodies are not supported in this version.

## Preconditions

<a id="REQ-NET-03-0017"></a>

**REQ-NET-03-0017:**

- A stable network generation must be available.

<a id="REQ-NET-03-0018"></a>

**REQ-NET-03-0018:**

- The validation target and expected response profile must be current and locally available.

<a id="REQ-NET-03-0019"></a>

**REQ-NET-03-0019:**

- The test must not run if a validated captive-portal flow would display, submit, or retain user data.

<a id="REQ-NET-03-0020"></a>

**REQ-NET-03-0020:**

Task execution constraints and local probe policy may impose stricter preconditions.

## Resource Bounds

<a id="REQ-NET-03-0021"></a>

**REQ-NET-03-0021:**

| Resource | Baseline limit | Behavior when reached |
|---|---|---|
| Duration | One bounded request within the task execution deadline. | Stop and retain the directly observed failure stage. |
| Requests or connections | One request; no redirect requests. | Stop after the first response or connection failure. |
| Data transferred | At most 16,384 response-header bytes and a 1,024-byte response prefix, with an absolute prefix maximum of 4,096 bytes under stricter registered profiles. | Stop reading and classify the response as exceeding the registered validation bound. |
| Retries | None within one run. | A retry requires a new execution attempt. |
| Concurrency | One active validation run per network generation. | Delay or reject overlapping runs. |

## Output

<a id="REQ-NET-03-0022"></a>

**REQ-NET-03-0022:**

The test uses Measurement Result `schema_version: 0.1.0` and `test.result_version: 0.1.0`.

<a id="REQ-NET-03-0023"></a>

**REQ-NET-03-0023:**

The result preserves platform validation and active request evidence separately. `platform_validation` never overrides the request observation, and the request does not rewrite the captured platform state.

```json
{
  "outcome": "validated",
  "observations": [
    {
      "type": "dns_query",
      "status": "succeeded",
      "duration_ms": 250,
      "details": {
        "engine": "system",
        "query_type": "A",
        "responses": []
      }
    },
    {
      "type": "tcp_connect",
      "status": "succeeded",
      "duration_ms": 500,
      "details": {
        "address_family": "ipv4"
      }
    },
    {
      "type": "http_exchange",
      "status": "succeeded",
      "duration_ms": 500,
      "details": {
        "address_family": "ipv4",
        "protocol": "http/1.1",
        "status_code": 204,
        "body": {
          "bytes_processed": 0,
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
  ],
  "platform_validation": "validated",
  "response_class": "expected"
}
```

### Additional Fields

<a id="REQ-NET-03-0024"></a>

**REQ-NET-03-0024:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `platform_validation` | string | Yes | `validated`, `not_validated`, `captive_portal`, or `unknown` | Platform state captured before the request. |
| `response_class` | string | Conditional | Required when a valid HTTP response was received. | Minimized active response classification. |

Initial `response_class` values are:

<a id="REQ-NET-03-0025"></a>

**REQ-NET-03-0025:**

- `expected`
- `redirect`
- `content_mismatch`
- `unexpected`

<a id="REQ-NET-03-0026"></a>

**REQ-NET-03-0026:**

For `redirect`, the `http_exchange` includes the common minimized redirect object. The full location is not retained or contacted.

### Outcomes

<a id="REQ-NET-03-0027"></a>

**REQ-NET-03-0027:**

| Outcome | Required terminal evidence |
|---|---|
| `validated` | The active request matched the expected profile. Platform state is retained independently and may be `unknown` or stale. |
| `captive_portal_suspected` | Platform state is `captive_portal`, or the bounded active response is a redirect or content mismatch consistent with interception. |
| `not_validated` | Platform state is `not_validated` and the request did not establish the expected response or a recognized captive-portal class. |
| `dns_failure` | DNS failed; its normalized failure is retained. |
| `connection_failure` | TCP failed; its normalized failure is retained. |
| `tls_failure` | TLS failed; its normalized failure is retained. |
| `unexpected_response` | A valid response was received with `response_class: unexpected`. |
| `inconclusive` | Platform and active observations conflict or the terminal observation is too coarse for another outcome. |

<a id="REQ-NET-03-0028"></a>

**REQ-NET-03-0028:**

For an HTTPS validation URL, an authenticated `tls_handshake` observation appears between TCP and HTTP. For an HTTP URL it is absent. Redirects are never followed.

<a id="REQ-NET-03-0029"></a>

**REQ-NET-03-0029:**

`network_changed`, cancellation, the outer attempt deadline, resource limit, and platform suspension produce an incomplete common execution state and no `measurement` object.

<a id="REQ-NET-03-0030"></a>

**REQ-NET-03-0030:**

The result must not contain the validation URL or address, redirect URL, response body or digest, HTTP header names or values, cookies, authentication state, platform portal URL, interface information, or raw errors.

## Interpretation

The cross-cutting [Measurement Limitations](../measurement-limitations.md) apply to this result and any derived analysis.

### Supported Interpretation

<a id="REQ-NET-03-0031"></a>

**REQ-NET-03-0031:**

One execution can establish whether the configured validation endpoint returned its expected response, appeared to be intercepted, or could not be validated on the observed network path.

### Alternative Explanations

- The validation endpoint, DNS provider, CDN, or certificate may be misconfigured or unavailable.

- A subscription, quota, or local access-control page may intercept traffic.

- The platform validation state may be stale.

- A proxy, antivirus product, enterprise gateway, or VPN may alter the response.

- A transient network change may split the observations.

### Evidence Needed for Stronger Interpretation

<a id="REQ-NET-03-0032"></a>

**REQ-NET-03-0032:**

- A repeat on the same stable network generation.
- Successful and failed measurements against independently operated benign endpoints.
- DNS, TCP, TLS, and HTTP layer results from the same time window.
- Independent reference signals from a comparable network context.

<a id="REQ-NET-03-0033"></a>

**REQ-NET-03-0033:**

A single result must not be described as definitive proof of censorship.

## Privacy and Safety

### Baseline Risk

<a id="REQ-NET-03-0034"></a>

**REQ-NET-03-0034:**

| Field | Value |
|---|---|
| Risk level | `low` |
| Requires user consent | `false`, subject to host and local policy |

### Risk Factors

<a id="REQ-NET-03-0035"></a>

**REQ-NET-03-0035:**

| Type | Level | Rationale and mitigation |
|---|---|---|
| `network_observability` | `low` | One ordinary request is visible to the network. |
| `traffic_distinctiveness` | `low` | The request resembles common connectivity validation, but a fixed target and pattern may still be recognizable. |
| `target_sensitivity` | `low` | Only reviewed, non-sensitive validation targets are permitted. |
| `data_sensitivity` | `low` | Output is limited to coarse response and failure classifications. |
| `legal_or_social_context` | `low` | No sensitive content is requested, but local deployment review remains necessary. |

### Safety Analysis

<a id="REQ-NET-03-0036"></a>

**REQ-NET-03-0036:**

- **Data minimization:** Do not retain response bodies, full redirect URLs, cookies, or unrelated headers.

<a id="REQ-NET-03-0037"></a>

**REQ-NET-03-0037:**

- **Traffic distinctiveness:** Avoid synchronized schedules and repeated validation requests when the platform already provides reliable state.

<a id="REQ-NET-03-0038"></a>

**REQ-NET-03-0038:**

- **User-identification risk:** Do not add identifiers, cache validators, cookies, or application authentication.

<a id="REQ-NET-03-0039"></a>

**REQ-NET-03-0039:**

- **Target risk:** Only locally registered benign validation targets may be contacted.

- **Repeated-execution risk:** A fixed endpoint and cadence could identify measurement behavior.

- **Residual risks:** Network operators can observe the destination and may return behavior tailored to known validation endpoints.

<a id="REQ-NET-03-0040"></a>

**REQ-NET-03-0040:**

The probe retains final authority to delay, skip, or reject execution. A task may increase the effective risk but must never lower this registered baseline.
