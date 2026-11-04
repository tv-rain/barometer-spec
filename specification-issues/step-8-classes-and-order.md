# Specification Issue: Unnamed Classes and Order in Step-8 Input and Options

## Identity and Ownership

- Local finding: `GO-SPEC-ISSUE-016` items 1 to 3 in the Go [finding record](https://github.com/tv-rain/barometer-go/blob/54feb7d76c3ef52b2746e02ae6df67b424c86629/docs/specification-issues.md#go-spec-issue-016-unnamed-classes-and-order-in-step-8-input-and-options), raised October 26, 2026 under DEV-663 from the maintainer safety review of the GO-SPEC-ISSUE-010 mapping. Item 4 is a Go codec-contract gap, not a public ambiguity, and is out of scope.
- Public record task: [DEV-716 — Public records for the remaining Go specification findings](https://app.clickup.com/t/124kk1zdmdq).
- Disposition: **Accepted; wording merged as REQ-TRUST-0057 to REQ-TRUST-0059 at `830e956`, internal alignment merged; Go reference update and cases pending.** The project owner, Lev, selected the current Go interim rules on November 4, 2026.
- Reporter: the Go implementation agent under the task owner's instruction. Public maintainers own disposition and wording; the Go implementation owner owns adoption.
- No duplicate identified. Related: [Step-8 Input and Options Admission Class](step-8-input-options-admission-class.md) named the classes this record extends; [Proxy Compatibility Admission Class](proxy-compatibility-admission-class.md) orders proxy compatibility after input and options.

## Affected Baselines and Requirements

- Public `tv-rain/barometer-spec` revision [`a46555b0a8c6500d5002e3768e76f2ddb38c67e6`](https://github.com/tv-rain/barometer-spec/tree/a46555b0a8c6500d5002e3768e76f2ddb38c67e6), Draft `0.1.0`.
- Requirements: [REQ-TRUST-0056](../library/task-trust.md#REQ-TRUST-0056) (step-8 classes), [REQ-OPTIONS-0033](../data-formats/task-options.md#REQ-OPTIONS-0033) (local-policy option refusal), [REQ-TRUST-0047](../library/task-trust.md#REQ-TRUST-0047) (condition-to-class table), [REQ-TRUST-0036](../library/task-trust.md#REQ-TRUST-0036), [REQ-TRUST-0039](../library/task-trust.md#REQ-TRUST-0039) and [REQ-LIMIT-0002](../library/registered-limits.md#REQ-LIMIT-0002).
- Implementation: `tv-rain/barometer-go` at [`54feb7d`](https://github.com/tv-rain/barometer-go/tree/54feb7d76c3ef52b2746e02ae6df67b424c86629) applies the interim rules for items 2 and 3 in admission, recorded by `TestGateInputOptionsClasses`; it has no local option restriction for item 1. No native, binding or field support is established.

## Finding and Reproduction

1. **Local-policy option restrictions.** REQ-OPTIONS-0033 sends an option local policy does not permit to the class REQ-TRUST-0047 lists for that condition, but REQ-TRUST-0047 lists local-policy refusal only for the network path at step 8 and the risk bound at step 9.
2. **Registered numeric limits on values.** REQ-TRUST-0056 names `task_limit_exceeded` only for byte limits, so a value above a registered numeric maximum, such as a DNS-01 `additional_response_window_ms` above its registered maximum, reads as a value the schema does not permit. REQ-LIMIT-0002 requires rejection without naming a class.
3. **Order among several failing values.** Nothing orders `input` against `options` or one member against another, so a task with invalid `input` and an over-limit option can receive either class.

These are source-inspected readings, with synthetic Go cases for items 2 and 3 only. **Blocked:** exact-class conformance assertions for these cases. **Interim handling:** Go returns `task_limit_exceeded` for item 2 and validates `input` before `options`, members in their presented order, for item 3. **Unaffected:** the rows REQ-TRUST-0056 names, proxy compatibility, path authority, target registration and composite rows.

## Impact and Required Reviews

- **Safety and privacy:** every case is rejected at admission before network activity; only the class differs. The rules add no traffic, field or retained value. Hosts and issuers that branch on classes no longer diverge between implementations.
- **Interpretation:** admission classes are operational states, not measurements or evidence of censorship (REQ-TRUST-0033).
- **Compatibility:** no new class or field; Draft `0.1.0` is retained. An implementation that returned `task_schema_invalid` for a registered numeric limit changes to `task_limit_exceeded`.
- **Reviews:** the maintainer safety review of the GO-SPEC-ISSUE-010 mapping suggested `task_issuer_not_authorized` for item 1. No further safety or privacy review is identified, because the rules change only which class a rejected task receives.

## Alternatives and Selected Public Resolution

- Item 1: `task_issuer_not_authorized` (**selected**, as for the step-8 local-policy path row), `task_schema_invalid`, or `task_unsupported`.
- Item 2: `task_limit_exceeded` (**selected**, consistent with the class name and with step 5 and REQ-TRUST-0056), or `task_schema_invalid`.
- Item 3: `input` before `options`, members in presented order (**selected**); limit failures before content failures across the whole step; or an explicit implementation choice.

The selected rules are prepared as [REQ-TRUST-0057](../library/task-trust.md#REQ-TRUST-0057) (item 1), [REQ-TRUST-0058](../library/task-trust.md#REQ-TRUST-0058) (item 2) and [REQ-TRUST-0059](../library/task-trust.md#REQ-TRUST-0059) (item 3), the next allocations above maximum 0056. REQ-OPTIONS-0033 and REQ-LIMIT-0002 gain editorial pointers and keep their IDs. REQ-TRUST-0059 keeps the byte-limit-first rule of REQ-TRUST-0056 and places normalization, including REQ-INPUT-0014 and the NET-05 declared maxima, after the `input` and `options` schema checks.

Expected cases: a locally restricted option value yields `task_issuer_not_authorized`; an option at a registered maximum is admitted and one above it yields `task_limit_exceeded`; invalid `input` with an over-limit option yields `task_schema_invalid`; an over-limit option with `input` that cannot be normalized yields `task_limit_exceeded`; the first of two failing members in presented order decides.

## Ordering and Public Disposition

No architecture or responsibility boundary changes, so no coordination decision is needed. Order: public review and merge of this wording; internal task-trust review alignment; Go reference update with exact-class cases and, when a local option restriction exists, its case; then bindings and hosts.

## Adoption and Closure Evidence

Merged: REQ-TRUST-0057 to REQ-TRUST-0059, the catalog entries, the editorial pointers and this record through [public PR #39](https://github.com/tv-rain/barometer-spec/pull/39) at [`830e956`](https://github.com/tv-rain/barometer-spec/tree/830e9564849ebfedaa0860d9f01032574e2b9fa3), retaining Draft `0.1.0`. Internal task-trust alignment merged through internal PR #19 at `a884513`. Pending: Go reference update and exact-class cases, the milestone manifest mapping, and downstream validation. The finding is not closed, and no platform, field or release support is claimed.
