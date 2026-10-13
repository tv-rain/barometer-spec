# Requirement Identifiers

**Status:** Draft
**Specification version:** 0.1.0

## Purpose and Authority

Requirement IDs identify normative obligations in the public specification independently of line numbers, headings, and file locations. The marked public text remains authoritative. The [catalog](catalog.json) contains only allocation, location, and lifecycle metadata; it is not another schema or a copy of the requirements.

IDs are for documentation, code, tests, and specification issues. They do not become serialized task or result fields. An ID, an `active` catalog entry, or a passing structural check does not establish implementation, conformance, platform support, or complete requirement coverage. `active` means the obligation is present in the selected specification revision; it does not change its Draft status.

## Directory Index

- [`../traceability/`](../traceability/README.md) — development mapping format for immutable specification/implementation baselines, cases, issues, evidence, and support scope.
- [`catalog.json`](catalog.json) — public namespaces and allocated requirement identities, including future retirement records.
- [`../scripts/README.md`](../scripts/README.md) — checker, tests, invocation, and validation limits.

## Syntax and Ownership

An ID has the form `REQ-<namespace>-<number>`. Namespaces match `[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*`; numbers are four decimal digits from `0001` through `9999`. The complete ID is case-sensitive ASCII. For example, `REQ-TASK-0001` identifies an obligation, while `TCP-01` remains a measurement code. `REQ-TCP-01-0001` is a requirement within that measurement's allocated namespace.

The catalog lists each namespace's scope and owning role. Public specification maintainers approve namespace allocation and requirement changes through public specification review. Contributors propose the next number above every allocated number in that namespace, including retired entries; gaps are not reused. Concurrent proposals must reconcile against the current target branch before merge. Allocate a new reviewed namespace if a namespace exhausts its numbers. Namespace names are permanent identity components, even when the owning document moves or changes title.

Other repositories consume these public IDs; they do not allocate them independently or give an internal scenario public normative status. Issue IDs, conformance-case IDs, measurement IDs, and requirement IDs are distinct identifiers.

## Marking a Normative Unit

Give each independently testable obligation one ID. Tightly coupled conditions and their required effect may remain one unit. Do not attach one ID to an entire document or unrelated obligations. Prose without the word “must”, table constraints, and required-field rules may be normative; examples, planning, and review checklists do not become normative merely by being tagged.

Place a standalone explicit anchor and visible label immediately before the existing paragraph, list item, list, or table row group it identifies:

```markdown
<a id="REQ-TASK-0001"></a>

**REQ-TASK-0001:**

Unknown top-level fields are rejected.
```

The example is instructional; fenced examples do not define or consume IDs. Outside fences, the anchor must use exactly this syntax and occupy its own line. The next nonblank line must be `**<ID>:**`, followed by the normative unit. Each anchor occurs once, at the catalog's `source` path relative to the public repository. When tagging table constraints, put the marker before the table and keep the identified row group unambiguous; split unrelated constraints before allocating separate IDs. Human review determines the unit's boundaries and meaning.

## Catalog Format

The JSON root has exactly `format_version` (integer `1`), `namespaces`, and `requirements`. Namespace objects have exactly nonempty `owner` and `scope` strings. Requirement records have exactly `id`, `status`, `source`, `successors`, and `reason`:

| Field | Meaning |
|---|---|
| `id` | Globally unique allocated ID in a declared namespace. |
| `status` | `active` or `retired`; independent of specification maturity. |
| `source` | Repository-relative Markdown path to the unique explicit anchor. No absolute paths, parent traversal, or symlinks. |
| `successors` | Empty for active IDs; zero or more allocated replacement IDs for retired IDs. No duplicates, self-reference, or cycles. |
| `reason` | Empty for active IDs; nonempty retirement explanation for retired IDs. |

## Editing and Lifecycle

- **Editorial change or move:** Retain the ID when the obligation and acceptance boundary are unchanged. Move the anchor with the text and update `source`; update current human-readable links in consumers. Old revisions remain available through Git. Do not derive identity from a heading, paragraph number, or filename.
- **New obligation or material change:** Allocate a new ID when accepted behavior changes. Retire the old ID when it no longer applies in the current specification, recording the reason and successor. Preserve applicable specification-version review independently of ID allocation.
- **Split or merge:** Retire the old ID or IDs and allocate new IDs for the resulting obligations. List the successor IDs on each retired record. Editorial restructuring without a semantic split does not require new IDs.
- **Removal:** Retain a retired record with an empty successor list and a reason. Retain its anchor with the next nonblank line `**<ID> (retired):**` and explanatory prose stating that it is historical, not a current obligation. It may move to a public retirement document, updating `source`.
- **Never reuse:** Keep every merged allocation, including retired IDs. Do not reactivate retired IDs, renumber existing IDs, or assign an old identity to unrelated text. Compare against the prior catalog when reviewing later changes. Semantic reuse still requires human review.

## Consumer References

Use a human-readable link to the public document's explicit ID anchor. Add a standalone machine-readable comment near each traceability record:

```markdown
<!-- requirement-ref: REQ-TASK-0001 -->
[REQ-TASK-0001](../data-formats/task.md#REQ-TASK-0001)
```

In Go source or tests use a standalone `// requirement-ref: REQ-TASK-0001` comment. One ID per comment is required. The checker validates these explicit reference comments, not arbitrary prose mentions or inferred test names. Historical citations use `requirement-history` instead of `requirement-ref`; they may resolve to active or retired allocations. Current `requirement-ref` comments must resolve to active IDs. Historical citations must explain why they are historical and cite the immutable revision that supplied the original text; the checker cannot establish that explanation's accuracy.

A review, test report, or implementation claim must identify the public repository, applicable specification version, immutable commit or immutable release tag, requirement ID, and evidence location. A branch URL is useful during review but is not an immutable baseline. A single document may declare a shared baseline for several references. This initial convention adds no supported implementation and deliberately makes no completed conformance claim.

## Initial Adoption and Limits

The initial catalog covers one task-format obligation, one trust-contract obligation, and one measurement obligation. All other normative text remains authoritative despite lacking an ID. The separate source inventory and later comprehensive mapping must identify coverage gaps; the checker does not infer requirements by searching for modal verbs.

The checker detects duplicate or malformed definitions and reference comments, undeclared namespaces, catalog entries without their source anchors, source anchors without catalog entries, unresolved references, invalid current references to retired IDs, and invalid successor relationships. With a prior catalog it also detects deleted allocations, reactivation, and non-monotonic allocation. It does not prove semantic stability, public behavior, completeness, or runtime conformance.
