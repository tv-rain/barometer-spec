# Proposal: Re-verification of Redelivered Remote Tasks After Key Expiry

**Disposition:** Accepted wording (alternative (a)); merge and downstream adoption pending
**Date:** October 20, 2026
**Related task:** [DEV-616 — Clarify whether REQ-TRUST-0054 tasks survive policy replacement without re-verification](https://app.clickup.com/t/124kk1zcf5d)

This record asks public maintainers whether a remote task admitted while its signing key was trusted and valid stays exempt from re-verification when it is presented again after that key's validity ends, in particular after a policy replacement. It confirms the existing fail-closed reading and states it as a new requirement. It changes no admission order, error class, serialized field or limit, and makes no support claim. Opening this record did not accept its proposal; the [maintainer disposition](#maintainer-disposition--october-20-2026) below did. Sections before it are the proposal as reviewed. The accepted wording is included in the same public change as this record.

## Identity and Ownership

- Local finding: the Open Interpretation Question under [Signed Remote Task Package Adoption](https://github.com/tv-rain/barometer-go/blob/33a90150b2ce0698b69c4cf90a8f1a9a0726b780/docs/specification-issues.md#signed-remote-task-package-adoption) in the Go specification-issue record, raised October 20, 2026 under DEV-612 while adopting signed remote task packages.
- Public identity: this Markdown record, once reviewed through a public PR. Responsible maintainer: the project owner, Lev.
- Reporter: the Go implementation agent under the task owner's instruction. Public maintainers own disposition and wording. The Go implementation owner owns adoption.
- Related: [Signed remote task packages](signed-remote-task-packages.md), which introduced REQ-TRUST-0054. Duplicates: none found.

## Affected Baselines and Requirements

- Public Draft `0.1.0` at immutable revision [`e97502747c917a16bc2b71337535ff972bbd7d64`](https://github.com/tv-rain/barometer-spec/tree/e97502747c917a16bc2b71337535ff972bbd7d64).
- Requirements:
  - [REQ-TRUST-0054](https://github.com/tv-rain/barometer-spec/blob/e97502747c917a16bc2b71337535ff972bbd7d64/library/task-trust.md#REQ-TRUST-0054): a task admitted while its signing key was trusted and valid is not re-verified when that key's validity period later ends; its own expiry still bounds it.
  - [REQ-TRUST-0052](https://github.com/tv-rain/barometer-spec/blob/e97502747c917a16bc2b71337535ff972bbd7d64/library/task-trust.md#REQ-TRUST-0052): every remote package is verified at admission step 2, including key trust (check 4) and key validity at the acceptance time (check 7).
  - [REQ-TRUST-0024](https://github.com/tv-rain/barometer-spec/blob/e97502747c917a16bc2b71337535ff972bbd7d64/library/task-trust.md#REQ-TRUST-0024): an exact redelivery is idempotent, applied by replay handling at a later admission step.
  - [REQ-TRUST-0029](https://github.com/tv-rain/barometer-spec/blob/e97502747c917a16bc2b71337535ff972bbd7d64/library/task-trust.md#REQ-TRUST-0029) to [REQ-TRUST-0031](https://github.com/tv-rain/barometer-spec/blob/e97502747c917a16bc2b71337535ff972bbd7d64/library/task-trust.md#REQ-TRUST-0031): policy replacement requires library reinitialization before new-policy tasks run.
  - [REQ-TRUST-0053](https://github.com/tv-rain/barometer-spec/blob/e97502747c917a16bc2b71337535ff972bbd7d64/library/task-trust.md#REQ-TRUST-0053): the package, signature and key identifier are not retained after admission.
- Implementation: `tv-rain/barometer-go` at `33a90150b2ce0698b69c4cf90a8f1a9a0726b780`. Policy replacement invalidates every task handle and delivery reference, and tasks still permitted are redelivered. Every redelivered package is verified at its new acceptance time. No binding, native or platform behavior is implemented or validated.

## Finding and Reproduction

REQ-TRUST-0054 exempts an admitted task from re-verification when its key's validity ends, but does not say whether the exemption covers a later presentation of the same task. Two cases follow from the existing order, in which package verification precedes replay handling:

1. A task whose key validity ends between its admission and a policy replacement is rejected with `task_source_unauthenticated` when it is redelivered after the replacement, although the new policy still permits it and a replay record exists.
2. Within one generation, an exact redelivery after key expiry is rejected with `task_source_unauthenticated` while the acceptance held by the instance stays valid until the task's own expiry.

Observed behavior: barometer-go implements both cases fail-closed and records the question without resolving it by local choice. Its synthetic test advances a manual clock past key validity and asserts that the handle still resolves while a new presentation of the same package is rejected. Assumption: the exemption was meant to avoid cancelling held tasks, not to exempt new presentations. Unresolved before this disposition: whether the public text intends replacement or reinitialization to preserve the exemption.

Affected work: none is blocked; the current fail-closed behavior conforms to the existing ordered checks. Interim handling: unchanged Go behavior.

## Impact and Required Reviews

- Safety/privacy: the fail-closed reading never admits a presentation signed with a key that is expired or no longer trusted, so a compromised key is not usable beyond its validity through redelivery. Exempting redelivery would need either retention of a key identifier or package, which REQ-TRUST-0053 prohibits, or reordering replay handling before verification, which would let unauthenticated bytes reach replay lookup. No destination, traffic, retained data or identifier is added under (a).
- Availability: under (a), a task stops before its own expiry when it is no longer held and its key has expired. Issuers can re-sign identical task bytes with a currently valid key; replay identity is the digest of the task bytes, so while a replay record exists the re-signed package is an exact redelivery with unchanged expiry. After data clearing it is evaluated as new under REQ-TRUST-0025.
- Measurement/interpretation: an admission rejection is not a Measurement Result and not evidence of censorship (REQ-TRUST-0033). Fewer runs after a replacement reflect key lifecycle, not network state.
- Compatibility: no field, class, order or limit changes. Hosts that redeliver after a replacement must expect `task_source_unauthenticated` for packages whose key has expired.
- Required reviews: public maintainer disposition. The safety review of residual key exposure required by the signed-package record also covers this rule; it is not completed. No privacy, legal or platform-policy effect is identified.

## Alternatives and Proposed Public Resolution

1. **(a) Confirm the fail-closed reading and state it (proposed; accepted).** The exemption applies only to an accepted task the initialized instance still holds. Every presentation is verified at its own acceptance time. Simple, conservative, needs no retained key material.
2. (b) Exempt an exact redelivery that matches a replay record from the key-validity check when the key is still in the active policy. Keeps tasks running across replacement but requires reordering verification against replay lookup, weakens the key-validity bound, and needs cryptographic and safety review and Go changes.
3. (c) Require implementations to carry accepted tasks across policy replacement and reinitialization without redelivery. Needs a persistent admitted-task store holding task content, including targets, which is not specified and requires privacy review.

Retaining the text without disposition leaves implementations free to diverge between (a) and (b).

Proposed wording, included in this change: a new requirement, REQ-TRUST-0055, after REQ-TRUST-0054 in `library/task-trust.md`, and a Residual Risks entry for tasks that stop before their own expiry.

Proposed requirement-ID lifecycle: REQ-TRUST-0054 remains active and unchanged; REQ-TRUST-0055 is a new allocation. Proposed version decision: retain Draft `0.1.0`; the change adds no serialized field.

Expected cases: with a key valid until one hour after acceptance and a task valid for three hours, after two hours the held acceptance still resolves with its original expiry, while a new presentation of the same package is rejected with `task_source_unauthenticated`; after a policy replacement that retains the expired key, a redelivery is rejected with `task_source_unauthenticated` and writes no replay record; a package re-signed over the identical task bytes with a valid key resolves to the retained acceptance with unchanged expiry. These remain proposals until the wording is merged.

## Ordering and Public Disposition

- Coordination decision: not needed; no architecture or responsibility boundary changes.
- Order: merge this record together with the wording and catalog allocation in one public change. Then align the internal task-trust review to cite REQ-TRUST-0055. Then update the Go record to close its Open Interpretation Question by reference and add REQ-TRUST-0055 to the traceability mapping of its existing rotation case. Bindings and hosts follow.
- Maintainer disposition, rationale and date: see [Maintainer Disposition](#maintainer-disposition--october-20-2026).

## Adoption and Closure Evidence

- Closure requires: the merged wording revision with its requirement allocation; internal review alignment citing it; and the Go record closing its open question by reference, with traceability citing REQ-TRUST-0055 to existing tests.
- No Go behavior change is expected. Binding and host adoption are outside the current tasks.

## Maintainer Disposition — October 20, 2026

The project owner and public maintainer, Lev, accepted alternative (a) on October 20, 2026, in the DEV-616 task review.

- **Rule:** the exemption from re-verification in REQ-TRUST-0054 applies only to an accepted task the initialized library instance still holds. Every presentation of a remote package, including an exact redelivery and a redelivery after policy replacement, reinitialization or data clearing, is verified at its own acceptance time before replay handling.
- **Rationale:** the fail-closed reading keeps a key's validity period as a hard bound on new admissions, requires no retained key material, and matches the existing check order.
- **Wording:** accepted as proposed. [REQ-TRUST-0055](../library/task-trust.md#REQ-TRUST-0055) follows REQ-TRUST-0054 in `library/task-trust.md`, and the Residual Risks section records that such tasks can stop before their own expiry.
- **Requirement IDs:** REQ-TRUST-0055 is a new allocation recorded in the [requirement catalog](../requirements/catalog.json). REQ-TRUST-0054 remains active and unchanged; no ID is retired or reused.
- **Version:** Draft `0.1.0` is retained. No schema, field, class or limit changes, and no release or runtime support claim is made.
- **Effect:** the merged immutable revision of this change becomes the accepted baseline for internal alignment and Go adoption; it is recorded as evidence on DEV-616 after merge. The required safety review is not represented as completed.
