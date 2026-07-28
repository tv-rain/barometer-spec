# Threat Model

**Status:** Draft  
**Version:** 0.1.0

## Purpose and Scope

This threat model covers Barometer's initial embedded mobile measurement system: task admission, local policy, bounded execution, direct and host-configured proxy paths, Network Context acquisition, result construction, optional rotating linkage, local persistence, and delivery to a collector.

It defines security and privacy assumptions, adversaries, trust boundaries, required mitigations, and residual exposure. It does not claim zero risk, anonymity, or complete protection from a compromised device or host application.

The model applies to the public version `0.1.0` specifications. A deployment must add its concrete host application, task-delivery mechanism, targets, proxy or circumvention component, context endpoints, collector, jurisdictions, and data flows before release.

## Safety Objectives

Barometer must:

- execute only authenticated, registered, locally permitted measurement behavior;
- prevent tasks from weakening local policy, consent, target, path, or resource controls;
- minimize identifiers and measurement content retained or transmitted;
- avoid silent fallback between direct and proxy paths;
- keep execution, repetition, result size, and local retention bounded;
- distinguish execution failures from network observations;
- avoid producing a local censorship, intent, or attribution verdict;
- preserve enough normalized evidence to support cautious later interpretation;
- provide explicit cancellation and data-clearing behavior.

Availability and measurement coverage are secondary to these safety objectives.

## System and Trust Boundaries

```text
remote task service
        |
        | authenticated and integrity-protected delivery
        v
trusted host integration ---- trusted local policy and target registrations
        |
        | admitted task plus non-task-controlled source context
        v
Barometer library
   |          |             |
   | direct   | local proxy | context lookup
   v          v             v
network   host-managed   reviewed context
target    proxy path     endpoint
   \          |             /
    \--------- network ----/
               |
               v
        result bundle delivery
               |
               v
            collector
               |
               v
        analysis and publication
```

The trusted computing base for one deployment includes the Barometer library, its native bindings, the host integration that establishes task provenance, trusted local policy, registered target data, and the operating-system facilities used for storage, time, network selection, and cancellation.

Remote tasks, measurement targets, network intermediaries, context endpoint responses, proxy responses, collector input, and analysis input are untrusted data even when their operators are organizationally trusted.

## Protected Assets

- Participant safety and plausible ordinary application behavior.
- The confidentiality of user, account, device, subscriber, location, and application data that Barometer must not collect.
- Task and policy integrity.
- Measurement target and path restrictions.
- Resource, schedule, retry, and retention limits.
- Installation secrets and rotating linkage tokens.
- The semantic integrity of observations, execution states, and interpretation limits.
- Local pending results and deletion state.

## Adversaries and Failure Sources

### Network Observer or Active Intermediary

An access provider, censor, enterprise gateway, captive portal, VPN, proxy, or on-path attacker may observe destinations and timing; drop, reset, delay, redirect, inject, or selectively allow traffic; fingerprint TLS or protocol behavior; and treat known measurement endpoints specially.

### Malicious or Compromised Task Source

An issuer may attempt to select sensitive targets, create distinctive schedules, exceed limits, replay tasks, reuse identifiers for tracking, lower declared risk, or cause different installations to receive uniquely identifying tasks.

### Malicious Target, Proxy, or Context Endpoint

An endpoint may return oversized, malformed, delayed, inconsistent, or identifying content; redirect to prohibited destinations; attempt protocol confusion; or retain source addresses and timing.

### Malicious or Over-collecting Collector

A collector may retain source IP addresses, precise arrival time, task IDs, rotating tokens, account identity, or rare context combinations and use them to re-identify or target participants.

### Compromised Host, Binding, Device, or Operating System

A compromised trusted component may inspect tasks, targets, results, keys, source addresses, or user state and may bypass library policy. Barometer can reduce exposed data but cannot fully protect against this adversary.

### Analyst Error or Misuse

An analyst may treat one failure as censorship, ignore missing or non-independent observations, conflate egress with physical location, treat an installation as a person, or present internal confidence and derived classifications as statistical proof.

### Ordinary Operational Failure

Outages, congestion, routing changes, DNS caching, CDN behavior, certificate errors, device clock problems, mobile handover, platform suspension, and stale configuration may resemble interference without malicious action.

## Required Assumptions

- The host establishes task authenticity and integrity as defined in [Task Trust and Local Policy](library/task-trust.md).
- Trusted local policy and target registrations are reviewed, non-user-specific, available before admission, and immutable for one initialized instance.
- The implementation enforces the canonical [Registered Initial Limits](library/registered-limits.md) or stricter local limits.
- The host does not add credentials, cookies, account identity, application telemetry, or stable identifiers to Barometer traffic.
- Measurement and context endpoints are public, controlled or explicitly approved, non-sensitive, and suitable for the registered operation.
- Collector and deployment operators apply bounded retention, access control, transport-log minimization, and aggregate publication rules.
- Supported platform behavior is validated on each released Android and Apple integration.

If an assumption is absent or cannot be evaluated reliably, the affected operation must fail closed or report an explicit non-censorship unavailable state.

## Threats, Mitigations, and Residual Exposure

