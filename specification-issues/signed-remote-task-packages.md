# Proposal: Library-Verified Signed Remote Task Packages

**Disposition:** Closed: accepted wording merged at `e97502747c917a16bc2b71337535ff972bbd7d64`, adopted in Go by DEV-612 and reviewed by the project maintainer in DEV-615; binding and host adoption not yet available
**Date:** October 20, 2026
**Related task:** [DEV-610 — Specify library-verified signed remote tasks in the public task-trust contract](https://app.clickup.com/t/124kk1zcexz)

This record asks public maintainers to replace host-asserted authentication for `remote` task origin with a signed task package that Barometer verifies itself, as adopted by project coordination decision 0011 (DEV-609). That decision is recorded in a non-public coordination repository; its content needed for public review is summarized under [Finding and Reproduction](#finding-and-reproduction). It proposes the package encoding, the signed-message construction, trusted issuer keys in local policy, their numeric limits, the position of verification in admission, and the admission class of each verification failure. It does not change embedded-origin delivery. Opening this record did not accept its proposal; the [maintainer disposition](#maintainer-disposition--october-20-2026) below did. Sections before it are the proposal as reviewed in [barometer-spec#17](https://github.com/tv-rain/barometer-spec/pull/17). The accepted wording is included in the same public change as this disposition. Acceptance does not authorize remote task delivery, which remains gated outside controlled development.

## Identity and Ownership

- Local finding: none. The change follows from coordination decision 0011 (DEV-609) and the remote-delivery gate (DEV-595), not from an implementation finding. The Go delivery-record seam and its `RemoteVerifier`, described in the Go [admission design](https://github.com/tv-rain/barometer-go/blob/9b1c44632ecb028931028a3d90afcd77fbae45c7/docs/admission.md#delivery-record-seam), has no production implementation.
- Public identity: this Markdown record, once reviewed through a public PR. Responsible maintainer: the project owner, Lev.
- Reporter: the specification agent under the task owner's instruction. Public maintainers own disposition and wording. Internal review alignment is DEV-611 and Go adoption is DEV-612 in the Admission and local policy sub-epic.
- Duplicates: none found. [Admission Error Classes](admission-error-classes.md) assigned classes to the existing source-binding conditions of steps 1 and 3; this record replaces those conditions for `remote` origin.

## Affected Baselines and Requirements

- Public Draft `0.1.0` at immutable revision [`59b192d498bf011e331928d192702e1205a89f35`](https://github.com/tv-rain/barometer-spec/tree/59b192d498bf011e331928d192702e1205a89f35).
- Requirements whose obligations change materially, all in `library/task-trust.md` at that revision:
  - [REQ-TRUST-0001](https://github.com/tv-rain/barometer-spec/blob/59b192d498bf011e331928d192702e1205a89f35/library/task-trust.md#REQ-TRUST-0001): remote acceptance conditions refer to host authentication and integrity verification.
  - [REQ-TRUST-0002](https://github.com/tv-rain/barometer-spec/blob/59b192d498bf011e331928d192702e1205a89f35/library/task-trust.md#REQ-TRUST-0002): "after the host establishes its provenance".
  - [REQ-TRUST-0004](https://github.com/tv-rain/barometer-spec/blob/59b192d498bf011e331928d192702e1205a89f35/library/task-trust.md#REQ-TRUST-0004): the `remote` origin is trusted when "the host authenticates the issuer and verifies task integrity".
  - [REQ-TRUST-0005](https://github.com/tv-rain/barometer-spec/blob/59b192d498bf011e331928d192702e1205a89f35/library/task-trust.md#REQ-TRUST-0005): an authenticated channel or a signed package as host-selectable mechanisms.
  - [REQ-TRUST-0006](https://github.com/tv-rain/barometer-spec/blob/59b192d498bf011e331928d192702e1205a89f35/library/task-trust.md#REQ-TRUST-0006) and [REQ-TRUST-0007](https://github.com/tv-rain/barometer-spec/blob/59b192d498bf011e331928d192702e1205a89f35/library/task-trust.md#REQ-TRUST-0007): the host supplies every source-context property, including `authenticated` and remote `issuer_id` and `issued_at`.
  - [REQ-TRUST-0009](https://github.com/tv-rain/barometer-spec/blob/59b192d498bf011e331928d192702e1205a89f35/library/task-trust.md#REQ-TRUST-0009): binding boundary for source context.
  - [REQ-TRUST-0017](https://github.com/tv-rain/barometer-spec/blob/59b192d498bf011e331928d192702e1205a89f35/library/task-trust.md#REQ-TRUST-0017): steps 1 to 3 receive host source context and "require valid remote authentication".
  - [REQ-TRUST-0037](https://github.com/tv-rain/barometer-spec/blob/59b192d498bf011e331928d192702e1205a89f35/library/task-trust.md#REQ-TRUST-0037): the step 1 and step 3 rows for source binding and remote `issued_at`.
- Requirements read with the change and proposed to remain unchanged: [REQ-TRUST-0003](https://github.com/tv-rain/barometer-spec/blob/59b192d498bf011e331928d192702e1205a89f35/library/task-trust.md#REQ-TRUST-0003) (the signature is outside the task bytes, so a task still cannot authenticate itself), REQ-TRUST-0024, REQ-TRUST-0029 to REQ-TRUST-0032, REQ-TRUST-0034, REQ-TRUST-0035, [REQ-LIMIT-0004](https://github.com/tv-rain/barometer-spec/blob/59b192d498bf011e331928d192702e1205a89f35/library/registered-limits.md#REQ-LIMIT-0004), [REQ-LIMIT-0009](https://github.com/tv-rain/barometer-spec/blob/59b192d498bf011e331928d192702e1205a89f35/library/registered-limits.md#REQ-LIMIT-0009) and [REQ-LIMIT-0010](https://github.com/tv-rain/barometer-spec/blob/59b192d498bf011e331928d192702e1205a89f35/library/registered-limits.md#REQ-LIMIT-0010).
- Unallocated text affected: the `library/task-trust.md` overview sentence that the contract does not require one "signature container", its Residual Risks section, and in [`threat-model.md`](https://github.com/tv-rain/barometer-spec/blob/59b192d498bf011e331928d192702e1205a89f35/threat-model.md) the system diagram, the host-authentication assumption, the "Unauthorized or modified task" mitigation row, abuse cases, residual exposure and review triggers.
- Implementation: `tv-rain/barometer-go` at `9b1c44632ecb028931028a3d90afcd77fbae45c7`. Remote admission accepts a delivery record installed by a host-side `RemoteVerifier`; the only verifier is a synthetic test HMAC envelope. No signed-package parsing, trusted-key model or Ed25519 verification exists. No binding, native or platform behavior is implemented or validated.

## Finding and Reproduction

The current contract lets each host choose and perform remote authentication and then pass `authenticated: true` with a host-supplied `issuer_id` and `issued_at`. Decision 0011 records why this is not acceptable for an embedded library: the trust boundary differs per host and cannot be covered by Barometer conformance tests, the library accepts an assertion it cannot check, and issuer binding, rotation and revocation have no common behavior. It decides that Barometer verifies an Ed25519-signed package against trusted keys in local policy shipped with the application release, and leaves the encoding, construction, bounds, verification order and classes to this public change. The decision's public-relevant reasons for its other choices are:

- A fast revocation channel is deferred because it requires either a reachable service, which conflicts with backend-independent deployment, or a second signed update path needing its own design and safety review.
- Ed25519 is selected for its small keys and signatures, deterministic signing, and availability in the Go standard library without a new dependency.
- A single fixed algorithm avoids negotiation and downgrade paths.

Evidence: document review only, at the baselines above. No synthetic, runtime or device reproduction is claimed.

Affected work that must stop: production remote admission and any production `RemoteVerifier`; remote delivery stays gated by DEV-595. Interim handling: the existing contract remains authoritative for the synthetic test verifier only; no host should implement host-asserted remote authentication for deployment. Unaffected: embedded-origin admission and admission steps 4 to 11.

## Impact and Required Reviews

- Safety/privacy:
  - Barometer makes no new network contact; the host still delivers the package over its own channel. The package adds `issuer_id`, `key_id`, `issued_at` and a signature, all deployment-scoped and non-user-specific.
  - A signed package is attributable to its issuer. A package retained on a device could show that a reviewed measurement issuer delivered a task to it. The proposal requires Barometer not to retain the package or signature after admission; the replay record keeps only the SHA-256 digest of the exact task bytes (REQ-TRUST-0022). Host retention of received packages is outside Barometer control and is flagged for host integration review.
  - A compromised signing key remains usable until its validity ends or installations update to a policy that removes it (decision 0011). Its reach stays bounded by local policy, registered targets, registered limits, the 7-day task lifetime, replay handling, and the rule that remote tasks can only narrow authority.
  - Key validity depends on trusted time; a wrong or manipulated device clock can make an expired key appear valid. Unavailable trusted time continues to fail closed.
  - Admission errors stay code-only (REQ-TRUST-0035). All verification failures share one class so that errors do not reveal which keys or issuers a policy trusts.
  - Resource bounds: the package has a byte limit checked before decoding, and key lookup and validity checks precede the signature computation.
- Measurement/interpretation: none. A rejected package is an admission error, not a Measurement Result and not evidence of censorship (REQ-TRUST-0033).
- Compatibility: the host boundary for `remote` origin changes from source-context assertion to opaque package bytes, and the `authenticated` source-context property is removed. Embedded origin and the public task object are unchanged. No external hosts, producers or stored packages are known; this is an assumption, not assessed deployment evidence.
- Platform policy and legal: signature verification only, with no encryption of content. Export-control and platform-policy classification of the verification code have not been assessed and remain deployment review questions; this record states no legal conclusion.
- Required reviews, none completed:
  - cryptographic review of the package encoding, signed-message construction, Ed25519 verification strictness and public-key validation;
  - safety review of the residual exposure and the maximum key validity;
  - host integration review of package retention and transport when a binding exposes remote delivery;
  - public maintainer disposition.

## Alternatives and Proposed Public Resolution

Alternatives already decided by decision 0011 and not reopened here: keeping host-verified remote delivery, adding a fast revocation channel in `0.1.0`, and selecting another signature algorithm. Alternatives within this record:

1. **Package encoding.** (a, proposed) A strict JSON envelope carrying the exact task bytes in base64url. It reuses the strict decoding contract, and the signature never depends on JSON canonicalization. (b) A detached signature supplied beside raw task bytes: two values must be kept together by every host, and binding fields would need a second container. (c) A binary container such as CBOR or COSE: adds a decoder dependency and a format the rest of the specification does not use. (d) Signing the parsed task in a canonical JSON form: canonicalization rules are a known source of verification divergence.
2. **Signed message.** (a, proposed) A length-prefixed concatenation with a fixed context string. (b) Signing the envelope bytes: binds whitespace and member order and still needs an exclusion rule for the signature field. (c) Ed25519ctx context parameter: not available in every native library, while an in-message context gives the same separation with pure Ed25519.
3. **Verification failure classes.** (a, proposed) `task_source_unauthenticated` for every malformed-package, key and signature failure; `task_limit_exceeded` for an oversized package; `task_trust_unavailable` for unavailable trusted time; `task_policy_unavailable` when trusted local policy is unavailable. (b) A distinct class per failure: helps debugging but lets a party presenting packages learn which key identifiers and issuers a policy trusts, against REQ-TRUST-0035. (c) A new class such as `task_signature_invalid`: adds vocabulary without a host action that differs from `task_source_unauthenticated`.
4. **Numeric limits.** Proposed values below. A shorter maximum key validity forces more frequent releases and can stop remote tasks on slowly updating installations; a longer one extends the use of a compromised key and of abandoned installations. 365 days permits annual rotation, with up to four keys per issuer allowing overlapping old and new keys during a release transition.

Retaining the current text leaves remote admission dependent on per-host mechanisms that decision 0011 no longer accepts.

### Proposed Wording Summary

Subject to maintainer review; the exact normative text is prepared with the disposition.

**Origins and source context.**

- `embedded`: unchanged.
- `remote`: the host passes the exact received signed task package bytes and does not perform or assert remote authentication. Transport security between issuer and host establishes nothing for admission.
- Source context:
  - The `authenticated` property is removed.
  - For `remote`, the host supplies only `origin` and the active `policy_generation`.
  - `issuer_id` and `issued_at` are taken only from a verified package.
  - Host-supplied values for them are not accepted.
- Bindings, including Flutter, never accept a verification key, a signature verdict or an authentication flag. Trusted keys enter only through the trusted local policy loaded at initialization.

**Signed task package.** One JSON object under the [strict decoding contract](../data-formats/json-decoding.md), with exactly these members, all required:

| Member | Constraints |
|---|---|
| `issuer_id` | Same syntax as source-context `issuer_id`: 1–64 lowercase ASCII letters, digits, `.`, `_`, or `-`. |
| `key_id` | 1–64 lowercase ASCII letters, digits, `.`, `_`, or `-`. |
| `issued_at` | Exactly `YYYY-MM-DDTHH:MM:SSZ`: a valid UTC calendar date and time with whole seconds, `Z` suffix, no fraction, offset or leap second. |
| `task` | Exact task bytes, encoded as unpadded base64url (RFC 4648 section 5); canonical encoding only, no whitespace; decodes to at least one byte. |
| `signature` | Ed25519 signature, encoded as unpadded canonical base64url; decodes to exactly 64 bytes. |

**Signed message.** With `LP(x)` meaning the 4-byte unsigned big-endian length of `x` followed by `x`:

```text
M = LP("barometer-signed-task-v1")
 || LP(key_id) || LP(issuer_id) || LP(issued_at) || LP(task bytes)
```

- String members contribute their decoded ASCII bytes.
- `task bytes` are the decoded `task` bytes.
- The signature is pure Ed25519 (RFC 8032) over `M`.
- There is no algorithm member, negotiation or alternative algorithm.
- A signature whose `S` value is not less than the group order is rejected.
- Whether to require further verification strictness, such as canonical `R` encoding and cofactorless versus cofactored verification so that implementations agree on edge-case signatures, is an open question for the cryptographic review. The accepted wording must state one rule.

**Trusted issuer keys.** Each key record in trusted local policy contains:

- `key_id`, unique across the policy;
- exactly one `issuer_id`, which the policy must authorize;
- a 32-byte Ed25519 public key that decodes to a valid point that is not of small order;
- `not_before` and `not_after` in the same fixed UTC format, with `not_before` earlier than `not_after` and a period no longer than the registered maximum.

Further rules:

- A policy with an invalid key record fails complete validation and is not activated (REQ-TRUST-0030, REQ-TRUST-0031).
- Remote tasks, collector responses and other delivered content cannot add, replace or extend keys (REQ-TRUST-0032).
- The concrete policy representation remains implementation-defined, as for other policy content.

**Admission steps.** REQ-TRUST-0017 steps 1 to 3 become:

1. Receive the exact presented bytes and trusted source context. For `embedded`, these are the reviewed packaged task bytes. For `remote`, they are the exact signed package bytes.
2. For `remote`, verify the signed package in the order below. For `embedded`, require reviewed embedded origin.
3. For `remote`, take `issuer_id` and the authenticated `issued_at` from the verified package. Parse the task bytes within the registered task byte limit.

Steps 4 to 11 are unchanged.

**Verification order and classes.** A rejected package receives the class of the first failing check:

| Order | Check | Class on failure |
|---|---|---|
| 1 | Package does not exceed the registered package byte limit; reading stops when it is exceeded. | `task_limit_exceeded` |
| 2 | Trusted local policy is available. | `task_policy_unavailable` |
| 3 | Package decodes strictly and every member meets its constraints. | `task_source_unauthenticated` |
| 4 | `key_id` names a trusted key. | `task_source_unauthenticated` |
| 5 | That key belongs to the package `issuer_id`. | `task_source_unauthenticated` |
| 6 | Trusted time is available; its reading is the acceptance time. | `task_trust_unavailable` |
| 7 | Both the acceptance time and `issued_at` fall within `[not_before, not_after]` of the key. | `task_source_unauthenticated` |
| 8 | `issued_at` is no more than 300 seconds after the acceptance time (REQ-LIMIT-0010). | `task_source_unauthenticated` |
| 9 | The signature verifies over `M` with the key. | `task_source_unauthenticated` |

The task is not parsed or evaluated before check 9 succeeds. The decoded task byte limit is then applied at step 3 with `task_limit_exceeded` (REQ-LIMIT-0004). Errors do not identify which check failed beyond the class, and do not include the package, key identifier, key, signature or issuer (REQ-TRUST-0035). The embedded-origin rows of REQ-TRUST-0037 are retained in the replacement table.

**Retention.** After admission, Barometer does not retain the package, signature or key identifier. The replay record remains as defined by REQ-TRUST-0021 to REQ-TRUST-0023.

**Rotation and revocation.** Keys, issuers and target registrations are added, rotated or removed only by a new reviewed local policy with a strictly greater `policy_generation`, shipped with an application release (REQ-TRUST-0029 to REQ-TRUST-0031). When a replacement policy removes a key or issuer, new admissions under it stop, and REQ-TRUST-0030 item 4 applies to queued and running tasks the new policy no longer permits. A task admitted under a key that remains trusted is not re-verified when the key's validity period later ends; its own `not_after` still bounds it. Version `0.1.0` has no other revocation channel.

**Registered limits.** A new table in `library/registered-limits.md`:

| Item | Maximum |
|---|---:|
| Complete signed task package | 98,304 bytes |
| `key_id` | 64 ASCII bytes |
| Trusted keys per issuer | 4 |
| Trusted keys in one local policy | 32 |
| Trusted key validity period (`not_after` − `not_before`) | 31,536,000 seconds (365 days) |

The package maximum fits a 65,536-byte task, which is 87,382 base64url characters, plus the other members.

**Threat model.**

- The diagram and the host-authentication assumption describe library-verified signed packages against keys in trusted local policy.
- The "Unauthorized or modified task" row cites signature verification and issuer-bound keys. Its residual exposure adds a compromised signing key, which stays usable until key expiry or policy update.
- New abuse cases:
  - a forged or altered package;
  - a package signed with another issuer's key;
  - a package signed with an expired or not-yet-valid key;
  - a package with `issued_at` moved within the key's validity;
  - an oversized or malformed package;
  - a host-asserted authentication flag.
- Residual exposure adds:
  - clock-dependent key validity;
  - issuer attribution of retained packages;
  - verification divergence across Ed25519 implementations, pending cryptographic review.
- Review triggers add a new signing key algorithm, a key validity period above the registered maximum, and any revocation or key-update channel outside an application release.

### Requirement-ID Lifecycle and Version

Proposed, reconciled against the target branch before merge:

| Retired | Successor | Topic |
|---|---|---|
| REQ-TRUST-0002 | REQ-TRUST-0040 | Overview: provenance from reviewed embedded packaging or library-verified signature |
| REQ-TRUST-0004 | REQ-TRUST-0041 | Origins table |
| REQ-TRUST-0005 | REQ-TRUST-0042 | Host as transport; channel security establishes nothing |
| REQ-TRUST-0001 | REQ-TRUST-0043 | Remote acceptance fails closed without verification, trusted keys, trusted time or source context |
| REQ-TRUST-0006, REQ-TRUST-0007 | REQ-TRUST-0044 | Source context without `authenticated`; remote issuer and time from the package |
| REQ-TRUST-0009 | REQ-TRUST-0045 | Binding boundary |
| REQ-TRUST-0017 | REQ-TRUST-0046 | Admission procedure |
| REQ-TRUST-0037 | REQ-TRUST-0047 | First-failing-step class table |

New allocations:

- REQ-TRUST-0048: package members.
- REQ-TRUST-0049: signed message and algorithm.
- REQ-TRUST-0050: Ed25519 verification strictness.
- REQ-TRUST-0051: trusted key record and policy validation.
- REQ-TRUST-0052: verification order and classes.
- REQ-TRUST-0053: no retention of package material.
- REQ-TRUST-0054: rotation and revocation by policy generation.
- REQ-LIMIT-0032: signed-package and trusted-key limits.

REQ-TRUST-0039 and other identifiers remain active. Retired identifiers keep their anchors as historical records under the [requirement convention](../requirements/README.md).

Proposed version decision: retain Draft `0.1.0`. Nothing has been released, and the change replaces an unselected host mechanism. This does not assert that any existing host or producer remains compatible.

### Expected Cases

These remain proposals until the wording is accepted and merged.

Accepted and passing cases:

- A package signed with a trusted key for its issuer, within the key's validity, with `issued_at` at most 300 seconds ahead, is accepted at step 2. Admission then proceeds with the package `issuer_id` and `issued_at` as source context.

Cases rejected with `task_source_unauthenticated`:

- The same package with:
  - one task byte changed;
  - `issuer_id` changed;
  - `issued_at` changed by one second;
  - `key_id` changed to another trusted key of the same issuer.
- A key belonging to another issuer.
- An unknown `key_id`.
- An acceptance time one second after `not_after`.
- An `issued_at` one second before `not_before`.
- `issued_at` 301 seconds ahead.
- A signature with `S` not less than the group order.
- A padded or non-canonical base64url member.
- An unknown or duplicate member.
- A fractional-second `issued_at`.

Cases with other classes:

- A package one byte over the limit is rejected with `task_limit_exceeded` before decoding.
- Unavailable trusted time yields `task_trust_unavailable` for a package with a trusted key.

Policy validation:

- A policy with a key whose validity exceeds 365 days fails validation.
- A policy with a fifth key for one issuer fails validation.
- A policy with a small-order public key fails validation.

Boundary cases:

- A host-supplied `authenticated` flag or `issuer_id` for remote origin has no effect on admission.
- An embedded task is admitted as before.
- No case leaves the package or signature in retained state.

## Ordering and Public Disposition

- Coordination decision: project coordination decision 0011 (DEV-609), accepted October 20, 2026, and summarized in this record.
- Order: maintainer disposition of this record; then one public change with the accepted wording, catalog allocations and retirements, the registered limits, the threat-model updates and this record's disposition. Then internal task-trust review alignment (DEV-611), then Go adoption (DEV-612), which must update `requirement-ref` comments citing retired identifiers. Bindings and host integration follow. Remote delivery remains gated by DEV-595 until that sequence and the required reviews are complete.
- Public review/PR, maintainer disposition, rationale and date: proposal reviewed in [barometer-spec#17](https://github.com/tv-rain/barometer-spec/pull/17); see [Maintainer Disposition](#maintainer-disposition--october-20-2026).

## Adoption and Closure Evidence

- Closure requires:
  - the maintainer disposition;
  - the merged wording revision with its requirement allocations, retirements and version decision;
  - internal review alignment;
  - Go adoption evidence: package decoding, trusted-key validation, verification-order and class tests, and traceability citing them;
  - completed cryptographic and safety reviews, or their recorded status as gates that block field use.
- Binding and host adoption are outside the current tasks and are assessed when those components exist.

## Maintainer Disposition — October 20, 2026

The project owner and public maintainer, Lev, accepted the proposal on October 20, 2026, in the DEV-610 task review, including alternatives (a) for package encoding, signed message and verification failure classes, and the proposed numeric limits.

- **Package, message and algorithm:** accepted as proposed. [REQ-TRUST-0048](../library/task-trust.md#REQ-TRUST-0048) defines the package members and [REQ-TRUST-0049](../library/task-trust.md#REQ-TRUST-0049) the signed message and the single algorithm, pure Ed25519.
- **Verification strictness:** the open question is resolved. Verification is cofactorless Ed25519 under RFC 8032; it rejects `S` not less than the group order and a non-canonical `R` encoding ([REQ-TRUST-0050](../library/task-trust.md#REQ-TRUST-0050)). A trusted public key must be canonically encoded and not of small order, checked at policy validation ([REQ-TRUST-0051](../library/task-trust.md#REQ-TRUST-0051)). This rule is provisional until the cryptographic review below; a change after review requires a new public change.
- **Trusted keys:** accepted as proposed, with the record properties named `key_id`, `issuer_id`, `public_key`, `not_before` and `not_after` ([REQ-TRUST-0051](../library/task-trust.md#REQ-TRUST-0051)).
- **Admission:** [REQ-TRUST-0046](../library/task-trust.md#REQ-TRUST-0046) replaces steps 1 to 3; [REQ-TRUST-0052](../library/task-trust.md#REQ-TRUST-0052) sets the nine checks and their classes; [REQ-TRUST-0047](../library/task-trust.md#REQ-TRUST-0047) replaces the class table, routing step 2 failures to REQ-TRUST-0052 and removing the step 3 row for remote `issued_at`, now check 8.
- **Source context and host boundary:** [REQ-TRUST-0040](../library/task-trust.md#REQ-TRUST-0040) to [REQ-TRUST-0045](../library/task-trust.md#REQ-TRUST-0045). The `authenticated` property is removed. For `embedded` origin the host still supplies `issuer_id`.
- **Retention, rotation and revocation:** [REQ-TRUST-0053](../library/task-trust.md#REQ-TRUST-0053) and [REQ-TRUST-0054](../library/task-trust.md#REQ-TRUST-0054), as proposed.
- **Limits:** [REQ-LIMIT-0032](../library/registered-limits.md#REQ-LIMIT-0032) with the proposed values and their rationale.
- **Threat model and residual risks:** [`threat-model.md`](../threat-model.md) and the Residual Risks section of `library/task-trust.md` are updated as proposed. The overview sentence of `library/task-trust.md` no longer says that no signature container is required.
- **Requirement IDs:** REQ-TRUST-0001, REQ-TRUST-0002, REQ-TRUST-0004 to REQ-TRUST-0007, REQ-TRUST-0009, REQ-TRUST-0017 and REQ-TRUST-0037 are retired with the successors listed in the proposal; their anchors remain as historical records. REQ-TRUST-0040 to REQ-TRUST-0054 and REQ-LIMIT-0032 are new allocations in the [requirement catalog](../requirements/catalog.json). REQ-TRUST-0039 is unchanged except that its step reference now links to REQ-TRUST-0046; step 8 is unchanged. No ID is reused.
- **Version:** Draft `0.1.0` is retained. The remote host boundary changes incompatibly; no external hosts, producers or stored packages are known, which is an assumption and not assessed deployment evidence. No release or runtime support claim is made.
- **Downstream references:** references in the internal reviews and the Go repository that cite retired identifiers must be updated in their alignment and adoption tasks. Go continuous integration pins an earlier public revision and is not affected until it moves its pin.
- **Required reviews:** the cryptographic review, the safety review of the residual exposure and the maximum key validity, and the host integration review remain required and are not represented as completed. They gate field use of remote delivery.
- **Effect:** the merged immutable revision of this change becomes the accepted baseline for internal alignment (DEV-611) and Go adoption (DEV-612); it is recorded as evidence on DEV-610 after merge.

## Closure Addendum — October 21, 2026

Recorded under DEV-625. The sections above keep their wording as historical evidence, including their then-pending statements.

- **Merged revisions:** the proposal was merged on October 20, 2026 through [public PR #17](https://github.com/tv-rain/barometer-spec/pull/17) at `8008e5bd52733ba0dd21407c5ad28b102a8b759b` (head `940620006b49b8b2a1821f708c5be380952787d9`). The accepted wording, allocations, retirements, registered limits, threat-model updates and Draft `0.1.0` retention were merged the same day through [public PR #18](https://github.com/tv-rain/barometer-spec/pull/18) as immutable revision [`e97502747c917a16bc2b71337535ff972bbd7d64`](https://github.com/tv-rain/barometer-spec/tree/e97502747c917a16bc2b71337535ff972bbd7d64) (head `5d6aa88615b0cff8a5dfcd1ae5c3cc631c69c158`).
- **Internal alignment:** the internal task-trust review validation plan and open questions were aligned to `e975027` under DEV-611 (internal review repository PR #6, merged at `1f24bb665b2b6332353115db578ad484b14ea119`), citing the successors of the retired identifiers.
- **Go adoption:** DEV-612 adopted the contract in Go [PR #55](https://github.com/tv-rain/barometer-go/pull/55), merged at `33a90150b2ce0698b69c4cf90a8f1a9a0726b780`: package decoding, trusted-key validation, the ordered checks and their classes, package-only single-use remote delivery records, updated `requirement-ref` comments, and traceability citing synthetic tests, Ed25519 edge vectors and fuzz targets ([adoption record](https://github.com/tv-rain/barometer-go/blob/33a90150b2ce0698b69c4cf90a8f1a9a0726b780/docs/specification-issues.md#signed-remote-task-package-adoption)). Evidence is synthetic only.
- **Required reviews:** the cryptographic review, the safety review of the residual exposure and the maximum key validity, and the host integration review were performed by the project maintainer under DEV-615 against this repository at `4743b636f29feb1f0f8d042866d04ccda3532938` and Go at `33a90150b2ce0698b69c4cf90a8f1a9a0726b780`, and recorded in the internal task-trust review (internal review repository PR #7, merged at `4522637fc91890acae9de6b4da9bd189d9f3318e`). Each passed with no findings; none requires a change to the public wording, including the provisional verification strictness of REQ-TRUST-0050. No binding exists yet, so the host integration review covers the contract, not binding code.
- **Maintainer decision, October 21, 2026:** the DEV-615 maintainer reviews satisfy the reviews required by coordination decision 0011 and by this record, and the remote-delivery gate (DEV-595) is lifted. Independent external reviews of the same scopes (DEV-618 to DEV-621) run asynchronously in a separate process and do not gate; their results return as ordinary findings under the [specification issue workflow](README.md). Lifting the gate is not a support claim: no native, Flutter or host adoption exists (DEV-455), so no host can deliver remote packages through a binding yet. Export-control and platform-policy classification and existing deployment legal and platform-policy gates remain applicable.
- **Follow-up:** the interpretation question about REQ-TRUST-0054 raised during Go adoption is resolved by [Re-verification of Redelivered Remote Tasks After Key Expiry](key-expiry-redelivery.md) (REQ-TRUST-0055), whose Go adoption is tracked there.
- **Disposition:** closed October 21, 2026 by the public maintainer through this DEV-625 change; the evidence required under [Adoption and Closure Evidence](#adoption-and-closure-evidence) is linked above. Binding and host adoption are assessed when those components exist (DEV-455). No runtime, platform, field or release support is claimed.
