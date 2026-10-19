# Task Trust and Local Policy

**Status:** Draft  
**Version:** 0.1.0

Runtime JSON values follow the shared [strict decoding contract](../data-formats/json-decoding.md) in addition to this document's schema, limits, and validation rules.

## Overview

<a id="REQ-TRUST-0002"></a>

**REQ-TRUST-0002:**

Barometer accepts a task only after the host establishes its provenance and the library validates it against immutable trusted local policy, registered measurement behavior, and [Registered Initial Limits](registered-limits.md).

<a id="REQ-TRUST-0003"></a>

**REQ-TRUST-0003:**

Task fields are untrusted input. A task cannot authenticate itself, authorize its targets, declare itself safe, update local policy, or establish that its identifier is non-user-specific.

This contract does not require one scheduler, backend, TLS profile, or signature container. It defines the evidence the host must establish and the behavior the library must enforce.

## Accepted Task Origins

Version `0.1.0` supports two origins:

<a id="REQ-TRUST-0004"></a>

**REQ-TRUST-0004:**

| Origin | Trust requirement |
|---|---|
| `embedded` | The exact task is packaged with a reviewed host deployment and covered by that deployment's release review. |
| `remote` | The host authenticates the issuer and verifies task integrity through a reviewed mechanism before passing the task to Barometer. |

<a id="REQ-TRUST-0005"></a>

**REQ-TRUST-0005:**

Examples of a remote mechanism include an authenticated, integrity-protected channel or a verified signed task package. Transport encryption without authenticated issuer authorization is insufficient.

<a id="REQ-TRUST-0001"></a>

**REQ-TRUST-0001:**

Barometer must not accept a remote task when authentication, integrity verification, trusted time needed for validity, or source context is unavailable.

## Trusted Source Context

<a id="REQ-TRUST-0006"></a>

**REQ-TRUST-0006:**

The host supplies source context through an internal initialization or admission boundary separate from serialized task fields:

<a id="REQ-TRUST-0007"></a>

**REQ-TRUST-0007:**

| Property | Required | Constraints | Meaning |
|---|:---:|---|---|
| `origin` | Yes | `embedded` or `remote` | How provenance was established. |
| `issuer_id` | Yes | 1–64 lowercase ASCII letters, digits, `.`, `_`, or `-`; deployment-scoped and non-user-specific | Stable policy principal authorized to submit the task. |
| `policy_generation` | Yes | Positive monotonically increasing integer | Trusted local policy generation used for admission. |
| `authenticated` | Yes | `true` for `remote`; `false` for reviewed `embedded` origin | Whether remote issuer authentication and integrity verification were required and succeeded. |
| `issued_at` | Conditional | RFC 3339 UTC timestamp required for `remote`; absent for `embedded`; no more than 300 seconds in the future | Authenticated issuance time used to bound task validity. |

<a id="REQ-TRUST-0008"></a>

**REQ-TRUST-0008:**

These properties are not task labels, do not appear in measurement traffic, and are not copied to Measurement Results. A task, server response, collector, target, or proxy cannot supply or override them through the public task object.

<a id="REQ-TRUST-0009"></a>

**REQ-TRUST-0009:**

The concrete Go, native, or Flutter API may represent this context differently, but it must preserve the same trust boundary. Flutter applications must not be asked to provide raw verification keys or mark arbitrary task data authenticated.

## Issuer Authorization

<a id="REQ-TRUST-0010"></a>

**REQ-TRUST-0010:**

Trusted local policy maps each `issuer_id` to the behavior it may request. Authorization is an intersection, not a union:

```text
effective authority =
    registered test behavior
    intersect issuer authorization
    intersect trusted local policy
    intersect platform capability
    intersect task-declared restrictions
```

<a id="REQ-TRUST-0011"></a>

**REQ-TRUST-0011:**

Issuer authorization must bound:

- permitted test IDs and exact versions;
- registered target, resolver, validation, and redirect entries;
- direct and proxy path use;
- maximum risk and consent handling;
- schedule, retry, resource, result, and retention limits;
- whether medium-risk tests and NET-05 are enabled;
- permitted task label namespaces, if any.

<a id="REQ-TRUST-0012"></a>

**REQ-TRUST-0012:**

A remote task may narrow these values. It cannot add authority or raise a limit.

## Target Registration

<a id="REQ-TRUST-0013"></a>

**REQ-TRUST-0013:**

Every remote destination or name must match a locally available registration before task acceptance. A registration identifies the complete safety-relevant tuple for the applicable test, including as needed:

<a id="REQ-TRUST-0014"></a>

**REQ-TRUST-0014:**

- normalized hostname, URL, IP address, port, and scheme;
- resolver name and approved bootstrap addresses;
- TLS server name and allowed ALPN values;
- expected response status and bounded checks;
- permitted redirect targets;
- allowed direct or proxy paths;
- baseline risk, owner, purpose, review generation, and expiry.

<a id="REQ-TRUST-0015"></a>

**REQ-TRUST-0015:**

Registrations must use stable non-user-specific identifiers and contain no credentials, participant data, runtime interpolation, or secret endpoints. Matching must occur on normalized typed values rather than substring or suffix rules that could authorize unintended targets.

