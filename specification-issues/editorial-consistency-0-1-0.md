# Proposal: Draft 0.1.0 Editorial Consistency Corrections

**Disposition:** Open (proposal; no specification text changed)
**Date:** October 16, 2026
**Related task:** [DEV-573 — Record DEV-572 specification ambiguities as Go findings and an editorial proposal](https://app.clickup.com/t/124kk1zc613)

This record asks public maintainers to correct three inconsistencies between test specifications and shared contracts in Draft `0.1.0`. In each case an existing rule already determines the behavior, so the proposal changes no observable behavior. It proposes wording only; the normative files are unchanged until maintainers approve a separate change.

## Identity and Ownership

- **Origin:** the October 16, 2026 triage of public-text ambiguities found while drafting Go conformance case plans under [DEV-572](https://app.clickup.com/t/124kk1zc5xp). The Go findings that need behavior decisions are recorded separately as GO-SPEC-ISSUE-004 to GO-SPEC-ISSUE-007 in the Go [specification-issue record](https://github.com/tv-rain/barometer-go/blob/main/docs/specification-issues.md). These three items have no local Go finding ID because none blocks implementation.
- **Public identity:** this Markdown record, once reviewed through a public PR.
- **Reporter:** the Go implementation agent, under the task owner's instruction. Public maintainers own disposition and wording.
- **Duplicates:** none found. [Observation vocabularies](observation-vocabularies.md) changed shared observation text but does not cover these test-level tables.

## Affected Baselines and Requirements

- **Public baseline:** Draft `0.1.0` at [`fca4bf63ff5f8405f12d64eaccab3f193cbe04e2`](https://github.com/tv-rain/barometer-spec/tree/fca4bf63ff5f8405f12d64eaccab3f193cbe04e2). The cited test sections are unchanged since the registered-test baseline [`59d49364d85e48cc8e69c762d130a7a86dc1fe65`](https://github.com/tv-rain/barometer-spec/tree/59d49364d85e48cc8e69c762d130a7a86dc1fe65).
- **Item 1, DNS-01 window maximum:**
  - [REQ-DNS-01-0025](https://github.com/tv-rain/barometer-spec/blob/fca4bf63ff5f8405f12d64eaccab3f193cbe04e2/tests/dns-01.md#REQ-DNS-01-0025) allows `additional_response_window_ms` from `1` through `10,000`.
  - [REQ-LIMIT-0014](https://github.com/tv-rain/barometer-spec/blob/fca4bf63ff5f8405f12d64eaccab3f193cbe04e2/library/registered-limits.md#REQ-LIMIT-0014) sets the additional-response observation window maximum to 1,000 ms.
  - [REQ-LIMIT-0001](https://github.com/tv-rain/barometer-spec/blob/fca4bf63ff5f8405f12d64eaccab3f193cbe04e2/library/registered-limits.md#REQ-LIMIT-0001) makes the registry canonical unless a test defines a stricter value, and [REQ-LIMIT-0002](https://github.com/tv-rain/barometer-spec/blob/fca4bf63ff5f8405f12d64eaccab3f193cbe04e2/library/registered-limits.md#REQ-LIMIT-0002) requires rejecting a task above a registered limit.
- **Item 2, `network_changed` in failure-class tables:**
  - The failure-class tables REQ-NET-01-0009, REQ-NET-03-0008, REQ-DNS-01-0013, REQ-DNS-03-0008, REQ-DNS-04-0008, REQ-TCP-01-0009, REQ-TLS-01-0008 and REQ-HTTP-01-0009 each list `network_changed`.
  - Each test's termination rule (REQ-NET-01-0027, REQ-NET-03-0029, REQ-DNS-01-0039, REQ-DNS-03-0028, REQ-DNS-04-0028, REQ-TCP-01-0026, REQ-TLS-01-0027, REQ-HTTP-01-0038) maps it to an incomplete execution state. Several also say it is not a test outcome.
  - [REQ-OBS-0016](https://github.com/tv-rain/barometer-spec/blob/fca4bf63ff5f8405f12d64eaccab3f193cbe04e2/data-formats/measurement-observations.md#REQ-OBS-0016) assigns network change to `execution.reason`, not to observation failure lists.
  - NET-05 already states the mapping explicitly in [REQ-NET-05-0047](https://github.com/tv-rain/barometer-spec/blob/fca4bf63ff5f8405f12d64eaccab3f193cbe04e2/tests/net-05.md#REQ-NET-05-0047) and is not affected.
- **Item 3, address prohibitions and DNS answers:**
  - [REQ-OBS-0012](https://github.com/tv-rain/barometer-spec/blob/fca4bf63ff5f8405f12d64eaccab3f193cbe04e2/data-formats/measurement-observations.md#REQ-OBS-0012) retains canonical public IP addresses as `A`/`AAAA` answer values.
  - [REQ-NET-03-0030](https://github.com/tv-rain/barometer-spec/blob/fca4bf63ff5f8405f12d64eaccab3f193cbe04e2/tests/net-03.md#REQ-NET-03-0030) prohibits the validation address, [REQ-HTTP-01-0039](https://github.com/tv-rain/barometer-spec/blob/fca4bf63ff5f8405f12d64eaccab3f193cbe04e2/tests/http-01.md#REQ-HTTP-01-0039) prohibits the destination address, and [REQ-DNS-03-0029](https://github.com/tv-rain/barometer-spec/blob/fca4bf63ff5f8405f12d64eaccab3f193cbe04e2/tests/dns-03.md#REQ-DNS-03-0029) prohibits the resolver address. Those addresses are what an internal DNS stage (or the DNS-03 bootstrap lookup) would return as answers.
  - Only the HTTP-01 output example shows the intended result, a `dns_query` with `responses: []`.
- **Implementation:** no Go runner for these tests exists at `tv-rain/barometer-go` `58e03a1f65600371960f735595f0a3c84550611f`. Nothing is implemented or validated.

## Finding and Reproduction

- **Documented rules and conflict:** in each item, a test-level table or example disagrees with, or only implies, a shared rule. A reader who follows the local text alone could accept a 10,000 ms window, emit `network_changed` as an observation failure, or retain a prohibited address as a DNS answer.
- **Existing resolution:** REQ-LIMIT-0001/0002 make the 1,000 ms registry value control. The termination rules and REQ-OBS-0016 make `network_changed` an execution reason. The test-specific prohibitions are stricter than REQ-OBS-0012 and apply to those tests' results.
- **Reproduction:** text comparison only. No runtime evidence is involved.
- **Blocked work:** none. Implementations follow the existing rules above.

## Impact and Required Reviews

- **Safety/privacy:** Item 3 prevents accidental retention of destination or resolver addresses; Item 1 prevents a longer listening window than the registry allows. Both clarifications tighten the reading of the current text. No new data, destinations or traffic.
- **Measurement/interpretation:** none. Item 2 keeps interruptions separate from protocol observations, as the shared format already requires.
- **Compatibility:** no conforming behavior changes. A task with a window above 1,000 ms is already rejected under REQ-LIMIT-0002.
- **Reviews:** public maintainer review of the wording. Privacy review should confirm Item 3. No platform-policy, legal or deployment review applies, because behavior does not change.

## Alternatives and Proposed Public Resolution

- **Alternative:** keep the current text and rely on the shared rules. Rejected because each item invites a non-conforming reading.
- **Proposed wording, Item 1:** in REQ-DNS-01-0025, change the constraint to "Required when additional-response collection is enabled; `1` through `1,000`, the registered maximum." The phrase "registered maximum" would link to REQ-LIMIT-0014.
- **Proposed wording, Item 2:** after each listed failure-class table, add: "`network_changed` is a termination condition, not an observation failure value; it is represented as described in Outcomes." The word "Outcomes" would link to that test's Outcomes section. Alternatively, remove the row and keep the termination rule. Maintainers choose one form for all eight tests.
- **Proposed wording, Item 3:** in REQ-NET-03-0030, REQ-HTTP-01-0039 and REQ-DNS-03-0029, add: "A `dns_query` observation made by this test retains no `A` or `AAAA` answer containing a prohibited address; its `responses` array is empty when every answer would be prohibited."
- **Requirement IDs and version:** the IDs stay the same as editorial corrections, and the Draft `0.1.0` version stays the same, subject to maintainer review.
- **Expected cases:** existing planned Go cases already follow the shared rules. No case result changes.

## Ordering and Public Disposition

- **Coordination decision:** none needed. No responsibility boundary changes.
- **Public review:** this record, then a separate maintainer-approved wording PR if accepted.
- **Downstream:** no internal alignment, Go behavior, binding or host change is expected. Go case-plan text may cite the new wording after it merges.
- **If rejected or deferred:** the current shared rules continue to control, and the inconsistencies remain documented here.

## Adoption and Closure Evidence

- **Accepted baseline:** pending.
- **Review alignment:** not applicable unless maintainers change behavior.
- **Implementation evidence:** not applicable; no Go behavior depends on this proposal.
- **Closure:** requires the maintainer disposition and, if wording changes, the merged immutable revision.
