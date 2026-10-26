# Proposal: Resolved-Address Validation Behind a Hostname CONNECT Proxy

**Disposition:** Open (proposal; no specification text changed)
**Date:** October 26, 2026
**Related task:** [DEV-659 — Check resolved addresses and redirect targets against registrations before contact](https://app.clickup.com/t/124kk1zcw4j)

This record asks maintainers to define the execution-time address-validation boundary when a hostname is resolved behind an HTTP CONNECT proxy. Checking the requested authority does not establish which address the proxy contacts. The alternatives below are proposals; this record accepts none and changes no runtime contract.

## Identity and Ownership

- Local finding: GO-SPEC-ISSUE-015 in `tv-rain/barometer-go`, `docs/specification-issues.md`, heading **GO-SPEC-ISSUE-015: Resolved-Address Validation Behind a Hostname CONNECT Proxy**. The finding is prepared on `agent/dev-659-target-validation-finding`; an immutable finding link is pending commit approval and publication.
- Public identity: this record, prepared on `agent/dev-659-proxy-target-validation`; human-created public PR and maintainer disposition pending.
- Reporter: the Go implementation agent under the task owner's instruction. Responsible public maintainer: the project owner, Lev. Implementation owner: the Go task owner under DEV-659; binding and host adoption belong to their implementation owners when applicable.
- Duplicates: none identified in the public issue index or Go findings record. Related: [`proxy-compatibility-admission-class.md`](proxy-compatibility-admission-class.md) covers admission compatibility, not visibility of proxy-side DNS answers.

## Affected Baselines and Requirements

- Public repository: `tv-rain/barometer-spec`, Draft `0.1.0`, immutable revision [`32062c4bafcc29f5050ca6b78423f2acaefdde56`](https://github.com/tv-rain/barometer-spec/tree/32062c4bafcc29f5050ca6b78423f2acaefdde56).
- [REQ-TRUST-0016](https://github.com/tv-rain/barometer-spec/blob/32062c4bafcc29f5050ca6b78423f2acaefdde56/library/task-trust.md#REQ-TRUST-0016) requires every address and redirect target to satisfy the registered test and local address policy immediately before contact; resolution and redirects do not extend authority.
- [REQ-PROXY-0019](https://github.com/tv-rain/barometer-spec/blob/32062c4bafcc29f5050ca6b78423f2acaefdde56/library/proxy.md#REQ-PROXY-0019) requires a hostname CONNECT authority and resolution behind the proxy when a compatible test supplies only a hostname. Explicit-IP tests use that IP in CONNECT.
- [REQ-PROXY-0026](https://github.com/tv-rain/barometer-spec/blob/32062c4bafcc29f5050ca6b78423f2acaefdde56/library/proxy.md#REQ-PROXY-0026) permits HTTP-01 over a hostname CONNECT tunnel with `address_family: auto`. [REQ-PROXY-0018](https://github.com/tv-rain/barometer-spec/blob/32062c4bafcc29f5050ca6b78423f2acaefdde56/library/proxy.md#REQ-PROXY-0018) requires a new tunnel on the same proxy generation for an accepted redirect.
- [REQ-PROXY-0037](https://github.com/tv-rain/barometer-spec/blob/32062c4bafcc29f5050ca6b78423f2acaefdde56/library/proxy.md#REQ-PROXY-0037) keeps prohibited targets ineligible through a proxy. [REQ-HTTP-01-0018](https://github.com/tv-rain/barometer-spec/blob/32062c4bafcc29f5050ca6b78423f2acaefdde56/tests/http-01.md#REQ-HTTP-01-0018) and [REQ-HTTP-01-0029](https://github.com/tv-rain/barometer-spec/blob/32062c4bafcc29f5050ca6b78423f2acaefdde56/tests/http-01.md#REQ-HTTP-01-0029) require redirect safety validation and registration.
- Implementation baseline: `tv-rain/barometer-go` at [`3c9a3ab9d5e2a3fa30d987b8398d3dde48d4469c`](https://github.com/tv-rain/barometer-go/tree/3c9a3ab9d5e2a3fa30d987b8398d3dde48d4469c). This is source-inspection evidence, not a release or conformance claim. Production target validation, registered measurement runners, native/binding adoption and field behavior are unimplemented or unvalidated in this scope.

## Finding and Reproduction

A requested hostname and port can match a registration, while resolution behind the proxy selects an address that local address policy would prohibit. The current CONNECT contract exposes no pre-contact list of those addresses and no address-policy enforcement acknowledgment. Checking a local DNS answer would not establish which address the proxy selects and would introduce a different DNS path. Checking after CONNECT would be too late to prevent contact.

Observed implementation: [`proxyDialer.DialContext`](https://github.com/tv-rain/barometer-go/blob/3c9a3ab9d5e2a3fa30d987b8398d3dde48d4469c/internal/execution/proxy.go) validates the syntax of the authority, connects to the configured loopback proxy, sends CONNECT and accepts a bounded successful response. It has no destination-address information from the proxy. [`directDialer.DialContext`](https://github.com/tv-rain/barometer-go/blob/3c9a3ab9d5e2a3fa30d987b8398d3dde48d4469c/internal/execution/direct.go) delegates resolution and connection to `net.Dialer`; execution-time registration/address checks do not yet exist. This finding does not assert a production exposure: the source evidence establishes the missing enforcement boundary.

Synthetic reasoning example, **not an executed test**:

1. A reviewed synthetic registration permits `https://target.example/` over the proxy path. Barometer sends the authority `target.example:443` to a scripted loopback proxy.
2. Consider two proxy scripts returning the same successful CONNECT response: one selects an address allowed by local policy; the other selects a prohibited loopback or private address. No external endpoint is needed to model either script.
3. The current exchange gives Barometer the same pre-tunnel information in both cases. An authority check therefore cannot distinguish them or establish the address check required by a literal reading of REQ-TRUST-0016.
4. A registered HTTPS redirect to a second hostname has the same gap on its new tunnel. A mixed allowed/prohibited proxy-side resolution set is equally unobservable.

Assumption: an ordinary hostname CONNECT proxy may resolve using a different resolver or network view from the device. The specification itself identifies the DNS-path difference. Whether the reviewed host-managed proxy must enforce Barometer's destination policy, or whether a requested-authority check is the intended limit, is unresolved.

Affected work: the proxy resolved-address guarantee and its target-validation evidence under DEV-659 cannot be completed under an invented rule. DEV-659's common enforcement design remains pending disposition because its direct and proxy guarantees must be stated consistently. This proposal changes no current runtime behavior, adds no probe or fallback, and does not enable a production runner. Explicit-address validation, direct-path checks and redirect-registration checks are conceptually separable and may proceed under a separately recorded plan; they would not resolve this finding or complete DEV-659. Unrelated approved work may continue.

## Impact and Required Reviews

- Safety and trust: a permitted hostname can resolve to a prohibited destination behind the proxy. An authority check alone cannot prove that the proxy avoided that destination. Accepting that limitation, assigning enforcement to the host-managed proxy, or disabling hostname tunnels each needs public maintainer and safety review. Neither this record nor task approval completes those reviews.
- Privacy and resources: local pre-resolution would add DNS traffic, potentially disclose proxy-only target names on the access network, consume time and energy, and still not pin the proxy's selected address. No new lookup, identifier, retained address, telemetry, retention or linkage is proposed here. Any new exchange or capability needs bounded time, bytes, cancellation and failure semantics.
- Measurement and interpretation: replacing a hostname authority with a locally resolved IP changes the specified proxy DNS path. Filtering or rejecting hostname tunnels reduces coverage. Proxy success after direct failure is not proof of censorship; different DNS answers, routing, endpoint availability and proxy behavior remain alternative explanations.
- Compatibility and APIs: disabling hostname CONNECT changes the compatible HTTP-01 surface; a new proxy enforcement capability changes the host/proxy contract. Authority-only enforcement would require an explicit limitation and consistency review of REQ-PROXY-0037. There is no schema, public API or version change in this record. Maintainers must decide compatibility and versioning for the selected resolution.
- Required roles: public specification maintainer; safety/privacy reviewer for the selected address-enforcement boundary; Go implementation reviewer; host/proxy integration owner if enforcement is delegated. Platform/binding review is required if capabilities or configuration change. All are pending; independent interpretation review remains separate from automated cases. No new deployment or participant processing is authorized; existing deployment legal/platform-policy gates remain applicable.
- Public-safe evidence: published rules, source inspection and the synthetic reasoning above suffice to describe the finding. No private evidence or deployment details are included.

## Alternatives and Proposed Public Resolution

1. **Define requested-authority validation as the library's boundary for hostname CONNECT.** Barometer checks the normalized authority, the complete applicable registration and each redirect before sending CONNECT, and makes no claim to have inspected proxy-side addresses. Public text must explicitly reconcile this limitation with REQ-TRUST-0016 and REQ-PROXY-0037. It preserves the specified DNS path but leaves a residual destination-policy risk requiring safety acceptance; hostname approval cannot be described as proof that resolved destinations were checked.
2. **Require a reviewed proxy-side enforcement capability.** Specify how trusted local address policy reaches the proxy and is enforced before every attempted destination connection, including retries, mixed answers and redirects, and how Barometer establishes capability before contact. This can preserve remote DNS, but it introduces a host/proxy responsibility and capability contract, failure mapping and review requirements absent from the current HTTP CONNECT interface. A success response alone is insufficient evidence.
3. **Fail closed for hostname CONNECT until such enforcement exists.** Keep explicit approved IP authorities available where the registered test permits them. This avoids claiming an unobservable address check, but narrows HTTP-01 compatibility and needs explicit admission/execution behavior and a compatibility decision. It must not cause a direct fallback or a substituted test target.
4. **Resolve locally and CONNECT to a checked IP.** Changes REQ-PROXY-0019 and the HTTP-01 path contract and may leak target names on the access network. It is a behavior change requiring review, not an implementation shortcut or a permitted fallback under the current contract.
5. **Retain the text without clarification.** A maintainer may identify an existing rule that settles the boundary, with an immutable citation and rationale. Without such disposition, the affected implementation and guarantee remain blocked.

Proposed target sections: Task Trust — Target Registration (REQ-TRUST-0016); Proxy — HTTP CONNECT behavior, initial test compatibility and privacy/safety (REQ-PROXY-0019, REQ-PROXY-0026, REQ-PROXY-0037); affected HTTP-01 redirect rules if their guarantees change. Exact normative wording is pending selection of the boundary; none is adopted in this proposal. A maintainer disposition must state what is checked before contact, who enforces any unobservable address policy, what happens when enforcement cannot be established, and what limitation remains.

Requirement-ID lifecycle and version: no IDs are allocated or retired here. Maintainers decide whether a clarification preserves IDs or a changed obligation needs replacement IDs, and whether Draft `0.1.0` remains appropriate. No unchanged-version compatibility is assumed.

Expected cases after disposition: registered/unregistered hostname and explicit-IP authorities; prohibited address classes; initial and redirect contacts; mixed resolution sets; expiry/path restrictions; absent or failed enforcement capability if selected; cancellation and bounds; zero prohibited target contacts and no direct fallback. Proxy-side allowed/disallowed resolution cases must prove the selected enforcement boundary or explicitly record unobservability, rather than treating an authority-only test as resolved-address evidence. These are planned cases, not executed conformance evidence.

## Ordering and Public Disposition

- Coordination decision: none is made by this proposal. Delegating destination-policy enforcement to the host/proxy or otherwise changing responsibility boundaries requires a coordination decision before public contract adoption; maintainers assess that need for the selected alternative.
- Human-created public PR, maintainer disposition, rationale/date and merged immutable revision: pending. Approval to prepare this proposal is not contract acceptance.
- After disposition: merge accepted public wording or record a no-text-change disposition with an immutable citation; align required internal trust/proxy validation and safety reviews; implement the Go shared gate and conformance cases under DEV-659; then adopt affected bindings and host integration. No internal repository is edited by this proposal. Public disposition and required alignment precede Go behavior changes; release ordering follows the selected capability/compatibility decision.
- If rejected, deferred or superseded: record the rationale, retain the original baselines and local finding, and name any remaining blocked guarantee. Do not silently substitute local DNS, broaden target authority or mark DEV-659 complete.

## Adoption and Closure Evidence

- Accepted public rule and immutable baseline: pending.
- Required safety/privacy review and internal validation-plan alignment: pending, or a reviewed reason for non-applicability.
- Go implementation revision and DEV-659 acceptance evidence, including the production target-validation rows of `CC-PROXY-PRIVACY-SAFETY-AND-INTERPRETATION`: pending. The whole family and its independent interpretation review are not promoted by this proposal.
- Binding/host capability adoption, compatibility/release order and bounded follow-ups: pending determination after disposition.
- Closure: open; responsible maintainer disposition and downstream evidence or explicit non-applicability are required. No runtime, platform, field or release support is claimed.