<a id="REQ-TRUST-0016"></a>

**REQ-TRUST-0016:**

DNS resolution or a redirect does not extend authority. Every address or redirect target must still satisfy the registered test and local address policy immediately before contact.

## Admission Procedure

<a id="REQ-TRUST-0017"></a>

**REQ-TRUST-0017:**

Barometer performs the following steps before a task is scheduled:

1. Receive the exact serialized task and trusted source context.
2. Require valid remote authentication or reviewed embedded origin.
3. Validate authenticated issuance time and parse within the registered task byte limit.
4. Validate the complete top-level schema and exact versions.
5. Validate `task_id` as campaign-scoped and non-user-specific.
6. Validate expiry, schedule, retry, execution, safety, and all numeric limits.
7. Resolve the exact test, target registrations, issuer authority, and current policy generation.
8. Validate all input, options, proxy compatibility, target tuples, redirect registrations, and composite steps atomically.
9. Determine effective risk and consent requirements without allowing the task to lower them.
10. Apply replay and conflicting-reuse checks.
11. Accept the task idempotently or return a bounded non-measurement admission error.

<a id="REQ-TRUST-0018"></a>

**REQ-TRUST-0018:**

No network measurement may begin during admission. Context lookup used only for later execution eligibility must not be performed to make an invalid task acceptable.

## Task Identifier Rules

<a id="REQ-TRUST-0019"></a>

**REQ-TRUST-0019:**

`task_id` must:

- be 1–128 bytes of lowercase ASCII letters, digits, `.`, `_`, or `-`;
- identify one campaign task definition within the issuer namespace;
- be identical for every installation receiving the same task definition;
- not contain or derive from a person, account, installation, device, advertising ID, push token, linkage token, IP address, or other participant-specific value;
- not be used to select an individual installation or reconstruct cross-bundle linkage.

<a id="REQ-TRUST-0020"></a>

**REQ-TRUST-0020:**

The effective replay key is `(issuer_id, task_id)`.

## Replay, Duplicate, and Rollback Handling

<a id="REQ-TRUST-0021"></a>

**REQ-TRUST-0021:**

For the validity of an accepted task plus the replay-retention period, Barometer stores a bounded local record containing:

<a id="REQ-TRUST-0022"></a>

**REQ-TRUST-0022:**

- the effective replay key;
- a SHA-256 digest of the exact accepted task bytes;
- the accepted policy generation;
- acceptance and expiry classes needed for cleanup.

<a id="REQ-TRUST-0023"></a>

**REQ-TRUST-0023:**

The record contains no task input, target, label, participant identifier, or result.

Handling is:

<a id="REQ-TRUST-0024"></a>

**REQ-TRUST-0024:**

| Condition | Behavior |
|---|---|
| New replay key and valid task | Continue admission. |
| Same replay key and same digest | Treat as idempotent redelivery; do not create duplicate runs or extend expiry. |
| Same replay key and different digest | Reject as `task_id_conflict`. |
| Lower policy generation than the active generation | Reject as `policy_rollback`. |
| Expired task | Reject as `task_expired`; never reactivate it. |
| Replay state unavailable or invalid for a remote task | Fail closed with `task_trust_unavailable`. |

<a id="REQ-TRUST-0025"></a>

**REQ-TRUST-0025:**

Reinstallation or explicit Barometer data clearing removes replay state. A remote task redelivered after that reset is evaluated as new, which is residual exposure and must remain bounded by task expiry and schedule limits.

<a id="REQ-TRUST-0038"></a>

**REQ-TRUST-0038:**

Unavailable or invalid replay state also fails closed for an `embedded` task: Barometer rejects it with `task_trust_unavailable` and does not accept it without replay state.

## Targeted Delivery

<a id="REQ-TRUST-0026"></a>

**REQ-TRUST-0026:**

The baseline version prohibits selecting task recipients using:

- Barometer installation or linkage tokens;
- bundle or run identifiers;
- account, advertising, device, SIM, subscriber, or push identifiers;
- exact IP address or precise location;
- prior per-installation measurement outcomes.

<a id="REQ-TRUST-0027"></a>

**REQ-TRUST-0027:**

Broad deployment, application-version, consented cohort, country, or network eligibility may be applied only by reviewed host policy using non-user-specific criteria and sufficiently broad groups. A task cannot request local interpolation of those values into its identifiers, labels, targets, or payload.

<a id="REQ-TRUST-0028"></a>

**REQ-TRUST-0028:**

Result linkage must not affect task selection. A deployment that needs participant-specific longitudinal research requires a new specification, explicit consent and ethics/privacy/safety review, and cannot claim compliance with this baseline.

## Local Policy Lifecycle

<a id="REQ-TRUST-0029"></a>

**REQ-TRUST-0029:**

Trusted local policy and target registrations are loaded during initialization and remain immutable for that initialized library instance.

<a id="REQ-TRUST-0030"></a>

**REQ-TRUST-0030:**

An update requires:

