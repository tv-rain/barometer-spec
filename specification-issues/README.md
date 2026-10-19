# Specification Issue Workflow

## Purpose and Authority

Use this contributor procedure for ambiguous, conflicting, unsafe, or impractical specification behavior found during implementation, validation, or consultation. Public specifications remain authoritative. Proposals, local interpretations, internal reviews, examples, and tests do not change them.

This is development guidance, not a runtime contract. It introduces no serialized fields, specification version change, or support claim. Public contributors can use it without private material or a particular tracker.

## Directory Index

- [`configuration-bounds.md`](configuration-bounds.md) — accepted no-text-change clarification that implementation-local host-configuration decoding bounds are permitted under REQ-JSON-0009; closed October 16, 2026.
- [`editorial-consistency-0-1-0.md`](editorial-consistency-0-1-0.md) — open proposal to correct three test-level inconsistencies with shared rules (DNS-01 window maximum, `network_changed` failure rows, address prohibitions in DNS answers); no behavior change proposed.
- [`observation-vocabularies.md`](observation-vocabularies.md) — approved closed DNS/TLS wording, coarse unknown handling, incomplete-field clarification and ordered adoption; merged at `a944ed6`, downstream adoption pending.
- [`risk-factors-timezone-domains.md`](risk-factors-timezone-domains.md) — accepted wording requiring at least one `risk_factors` entry for `medium`, `high` and `unknown` risk (REQ-SAFETY-0031) and closing `timezone` to `local` (REQ-SCHEDULE-0043), retaining Draft `0.1.0`; accepted October 19, 2026, merge and Go adoption pending.

- [`strict-json-decoding.md`](strict-json-decoding.md) — approved strict runtime JSON wording and version disposition, synthetic evidence, compatibility limits, and ordered adoption; merged at `05c1364`, downstream adoption pending.
- [`template.md`](template.md) — portable record covering evidence, impact, alternatives, public review, ordering, and adoption.

## Recording a Finding

Search existing findings first and link duplicates. Use the template in the discovering repository or its tracker. Retain established local IDs; a public issue URL or reviewed repository record supplies public identity. Requirement IDs, measurement codes, conformance-case IDs, local findings, and tracker IDs are distinct.

Identify the public repository, applicable specification/test/schema versions, maturity, and immutable commit or release tag. Cite allocated [requirement IDs](../requirements/README.md) and public anchors. For unallocated obligations, cite exact sections/fields at the immutable revision and mark the gap; the partial catalog does not exclude authoritative requirements. Public maintainers allocate/retire IDs during the reviewed specification change.

Use sanitized synthetic reproduction and bounded evidence. Separate documented rules, observed behavior, assumptions, and unresolved questions. Do not publish credentials, participant data, private endpoints, identifying device details, sensitive logs, or private deliberations. Unknown impact must be explicit; missing evidence does not establish safety.

Stop affected implementation when the finding requires inventing, weakening, or extending observable behavior. Record the blocked scope and interim handling under the existing contract without selecting a new runtime fallback. Unaffected approved work may continue. Escalate urgent safety concerns to maintainers for containment review; urgency does not authorize silently changing the contract.

## Public Review and Ownership

The reporter prepares a sanitized public proposal and links the local finding. Use a public repository issue or a Markdown record reviewed through a public PR. Opening a proposal does not authorize implementing it. Private evidence may inform review, but public reasoning must be sufficient and accepted behavior must be understandable without private access.

Public specification maintainers own disposition and normative wording. They identify responsible reviewers and affected implementation owners. Evaluate compatibility, version selection, requirement-ID lifecycle, safety/privacy, traffic distinctiveness, resource bounds, platform behavior, and alternative non-censorship explanations where applicable. Record required specialist reviews, findings/evidence, or reasons they do not apply. An unchecked review is not completed. Existing deployment legal/platform-policy gates remain applicable.

## Issue Lifecycle

These dispositions are separate from tracker statuses. Record dates, responsible roles, evidence links, and remaining work for transitions.

| Disposition | Required evidence and next step |
|---|---|
| Open | Finding, affected baseline, blocked scope, and missing evidence recorded. |
| In review | Public proposal, alternatives, responsible maintainer/review roles, and required reviews identified. |
| Accepted; adoption pending | Maintainer approval/disposition linked. If text changes, record the merged public revision and version decision before adoption; approved but unmerged wording remains pending. |
| Rejected or deferred | Public rationale and interim disposition recorded. Existing contract remains authoritative; affected work stays blocked if it still cannot conform safely. |
| Closed | Accepted resolution is available and applicable downstream implementation/conformance, review alignment, and compatibility evidence are linked. No-change clarification cites the existing rule and public disposition. Rejection, duplicate, or non-applicable downstream work has an explicit closure rationale and any still-blocked follow-up. |

Do not close an accepted finding solely because its specification PR merged. Reopen or link a follow-up when later evidence invalidates its resolution; retain prior dispositions and baselines.

## Cross-repository Ordering

1. Review a coordination architecture decision first when responsibility boundaries or long-lived architecture change.
2. Review and merge the public specification clarification/change. Record the immutable revision, affected versions, compatibility decision, and requirement-ID lifecycle. Editorial changes retain IDs; materially changed obligations follow the public replacement convention.
3. Align required internal reviews and validation plans with that revision without adding private-only normative requirements.
4. Implement Go behavior and conformance cases against the accepted baseline.
5. Update native/Flutter bindings, then host integration and deployment guidance as applicable.
6. Release in the recorded compatibility order; identify negotiation, migration, and blocked combinations. Matching version numbers do not imply compatibility.

Linked review branches may be prepared in parallel only with explicit bases and dependencies. Merge public changes before adopting changed behavior downstream. No-text-change clarification still requires public maintainer disposition and an immutable citation to the existing rule. Repositories retain independent branches, commits, reviews, and release histories.

## Resolution and Validation

Link accepted wording or no-change clarification, required reviews, immutable specification baseline, requirements, implementation revisions, conformance cases/results, and outstanding follow-ups. Public disposition and implementation are separate facts. Planned cases, structural checks, compilation, and synthetic tests do not establish field/platform support.

Check every template section, links, indexes, and whitespace with `git diff --check`. Use the [requirement checker](../scripts/README.md) for changed definitions/references and each affected implementation repository's required checks. Record validation scope and limitations without reporting unresolved findings as resolved.
