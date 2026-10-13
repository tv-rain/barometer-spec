# Task Trust and Local Policy

**Status:** Draft  
**Version:** 0.1.0

Runtime JSON values follow the shared [strict decoding contract](../data-formats/json-decoding.md) in addition to this document's schema, limits, and validation rules.

## Overview

Barometer accepts a task only after the host establishes its provenance and the library validates it against immutable trusted local policy, registered measurement behavior, and [Registered Initial Limits](registered-limits.md).

Task fields are untrusted input. A task cannot authenticate itself, authorize its targets, declare itself safe, update local policy, or establish that its identifier is non-user-specific.

This contract does not require one scheduler, backend, TLS profile, or signature container. It defines the evidence the host must establish and the behavior the library must enforce.

## Accepted Task Origins

Version `0.1.0` supports two origins:

| Origin | Trust requirement |
|---|---|
| `embedded` | The exact task is packaged with a reviewed host deployment and covered by that deployment's release review. |
| `remote` | The host authenticates the issuer and verifies task integrity through a reviewed mechanism before passing the task to Barometer. |

Examples of a remote mechanism include an authenticated, integrity-protected channel or a verified signed task package. Transport encryption without authenticated issuer authorization is insufficient.

<a id="REQ-TRUST-0001"></a>

**REQ-TRUST-0001:**

Barometer must not accept a remote task when authentication, integrity verification, trusted time needed for validity, or source context is unavailable.

## Trusted Source Context

The host supplies source context through an internal initialization or admission boundary separate from serialized task fields:

| Property | Required | Constraints | Meaning |
|---|:---:|---|---|
| `origin` | Yes | `embedded` or `remote` | How provenance was established. |
| `issuer_id` | Yes | 1–64 lowercase ASCII letters, digits, `.`, `_`, or `-`; deployment-scoped and non-user-specific | Stable policy principal authorized to submit the task. |
| `policy_generation` | Yes | Positive monotonically increasing integer | Trusted local policy generation used for admission. |
| `authenticated` | Yes | `true` for `remote`; `false` for reviewed `embedded` origin | Whether remote issuer authentication and integrity verification were required and succeeded. |
| `issued_at` | Conditional | RFC 3339 UTC timestamp required for `remote`; absent for `embedded`; no more than 300 seconds in the future | Authenticated issuance time used to bound task validity. |

These properties are not task labels, do not appear in measurement traffic, and are not copied to Measurement Results. A task, server response, collector, target, or proxy cannot supply or override them through the public task object.

The concrete Go, native, or Flutter API may represent this context differently, but it must preserve the same trust boundary. Flutter applications must not be asked to provide raw verification keys or mark arbitrary task data authenticated.

## Issuer Authorization

Trusted local policy maps each `issuer_id` to the behavior it may request. Authorization is an intersection, not a union:

```text
effective authority =
    registered test behavior
    intersect issuer authorization
    intersect trusted local policy
    intersect platform capability
    intersect task-declared restrictions
```

Issuer authorization must bound:

- permitted test IDs and exact versions;
- registered target, resolver, validation, and redirect entries;
- direct and proxy path use;
- maximum risk and consent handling;
- schedule, retry, resource, result, and retention limits;
- whether medium-risk tests and NET-05 are enabled;
- permitted task label namespaces, if any.

A remote task may narrow these values. It cannot add authority or raise a limit.

## Target Registration

Every remote destination or name must match a locally available registration before task acceptance. A registration identifies the complete safety-relevant tuple for the applicable test, including as needed:

- normalized hostname, URL, IP address, port, and scheme;
- resolver name and approved bootstrap addresses;
- TLS server name and allowed ALPN values;
- expected response status and bounded checks;
- permitted redirect targets;
- allowed direct or proxy paths;
- baseline risk, owner, purpose, review generation, and expiry.

Registrations must use stable non-user-specific identifiers and contain no credentials, participant data, runtime interpolation, or secret endpoints. Matching must occur on normalized typed values rather than substring or suffix rules that could authorize unintended targets.

