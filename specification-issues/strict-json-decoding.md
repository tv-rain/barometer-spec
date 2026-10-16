# Resolution: Strict Runtime JSON Decoding

**Disposition:** Accepted wording; merged at `05c1364af4f9a604b617fca45f060949b557d265`; downstream adoption pending
**Date:** October 13, 2026
**Related task:** [DEV-477 — Implement shared strict-decoding infrastructure](https://app.clickup.com/t/86cbb8f0x)

The project owner approved the proposed wording and retention of Draft 0.1.0 on October 13, 2026. The corresponding contract and requirement allocations are prepared in this public review branch. Public merge, immutable-baseline adoption, and downstream implementation remain pending; this record does not close the finding or establish runtime conformance.

## Identity and Ownership

The existing Go finding retains its local ID GO-SPEC-ISSUE-001: [Duplicate JSON Member Names Outside Labels](https://github.com/tv-rain/barometer-go/blob/d516122446d22e29f65194c21ea16b88718844fc/docs/specification-issues.md#go-spec-issue-001-duplicate-json-member-names-outside-labels). This record also covers related numeric/Unicode representation gaps exposed by the strict-decoder task. These are additional review questions, not previously accepted interpretations of that finding.

The reporter is the Go implementation agent under the task owner's instruction. Public specification maintainers own disposition and requirement allocation; the Go implementation owner owns downstream adoption and conformance. The project owner, Lev, reviewed and approved the public wording and version disposition in the task review on October 13, 2026. Public PR and any additional specialist reviewers remain pending. No duplicate public proposal was found in the current issue directory. Initial task-plan approval authorized preparation; the subsequent wording approval authorized this contract change.

## Affected Baselines and Requirements

| Source | Baseline and scope |
|---|---|
| Public specification | Draft 0.1.0; proposal base 3a8af25d610ec73c55521a0bbb57cb79b4d5eba0. The Go inventory's historical runtime baseline 95dfeef1367f4c320bca7c7ae91b13ca7608b37f is retained as evidence, not silently replaced. |
| Go repository | d516122446d22e29f65194c21ea16b88718844fc, after merged API design PR #12. Runtime task decoding and production facade remain unimplemented. |
| Native/Flutter consumers | Implementations and affected releases are unknown; no runtime/device validation is claimed. |

[Task top-level fields](https://github.com/tv-rain/barometer-spec/blob/3a8af25d610ec73c55521a0bbb57cb79b4d5eba0/data-formats/task.md#top-level-fields) reject unknown fields under [REQ-TASK-0001](../data-formats/task.md#REQ-TASK-0001). [Labels — Keys](https://github.com/tv-rain/barometer-spec/blob/3a8af25d610ec73c55521a0bbb57cb79b4d5eba0/data-formats/task-labels.md#keys) explicitly rejects duplicates and requires case-sensitive keys. Broader duplicate handling and integer lexical rules have no allocated requirement ID at these baselines.

Other controlling unallocated sections are [Task Trust — Admission Procedure](https://github.com/tv-rain/barometer-spec/blob/3a8af25d610ec73c55521a0bbb57cb79b4d5eba0/library/task-trust.md#admission-procedure), [Replay Handling](https://github.com/tv-rain/barometer-spec/blob/3a8af25d610ec73c55521a0bbb57cb79b4d5eba0/library/task-trust.md#replay-duplicate-and-rollback-handling), [Schedule field tables](https://github.com/tv-rain/barometer-spec/blob/3a8af25d610ec73c55521a0bbb57cb79b4d5eba0/data-formats/task-schedule.md), [Input Validation](https://github.com/tv-rain/barometer-spec/blob/3a8af25d610ec73c55521a0bbb57cb79b4d5eba0/data-formats/task-input.md#validation), [Options Validation](https://github.com/tv-rain/barometer-spec/blob/3a8af25d610ec73c55521a0bbb57cb79b4d5eba0/data-formats/task-options.md#validation), and [Registered Limits](https://github.com/tv-rain/barometer-spec/blob/3a8af25d610ec73c55521a0bbb57cb79b4d5eba0/library/registered-limits.md). Their field/range rules remain authoritative; examples are not alternative schemas.

## Finding and Synthetic Evidence

Unknown-field rejection alone does not produce strict decoding. A decoder may merge repeated names, match the wrong case, replace invalid text, coerce null, lose integer precision, or stop after one value while ignoring trailing content. [Go JSON documentation](https://pkg.go.dev/encoding/json) describes default behaviors; [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) supplies JSON grammar and interoperability context. Neither establishes Barometer's acceptance policy.

A temporary local program using Go 1.26.0, encoding/json.Decoder, DisallowUnknownFields, and one Decode call reproduced these behaviors. Fragments are not complete valid Barometer tasks.

| Synthetic operation | Observed Go behavior |
|---|---|
| Repeated test_id with NET-01 then TCP-01 | Accepts and retains TCP-01. |
| Literal test_id followed by test_\u0069d | Accepts and retains the second value. |
| TEST_ID against the JSON field tag test_id | Accepts the case variant. |
| 1.0 or 1e0 into int64 | Rejects; generic numeric decoding accepts these JSON numbers. |
| -0 into int64 | Accepts and returns zero. |
| String containing escape \ud800 | Accepts and substitutes U+FFFD. |
| null into a fresh int64 field | Accepts and leaves zero. |
| Two consecutive objects with one Decode | Accepts the first and leaves the second unread. |
| 9007199254740993 decoded into any | Produces float64 value 9007199254740992. |

These observations concern one toolchain and destination types. They do not establish behavior across all parsers or an implemented Barometer vulnerability. No production decoder, network operation, or participant data was used. Affected decoding implementation remains blocked; unrelated unambiguous work may continue.

The duplicate-name and trailing-value behavior can be reproduced with this standalone synthetic program. The malformed-text and numeric observations above used equivalent fresh destination structs and generic numeric destinations; a single Decode call intentionally demonstrates the missing end-of-input check.

~~~go
package main

import (
    "encoding/json"
    "fmt"
    "strings"
)

func main() {
    for _, input := range []string{
        "{\"test_id\":\"NET-01\",\"test_id\":\"TCP-01\"}",
        "{\"test_id\":\"NET-01\",\"test_\\u0069d\":\"TCP-01\"}",
        "{\"TEST_ID\":\"TCP-01\"}",
        "{} {}",
    } {
        var candidate struct {
            TestID string `json:"test_id"`
        }
        decoder := json.NewDecoder(strings.NewReader(input))
        decoder.DisallowUnknownFields()
        err := decoder.Decode(&candidate)
        fmt.Printf("accepted=%t, test=%q\n", err == nil, candidate.TestID)
    }
}
~~~

## Alternatives and Tradeoffs

1. Reject duplicate decoded names throughout runtime JSON, require exact schema names, reject invalid Unicode, and use plain decimal integer tokens. Recommended: avoids first/last-member selection and numeric coercion, but rejects some grammatically valid JSON and needs producer compatibility review.
2. Permit integral decimal/exponent spellings and negative zero using exact arithmetic. Feasible without floating-point loss, but requires additional consistent producer/consumer semantics and tests.
3. Define first/last-member selection and permissive string/name matching. Follows some parser defaults, but risks host/core disagreement and turns parser choices into an implicit contract.
4. Retain current text or issue a no-change clarification. A no-change disposition must cite an existing rule that settles the questions; otherwise affected work remains blocked.

## Approved Contract

The approved wording is in [Runtime JSON Decoding](../data-formats/json-decoding.md), indexed in the data-format directory and linked from all existing data-format and library contracts. Existing field schemas, explicitly nullable fields, and label-key rules continue to apply. The shared contract excludes development artifacts and introduces no trusted context into public task input.

## Requirement and Version Disposition

REQ-TASK-0001 remains unchanged. The public JSON namespace allocates eleven new obligations, REQ-JSON-0001 through REQ-JSON-0011, for framing, Unicode validity, duplicate names, exact/unknown fields, types/presence, integer lexical form, exact numeric conversion, version selection, byte bounds, bounded atomic processing, and sanitized errors. They are new allocations, not reuse or replacement of the existing Task requirement or labels duplicate-key rule. The catalog records the canonical source of each obligation.

The project owner approved retention of Draft 0.1.0 as a restriction/clarification before the project's decoder is implemented. The immutable accepted public revision must be recorded after merge and selected explicitly by Go adoption. Keeping the version label does not assert that every previous producer remains compatible: duplicate names, integer exponents/decimals/negative zero, invalid Unicode, and case aliases now have explicit rejection rules. External producers, stored bundles, and delivery verifiers remain unassessed and need review before use with the revised contract. Existing field/schema/test version values are unchanged; no release or runtime support claim is made. Do not normalize exact task bytes to migrate them: changed bytes require integrity/replay treatment and must not evade conflicting task-ID checks.

## Accepted Case Expectations

These are expectations under the approved wording, not executed Barometer conformance cases. Token/framing acceptance still requires complete schema validation.

| Case | Expected outcome |
|---|---|
| Valid model with surrounding JSON whitespace | Accept framing, then validate the schema. |
| Duplicates at top level, in labels/nested objects, or in an object within an array | Reject the entire model, whether values agree or conflict. |
| Literal/escaped spellings of the same name | Reject duplicates; a sole escaped known name is valid if it satisfies the schema. |
| Same name in different objects | No duplicate failure; validate each object. |
| Case variant of a fixed field or unknown nested input/option field | Reject in the applicable closed schema. |
| Valid unreserved label or explicit nullable starts_at | Preserve existing acceptance rules. |
| Empty/truncated input, comments, trailing commas, second value, trailing garbage, BOM | Reject. |
| Invalid UTF-8 or unpaired surrogate in a name/value | Reject without repair. |
| Valid surrogate pair or literal U+FFFD | No Unicode failure; apply field-specific rules. |
| Integer 0, positive decimal integer, nonzero negative integer | Accept lexical form; enforce field sign/range. |
| Integer-field -0, 1.0, 1e0, 1E+0, 1.5, quoted number, boolean | Reject. |
| Large exact integer 9007199254740993 | Preserve until range/representation checking; never round to 9007199254740992. |
| Missing required field, wrong type, null in a non-nullable field | Reject without substituting zero/default. |
| Unsupported/missing required version or wrong test/version pairing | Reject without a second schema attempt. |
| Size/count boundary, oversized input, deeply nested malformed input | Enforce bounds and atomic failure; never publish partial data. |
| Rejection involving synthetic secret-like values/names | Bounded error contains none of them. |

## Impact and Required Reviews

Safety/trust review is required because parser disagreement can authorize different targets or configuration. This proposal adds no destinations, telemetry, identifiers, retention, linkage, traffic, or consent behavior. Existing measurement interpretation limitations remain; decoder rejection is an operational state. Hostile-input/resource review must cover size bounds, nesting, exact numbers, and atomic failure.

Public schema/version maintainers must review acceptance narrowing and requirement units. Go and future native/Flutter owners must review consistent name, Unicode, numeric, and version handling; compilation alone is insufficient. Internal admission/validation review alignment follows accepted public wording without adding private normative obligations. No specialist review is claimed complete. Participant collection and deployment are outside this work; existing privacy/platform-policy/legal gates remain applicable. This record needs no private evidence and contains only synthetic inputs and public facts.

## Ordering and Public Disposition

No new coordination ADR is proposed: responsibility boundaries and long-lived architecture remain unchanged. The accepted issue workflow governs this clarification. Merge reviewed public wording/version decisions first, align required internal reviews, implement Go on its own task branch against the immutable accepted baseline, then validate applicable bindings and producer/host migration. Each repository retains independent commits/reviews. No release or support promotion is authorized.

**Public disposition:** Wording and retention of Draft 0.1.0 approved by the project owner, Lev, on October 13, 2026, in the DEV-477 task review. The contract and eleven new requirement allocations are prepared for final change review. Commit/push approval, public PR, merged immutable revision, required internal alignment, Go implementation/conformance, binding/producer validation, migration/release order, and closure evidence remain pending. No specialist review is represented as completed. If later review changes the resolution, preserve this disposition history and reassess downstream adoption. GO-SPEC-ISSUE-001 is not closed until applicable downstream evidence or explicit non-applicability is recorded.

**Merge record:** The approved wording, Draft `0.1.0` retention and requirement allocations were merged on October 13, 2026 through [public PR #5](https://github.com/tv-rain/barometer-spec/pull/5) as immutable revision `05c1364af4f9a604b617fca45f060949b557d265` (head `16001c30af7bef4b651e18b9750e71f3647715ca`). Downstream adoption selects that revision explicitly. The merge does not close the finding; applicable downstream evidence or reviewed non-applicability remains pending, and no specialist review is represented as completed.

## Validation

On October 13, 2026, the synthetic Go 1.26.0 reproduction produced the observations above. Before wording approval, the public requirement structure checker, proposal links, and whitespace checks passed. After materializing the approved contract, allocation-history validation against the immutable proposal base passed, all 23 requirement-checker regression tests passed, and changed-document links, versions, and whitespace checks passed (including new untracked files). These checks establish metadata/document integrity, not runtime conformance. No Go runtime files are changed by this public prerequisite.
