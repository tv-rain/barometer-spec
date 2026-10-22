# Proposal: Boundary Between `not_run` and `incomplete`

**Disposition:** Accepted; adoption pending: wording merged at `84f52f8`, internal alignment merged, Go adoption pending; alternative (a) with `completed` after a recorded terminal outcome, `completed` for the NET-05 `network_not_validated` and `inconclusive` outcomes, `constraints_unsatisfied` for undetectable required network conditions, and no Network Context in `not_run` results
**Date:** October 22, 2026
**Related task:** [DEV-579 — Obtain public disposition for GO-SPEC-ISSUE-004 (not_run vs incomplete boundary)](https://app.clickup.com/t/124kk1zcaae)

This record asks public maintainers when an execution attempt is `not_run` and when it becomes `incomplete`, and settles three related cases: an interruption after a terminal observation, the execution state of two NET-05 composite outcomes, and the reason for a required network condition that cannot be detected. Because the state decides whether a result retains Network Context, it also decides a data-minimization question. It adds no state, reason, field or limit and makes no support claim. Opening this record did not accept its proposal; the [maintainer disposition](#maintainer-disposition--october-22-2026) below did. Sections before it are the proposal as reviewed. The accepted wording is included in the same public change as this record.

## Identity and Ownership

- Local finding: [GO-SPEC-ISSUE-004](https://github.com/tv-rain/barometer-go/blob/2a6d7af52b0d18cfe6efb5cc10161f3a33eb7a67/docs/specification-issues.md#go-spec-issue-004-boundary-between-not_run-and-incomplete) in the Go specification-issue record, raised October 16, 2026 under DEV-573 from the DEV-572 case-plan triage.
- Public identity: this Markdown record, once reviewed through a public PR. Responsible maintainer: the project owner, Lev.
- Reporter: the Go implementation agent under the task owner's instruction. Public maintainers own disposition and wording. The Go implementation owner owns adoption.
- Related: [Observation vocabularies](observation-vocabularies.md) clarified incomplete observation fields, not execution states. Duplicates: none found.

## Affected Baselines and Requirements

- Public Draft `0.1.0` at immutable revision [`02fdbf20545ee7e6279dd7378c375ce1d5a13875`](https://github.com/tv-rain/barometer-spec/tree/02fdbf20545ee7e6279dd7378c375ce1d5a13875). The finding was raised against [`a944ed6`](https://github.com/tv-rain/barometer-spec/tree/a944ed6c389fec9f0d089f0044ead6fe845328b1); the cited text is unchanged between the two revisions.
- Requirements at `02fdbf2`:
  - [REQ-RESULT-0019](https://github.com/tv-rain/barometer-spec/blob/02fdbf20545ee7e6279dd7378c375ce1d5a13875/data-formats/measurement-result.md#REQ-RESULT-0019) to [REQ-RESULT-0021](https://github.com/tv-rain/barometer-spec/blob/02fdbf20545ee7e6279dd7378c375ce1d5a13875/data-formats/measurement-result.md#REQ-RESULT-0021): the three states, the reasons and the state rules, without a boundary between `not_run` and `incomplete`.
  - [REQ-RESULT-0023](https://github.com/tv-rain/barometer-spec/blob/02fdbf20545ee7e6279dd7378c375ce1d5a13875/data-formats/measurement-result.md#REQ-RESULT-0023) and [REQ-RESULT-0024](https://github.com/tv-rain/barometer-spec/blob/02fdbf20545ee7e6279dd7378c375ce1d5a13875/data-formats/measurement-result.md#REQ-RESULT-0024): Network Context is required for completed and incomplete remote tests, and may be omitted for `not_run` only before a snapshot was captured.
  - [REQ-EXECUTION-0015](https://github.com/tv-rain/barometer-spec/blob/02fdbf20545ee7e6279dd7378c375ce1d5a13875/data-formats/task-execution.md#REQ-EXECUTION-0015): a task "may not run" when network conditions cannot be detected, with no state or reason.
  - [REQ-EXECUTION-0023](https://github.com/tv-rain/barometer-spec/blob/02fdbf20545ee7e6279dd7378c375ce1d5a13875/data-formats/task-execution.md#REQ-EXECUTION-0023), [REQ-CONTEXT-0025](https://github.com/tv-rain/barometer-spec/blob/02fdbf20545ee7e6279dd7378c375ce1d5a13875/library/network-context.md#REQ-CONTEXT-0025) and [REQ-CONTEXT-0028](https://github.com/tv-rain/barometer-spec/blob/02fdbf20545ee7e6279dd7378c375ce1d5a13875/library/network-context.md#REQ-CONTEXT-0028): context acquisition is part of the bounded attempt; an unavailable required field makes the constraint unsatisfied and records `network_context_unavailable`.
  - [REQ-NET-05-0046](https://github.com/tv-rain/barometer-spec/blob/02fdbf20545ee7e6279dd7378c375ce1d5a13875/tests/net-05.md#REQ-NET-05-0046) and [REQ-NET-05-0047](https://github.com/tv-rain/barometer-spec/blob/02fdbf20545ee7e6279dd7378c375ce1d5a13875/tests/net-05.md#REQ-NET-05-0047): the NET-05 composite outcomes, without the accompanying execution state for `network_not_validated` and `inconclusive`.
  - Test termination rules REQ-NET-01-0027, REQ-NET-03-0029, REQ-DNS-01-0039, REQ-DNS-03-0028, REQ-DNS-04-0028, REQ-TCP-01-0026, REQ-TLS-01-0027 and REQ-HTTP-01-0038: interruptions during a running test produce `incomplete`. They do not say when a test starts.
- Implementation: `tv-rain/barometer-go` at `2a6d7af52b0d18cfe6efb5cc10161f3a33eb7a67`. `internal/execution` and `internal/result` model the three states and validate state, reason and measurement combinations, including the current REQ-RESULT-0024 rule. No runner selects a state for a real interruption. No binding, native or platform behavior is implemented or validated.

## Finding and Reproduction

No public rule says when an attempt stops being `not_run` and becomes `incomplete`. Four cases are open:

1. An interruption after admission and context capture but before any test traffic.
2. An interruption after a test's terminal observation is recorded but before its connection is closed.
3. The execution state that accompanies the NET-05 composite outcomes `network_not_validated` and `inconclusive`.
4. The state and reason when a required network condition cannot be detected (REQ-EXECUTION-0015), where neither `constraints_unsatisfied` nor `network_context_unavailable` is named.

Documented rules: `not_run` prohibits `measurement`; a snapshot captured before a `not_run` attempt stops must be retained, because REQ-RESULT-0024 permits omission only before capture. The [result bundle example](https://github.com/tv-rain/barometer-spec/blob/02fdbf20545ee7e6279dd7378c375ce1d5a13875/data-formats/result-bundle.md) shows a `not_run` result with `constraints_unsatisfied` and no context. Assumption: context acquisition, which can send traffic to a context endpoint, is part of the attempt but not of the test. Unresolved before this disposition: all four cases.

Reproduction: none is required; the gap is in the text. Synthetic cases are listed under the proposed resolution.

Affected work that must stop: selecting the state and reason for these four cases in Go runner, execution and result code (DEV-561), and the expected values in the `M-*-TERMINATION` case plans. Interim handling: existing Go models keep validating only the documented combinations; no fallback state is chosen. Unaffected: interruptions during an active protocol operation, which every termination rule already maps to `incomplete` with no `measurement`.

## Impact and Required Reviews

- Safety/privacy: the state decides whether a context snapshot is kept for an attempt that sent no test traffic. Under the current text, a `not_run` attempt that stopped after capture must retain coarse access and egress classification, including country, region and ASN when available, even though no measurement was made. Under the proposed resolution, no `not_run` result retains context; snapshots are used only for eligibility and are discarded with the attempt. Cases 1 and 4 produce `not_run`, so context for those attempts is no longer retained. No destination, traffic, identifier or retained field is added. The change reduces retention and does not create distinctive traffic.
- Measurement/interpretation: analysts can separate "never started" (`not_run`) from "interrupted after the test started" (`incomplete`). Neither state is evidence of interference; both are commonly caused by host cancellation, scheduling, mobile lifecycle, network changes or unavailable context services. Without context, a `not_run` result cannot show which network it would have run on; that is accepted as the cost of minimization. An allowlist mismatch or an undetectable condition is an eligibility outcome, not a network observation.
- Compatibility: Draft `0.1.0` wording change. A producer that retained context in a `not_run` result after capture, as REQ-RESULT-0024 required, is non-conforming under the new rule; receivers must reject such a result. No field, state or reason is added or removed.
- Required reviews: public maintainer disposition. A privacy review is required by GO-SPEC-ISSUE-004 only for a rule that retains more context; the proposed rule retains less, so no additional privacy review is required for this change. No legal or platform-policy effect is identified. Safety review of the overall runtime mapping remains with the runtime and execution work.

## Alternatives and Proposed Public Resolution

Case 1, the boundary:

1. **(a) `not_run` until the test starts its first test-specific operation, then `incomplete` (proposed; accepted).** Admission, validation, context capture and acquisition, and constraint evaluation do not start the test. The state then describes whether the measurement began, matches the existing bundle example and the per-test termination rules, and does not depend on context endpoint behavior.
2. (b) `not_run` only before admission completes. Every admitted attempt that is interrupted, including one that failed only while acquiring context, would be `incomplete` and would retain context although no test traffic was sent. This conflicts with `constraints_unsatisfied` being reported as `not_run` and increases retention.
3. (c) Per-test definitions. More precise for unusual tests but inconsistent across tests, harder to validate, and unnecessary for the nine initial tests; a single shared rule with the test-start definition covers zero-traffic NET-01 and the NET-05 profile.

Retaining the current text leaves implementations free to diverge.

Case 2: once the test records its terminal outcome, the attempt is `completed`; a later interruption while connections close does not change it. The alternative, `incomplete`, would discard a valid observation because of cleanup timing and would conflict with a first-termination rule.

Case 3: `network_not_validated` and `inconclusive` are terminal composite outcomes retained with `completed`. The alternatives, `incomplete` or `not_run`, conflict with REQ-RESULT-0021 (`not_run` prohibits `measurement`) and with REQ-NET-05-0047 (only interruption maps to the `incomplete` outcome). A task-level `require_validated` constraint that fails before the test starts stays an execution constraint: `not_run` with `constraints_unsatisfied`.

Case 4: `not_run` with `constraints_unsatisfied`; Barometer must not guess the condition. `network_context_unavailable` stays limited to required Network Context fields under REQ-CONTEXT-0028. Naming `network_context_unavailable` instead would blur access-state detection with egress-context acquisition.

Network Context: a `not_run` result never contains `network_context`. The alternative, keeping it optional after capture, retains context for attempts that made no measurement and lets producers diverge.

Proposed wording, included in this change:

- `data-formats/measurement-result.md`: a State Boundaries subsection with new [REQ-RESULT-0051](../data-formats/measurement-result.md#REQ-RESULT-0051) (test start and the `not_run`/`incomplete` boundary) and [REQ-RESULT-0052](../data-formats/measurement-result.md#REQ-RESULT-0052) (a recorded terminal outcome stays `completed`); [REQ-RESULT-0053](../data-formats/measurement-result.md#REQ-RESULT-0053) replacing REQ-RESULT-0024; and an editorial pointer in the `network_context` field description.
- `data-formats/task-execution.md`: [REQ-EXECUTION-0031](../data-formats/task-execution.md#REQ-EXECUTION-0031) replacing REQ-EXECUTION-0015.
- `tests/net-05.md`: new [REQ-NET-05-0061](../tests/net-05.md#REQ-NET-05-0061) giving the execution state of each composite outcome.

Proposed requirement-ID lifecycle: REQ-RESULT-0024 and REQ-EXECUTION-0015 are retired with successors REQ-RESULT-0053 and REQ-EXECUTION-0031, because their obligations change materially. REQ-RESULT-0051, REQ-RESULT-0052 and REQ-NET-05-0061 are new allocations. All other IDs, including the per-test termination rules, remain active and unchanged. Proposed version decision: retain Draft `0.1.0`; no serialized field, state or reason is added.

Expected cases, synthetic only:

- Host cancellation after admission and context capture, before the first TCP-01 connection attempt: `not_run`, `cancelled_by_host`, no `measurement`, no `network_context`.
- Egress-context acquisition fails for a required `country_code`: `not_run`, `network_context_unavailable`, no `network_context`.
- Context available but the country is not in `allowed_country_codes`: `not_run`, `constraints_unsatisfied`, no `network_context`.
- Attempt deadline expires during the first DNS-01 query: `incomplete`, `attempt_deadline_exceeded`, no `measurement`, `network_context` present.
- TLS-01 records its terminal outcome and the host cancels while the connection closes: `completed`, the recorded `measurement`, no `reason`; a cleanup failure does not change the result.
- NET-05 observes `not_validated` under a local policy that requires validation: `completed` with outcome `network_not_validated`; NET-05 whose completion state cannot be normalized: `completed` with outcome `inconclusive`.
- A task with `allowed_transports: [wifi]` on a platform that reports the transport as unknown: `not_run`, `constraints_unsatisfied`.
- A receiver gets a `not_run` result containing `network_context`: the result is rejected.

These remain proposals until the wording is merged.

## Ordering and Public Disposition

- Coordination decision: not needed; no architecture or responsibility boundary changes.
- Order: merge this record together with the wording and catalog changes in one public change. Then record internal review alignment. Then adopt in Go: the Go record cites the merged revision, the result decoder rejects `not_run` results with `network_context`, the runner selects states under REQ-RESULT-0051 and REQ-RESULT-0052 (DEV-561), and the traceability mapping is rebaselined to replace references to the retired IDs. Bindings and hosts follow.
- Maintainer disposition, rationale and date: see [Maintainer Disposition](#maintainer-disposition--october-22-2026).

## Adoption and Closure Evidence

- Closure requires: the merged wording revision with its catalog changes; internal review alignment or its recorded non-applicability; and Go adoption evidence: execution and result code selecting states under the accepted rules, the decoder rejecting context in `not_run` results, termination case plans with the expected values, and traceability citing the new IDs.
- Go currently enforces the retired REQ-RESULT-0024 and cites REQ-RESULT-0024 and REQ-EXECUTION-0015 against its pinned baseline; those references remain valid for that baseline until rebaselined. Binding and host adoption are outside the current tasks.

## Maintainer Disposition — October 22, 2026

The project owner and public maintainer, Lev, accepted the recommended resolution on October 22, 2026, in the DEV-579 task review, including the prohibition of `network_context` in `not_run` results. The public PR review records confirmation of the wording.

- **Rule:** an attempt is `not_run` until the test starts its first test-specific operation and `incomplete` if a cross-cutting condition stops it afterwards; a recorded terminal outcome stays `completed`; NET-05 `network_not_validated` and `inconclusive` are retained with `completed`; an undetectable required network condition produces `not_run` with `constraints_unsatisfied`; a `not_run` result never contains `network_context`.
- **Rationale:** the state then describes whether the measurement began, independent of context endpoint behavior; valid observations are not discarded because of cleanup timing; and attempts that made no measurement retain no Network Context.
- **Wording:** accepted as proposed: REQ-RESULT-0051, REQ-RESULT-0052 and REQ-RESULT-0053 in `data-formats/measurement-result.md`, REQ-EXECUTION-0031 in `data-formats/task-execution.md`, and REQ-NET-05-0061 in `tests/net-05.md`.
- **Requirement IDs:** REQ-RESULT-0024 and REQ-EXECUTION-0015 are retired with successors REQ-RESULT-0053 and REQ-EXECUTION-0031 in the [requirement catalog](../requirements/catalog.json). REQ-RESULT-0051, REQ-RESULT-0052, REQ-RESULT-0053, REQ-EXECUTION-0031 and REQ-NET-05-0061 are new allocations. No ID is reused.
- **Version:** Draft `0.1.0` is retained. No schema field, state, reason or limit is added, and no release or runtime support claim is made.
- **Effect:** the merged immutable revision of this change becomes the accepted baseline for internal alignment and Go adoption; it is recorded as evidence on DEV-579 after merge.

## Merge Addendum — October 22, 2026

Recorded under DEV-579. The sections above keep their wording as historical evidence, including their then-pending statements.

- **Merged revision:** the accepted wording, the catalog changes and the Draft `0.1.0` retention were merged on October 22, 2026 through [public PR #22](https://github.com/tv-rain/barometer-spec/pull/22) as immutable revision [`84f52f8872a5af9e6d97894611e3b2eaba18aba8`](https://github.com/tv-rain/barometer-spec/tree/84f52f8872a5af9e6d97894611e3b2eaba18aba8) (head `334c6ce1cf633e69f02805664ff5d078357e2470`). It is the accepted baseline for [REQ-RESULT-0051](https://github.com/tv-rain/barometer-spec/blob/84f52f8872a5af9e6d97894611e3b2eaba18aba8/data-formats/measurement-result.md#REQ-RESULT-0051), [REQ-RESULT-0052](https://github.com/tv-rain/barometer-spec/blob/84f52f8872a5af9e6d97894611e3b2eaba18aba8/data-formats/measurement-result.md#REQ-RESULT-0052), [REQ-RESULT-0053](https://github.com/tv-rain/barometer-spec/blob/84f52f8872a5af9e6d97894611e3b2eaba18aba8/data-formats/measurement-result.md#REQ-RESULT-0053), [REQ-EXECUTION-0031](https://github.com/tv-rain/barometer-spec/blob/84f52f8872a5af9e6d97894611e3b2eaba18aba8/data-formats/task-execution.md#REQ-EXECUTION-0031) and [REQ-NET-05-0061](https://github.com/tv-rain/barometer-spec/blob/84f52f8872a5af9e6d97894611e3b2eaba18aba8/tests/net-05.md#REQ-NET-05-0061), and for the retirement of REQ-RESULT-0024 and REQ-EXECUTION-0015.
- **Internal alignment:** the NET-05 validation plan was aligned with these rules through internal review repository PR #10, merged at `0414e543db2fea2bb156daaa823e0cc37c759ae0`.
- **Go record:** the disposition was recorded in [Go PR #59](https://github.com/tv-rain/barometer-go/pull/59), merged at `30f0c39be044535f4e6a26c0d677d81b3a2cb770`. No Go behavior changed.
- **Remaining before closure:** Go adoption: the result decoder rejecting `network_context` in `not_run` results, runner and execution state selection under REQ-RESULT-0051 and REQ-RESULT-0052 (DEV-561), termination case plans with the expected values, and traceability rebaselined to this revision so that current references cite the new IDs. Binding and host adoption follow. The disposition remains accepted with adoption pending. No runtime, platform, field or release support is claimed.
