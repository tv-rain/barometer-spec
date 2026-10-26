# Measurement Limitations

**Status:** Draft  
**Version:** 0.1.0

## Purpose

This document defines cross-cutting limitations for interpreting Barometer measurements and provides a consolidated index of test-specific limitations. It applies to source observations, direct and proxy comparisons, derived analysis, aggregate reporting, and public claims.

The individual test specifications remain authoritative for their measurement questions, methods, outcomes, and test-specific alternative explanations. The [Threat Model](threat-model.md) separately defines adversaries, assumptions, mitigations, and residual exposure.

## Fundamental Interpretation Boundary

A Barometer result is an observation produced by one registered test version, implementation version, device platform, task configuration, network path, network generation, and time window.

A result does not by itself:

- prove censorship, blocking policy, manipulation, or intent;
- identify who caused an observed condition;
- establish that a DNS answer, endpoint response, or external reference is correct;
- establish that a failure is persistent, geographically broad, or shared by other users;
- represent a person, population, provider, country, or all users of a network;
- establish physical location from an egress classification;
- show that a direct and proxy path differed only in circumvention behavior;
- make repeated, cached, retried, or bundled observations independent.

Use language such as “observed,” “consistent with,” “could not complete,” or “differed on the measured paths.” Do not convert a single negative outcome into “censored,” “blocked by the government,” “country-wide,” or an equivalent definitive claim.

## Execution, Missingness, and Reporting

Tasks may be rejected, delayed, skipped, cancelled, suspended, interrupted by network change, prevented by local policy, or left unreported because the application cannot deliver a pending result. These cases are not successful measurements of reachability and must not be counted as target failures.

Observed results can be a biased subset of scheduled work:

- devices with stable connectivity may report more often;
- hostile or heavily restricted networks may prevent both measurement and upload;
- operating systems may favor foreground, charged, or recently used applications;
- local policy may exclude higher-risk contexts;
- application adoption and usage are not random samples of a population;
- delayed uploads can separate observation time from collector arrival time.

Analyses must report the relevant counts of accepted, not-run, incomplete, completed, missing, expired, and undelivered work when those denominators are available. Absence of a result must remain unknown rather than being imputed as success or failure without a documented method.

## Sampling and Representativeness

Barometer observes devices on which a participating host application is installed, enabled, permitted to run, and able to report. This is a deployment sample, not a probability sample of:

- people in a country or region;
- subscribers of an operator;
- all devices on an ASN;
- all users of a circumvention system;
- all destinations or protocols on the Internet.

Installation tokens are not people. One person may use multiple installations, while one installation or device may be shared. Counts must not be presented as unique-user counts.

Population estimates, prevalence claims, and comparisons between deployments require a separately documented sampling and weighting method. The source measurement format does not provide one.

## Time and Network Scope

Results apply to the recorded time precision and observed network generation. Mobile networks can change access path, public egress, address family, NAT, carrier gateway, proxy strategy, or routing without every change being visible to the operating system.

Comparisons should require:

- compatible test, result, and implementation versions;
- equivalent normalized inputs and options;
- the same intended connection path;
- stable network generation where observable;
- sufficiently close observation times for the stated claim;
- explicit treatment of cached context and delayed upload.

Observations from different times, regions, networks, address families, or methods may support triangulation, but they are not interchangeable controls or ground truth.

## Repetition, Caching, and Independence

Repeated observations strengthen interpretation only when their dependence is considered. They may reuse:

- operating-system or resolver caches;
- the same recursive resolver, CDN, origin, route, proxy, or carrier gateway;
- one Network Context classification;
- one task profile or known endpoint sequence;
- the same platform implementation and error mapping.

Back-to-back repetition can increase traffic distinctiveness without adding independent evidence. A repeated result is not automatically an independent sample, and a retry of an execution failure is not a new measurement outcome.

## Targets, Controls, and External References

Measurement targets, resolvers, validation services, CDNs, and context endpoints can fail, change behavior, rate-limit, vary by geography, or receive special treatment.

