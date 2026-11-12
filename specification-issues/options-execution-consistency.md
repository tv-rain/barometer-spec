# Specification Issue: Options and Execution-Limit Consistency at Admission

## Identity and Ownership

- Local finding: `GO-SPEC-ISSUE-024` in the Go [finding record](https://github.com/tv-rain/barometer-go/blob/main/docs/specification-issues.md#go-spec-issue-024-options-and-execution-limit-consistency-at-admission), recorded from the residual review of the shared sources that carry no requirement ID.
- Disposition: **Accepted; editorial wording merged with this record, retaining Draft `0.1.0`.** The project owner, Lev, selected alternative (a) on November 12, 2026.
- Reporter: the Go implementation agent under the task owner's instruction. Public maintainers own disposition and wording; the Go implementation owner owns adoption.
- No duplicate identified. Related: [`step-8-classes-and-order.md`](step-8-classes-and-order.md) and [`step-8-input-options-admission-class.md`](step-8-input-options-admission-class.md) define the step-8 classes for `options` that fail validation or exceed a registered maximum.

## Affected Baselines and Requirements

- Public `tv-rain/barometer-spec` revision [`45bc424bd9829f5389b3b4494d0966e10e21da94`](https://github.com/tv-rain/barometer-spec/tree/45bc424bd9829f5389b3b4494d0966e10e21da94), Draft `0.1.0`, [Task Options — Execution Precedence](https://github.com/tv-rain/barometer-spec/blob/45bc424bd9829f5389b3b4494d0966e10e21da94/data-formats/task-options.md#execution-precedence). The section is unchanged at `dc51b6d52abb414cdfd71930f442b80408f36f00`.
- Requirements: [REQ-OPTIONS-0016](https://github.com/tv-rain/barometer-spec/blob/45bc424bd9829f5389b3b4494d0966e10e21da94/data-formats/task-options.md#REQ-OPTIONS-0016) (options cannot extend or override an execution limit) and [REQ-OPTIONS-0017](https://github.com/tv-rain/barometer-spec/blob/45bc424bd9829f5389b3b4494d0966e10e21da94/data-formats/task-options.md#REQ-OPTIONS-0017). The unmarked paragraph after REQ-OPTIONS-0016, "Clearly inconsistent tasks should be rejected during validation", has no ID. The step-8 rules REQ-TRUST-0056 to REQ-TRUST-0059 name no class for it.
- Implementation: `tv-rain/barometer-go` at [`c1ed38f`](https://github.com/tv-rain/barometer-go/tree/c1ed38fbb7a5ea9dd2dd3b0000eda2b95e981874) applies no cross-field consistency check at admission; the outer attempt deadline bounds execution. No native, binding or field support is established.

## Finding and Reproduction

"Should", "clearly" and "normally" leave open whether rejection is required, which option and limit combinations are inconsistent, and which admission class applies. Two conforming implementations could disagree on admitting a synthetic task whose single mandatory operation has an option timeout of 40,000 ms with `execution.limits.max_duration_ms` of 30,000 ms: one admits it and stops the attempt at 30,000 ms, the other rejects it with an unnamed class.

**Blocked:** an exact admission assertion for inconsistent option and limit combinations. **Interim handling:** Go admits such a task when every value is otherwise valid, and the execution limit stops the attempt. **Unaffected:** REQ-OPTIONS-0016 and REQ-OPTIONS-0017 run-time cases.

## Impact and Required Reviews

- **Safety and privacy:** none under the selected rule. REQ-OPTIONS-0016 keeps every attempt within its execution limits, which cannot exceed the registered maxima, so admitting the task adds no traffic, time or retained value beyond those bounds.
- **Interpretation:** an attempt stopped by the outer deadline is an execution interruption, not a protocol outcome (REQ-OPTIONS-0017).
- **Compatibility:** no field, class or bound changes; Draft `0.1.0` is retained. An implementation that rejected such tasks would now admit them.
- **Reviews:** maintainer disposition recorded above. The rule adds no admission or traffic surface, so no further safety or privacy review is identified.

## Alternatives and Selected Public Resolution

1. **(a) Informative (selected).** The paragraph becomes explicitly informative: run-time precedence under REQ-OPTIONS-0016 bounds execution, and admission does not reject a task on that ground alone. No new rejection surface.
2. **(b) Normative rejection** at step 8 with `task_schema_invalid` when a single mandatory operation's option timeout exceeds `max_duration_ms`, with a closed list of covered option and limit pairs. Fails earlier, but adds a rejection rule and a list to maintain.
3. **(c) Per-test rules.** Each registered test declares its own consistency rules. Spreads one question over every test document.

Wording: the paragraph in [Execution Precedence](../data-formats/task-options.md#execution-precedence) now states that it is informative and that admission does not reject a task on that ground alone. It was never allocated an ID; REQ-OPTIONS-0016 and REQ-OPTIONS-0017 keep their IDs and wording, and no ID is allocated or retired.

Expected cases: a task whose option timeout exceeds `max_duration_ms` and is otherwise valid is admitted, and its attempt stops at the execution deadline without a protocol outcome.

## Ordering and Public Disposition

No architecture or responsibility boundary changes, so no coordination decision is needed. Order: public merge of this wording and record; internal alignment only where an internal plan cites the paragraph; the Go reference pin update and record; bindings and hosts.

## Adoption and Closure Evidence

Merged with this record, retaining Draft `0.1.0`; the merge revision is recorded in the Go finding record. Go behavior already matches the selected rule, so no code changes. The run-time case belongs to the planned `CC-OPTIONS-EXECUTION-PRECEDENCE` family in Go. No platform, field or release support is claimed.
