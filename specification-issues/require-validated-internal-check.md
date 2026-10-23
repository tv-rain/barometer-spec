# Proposal: Library Internal Check for `require_validated`

**Disposition:** Open (proposal; no specification text changed)
**Date:** October 23, 2026
**Related task:** [DEV-649 — Prepare the public specification-issue record for the require_validated internal check (GO-SPEC-ISSUE-013)](https://app.clickup.com/t/124kk1zct3d)

This record asks public maintainers to resolve a conflict between two rules for the `require_validated` network condition. One rule says the library calls its own connectivity check when the platform offers no validation method; another says an undeterminable validation state is unsatisfied and Barometer must not guess. The contract does not define the check. This record lists alternatives and their tradeoffs and does not select one; disposition and wording belong to public maintainers. The normative files are unchanged until maintainers approve a separate change. Opening this record does not accept any alternative, including the interim rule one implementation uses.

## Identity and Ownership

- Local finding: [GO-SPEC-ISSUE-013](https://github.com/tv-rain/barometer-go/blob/cdbd16043d991d4b11544420b5ba8531fb8c95f1/docs/specification-issues.md#go-spec-issue-013-library-internal-check-for-require_validated) in the Go specification-issue record, raised October 23, 2026 under [DEV-644](https://app.clickup.com/t/124kk1zcrjd) while implementing network-condition evaluation.
- Public identity: this Markdown record, once reviewed through a public PR. Responsible maintainer: the project owner, Lev.
- Reporter: the Go implementation agent under the task owner's instruction. Public maintainers own disposition and wording. The Go implementation owner owns adoption.
- Duplicates: none found. Related: [`not-run-incomplete-boundary.md`](not-run-incomplete-boundary.md), which introduced REQ-EXECUTION-0031 and its mapping of undetectable required network conditions; it did not change REQ-EXECUTION-0016.

## Affected Baselines and Requirements

- Public Draft `0.1.0` at immutable revision [`5d01879cfd1d47396c780befa2567f7e90439948`](https://github.com/tv-rain/barometer-spec/tree/5d01879cfd1d47396c780befa2567f7e90439948), the baseline the Go finding cites. `data-formats/task-execution.md` and `data-formats/network-context.md` are unchanged at [`9804ab34f21863723a94caba0541fd4e64870fce`](https://github.com/tv-rain/barometer-spec/tree/9804ab34f21863723a94caba0541fd4e64870fce).
- Requirements:
  - [REQ-EXECUTION-0016](https://github.com/tv-rain/barometer-spec/blob/5d01879cfd1d47396c780befa2567f7e90439948/data-formats/task-execution.md#REQ-EXECUTION-0016): the network-condition fields table describes `require_validated` as "Require confirmed Internet connectivity, system method will be used to check when available, lib internal check will be called otherwise."
  - [REQ-EXECUTION-0031](https://github.com/tv-rain/barometer-spec/blob/5d01879cfd1d47396c780befa2567f7e90439948/data-formats/task-execution.md#REQ-EXECUTION-0031): a required network condition that cannot be determined, including validation required by `require_validated`, is unsatisfied; the task must not run, Barometer must not guess the condition, and a recorded attempt has `execution.state: not_run` and `execution.reason: constraints_unsatisfied`.
  - Context only: [REQ-CONTEXT-FORMAT-0004](https://github.com/tv-rain/barometer-spec/blob/5d01879cfd1d47396c780befa2567f7e90439948/data-formats/network-context.md#REQ-CONTEXT-FORMAT-0004) defines the access object's `validated` field (`yes`, `no`, `unknown`) as the "coarse platform Internet-validation state". It is not in question.
- Implementation: `tv-rain/barometer-go` at [`cdbd16043d991d4b11544420b5ba8531fb8c95f1`](https://github.com/tv-rain/barometer-go/tree/cdbd16043d991d4b11544420b5ba8531fb8c95f1), merged into Go `main` with Go PR #70 at `c4b3761085c8bc9703db32baf7c3327d9697d18b` (the finding is unchanged there), implements the interim rule described below with synthetic tests only. No binding, native, host or platform behavior is implemented or validated, and which platforms report `unknown` validation in practice is not established.

## Finding and Reproduction

REQ-EXECUTION-0016 says the library calls its own connectivity check when the platform offers no validation method. REQ-EXECUTION-0031 says an undeterminable validation state is unsatisfied and the task does not run. Read together, it is unclear whether an implementation must send a check before deciding the condition, or must treat the condition as unsatisfied.

The contract does not define the check named in REQ-EXECUTION-0016. It gives no:

1. endpoint or destination selection;
2. protocol, request content or success criterion;
3. traffic, time or retry bound, or relationship to the attempt's limits and byte accounting;
4. timing relative to the measurement, or caching across attempts;
5. privacy or safety property;
6. result representation, including whether `validated` reports the platform state or the check's outcome.

An implementation therefore cannot build the check without inventing observable behavior, including network traffic outside the attempt's registered test.

Observed behavior: barometer-go implements this interim rule, approved by its task owner with the DEV-644 plan while this record is open. It is a local interpretation and not accepted public behavior:

1. `require_validated` is satisfied only when the platform's own validation state is `validated: yes`.
2. `no`, `unknown`, a capability error and an unreadable access context leave the condition unsatisfied, as REQ-EXECUTION-0031 requires. The run is not started; before the first attempt of a run that was already reserved, the attempt is `not_run` with `constraints_unsatisfied`.
3. No library connectivity check is implemented, and no traffic is sent to decide validation.

Synthetic reproduction: a task with `require_validated: true` on a platform whose access state reports `validated: unknown`. Under REQ-EXECUTION-0031 the task does not run. Under REQ-EXECUTION-0016 the library calls an internal check and the outcome depends on a check the contract does not define.

Assumptions: the platform validation state is the "system method" REQ-EXECUTION-0016 refers to. Unresolved: whether a library check is intended at all, and if so its definition and representation.

Affected work: the conformance row of the internal execution validation plan that exercises the network-condition fields with a fake library internal check is blocked until disposition. Interim handling: the Go behavior above, recorded locally as GO-SPEC-ISSUE-013. Other network-condition evaluation is unaffected.

## Impact and Required Reviews

- Safety/privacy: the interim rule sends no traffic outside the registered test. A library check would send additional traffic before or alongside a measurement, to a destination the contract would have to choose. That traffic could make Barometer more distinctive on a monitored network, could reveal which service or deployment the device belongs to, and adds to the device's network, time and energy use. No identifier or retained data changes under the interim rule. Any library check needs a **safety and privacy review** before it is specified or implemented, **not completed**.
- Resource bounds: alternatives (b) and (c) add traffic and time that the attempt and aggregate limits do not currently account for; their accounting would have to be specified.
- Measurement/interpretation: under the interim rule, a task requiring validation never runs on a platform that reports no validation state, which reduces coverage there. Under (b) and (c), a check that fails on a filtered or degraded network would leave the condition unsatisfied and the measurement would not run, so networks where the check destination is blocked could be under-measured. A task that does not run because validation is unsatisfied is not evidence of censorship or of a network failure; outages, captive portals, congestion and platform behavior are alternative explanations.
- Compatibility: (a) is a Draft `0.1.0` clarification with no new field. (b) and (c) add behavior, and (c) adds local policy configuration; both need a version or compatibility decision. Implementations that sent a check under the current text would change behavior under (a).
- Platform policy: platform validation methods are outside Barometer's control and their availability varies by platform. A library check could raise platform-policy questions about background network use; this is not assessed. No legal effect is identified.
- Required reviews: public maintainer disposition; a safety and privacy review of any library check, not completed. No review is identified as required for (a) beyond maintainer disposition.

## Alternatives and Proposed Public Resolution

1. **(a) Remove the internal-check clause.** REQ-EXECUTION-0016 describes `require_validated` as satisfied by the platform validation state, and REQ-EXECUTION-0031 remains the only rule when that state cannot be determined. Matches the Go interim rule; sends no extra traffic and needs no new field. A task requiring validation never runs where the platform reports no validation state.
2. **(b) Specify a bounded, reviewed library check.** Define the endpoint or destination selection, protocol, success criterion, traffic and time bounds, accounting against the attempt's limits, timing, failure mapping and result representation. Allows tasks to run where the platform reports no validation state, at the cost of distinctive traffic outside the registered test, a destination choice with its own safety and availability concerns, and a safety and privacy review before adoption.
3. **(c) Let local policy enable a reviewed check per deployment.** As (b), but off unless the host's local policy enables it for a deployment. Keeps the default free of extra traffic and lets deployments that accept the tradeoff opt in, at the cost of a new configuration surface and per-deployment review of that choice.
4. **Retain the current text.** Leaves the conflict in place; implementations may diverge between not running and inventing a check, and the blocked conformance row stays undefined.

Proposed exact wording: none; maintainers select the rule and wording. The target is the `require_validated` row of REQ-EXECUTION-0016 in `data-formats/task-execution.md`, and REQ-EXECUTION-0031 if its relationship to a check changes.

Proposed requirement-ID lifecycle and version: subject to maintainer review. Whether REQ-EXECUTION-0016 is edited in place or replaced depends on whether maintainers treat the change as editorial or as a changed obligation. Draft `0.1.0` can be retained under (a); (b) and (c) need a version or compatibility decision.

Expected cases, to be defined after disposition: `require_validated: true` with platform `validated` of `yes`, `no` and `unknown`; a capability error and an unreadable access context; under (b) or (c), check success, failure, timeout and cancellation, with limit accounting; under (c), the check disabled and enabled by local policy. These remain proposals until the contract is accepted.

## Ordering and Public Disposition

- Coordination decision: not needed for (a). For (b) or (c), maintainers decide whether a library-originated check changes a responsibility boundary that needs a coordination decision first.
- Public review: this record, reviewed through a public PR. Maintainer disposition, rationale and date: pending.
- Order after disposition: merge the accepted wording, if any, and record its immutable revision; align the internal execution validation plan's network-condition row; adopt in Go with that row's case and update GO-SPEC-ISSUE-013; then bindings and hosts.
- If deferred or rejected: the existing text remains authoritative, Go keeps its interim rule as a local interpretation, and the conformance row stays blocked.

## Adoption and Closure Evidence

- Accepted public baseline and requirement links: pending.
- Internal review and validation-plan alignment: pending, or a recorded reason it does not apply.
- Go adoption evidence, or a recorded statement that the interim rule already conforms: pending.
- Closure requires the public disposition, its immutable revision if wording changes, the safety and privacy review if a library check is accepted, and Go adoption evidence or recorded non-applicability. Binding and host adoption are assessed when those components exist. No runtime, platform, field or release support is claimed.
