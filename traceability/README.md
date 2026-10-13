# Traceability Manifest

**Status:** Draft
**Specification version:** 0.1.0
**Manifest format version:** 1

## Purpose and Authority

This development format maps public [requirement IDs](../requirements/README.md) at an immutable specification baseline to implementation locations, conformance cases, support claims, evidence, and [specification issues](../specification-issues/README.md). The marked public obligation remains authoritative. A manifest is neither a second specification nor a runtime task/result object. Internal reviews and planned tests cannot supply private normative requirements.

Public maintainers own this format. Each implementation repository owns its manifests and evidence. Format version `1`, specification version `0.1.0`, implementation release version, requirement lifecycle, and support status are independent. A structural pass establishes none of semantic conformance, complete normative coverage, platform support, or field validation.

## Directory Index

- [`manifest.schema.json`](manifest.schema.json) — closed JSON Schema for structural validation.
- [`example.partial.json`](example.partial.json) — one planned requirement and case at real immutable baselines; no implementation or support claim.
- [`invalid-scenarios.json`](invalid-scenarios.json) — intentionally broken example mutations and required diagnostic subsets for the future checker.

## Encoding and Baselines

Use UTF-8 JSON with one root object. Reject duplicate decoded member names at every depth before constructing an object, including differently escaped spellings of the same name. Reject invalid JSON, unknown fields, invalid types, unsupported format versions, empty/whitespace-only required strings, and duplicate array values. All properties declared in the schema are required; empty arrays represent absent mappings, not implied success. JSON booleans are not integer format versions. Object order and indentation have no meaning.