A suitable control should be selected for the specific measurement question and should have documented ownership, expected behavior, and relevant infrastructure dependencies. Two different hostnames are not necessarily independent when they share DNS, CDN, hosting, transit, certificate, or administrative control.

A capable network operator may recognize and selectively allow known validation or measurement endpoints. Successful controls therefore reduce some alternative explanations but do not prove that the measurement traffic was treated like ordinary user traffic.

External measurement datasets and server-side reference observations may differ in time, geography, vantage point, resolver, protocol, software, and target configuration. They support triangulation but are not ground truth.

## Layer Attribution

Ordered DNS, TCP, TLS, and HTTP observations can identify the first stage that did not complete normally under the registered method. They do not uniquely identify the cause.

For example:

- DNS failure can result from resolver, authoritative, routing, cache, policy, or platform behavior.
- TCP timeout can result from packet loss, routing, firewall policy, target overload, or silent filtering.
- TLS failure can result from certificates, device time, trust-store differences, protocol compatibility, proxying, or interference.
- HTTP mismatch can result from application deployment, redirects, personalization, CDN behavior, captive portals, intermediaries, or stale expectations.

Later stages cannot be interpreted when an earlier prerequisite stage did not complete. A successful lower layer does not guarantee that the application protocol is usable.

## Direct and Proxy Comparisons

A direct failure followed by proxy success can support a path comparison, but it does not prove that the direct path was censored or that the proxy bypassed censorship.

The paths may differ in:

- DNS resolution location and cache state;
- public egress, routing, peering, NAT, and address family;
- TLS and HTTP fingerprints;
- target-side geolocation, rate limits, or access policy;
- proxy retries, upstream selection, multiplexing, and hidden strategy changes;
- timing and network state between attempts.

Version `0.1.0` refuses hostname CONNECT because the library cannot inspect proxy-side destination addresses before contact. Proxy HTTP-01 therefore requires a permitted explicit-IP URL, and proxy context acquisition requires eligible explicit-IP endpoints. This reduces available path comparisons; missing proxy observations caused by these restrictions are not evidence of interference. Locally resolving or rewriting a hostname to manufacture a comparison is not permitted.

The proxy contract prohibits silent direct fallback, but it cannot make the two paths identical except for one presumed circumvention variable. Stronger comparison requires equivalent test inputs, stable context, close timing, repeated observations, and independent supporting signals.

## Platform and Implementation Differences

Android, Apple, Go, native, and host networking APIs may differ in:

- resolver selection, caching, retries, and exposed DNS response detail;
- socket-to-network binding and handover behavior;
- trust stores and certificate evaluation;
- TLS and HTTP fingerprints and protocol negotiation;
- proxy inheritance, cookies, caches, compression, and redirects;
- error granularity and timeout reporting;
- background suspension and callback delivery.

Unsupported or hidden detail remains `unknown` or `inconclusive`; implementations must not invent equivalence. Comparisons across platforms or library versions must identify material implementation differences.

## Network Context Limitations

Network Context is minimized interpretation metadata, not a device or location record.

- Country and region describe an IP classification of the selected egress, not physical location.
- ASN identifies an origin routing classification and may not identify the access provider.
- VPN detection can be unavailable or can detect an interface without proving that measured traffic used it.
- IPv4 or IPv6 availability does not establish Internet reachability.
- Platform validation can be stale or use different definitions across operating systems.
- Cached classification can outlive a public-egress change that the platform did not expose.
- A proxy `connection_code` is a host-provided category, not proof of its internal strategy.

Rare combinations of time, region, ASN, network type, task, connection code, and linkage can become identifying even when each field is coarse.

## Data-Minimization Tradeoffs

Barometer intentionally omits raw packets, full URLs in results, response bodies, header values, certificate chains, raw platform errors, resolver configuration, public IP addresses, and detailed device information.

This reduces participant and data risk but limits retrospective analysis:

- omitted raw data cannot be reclassified later;
- normalized failures can collapse platform-specific distinctions;
- coarse timing cannot support fine-grained performance claims;
- body and response bounds may stop evaluation before a mismatch is decidable;
- hashes and indexed check outcomes show configured comparison results, not the omitted content;
- task inputs must be resolved separately through authorized task records.

