# Specification Issue: Equal Start and End in a Time-Window Range

## Identity and Ownership

- Local finding: `GO-SPEC-ISSUE-014` in the Go [finding record](https://github.com/tv-rain/barometer-go/blob/54feb7d76c3ef52b2746e02ae6df67b424c86629/docs/specification-issues.md#go-spec-issue-014-equal-start-and-end-in-a-time-window-range), recorded from the runtime closeout limitation.
- Disposition: **Accepted; wording merged as REQ-SCHEDULE-0044 at `830e956`; Go reference update and case pending.** The project owner, Lev, selected the explicitly empty range on November 4, 2026.
- Reporter: the Go implementation agent under the task owner's instruction. Public maintainers own disposition and wording; the Go implementation owner owns adoption.
- No duplicate identified. Related: [`interval-due-times-catch-up.md`](interval-due-times-catch-up.md) covers other schedule timing.

## Affected Baselines and Requirements

- Public `tv-rain/barometer-spec` revision [`a46555b0a8c6500d5002e3768e76f2ddb38c67e6`](https://github.com/tv-rain/barometer-spec/tree/a46555b0a8c6500d5002e3768e76f2ddb38c67e6), Draft `0.1.0`, [Task Schedule — Time Window](https://github.com/tv-rain/barometer-spec/blob/a46555b0a8c6500d5002e3768e76f2ddb38c67e6/data-formats/task-schedule.md#time-window).
- Requirements: REQ-SCHEDULE-0013 (one to four unique, non-overlapping ranges), REQ-SCHEDULE-0015 (inclusive `start`, exclusive `end`), REQ-SCHEDULE-0016 (`HH:mm`) and REQ-SCHEDULE-0017 (a range crosses midnight when `end` is earlier than `start`). None defines equal endpoints.
- Implementation: `tv-rain/barometer-go` at [`54feb7d`](https://github.com/tv-rain/barometer-go/tree/54feb7d76c3ef52b2746e02ae6df67b424c86629) accepts an otherwise valid range with equal endpoints and matches no minute for it. No native, binding or field support is established.

## Finding and Reproduction

A synthetic window `{"ranges":[{"start":"12:00","end":"12:00"}]}` reads three ways: an empty range (inclusive start and exclusive end at the same minute), a full-day range (by analogy with crossing midnight), or an invalid range. The readings differ in whether the task ever runs. Go treats it as empty: it passes validation and never permits a run start or retry; another nonempty range in the same window still applies. This is source-inspected behavior, not a conformance result.

**Blocked:** exact conformance assertions for equal endpoints. **Interim handling:** Go behavior is unchanged. **Unaffected:** every range with distinct endpoints.

## Impact and Required Reviews

- **Safety and privacy:** the selected rule adds no traffic, field or retained value; a range that permits nothing cannot enlarge the run schedule. A full-day reading would have expanded eligible traffic, and rejection would have changed admission compatibility.
- **Interpretation:** an issuer expecting a full day gets no run. A missing run is not a measurement and carries no interpretation.
- **Compatibility:** no field, class or bound changes; Draft `0.1.0` is retained. Tasks that relied on a full-day reading in another implementation would stop running there.
- **Reviews:** maintainer disposition recorded above. Scoped safety review: the rule only narrows when a run may start, so no safety or privacy review beyond this record is identified.

## Alternatives and Selected Public Resolution

1. **Explicitly empty range (selected).** Matches the inclusive-start, exclusive-end definition and current Go behavior.
2. **Reject equal endpoints** with `task_schema_invalid`. Fails earlier, but rejects tasks that implementations admit today.
3. **Full-day range.** Allows a 24-hour range in one entry, at the cost of expanding eligible traffic from a form that currently runs nothing.

The selected rule is prepared as [REQ-SCHEDULE-0044](../data-formats/task-schedule.md#REQ-SCHEDULE-0044), the next allocation above maximum 0043. An empty range overlaps no other range, and an identical range remains a duplicate under REQ-SCHEDULE-0013. No existing requirement is retired or redefined.

Expected cases: a window of one empty range never permits a run start or retry; an empty range beside a nonempty range leaves the nonempty range effective; two identical empty ranges are rejected as duplicates.

## Ordering and Public Disposition

No architecture or responsibility boundary changes, so no coordination decision is needed. Order: public review and merge of this wording; internal schedule review alignment where applicable; Go reference update and an equal-endpoint case; native and host validation before release.

## Adoption and Closure Evidence

Merged: REQ-SCHEDULE-0044, the catalog entry and this record through [public PR #39](https://github.com/tv-rain/barometer-spec/pull/39) at [`830e956`](https://github.com/tv-rain/barometer-spec/tree/830e9564849ebfedaa0860d9f01032574e2b9fa3), retaining Draft `0.1.0`. No internal schedule companion exists to align. Pending: Go reference update and an equal-endpoint case, the milestone manifest mapping, and downstream validation. The finding is not closed, and no platform, field or release support is claimed.
