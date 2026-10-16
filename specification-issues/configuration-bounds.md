# Proposal: Local Host-Configuration Decoding Bounds

**Disposition:** Proposed; maintainer disposition pending
**Date:** October 16, 2026
**Related task:** [DEV-571 — Close minor Foundation assessment gaps in barometer-go](https://app.clickup.com/t/124kk1zc521)

This record asks public maintainers to dispose of local host-configuration decoding bounds selected by the Go implementation where the public contract registers no maximum. It proposes a no-text-change clarification that the bounds are explicitly local and non-normative under an existing rule. It introduces no normative limit, serialized field, version change or support claim. Opening this record does not accept its proposal.

## Identity and Ownership

- Local finding: `GO-SPEC-ISSUE-003` in the Go [specification-issue record](https://github.com/tv-rain/barometer-go/blob/main/docs/specification-issues.md#go-spec-issue-003-local-host-configuration-decoding-bounds). That link resolves after the Go change merges; it is not immutable evidence.
- Public identity: this Markdown record, reviewed through a human-created public PR. PR URL and responsible maintainer are pending.
- Reporter: the Go implementation agent under the task owner's instruction. Public maintainers own disposition; the Go implementation owner owns the local bounds and their documentation.
- Duplicates: none found. The [strict JSON decoding](strict-json-decoding.md) proposal defines the bound rule cited below but does not choose host-configuration values.

## Affected Baselines and Requirements

- Public Draft `0.1.0` at immutable revision [`83d0b10cffb37a53de120b56825b42eb226568d9`](https://github.com/tv-rain/barometer-spec/tree/83d0b10cffb37a53de120b56825b42eb226568d9). The cited decoding text is unchanged from the adopted revision `05c1364af4f9a604b617fca45f060949b557d265`.
- [REQ-JSON-0009](https://github.com/tv-rain/barometer-spec/blob/83d0b10cffb37a53de120b56825b42eb226568d9/data-formats/json-decoding.md#REQ-JSON-0009) applies registered complete-input limits, permits stricter reviewed local bounds, and requires a finite reviewed local input bound for models without a registered complete-input maximum. [REQ-JSON-0010](https://github.com/tv-rain/barometer-spec/blob/83d0b10cffb37a53de120b56825b42eb226568d9/data-formats/json-decoding.md#REQ-JSON-0010) requires bounded memory and work.
- Host-configuration sections: [Proxy](https://github.com/tv-rain/barometer-spec/blob/83d0b10cffb37a53de120b56825b42eb226568d9/library/proxy.md), [Network Context](https://github.com/tv-rain/barometer-spec/blob/83d0b10cffb37a53de120b56825b42eb226568d9/library/network-context.md) and [Result Linkage](https://github.com/tv-rain/barometer-spec/blob/83d0b10cffb37a53de120b56825b42eb226568d9/library/result-linkage.md). None registers a complete host-configuration byte, depth or node maximum, or a URL length maximum.
- Implementation: `tv-rain/barometer-go` `internal/config` at `374c8bd7a8db634ddac5f799b2894ce3d96856d5` (DEV-486 models). No runtime initialization, binding, native or platform behavior is implemented or validated.

## Finding and Reproduction

The Go configuration decoder selects these local bounds, documented in its [configuration models](https://github.com/tv-rain/barometer-go/blob/374c8bd7a8db634ddac5f799b2894ce3d96856d5/docs/configuration-models.md#defaults-validation-and-local-bounds):

| Bound | Local value |
|---|---|
| Complete configuration input | 16,384 original encoded UTF-8 bytes, including whitespace and unknown fields |
| Value depth | 8 levels |
| Value nodes | 64 |
| Endpoint URL | 2,048 decoded bytes |
| Trusted approval list | 64 entries |

The first four apply to host-supplied public configuration JSON. The approval-list bound applies to trusted internal adapter inputs, which are not a public serialized model; it is listed for completeness only.

The ambiguity is whether REQ-JSON-0009's "finite reviewed local input bound" is satisfied by implementation-local documentation and review, or whether public maintainers intend to register host-configuration maxima for interoperability. The Go synthetic tests accept a whitespace-padded empty configuration of exactly 16,384 bytes and reject the same input at 16,385 bytes with a bounds error. Another conforming implementation could accept the larger input. No measurement, runtime or device reproduction is claimed.

Affected work: none is stopped. The Go decoder already enforces the bounds before parsing and fails atomically. Interim handling keeps them as local, non-normative implementation bounds. Hosts must not rely on them as public maxima.

## Impact and Required Reviews

- Safety/privacy: the bounds limit memory and work before trust or activation. They add no destination, traffic, data, retention or linkage behavior. Raising them would increase parser exposure. Lowering them could reject valid deployment configurations and push hosts toward ad hoc workarounds.
- Measurement/interpretation: none. A configuration rejection is an operational error, not a measurement result or evidence of censorship.
- Compatibility: hosts and bindings that generate configuration larger than these bounds would fail to initialize against the Go implementation. The current public configuration sections are small and closed, so representative valid configurations are expected to fit; this is an assumption, not measured deployment evidence.
- Required reviews: public maintainer disposition. Mobile resource review applies if public maxima are registered. No legal or platform-policy effect is identified.

## Alternatives and Proposed Public Resolution

1. **No-text-change clarification (proposed).** Maintainers confirm that REQ-JSON-0009 already permits implementation-local finite bounds for models without a registered maximum, and that the Go values are local, non-normative and reviewed through the implementation's own records. Keeps the public contract minimal. Leaves cross-implementation size agreement to deployment integration.
2. Register public host-configuration maxima, such as a complete-input byte limit, in the public contract. Gives hosts a portable guarantee. Requires choosing values, a version/compatibility decision and requirement-ID allocation. It may constrain future configuration sections.
3. Retain the current text without disposition. Leaves the "reviewed" status of the Go bounds unresolved.

Proposed wording: none; alternative 1 cites the existing REQ-JSON-0009 rule. No requirement-ID or version change is proposed. Expected outcome under alternative 1: implementations document their local bounds; inputs above a local bound fail atomically with a bounded operational error.

## Ordering and Public Disposition

- Coordination decision: not needed; no architecture or responsibility boundary changes.
- Order: merge this public record first, then the Go `GO-SPEC-ISSUE-003` entry and configuration-model link. If maintainers choose alternative 2, the wording change follows its own reviewed public PR. Go adoption, internal alignment if required, and binding/host updates follow that merge.
- Maintainer disposition, rationale and date: pending.

## Adoption and Closure Evidence

- Alternative 1: closure requires the maintainer disposition citing REQ-JSON-0009 and the Go record linking it. Existing Go bound tests in `internal/config` are synthetic regression evidence only.
- Alternative 2: closure requires the merged public revision, version decision, Go adoption and conformance cases at the registered maxima.
- Pending: disposition, PR link and responsible roles.
