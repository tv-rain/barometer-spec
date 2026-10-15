# Proxy Integration

**Status:** Draft  
**Version:** 0.1.0

Runtime JSON values follow the shared [strict decoding contract](../data-formats/json-decoding.md) in addition to this document's schema, limits, and validation rules.

## Overview

Barometer can use one proxy supplied by the host application to run compatible measurements through a host-managed circumvention or alternate connection path. The proxy is configured with a small serializable object suitable for Flutter bindings. Tasks select either the direct path or the currently configured proxy without receiving or controlling the proxy endpoint.

<a id="REQ-PROXY-0001"></a>

**REQ-PROXY-0001:**

The first version supports a local HTTP/1.1 CONNECT proxy for TCP streams. It does not require the host application to know Barometer test identifiers or declare test capabilities.

## Compatibility Basis

The first proxy contract is designed for [Outline SDK MobileProxy](https://github.com/OutlineFoundation/outline-sdk/tree/main/x/mobileproxy). MobileProxy runs a local web proxy backed by an Outline `StreamDialer`; its documented integrations configure Dart and Android clients as HTTP proxies and configure supported Apple clients as HTTP CONNECT proxies.

This specification does not depend on the circumvention strategy used behind MobileProxy. Any host-managed endpoint satisfying the HTTP CONNECT behavior in this document may be used.

## Terminology

- **Proxy transport:** The protocol Barometer uses to communicate with the configured endpoint. The first version fixes this to local HTTP/1.1 CONNECT.
- **Connection path:** The network behavior implemented behind the proxy, such as an Outline transport, smart strategy, or another host-managed circumvention method.
- **`connection_code`:** Coarse host-supplied metadata identifying the connection-path category for later analysis. It is not a proxy identifier, test identifier, endpoint name, or protocol declaration.
- **Proxy generation:** An internal monotonically changing value assigned whenever the host sets, replaces, or clears the proxy. It is not supplied by tasks and is not a persistent identifier.

## Host Integration

<a id="REQ-PROXY-0002"></a>

**REQ-PROXY-0002:**

The host may provide the proxy during Barometer initialization and may replace or clear it while the application is running. The binding must accept only ordinary serializable values and must not require native callbacks, interfaces, sockets, or complex objects.

Conceptual Flutter usage:

```dart
await Barometer.initialize({
  "proxy": {
    "host": "127.0.0.1",
    "port": 54321,
    "connection_code": "outline_mobileproxy"
  }
});

await Barometer.setProxy({
  "host": "127.0.0.1",
  "port": 55001,
  "connection_code": "outline_mobileproxy"
});

await Barometer.clearProxy();
```

<a id="REQ-PROXY-0003"></a>

**REQ-PROXY-0003:**

The exact language-specific method names may follow binding conventions, but initialization, atomic replacement, and clearing must have equivalent semantics.

<a id="REQ-PROXY-0004"></a>

**REQ-PROXY-0004:**

The optional egress-classification endpoints are configured separately during the same library initialization as defined in [`network-context.md`](network-context.md#host-initialization). They are not properties of the proxy object.

## Proxy Configuration

```json
{
  "host": "127.0.0.1",
  "port": 54321,
  "connection_code": "outline_mobileproxy"
}
```

<a id="REQ-PROXY-0005"></a>

**REQ-PROXY-0005:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `host` | string | Yes | Loopback IP address or `localhost` in the first version. | Address on which the host-managed HTTP CONNECT proxy listens. |
| `port` | integer | Yes | `1` through `65535`. | Current listening port of the proxy. |
| `connection_code` | string | Yes | 1–64 lowercase ASCII letters, digits, `_`, `-`, or `.`; must not be user-specific. | Coarse connection-path category retained with proxied results. |

<a id="REQ-PROXY-0006"></a>

**REQ-PROXY-0006:**

Unknown fields are rejected. Proxy authentication, credentials, TLS to the local proxy, proxy IDs, display names, PAC scripts, proxy chains, and multiple concurrent proxies are not supported in the first version.

<a id="REQ-PROXY-0007"></a>

**REQ-PROXY-0007:**

`host` and `port` are trusted host configuration, not measurement targets. Loopback is allowed here even though test target validation normally rejects loopback destinations. A non-loopback proxy endpoint is rejected in the first version because an unencrypted HTTP CONNECT request can expose target authority information and requires a separate threat model.

## Configuration Validation

<a id="REQ-PROXY-0008"></a>

**REQ-PROXY-0008:**

The library must validate the complete object before changing the active configuration. Invalid replacement input must leave the previous configuration unchanged.

<a id="REQ-PROXY-0009"></a>

**REQ-PROXY-0009:**

`connection_code` must be bounded, low-cardinality, and stable across endpoint renewal when the underlying connection-path category has not changed. It must not contain an account name, access key, server address, session identifier, installation identifier, or other user-linked value.

<a id="REQ-PROXY-0010"></a>

**REQ-PROXY-0010:**

The library does not ask the host to declare supported tests. Compatibility is derived internally from the fixed HTTP CONNECT stream capability and each registered test's concrete input and options.

## Lifecycle and Renewal

<a id="REQ-PROXY-0011"></a>

**REQ-PROXY-0011:**

Only one proxy may be configured at a time.

<a id="REQ-PROXY-0012"></a>

**REQ-PROXY-0012:**

When a proxy task starts, the library snapshots the current configuration and proxy generation. Direct tasks are unaffected by proxy configuration.

<a id="REQ-PROXY-0013"></a>

**REQ-PROXY-0013:**

`setProxy` and `clearProxy` must:

1. stop admission of new attempts using the previous generation;
2. cancel and close running proxy attempts using that generation;
3. wait for their bounded cleanup;
4. atomically install the new configuration or clear the proxy;
5. return only after the previous generation is no longer in use by Barometer.

<a id="REQ-PROXY-0014"></a>

**REQ-PROXY-0014:**

The host must keep the previous local proxy available until `setProxy` or `clearProxy` returns. It may then stop or replace the external proxy service.

<a id="REQ-PROXY-0015"></a>

**REQ-PROXY-0015:**

An affected attempt records `proxy_reconfigured`; it must not continue through a new endpoint or fall back to the direct path. A `NET-05` execution must never mix proxy generations between steps.

<a id="REQ-PROXY-0016"></a>

**REQ-PROXY-0016:**

Replacing or clearing the proxy invalidates every cached proxy egress context associated with the previous generation.

## HTTP CONNECT Behavior

<a id="REQ-PROXY-0017"></a>

**REQ-PROXY-0017:**

For each proxied TCP stream, Barometer:

1. opens one TCP connection to the configured loopback endpoint;
2. sends a bounded HTTP/1.1 `CONNECT` request for the exact target authority selected by the test;
3. sends no proxy credentials or application cookies;
4. accepts only a syntactically valid 2xx CONNECT response within the execution deadline;
5. treats the established tunnel as the test's TCP stream;
6. performs TLS, HTTP, or another registered application operation inside that stream;
7. closes the tunnel when the operation completes, is cancelled, or reaches a bound.

<a id="REQ-PROXY-0018"></a>

**REQ-PROXY-0018:**

Barometer must not send the measurement target as a normal cleartext HTTP request through the proxy. Redirects accepted by a test require a new CONNECT tunnel and must remain on the same proxy generation.

<a id="REQ-PROXY-0019"></a>

**REQ-PROXY-0019:**

When a test supplies an explicit target IP address, the CONNECT authority uses that address and port. When a compatible test supplies only a hostname, the CONNECT authority uses the normalized hostname and port, and destination resolution occurs behind the proxy. Results must preserve this distinction because direct and proxied runs may use different DNS paths.

<a id="REQ-PROXY-0020"></a>

**REQ-PROXY-0020:**

Connection pooling or tunnel reuse across separate measurement attempts is not supported in the first version. HTTP/2 CONNECT, HTTP/3 CONNECT, SOCKS, UDP association, and CONNECT authentication are outside the initial scope.

## Task Selection

Tasks select the path through [`execution.network_path`](../data-formats/task-execution.md#network-path):

```json
{
  "execution": {
    "network_path": "proxy",
    "limits": {}
  }
}
```

<a id="REQ-PROXY-0021"></a>

**REQ-PROXY-0021:**

The task contains no proxy ID because the first version supports only the single proxy currently configured by the host. It also contains no endpoint or `connection_code`.

<a id="REQ-PROXY-0022"></a>

**REQ-PROXY-0022:**

If `network_path` is omitted, the task uses `direct`. A task requesting `proxy` is eligible only when the host has configured a valid proxy, local policy permits its use, and the complete test configuration is compatible.

## Network Context

<a id="REQ-PROXY-0023"></a>

**REQ-PROXY-0023:**

When egress context is enabled, lookup requests for a proxy task must use the same proxy generation as the measurement. The primary endpoint and optional fallback endpoint are both contacted through HTTP CONNECT. Failure of the primary must not cause a direct request; the fallback is attempted through the same proxy.

<a id="REQ-PROXY-0024"></a>

**REQ-PROXY-0024:**

A cached context may be reused only when it belongs to the same access-network generation and proxy generation. Proxy context acquisition and fallback behavior are defined in [`network-context.md`](network-context.md#acquisition-and-fallback).

<a id="REQ-PROXY-0025"></a>

**REQ-PROXY-0025:**

Failure to classify proxy egress is recorded as unavailable network context. It does not prove that the proxy or classification service is censored and does not permit direct fallback. If the task requires the missing context, execution does not begin.

## Initial Test Compatibility

<a id="REQ-PROXY-0026"></a>

**REQ-PROXY-0026:**

| Test | Proxy compatibility |
|---|---|
| `TCP-01` | Supported. CONNECT uses the configured IP address and port. |
| `TLS-01` | Supported. CONNECT uses the configured IP address and port; TLS SNI and certificate validation remain unchanged inside the tunnel. |
| `HTTP-01` | Supported when `address_family` is `auto`. CONNECT uses the URL hostname and destination resolution occurs behind the proxy. Every followed redirect must use the same proxy generation. |
| `DNS-01` | Supported only in `direct` resolver mode with `transport: tcp`. System resolution and direct UDP are incompatible with HTTP CONNECT. |
| `DNS-03` | Supported only with an approved `bootstrap_ip`; CONNECT uses that address while TLS authenticates the resolver hostname. |
| `DNS-04` | Supported only with an approved `bootstrap_ip`; CONNECT uses that address while TLS authenticates the resolver hostname. |
| `NET-01` | Not applicable and therefore rejected with `network_path: proxy`; the test observes local device network state and opens no proxyable stream. |
| `NET-03` | Not supported through the proxy in the first version because it combines platform validation state with an endpoint request and requires separate path semantics. |
| `NET-05` | Supported only when every contained step is compatible. The full profile is rejected before execution if any step is incompatible. |

<a id="REQ-PROXY-0027"></a>

**REQ-PROXY-0027:**

Compatibility is validated before network activity. The library must not execute a compatible subset of an incompatible task or NET-05 profile.

## Execution States

<a id="REQ-PROXY-0028"></a>

**REQ-PROXY-0028:**

| State | Meaning |
|---|---|
| `proxy_not_configured` | The task requires `proxy`, but the host has no active proxy configuration. |
| `proxy_not_permitted` | Local policy does not allow the task to use the configured proxy. |
| `proxy_path_unsupported` | The test, input, or options require an operation that HTTP CONNECT cannot provide. |
| `proxy_unavailable` | Barometer cannot open a TCP connection to the configured local endpoint. |
| `proxy_connect_failed` | The proxy returns a non-2xx response, closes the connection, produces an invalid response, or does not complete CONNECT within the deadline. |
| `proxy_reconfigured` | The host replaces or clears the proxy during the attempt. |

<a id="REQ-PROXY-0029"></a>

**REQ-PROXY-0029:**

These are execution or path observations, not proof that the target, proxy, circumvention method, or network is censored. When CONNECT succeeds, subsequent protocol outcomes remain the registered test's observations.

<a id="REQ-PROXY-0030"></a>

**REQ-PROXY-0030:**

The library must not retry through the direct path. Any retry through a newly configured proxy requires a separately scheduled execution attempt.

## Result Metadata

<a id="REQ-PROXY-0031"></a>

**REQ-PROXY-0031:**

A completed or failed attempt records the selected path and connection code inside the normalized [Network Context](../data-formats/network-context.md):

```json
{
  "network_context": {
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
      "asn": 64500,
      "classification_version": "0.1.0"
    }
  }
}
```

<a id="REQ-PROXY-0032"></a>

**REQ-PROXY-0032:**

Direct attempts record `network_path: direct` and omit `connection_code`.

<a id="REQ-PROXY-0033"></a>

**REQ-PROXY-0033:**

Results must not contain the proxy host, port, generation, CONNECT request, proxy response headers, proxy response body, or Outline transport configuration. A normalized CONNECT status class may be retained only if the result schema demonstrates that it is necessary for interpretation.

## Privacy, Safety, and Interpretation

<a id="REQ-PROXY-0034"></a>

**REQ-PROXY-0034:**

- The proxy endpoint is supplied only by the trusted host integration and cannot be changed by a task.

<a id="REQ-PROXY-0035"></a>

**REQ-PROXY-0035:**

- Local policy retains final authority to reject proxy execution.

<a id="REQ-PROXY-0036"></a>

**REQ-PROXY-0036:**

- No direct fallback is permitted after a task selects `proxy`.

<a id="REQ-PROXY-0037"></a>

**REQ-PROXY-0037:**

- Target validation remains in force; a proxy must not make local, private, sensitive, or otherwise prohibited measurement targets eligible.

<a id="REQ-PROXY-0038"></a>

**REQ-PROXY-0038:**

- `connection_code` must remain coarse enough to avoid identifying a user, account, server, session, or installation.

<a id="REQ-PROXY-0039"></a>

**REQ-PROXY-0039:**

- A successful proxied result does not prove that the direct path is censored.

<a id="REQ-PROXY-0040"></a>

**REQ-PROXY-0040:**

- A direct failure followed by proxied success can support comparison, but outages, DNS-path differences, endpoint changes, proxy behavior, and transient network conditions remain alternative explanations.

<a id="REQ-PROXY-0041"></a>

**REQ-PROXY-0041:**

- Stronger interpretation requires repeated observations, stable network context, equivalent test inputs, and independent supporting signals.

## Known Limitations

- HTTP CONNECT provides TCP streams only and cannot carry the direct UDP behavior required by some DNS measurements.
- Hostname-based CONNECT moves destination resolution behind the proxy, so a proxied HTTP result is not a pure transport-only comparison with a direct result.
- A local proxy may select or change its own upstream strategy without exposing that change to Barometer. `connection_code` describes the host-provided category, not a verified internal strategy.
- Cancelling active attempts during proxy renewal may produce incomplete measurements.
- Mobile background suspension can stop either Barometer or the host proxy and must not be interpreted as network interference.