1. authentication and integrity verification by the host deployment;
2. a strictly greater `policy_generation`;
3. complete validation before activation;
4. cancellation or rejection of tasks no longer permitted;
5. invalidation of policy-dependent caches;
6. library reinitialization before new-policy tasks run.

<a id="REQ-TRUST-0031"></a>

**REQ-TRUST-0031:**

Failure during update leaves the previous complete policy active or leaves Barometer uninitialized. Partial activation and rollback to an earlier generation are prohibited.

<a id="REQ-TRUST-0032"></a>

**REQ-TRUST-0032:**

Remote tasks, collector responses, measurement targets, proxies, and context endpoints cannot update policy.

## Admission Errors

<a id="REQ-TRUST-0033"></a>

**REQ-TRUST-0033:**

Task trust and validation errors are bounded operational states, not Measurement Results and not evidence of censorship. Initial error classes include:

<a id="REQ-TRUST-0034"></a>

**REQ-TRUST-0034:**

- `task_source_unauthenticated`
- `task_issuer_not_authorized`
- `task_policy_unavailable`
- `task_trust_unavailable`
- `task_expired`
- `task_id_conflict`
- `policy_rollback`
- `target_not_registered`
- `task_limit_exceeded`
- `task_schema_invalid`

<a id="REQ-TRUST-0035"></a>

**REQ-TRUST-0035:**

Errors must not include task payloads, target values, credentials, verification keys, signatures, participant data, or raw platform errors.

<a id="REQ-TRUST-0036"></a>

**REQ-TRUST-0036:**

In addition to the classes in REQ-TRUST-0034, Barometer returns `task_unsupported` when a task is valid under the public task schema but requires something the implementation does not provide:

- a well-formed `test_id` and `test_version` pair that the implementation does not register;
- a risk factor `type` the implementation does not recognize, when the implementation rejects the task under [REQ-SAFETY-0017](../data-formats/task-safety.md#REQ-SAFETY-0017) instead of treating that factor's risk as `unknown`;
- a capability that a valid task field requires, such as egress Network Context acquisition for `execution.context`.

`task_unsupported` describes the implementation, not the task's validity or safety or the state of the network. An implementation that provides a capability does not return this class for it. Runtime unavailability of a provided capability remains an unsatisfied execution constraint under [REQ-CONTEXT-0026](network-context.md#REQ-CONTEXT-0026) and [REQ-CONTEXT-0028](network-context.md#REQ-CONTEXT-0028).

<a id="REQ-TRUST-0037"></a>

**REQ-TRUST-0037:**

A rejected task receives exactly one class: the class of the first step, in [REQ-TRUST-0017](#REQ-TRUST-0017) order, that fails. Where another requirement names the class for a condition, that class applies. The following conditions use the listed class:

| Step | Condition | Class |
|---|---|---|
| 1 | The exact presented task bytes are not bound to the supplied trusted source context, or that binding is missing or expired. | `task_source_unauthenticated` |
| 3 | Trusted time needed for validity is unavailable. | `task_trust_unavailable` |
| 3 | Remote `issued_at` is more than 300 seconds in the future. | `task_source_unauthenticated` |
| 4 | The `test_id` and `test_version` pair is not registered by the implementation (REQ-TRUST-0036). | `task_unsupported` |
| 5 | `task_id` exceeds 128 bytes. | `task_limit_exceeded` |
| 6 | A risk factor type is rejected as unsupported, or a valid field requires a capability the implementation does not provide (REQ-TRUST-0036). | `task_unsupported` |
| 7 | The source context `policy_generation` is greater than the active policy generation. | `task_policy_unavailable` |
| 8 | A direct or proxy path is not permitted by issuer authority or local policy. | `task_issuer_not_authorized` |
| 8 | A direct or proxy path is not permitted by the matched target registration. | `target_not_registered` |
| 9 | Effective risk exceeds a local-policy bound, or is `unknown` without an explicit reviewed local policy permitting it. | `task_issuer_not_authorized` |

<a id="REQ-TRUST-0039"></a>

**REQ-TRUST-0039:**

At step 8 of [REQ-TRUST-0017](#REQ-TRUST-0017), a task with `network_path: proxy` whose test, input or options are not compatible with HTTP CONNECT under [REQ-PROXY-0026](proxy.md#REQ-PROXY-0026), including a `NET-05` profile with any incompatible step, is rejected with `task_schema_invalid`. Within step 8, proxy compatibility is evaluated after input and options and before path authority and target registration. A combination that REQ-PROXY-0026 permits but the implementation does not provide through the proxy is rejected with `task_unsupported` under [REQ-TRUST-0036](#REQ-TRUST-0036).

## Residual Risks

- A compromised host, admitted issuer, operating system, or policy package can misuse authority available to it.
- Authentication establishes provenance, not that a task is safe; local policy remains mandatory.
- Authenticated delivery infrastructure can observe recipient addresses and timing unless separately minimized.
- Broad cohort delivery can still expose rare groups when combined with other data.
- Local replay state cannot survive explicit data clearing by design.
- Target ownership, infrastructure, and sensitivity can change after review; registrations therefore require bounded validity and operational review.
