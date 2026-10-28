# Specification Issue: NET-05 Declared Primitive Maxima

## Identity and Ownership

- Local finding: `GO-SPEC-ISSUE-021` in the Go [finding record](https://github.com/tv-rain/barometer-go/blob/agent/dev-687-net05-summed-maxima/docs/specification-issues.md#go-spec-issue-021-net-05-declared-primitive-maxima). The branch link is a proposed record, not immutable published evidence.
- Implementation task: [DEV-687 — Reject NET-05 profiles whose summed declared maxima exceed the composite limits at admission](https://app.clickup.com/t/124kk1zd4vp).
- Disposition: **Accepted; wording prepared, adoption pending.** The project owner, Lev, selected the declared-only rule on October 28, 2026 and authorized preparing the wording with the Go adoption. The wording is not accepted public behavior until it merges.
- Reporter: the Go implementation agent under the task owner's instruction. Public maintainers own disposition and wording; the Go implementation owner owns adoption.
- No duplicate identified. Related: [Bytes Counted Toward Attempt Byte Limits](attempt-byte-accounting.md) defines the counting boundary the sums use; [`editorial-consistency-0-1-0.md`](editorial-consistency-0-1-0.md) covers the DNS-01 window maximum, which bounds the duration a DNS-01 step declares; [`net-05-profile-input-bound.md`](net-05-profile-input-bound.md) covers a different NET-05 admission bound.

## Affected Baselines and Requirements

- Public `tv-rain/barometer-spec` revision [`9b220c436f6e429c971b2b6d82df28c20ab94579`](https://github.com/tv-rain/barometer-spec/tree/9b220c436f6e429c971b2b6d82df28c20ab94579), Draft `0.1.0`.
- Requirements:
  - [REQ-LIMIT-0020](https://github.com/tv-rain/barometer-spec/blob/9b220c436f6e429c971b2b6d82df28c20ab94579/library/registered-limits.md#REQ-LIMIT-0020): a profile is rejected before network activity if the sum of declared maxima cannot fit within the outer limits.
  - [REQ-NET-05-0026](https://github.com/tv-rain/barometer-spec/blob/9b220c436f6e429c971b2b6d82df28c20ab94579/tests/net-05.md#REQ-NET-05-0026): the declared primitive maxima must fit within 60,000 ms, 12 connections or tunnels, 65,536 application bytes sent and 262,144 received.
  - [REQ-NET-05-0037](https://github.com/tv-rain/barometer-spec/blob/9b220c436f6e429c971b2b6d82df28c20ab94579/tests/net-05.md#REQ-NET-05-0037) and [REQ-LIMIT-0019](https://github.com/tv-rain/barometer-spec/blob/9b220c436f6e429c971b2b6d82df28c20ab94579/library/registered-limits.md#REQ-LIMIT-0019): the composite limits, subject to stricter primitive and task bounds.
  - The resource-bound tables of [DNS-01](../tests/dns-01.md), [TCP-01](../tests/tcp-01.md), [TLS-01](../tests/tls-01.md) and [HTTP-01](../tests/http-01.md), the [DNS and HTTP limits](../library/registered-limits.md#dns-limits) and [REQ-TRUST-0047](../library/task-trust.md#REQ-TRUST-0047) for the rejection class.
- Implementation: `tv-rain/barometer-go` at [`9de36e3`](https://github.com/tv-rain/barometer-go/tree/9de36e35d7471543baf879b1b5d5646d134158fc) checks each primitive's own option bounds against the outer envelope and enforces the aggregate duration, connection and received-byte limits at run time. It does not sum declared maxima at admission, an approved deferral recorded as `CC-LIMIT-NET-05-COMPOSITE-LIMITS`. No native, binding or field support is established.

## Finding and Reproduction

REQ-LIMIT-0020 and REQ-NET-05-0026 require summing "declared maxima", but no primitive declares a maximum for every resource:

1. **Duration.** No primitive declares a duration; each runs "within the task deadline". The only declared duration is the DNS-01 `additional_response_window_ms`, at most 1,000 ms under the registered DNS limits, so eight steps declare at most 8,000 ms and the 60,000 ms composite limit cannot be reached from declarations.
2. **Bytes sent.** No primitive declares a sent maximum. DNS query and HTTP request sizes depend on the implementation, and TCP-01 and TLS-01 send no application data.
3. **Bytes received.** Derivable but unstated: HTTP-01 declares 16,384 response-header bytes and `max_body_bytes` for the terminal body, without saying whether the header bound applies to each redirect response; DNS-01 declares message maxima and a retained-response count per mode; the system resolver is not counted under REQ-LIMIT-0034.
4. **Connections.** Derivable but unstated: one per TCP-01, TLS-01, direct TCP DNS-01 and HTTP-01 request, including each permitted redirect.
5. **Class.** No row names the rejection class for an over-budget profile.

Two conforming implementations could therefore admit different profiles. Source-inspected reading of the public text, not an executed reproduction. **Blocked:** the summed-maxima admission check and the matching `M-NET-05-LIMITS` row. Run-time aggregate enforcement and unrelated NET-05 work are unaffected.

## Impact and Required Reviews

- **Safety and privacy:** the rule only rejects profiles before contact. It adds no destination, request, field, retained value or retry, and changes no registered number. Profiles that previously relied on the run-time meter alone may now be rejected earlier, which reduces approved traffic.
- **Interpretation:** an admission rejection produces no measurement and is not evidence of interference.
- **Compatibility:** Draft `0.1.0` is retained; no field, class or vocabulary is added. Admission narrows: for example, eight HTTP-01 steps following two redirects each declare 24 connections, and four HTTP-01 steps with 65,536-byte bodies declare 327,680 received bytes; both are rejected. Producers of large profiles need compatibility review.
- **Reviews:** public measurement and implementation maintainers review the table and class; a scoped resource review confirms that the rule only narrows admission. Reviews and assignments are pending.

## Alternatives and Selected Public Resolution

1. **Declared only (selected).** A step declares the amounts its primitive's registered limits and normalized `input` and `options` bound; undeclared resources add nothing and remain bounded at run time by the outer limits. Needs no implementation-specific numbers, rejects every profile whose declarations cannot fit, and keeps the run-time meter authoritative for the rest.
2. Assign registered defaults to undeclared resources (for example a fixed duration per step). Adds new registered numbers without evidence, and could reject ordinary profiles.
3. Use implementation-computed request sizes and timeouts. Makes admission differ between implementations.
4. Retain the current text. Implementations stay free to diverge.

Prepared wording: [REQ-LIMIT-0035](../library/registered-limits.md#REQ-LIMIT-0035), the next allocation above maximum 0034, with a per-step table, per-resource sums, comparison with the smaller of the composite limit and the task's `execution.limits` value, and rejection with `task_limit_exceeded` as part of `input` validation at admission step 8. REQ-LIMIT-0020 and REQ-NET-05-0026 gain editorial pointers and keep their IDs, because their obligation is unchanged. No requirement is retired. HTTP-01 counts 16,384 header bytes for every response its connection count permits; redirect response bodies are not declared.

Expected cases: 11, 12 and 13 declared connections; 262,143, 262,144 and 262,145 declared received bytes; task `max_connections`, `max_bytes_received` and `max_duration_ms` values below, at and above a profile's declared sums, each rejected atomically before contact with `task_limit_exceeded`. The 60,000 ms and 65,536-byte sent composite limits cannot be reached from declarations and have no admission case.

## Ordering and Public Disposition

No architecture or responsibility boundary changes, so no coordination decision is needed. Order: public review and merge of this wording; internal NET-05 and registered-limits review alignment; Go adoption under DEV-687, prepared on its branch for merge after this record; native and host validation before release. If the wording is deferred or rejected, the Go check stays unmerged and the deferral remains.

## Adoption and Closure Evidence

Prepared: REQ-LIMIT-0035, the editorial pointers, the catalog entry and this record. Pending: immutable public merge, review and alignment evidence, Go adoption commits and cases, compatibility confirmation and downstream validation. The finding is not closed, and no platform, field or release support is claimed.
