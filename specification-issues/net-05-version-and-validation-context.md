# Proposal: NET-05 Profile-Version Monotonicity and NET-03 Validation Context

**Disposition:** Accepted; adoption pending. The project owner selected alternative (a) for both findings on November 5, 2026. See the [disposition record](#disposition-record--november-5-2026).
**Date:** November 5, 2026

This record resolves two NET-05 rules that an implementation cannot satisfy without inventing observable behavior: who enforces the monotonic increase of `profile_version`, and where the `NET-03` validation context a profile may use comes from. It records the evidence, the alternatives and the selected disposition, and it accompanies the wording change that applies that disposition.

## Identity and Ownership

- Local findings: GO-SPEC-ISSUE-022 (profile-version monotonicity) and GO-SPEC-ISSUE-023 (NET-03 validation context) in the Go [specification-issue record](https://github.com/tv-rain/barometer-go/blob/main/docs/specification-issues.md), raised November 5, 2026 from the two NET-05 rows the Go implementation had recorded as approved deferrals.
- Public identity: this Markdown record, reviewed through a public PR. Responsible maintainer: the project owner, Lev.
- Reporter: the Go implementation agent under the task owner's instruction. Public maintainers own disposition and wording; the Go implementation owner owns adoption.
- Duplicates: none found. Related: [`require-validated-internal-check.md`](require-validated-internal-check.md), which removed library-originated traffic for deciding validation (REQ-EXECUTION-0033); [`net-05-declared-maxima.md`](net-05-declared-maxima.md), which bounds a profile's admission budget by its declared primitive steps (REQ-LIMIT-0035).

## Affected Baselines and Requirements

- Public Draft `0.1.0` at immutable revision [`c66a17005272d192b28072bb516f3afeae9e14d5`](https://github.com/tv-rain/barometer-spec/tree/c66a17005272d192b28072bb516f3afeae9e14d5). The affected rules are unchanged there since their allocation.
- Requirements:
  - [REQ-NET-05-0015](https://github.com/tv-rain/barometer-spec/blob/c66a17005272d192b28072bb516f3afeae9e14d5/tests/net-05.md#REQ-NET-05-0015): the `profile` object table constrains `profile_version` to be "Positive and monotonically increasing for a given `profile_id`."
  - [REQ-NET-05-0008](https://github.com/tv-rain/barometer-spec/blob/c66a17005272d192b28072bb516f3afeae9e14d5/tests/net-05.md#REQ-NET-05-0008): the probe "may use an available `NET-03` observation to retain validation or captive-portal context."
  - [REQ-NET-05-0009](https://github.com/tv-rain/barometer-spec/blob/c66a17005272d192b28072bb516f3afeae9e14d5/tests/net-05.md#REQ-NET-05-0009) step 4: "Obtain or reuse a sufficiently recent `NET-03` observation under local policy."
  - [REQ-NET-05-0043](https://github.com/tv-rain/barometer-spec/blob/c66a17005272d192b28072bb516f3afeae9e14d5/tests/net-05.md#REQ-NET-05-0043): `network_validation.source` is `fresh`, `cached` or `platform`.
  - Context only: [REQ-EXECUTION-0033](https://github.com/tv-rain/barometer-spec/blob/c66a17005272d192b28072bb516f3afeae9e14d5/data-formats/task-execution.md#REQ-EXECUTION-0033) (Barometer sends no traffic to decide validation) and [REQ-LIMIT-0035](https://github.com/tv-rain/barometer-spec/blob/c66a17005272d192b28072bb516f3afeae9e14d5/library/registered-limits.md#REQ-LIMIT-0035) (declared maxima come only from the profile's primitive steps). Neither is in question.
- Implementation: `tv-rain/barometer-go` at [`db100b4d6f4b2b23fbdd75f64cf5b6c01bead96d`](https://github.com/tv-rain/barometer-go/tree/db100b4d6f4b2b23fbdd75f64cf5b6c01bead96d) requires a positive `profile_version`, keeps no cross-task history, reports `source: platform` and obtains no `NET-03` observation, with synthetic tests only. No binding, native, host or platform behavior is implemented or validated.

## Finding and Reproduction

**Profile-version monotonicity.** The constraint names no scope (one issuer, one installation, one task store, all time), no rejection class, no persistence, and no clearing behavior. Enforcing it in the library needs durable per-profile history that outlives the task that introduced a version, in protected storage, with retention and clearing rules the contract does not give. Barometer keeps no admitted-task records across restarts, so any check would also be incomplete after a restart. Synthetic reproduction: two otherwise valid tasks with the same `profile_id`, the first with `profile_version: 5` and the second with `profile_version: 3`. REQ-NET-05-0015 reads as if the second must be rejected, but no rule says with which class, and an implementation that has cleared or never retained the first task cannot tell.

**NET-03 validation context.** REQ-NET-05-0008 permits using an available `NET-03` observation and REQ-NET-05-0009 step 4 requires obtaining or reusing a sufficiently recent one under local policy. The contract defines no local-policy field that provides one, no maximum age for reuse, no relationship to the network generation, and no accounting for a fresh `NET-03` run inside the profile's limits. A fresh run would add traffic outside the profile's declared primitive steps, which REQ-LIMIT-0035 does not count and REQ-EXECUTION-0033 avoids for validation. Synthetic reproduction: a profile run on a platform that reports `validated: yes`. Step 4 cannot be satisfied as written without choosing a cache, an age or an unaccounted request.

Observed behavior: the Go implementation keeps both rows as interim rules approved by its task owner: a positive `profile_version` without cross-task history, and platform validation context with `source: platform` and no `NET-03` request.

Affected work: the nonmonotone-version row of the NET-05 admission plan and the fresh and cached rows of the NET-05 execution plan. Other NET-05 work is unaffected.

## Impact and Required Reviews

- Safety/privacy: the selected rules add no traffic, destination, identifier, stored record or retained field. A durable version history (rejected alternative (b) below) would add persisted per-issuer state needing a privacy review and clearing rules; a fresh `NET-03` pre-step (rejected alternative (c)) would add traffic needing a safety review. Neither is introduced.
- Resource bounds: unchanged. No `NET-03` traffic is added to the profile, so REQ-LIMIT-0035 and the composite limits remain complete.
- Measurement/interpretation: a retained `profile_version` is the issuer's value and is not evidence that monotonicity was checked; correlation across versions relies on issuer discipline. Validation context is the platform's own state, which can be wrong or unavailable; a profile that does not run because platform validation is negative or unknown is not evidence of censorship, and captive portals, outages and platform behavior remain alternative explanations.
- Compatibility: Draft `0.1.0` is retained. No field is added or removed; `fresh` and `cached` stay in the `source` schema as reserved values. An implementation that rejected a lower version or emitted `fresh` or `cached` would change behavior.
- Required reviews: public maintainer disposition. No safety or privacy review applies to the selected rules, because they add no traffic, state or field.

## Alternatives and Proposed Public Resolution

Profile-version monotonicity (GO-SPEC-ISSUE-022):

1. **(a) Issuer authoring obligation.** Monotonic increase is the issuer's obligation; Barometer validates only a positive integer and keeps no cross-task history. Adds no state and matches current Go behavior.
2. **(b) Durable library history.** Keep the highest version per issuer and `profile_id` in protected storage and reject a task whose version is not higher. Needs new persisted state, a scope, a rejection class, a privacy review and clearing rules.
3. **Retain the current text.** Leaves enforcement undefined.

NET-03 validation context (GO-SPEC-ISSUE-023):

1. **(a) Platform context only in this version.** Local policy provides no `NET-03` reuse and Barometer sends no traffic to obtain one; `source` is `platform`, and `fresh` and `cached` remain reserved. Consistent with REQ-EXECUTION-0033 and REQ-LIMIT-0035; matches current Go behavior.
2. **(b) In-memory same-generation reuse.** Reuse a `NET-03` result from the same network generation within a new registered maximum age. Needs the age, the generation rule and a local-policy surface.
3. **(c) Fresh `NET-03` pre-step.** Run `NET-03` before the first step and count it in the declared maxima. Adds traffic outside the profile's primitives and needs a safety review.
4. **Retain the current text.** Leaves step 4 unsatisfiable without inventing behavior.

## Ordering and Public Disposition

- Coordination decision: not needed; no responsibility boundary changes.
- Public review: this record and the wording change, reviewed through one public PR. Maintainer disposition: see below.
- Order: merge this change and record its immutable revision; align the internal NET-05 validation plan; adopt in Go with its cases and update GO-SPEC-ISSUE-022 and GO-SPEC-ISSUE-023; then bindings and hosts.

## Adoption and Closure Evidence

- Accepted public baseline: the merge of this change; requirement links below.
- Internal alignment, Go adoption evidence, and binding and host adoption: pending.
- Closure requires the merged revision, internal alignment and Go adoption evidence. No runtime, platform, field or release support is claimed.

## Disposition Record — November 5, 2026

- **Disposition:** the project owner, Lev, selected alternative (a) for both findings.
- **Profile version:** [REQ-NET-05-0062](../tests/net-05.md#REQ-NET-05-0062) and [REQ-NET-05-0063](../tests/net-05.md#REQ-NET-05-0063) replace REQ-NET-05-0015, which is retired because removing library enforcement of monotonicity changes the acceptance boundary. The `profile_id` and `steps` rows are unchanged.
- **Validation context:** [REQ-NET-05-0064](../tests/net-05.md#REQ-NET-05-0064) and [REQ-NET-05-0066](../tests/net-05.md#REQ-NET-05-0066) replace REQ-NET-05-0008, and [REQ-NET-05-0065](../tests/net-05.md#REQ-NET-05-0065) replaces REQ-NET-05-0009, whose step 4 changes; both are retired because a permitted and a required behavior are removed. REQ-NET-05-0043 keeps its ID: its values are unchanged and its description gains an editorial pointer to REQ-NET-05-0066. The partial-result example now shows `source: platform`.
- **Rationale:** the specification names no scope, rejection class, persistence or clearing behavior for monotonicity, and Barometer keeps no admitted-task records across restarts. No local-policy reuse, maximum age or traffic accounting exists for a `NET-03` observation, and obtaining one would add traffic outside the profile's declared primitive steps, contrary to the approach of REQ-EXECUTION-0033 and REQ-LIMIT-0035. Rejected: (b) durable per-issuer, per-profile history (new persisted state, privacy review, clearing rules); for the context, (b) in-memory same-generation reuse with a new registered maximum age, and (c) a fresh `NET-03` pre-step counted in the declared maxima (new traffic, safety review).
- **Version:** Draft `0.1.0` is retained; no field is added or removed.
- **Reviews:** maintainer disposition only; the selected rules add no traffic, state or field.
- **Remaining:** merged revision, internal alignment, Go adoption, then binding and host adoption. The findings are not closed.
