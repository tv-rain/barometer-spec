# `HTTP-01` Small HTTPS request

**Status:** `Draft`
**Version:** `0.1.0`
**Category:** `HTTPS connectivity`

## Overview

This test sends one bounded, unauthenticated HTTPS `GET` request to a configured URL and records the transport stages, response status, redirect behavior, and limited response properties.

A test defines registered measurement behavior. A task references the test by `test_id` and supplies the measurement input, options, execution constraints, schedule, and task-specific safety requirements.

## Purpose

### Measurement Question

Does the configured HTTPS endpoint return its expected bounded response through the device's normal application networking path?

### Non-goals

<a id="REQ-HTTP-01-0001"></a>

**REQ-HTTP-01-0001:**

- The test does not browse or render a web page.

<a id="REQ-HTTP-01-0002"></a>

**REQ-HTTP-01-0002:**

- The test does not authenticate, submit user data, or execute scripts.

<a id="REQ-HTTP-01-0003"></a>

**REQ-HTTP-01-0003:**

- An unexpected response does not by itself establish a block page or intentional manipulation.

## Measurement Method

### Target

<a id="REQ-HTTP-01-0004"></a>

**REQ-HTTP-01-0004:**

One reviewed HTTPS URL with a stable, non-sensitive, bounded response. The endpoint must not require credentials, cookies, application identity, or user-specific query parameters.

### Operation

<a id="REQ-HTTP-01-0005"></a>

**REQ-HTTP-01-0005:**

The probe uses the documented HTTP stack to resolve the hostname, establish TCP and authenticated TLS, and issue one ordinary `GET` request. Redirects may be followed only when explicitly enabled and each next target passes validation. Only configured header checks and body checks are evaluated. Body processing stops at the configured byte limit.

<a id="REQ-HTTP-01-0006"></a>

**REQ-HTTP-01-0006:**

The test limits application body bytes rather than network packets. HTTP/TLS buffering and multiplexed transports do not provide a portable packet-count limit at this layer.

### Procedure

<a id="REQ-HTTP-01-0007"></a>

**REQ-HTTP-01-0007:**

1. Validate the HTTPS URL, redirect policy, byte limit, and optional response checks.
2. Confirm a stable network generation.
3. Resolve the hostname through the documented system resolver path.
4. Establish TCP and authenticated TLS for the URL origin.
5. Send one `GET` request without credentials, cookies, custom identifiers, or a request body and request an identity-encoded response.
6. If a redirect is received and following is disabled, retain a minimized redirect observation and stop.
7. If following is enabled, validate the next URL before contacting it and stop when the redirect bound is reached.
8. On the terminal response, evaluate configured status, header, and body checks while reading no more than `max_body_bytes`.
9. Record the first failed stage or bounded response properties and close the response body.

### Success Condition

<a id="REQ-HTTP-01-0008"></a>

**REQ-HTTP-01-0008:**

The endpoint, or the terminal approved redirect target, returns an HTTPS response on the same network generation. All configured status, header, and body checks must match for the outcome to be classified as the expected response.

### Failure Conditions

<a id="REQ-HTTP-01-0009"></a>

**REQ-HTTP-01-0009:**

| Failure class | Required observation |
|---|---|
| `dns_failure` | The URL hostname cannot be resolved through the documented resolver path. |
| `tcp_failure` | The connection cannot be established; a normalized sub-class may retain timeout, refusal, or reset. |
| `tls_failure` | TLS negotiation or certificate validation fails. |
| `http_timeout` | No complete response headers arrive within the operation bound. |
| `protocol_error` | The peer response is not valid supported HTTP. |
| `redirect_observed` | A redirect response is received while redirect following is disabled. |
| `redirect_rejected` | The next redirect target fails URL or local safety validation and is not contacted. |
| `redirect_limit_reached` | The configured number of followed redirects is reached before a terminal response. |
| `unexpected_status` | The response status differs from the registered expected status. |
| `header_check_failed` | One or more configured header checks do not match. |
| `body_check_failed` | One or more configured body checks do not match after a complete bounded body is read. |
| `body_limit_reached` | The configured body-byte limit is reached before all body checks can be decided. |
| `unsupported_content_encoding` | A body check is configured but the server returns a content encoding unsupported by this test version. |
| `network_changed` | The network generation changes during the run. |
| `inconclusive` | Available observations are insufficient for a more specific class. |

