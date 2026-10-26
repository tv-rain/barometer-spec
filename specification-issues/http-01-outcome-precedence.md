# Specification Issue: HTTP-01 Terminal Response Outcome Precedence

## Identity and Ownership

- Local finding: `GO-SPEC-ISSUE-017`; Go [finding record](https://github.com/tv-rain/barometer-go/blob/agent/dev-667-http-outcome-precedence/docs/specification-issues.md#go-spec-issue-017-http-01-terminal-response-outcome-precedence). The branch link is a proposed record, not immutable published evidence.
- Implementation task: [DEV-667 — Implement HTTP-01](https://app.clickup.com/t/124kk1zcw4x). Public PR and individual reviewers are pending human assignment.
- Disposition: **Open proposal**, October 26, 2026. The Go implementation agent reports this under the task owner's instruction; public maintainers own disposition. Approval to record it is not acceptance of proposed behavior.
- No duplicate identified in the public or Go findings. GO-SPEC-ISSUE-004 governs common execution termination separately.

## Affected Baselines and Requirements

- Public `tv-rain/barometer-spec` revision [`2b843611ddc6fe3718359034574cd2989b3cbf9d`](https://github.com/tv-rain/barometer-spec/tree/2b843611ddc6fe3718359034574cd2989b3cbf9d), Draft `0.1.0`: HTTP-01 test/result versions and Measurement Result schema `0.1.0`.
- [HTTP-01](https://github.com/tv-rain/barometer-spec/blob/2b843611ddc6fe3718359034574cd2989b3cbf9d/tests/http-01.md): REQ-HTTP-01-0007 (procedure), -0008 (all checks match), -0009 and -0036 (outcome tables), -0037 (decidable checks), -0038 (common interruption), -0039 (minimization).
- [HTTP observations](https://github.com/tv-rain/barometer-spec/blob/2b843611ddc6fe3718359034574cd2989b3cbf9d/data-formats/measurement-observations.md): REQ-OBS-0023 (failures), -0028 (body metadata), -0030 and -0031 (indexed checks/minimization). They define values and fields without precedence among concurrent HTTP failure conditions.
- Go baseline [`8576bbc10d68c4a5c2328df34043d31124b06bad`](https://github.com/tv-rain/barometer-go/tree/8576bbc10d68c4a5c2328df34043d31124b06bad): `internal/protocol/http/checks.go` (`evaluate`) and `exchange.go` (`Exchange`). The primitive exists; production HTTP-01 registration and caller-specific conformance remain pending. No affected release, native, binding or field support is established.

## Finding and Reproduction

HTTP-01 records one terminal outcome, but several failure rows can apply to one response. Stopping at the first failed stage does not explicitly order status, header and body conditions within the HTTP stage or say whether a body-processing failure replaces an earlier mismatch. Retaining every decidable check does not select the summary outcome.

The synthetic examples below describe source-inspected paths, not newly executed reproductions or conformance evidence. No external destination is needed.

| Synthetic conditions | Existing primitive selection | Public question |
|---|---|---|
| Expected status 200 and body `contains: ok`; status 503, `Content-Encoding: gzip`, empty body | `unsupported_content_encoding`; failed status retained, body check absent | Encoding or status failure? |
| Expected status 200 and required header absent; status 503, complete empty identity body | `unexpected_status`; both failures retained as checks | Status or header failure? |
| Expected status 200 and body `suffix: ok`; bound 4; status 503, identity body longer than 4 bytes | `unexpected_status`; body truncated, suffix check absent | Status or `body_limit_reached`? |
| Expected status 200; status 503, declared identity body length 4, stream ends after 2 bytes | `protocol_error`; earlier failed status check retained | Body processing or status failure? |

Source inspection also shows that an HTTP operation timeout replaces an earlier mismatch. Otherwise status wins over header, header over body, and `body_limit_reached` is selected only when checks remain undecidable and no check mismatch was selected. These are current implementation choices, not accepted public precedence.

**Blocked:** affected HTTP-01 outcome selection, exact multi-failure assertions in `M-HTTP-01-NORMALIZATION`, and a complete DEV-667 conformance claim. Existing primitive behavior stays unchanged; this proposal adds no runner or runtime fallback. Unaffected codec, target, bounds and common-termination work may continue within its approved scope.

## Impact and Required Reviews

Different summaries of the same response affect comparison and aggregation even when indexed checks agree. Server errors, changed content, compression and truncated transfers remain alternative explanations; none establishes censorship.

The proposal adds no destination, identifier, retained content, read allowance, retry or redirect. Public measurement and implementation maintainers must review precedence and decidable-check handling. Scoped safety/privacy review must confirm unchanged traffic, minimization, bounds and common termination. Reviews, findings and individual assignments are pending. Native stack behavior still needs downstream validation; no device evidence is supplied.

No API, serialized field or vocabulary change is proposed. Producers and consumers grouping by outcome need compatibility review because combined-failure classification becomes constrained. No deployment or participant data flow changes here; existing legal and platform-policy gates remain applicable.

## Alternatives and Proposed Public Resolution

1. **Specify the existing primitive's order (recommended).** Preserve current summaries and individual check evidence while giving body-processing errors priority.
2. **Prefer the earliest failed configured check.** Status would win even over a later malformed body or HTTP timeout; some primitive behavior must change.
3. **Explicitly permit implementation choice.** Exact expectations accept several outcomes, reducing comparability.
4. **Retain ambiguity.** Affected conformance remains blocked; silence does not authorize a new rule.

Proposed exact wording for a new requirement in `tests/http-01.md`, after the outcome table and before the decidable-check rule; **not adopted**:

> For a terminal non-redirect HTTP response, common execution interruptions remain governed by the common execution-state rules and do not become HTTP outcomes. An HTTP operation timeout, malformed or prematurely terminated protocol body, or inconclusive body read takes precedence over already evaluated response-check mismatches and uses its registered HTTP outcome. If a body check is configured and the response encoding is unsupported, select `unsupported_content_encoding` without evaluating body checks. Otherwise select the first applicable class in this order: `unexpected_status`, `header_check_failed`, `body_check_failed`, `body_limit_reached`, `expected_response`. `body_limit_reached` applies when the body bound leaves at least one configured body check undecidable; truncation alone does not override an already decidable mismatch or require that outcome when all checks are decidable. Preserve every check result decidable before termination; do not invent results for unevaluated checks. This order authorizes no additional reads, retries or network operations and changes neither redirect nor preceding-stage outcomes.

A protocol body failure here is a transport/read failure inside the HTTP operation; common cancellation/deadline/network/proxy interruption retains REQ-HTTP-01-0038 precedence. Simultaneous independent common execution reasons are outside this proposal.

Maintainers should allocate a new requirement above the current HTTP-01 maximum after reconciling the merge base; no ID is allocated here. Existing requirements remain active unless review identifies materially replaced obligations. Proposed version decision: retain Draft `0.1.0`, with the combined-failure compatibility constraint recorded explicitly; acceptance remains pending.

Expected cases: every row above; header plus body mismatch; prefix mismatch plus undecidable suffix at the bound; all checks decidable despite truncation; HTTP timeout after headers; common execution interruption at the same points. Expected combined-failure outcomes remain proposals until disposition. All cases must preserve minimization and evaluated-check evidence.

## Ordering and Public Disposition

No architecture or responsibility boundary change is proposed, so no coordination ADR is currently needed. Public PR, maintainer disposition, required reviews, version decision and merged immutable revision are pending. This record selects no runtime rule.

Order: public disposition and merged wording (or immutable no-text-change clarification), required internal HTTP-01 review/validation alignment, Go adoption under DEV-667, then affected native/binding and host/consumer validation before release. Public maintainers own disposition, internal review owners own alignment and the Go implementation owner owns synthetic adoption evidence. Downstream individual owners/task links remain to be assigned. If deferred or rejected without a usable clarification, retain the blocked scope and record the rationale.

## Adoption and Closure Evidence

Pending: accepted public baseline and requirement links, required review/alignment evidence, Go adoption commits and multi-failure cases, compatibility decision, downstream validation or explicit non-applicability. Source inspection is not runtime conformance evidence. This proposal neither completes DEV-667 nor closes GO-SPEC-ISSUE-017 and makes no platform, field or release-support claim.
