# Proposal: NET-05 Profile Bound Inside the Common Input Bound

**Disposition:** Open (proposal; no specification text changed)
**Date:** October 27, 2026
**Related task:** [DEV-670 — Close out the Measurement web reachability and composite sub-epic](https://app.clickup.com/t/124kk1zcw50)

This record asks public maintainers to state how the NET-05 encoded `profile` bound relates to the common `input` bound. Both are 49,152 bytes, and the `profile` is one member of `input`, so a `profile` at its own registered maximum always makes `input` exceed its maximum. The record lists alternatives and does not select one. The normative files are unchanged until maintainers approve a separate change.

## Identity and Ownership

- Local finding: GO-SPEC-ISSUE-018 in the Go [specification-issue record](https://github.com/tv-rain/barometer-go/blob/main/docs/specification-issues.md), raised October 27, 2026 under DEV-670 from the closeout coverage check of the NET-05 admission and limits families.
- Public identity: this Markdown record, once reviewed through a public PR. Responsible maintainer: the project owner, Lev.
- Reporter: the Go implementation agent under the task owner's instruction. Public maintainers own disposition and wording; the Go implementation owner owns adoption, followed by [DEV-658 — Coverage completion](https://app.clickup.com/t/124kk1zcw4g).
- Duplicates: none found. Related: [`editorial-consistency-0-1-0.md`](editorial-consistency-0-1-0.md), which proposes corrections where a test-level value conflicts with a shared rule.

## Affected Baselines and Requirements

- Public Draft `0.1.0` at immutable revision [`e6257ec64564ad415a2d6c1f8d106fa1763d7de8`](https://github.com/tv-rain/barometer-spec/tree/e6257ec64564ad415a2d6c1f8d106fa1763d7de8).
- Requirements:
  - [REQ-INPUT-0007](https://github.com/tv-rain/barometer-spec/blob/e6257ec64564ad415a2d6c1f8d106fa1763d7de8/data-formats/task-input.md#REQ-INPUT-0007): the complete `input` object must not exceed 49,152 encoded UTF-8 bytes. The registered-limits table repeats this maximum for test-specific `input` JSON.
  - [REQ-NET-05-0025](https://github.com/tv-rain/barometer-spec/blob/e6257ec64564ad415a2d6c1f8d106fa1763d7de8/tests/net-05.md#REQ-NET-05-0025): the encoded `profile` must not exceed 49,152 bytes. [REQ-LIMIT-0019](https://github.com/tv-rain/barometer-spec/blob/e6257ec64564ad415a2d6c1f8d106fa1763d7de8/library/registered-limits.md#REQ-LIMIT-0019) registers the same maximum for the encoded `profile` object.
- Implementation: `tv-rain/barometer-go` at [`e2cb97361307914ed5bec52a6fa36745e81b5435`](https://github.com/tv-rain/barometer-go/tree/e2cb97361307914ed5bec52a6fa36745e81b5435) applies both bounds, with synthetic tests only.

## Finding and Reproduction

NET-05 `input` is an object whose `profile` member holds the profile. The smallest wrapper, `{"profile":` and `}`, adds 12 bytes, so the largest admissible `profile` is 49,140 bytes. REQ-NET-05-0025 and REQ-LIMIT-0019 never decide admission at or near their stated maximum, and nothing says whether that is intended.

Synthetic reproduction: a NET-05 task whose encoded `profile` is exactly 49,152 bytes, padded with insignificant whitespace, otherwise valid. The `profile` satisfies REQ-NET-05-0025; the `input` is 49,164 bytes and fails REQ-INPUT-0007. Go rejects it with `task_limit_exceeded` before contact (`TestMNet05Admission` checks 49,151, 49,152 and 49,153 bytes).

Observed behavior: Go applies the common `input` bound first and the `profile` bound second, so the stricter common bound decides. This conforms to both rules as written and adds no traffic or resource allowance. It is not accepted public behavior for the intended relationship.

Unresolved: whether the `profile` maximum was meant to leave headroom inside `input`, to raise the `input` maximum for NET-05, or to equal it by mistake.

## Impact and Required Reviews

- Safety/privacy: none under the current behavior; every case is rejected at admission before network activity. Raising any maximum would increase memory, decoding and storage bounds and needs a maintainer review of those bounds.
- Interoperability: producers that size profiles to 49,152 bytes are rejected. An implementation that checks only the `profile` bound would admit a task another implementation rejects.
- Conformance: a `profile` boundary case at 49,152 bytes cannot be admitted, so the NET-05 limits family can test that boundary only for rejection.
- Required reviews: public maintainer disposition. No other review is identified for alternatives (a) and (b).

## Alternatives and Proposed Public Resolution

1. **(a) Lower the `profile` maximum** so it fits inside REQ-INPUT-0007 with the wrapper, for example to 49,140 bytes, or state that the `profile` bound applies in addition to REQ-INPUT-0007 and the stricter one decides. Matches current Go behavior; no compatibility change for conforming producers.
2. **(b) No text change.** Maintainers confirm that both bounds apply and the common bound decides, citing the existing rules. Leaves REQ-NET-05-0025 as a bound that never decides.
3. **(c) Raise the NET-05 `input` maximum** so a 49,152-byte `profile` is admissible. Allows larger profiles at the cost of a larger decoding bound and a change to the registered common limit for one test; needs a version or compatibility decision.

Proposed exact wording: none; maintainers select the rule and wording.

## Ordering and Public Disposition

- Coordination decision: not needed.
- Order after disposition: merge any accepted wording and record its immutable revision; align the internal NET-05 validation plan; adopt in Go and update GO-SPEC-ISSUE-018 and the NET-05 limits case plan; then bindings and hosts.
- Interim: Go keeps applying both bounds.

## Adoption and Closure Evidence

Pending: maintainer disposition, merged wording or no-text-change citation, internal alignment, Go adoption evidence or recorded conformance. No runtime, platform, field or release support is claimed.
