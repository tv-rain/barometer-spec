# Specification Issue: NET-03 Response Classification and Outcome Selection

## Identity and Ownership

- Local findings: `GO-SPEC-ISSUE-006` (over-bound response classification) and `GO-SPEC-ISSUE-019` (platform and active outcome selection); Go [finding records](https://github.com/tv-rain/barometer-go/blob/agent/dev-674-net-03-network-validation/docs/specification-issues.md#go-spec-issue-019-net-03-platform-and-active-outcome-selection). The branch link is a proposed record, not immutable published evidence.
- Implementation task: [DEV-674 — Implement NET-03](https://app.clickup.com/t/124kk1zcw55).
- Disposition: **Maintainer-selected; wording prepared, public merge pending.** The project owner, Lev, selected the rules on October 27, 2026 and authorized preparing the wording with the Go adoption. Required reviews and immutable public merge remain pending.
- No duplicate identified. [HTTP-01 Terminal Response Outcome Precedence](http-01-outcome-precedence.md) settles the analogous question for HTTP-01 only; [`not-run-incomplete-boundary.md`](not-run-incomplete-boundary.md) governs common termination.

## Affected Baselines and Requirements

- Public `tv-rain/barometer-spec` revision [`bf3d6f755cf2fa35d3d6d063ef0297592a17980e`](https://github.com/tv-rain/barometer-spec/tree/bf3d6f755cf2fa35d3d6d063ef0297592a17980e), Draft `0.1.0`: NET-03 test and result versions and Measurement Result schema `0.1.0`.
- [NET-03](../tests/net-03.md): REQ-NET-03-0008 (failure classes), -0009 (inputs), -0021 (resource bounds), -0023 (separate evidence), -0024 and -0025 (`platform_validation`, `response_class`), -0027 (outcomes) and -0029 (common interruption).
- Go: no NET-03 runner exists at [`b7de8a1`](https://github.com/tv-rain/barometer-go/tree/b7de8a1e7df7dc90c5c05bf19877542a1d82e237); the shared HTTP exchange and the NET-03 result validation exist. No native, binding or field support is established.

## Finding and Reproduction

1. **Outcome selection.** REQ-NET-03-0027 assigns `captive_portal_suspected` to platform state `captive_portal` and `not_validated` to platform state `not_validated`, while `validated` and the DNS, TCP and TLS failure rows describe the active request. One run can satisfy several rows, for example platform `captive_portal` with an expected response, or platform `not_validated` with a DNS failure. REQ-NET-03-0023 says `platform_validation` never overrides the request observation, which, read literally, leaves the platform rows no case to apply to.
2. **Response classes.** REQ-NET-03-0025 lists `expected`, `redirect`, `content_mismatch` and `unexpected` without defining them, so a 200 response when 204 is expected could be `content_mismatch` or `unexpected`.
3. **Over-bound response.** REQ-NET-03-0021 requires a response that reaches the header or prefix bound to be classified "as exceeding the registered validation bound", but no class or outcome carries that meaning, and REQ-NET-03-0029 makes a resource limit an incomplete state with no `measurement`.
4. **Unreachable input.** REQ-NET-03-0009 accepts any valid status as `expected_status`, but redirects are never followed, so an expected redirect or informational status could never establish validation.

These are source-inspected readings of the public text, not executed reproductions. **Blocked:** NET-03 outcome selection, response classification, the over-bound path and the matching `M-NET-03-NORMALIZATION`, `M-NET-03-LIMITS` and `M-NET-03-OUTPUT` rows. Unaffected codec, target and termination work may continue.

## Impact and Required Reviews

- **Safety and privacy:** the rules add no destination, request, read, retry, redirect contact, field or retained value. Traffic, minimization and bounds are unchanged.
- **Interpretation:** the selected rules let the active request decide whenever it produced a response, and use platform state only when it did not. `content_mismatch` is limited to a matching status with a different body digest, so a different status is `unexpected_response` rather than a portal claim. Captive portals, quota pages, CDN or endpoint faults and stale platform state remain alternative explanations; no outcome is evidence of censorship.
- **Compatibility:** no field, vocabulary or numeric bound changes; Draft `0.1.0` is retained. Rejecting a redirect or informational `expected_status` narrows accepted input, so producers of such tasks need compatibility review.
- **Reviews:** public measurement and implementation maintainers must review the classes and order; scoped safety and privacy review must confirm unchanged traffic and minimization. Reviews and assignments are pending.

## Alternatives and Selected Public Resolution

Outcome selection: (1) request first, with platform rows only when no response class exists (**selected**); (2) treat any conclusive platform and request disagreement as `inconclusive`; (3) platform first.

Over-bound response ([GO-SPEC-ISSUE-006](https://github.com/tv-rain/barometer-go/blob/agent/dev-674-net-03-network-validation/docs/specification-issues.md#go-spec-issue-006-net-03-over-bound-response-classification)): (a) `response_class: unexpected` with `unexpected_response` (**selected** for the response prefix); (b) a new registered value; (c) `resource_limit` with no measurement. A header block over the bound has no parsed status and is therefore not a valid response; it carries no `response_class` and follows the no-class rule.

`content_mismatch`: (1) status matched with a different digest (**selected**); (2) any non-matching 2xx response.

`expected_status`: (1) reject redirect and informational statuses as invalid input (**selected**); (2) accept them although they can never validate.

The selected rules are prepared as [REQ-NET-03-0041](../tests/net-03.md#REQ-NET-03-0041) (valid response and classes), [REQ-NET-03-0042](../tests/net-03.md#REQ-NET-03-0042) (outcome order) and [REQ-NET-03-0043](../tests/net-03.md#REQ-NET-03-0043) (`expected_status` domain), the next allocations above maximum 0040. No existing requirement is retired or redefined.

Expected cases: each response class with each platform state; DNS, TCP, TLS and HTTP failures with each platform state; a body at, below and above the 1,024-byte prefix with and without a digest; a header block at and above 16,384 bytes; and rejection of each redirect and an informational `expected_status`.

## Ordering and Public Disposition

No architecture or responsibility boundary changes, so no coordination decision is needed. Order: public review and merge of this wording; internal NET-03 review and validation alignment; Go adoption under DEV-674, prepared on its branch for merge after this record; native and host validation before release. If the wording is deferred or rejected, the blocked scope returns to the existing contract.

## Adoption and Closure Evidence

Prepared: REQ-NET-03-0041 to REQ-NET-03-0043, the catalog entries and this record. Pending: immutable public merge, review and alignment evidence, Go adoption commits and cases, compatibility confirmation and downstream validation. Neither finding is closed, and no platform, field or release support is claimed.
