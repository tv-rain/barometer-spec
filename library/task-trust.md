# Task Trust and Local Policy

**Status:** Draft  
**Version:** 0.1.0

Runtime JSON values follow the shared [strict decoding contract](../data-formats/json-decoding.md) in addition to this document's schema, limits, and validation rules.

## Overview

<a id="REQ-TRUST-0002"></a>

**REQ-TRUST-0002 (retired):**

The historical overview required the host to establish task provenance. [REQ-TRUST-0040](#REQ-TRUST-0040) replaces it: Barometer verifies remote provenance itself; historical revisions remain available.

<a id="REQ-TRUST-0040"></a>

**REQ-TRUST-0040:**

Barometer accepts a task only after its provenance is established, by reviewed embedded packaging or by Barometer's verification of a signed remote task package, and the library validates it against immutable trusted local policy, registered measurement behavior, and [Registered Initial Limits](registered-limits.md).

<a id="REQ-TRUST-0003"></a>

**REQ-TRUST-0003:**

Task fields are untrusted input. A task cannot authenticate itself, authorize its targets, declare itself safe, update local policy, or establish that its identifier is non-user-specific.

This contract does not require one scheduler, backend, or TLS profile. It defines the single signed package format Barometer verifies for remote origin and the behavior the library must enforce.

## Accepted Task Origins

Version `0.1.0` supports two origins:

<a id="REQ-TRUST-0004"></a>

**REQ-TRUST-0004 (retired):**

The historical origins table trusted a `remote` task when the host authenticated the issuer and verified integrity. [REQ-TRUST-0041](#REQ-TRUST-0041) replaces it; historical revisions remain available.

<a id="REQ-TRUST-0041"></a>

**REQ-TRUST-0041:**

| Origin | Trust requirement |
|---|---|
| `embedded` | The exact task is packaged with a reviewed host deployment and covered by that deployment's release review. |
| `remote` | The task is delivered inside a [signed remote task package](#signed-remote-task-packages) that Barometer verifies against a trusted issuer key in trusted local policy. |

<a id="REQ-TRUST-0005"></a>

**REQ-TRUST-0005 (retired):**

The historical text allowed a host-selected remote mechanism, such as an authenticated channel. [REQ-TRUST-0042](#REQ-TRUST-0042) replaces it; historical revisions remain available.

<a id="REQ-TRUST-0042"></a>

**REQ-TRUST-0042:**

For `remote` origin the host is a transport. It passes the exact received signed package bytes to Barometer and does not perform or assert remote authentication. Host-performed verification, an authenticated channel reported by the host, and transport security between the issuer and the host establish nothing for admission.

<a id="REQ-TRUST-0001"></a>

**REQ-TRUST-0001 (retired):**

The historical text referred to host authentication and integrity verification. [REQ-TRUST-0043](#REQ-TRUST-0043) replaces it; historical revisions remain available.

<a id="REQ-TRUST-0043"></a>

**REQ-TRUST-0043:**

Barometer must not accept a remote task when signed package verification fails or cannot be performed, or when trusted local policy, trusted time needed for validity, or source context is unavailable.

## Trusted Source Context

<a id="REQ-TRUST-0006"></a>

**REQ-TRUST-0006 (retired):**

The historical text had the host supply every source-context property. [REQ-TRUST-0044](#REQ-TRUST-0044) replaces it together with REQ-TRUST-0007; historical revisions remain available.

<a id="REQ-TRUST-0007"></a>

**REQ-TRUST-0007 (retired):**

The historical source-context table included a host-asserted `authenticated` property and host-supplied remote `issuer_id` and `issued_at`. [REQ-TRUST-0044](#REQ-TRUST-0044) replaces it; historical revisions remain available.

<a id="REQ-TRUST-0044"></a>

**REQ-TRUST-0044:**

Admission uses the following source context, kept separate from serialized task fields. The host supplies `origin` and `policy_generation` through an internal initialization or admission boundary. For `embedded` origin the host also supplies `issuer_id`. For `remote` origin, `issuer_id` and `issued_at` are taken only from a verified signed package; a host-supplied value for either is not accepted.

| Property | Required | Constraints | Meaning |
|---|:---:|---|---|
| `origin` | Yes | `embedded` or `remote` | How provenance was established. |
| `issuer_id` | Yes | 1–64 lowercase ASCII letters, digits, `.`, `_`, or `-`; deployment-scoped and non-user-specific | Stable policy principal authorized to submit the task. |
| `policy_generation` | Yes | Positive monotonically increasing integer | Trusted local policy generation used for admission. |
| `issued_at` | Conditional | Required for `remote`, from the verified package; absent for `embedded`; no more than 300 seconds after the acceptance time | Authenticated issuance time used to bound task validity. |

<a id="REQ-TRUST-0008"></a>

**REQ-TRUST-0008:**

These properties are not task labels, do not appear in measurement traffic, and are not copied to Measurement Results. A task, server response, collector, target, or proxy cannot supply or override them through the public task object.

<a id="REQ-TRUST-0009"></a>

**REQ-TRUST-0009 (retired):**

The historical binding-boundary text assumed host-supplied authentication context. [REQ-TRUST-0045](#REQ-TRUST-0045) replaces it; historical revisions remain available.

<a id="REQ-TRUST-0045"></a>

**REQ-TRUST-0045:**

The concrete Go, native, or Flutter API may represent source context and signed packages differently, but it must preserve the same trust boundary. No binding accepts a verification key, a signature verdict, or an authentication flag for a task, and Flutter applications must not be asked to provide raw verification keys or mark task data authenticated. Trusted issuer keys enter Barometer only as part of the trusted local policy loaded at initialization.

## Signed Remote Task Packages

<a id="REQ-TRUST-0048"></a>

**REQ-TRUST-0048:**

A signed remote task package is one JSON object decoded under the [strict decoding contract](../data-formats/json-decoding.md). It has exactly the following members, all required, and rejects unknown members:

| Member | Type | Constraints |
|---|---|---|
| `issuer_id` | string | 1–64 lowercase ASCII letters, digits, `.`, `_`, or `-`. |
| `key_id` | string | 1–64 lowercase ASCII letters, digits, `.`, `_`, or `-`. |
| `issued_at` | string | Exactly `YYYY-MM-DDTHH:MM:SSZ`: a valid UTC calendar date and time with whole seconds and the `Z` suffix; no fraction, numeric offset, lowercase letter, or leap second `60`. |
| `task` | string | The exact task bytes, encoded as base64url without padding (RFC 4648 section 5). Only canonical encoding is accepted: no padding, whitespace, or nonzero unused trailing bits. Decodes to at least one byte. |
| `signature` | string | The Ed25519 signature, encoded as canonical base64url without padding. Decodes to exactly 64 bytes. |

The package carries no algorithm, version, or other selector. The decoded `task` bytes are the exact serialized task presented to the rest of admission.

<a id="REQ-TRUST-0049"></a>

**REQ-TRUST-0049:**

The signature is pure Ed25519 as defined by RFC 8032 over the message `M`, where `LP(x)` is the length of `x` in bytes as a 4-byte unsigned big-endian integer followed by the bytes of `x`:

```text
M = LP("barometer-signed-task-v1")
 || LP(key_id) || LP(issuer_id) || LP(issued_at) || LP(task bytes)
```

`key_id`, `issuer_id`, and `issued_at` contribute the ASCII bytes of their decoded string values, and `task bytes` are the decoded `task` bytes. Version `0.1.0` defines no other signature algorithm, context string, or message construction, and no package can select one.

<a id="REQ-TRUST-0050"></a>

**REQ-TRUST-0050:**

Signature verification is cofactorless Ed25519 verification under RFC 8032 and rejects a signature when:

- the scalar `S` is not less than the group order;
- the encoding of `R` is not canonical;
- the equation `[S]B = R + [k]A` does not hold, where `k` is computed from `R`, the public key encoding `A`, and `M` as defined by RFC 8032.

These rules are set so that conforming implementations accept the same signatures; an implementation whose Ed25519 library verifies differently must add the missing checks.

<a id="REQ-TRUST-0051"></a>

**REQ-TRUST-0051:**

Each trusted issuer key in trusted local policy contains:

| Property | Constraints |
|---|---|
| `key_id` | 1–64 lowercase ASCII letters, digits, `.`, `_`, or `-`; unique across the policy. |
| `issuer_id` | Exactly one issuer that the same policy authorizes. |
| `public_key` | 32-byte Ed25519 public key in canonical encoding that decodes to a curve point not of small order. |
| `not_before` | UTC time in the same fixed format as package `issued_at`. |
| `not_after` | UTC time in the same format, later than `not_before`; the period from `not_before` to `not_after` does not exceed the registered maximum key validity. |

Policy validation enforces these constraints and the registered key-count limits. A policy with an invalid key record fails complete validation and is not activated under [REQ-TRUST-0030](#REQ-TRUST-0030) and [REQ-TRUST-0031](#REQ-TRUST-0031). The concrete policy representation is implementation-defined. Remote tasks, signed packages, collector responses, and other delivered content cannot add, replace, or extend trusted keys.

<a id="REQ-TRUST-0052"></a>

**REQ-TRUST-0052:**

At step 2 of [REQ-TRUST-0046](#REQ-TRUST-0046), Barometer verifies a remote package by the following checks in order. A rejected package receives the class of the first failing check:

| Order | Check | Class on failure |
|---|---|---|
| 1 | The package does not exceed the registered signed-package byte limit; reading stops when the limit is exceeded. | `task_limit_exceeded` |
| 2 | Trusted local policy is available. | `task_policy_unavailable` |
| 3 | The package decodes under REQ-TRUST-0048 and every member meets its constraints. | `task_source_unauthenticated` |
| 4 | `key_id` names a trusted key in the active policy. | `task_source_unauthenticated` |
| 5 | That key's `issuer_id` equals the package `issuer_id`. | `task_source_unauthenticated` |
| 6 | Trusted time is available; this reading is the acceptance time. | `task_trust_unavailable` |
| 7 | Both the acceptance time and `issued_at` are no earlier than the key's `not_before` and no later than its `not_after`. | `task_source_unauthenticated` |
| 8 | `issued_at` is no more than 300 seconds after the acceptance time. | `task_source_unauthenticated` |
| 9 | The signature verifies over `M` with the key under REQ-TRUST-0049 and REQ-TRUST-0050. | `task_source_unauthenticated` |

The task bytes are not parsed or evaluated before check 9 succeeds. The error does not indicate which check failed beyond its class and does not include the package, task, key identifier, key, signature, or issuer, consistent with [REQ-TRUST-0035](#REQ-TRUST-0035).

<a id="REQ-TRUST-0053"></a>

**REQ-TRUST-0053:**

After admission, Barometer does not retain the signed package, its signature, or its key identifier, whether the task is accepted or rejected. The accepted task bytes and the replay record of [REQ-TRUST-0021](#REQ-TRUST-0021) to [REQ-TRUST-0023](#REQ-TRUST-0023) remain subject to their own requirements.

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

**REQ-TRUST-0017 (retired):**

The historical procedure received host-supplied remote source context and required host-performed remote authentication at steps 1 to 3. [REQ-TRUST-0046](#REQ-TRUST-0046) replaces it; steps 4 to 11 are unchanged in substance. Historical revisions remain available.

<a id="REQ-TRUST-0046"></a>

**REQ-TRUST-0046:**

Barometer performs the following steps before a task is scheduled:

1. Receive the exact presented bytes and trusted source context: for `embedded` origin, the exact serialized task; for `remote` origin, the exact signed remote task package.
2. For `remote` origin, verify the signed package under [REQ-TRUST-0052](#REQ-TRUST-0052); for `embedded` origin, require reviewed embedded origin.
3. For `remote` origin, take `issuer_id` and the authenticated `issued_at` from the verified package. Parse the task bytes within the registered task byte limit.
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

<a id="REQ-TRUST-0054"></a>

**REQ-TRUST-0054:**

Trusted issuer keys, issuers, and target registrations are added, rotated, or removed only by a new reviewed local policy with a strictly greater `policy_generation`, shipped with an application release and activated under [REQ-TRUST-0029](#REQ-TRUST-0029) to [REQ-TRUST-0031](#REQ-TRUST-0031). When a replacement policy removes a key or issuer, no new task is admitted under it, and item 4 of REQ-TRUST-0030 applies to queued and running tasks that the new policy no longer permits. A task admitted while its signing key was trusted and valid is not re-verified when that key's validity period later ends; its own expiry still bounds it. Version `0.1.0` has no other key revocation or key update channel.

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

**REQ-TRUST-0037 (retired):**

The historical condition-to-class table ordered steps by REQ-TRUST-0017 and placed the remote `issued_at` check at step 3. [REQ-TRUST-0047](#REQ-TRUST-0047) replaces it; historical revisions remain available.

<a id="REQ-TRUST-0047"></a>

**REQ-TRUST-0047:**

A rejected task receives exactly one class: the class of the first step, in [REQ-TRUST-0046](#REQ-TRUST-0046) order, that fails. Where another requirement names the class for a condition, that class applies. The following conditions use the listed class:

| Step | Condition | Class |
|---|---|---|
| 1 | The exact presented bytes are not bound to the supplied trusted source context, or that binding is missing or expired. | `task_source_unauthenticated` |
| 2 | A remote signed package fails a verification check. | The class of the first failing check in [REQ-TRUST-0052](#REQ-TRUST-0052) |
| 3 | Trusted time needed for validity is unavailable. | `task_trust_unavailable` |
| 4 | The `test_id` and `test_version` pair is not registered by the implementation (REQ-TRUST-0036). | `task_unsupported` |
| 5 | `task_id` exceeds 128 bytes. | `task_limit_exceeded` |
| 6 | A risk factor type is rejected as unsupported, or a valid field requires a capability the implementation does not provide (REQ-TRUST-0036). | `task_unsupported` |
| 7 | The source context `policy_generation` is greater than the active policy generation. | `task_policy_unavailable` |
| 8 | A direct or proxy path is not permitted by issuer authority or local policy. | `task_issuer_not_authorized` |
| 8 | A direct or proxy path is not permitted by the matched target registration. | `target_not_registered` |
| 9 | Effective risk exceeds a local-policy bound, or is `unknown` without an explicit reviewed local policy permitting it. | `task_issuer_not_authorized` |

<a id="REQ-TRUST-0039"></a>

**REQ-TRUST-0039:**

At step 8 of [REQ-TRUST-0046](#REQ-TRUST-0046), a task with `network_path: proxy` whose test, input or options are not compatible with HTTP CONNECT under [REQ-PROXY-0026](proxy.md#REQ-PROXY-0026), including a `NET-05` profile with any incompatible step, is rejected with `task_schema_invalid`. Within step 8, proxy compatibility is evaluated after input and options and before path authority and target registration. A combination that REQ-PROXY-0026 permits but the implementation does not provide through the proxy is rejected with `task_unsupported` under [REQ-TRUST-0036](#REQ-TRUST-0036).

## Residual Risks

- A compromised host, admitted issuer, operating system, or policy package can misuse authority available to it.
- A valid signature establishes which trusted issuer key signed the package, not that a task is safe; local policy remains mandatory.
- A compromised issuer signing key remains usable until its validity period ends or until installations update to a policy that removes it. Its reach stays bounded by issuer authority, local policy, registered targets and limits, task expiry, and replay handling.
- Key validity depends on trusted time. A wrong or manipulated device clock can make an expired key appear valid or a valid key appear expired.
- A signed package is attributable to its issuer. Barometer does not retain it after admission, but a host or delivery infrastructure that retains received packages can reveal that a device received a measurement task.
- Delivery infrastructure can observe recipient addresses and timing unless separately minimized.
- Broad cohort delivery can still expose rare groups when combined with other data.
- Local replay state cannot survive explicit data clearing by design.
- Target ownership, infrastructure, and sensitivity can change after review; registrations therefore require bounded validity and operational review.
