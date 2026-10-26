# Proposal: Admission Class for Step-8 Input and Options Failures

**Disposition:** Accepted wording (alternative (a)); merged at `1206247`; internal alignment merged; maintainer safety review of the mapping passed; adopted in Go; binding and host adoption pending; follow-up finding GO-SPEC-ISSUE-016 open
**Date:** October 26, 2026
**Related task:** [DEV-663 — Obtain the public disposition for GO-SPEC-ISSUE-010 and adopt it in Go](https://app.clickup.com/t/124kk1zcw4r)

This record asks public maintainers to name the admission error class for a task whose `input` or `options` fail validation at admission step 8, and to resolve whether invalid options are rejected or skipped. It proposes `task_schema_invalid` for invalid content and `task_limit_exceeded` for a stricter test-defined byte limit, with rejection at admission. It adds no admission class or serialized field and makes no support claim. The proposal and the [maintainer disposition](#maintainer-disposition--october-26-2026) are reviewed in the same public change.

## Identity and Ownership

- Local finding: `GO-SPEC-ISSUE-010` in the Go [specification-issue record](https://github.com/tv-rain/barometer-go/blob/d8310854460ebf83f264cbdd8edcb4db630c7743/docs/specification-issues.md#go-spec-issue-010-admission-class-for-step-8-input-and-options-failures), raised October 21, 2026 under DEV-624 from an observation recorded in the [proxy-compatibility admission class](proxy-compatibility-admission-class.md#alternatives-and-proposed-public-resolution) record.
- Public identity: this Markdown record, once reviewed through a public PR. Responsible maintainer: the project owner, Lev.
- Reporter: the Go implementation agent under the task owner's instruction. Public maintainers own disposition and wording. The Go implementation owner owns adoption under DEV-663.
- Duplicates: none found. [Admission Error Classes](admission-error-classes.md) mapped the step-8 path-authority and target-registration rows; [Admission Class for Proxy-Incompatible Task Parameters](proxy-compatibility-admission-class.md) mapped proxy compatibility only and left this class unmapped.

## Affected Baselines and Requirements

- Public Draft `0.1.0` at immutable revision [`bb805f07a36630db7250d5ab63006ed5e351f7a7`](https://github.com/tv-rain/barometer-spec/tree/bb805f07a36630db7250d5ab63006ed5e351f7a7). The Go finding cites `4743b636f29feb1f0f8d042866d04ccda3532938`; the cited requirements are unchanged since, except that REQ-TRUST-0039 now cites REQ-PROXY-0044.
- Admission:
  - Step 8 of [REQ-TRUST-0046](https://github.com/tv-rain/barometer-spec/blob/bb805f07a36630db7250d5ab63006ed5e351f7a7/library/task-trust.md#REQ-TRUST-0046) validates "all input, options, proxy compatibility, target tuples, redirect registrations, and composite steps atomically".
  - The [REQ-TRUST-0047](https://github.com/tv-rain/barometer-spec/blob/bb805f07a36630db7250d5ab63006ed5e351f7a7/library/task-trust.md#REQ-TRUST-0047) table has two step-8 rows, for a path refused by issuer authority or local policy and by the matched target registration. It applies a class another requirement names for a condition.
  - [REQ-TRUST-0039](https://github.com/tv-rain/barometer-spec/blob/bb805f07a36630db7250d5ab63006ed5e351f7a7/library/task-trust.md#REQ-TRUST-0039) names `task_schema_invalid` for proxy incompatibility and orders it after input and options, but names no class for input or options themselves.
- Input and options:
  - [REQ-INPUT-0006](https://github.com/tv-rain/barometer-spec/blob/bb805f07a36630db7250d5ab63006ed5e351f7a7/data-formats/task-input.md#REQ-INPUT-0006) and [REQ-OPTIONS-0009](https://github.com/tv-rain/barometer-spec/blob/bb805f07a36630db7250d5ab63006ed5e351f7a7/data-formats/task-options.md#REQ-OPTIONS-0009) reject unknown properties; [REQ-INPUT-0014](https://github.com/tv-rain/barometer-spec/blob/bb805f07a36630db7250d5ab63006ed5e351f7a7/data-formats/task-input.md#REQ-INPUT-0014) rejects an input that cannot be normalized safely; [REQ-OPTIONS-0021](https://github.com/tv-rain/barometer-spec/blob/bb805f07a36630db7250d5ab63006ed5e351f7a7/data-formats/task-options.md#REQ-OPTIONS-0021) prohibits certain option content.
  - [REQ-OPTIONS-0019](https://github.com/tv-rain/barometer-spec/blob/bb805f07a36630db7250d5ab63006ed5e351f7a7/data-formats/task-options.md#REQ-OPTIONS-0019) says that when options are unsupported, invalid or unsafe the probe "should reject or skip the task", without naming a class or choosing between rejection and an execution status.
  - [REQ-INPUT-0007](https://github.com/tv-rain/barometer-spec/blob/bb805f07a36630db7250d5ab63006ed5e351f7a7/data-formats/task-input.md#REQ-INPUT-0007) and [REQ-OPTIONS-0010](https://github.com/tv-rain/barometer-spec/blob/bb805f07a36630db7250d5ab63006ed5e351f7a7/data-formats/task-options.md#REQ-OPTIONS-0010) set the registered 49,152-byte `input` and 8,192-byte `options` maxima.
- Classes: [REQ-TRUST-0034](https://github.com/tv-rain/barometer-spec/blob/bb805f07a36630db7250d5ab63006ed5e351f7a7/library/task-trust.md#REQ-TRUST-0034) and [REQ-TRUST-0036](https://github.com/tv-rain/barometer-spec/blob/bb805f07a36630db7250d5ab63006ed5e351f7a7/library/task-trust.md#REQ-TRUST-0036).
- Implementation: `tv-rain/barometer-go` at `3aece5ef33f6c151a7f92c25a2fdf44116519bad`. Admission validates input and options against the selected test's schemas and codec and returns `task_schema_invalid` on failure, or `task_limit_exceeded` when a test-specific byte cap stricter than the registered maximum is exceeded. Only synthetic test-scoped codecs exist; no production test codec, binding, native or platform behavior is implemented or validated.

## Finding and Reproduction

The public text requires step 8 to validate input and options atomically but names no class for a failure, while REQ-OPTIONS-0019 permits either rejection or skipping with an execution status. A reader cannot tell:

- which class a task with an unknown option, an out-of-range value or an unnormalizable input receives; or
- whether a task with invalid options is rejected at admission or admitted and skipped.

No Draft `0.1.0` test currently defines an `input` or `options` byte limit stricter than the registered maximum; NET-05's `profile` limit equals the registered `input` maximum. The `task_limit_exceeded` row therefore has no current public instance and applies only to a future test that defines one.

Evidence: document review only, at the baselines above. No synthetic, runtime or device reproduction is claimed.

Affected work: exact-class assertions for these rows in admission conformance cases. Interim handling: no behavior change; Go keeps its current classes and marks them unmapped. Unaffected: the proxy-compatibility, path-authority, target-registration and composite rows of step 8, and the registered byte maxima.

## Impact and Required Reviews

- Safety/privacy: every alternative rejects or skips before network activity, so the direct safety difference is small. Admitting a task that cannot run schedules attempts with no measurement value. No destination, traffic, retained data or identifier is added. Error classes remain code-only (REQ-TRUST-0035).
- Measurement/interpretation: an admission error is not a Measurement Result and not evidence of censorship (REQ-TRUST-0033). The rejection depends only on the task's own fields.
- Compatibility: no class, field or schema value is added. Hosts and issuers that branch on admission classes gain a defined class; a host that relied on skipped execution for invalid options would instead see an admission rejection. No external producers, hosts or stored tasks are known; this is an assumption, not assessed deployment evidence.
- Required reviews: public maintainer disposition; safety review of the mapping, required and not completed; internal task-trust review alignment, because its validation plan covers the REQ-TRUST-0047 rows. Host integration review applies when a binding exposes admission classes. No privacy, legal or platform-policy effect is identified. No specialist review is claimed complete.

## Alternatives and Proposed Public Resolution

1. **(a) `task_schema_invalid` for invalid input or options, `task_limit_exceeded` for a stricter test-defined byte limit, rejection at admission (proposed).** Matches current Go behavior and the class names: invalid content is a malformed issuer task, and an exceeded byte limit is a limit failure wherever the limit is defined. Resolves REQ-OPTIONS-0019 toward rejection, consistent with step 8 rejecting atomically.
2. (b) `task_schema_invalid` for every step-8 input or options failure, including test-specific byte limits. Simpler, but reports the same byte-limit condition with different classes depending on whether the limit is registered or test-defined.
3. (c) `task_unsupported` for an option value a test defines but an implementation does not provide, with (a) or (b) for invalid values. REQ-TRUST-0036 and the REQ-TRUST-0047 step-6 row already give such a capability gap `task_unsupported`; a separate step-8 rule would narrow an existing class and needs its own review.
4. (d) Admit the task and record an execution status, as REQ-OPTIONS-0019 permits. Conflicts with step 8 rejecting atomically and schedules attempts that cannot run.

Retaining the current text leaves implementations free to diverge between (a) to (d).

Proposed wording:

- In `library/task-trust.md`, after REQ-TRUST-0039, a new requirement REQ-TRUST-0056 naming `task_schema_invalid` for input or options that fail validation against the selected test, `task_limit_exceeded` for a stricter test-defined byte limit checked before the content it bounds, `task_unsupported` unchanged for a capability gap, and no admission of a failing task for skipping or failure at execution.
- In `data-formats/task-options.md`, retire REQ-OPTIONS-0019 and add REQ-OPTIONS-0033: invalid or prohibited options are rejected at admission under REQ-TRUST-0056; an unprovided capability under REQ-TRUST-0036; options local policy does not permit under the REQ-TRUST-0047 class for that condition; and the task is not admitted to be skipped.

The byte-limit check precedes content validation so that a single step-8 failure combining both conditions receives exactly one class, and so that the content is decoded only within its bound. No other order within input and options is set.

Proposed requirement-ID lifecycle: REQ-TRUST-0056 and REQ-OPTIONS-0033 are new allocations above the current maxima. REQ-OPTIONS-0019 is retired with successor REQ-OPTIONS-0033, because the obligation changes from "reject or skip" to "reject". REQ-TRUST-0034, REQ-TRUST-0036, REQ-TRUST-0039, REQ-TRUST-0046, REQ-TRUST-0047, REQ-INPUT-0006, REQ-INPUT-0007, REQ-INPUT-0014, REQ-OPTIONS-0009, REQ-OPTIONS-0010 and REQ-OPTIONS-0021 remain active and unchanged. Proposed version decision: retain Draft `0.1.0`, because no class, field or schema value is added; this does not assert that every existing host remains compatible.

Expected cases: a task with an unknown `options` property is rejected with `task_schema_invalid`; a task with an input that cannot be normalized safely is rejected with `task_schema_invalid`; a task with an option value outside the test's field table is rejected with `task_schema_invalid`; a task whose `options` exceed a stricter test-defined byte limit is rejected with `task_limit_exceeded`, also when the content is otherwise invalid; a `proxy` task with invalid options and an incompatible configuration is rejected with `task_schema_invalid` at the input-and-options check; a valid option requiring an unprovided capability is rejected with `task_unsupported`. Every rejection occurs with no network activity, run or attempt. The byte-limit case needs a test that defines such a limit and is not executable against current public tests.

## Ordering and Public Disposition

- Coordination decision: not needed; no architecture or responsibility boundary changes.
- Order: this public change carries the proposal, disposition, wording, catalog allocations and version decision. Then the internal task-trust review validation plan is aligned to the merged revision. Then Go records the disposition in `GO-SPEC-ISSUE-010`, rebaselines its REQ-OPTIONS-0019 references to REQ-OPTIONS-0033 and adds exact-class admission cases under DEV-663. Bindings and hosts follow.
- Go compatibility: Go traceability cites REQ-OPTIONS-0019 at an earlier immutable baseline; those references stay valid until Go rebaselines, which must then cite REQ-OPTIONS-0033.

## Adoption and Closure Evidence

- Closure requires: the merged revision of this change; the internal task-trust review alignment; Go adoption evidence (admission cases asserting each class and the byte-limit precedence where a test defines such a limit, or its recorded non-applicability, and traceability citing them); the safety review of the mapping; and the Go record linking all of these.
- Binding and host adoption are outside the current Go tasks and remain to be assessed when those components exist.

## Maintainer Disposition — October 26, 2026

The project owner and public maintainer, Lev, accepted alternative (a) on October 26, 2026, in the DEV-663 task review, with the proposal, disposition and wording in one public change.

- **Class:** a task whose `input` or `options` fail validation against the selected registered test at admission step 8 is rejected with `task_schema_invalid`. A stricter test-defined byte limit on `input`, `options` or a value within them is rejected with `task_limit_exceeded`, checked before the content it bounds.
- **Capability gaps:** a valid value that requires a capability the implementation does not provide remains `task_unsupported` under REQ-TRUST-0036.
- **Rejection, not skipping:** a task with invalid or prohibited options is rejected at admission and is not admitted to be skipped or to fail at execution.
- **Rationale:** the conditions depend only on the task's own fields and every conforming implementation evaluates them the same way. Rejecting at admission matches step 8's atomic validation and avoids scheduling attempts that cannot run.
- **Wording:** [REQ-TRUST-0056](../library/task-trust.md#REQ-TRUST-0056) follows REQ-TRUST-0039 in the Admission Errors section of `library/task-trust.md`. [REQ-OPTIONS-0033](../data-formats/task-options.md#REQ-OPTIONS-0033) follows the retired [REQ-OPTIONS-0019](../data-formats/task-options.md#REQ-OPTIONS-0019) in `data-formats/task-options.md`.
- **Requirement IDs:** REQ-TRUST-0056 and REQ-OPTIONS-0033 are new allocations recorded in the [requirement catalog](../requirements/catalog.json). REQ-OPTIONS-0019 is retired with successor REQ-OPTIONS-0033. No ID is reused.
- **Version:** Draft `0.1.0` is retained. No admission class, field, schema or test version value changes. External hosts, producers and stored tasks are unassessed. No release or runtime support claim is made.
- **Internal alignment:** required; the internal task-trust review validation plan must cite the merged wording without adding private normative obligations.
- **Effect:** the merged immutable revision of this change becomes the accepted baseline for internal alignment and Go adoption under DEV-663; it is recorded as evidence on DEV-663 after merge. The required safety review of the mapping is not represented as completed.

## Adoption Record — October 26, 2026

Recorded under DEV-664. The sections above keep their wording as historical evidence, including their then-pending statements.

- **Merged revision:** the accepted wording, the REQ-TRUST-0056 and REQ-OPTIONS-0033 allocations, the retirement of REQ-OPTIONS-0019 and the Draft `0.1.0` retention were merged through [public PR #30](https://github.com/tv-rain/barometer-spec/pull/30) as immutable revision [`12062471875bbfbc55eafc94dc5a7ea4cd07ca5e`](https://github.com/tv-rain/barometer-spec/tree/12062471875bbfbc55eafc94dc5a7ea4cd07ca5e).
- **Internal alignment and review:** the task-trust review validation plan was aligned through internal review repository PR #14, merged at `bf2fce978f526fcc80aac2cf9d568352a45799f3`. PR #15, merged at `7868ed6ca180ef9ab6330d4256070a80d4402cd7`, records the safety review of the mapping by the project maintainer: passed, with one follow-up finding. It is a maintainer review, not an independent specialist review.
- **Go adoption:** [Go PR #80](https://github.com/tv-rain/barometer-go/pull/80), merged at `bb5df9ef2b97070b5301f473f8717e192b846e8e`, records the adoption; admission already returned these classes, and synthetic gate cases assert them for embedded and remote origin. The TCP-01 and DNS-01 production codecs use the same staged validation and define no stricter byte limit.
- **Remaining:** binding and host adoption. The unnamed classes and ordering found during adoption are tracked in the Go finding GO-SPEC-ISSUE-016 and need their own public record before any change. No runtime, platform, field or release support is claimed.
