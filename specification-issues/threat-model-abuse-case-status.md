# Specification Issue: Status of the Threat Model's Abuse Cases

## Identity and Ownership

- Local finding: `GO-SPEC-ISSUE-025` in the Go [finding record](https://github.com/tv-rain/barometer-go/blob/main/docs/specification-issues.md#go-spec-issue-025-status-of-the-threat-models-abuse-cases), recorded from the residual review of the shared sources that carry no requirement ID.
- Disposition: **Accepted; status sentence merged with this record, retaining Draft `0.1.0`.** The project owner, Lev, selected alternative (a) on November 12, 2026.
- Reporter: the Go implementation agent under the task owner's instruction. Public maintainers own disposition and wording; implementation owners show coverage through the existing IDs.
- No duplicate identified.

## Affected Baselines and Requirements

- Public `tv-rain/barometer-spec` revision [`45bc424bd9829f5389b3b4494d0966e10e21da94`](https://github.com/tv-rain/barometer-spec/tree/45bc424bd9829f5389b3b4494d0966e10e21da94), Draft `0.1.0`, [Threat Model — Abuse Cases That Must Be Tested](https://github.com/tv-rain/barometer-spec/blob/45bc424bd9829f5389b3b4494d0966e10e21da94/threat-model.md#abuse-cases-that-must-be-tested), 14 items. The section is unchanged at `dc51b6d52abb414cdfd71930f442b80408f36f00`.
- Requirements: the section has no namespace or IDs. Its items restate obligations allocated in the trust, schedule, safety, input, task, proxy, limit, context, execution, linkage and bundle documents. The [requirement convention](../requirements/README.md#marking-a-normative-unit) says review checklists do not become normative by tagging.
- Implementation: `tv-rain/barometer-go` at [`c1ed38f`](https://github.com/tv-rain/barometer-go/tree/c1ed38fbb7a5ea9dd2dd3b0000eda2b95e981874) maps the underlying IDs. No native, binding or field support is established.

## Finding and Reproduction

"Must be tested" reads as a conformance obligation, but the section carries no IDs and duplicates allocated rules. It was unclear whether each item needs its own ID and traceable case, or whether the section is a checklist whose obligations are already allocated. Two items fall partly outside the library: interrupted data clearing involves the binding and host, and collector co-retention of linkage involves the collector. No runtime reproduction applies; this is a question of document status.

**Blocked:** treating the section as allocated or as fully covered in implementation traceability. **Interim handling:** none needed; the underlying IDs are authoritative. **Unaffected:** every allocated obligation the items exercise.

## Impact and Required Reviews

- **Safety and privacy:** none. The status sentence removes no test obligation: each runtime obligation keeps its existing ID and its own cases.
- **Interpretation:** not applicable.
- **Compatibility:** no field, class, bound or ID changes; Draft `0.1.0` is retained.
- **Reviews:** maintainer disposition recorded above. No further review is identified.

## Alternatives and Selected Public Resolution

1. **(a) Validation checklist (selected).** The section is declared a validation checklist; each item maps to existing runtime IDs, and implementations show coverage through those IDs. No duplicate obligations, which the convention forbids counting as independent evidence.
2. **(b) New namespace** with one ID per abuse case (14 IDs). Makes each case traceable, at the cost of duplicating allocated obligations.
3. **(c) Split.** IDs only for library-side items, with collector and host items assigned to their owners. Partial duplication with an ownership split to maintain.

Wording: one status sentence at the start of [Abuse Cases That Must Be Tested](../threat-model.md#abuse-cases-that-must-be-tested) declares the section a validation checklist whose runtime obligations are allocated to existing requirement IDs. The heading and items are unchanged. No ID is allocated or retired.

Expected evidence: implementation traceability maps each abuse case to the existing IDs and cases that exercise it; items owned by a binding, host or collector are shown by those owners.

## Ordering and Public Disposition

No architecture or responsibility boundary changes, so no coordination decision is needed. Order: public merge of this sentence and record; internal alignment only where an internal plan treats the section as allocated; the Go cross-reference from each abuse case to its existing IDs; bindings, hosts and the collector for their items.

## Adoption and Closure Evidence

Merged with this record, retaining Draft `0.1.0`; the merge revision is recorded in the Go finding record. No runtime behavior changes. No platform, field or release support is claimed.
