# Proposal: Registered Observation Vocabularies

**Disposition:** Wording approved; merged at `a944ed6c389fec9f0d089f0044ead6fe845328b1`; downstream adoption pending
**Date:** October 15, 2026
**Related task:** [DEV-481 — Implement observation and Network Context models](https://app.clickup.com/t/86cbb8f2n)

This review package defines the approved normalized DNS/TLS wording and clarifies incomplete-observation failures. After preparation, the project owner, Lev, reviewed the specifications and approved the wording, Draft `0.1.0` version disposition and specification commit/push on October 15, 2026. Affected Go implementation remains stopped until public merge and required internal alignment. No specialist review, conformance or release support is claimed.

## Identity and Ownership

The originating Go finding retains local ID `GO-SPEC-ISSUE-002`, [Missing Registered Observation Vocabularies](https://github.com/tv-rain/barometer-go/blob/agent/dev-481-observation-context-models/docs/specification-issues.md#go-spec-issue-002-missing-registered-observation-vocabularies). That branch link is the intended discovering record; its initial commit/push is pending and it is not immutable evidence. This public Markdown record supplies the proposed public identity once reviewed through the human-created PR. Public PR URL, responsible maintainer and specialist reviewer assignments are pending. The reporter is the Go implementation agent under the task owner's instruction; public maintainers own wording, allocation and disposition. No matching existing public proposal was found. The strict-JSON issue provides parsing rules, not these value registries.

## Affected Baselines and Requirements

The public proposal base is Draft `0.1.0`, immutable revision `59d49364d85e48cc8e69c762d130a7a86dc1fe65`. The Go base is `0f1a2020726f6dc0ec5a25fe90ee4c61177ba230`. DNS/TLS observation models and runtime measurements have no implementation/release evidence at those bases. The current Go task has partial, uncommitted TCP/HTTP/context models; these do not resolve the finding. Native/Flutter producer compatibility and deployed/stored results are unassessed.

- Historical [REQ-OBS-0011](https://github.com/tv-rain/barometer-spec/blob/59d49364d85e48cc8e69c762d130a7a86dc1fe65/data-formats/measurement-observations.md#REQ-OBS-0011) requires registered DNS response-code names but supplies no membership list.
- Historical [REQ-OBS-0021](https://github.com/tv-rain/barometer-spec/blob/59d49364d85e48cc8e69c762d130a7a86dc1fe65/data-formats/measurement-observations.md#REQ-OBS-0021) requires registered TLS versions, ALPN values and coarse alert classes without defining them.
- [REQ-TLS-01-0016](../tests/tls-01.md#REQ-TLS-01-0016) requires registered offered ALPN values; [REQ-OBS-0003](../data-formats/measurement-observations.md#REQ-OBS-0003) permits a failure for an incomplete observation only when registered.
- [REQ-OBS-0041](../data-formats/measurement-observations.md#REQ-OBS-0041) provides conservative failure normalization, but does not supply the missing detail-field memberships. Existing privacy, answer/byte limits and test outcome rules continue to apply.

## Finding and Synthetic Reproduction

The baseline provides examples such as `NOERROR`, `TLS1.3` and `h2`, not exhaustive registries. A valid DNS response carrying effective code 16 therefore has no defined retained label or coarse fallback. A received TLS description code 42 similarly has no defined coarse alert class. A malformed serialized detail such as `{"alert":"arbitrary library text"}` must not become valid merely because a producer can emit a string. These are incomplete synthetic fragments, not executed Barometer measurements.

Protocol documentation supplies facts, not Barometer retention policy. [IANA DNS RCODEs](https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml#dns-parameters-6) assigns the six common codes and additional codes; its numeric value 16 has different meanings in EDNS and TSIG contexts. [IANA ALPN](https://www.iana.org/assignments/tls-extensiontype-values/tls-extensiontype-values.xhtml#alpn-protocol-ids) registers the three selected identifiers and many others. [RFC 8446 section 6](https://www.rfc-editor.org/rfc/rfc8446.html#section-6) distinguishes received alerts from local error conditions and normal closure. The proposed coarse subsets below are project choices informed by those sources, not external requirements.

Blocked work is DNS/TLS model validation and any incomplete observation carrying a failure. Unambiguous TCP/HTTP/context model work may continue. An unaccepted proposal, successful parser test or external registry entry cannot authorize adopting the proposed values.

## Alternatives and Proposed Resolution

1. **Fixed project vocabularies with coarse markers (proposed).** Bounds retained detail, removes dependency on mutable external registries and preserves the difference between an unavailable field and an observed value outside the retained subset. Loses some protocol detail and needs compatibility review.
2. Adopt an enumerated snapshot of every external registry value. Retains more detail, but increases review/mapping work; raw alert names still would not define coarse alert classes. New entries could not be adopted automatically.
3. Infer only the example values or permit arbitrary bounded strings. Examples are incomplete; arbitrary strings risk retaining application-specific or identifying values and do not meet the registered-value requirement.
4. No-text-change disposition identifying an existing complete authoritative registry. No such source has been identified; without one the blocker remains.

The proposed exact normative wording is materialized in [Registered Normalized Vocabularies](../data-formats/measurement-observations.md#registered-normalized-vocabularies), the replacement DNS/TLS field tables, and the [TLS options cross-reference](../tests/tls-01.md#options).

| Field/operation | Proposed closed values or handling |
|---|---|
| DNS `rcode` | `NOERROR`, `FORMERR`, `SERVFAIL`, `NXDOMAIN`, `NOTIMP`, `REFUSED`, `OTHER`; reliable effective codes 0–5 map individually, all other valid observed codes map to `OTHER`. |
| DNS code unavailable | Omit the response record; do not invent a response code. Malformed/nonmatching responses remain subject to existing rejection/failure rules. |
| Negotiated `tls_version` | `TLS1.2`, `TLS1.3`, `unknown`; omit when no version was negotiated/exposed. |
| Offered ALPN | Exactly `http/1.1`, `h2`, `dot`; `unknown` is never an offer. Existing test/target/local policy still restricts use. |
| Retained negotiated `alpn` | Those three identifiers or `unknown`; omit when no protocol was negotiated/exposed. A coarse value cannot make invalid negotiation succeed. |
| Peer-alert class | `handshake_failure`, `certificate_error`, `protocol_error`, `access_denied`, `internal_error`, `other`, using the exact public numeric grouping. |
| Peer-alert description unavailable | Omit `details.alert`; an opaque/local error is not evidence that a peer alert was received. |
| `status: incomplete` | No `failure` field for any of the four initial types; registered-test partial-output rules and `execution.reason` still apply. |
| Serialized value outside these vocabularies | Reject atomically; producer normalization is not decoder repair. |

The proposal adds no network operation or raw-data retention. In particular it neither enables legacy TLS, changes security settings, nor offers a new ALPN automatically. `unknown` is not an offer/handshake capability; `OTHER` is not DNS success. Coarse peer certificate alerts cannot overwrite local certificate validation. Cross-cutting termination remains separate from protocol failures.

## Requirement and Version Proposal

The proposed catalog retires `REQ-OBS-0011` and `REQ-OBS-0021` with successors `REQ-OBS-0042` and `REQ-OBS-0043`, because the replacement tables define materially explicit acceptance boundaries and permit coarse markers rather than only protocol names. Historical anchors and immutable citations remain available. Proposed new obligations `REQ-OBS-0044` through `REQ-OBS-0051` define fixed contract ownership, producer/decoder separation, DNS normalization and failure handling, TLS negotiated versions, ALPN, alerts and incomplete-field rejection. Numbers must be reconciled with the target branch before merge. This is proposed public allocation, not implementation support.

The project owner approved retention of Draft `0.1.0` before DNS/TLS implementation on October 15, 2026, consistent with the repository's existing version policy. The wire object shape, schema/test version fields, generic numeric ceilings and failure/outcome enums remain unchanged, but accepted detail values and offered ALPN membership become explicit and narrower than an arbitrary-string producer might assume. Such producers, stored results, bindings and analytics are unassessed; they require compatibility review or migration before use. Matching `0.1.0` labels do not prove compatibility. No value is silently rewritten during decoding, no new result field carries original unregistered data, and no release is authorized here.

## Impact and Required Reviews

Public schema/version and measurement maintainers must review membership, coarse mapping, outcome precedence, requirement replacement and Draft version retention. Safety/privacy review must check that peer-controlled identifiers and raw diagnostic strings cannot leak through coarse-value paths. Implementation review must check platform API exposure, unavailable values, exact effective DNS codes and negotiated-versus-record TLS versions. Native/Flutter and producer/analysis owners must assess compatibility before adoption. These reviews are pending; proposal preparation does not mark specialist review complete.

This changes retained normalization and a referenced offered-ALPN membership boundary, so reviewers must assess whether existing intended target profiles remain expressible and whether any offer changes traffic distinctiveness. It mandates no new traffic, destinations, retries, identifiers, linkage, retention or participant collection. Existing deployment safety, platform-policy and legal gates remain applicable. No blanket legal or anonymity conclusion follows. Protocol outcomes continue to admit ordinary endpoint, certificate, routing, platform and transient-network explanations. This public-safe proposal requires no private evidence or internal access.

## Proposed Case Expectations

These are review expectations, not executed implementation/conformance results.

| Synthetic case | Proposed expectation |
|---|---|
| Effective DNS codes 0–5 | Map exactly to their six names; retain existing failure/no-data semantics. |
| Valid effective code 6, 16, 23 or a private/unassigned code | Producer emits `OTHER`; a valid nonzero code without a specific registered failure uses `inconclusive`. |
| Extended code 16 with low bits 0 | Do not report `NOERROR`; do not retain the extension or its numeric value. |
| System result without a reliable response code | No fabricated response record or `OTHER`. |
| Serialized `rcode: BADVERS`, `rcode: noerror`, numeric code or an arbitrary string | Reject; producer coarse mapping cannot repair serialized data. |
| Negotiated `0x0303`, `0x0304`, another safely established version, or no negotiated version | `TLS1.2`, `TLS1.3`, `unknown`, or absent, respectively. Record-layer legacy fields cannot supply that evidence. |
| Offered `http/1.1`, `h2`, `dot` | Membership valid; still enforce target, count, duplicates, supported test and policy. |
| Offered `unknown`, `h2c`, `h3` or a private token | Reject before traffic; no implicit substitution. |
| Safely observed negotiated identifier outside the fixed set | Producer retains `unknown` without retaining the original; invalid/unoffered selection still fails protocol validation. |
| Peer alert 42, 40, 50, 49, 80 or an ungrouped code | Exact six-class mapping in the public table; no raw code or error text. |
| Local certificate error, local cancellation, or normal closure after success | Do not invent peer-alert reception or alter a completed handshake. |
| `details.alert` with succeeded/incomplete status or a failure other than `alert` | Reject as inconsistent with the field contract. |
| Any incomplete observation with absent `failure` versus present value/null/empty string | Preserve absence; reject presence, subject to test-specific partial-output eligibility. |
| Maximum strings/counts/encoded bytes; unknown nested fields and versions | Preserve existing bounds, closed schemas, exact contract selection and atomic failure. |

## Ordering and Public Disposition

No coordination ADR is proposed because ownership, trust boundaries and architecture remain unchanged. If maintainer review identifies such an effect, resolve it first. Review/approve the exact public wording and compatibility/version decision, then commit/push under separate final approval; the human creates and merges the public PR. Record its immutable merge revision. The corresponding internal review branch is a dependent draft prepared against this exact public proposal; it must be reconciled to the accepted merge revision before internal merge and Go adoption. Complete Go DNS/TLS models/tests only after those gates, then validate applicable bindings, producers and analysis consumers in the documented compatibility order.

**Public disposition:** The initial October 15 authorization covered preparation. Following review of the prepared specifications, the project owner, Lev, approved the wording, requirement lifecycle, retention of Draft `0.1.0` and specification commit/push on October 15, 2026. Public PR and immutable merge revision, required internal reconciliation to that revision, specialist review evidence, DNS/TLS implementation and applicable migration evidence remain pending. GO-SPEC-ISSUE-002 remains open.

**Merge record:** The approved wording, requirement lifecycle and Draft `0.1.0` retention were merged on October 15, 2026 through [public PR #8](https://github.com/tv-rain/barometer-spec/pull/8) as immutable revision `a944ed6c389fec9f0d089f0044ead6fe845328b1` (head `5869bc314c877e2ccd3426b82aadcd9c92414f02`). Downstream adoption selects that revision explicitly. A public merge alone is insufficient for closure; GO-SPEC-ISSUE-002 remains open until the evidence listed below is recorded.

## Adoption and Closure Evidence

Closure requires accepted public wording/version/ID disposition, immutable public merge revision, required internal alignment/review evidence, Go implementation commits and executed cases against that baseline, and applicable binding/producer/analysis migration evidence or explicit non-applicability. A public merge alone is insufficient. Link follow-ups and preserve the historical finding if later review changes the proposed mapping.

On October 15, 2026, requirement/catalog structure and allocation-history validation against the immutable public proposal base passed, with the internal and Go repositories supplied explicitly as consumers. The changed-document check passed for 117 relative links/anchors across 19 changed/new Markdown files, including the dependent drafts. Whitespace checks passed in all three repositories. Existing JSON examples retain values present in the proposed fixed sets; table memberships, numeric groups, optional-field handling and existing test outcome references were reviewed for consistency. These checks validate document/metadata integrity; they do not execute DNS/TLS measurements, establish specialist review, prove safe API exposure or establish runtime/device conformance.
