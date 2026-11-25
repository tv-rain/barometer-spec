# Specification Issue: Collector Account Separation and Publication Rules

## Identity and Ownership

- Local finding: none. Raised November 25, 2026 by the project owner, Lev, during the deployment privacy review of bundle collection and reporting, not by an implementation.
- Disposition: **Maintainer-selected; wording proposed in this change, pending public review and merge.** The project owner selected mandatory account separation for all deployments and the publication rules below on November 25, 2026.
- Reporter: the project owner. Public maintainers own disposition and wording; implementation owners own adoption.
- No duplicate identified. Related: [`bundle-retention-start.md`](bundle-retention-start.md) (another collector-facing privacy rule).

## Affected Baselines and Requirements

- Public `tv-rain/barometer-spec` revision [`da7517c07af7008f432b8e7bf4c4db41b87bd696`](https://github.com/tv-rain/barometer-spec/tree/da7517c07af7008f432b8e7bf4c4db41b87bd696), Draft `0.1.0`.
- Requirements: [REQ-LINKAGE-0041](../library/result-linkage.md#REQ-LINKAGE-0041) recommended avoiding application account authentication on the bundle endpoint "where the deployment permits"; [REQ-LINKAGE-0042](../library/result-linkage.md#REQ-LINKAGE-0042) permitted delivery through an account-authenticated API after a separate privacy and safety review. [REQ-BUNDLE-0035](../data-formats/result-bundle.md#REQ-BUNDLE-0035) and [REQ-CONTEXT-0041](../library/network-context.md#REQ-CONTEXT-0041) required aggregation for analysis and public reporting but set no rule for raw data release, the counting unit, small groups, or overlapping selections.
- Implementation: `tv-rain/barometer-go` maps REQ-LINKAGE-0041 and REQ-LINKAGE-0042 to a planned host and collector review case in its cross-cutting traceability. No collector is implemented in a public repository, and no runtime behavior changes.

## Finding

Account separation was optional. A deployment could deliver bundles through its account-authenticated API, and the backend could then associate every result with an account whether or not linkage was enabled. A separate review could permit it, but nothing in the public contract prevented it.

Publication rules stopped at "aggregate". They did not prohibit releasing raw results, did not say what a statistic counts, and did not address small groups or differencing. Results carry no identifier, so a statistic presented as a share of users misstates what the data can show, and a group of a few results, or the difference between two overlapping published selections, can describe one person.

**Blocked:** nothing; no implementation enforces these rules today. **Interim handling:** deployments apply the selected rules before collecting participant results.

## Impact and Required Reviews

- **Privacy:** both changes narrow what a deployment may do. Account separation removes the account association path entirely. The publication rules prohibit raw data release outside a written data-sharing agreement and bound what published statistics can reveal.
- **Interpretation:** counting results rather than people matches what unlinked results can establish, consistent with [REQ-BUNDLE-0019](../data-formats/result-bundle.md#REQ-BUNDLE-0019) and the threat model's warning against treating an installation as a person.
- **Compatibility:** no field, class, registered number, or library behavior changes; Draft `0.1.0` is retained. A host that delivered bundles through an account-authenticated API must move delivery to a separate unauthenticated endpoint. The minimum group size is set and documented per deployment; this change sets no number.
- **Reviews:** maintainer disposition recorded above. A scoped **privacy review of the selected rules** is required before merge. Deployment legal review continues separately and is not replaced by this record.

## Alternatives and Selected Public Resolution

1. **Mandatory account separation for all deployments (selected).** Retire REQ-LINKAGE-0041 and REQ-LINKAGE-0042; keep the other ingress recommendations as [REQ-LINKAGE-0053](../library/result-linkage.md#REQ-LINKAGE-0053) and state the prohibition as [REQ-LINKAGE-0054](../library/result-linkage.md#REQ-LINKAGE-0054).
2. **Keep the recommendation with a review exception.** Leaves account association available to any deployment that passes its own review.

Publication rules, new and in addition to REQ-BUNDLE-0035: [REQ-BUNDLE-0038](../data-formats/result-bundle.md#REQ-BUNDLE-0038) prohibits publishing raw bundles and results and requires a written data-sharing agreement for any sharing; [REQ-BUNDLE-0039](../data-formats/result-bundle.md#REQ-BUNDLE-0039) makes results the counting unit; [REQ-BUNDLE-0040](../data-formats/result-bundle.md#REQ-BUNDLE-0040) requires suppressing or merging groups below a documented deployment minimum; [REQ-BUNDLE-0041](../data-formats/result-bundle.md#REQ-BUNDLE-0041) requires fixed published groupings and periods and prohibits differencing selections. REQ-BUNDLE-0035 gains an editorial pointer and keeps its ID.

Expected review cases: a bundle request carrying an account token is rejected or stripped before storage; no stored result references an account; a published table labels its unit as results; a group below the deployment minimum is absent or merged; two published selections never differ by fewer results than the minimum.

## Ordering and Public Disposition

No architecture or responsibility boundary changes: collectors and hosts already own ingress and reporting. No coordination decision is needed. Order: public review, privacy review sign-off, and merge of this wording; Go traceability update replacing REQ-LINKAGE-0041 and REQ-LINKAGE-0042 with REQ-LINKAGE-0053 and REQ-LINKAGE-0054; host and collector review before participant result collection.

## Adoption and Closure Evidence

Pending: public review and merge, the privacy review, the Go traceability update, and host and collector adoption. The finding is not closed, and no platform, field, or release support is claimed.
