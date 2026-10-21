# Proposal: Admission Error Classes for Unsupported and Unmapped Rejections

**Disposition:** Accepted wording (alternative (b) for unsupported features, alternative (a) for the other mappings); merged at `d93aff93cbc17e7c065fb40d8f6e2e01a697bf35`; internal alignment merged; Go adoption in progress; safety review of the mapping pending
**Date:** October 19, 2026
**Related task:** [DEV-596 — Obtain public disposition for GO-SPEC-ISSUE-008](https://app.clickup.com/t/124kk1zcb6g)

This record asks public maintainers to decide which admission error class Barometer returns when the public text names none: for a valid task that uses a feature the implementation does not provide, and for several other rejections that REQ-TRUST-0017 orders without assigning a class. It also asks for the precedence between failing steps and for replay fail-closed handling of embedded tasks. It adds one admission error class and no serialized task field, and makes no support claim. Opening this record did not accept its proposal; the [maintainer disposition](#maintainer-disposition--october-19-2026) below did. Sections before it are the proposal as reviewed. The accepted wording is included in the same public change as this record.

## Identity and Ownership

- Local finding: `GO-SPEC-ISSUE-008` in the Go [specification-issue record](https://github.com/tv-rain/barometer-go/blob/main/docs/specification-issues.md#go-spec-issue-008-admission-error-classes-for-unsupported-and-unmapped-rejections), raised October 19, 2026 under DEV-583 while recording the Go admission design.
- Public identity: this Markdown record, once reviewed through a public PR. Responsible maintainer: the project owner, Lev.
- Reporter: the Go implementation agent under the task owner's instruction. Public maintainers own disposition and wording. The Go implementation owner owns adoption in the admission tasks of the Admission and local policy sub-epic (DEV-586, DEV-587, DEV-589 and DEV-590).
- Duplicates: none found. The open GO-SPEC-ISSUE-004 (`not_run` versus `incomplete`) concerns execution states, not admission classes. [Risk factor and timezone domains](risk-factors-timezone-domains.md) closes value domains, not error classes.

## Affected Baselines and Requirements

- Public Draft `0.1.0` at immutable revision [`5a37e82865a08922c4821c7318656286933421e5`](https://github.com/tv-rain/barometer-spec/tree/5a37e82865a08922c4821c7318656286933421e5).
- Admission:
  - [REQ-TRUST-0017](https://github.com/tv-rain/barometer-spec/blob/5a37e82865a08922c4821c7318656286933421e5/library/task-trust.md#REQ-TRUST-0017) orders eleven admission steps without assigning a class to each.
  - [REQ-TRUST-0033](https://github.com/tv-rain/barometer-spec/blob/5a37e82865a08922c4821c7318656286933421e5/library/task-trust.md#REQ-TRUST-0033) introduces "initial" error classes; [REQ-TRUST-0034](https://github.com/tv-rain/barometer-spec/blob/5a37e82865a08922c4821c7318656286933421e5/library/task-trust.md#REQ-TRUST-0034) lists ten.
  - [REQ-TRUST-0024](https://github.com/tv-rain/barometer-spec/blob/5a37e82865a08922c4821c7318656286933421e5/library/task-trust.md#REQ-TRUST-0024) requires fail-closed `task_trust_unavailable` for unavailable or invalid replay state "for a remote task" and is silent for embedded tasks.
  - [REQ-TRUST-0007](https://github.com/tv-rain/barometer-spec/blob/5a37e82865a08922c4821c7318656286933421e5/library/task-trust.md#REQ-TRUST-0007) bounds remote `issued_at` to 300 seconds in the future; [REQ-TRUST-0001](https://github.com/tv-rain/barometer-spec/blob/5a37e82865a08922c4821c7318656286933421e5/library/task-trust.md#REQ-TRUST-0001) rejects a remote task without trusted time. Neither names a class.
- Unsupported features:
  - [REQ-SAFETY-0017](https://github.com/tv-rain/barometer-spec/blob/5a37e82865a08922c4821c7318656286933421e5/data-formats/task-safety.md#REQ-SAFETY-0017) permits rejecting an unknown risk factor type "as unsupported", but no class exists for it.
  - [REQ-EXECUTION-0021](https://github.com/tv-rain/barometer-spec/blob/5a37e82865a08922c4821c7318656286933421e5/data-formats/task-execution.md#REQ-EXECUTION-0021), [REQ-EXECUTION-0023](https://github.com/tv-rain/barometer-spec/blob/5a37e82865a08922c4821c7318656286933421e5/data-formats/task-execution.md#REQ-EXECUTION-0023), [REQ-CONTEXT-0026](https://github.com/tv-rain/barometer-spec/blob/5a37e82865a08922c4821c7318656286933421e5/library/network-context.md#REQ-CONTEXT-0026) and [REQ-CONTEXT-0028](https://github.com/tv-rain/barometer-spec/blob/5a37e82865a08922c4821c7318656286933421e5/library/network-context.md#REQ-CONTEXT-0028) treat an unavailable required egress field as an unsatisfied execution constraint, recorded per attempt as `network_context_unavailable`. They do not address an implementation that has no egress acquisition at all.
- `task_id` length: [REQ-TRUST-0019](https://github.com/tv-rain/barometer-spec/blob/5a37e82865a08922c4821c7318656286933421e5/library/task-trust.md#REQ-TRUST-0019) states the 1–128 byte rule as identifier syntax, while [Registered Initial Limits](https://github.com/tv-rain/barometer-spec/blob/5a37e82865a08922c4821c7318656286933421e5/library/registered-limits.md) lists 128 bytes as a registered limit.
- Implementation: `tv-rain/barometer-go` at `b7f5372eae4292faf65078e88bc941b5d076d8cf`. No admission package exists. `task.AdmissionError` holds the ten public codes; validation rejects an unknown risk factor type with a validation error that has no admission class yet. The Go [admission design](https://github.com/tv-rain/barometer-go/blob/main/docs/admission.md) marks each affected mapping *open*. No binding, native or platform behavior is implemented or validated.

## Finding and Reproduction

No public class covers a task that is valid under the public schema but uses a feature the implementation does not provide. The Go admission plan rejects tasks that require egress Network Context until egress acquisition exists. The public text instead admits such a task and lets every attempt end with `network_context_unavailable`. REQ-SAFETY-0017's "unsupported" rejection likewise has no class.

The public text also leaves these mappings open:

- the presented bytes are not bound to the supplied source context (missing, expired or mismatched binding), and trusted time is unavailable: `task_source_unauthenticated` or `task_trust_unavailable`;
- remote `issued_at` more than 300 seconds in the future;
- `task_id` over 128 bytes: `task_schema_invalid` or `task_limit_exceeded`;
- a well-formed but unregistered test or test version;
- a source policy generation higher than the active one;
- a path or proxy that issuer authority, local policy or the target registration does not permit;
- effective risk above a local-only bound, or `unknown` without a reviewed local permission;
- precedence when several steps would fail.

Evidence: document review only, at the baselines above. No Go behavior is affected yet, because no admission code exists. No synthetic, runtime or device reproduction is claimed.

Affected work: the *open* admission mappings and their Go conformance cases. Interim handling: no class is chosen and no Go behavior changes; Go case plans assert only that rejection happens, that the class is a public class and that no network activity occurs. Unaffected: mappings the public text already determines, such as `task_expired`, `task_id_conflict`, `policy_rollback` and `target_not_registered` for an unmatched target.

## Impact and Required Reviews

- Safety/privacy: every alternative rejects or skips before network activity, so the direct safety difference is small. Admitting an unsupported task can produce a stream of `not_run` attempts that hosts and analysts may mistake for network failures. A dedicated class keeps "this build cannot run the task" separate from task invalidity and from network state. No destination, traffic, retained data or identifier is added. Error classes remain code-only (REQ-TRUST-0035).
- Measurement/interpretation: an admission error is not a Measurement Result and not evidence of censorship (REQ-TRUST-0033). `task_unsupported` must not be read as a property of the network or of the task's safety.
- Compatibility: `task_unsupported` extends the operational vocabulary. Hosts and issuers that branch on the ten classes must handle an eleventh. The mapping table and embedded replay rule clarify or tighten behavior without new fields. No external producers, hosts or stored tasks are known; this is an assumption, not assessed deployment evidence.
- Required reviews: public maintainer disposition; safety review of the mapping, which is required and not completed. Host integration review applies when a binding exposes admission classes. No privacy, legal or platform-policy effect is identified. No specialist review is claimed complete.

## Alternatives and Proposed Public Resolution

Unsupported features:

1. (a) Reuse `task_schema_invalid`. No vocabulary change, but it labels a valid task invalid and hides the difference between a malformed task and an older or smaller implementation.
2. **(b) Add `task_unsupported` (proposed; accepted).** A distinct class for a valid task that requires a test, version, risk factor type or capability the implementation does not provide.
3. (c) Admit the task and let execution record `network_context_unavailable`. Already conforms for egress, but produces attempt streams that resemble network failures, and gives REQ-SAFETY-0017's rejection branch no class.

Other mappings:

1. **(a) A normative condition-to-class table, with first-failing-step precedence (proposed; accepted).** Implementations agree on the class for each condition.
2. (b) State that classes are advisory and only rejection is normative. Avoids a table but leaves hosts and issuers unable to branch consistently.

Retaining the current text without disposition leaves implementations free to diverge.

Proposed wording, included in this change (see the disposition), in `library/task-trust.md`:

- After REQ-TRUST-0025, a new requirement extending fail-closed replay handling to `embedded` tasks.
- After REQ-TRUST-0035, a new requirement defining `task_unsupported` and its scope, and a new requirement with first-failing-step precedence and the condition-to-class table. The proposed table maps:
  - unbound task bytes and future remote `issued_at` to `task_source_unauthenticated`, because provenance is not established;
  - unavailable trusted time to `task_trust_unavailable`;
  - `task_id` over 128 bytes to `task_limit_exceeded`, because Registered Initial Limits lists it as a registered limit;
  - an unregistered test or version, a rejected unknown risk factor type and a missing capability to `task_unsupported`;
  - a higher source policy generation to `task_policy_unavailable`, because the policy the task was issued under is not active;
  - a path not permitted by issuer authority or local policy, and risk above a local bound or unpermitted `unknown`, to `task_issuer_not_authorized`, as failures of the effective-authority intersection (REQ-TRUST-0010);
  - a path not permitted by the matched target registration to `target_not_registered`.

Rejected options within (a): `task_schema_invalid` for `task_id` length, which would split one registered limit across two classes; `policy_rollback` for a higher generation, which names the opposite condition; a separate local-policy denial class, which would add a second new class without a demonstrated host need. The name `task_issuer_not_authorized` for local-policy denials is imprecise; maintainers accept it as the intersection failure rather than add a class.

Proposed requirement-ID lifecycle: REQ-TRUST-0017, REQ-TRUST-0024, REQ-TRUST-0033 and REQ-TRUST-0034 remain active and unchanged. Each new obligation receives a new allocation above the current maximum, REQ-TRUST-0035: REQ-TRUST-0036 (`task_unsupported`), REQ-TRUST-0037 (precedence and table) and REQ-TRUST-0038 (embedded replay), reconciled against the target branch before merge. Proposed version decision: retain Draft `0.1.0`. REQ-TRUST-0033 already describes the list as initial, and the change adds no serialized field; this does not assert that every existing host remains compatible.

Expected cases: a task with `execution.context` requirements is rejected with `task_unsupported` by an implementation without egress acquisition, and is admitted by one that has it; a task with an unknown risk factor type is either rejected with `task_unsupported` or admitted with that factor treated as `unknown`; a task with a 129-byte `task_id` is rejected with `task_limit_exceeded`; a task failing at both step 3 and step 6 receives the step 3 class; an embedded task with unreadable replay state is rejected with `task_trust_unavailable`. Every rejection occurs with no network activity, run or attempt. These remain proposals until the wording is merged.

## Ordering and Public Disposition

- Coordination decision: not needed; no architecture or responsibility boundary changes.
- Order: merge this record together with the wording, catalog allocations and version decision in one public change. Then align the internal task-trust review, whose validation plan names admission classes. Then update the Go `GO-SPEC-ISSUE-008` entry, admission design and case plans, and add `task_unsupported` to `task.AdmissionError`. Go admission tasks adopt the table. Bindings and hosts follow.
- Internal alignment: required. The internal task-trust review validation plan lists admission classes, including fail-closed replay "for remote task"; it must cite the merged wording without adding private normative obligations.
- Maintainer disposition, rationale and date: see [Maintainer Disposition](#maintainer-disposition--october-19-2026).

## Adoption and Closure Evidence

- Closure requires: the merged wording revision with its requirement allocations and version decision; internal review alignment; Go adoption evidence (the new code in `task.AdmissionError`, admission tests asserting the exact class for each table row and for precedence, and traceability citing them); and the Go record linking all of these.
- Binding and host adoption are outside the current Go tasks and remain to be assessed when those components exist.

## Maintainer Disposition — October 19, 2026

The project owner and public maintainer, Lev, accepted alternative (b) for unsupported features and alternative (a) for the other mappings on October 19, 2026, in the DEV-596 task review.

- **`task_unsupported`:** a new admission class for a task that is valid under the public schema but requires a test or version, risk factor type or capability the implementation does not provide. Runtime unavailability of a provided capability remains an execution constraint.
- **Mappings and precedence:** a rejected task receives the class of the first failing step in REQ-TRUST-0017 order. Conditions the public text did not map use the table as proposed above.
- **Embedded replay:** unavailable or invalid replay state fails closed with `task_trust_unavailable` for `embedded` tasks as well as remote tasks.
- **Rationale:** a dedicated class keeps implementation capability separate from task validity and network state, so hosts do not mistake unsupported tasks for network failures. A normative table lets independent implementations, hosts and issuers agree. Failing closed on replay state for every origin is the conservative reading.
- **Wording:** accepted as proposed above. [REQ-TRUST-0036](../library/task-trust.md#REQ-TRUST-0036) and [REQ-TRUST-0037](../library/task-trust.md#REQ-TRUST-0037) follow REQ-TRUST-0035, and [REQ-TRUST-0038](../library/task-trust.md#REQ-TRUST-0038) follows REQ-TRUST-0025, in `library/task-trust.md`.
- **Requirement IDs:** REQ-TRUST-0036, REQ-TRUST-0037 and REQ-TRUST-0038 are new allocations recorded in the [requirement catalog](../requirements/catalog.json). REQ-TRUST-0017, REQ-TRUST-0024, REQ-TRUST-0033 and REQ-TRUST-0034 remain active and unchanged; no ID is retired or reused.
- **Version:** Draft `0.1.0` is retained. The admission error vocabulary gains `task_unsupported`; hosts that assume exactly ten classes must be updated. External hosts, producers and stored tasks are unassessed. No schema, field or test version value changes, and no release or runtime support claim is made.
- **Effect:** the merged immutable revision of this change becomes the accepted baseline for internal alignment and Go adoption; it is recorded as evidence on DEV-596 after merge. The required safety review of the mapping is not represented as completed.
- **Reopening:** if host integration shows a need to distinguish local-policy denials from issuer denials, open a new specification issue for a separate class and link it here.

## Merge and Adoption Addendum — October 21, 2026

Recorded under DEV-625. The sections above keep their wording as historical evidence, including their then-pending statements.

- **Merged revision:** the accepted wording, the REQ-TRUST-0036 to REQ-TRUST-0038 allocations and the Draft `0.1.0` retention were merged on October 19, 2026 through [public PR #14](https://github.com/tv-rain/barometer-spec/pull/14) as immutable revision [`d93aff93cbc17e7c065fb40d8f6e2e01a697bf35`](https://github.com/tv-rain/barometer-spec/tree/d93aff93cbc17e7c065fb40d8f6e2e01a697bf35) (head `46f44bb0366dfc46e409b9f607910772b8d971e2`).
- **Later public change:** the [signed remote task package](signed-remote-task-packages.md) change at `e97502747c917a16bc2b71337535ff972bbd7d64` retired REQ-TRUST-0037 with successor [REQ-TRUST-0047](../library/task-trust.md#REQ-TRUST-0047), which keeps its conditions and classes except that step 2 failures follow REQ-TRUST-0052 and the remote `issued_at` row became a package check. REQ-TRUST-0036 and REQ-TRUST-0038 remain active. The proxy-compatibility row is tracked in [Admission Class for Proxy-Incompatible Task Parameters](proxy-compatibility-admission-class.md).
- **Internal alignment:** the internal task-trust review validation plan was aligned to `d93aff9` under DEV-596 (internal review repository PR #5, merged at `56ee602b858a0db63cc0b8d1d8a3dc9b3c35e66d`).
- **Go adoption:** [DEV-597](https://app.clickup.com/t/124kk1zcb7t) adopted the disposition in Go [PR #41](https://github.com/tv-rain/barometer-go/pull/41), merged at `e4dbfc2c4068f95d8579f38a1e1d2103cc8322ba`, adding `task_unsupported` to `task.AdmissionError` and updating the admission design, case plans and traceability ([adoption addendum](https://github.com/tv-rain/barometer-go/blob/e4dbfc2c4068f95d8579f38a1e1d2103cc8322ba/docs/specification-issues.md#adoption-addendum--october-19-2026-1)). The admission tasks [DEV-586](https://app.clickup.com/t/124kk1zcadx) to [DEV-590](https://app.clickup.com/t/124kk1zcae4) (Go PRs #44, #45, #46, #48 and #49), [DEV-591](https://app.clickup.com/t/124kk1zcae5) (PR #50), [DEV-592](https://app.clickup.com/t/124kk1zcae7) (PR #52) and [DEV-594](https://app.clickup.com/t/124kk1zcaea) (PR #54) implement the rows, first-failing-step precedence and embedded fail-closed replay, with synthetic unit-test evidence recorded in the Go record. `CC-TRUST-ADMISSION-PROCEDURE` and `CC-TRUST-ADMISSION-ERRORS` remain planned.
- **Remaining before closure:** the required safety review of the mapping, to be confirmed by the maintainer in the DEV-575 assessment; the Go record linking the internal alignment and recording whether the unit-test evidence covers every table row and precedence, which it currently leaves to review; and binding and host adoption, unassessed until those components exist (DEV-455). The disposition remains accepted with adoption pending. No runtime, platform, field or release support is claimed.