| Threat | Required mitigations | Residual exposure |
|---|---|---|
| Unauthorized or modified task | Host-authenticated provenance; complete schema validation; trusted issuer authorization; local policy and target allowlists | A compromised admitted issuer or host can still request harmful behavior within its authority |
| Task replay or conflicting identifier reuse | Bounded validity; exact duplicate idempotency; reject same issuer and `task_id` with different content; bounded replay state | Restore, clock, or storage failure can make replay detection unavailable, which must fail closed for remote tasks |
| Per-installation task targeting | Campaign-scoped non-user-specific task identifiers; prohibit delivery selection by installation, account, linkage token, or device property | Network delivery infrastructure may still observe source addresses unless separately minimized |
| Excessive or distinctive measurement cadence | Required expiry and run count for repeated tasks; minimum interval; local jitter; no measurement-outcome retry; registered traffic limits | Even bounded repeated traffic and fixed endpoint sequences may be recognizable |
| Sensitive or internal target access | Registered public target tuples; redirect validation before contact; reject local, private, link-local, special-purpose, credentialed, or interpolated targets | Public targets may change ownership, behavior, hosting, or sensitivity after registration |
| Direct-path leakage after proxy selection | Immutable path snapshot; no direct fallback; atomic NET-05 profile validation | The local proxy and its upstream can observe target authority and source-network information |
| Endpoint response resource exhaustion | Response, body, header, DNS, result, bundle, time, and connection limits; bounded parsing; cancellation | Protocol stacks may buffer more on wire than the application processes |
| Identifier leakage or linkage abuse | Prohibit user/device/account identifiers; random run and bundle IDs; linkage off by default; bounded token rotation; no task selection by linkage | Source IP, time, task, context, and token combinations can re-identify if a collector retains them together |
| Result tampering or semantic confusion | Exact versioned schemas; reject unknown fields; preserve source observations; separate derived analysis | The initial specification does not provide end-to-end result signatures |
| Selective treatment of known endpoints | Multiple reviewed controls, repeated observations, independent signals, cautious interpretation | A capable censor can identify or selectively allow every known measurement target |
| False censorship conclusion | Explicit alternative explanations; separate execution and measurement states; no local censorship verdict | Later analysts or downstream products may still misuse valid observations |
| Local data persistence after reset | Bounded pending retention; protected non-synchronizing secret storage; explicit clear-data contract; orphan recovery | Platform bugs, backups, crash logs, or a compromised OS can retain data |

## Abuse Cases That Must Be Tested

- A validly shaped remote task arrives without authenticated source context.
- An exact task is redelivered, followed by a task using the same issuer and `task_id` with different bytes.
- A repeating task omits expiry, exceeds the maximum run count, requests too short an interval, or requests no jitter.
- A task declares lower risk or consent requirements than the registered test.
- A task uses a unique participant, account, device, or linkage-derived value in `task_id`, labels, targets, or scheduling.
- A redirect resolves to a prohibited address or changes to a prohibited target between validation and connection.
- A proxy-selected operation loses the proxy or receives a new proxy generation during execution.
- A DNS, HTTP, context, or proxy response reaches every registered size and time boundary.
- A network changes during each measurement stage and during a NET-05 profile.
- Data clearing is interrupted after result deletion and after key deletion.
- A collector receives linkage together with account authentication, source IP, precise time, or rare location/network context.

## Interpretation and Misuse Boundary

A Measurement Result is an observation from one implementation, task, path, network context, and time window. It does not by itself:

- prove censorship or intent;
- identify an interfering party;
- establish that a target or resolver answer is correct;
- represent a person, population, country, provider, or all users of a network;
- establish physical location from egress classification;
- make skipped, missing, cached, retried, or repeated observations independent.

Derived analysis must identify its method and version, preserve links to source observations, account for alternative explanations and missingness, and remain separate from the source result.

## Residual Risks

- A compromised host, operating system, admitted issuer, proxy, collector, or endpoint may observe or misuse data that it legitimately receives.
- Network observers can see destinations, ports, timing, traffic volume, and plaintext protocol metadata such as DNS names or TLS SNI where applicable.
- Fixed resolver, validation, and multi-endpoint profiles can identify participation even when payloads contain no identifier.
- Endpoint and infrastructure independence cannot be guaranteed from configuration alone.
- Mobile platform APIs can hide retries, caches, routing, or failure detail and can terminate work without a protocol-level outcome.
- Source IP and timing exist at network-facing services even when Barometer does not serialize them.
- A valid low-risk classification is conditional on reviewed targets, cadence, deployment, platform behavior, and current local context.

## Review Triggers

The threat model and affected public requirements must be reviewed before adding:

- a new measurement or protocol behavior;
- sensitive, political, circumvention, local-network, malformed, scanning, packet-capture, or high-volume targets;
- a non-loopback proxy, proxy authentication, UDP proxying, or direct fallback;
- remote policy updates without reinitialization;
- participant-targeted task delivery;
- stable linkage, longer linkage rotation, account-authenticated ingestion, or new retained identifiers;
- precise location, operator, device, SIM, subscriber, or user information;
- increased registered limits or background execution behavior;
- a new collector, task issuer, context endpoint, platform, or deployment jurisdiction.