The schema uses [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/schema), with local `$defs` and no remote schema references. Its [core](https://json-schema.org/draft/2020-12/json-schema-core) and [validation](https://json-schema.org/draft/2020-12/json-schema-validation) specifications define structural keyword behavior. Load the checked-in schema explicitly; do not fetch or execute URLs from a manifest. Structural validation is only the first stage of the validation contract below.

Every baseline/reference identifies a canonical public HTTPS Git repository URL without credentials, query, fragment, or trailing slash, and a full lowercase 40- or 64-hex Git commit ID. Branch names, abbreviated hashes, and tag names are not accepted; resolve a release tag to its commit before writing a manifest. The checker receives an explicit repository-to-local-checkout mapping and reads the named Git objects, not arbitrary working files or whatever `main` currently contains. Missing Git objects or unspecified repositories are errors; the checker must not fetch automatically. Reject an all-zero revision even if it matches the schema's lexical pattern.

The `specification.version` must agree with the applicable public source declarations at its revision. A reused Draft version label does not make different commits equivalent. Validation of a current claim must also receive explicitly selected expected specification and implementation revisions; mismatch is stale. Historical validation selects the original revisions and labels its report historical. No manifest can silently switch to current text or advertise an old pass as a current claim.

Paths are case-sensitive repository-relative file paths using ASCII letters, digits, `.`, `_`, `-`, and `/`. Reject absolute paths, empty segments, parent/current-directory traversal, backslashes, symlinks, submodules, and non-regular files. A `planned` location is a prospective path and need not exist; it is never implementation evidence. An `existing` location and every evidence/issue reference must resolve at the stated revision.

Selectors are exactly `file`, `anchor:<literal-id>`, `heading:<literal-heading>`, or `symbol:<literal-name>`, with a nonempty suffix and no surrounding whitespace. `file` selects the whole file; anchors and headings select one explicit Markdown anchor or heading; symbols select one language-aware declaration (including its containing type when needed). Non-file selectors must resolve uniquely, without fuzzy matching, line-number inference, substring matching, or regular-expression execution. An unsupported language/selector is an error, not assumed valid. Planned selectors are syntax-checked but not resolved. The schema checks only that selectors are nonempty strings; these rules require the semantic checker.

## Root Fields

| Field | Meaning |
|---|---|
| `format_version` | Integer `1`; changes to this development format are independently versioned. |
| `specification` | Public `repository`, immutable `revision`, and applicable specification `version`; requirement catalog/anchors are read here. |
| `implementation` | Implementation `repository` and immutable `revision`; implementation and case locations are relative to it. |
| `coverage` | `mode`, `unallocated_sources`, and `notes`, as described below. |
| `requirements` | One record per mapped public requirement ID. |
| `cases` | Locally unique conformance-case records referenced by requirements. |
| `issues` | Locally unique issue records referenced by affected requirements. |
| `evidence` | Locally unique evidence records referenced by cases, reviews, or support claims. |

`coverage.mode` is `partial` or `catalog_complete`. `catalog_complete` means every active ID in the selected catalog has exactly one record; it does not mean every authoritative obligation has been allocated an ID. `partial` accepts omissions as reported gaps. `unallocated_sources` lists applicable public source paths containing obligations still lacking IDs; resolve these paths at the specification revision. `notes` explains mapping boundaries and remaining inventory work. Reviewers must compare this list with the applicable normative source inventory; the checker cannot discover normative units or prove the list complete. An empty list is not evidence of full coverage.

Retired or unknown IDs cannot appear in `requirements` at the selected baseline. To retain a prior claim, retain its separate historical manifest at the original revision where that ID was active. Do not rewrite an old claim to a successor ID without renewed mapping and evidence review.

## Requirement Records and Implementation Status

| Field | Meaning |
|---|---|
| `id` | Allocated active public requirement ID; catalog source and unique anchor must resolve. |
| `implementation_status` | One value from the table below. |
| `implementation_locations` | Array of `{path, selector, state}` records in the implementation baseline; `state` is `planned` or `existing`. |
| `case_ids` | Unique case IDs linking to `cases`. Shared cases are allowed across requirements. |
| `issue_ids` | Unique issue IDs linking to findings affecting this obligation; unresolved linked findings block an implemented claim. |
| `review_evidence_ids` | Review evidence recording that mapped code and cases cover the whole obligation and applicable contexts. |
| `support` | Array of scoped support records; no duplicate `(kind, scope)` pair. |
| `notes` | Limits, missing work, partial behavior, or reason for blocked/unsupported status. |

| Status | Meaning |
|---|---|
| `not_implemented` | No implementation claimed. |
| `planned` | Intended ownership or cases recorded; no implementation claimed. |
| `partial` | Some behavior exists, but coverage, validation, or review remains incomplete. |
| `blocked` | An unresolved specification issue or other stated prerequisite prevents completion. |
| `unsupported` | This implementation explicitly excludes the requirement; rationale is recorded. |
| `implemented` | The complete obligation has reviewed implementation and passing applicable conformance evidence at the declared baselines. This alone does not claim a released measurement, platform, or field support. |

An `implemented` record requires at least one existing implementation location, at least one case, all referenced cases `passed` with resolvable matching conformance evidence, at least one matching `review` evidence record, and no linked issue with disposition other than `closed`. Every mapped location must be existing. Evidence must name this requirement and the exact specification/implementation revisions. The review record must establish completeness and applicability of cases, not merely their presence. Passing a generic compilation check or one representative case cannot justify the claim. A failed/not-run/blocked applicable case, unresolved issue, missing evidence, or explicitly unsupported requirement requires a non-implemented status. Do not hide an affected issue or failing applicable case by removing its mapping; completeness remains a review obligation.

## Cases, Issues, Evidence, and Support

Case records have `id`, `location`, `scope`, `status`, and `evidence_ids`. IDs match `[A-Za-z][A-Za-z0-9._-]*` and are distinct from public requirement IDs. The `location` selects the case in the implementation baseline. `scope` describes what is exercised and under which conditions; case existence is not an executed result.

| Case status | Required interpretation |
|---|---|
| `planned` | Planned location; no result evidence permitted. |
| `not_run` | Existing case, no executed result claimed; result evidence must be empty. |
| `passed` | Existing case and at least one conformance evidence record establishing its passing result. |
| `failed` | Existing case and at least one conformance evidence record establishing its failed result. |
| `blocked` | Existing case could not run; evidence may record the blocking condition but must not assert a passing result. |

All evidence linked from cases has kind `conformance`, exact matching baselines, matching case scope, and covers every requirement referencing that case. Its `case_results` must include that case ID with the same result as its case status. Its selected content must identify the case ID, result, environment, execution inputs, and limits. A shared case must establish each linked obligation; repeating an ID does not establish coverage.

Issue records have `id`, `disposition`, `finding` (immutable `{repository, revision, path, selector}`), `resolution_references` (array of the same reference shape), and `notes`. Dispositions are `open`, `in_review`, `accepted_adoption_pending`, `rejected_or_deferred`, and `closed`, corresponding to the public issue workflow. The finding selects a real record with that identity. `closed` requires at least one public disposition/closure reference and a rationale for applicable downstream adoption or non-applicability. When accepted wording changes, it must already be present in the selected public baseline and adopted in the selected implementation baseline. Rejection does not make an unresolved conflict implementable. Tracker status alone, a merged proposal without adoption, or a private agreement is not resolution evidence.

Evidence records have `id`, `kind` (`conformance`, `review`, `platform`, or `field`), immutable `reference`, `specification_revision`, `implementation_revision`, nonempty `requirement_ids`, `scope`, and `case_results`. `case_results` contains `{case_id, result}` records, where result is `passed`, `failed`, or `blocked`; case IDs must be unique within that array and resolve to mapped cases. It is nonempty for conformance evidence and empty for other kinds. Every reported case must link back to that evidence, preventing orphan result assertions. Evidence content must support its declared kind, IDs, baselines, and scope. Revision fields must equal the root baselines, even when an evidence report itself is committed later in a separate evidence revision. Evidence references can point to another explicitly supplied public repository. Public manifests must be verifiable without private repositories. Reports must be sanitized; do not include participant data, measurement data, secrets, private deployment details, or personal paths.

The checker mechanically compares these explicit result/baseline/ID/scope assertions and resolves the selected evidence files. It does not parse arbitrary prose to infer a result or decide whether tests prove a requirement. Evidence authenticity, agreement with the report, completeness, and closure/adoption sufficiency require human review; the report must label these as review assertions rather than mechanically verified facts. Review evidence linked by a requirement must have kind `review` and include that requirement in `requirement_ids`.

A support record has `kind` (`core`, `platform`, or `field`), explicit `scope`, `status` (`unclaimed`, `unsupported`, or `supported`), and `evidence_ids`. `unclaimed` states no support claim; `unsupported` records an explicit exclusion, explained in requirement `notes`. `supported` requires an `implemented` requirement, applicable conformance and completeness review, and matching scoped evidence: `review` for `core`, `platform` for `platform`, and both `platform` and `field` for `field`. The evidence must cover that requirement and exact scope/baselines; platform scopes identify the tested versions/targets, while field scopes identify the reviewed deployment and limitations without identifying participants. Broader support than the cited evidence is invalid. Excluding a platform/field scope does not itself invalidate a core implementation claim; the complete applicable obligation must still be satisfied. An omitted support scope remains unclaimed.

## Deterministic Validation Contract

The future checker must validate in stages: strict JSON decoding, schema, explicit baseline/repository inputs, catalog integrity, record identity/references, locations, evidence consistency, then claim gates and coverage. Stop after a decoding or structural failure; do not evaluate semantic claims on a malformed object. A stage with unavailable prerequisites reports the error and skips dependent checks without guessing. Continue independent checks. Report all independent findings in deterministic order `(code, JSON Pointer, related ID)` using case-sensitive lexicographic UTF-8 byte ordering, never traversal timing or network state. Deduplicate identical findings. JSON Pointers escape `~` and `/` as defined by [RFC 6901](https://www.rfc-editor.org/rfc/rfc6901).

Each finding includes `code`, `level` (`error` or `gap`), `pointer`, `related_id` (empty when absent), and a human-readable explanation. The explanation is not a stable API. The report also identifies selected baselines and current/historical validation mode. Errors invalidate the manifest; partial coverage gaps are reported without making its metadata invalid. `catalog_complete` missing-ID gaps become errors. No success report may suppress gaps or imply semantic verification beyond the checks performed. Exit `0` means structurally/semantically valid metadata with any permitted gaps reported, `1` means invalid metadata or unjustified claims, and `2` means invalid invocation. Detailed CLI/report packaging and checker tests belong to DEV-469.

| Code | Level and deterministic rule |
|---|---|
| `DUPLICATE_MEMBER` | Error at the duplicate member pointer; reject decoded duplicate keys before schema validation. |
| `MALFORMED` | Error at the offending property or containing object for a missing/conditional property; invalid JSON uses the root pointer. Reject every violated encoding/schema/selector/repository rule. |
| `DUPLICATE_ID` | Error at each later duplicate `id` in requirements or within each case/issue/evidence catalog, even when records differ. Record IDs need only be unique within their catalog; arrays of references must contain no duplicates. Do not choose first/last-wins semantics. |
| `BASELINE_UNAVAILABLE` | Error at the unresolved repository/revision; unknown checkout mapping, missing commit, or prohibited revision prevents dependent checks. |
| `STALE_BASELINE` | Error at a root revision/version inconsistent with explicit expected baselines or applicable source declarations. |
| `UNKNOWN_REQUIREMENT` | Error at a requirement ID or evidence requirement ID absent from the selected catalog. |
| `RETIRED_REQUIREMENT` | Error at a requirement ID or evidence requirement ID retired at the selected baseline. |
| `CATALOG_INVALID` | Error at `/specification` when public allocation/source/anchor integrity fails; use the public requirement convention, not a new allocation authority. |
| `DANGLING_REFERENCE` | Error at every case/issue/evidence ID reference that has no target record. Evidence requirement IDs must also map to a requirement record in this manifest. |
| `UNREFERENCED_RECORD` | Error at a case, issue, or evidence `id` never reached from any requirement through its case, issue, review, or support links. Loose evidence cannot imply a claim. |
| `STALE_LOCATION` | Error at an existing location/reference path or selector that no longer resolves uniquely at its named revision. Planned locations receive syntax checks only. Apply this also to unallocated source paths. |
| `EVIDENCE_MISMATCH` | Error at evidence kind, baseline, requirement, scope, or declared case status inconsistent with its use/content. Unsupported verification capability must be reported explicitly, never accepted as a verified claim. |
| `CLAIM_NOT_JUSTIFIED` | Error at implementation/support status violating the claim gates, or at a closed issue lacking applicable public resolution/adoption. |
| `MISSING_REQUIREMENT` | One finding per active catalog ID absent from `requirements`, pointer `/requirements`; gap in partial mode, error in catalog-complete mode. |
| `MISSING_IMPLEMENTATION` | Gap at a non-implemented record's `implementation_locations` when no existing location is mapped. |
| `MISSING_CONFORMANCE` | Gap at a non-implemented record's `case_ids` when no case is mapped or any mapped case lacks a passing result. |
| `UNALLOCATED_REQUIREMENTS` | Gap for every listed unallocated source, plus a gap at `/coverage/notes` when inventory completeness remains unverified. Catalog completeness never suppresses these gaps. |

For repeated location tuples `(path, selector, state)` within a requirement, duplicate support `(kind, scope)`, duplicate case-result `case_id`, or duplicate reference tuples `(repository, revision, path, selector)` within an issue, report `MALFORMED` at the later item. Sharing the same implementing location or case across different requirements is valid when completeness review supports it. Compare case-sensitive values without coercion or URL/path normalization. Review of whether evidence actually proves the whole obligation is still required; a future checker must distinguish mechanically checked properties from review assertions.

## Examples and Adoption

The partial example pins public revision `72bbc985280b072e80de65ee9dc13ba600ea2ba4` and Go revision `d808f1b94e713a5f3970f8c780e0aef5b22a391d`. Its proposed code and case paths intentionally do not exist. It is valid partial metadata with missing-requirement gaps for `REQ-TRUST-0001` and `REQ-TCP-01-0001`, missing implementation/conformance for `REQ-TASK-0001`, and unallocated/inventory-review gaps. It is not a production manifest or conformance evidence.

Invalid scenarios use ordered `add`/`replace` operations with JSON Pointer paths against this example; `/-` appends. The raw-JSON duplicate-member scenario bypasses mutation. Expected findings are required subsets, not complete output snapshots; ordinary example gaps remain and independent semantic failures may add findings. The unresolved-issue scenario deliberately lacks review/passing-case evidence as well as linking an open issue: it must never be accepted as implemented. These scenarios describe future checker acceptance inputs; they are not an executed checker test suite.

Adopt the coordination decision, then this public format, then implementation guidance/manifests. Do not duplicate this schema in consumers. A future checker may validate against an explicitly supplied public checkout/schema revision without private access or network calls. Preserve prior manifests and evidence when adopting a new baseline; remap changed/retired requirements and re-evaluate affected code, cases, issues, and support claims. Format-version changes require explicit compatibility review; consumers must reject unknown versions rather than silently reinterpret them. This adoption changes no runtime schema, API, release tag, specification maturity, or support status.