DNS resolution or a redirect does not extend authority. Every address or redirect target must still satisfy the registered test and local address policy immediately before contact.

## Admission Procedure

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

No network measurement may begin during admission. Context lookup used only for later execution eligibility must not be performed to make an invalid task acceptable.

## Task Identifier Rules

`task_id` must:

- be 1–128 bytes of lowercase ASCII letters, digits, `.`, `_`, or `-`;
- identify one campaign task definition within the issuer namespace;
- be identical for every installation receiving the same task definition;
- not contain or derive from a person, account, installation, device, advertising ID, push token, linkage token, IP address, or other participant-specific value;
- not be used to select an individual installation or reconstruct cross-bundle linkage.

The effective replay key is `(issuer_id, task_id)`.

## Replay, Duplicate, and Rollback Handling

For the validity of an accepted task plus the replay-retention period, Barometer stores a bounded local record containing:

- the effective replay key;
- a SHA-256 digest of the exact accepted task bytes;
- the accepted policy generation;
- acceptance and expiry classes needed for cleanup.

The record contains no task input, target, label, participant identifier, or result.

Handling is:

| Condition | Behavior |
|---|---|
| New replay key and valid task | Continue admission. |
| Same replay key and same digest | Treat as idempotent redelivery; do not create duplicate runs or extend expiry. |
| Same replay key and different digest | Reject as `task_id_conflict`. |
| Lower policy generation than the active generation | Reject as `policy_rollback`. |
| Expired task | Reject as `task_expired`; never reactivate it. |
| Replay state unavailable or invalid for a remote task | Fail closed with `task_trust_unavailable`. |

Reinstallation or explicit Barometer data clearing removes replay state. A remote task redelivered after that reset is evaluated as new, which is residual exposure and must remain bounded by task expiry and schedule limits.

## Targeted Delivery

The baseline version prohibits selecting task recipients using:

- Barometer installation or linkage tokens;
- bundle or run identifiers;
- account, advertising, device, SIM, subscriber, or push identifiers;
- exact IP address or precise location;
- prior per-installation measurement outcomes.

Broad deployment, application-version, consented cohort, country, or network eligibility may be applied only by reviewed host policy using non-user-specific criteria and sufficiently broad groups. A task cannot request local interpolation of those values into its identifiers, labels, targets, or payload.

Result linkage must not affect task selection. A deployment that needs participant-specific longitudinal research requires a new specification, explicit consent and ethics/privacy/safety review, and cannot claim compliance with this baseline.

## Local Policy Lifecycle

Trusted local policy and target registrations are loaded during initialization and remain immutable for that initialized library instance.

An update requires:

1. authentication and integrity verification by the host deployment;
2. a strictly greater `policy_generation`;
3. complete validation before activation;
4. cancellation or rejection of tasks no longer permitted;
5. invalidation of policy-dependent caches;
6. library reinitialization before new-policy tasks run.

Failure during update leaves the previous complete policy active or leaves Barometer uninitialized. Partial activation and rollback to an earlier generation are prohibited.

Remote tasks, collector responses, measurement targets, proxies, and context endpoints cannot update policy.

## Admission Errors

Task trust and validation errors are bounded operational states, not Measurement Results and not evidence of censorship. Initial error classes include:

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

Errors must not include task payloads, target values, credentials, verification keys, signatures, participant data, or raw platform errors.

## Residual Risks

- A compromised host, admitted issuer, operating system, or policy package can misuse authority available to it.
- Authentication establishes provenance, not that a task is safe; local policy remains mandatory.
- Authenticated delivery infrastructure can observe recipient addresses and timing unless separately minimized.
- Broad cohort delivery can still expose rare groups when combined with other data.
- Local replay state cannot survive explicit data clearing by design.
- Target ownership, infrastructure, and sensitivity can change after review; registrations therefore require bounded validity and operational review.
