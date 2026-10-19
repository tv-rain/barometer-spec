# Proposal: `risk_factors` and `timezone` Value Domains

**Disposition:** Accepted wording (alternative (a) for both questions); merge and downstream adoption pending
**Date:** October 19, 2026
**Related task:** [DEV-581 — Obtain public disposition for GO-SPEC-ISSUE-007](https://app.clickup.com/t/124kk1zcaag)

This record asks public maintainers to dispose of two value domains that Draft `0.1.0` leaves unspecified: whether an empty `risk_factors` array satisfies the requirement to supply risk factors, and which `timezone` values exist. It adds no serialized field and makes no support claim. Opening this record did not accept its proposal; the [maintainer disposition](#maintainer-disposition--october-19-2026) below did. Sections before it are the proposal as reviewed. The accepted wording is included in the same public change as this record.

## Identity and Ownership

- Local finding: `GO-SPEC-ISSUE-007` in the Go [specification-issue record](https://github.com/tv-rain/barometer-go/blob/main/docs/specification-issues.md#go-spec-issue-007-undefined-allowed-values-for-risk_factors-and-timezone), raised October 16, 2026 under DEV-573 from the DEV-572 case-plan triage.
- Public identity: this Markdown record, once reviewed through a public PR. Responsible maintainer: the project owner, Lev.
- Reporter: the Go implementation agent under the task owner's instruction. Public maintainers own disposition and wording; the Go implementation owner owns adoption under [DEV-582](https://app.clickup.com/t/124kk1zcaah).
- Duplicates: none found. [Strict JSON decoding](strict-json-decoding.md) governs member names, types and presence, not these value domains.

## Affected Baselines and Requirements

- Public Draft `0.1.0` at immutable revision [`9cafe8d1dc48fb40fb6e49b58a8eefe41a9ee306`](https://github.com/tv-rain/barometer-spec/tree/9cafe8d1dc48fb40fb6e49b58a8eefe41a9ee306). The cited safety and schedule text is unchanged from the Go finding's baseline `a944ed6c389fec9f0d089f0044ead6fe845328b1`.
- `risk_factors`:
  - [REQ-SAFETY-0012](https://github.com/tv-rain/barometer-spec/blob/9cafe8d1dc48fb40fb6e49b58a8eefe41a9ee306/data-formats/task-safety.md#REQ-SAFETY-0012) requires `risk_factors` when `risk_level` is `medium`, `high` or `unknown`, and allows omission for `low`. It sets no minimum number of factors.
  - [REQ-SAFETY-0013](https://github.com/tv-rain/barometer-spec/blob/9cafe8d1dc48fb40fb6e49b58a8eefe41a9ee306/data-formats/task-safety.md#REQ-SAFETY-0013) defines the factor fields; [REQ-SAFETY-0018](https://github.com/tv-rain/barometer-spec/blob/9cafe8d1dc48fb40fb6e49b58a8eefe41a9ee306/data-formats/task-safety.md#REQ-SAFETY-0018) requires the overall level to be at least as restrictive as every known factor.
- `timezone`:
  - [REQ-SCHEDULE-0013](https://github.com/tv-rain/barometer-spec/blob/9cafe8d1dc48fb40fb6e49b58a8eefe41a9ee306/data-formats/task-schedule.md#REQ-SCHEDULE-0013) describes `timezone` as optional, "`local` is default", without listing allowed values.
  - [REQ-SCHEDULE-0014](https://github.com/tv-rain/barometer-spec/blob/9cafe8d1dc48fb40fb6e49b58a8eefe41a9ee306/data-formats/task-schedule.md#REQ-SCHEDULE-0014) defines only `local`, as the current timezone reported by the device.
- Implementation: `tv-rain/barometer-go` at `58e03a1f65600371960f735595f0a3c84550611f` (merged Foundation code); the affected `internal/validation` and `internal/taskdecode` code is unchanged on Go `main` at `66bfdeb6090a23a3942d92a97910949a9c7790e4`. The Go cross-cutting traceability manifest at that revision marks REQ-SAFETY-0012, REQ-SCHEDULE-0013 and REQ-SCHEDULE-0014 as `planned`; their conformance cases are not implemented. No binding, native or platform behavior is implemented or validated.

## Finding and Reproduction

Current merged Go behavior:

- `risk_factors`: the task decoder accepts an array of any length. Validation rejects only a missing list. A `medium`, `high` or `unknown` task with `risk_factors: []` is accepted.
- `timezone`: validation accepts only `local` (or omission, treated as `local`) and rejects every other value.

Both choices were made without a public disposition. The `timezone` choice is the conservative reading. The `risk_factors` choice is not: it admits a higher-risk task with no machine-readable explanation of that risk. Another conforming implementation could reasonably decide either question the other way.

Synthetic reproduction, October 16, 2026: a temporary, uncommitted local test using the existing Go fixture decoder decoded synthetic tasks with `risk_level` `medium`, `high` and `unknown` and `risk_factors: []` without error, and rejected the same tasks with `risk_factors` absent. No measurement, runtime or device reproduction is claimed.

Affected work: further Go adoption that depends on either domain, and any claim that the affected validators conform. Interim handling: Go behavior is unchanged until an approved adoption task; no fallback is selected. Unaffected: other safety and schedule validation.

## Impact and Required Reviews

- Safety/privacy: `risk_factors` explains effective risk to hosts and reviewers. Accepting `[]` does not lower effective risk, which remains bounded by the registered baseline (REQ-SAFETY-0018 and the baseline rule), but it weakens review and host decision-making for exactly the tasks that need it. A `timezone` value domain beyond `local` would let a task schedule runs by a zone other than the device's, which adds an input the device must interpret and could make run timing correlate across devices in different zones. Neither question adds destinations, traffic, retained data or identifiers.
- Measurement/interpretation: none directly. A rejected task is an admission error, not a measurement result or evidence of censorship.
- Compatibility: alternative (a) for both questions matches or tightens current Go behavior. Producers that emit `risk_factors: []` for `medium`, `high` or `unknown` tasks would be rejected. No external producers or stored tasks are known; this is an assumption, not assessed deployment evidence. Alternative (b) for either question is a schema extension that needs a version decision.
- Required reviews: public maintainer disposition; safety review of the `risk_factors` rule. Mobile platform review applies only if an IANA timezone domain is adopted. No privacy, legal or platform-policy effect is identified for alternative (a). No specialist review is claimed complete.

## Alternatives and Proposed Public Resolution

`risk_factors`:

1. **(a) Require at least one factor (proposed; accepted).** For `medium`, `high` and `unknown`, an empty array does not satisfy REQ-SAFETY-0012 and the task is rejected. Conservative; keeps a machine-readable explanation for every task that is not `low`. Tightens current Go behavior.
2. (b) Allow `[]` explicitly. Matches current Go behavior. Leaves higher-risk tasks without an explanation and makes the "required" field a presence marker only.

`timezone`:

1. **(a) Close the domain to `local` in Draft `0.1.0` (proposed; accepted).** Any other value is rejected. Matches current Go behavior. Defers zone-specific scheduling to a later reviewed version.
2. (b) Define a bounded IANA timezone domain. Needs an identifier set and version, a length bound, handling for zones unknown to the device database and for database version skew, mobile platform review, and a version decision.

Retaining the current text without disposition leaves implementations free to diverge on both questions.

Proposed wording under alternative (a), included in this change (see the disposition):

- `data-formats/task-safety.md`, after REQ-SAFETY-0012, a new requirement: "When `risk_level` is `medium`, `high`, or `unknown`, `risk_factors` must contain at least one risk factor. An empty array does not satisfy this requirement, and the task must be rejected."
- `data-formats/task-schedule.md`, after REQ-SCHEDULE-0014, a new requirement: "In this version, `local` is the only defined `timezone` value. A task containing any other `timezone` value must be rejected."

Proposed requirement-ID lifecycle: REQ-SAFETY-0012, REQ-SCHEDULE-0013 and REQ-SCHEDULE-0014 remain active and unchanged. Each new sentence is a new obligation and receives a new allocation above the current maximum in its namespace (currently REQ-SAFETY-0031 and REQ-SCHEDULE-0043), reconciled against the target branch before merge. Proposed version decision: retain Draft `0.1.0` as a restriction/clarification, following the [strict JSON decoding](strict-json-decoding.md) precedent; this does not assert that every previous producer remains compatible.

Expected cases under alternative (a): `medium`, `high` and `unknown` tasks with `risk_factors: []` are rejected at admission with a bounded non-measurement error and no run or attempt; the same tasks with one valid factor are accepted as structurally valid. A task with `timezone` omitted or `local` is accepted; values such as `UTC`, `Europe/Berlin`, `""` and `Local` are rejected. These remain proposals until the wording is merged.

## Ordering and Public Disposition

- Coordination decision: not needed; no architecture or responsibility boundary changes.
- Order: merge this record together with the wording, catalog allocations and version decision in one public change, then the Go `GO-SPEC-ISSUE-007` entry update. Go adoption under DEV-582 then changes `risk_factors` validation, adds negative and positive cases for both domains, and updates traceability against the merged revision. Bindings and hosts follow.
- Internal alignment: no internal review or validation plan currently covers these fields or requirements, so none is required now. If later internal task-trust or safety review covers task safety declarations, it must cite the merged wording without adding private normative obligations.
- Maintainer disposition, rationale and date: see [Maintainer Disposition](#maintainer-disposition--october-19-2026).

## Adoption and Closure Evidence

- Closure requires: the merged wording revision with its requirement allocations and version decision; Go adoption evidence under DEV-582 (rejection of `risk_factors: []` for `medium`, `high` and `unknown`, `timezone` cases, and traceability citing the new tests); and the Go record linking both.
- Existing Go `timezone` validation is expected to need no behavior change; DEV-582 records the evidence or the non-applicability.
- Binding and host adoption are outside the current Go task and remain to be assessed when those components exist.

## Maintainer Disposition — October 19, 2026

The project owner and public maintainer, Lev, accepted alternative (a) for both questions on October 19, 2026, in the DEV-581 task review.

- **`risk_factors`:** for `risk_level` `medium`, `high` and `unknown`, `risk_factors` must contain at least one risk factor. An empty array does not satisfy REQ-SAFETY-0012 and the task is rejected. Current Go behavior, which accepts `[]`, does not conform and must change under DEV-582.
- **`timezone`:** in Draft `0.1.0`, `local` is the only defined value. Any other value is rejected. Current Go behavior conforms.
- **Rationale:** both readings are the conservative ones. A task that is not `low` risk must explain its risk in machine-readable form for hosts and reviewers. Additional timezone values would need their own bounded domain and platform review, and no deployment need for them has been identified.
- **Wording:** accepted as proposed above. [REQ-SAFETY-0031](../data-formats/task-safety.md#REQ-SAFETY-0031) follows REQ-SAFETY-0012 in `data-formats/task-safety.md`, and [REQ-SCHEDULE-0043](../data-formats/task-schedule.md#REQ-SCHEDULE-0043) follows REQ-SCHEDULE-0014 in `data-formats/task-schedule.md`.
- **Requirement IDs:** REQ-SAFETY-0031 and REQ-SCHEDULE-0043 are new allocations recorded in the [requirement catalog](../requirements/catalog.json). REQ-SAFETY-0012, REQ-SCHEDULE-0013 and REQ-SCHEDULE-0014 remain active and unchanged; no ID is retired or reused.
- **Version:** Draft `0.1.0` is retained as a restriction/clarification. Producers that emit `risk_factors: []` for `medium`, `high` or `unknown` tasks, or a `timezone` other than `local`, do not conform. External producers and stored tasks are unassessed. No schema, field or test version value changes, and no release or runtime support claim is made.
- **Effect:** the merged immutable revision of this change becomes the accepted baseline for Go adoption; it is recorded as evidence on DEV-581 after merge. No specialist safety review is represented as completed.
- **Reopening:** if a deployment needs zone-specific scheduling, open a new specification issue for a bounded timezone domain and link it here.