Analysts must not infer omitted values or treat normalization as evidence that no other behavior occurred.

## Test-Specific Limitations

| Test | Supported scope and principal limitations |
|---|---|
| [`DNS-01`](tests/dns-01.md) | Observes the selected system or direct resolver path. System APIs may hide transport, retries, caches, and response codes. Direct UDP can retain conflicting matching datagrams but cannot establish which response is legitimate; source addresses can be forged and arrival order is not authority. |
| [`DNS-03`](tests/dns-03.md) | Observes staged DoH completion and a bounded DNS result. Resolver policy, geography, bootstrap DNS, CDN behavior, certificates, and fixed bootstrap-address staleness remain alternative explanations. Failure must be attributed to the observed stage, not automatically to DoH blocking. |
| [`DNS-04`](tests/dns-04.md) | Observes staged DoT completion and a bounded DNS result. Dedicated-port failure is not uniquely attributable to censorship; bootstrap, routing, resolver, certificate, and port-policy failures remain possible. |
| [`TCP-01`](tests/tcp-01.md) | Observes one connection attempt to one address and port. Mobile error APIs may not distinguish target non-response from path filtering, and successful connection establishment does not establish application-layer usability. |
| [`TLS-01`](tests/tls-01.md) | Observes one authenticated TLS handshake. Trust-store, device-time, protocol, ALPN, server, and fingerprint differences can affect outcomes. The Go or platform TLS fingerprint may differ from host application traffic; Encrypted ClientHello is outside version `0.1.0`. |
| [`HTTP-01`](tests/http-01.md) | Observes one bounded HTTPS response and configured checks. Dynamic content, legitimate redirects, CDN behavior, geolocation, buffering beyond the application read limit, and stack fingerprint differences limit comparison. Matching is intentionally limited and does not render or execute a page. |
| [`NET-01`](tests/net-01.md) | Reports coarse operating-system state without network traffic. Platform meanings of availability, validation, and VPN differ; notifications may be delayed; address-family availability is not reachability. |
| [`NET-03`](tests/net-03.md) | Compares platform state with one known validation endpoint. The endpoint may fail or receive special treatment, and subscription, quota, enterprise, VPN, proxy, or captive-portal behavior can resemble broader interference. It does not prove arbitrary Internet reachability. |
| [`NET-05`](tests/net-05.md) | Preserves an ordered, bounded set of primitive results without a combined censorship verdict. Target roles and infrastructure independence are external to the result; known profiles can be recognizable or selectively allowed; incomplete execution is not broad restriction. |

## Stronger Interpretation

Stronger interference analysis normally requires a documented combination of:

- repeated completed observations under a conservative schedule;
- stable and comparable network context;
- multiple protocol layers;
- suitable local, application, and independently operated controls;
- direct and proxy comparisons with documented path differences;
- exclusion of captive portal, subscription, outage, configuration, and target explanations;
- independent observations from comparable times and network or geographic contexts;
- a versioned analysis method that preserves source-result links and uncertainty.

No amount of correlation establishes censor identity or intent with certainty from Barometer source observations alone.

## Derived Analysis and Publication

Derived classifications must remain separate from Measurement Results and identify:

- analysis method and version;
- source test, result, and implementation versions;
- inclusion, exclusion, missingness, and deduplication rules;
- time, network, geography, and path comparison rules;
- control selection and known shared dependencies;
- thresholds and uncertainty;
- alternative explanations that remain;
- privacy aggregation and retention controls.

Public reporting must aggregate sufficiently broad groups and suppress rare combinations that could identify an installation or access context. It must not equate installations with people, egress with physical location, internal registry confidence with statistical confidence, or a single observation with definitive censorship.

## Review and Change Requirements

This document and affected test-specific interpretation sections require review when:

- a new test or outcome is registered;
- retained fields, limits, timing precision, context, linkage, or proxy behavior change;
- an analysis component begins producing anomaly or interference classifications;
- a deployment introduces new targets, platforms, collectors, delivery paths, or participant cohorts;
- validation evidence changes a documented false-positive, false-negative, or comparability limitation.