## Inputs

<a id="REQ-HTTP-01-0010"></a>

**REQ-HTTP-01-0010:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `url` | string | Yes | Absolute `https` URL, maximum 2,048 UTF-8 bytes; no credentials or fragment; target must pass local policy. | Endpoint to request. |
| `expected_status` | integer | No | Valid HTTP status code. | Optional expected response status. |
| `body_checks` | array of objects | No | At most 8 non-empty checks using supported types. | Optional checks applied to the terminal response body within `max_body_bytes`. |
| `header_checks` | array of objects | No | At most 8 checks of non-sensitive response headers. | Optional checks applied to terminal response headers. |

Each `body_checks` entry has:

<a id="REQ-HTTP-01-0011"></a>

**REQ-HTTP-01-0011:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `type` | string | Yes | `contains`, `prefix`, `suffix`, or `sha256`. | Body comparison operation. |
| `value` | string | Yes | Non-empty UTF-8 literal of at most 256 bytes for string checks or lowercase SHA-256 hex for `sha256`. | Expected value. |

<a id="REQ-HTTP-01-0012"></a>

**REQ-HTTP-01-0012:**

Body string checks are case-sensitive and operate on body bytes interpreted as UTF-8. All configured body checks must match. Regular expressions are not supported in this version.

Each `header_checks` entry has:

<a id="REQ-HTTP-01-0013"></a>

**REQ-HTTP-01-0013:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `name` | string | Yes | Valid non-sensitive HTTP response header name. | Header to check; names are case-insensitive. |
| `type` | string | Yes | `present`, `absent`, `equals`, or `contains`. | Header comparison operation. |
| `value` | string | Conditional | Required for `equals` and `contains`; prohibited otherwise; non-empty UTF-8 value of at most 256 bytes. | Expected header value or substring. |

<a id="REQ-HTTP-01-0014"></a>

**REQ-HTTP-01-0014:**

For a multi-valued header, `equals` or `contains` succeeds when at least one field value matches. All configured header checks must match. Results retain check outcomes, not raw header values.

### Input Validation

<a id="REQ-HTTP-01-0051"></a>

**REQ-HTTP-01-0051:**

