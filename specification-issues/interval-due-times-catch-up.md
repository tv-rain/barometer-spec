# Proposal: Due Times and Catch-Up for Interval Repetition

**Disposition:** Open (proposal; no specification text changed)
**Date:** October 22, 2026
**Related task:** [DEV-639 — Prepare the public specification-issue record for interval due times and catch-up (GO-SPEC-ISSUE-011)](https://app.clickup.com/t/124kk1zcpc3)

This record asks public maintainers to define when the runs of an `interval` schedule become due: what the interval is measured from, whether the first run is jittered, and what happens to occurrences that become due while the host does not ask to start a run. It lists alternatives and their tradeoffs and does not select one; disposition and wording belong to public maintainers. The normative files are unchanged until maintainers approve a separate change. Opening this record does not accept any alternative, including the interim rule one implementation uses.

## Identity and Ownership

- Local finding: [GO-SPEC-ISSUE-011](https://github.com/tv-rain/barometer-go/blob/daeb718a291a33aff0eff492cc59d8dba8b00d2f/docs/specification-issues.md#go-spec-issue-011-due-times-and-catch-up-for-interval-repetition) in the Go specification-issue record, raised October 22, 2026 under [DEV-636](https://app.clickup.com/t/124kk1zcn0g) while implementing `StartRun`.
- Public identity: this Markdown record, once reviewed through a public PR. Responsible maintainer: the project owner, Lev.
- Reporter: the Go implementation agent under the task owner's instruction. Public maintainers own disposition and wording. The Go implementation owner owns adoption.
- Duplicates: none found. Related: none.

## Affected Baselines and Requirements

- Public Draft `0.1.0` at immutable revision [`5d01879cfd1d47396c780befa2567f7e90439948`](https://github.com/tv-rain/barometer-spec/tree/5d01879cfd1d47396c780befa2567f7e90439948), the baseline the Go finding cites. `data-formats/task-schedule.md` is unchanged at [`2ea5e0e27ac16b95f2e11f8f6689aef33b83f9a7`](https://github.com/tv-rain/barometer-spec/tree/2ea5e0e27ac16b95f2e11f8f6689aef33b83f9a7).
- Requirements in `data-formats/task-schedule.md`:
  - [REQ-SCHEDULE-0007](https://github.com/tv-rain/barometer-spec/blob/5d01879cfd1d47396c780befa2567f7e90439948/data-formats/task-schedule.md#REQ-SCHEDULE-0007): `starts_at` is the earliest time the task becomes eligible.
  - [REQ-SCHEDULE-0009](https://github.com/tv-rain/barometer-spec/blob/5d01879cfd1d47396c780befa2567f7e90439948/data-formats/task-schedule.md#REQ-SCHEDULE-0009): without `starts_at`, the task becomes eligible immediately after the probe accepts it.
  - [REQ-SCHEDULE-0019](https://github.com/tv-rain/barometer-spec/blob/5d01879cfd1d47396c780befa2567f7e90439948/data-formats/task-schedule.md#REQ-SCHEDULE-0019): `interval` is the number of seconds "between scheduled runs" (21,600 to 604,800); `jitter` is 300 seconds up to the lesser of 1,800 seconds or a quarter of `interval`.
  - [REQ-SCHEDULE-0020](https://github.com/tv-rain/barometer-spec/blob/5d01879cfd1d47396c780befa2567f7e90439948/data-formats/task-schedule.md#REQ-SCHEDULE-0020): a repeated run becomes due according to the interval and may start later because of execution constraints or time windows.
  - [REQ-SCHEDULE-0021](https://github.com/tv-rain/barometer-spec/blob/5d01879cfd1d47396c780befa2567f7e90439948/data-formats/task-schedule.md#REQ-SCHEDULE-0021): jitter is drawn locally and independently for each due run, and must not move a run before `starts_at`, after `not_after` or outside a time window.
  - [REQ-SCHEDULE-0030](https://github.com/tv-rain/barometer-spec/blob/5d01879cfd1d47396c780befa2567f7e90439948/data-formats/task-schedule.md#REQ-SCHEDULE-0030): `max_runs` (1 to 28) is required for `interval` repetition.
  - [REQ-SCHEDULE-0032](https://github.com/tv-rain/barometer-spec/blob/5d01879cfd1d47396c780befa2567f7e90439948/data-formats/task-schedule.md#REQ-SCHEDULE-0032): the first limit reached terminates the schedule.
  - [REQ-SCHEDULE-0034](https://github.com/tv-rain/barometer-spec/blob/5d01879cfd1d47396c780befa2567f7e90439948/data-formats/task-schedule.md#REQ-SCHEDULE-0034): a run or retry attempt may start only when every eligibility condition holds, including `max_runs` not reached.
  - [REQ-SCHEDULE-0035](https://github.com/tv-rain/barometer-spec/blob/5d01879cfd1d47396c780befa2567f7e90439948/data-formats/task-schedule.md#REQ-SCHEDULE-0035): the probe retains final authority to delay, skip or reject execution.
  - Context only: [REQ-SCHEDULE-0031](https://github.com/tv-rain/barometer-spec/blob/5d01879cfd1d47396c780befa2567f7e90439948/data-formats/task-schedule.md#REQ-SCHEDULE-0031) excludes retries from `max_runs`; it is not in question.
- Implementation: `tv-rain/barometer-go` at [`daeb718a291a33aff0eff492cc59d8dba8b00d2f`](https://github.com/tv-rain/barometer-go/tree/daeb718a291a33aff0eff492cc59d8dba8b00d2f) implements the interim rule described below, with synthetic tests only. The core starts no runs by itself; the host calls `StartRun`. No binding, native, host or platform behavior is implemented or validated.

## Finding and Reproduction

The existing text says that repeated runs become due "according to the interval" and may start late, and that each due run gets its own jitter. It does not say:

1. **Anchor.** What the interval is measured from: the first run's due time, `starts_at`, the acceptance time, or the actual start of the previous run.
2. **First run.** Whether the first run of a repeated task is jittered. REQ-SCHEDULE-0007 and REQ-SCHEDULE-0009 make the task eligible at `starts_at` or acceptance; REQ-SCHEDULE-0021 jitters "each due run".
3. **Missed occurrences.** What happens to occurrences that become due while the host does not ask to start a run, or while a time window or constraint prevents a run: whether each is run late, one after another, or skipped.
4. **Run limit.** Whether a skipped occurrence counts toward `max_runs`, so whether a task always makes `max_runs` runs or can make fewer.

These choices change how many runs a task makes and how close together they can start, which is observable behavior and affects traffic patterns.

Observed behavior: barometer-go implements this interim rule, approved by its task owner while this record is open. It is a local interpretation and not accepted public behavior:

1. The anchor is `starts_at` when present, otherwise the time the instance accepted the task.
2. Occurrence 0 is due at the anchor without jitter. Occurrence *k* ≥ 1 is due at anchor + *k* × `interval` + *j*ₖ, with *j*ₖ drawn locally once in [0, `jitter`] when the occurrence first becomes current.
3. The current occurrence is the latest *k* whose unjittered time has passed. Earlier occurrences that never started are skipped and do not start late. A skipped occurrence consumes no run; the schedule ends once *k* reaches `max_runs`, so a task makes at most `max_runs` runs and can make fewer.
4. The current occurrence starts only after its jittered due time while every other eligibility condition holds. A due time at or after `not_after` never starts. A call outside a time window leaves the occurrence current until the next one becomes current.
5. At most one run is reserved per occurrence.

Synthetic reproduction: with `interval` 21,600 seconds, `jitter` 300 and `max_runs` 4, a host that starts the first run at the anchor and next calls at anchor + 50,000 seconds gets occurrence 2 under the interim rule; occurrence 1 is skipped. The text does not say whether the conforming outcome is occurrence 2, occurrence 1 late, or occurrences 1 and 2 on successive calls.

Assumptions: the interval is meant as a nominal spacing, and the probe's authority to skip (REQ-SCHEDULE-0035) permits not running a missed occurrence. Unresolved: the four questions above.

Affected work: nothing is blocked; the task owner approved the interim rule while this record is open. Interim handling: the Go behavior above, recorded locally as GO-SPEC-ISSUE-011. Due-time conformance cases depend on the disposition.

## Impact and Required Reviews

- Safety/privacy: the rule decides how many measurement runs a device makes and how closely spaced they can be. Catch-up can produce several runs in a short period after a device was idle, which is more distinctive traffic than evenly spaced runs. The interim rule never exceeds `max_runs` and never runs missed occurrences in a burst, but two runs can still start close together when a window or constraint delays one occurrence until the next becomes current. Whether occurrence 0 is jittered changes how predictable the first run is relative to `starts_at` or delivery. No destination, retained data or identifier changes under any alternative.
- Resource bounds: alternatives (b) and (c) can produce more runs than (a) for the same host behavior; none exceeds `max_runs`.
- Measurement/interpretation: under (a) and (d), the number and spacing of runs depend on how often the host wakes, which reflects platform scheduling and device use, not network state. A missing or skipped run is not evidence of censorship or of a network failure.
- Compatibility: each alternative is a Draft `0.1.0` clarification with no new field. Implementations that adopted a different reading would change run counts and timing.
- Platform policy: hosts schedule wakeups with platform background facilities whose timing is not guaranteed; the rule must tolerate late and missed wakeups. No legal effect is identified.
- Required reviews: public maintainer disposition; a **safety review of the chosen rule** (traffic distinctiveness and run spacing), **not completed**. No privacy, legal or platform-policy review is identified as required beyond that.

## Alternatives and Proposed Public Resolution

1. **(a) Anchored grid with skipping.** The Go interim rule above. Runs stay on a fixed grid from the anchor; missed occurrences are skipped and consume no run. Never bursts; the schedule does not drift; a task can make fewer than `max_runs` runs when the host wakes rarely, and its end is bounded by the grid.
2. **(b) Anchor to the previous actual run start.** Each run becomes due `interval` after the previous run started. No occurrence is ever skipped and runs are always at least `interval` apart, but the schedule drifts with host wakeups and the task's total duration is unbounded except by `not_after` and expiry.
3. **(c) Fixed grid with catch-up, one run per call.** Each missed occurrence runs once, at most one per host call. Preserves `max_runs` runs when possible, but can start runs much closer together than `interval` after an idle period, which is the most distinctive traffic of the options.
4. **(d) Jitter occurrence 0 as well.** Independent of the choice above: the first run is also delayed by a local jitter of up to `jitter` after the anchor. Makes the first run less predictable relative to delivery; delays it by up to 30 minutes; reads REQ-SCHEDULE-0021 "each due run" literally.
5. **Retain the current text.** Leaves implementations free to diverge in run counts and spacing, and leaves due-time conformance cases undefined.

Proposed exact wording: none; maintainers select the rule and wording. The target is `data-formats/task-schedule.md` near REQ-SCHEDULE-0020 and REQ-SCHEDULE-0021.

Proposed requirement-ID lifecycle and version: subject to maintainer review. A clarification that adds obligations would normally use new allocations; whether REQ-SCHEDULE-0020 or REQ-SCHEDULE-0021 is replaced depends on the chosen wording. Draft `0.1.0` can be retained under each alternative, as none adds a serialized field.

Expected cases, to be defined after disposition: due time of occurrence 0 with and without `starts_at`; occurrence *k* at, just before and after its due time; a host idle across one and several occurrences; an occurrence delayed by a time window until the next becomes current; `max_runs` reached with and without skipped occurrences; a due time at or after `not_after`. These remain proposals until the contract is accepted.

## Ordering and Public Disposition

- Coordination decision: not needed; no architecture or responsibility boundary changes.
- Public review: this record, reviewed through a public PR. Maintainer disposition, rationale and date: pending.
- Order after disposition: merge the accepted wording, if any, and record its immutable revision; align the internal task-schedule review if its validation plan names due times; adopt in Go with due-time cases and update GO-SPEC-ISSUE-011; then bindings and hosts.
- If deferred or rejected: the existing text remains authoritative and Go keeps its interim rule as a local interpretation; nothing is blocked.

## Adoption and Closure Evidence

- Accepted public baseline and requirement links: pending.
- Internal review and validation-plan alignment: pending, or a recorded reason it does not apply.
- Go adoption evidence, or a recorded statement that the interim rule already conforms: pending.
- Closure requires the public disposition, its immutable revision if wording changes, the safety review of the chosen rule, and Go adoption evidence or recorded non-applicability. Binding and host adoption are assessed when those components exist. No runtime, platform, field or release support is claimed.
