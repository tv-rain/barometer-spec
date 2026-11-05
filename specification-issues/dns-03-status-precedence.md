# Specification Issue: DNS-03 Non-Success Status and Media-Type Precedence

## Identity and Ownership

- Local finding: `GO-SPEC-ISSUE-020` in the Go [finding record](https://github.com/tv-rain/barometer-go/blob/54feb7d76c3ef52b2746e02ae6df67b424c86629/docs/specification-issues.md#go-spec-issue-020-dns-03-non-success-status-and-media-type-precedence).
- Disposition: **Accepted; wording merged as REQ-DNS-03-0040 at `830e956`, internal alignment merged, adopted in Go with its reference update; binding and host adoption pending.** The project owner, Lev, selected the rule on October 27, 2026.
- Reporter: the Go implementation agent under the task owner's instruction. Public maintainers own disposition and wording; the Go implementation owner owns adoption.
- No duplicate identified. Related: [HTTP-01 Terminal Response Outcome Precedence](http-01-outcome-precedence.md) settles the analogous question for HTTP-01 only.

## Affected Baselines and Requirements

- Public `tv-rain/barometer-spec` revision [`f889a381c84a781176024f3fed3a3d4f5c92b241`](https://github.com/tv-rain/barometer-spec/blob/f889a381c84a781176024f3fed3a3d4f5c92b241/tests/dns-03.md), DNS-03 Draft `0.1.0`, unchanged through [`a46555b`](https://github.com/tv-rain/barometer-spec/tree/a46555b0a8c6500d5002e3768e76f2ddb38c67e6).
- Requirements: [REQ-DNS-03-0006](../tests/dns-03.md#REQ-DNS-03-0006) (validate the HTTP response before parsing), [REQ-DNS-03-0008](../tests/dns-03.md#REQ-DNS-03-0008) (`http_failure` and `unexpected_content_type` failure rows), [REQ-DNS-03-0012](../tests/dns-03.md#REQ-DNS-03-0012) (redirect targets not contacted) and [REQ-DNS-03-0027](../tests/dns-03.md#REQ-DNS-03-0027) (outcomes).
- Implementation: `tv-rain/barometer-go` at [`54feb7d`](https://github.com/tv-rain/barometer-go/tree/54feb7d76c3ef52b2746e02ae6df67b424c86629) applies the selected rule in `internal/protocol/http` (`evaluate`, `Exchange`) and `internal/measurement/dns03`, with synthetic cases including `TestPOSTStatusPrecedesMediaType`. No native, binding or field support is established.

## Finding and Reproduction

REQ-DNS-03-0008 defines `http_failure` as a failed exchange or "a non-success status that does not contain a DNS response", and `unexpected_content_type` as a response that "is not a supported DNS message media type". A synthetic `503` response with `Content-Type: text/html` satisfies both rows. The text also does not say whether a non-2xx response declaring `application/dns-message` is parsed. REQ-DNS-03-0006 orders HTTP validation before DNS parsing without ordering the checks inside the HTTP stage.

Before adoption, the shared Go exchange checked the media type of every response regardless of status, so the `503` page would have been `unexpected_content_type`. **Blocked:** exact conformance assertions for overlapping status and media-type failures until this wording merges. **Unaffected:** every other DNS-03 path.

## Impact and Required Reviews

- **Safety and privacy:** the rule adds no traffic, read, retry, field or retained value. It reads less of a non-2xx response than the alternatives: the body is not read and a redirect `Location` is neither classified nor contacted.
- **Interpretation:** a non-2xx status from a DoH resolver can come from resolver overload, CDN faults, rate limiting or a middlebox; `http_failure` with the retained status leaves those explanations open. A non-2xx body is not interpreted as DNS data, even when it is labeled as such.
- **Compatibility:** no field, vocabulary or bound changes; Draft `0.1.0` is retained. An implementation that parsed non-2xx `application/dns-message` bodies or reported `unexpected_content_type` for non-2xx responses changes.
- **Reviews:** the owner-selected rule was reviewed for unchanged traffic and minimization with the Go DNS-03 runner. Public measurement maintainer review is recorded by this disposition; no further specialist review is identified.

## Alternatives and Selected Public Resolution

1. **Status first (selected).** Any non-2xx response is `http_failure`, with no media-type check, body read or parse; only 2xx responses are checked for media type and parsed.
2. **Media type first.** A non-2xx response with an unsupported media type is `unexpected_content_type`. Reports a less useful class for ordinary error pages.
3. **Parse any `application/dns-message` body.** Interprets data that a failing server labels as DNS, reads more and adds ambiguity between HTTP and DNS failures.

The selected rule is prepared as [REQ-DNS-03-0040](../tests/dns-03.md#REQ-DNS-03-0040), the next allocation above maximum 0039. The `http_failure` and `unexpected_content_type` rows of REQ-DNS-03-0008 gain editorial pointers and keep their IDs. No requirement is retired or redefined.

Expected cases: `503` with an HTML media type is `http_failure` with status retained; `503` with `application/dns-message` is `http_failure` with no body read and no `doh` `dns_query` observation; a `302` with `Location` is `http_failure` and the location is never contacted; `200` with an HTML media type is `unexpected_content_type`; `200` with `application/dns-message` is parsed.

## Ordering and Public Disposition

No architecture or responsibility boundary changes, so no coordination decision is needed. Order: public review and merge of this wording; internal DNS-03 validation alignment; Go reference update and a machine-readable reference to REQ-DNS-03-0040 (behavior already adopted); native and host validation before release.

## Adoption and Closure Evidence

Merged: REQ-DNS-03-0040, the catalog entry, the editorial pointers and this record through [public PR #39](https://github.com/tv-rain/barometer-spec/pull/39) at [`830e956`](https://github.com/tv-rain/barometer-spec/tree/830e9564849ebfedaa0860d9f01032574e2b9fa3), retaining Draft `0.1.0`. Internal DNS-03 alignment merged through internal PR #19 at `a884513`. Go behavior: adopted. Go reference update: the shared HTTP exchange, the DNS-03 runner and the existing status-precedence cases cite REQ-DNS-03-0040 through [barometer-go PR #118](https://github.com/tv-rain/barometer-go/pull/118) at [`db100b4`](https://github.com/tv-rain/barometer-go/commit/db100b4d6f4b2b23fbdd75f64cf5b6c01bead96d). Pending: the milestone manifest mapping, and binding, host and downstream validation. The finding is not closed, and no platform, field or release support is claimed.
