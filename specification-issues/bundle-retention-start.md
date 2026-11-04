# Specification Issue: Start of Unacknowledged Bundle Retention

## Identity and Ownership

- Local finding: `GO-SPEC-ISSUE-012` in the Go [finding record](https://github.com/tv-rain/barometer-go/blob/d3886377ea48ff30cdac845b0de30b6917d44256/docs/specification-issues.md#go-spec-issue-012-start-of-unacknowledged-bundle-retention), raised October 22, 2026 while implementing the pending-result store.
- Disposition: **Accepted; wording prepared as REQ-BUNDLE-0037, merge pending; privacy review drafted, sign-off pending.** The project owner, Lev, selected retention from the first persisted result on November 4, 2026.
- Reporter: the Go implementation agent under the task owner's instruction. Public maintainers own disposition and wording; the Go implementation owner owns adoption.
- No duplicate identified. Related: none.

## Affected Baselines and Requirements

- Public `tv-rain/barometer-spec` revision [`2696742b9ea90468842cfa81d2dd5038c960a611`](https://github.com/tv-rain/barometer-spec/tree/2696742b9ea90468842cfa81d2dd5038c960a611), Draft `0.1.0`.
- Requirements: [REQ-LIMIT-0023](../library/registered-limits.md#REQ-LIMIT-0023) sets "Unacknowledged local bundle retention" to at most 86,400 seconds; [REQ-LIMIT-0024](../library/registered-limits.md#REQ-LIMIT-0024) deletes expired pending bundles rather than uploading them late; [REQ-BUNDLE-0015](../data-formats/result-bundle.md#REQ-BUNDLE-0015) step 8 deletes the local bundle "after at most 86,400 seconds without acknowledgement", after steps 1 to 5 finish the selected attempts, generate the identifier and persist the bundle. None says when the 86,400 seconds start.
- Implementation: `tv-rain/barometer-go` at [`d388637`](https://github.com/tv-rain/barometer-go/tree/d3886377ea48ff30cdac845b0de30b6917d44256) implements the selected rule in its pending-result store with synthetic tests only. No binding, native, host or platform behavior is implemented or validated.

## Finding and Reproduction

Results wait locally before their logical bundle is complete. The 86,400 seconds could start when a result is first persisted, when the complete bundle is encoded and persisted with its identifier (step 5), or when the bundle is first submitted or offered to the host. The later readings let a result stay on the device longer than 86,400 seconds, by as long as its bundle stays open, and the reading changes when data is deleted. The contract also defines no separate retention for results not yet in a bundle.

Synthetic reproduction: a result is persisted at *t*, a second result joins the same bundle at *t* + 80,000 seconds, and the bundle is first offered at *t* + 82,000 seconds. Starting at the first result deletes the bundle at *t* + 86,400 seconds; starting at step 5 or at the first offer keeps the first result until about *t* + 166,400 or *t* + 168,400 seconds.

**Blocked:** nothing; Go implemented the most conservative reading as an interim rule. **Interim handling:** retention starts when a bundle's first result is persisted. **Unaffected:** acknowledgement deletion and the bundle count and byte limits.

## Impact and Required Reviews

- **Privacy:** the start decides how long measurement results stay on the device. The selected rule never retains a result longer than any other reading allows, and no identifier, field or destination changes. Its cost is that a result added late to a bundle is deleted sooner than 86,400 seconds after its own persistence.
- **Interpretation:** a result deleted before delivery is missing data, not a measurement outcome, and carries no interpretation.
- **Compatibility:** no field, class or registered number changes; Draft `0.1.0` is retained. An implementation that started retention later would delete data earlier under this rule.
- **Reviews:** maintainer disposition recorded above. A scoped **privacy review of the selected rule** is drafted in the internal registered-limits review and awaits sign-off by a reviewer other than the drafting agent. It is not complete.

## Alternatives and Selected Public Resolution

1. **From the first persisted result (selected).** Matches current Go behavior; every result is deleted at most 86,400 seconds after it was first persisted.
2. **From the final persistence of the complete bundle (step 5).** A result can wait for as long as its bundle stays open plus 86,400 seconds.
3. **From the first submission or offer to the host.** The longest retention of the options.
4. **Per result, from each result's own persistence.** Needs per-result expiry inside a bundle, which conflicts with exact retransmission of immutable bundle bytes under REQ-BUNDLE-0015 step 7.

The selected rule is prepared as [REQ-BUNDLE-0037](../data-formats/result-bundle.md#REQ-BUNDLE-0037), the next allocation above maximum 0036. REQ-BUNDLE-0015 step 8 and REQ-LIMIT-0024 gain editorial pointers to it and keep their IDs: the rule defines a start they left open and does not change the 86,400-second bound. No requirement is retired.

Expected cases: a bundle expires exactly 86,400 seconds after its first result was persisted; adding a result, sealing the bundle, returning it to the host or restarting does not move that time; an expired bundle is deleted and never returned; a failed expiry deletion fails the access rather than returning the bundle.

## Ordering and Public Disposition

No architecture or responsibility boundary changes, so no coordination decision is needed. Order: public review and merge of this wording; privacy review sign-off and internal registered-limits review alignment; Go reference update and retention cases; native and host validation before release.

## Adoption and Closure Evidence

Pending: immutable public merge, privacy review sign-off, the Go reference update and retention cases, the milestone manifest mapping, and downstream validation. The finding is not closed, and no platform, field or release support is claimed.