For `network_path: proxy`, the initial URL must have an explicit IP address as its host and satisfy [REQ-PROXY-0044](../library/proxy.md#REQ-PROXY-0044). A hostname initial URL is incompatible at admission. When following a redirect, a hostname destination is rejected before any destination contact, proxy connection, CONNECT or local resolution for that redirect, even if separately registered. The outcome is `redirect_rejected` using the existing minimized observation representation; it is a local safety rejection, not evidence that the destination is censored. Explicit-IP redirects still require every existing URL, registration, local address policy, redirect-count and same-proxy-generation check. Barometer must not replace a hostname URL with a resolved IP URL or weaken TLS certificate validation to enable proxy execution. Direct-path hostname URLs retain their existing behavior.

<a id="REQ-HTTP-01-0015"></a>

**REQ-HTTP-01-0015:**

- Only `https` is supported in this test version.

<a id="REQ-HTTP-01-0016"></a>

**REQ-HTTP-01-0016:**

- URLs containing credentials, local/private targets, runtime interpolation, or user-specific identifiers are rejected.

<a id="REQ-HTTP-01-0017"></a>

**REQ-HTTP-01-0017:**

- Query parameters are permitted only when part of a locally registered static target and must not contain secrets.

<a id="REQ-HTTP-01-0018"></a>

**REQ-HTTP-01-0018:**

- Every redirect destination must pass the same URL and target-safety validation before contact. Approval of the initial URL does not authorize a redirect target.

<a id="REQ-HTTP-01-0019"></a>

**REQ-HTTP-01-0019:**

- Redirects to a non-HTTPS scheme, embedded credentials, local or prohibited addresses, or unregistered targets are rejected.

<a id="REQ-HTTP-01-0020"></a>

**REQ-HTTP-01-0020:**

- Body and header check arrays and values must satisfy registered count and length bounds.

<a id="REQ-HTTP-01-0021"></a>

**REQ-HTTP-01-0021:**

- Sensitive headers, including authentication and cookie headers, cannot be configured for value matching or retained in results.

<a id="REQ-HTTP-01-0022"></a>

**REQ-HTTP-01-0022:**

- Unknown fields are rejected.

<a id="REQ-HTTP-01-0023"></a>

**REQ-HTTP-01-0023:**

Invalid input must prevent measurement execution and must not produce a measurement result that could be interpreted as network interference.

## Options

<a id="REQ-HTTP-01-0024"></a>

**REQ-HTTP-01-0024:**

| Option | Type | Required | Default | Constraints | Description |
|---|---|:---:|---|---|---|
| `address_family` | string | No | `auto` | `auto`, `ipv4`, or `ipv6`. | Limits hostname resolution and connection to one family where supported. |
| `max_body_bytes` | integer | No | `4096` | Positive and no greater than `65536` or a stricter task receive bound. | Maximum terminal-response body bytes processed by this test. |
| `follow_redirects` | boolean | No | `false` | — | Whether approved HTTPS redirects may be followed. |
| `max_redirects` | integer | Conditional | — | Required when `follow_redirects` is `true`; `1` or `2`. | Maximum redirects contacted before stopping. |

<a id="REQ-HTTP-01-0025"></a>

**REQ-HTTP-01-0025:**

`max_redirects` must be absent when redirect following is disabled. Custom methods, request headers, request bodies, cookies, credentials, proxy selection, compression negotiation, and TLS-validation overrides are not supported in this version.

## Preconditions

<a id="REQ-HTTP-01-0026"></a>

**REQ-HTTP-01-0026:**

- The URL and any expected response properties must be locally registered and current.

<a id="REQ-HTTP-01-0027"></a>

**REQ-HTTP-01-0027:**

- A stable network generation and task execution deadline must be available.

<a id="REQ-HTTP-01-0028"></a>

**REQ-HTTP-01-0028:**

- The endpoint must provide a small response suitable for bounded mobile measurement.

<a id="REQ-HTTP-01-0029"></a>

**REQ-HTTP-01-0029:**

- Every permitted redirect target and response check must be locally registered with the measurement target.

<a id="REQ-HTTP-01-0030"></a>

**REQ-HTTP-01-0030:**

- The test must not run if application or platform defaults would attach credentials, cookies, or identifying headers that cannot be disabled.

<a id="REQ-HTTP-01-0031"></a>

**REQ-HTTP-01-0031:**

Task execution constraints and local probe policy may impose stricter preconditions.

## Resource Bounds

<a id="REQ-HTTP-01-0032"></a>

**REQ-HTTP-01-0032:**

| Resource | Baseline limit | Behavior when reached |
|---|---|---|
| Duration | One DNS, TCP, TLS, and HTTPS operation chain within the task deadline. | Stop at the first failed or expired stage. |
| Requests or connections | One initial HTTPS request plus at most two configured redirect requests, within the outer connection bound. | Stop before contacting a redirect beyond the bound or an unsafe redirect target. |
| Data transferred | At most 16,384 response-header bytes and `max_body_bytes` of the terminal response body, within the outer byte limits. | Stop reading, close the body, and report whether evaluation was truncated. |
| Retries | None at the test layer. | A retry requires a new execution attempt. |
| Concurrency | One active run per normalized URL. | Deduplicate or delay equivalent runs. |

## Output

<a id="REQ-HTTP-01-0033"></a>

**REQ-HTTP-01-0033:**

The test uses Measurement Result `schema_version: 0.1.0` and `test.result_version: 0.1.0`.

<a id="REQ-HTTP-01-0034"></a>

**REQ-HTTP-01-0034:**

The result contains ordered DNS, TCP, TLS, and HTTP observations for operations that began. Redirects may add another bounded DNS, TCP, TLS, and HTTP sequence. An operation that reused an established connection emits only the observations actually performed.

<a id="REQ-HTTP-01-0035"></a>

**REQ-HTTP-01-0035:**

The terminal [`http_exchange` observation](../data-formats/measurement-observations.md#http-exchange) retains status, a minimized redirect class, bounded body-processing metadata, and indexed check outcomes. It does not retain request or response content.

Example:

```json
{
  "outcome": "expected_response",
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
      "duration_ms": 750,
      "details": {
        "address_family": "ipv4",
        "protocol": "h2",
        "status_code": 200,
        "content_encoding": "identity",
        "body": {
          "bytes_processed": 512,
          "truncated": false
        },
        "checks": [
          {
            "kind": "status",
            "index": 0,
            "matched": true
          },
          {
            "kind": "body",
            "index": 0,
            "matched": true
          }
        ]
      }
    }
  ]
}
```

### Outcomes

<a id="REQ-HTTP-01-0036"></a>

**REQ-HTTP-01-0036:**

| Outcome | Required terminal observation |
|---|---|
| `expected_response` | The terminal HTTP response satisfied every configured check. |
| `dns_failure` | DNS failed; its normalized failure remains in the DNS observation. |
| `tcp_failure` | TCP failed; its normalized failure remains in the TCP observation. |
| `tls_failure` | TLS failed; its normalized failure remains in the TLS observation. |
| `http_timeout` | HTTP failed with `timeout`. |
| `protocol_error` | HTTP failed with `protocol_error`. |
| `redirect_observed` | Redirect following was disabled and a valid redirect status was observed. The HTTP observation succeeded and contains the minimized redirect. |
| `redirect_rejected` | HTTP failed with `redirect_rejected` and contains the rejected location class. |
| `redirect_limit_reached` | HTTP failed with `redirect_limit_reached` and contains the bounded followed count. |
| `unexpected_status` | HTTP failed with `unexpected_status`; `status_code` and the failed status check are retained. |
| `header_check_failed` | HTTP failed with `header_check_failed`; indexed header-check outcomes are retained. |
| `body_check_failed` | HTTP failed with `body_check_failed`; indexed body-check outcomes are retained. |
| `body_limit_reached` | HTTP failed with `body_limit_reached`; body metadata has `truncated: true`. |
| `unsupported_content_encoding` | HTTP failed with `unsupported_content_encoding`; `content_encoding` is `unsupported`. |
| `inconclusive` | The terminal observation failed with `inconclusive`. |

<a id="REQ-HTTP-01-0037"></a>

**REQ-HTTP-01-0037:**

When multiple checks are configured, the result retains the outcome of each check that was decidable before termination. It must not invent outcomes for checks that were not evaluated.

<a id="REQ-HTTP-01-0038"></a>

**REQ-HTTP-01-0038:**

`network_changed`, cancellation, the outer attempt deadline, proxy failure or reconfiguration, and platform suspension produce an incomplete common execution state. They are not HTTP outcomes.

<a id="REQ-HTTP-01-0039"></a>

**REQ-HTTP-01-0039:**

The result must not contain the requested or redirect URL, hostname, path, query, destination address, request headers, response header names or values, request or response body, expected or observed body digest, matched strings, cookies, credentials, certificate data, cache contents, or raw protocol errors.

## Interpretation

The cross-cutting [Measurement Limitations](../measurement-limitations.md) apply to this result and any derived analysis.

### Supported Interpretation

<a id="REQ-HTTP-01-0040"></a>

**REQ-HTTP-01-0040:**

One execution can establish whether the configured endpoint or an approved terminal redirect target returned a response and whether its bounded status, header, and body properties matched the registered expectations through the observed DNS, TCP, TLS, and HTTP path.

<a id="REQ-HTTP-01-0041"></a>

**REQ-HTTP-01-0041:**

`max_body_bytes` limits bytes processed by the application. It is not an exact on-wire limit because the HTTP, TLS, and socket layers may buffer additional data before the body is closed.

### Alternative Explanations

- Origin, CDN, DNS, routing, certificate, or deployment failure.

- Intentional application redirect or changed response content.

- Captive portal, enterprise proxy, VPN, antivirus, or local filtering.

- Server-side geolocation, rate limiting, load balancing, or maintenance.

- IPv4/IPv6 differences or transient mobile-network behavior.

- Stale expected status, body pattern, digest, or header expectation.

- Legitimate redirect-chain changes.

### Evidence Needed for Stronger Interpretation

<a id="REQ-HTTP-01-0042"></a>

**REQ-HTTP-01-0042:**

- `DNS-01`, `TCP-01`, and `TLS-01` observations for related approved targets.
- A `NET-03` result excluding obvious validation or captive-portal problems.
- Repeated observations under a stable network generation.
- Suitable control endpoints and independent reference signals.

<a id="REQ-HTTP-01-0043"></a>

**REQ-HTTP-01-0043:**

Response differences and redirects require manual or separately reviewed classification before they can support a stronger blocking interpretation.

## Privacy and Safety

### Baseline Risk

<a id="REQ-HTTP-01-0044"></a>

**REQ-HTTP-01-0044:**

| Field | Value |
|---|---|
| Risk level | `low` |
| Requires user consent | `false`, subject to host and local policy |

### Risk Factors

<a id="REQ-HTTP-01-0045"></a>

**REQ-HTTP-01-0045:**

| Type | Level | Rationale and mitigation |
|---|---|---|
| `network_observability` | `low` | The destination and TLS metadata are observable; HTTPS content is encrypted in transit. |
| `traffic_distinctiveness` | `low` | One ordinary bounded request resembles application traffic. |
| `target_sensitivity` | `low` | Only reviewed, non-sensitive endpoints are permitted. |
| `data_sensitivity` | `low` | Response collection is bounded and bodies are not retained. |
| `legal_or_social_context` | `low` | Target and content sensitivity must still be reviewed for each deployment. |

### Safety Analysis

<a id="REQ-HTTP-01-0046"></a>

**REQ-HTTP-01-0046:**

- **Data minimization:** Do not retain response bodies, full headers, matched strings, cookies, full redirect URLs, or unrelated certificate metadata.

<a id="REQ-HTTP-01-0047"></a>

**REQ-HTTP-01-0047:**

- **Traffic distinctiveness:** Use an ordinary request without measurement identifiers, unusual headers, or repeated redirect chains.

<a id="REQ-HTTP-01-0048"></a>

**REQ-HTTP-01-0048:**

- **User-identification risk:** Disable cookies, credentials, caches containing user state, and application-specific identifiers.

<a id="REQ-HTTP-01-0049"></a>

**REQ-HTTP-01-0049:**

- **Target risk:** Only static, non-sensitive, reviewed URLs and separately validated redirect targets may be contacted.

- **Repeated-execution risk:** Repeated requests to a fixed validation path can become recognizable.

- **Residual risks:** Each redirect target sees the source network and request fingerprint; TLS behavior may differ from native host traffic, and the stack may receive more bytes on the wire than the application processes.

<a id="REQ-HTTP-01-0050"></a>

**REQ-HTTP-01-0050:**

The probe retains final authority to delay, skip, or reject execution. A task may increase the effective risk but must never lower this registered baseline.
