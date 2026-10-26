# Resolved-Address Validation Behind a Hostname CONNECT Proxy

**Disposition:** Maintainer direction accepted; wording prepared for review, merge and downstream adoption pending
**Date:** October 26, 2026
**Related task:** [DEV-659 — Check resolved addresses and redirect targets against registrations before contact](https://app.clickup.com/t/124kk1zcw4j)

The project owner and public maintainer, Lev, selected fail-closed hostname CONNECT on October 26, 2026. This is alternative 3 of the original proposal, presented as option 1 in the decision discussion. Version `0.1.0` permits only approved explicit-IP destination authorities; a future hostname enforcement capability requires a separately reviewed contract. This record does not establish Go implementation, completed downstream reviews or runtime support.

## Identity and Evidence

- Local finding: [GO-SPEC-ISSUE-015](https://github.com/tv-rain/barometer-go/blob/d8310854460ebf83f264cbdd8edcb4db630c7743/docs/specification-issues.md#go-spec-issue-015-resolved-address-validation-behind-a-hostname-connect-proxy), published through [Go PR #78](https://github.com/tv-rain/barometer-go/pull/78).
- Original public proposal: [public PR #28](https://github.com/tv-rain/barometer-spec/pull/28), immutable publication revision [`f9d4348a5cc7963e81887a20d8dae887e927bbd6`](https://github.com/tv-rain/barometer-spec/tree/f9d4348a5cc7963e81887a20d8dae887e927bbd6). Its alternatives and then-pending statements are historical; that publication did not select a rule.
- Coordination decision: `tv-rain/barometer`, `docs/decisions/0013-explicit-ip-only-proxy-connect.md`, prepared on `agent/dev-659-fail-closed-hostnames`; immutable publication and merge evidence pending. The coordination decision must merge before this normative contract is adopted.
- Responsible public maintainer: the project owner, Lev. DEV-659 owns Go adoption. Native, binding and host adoption belong to their implementation owners when applicable.
- Duplicates: none identified. The separate [proxy-compatibility admission finding](proxy-compatibility-admission-class.md) supplies the existing rejection class and precedence; it does not establish visibility of proxy-side DNS answers.

## Finding and Affected Baseline

At public Draft `0.1.0` revision [`32062c4bafcc29f5050ca6b78423f2acaefdde56`](https://github.com/tv-rain/barometer-spec/tree/32062c4bafcc29f5050ca6b78423f2acaefdde56), [REQ-TRUST-0016](https://github.com/tv-rain/barometer-spec/blob/32062c4bafcc29f5050ca6b78423f2acaefdde56/library/task-trust.md#REQ-TRUST-0016) requires address and redirect checks immediately before contact, while the historical REQ-PROXY-0019 and REQ-PROXY-0026 permit hostname CONNECT with resolution behind the proxy. REQ-PROXY-0037 keeps prohibited targets ineligible.

The [inspected Go proxy dialer](https://github.com/tv-rain/barometer-go/blob/3c9a3ab9d5e2a3fa30d987b8398d3dde48d4469c/internal/execution/proxy.go) sends a bounded CONNECT exchange without pre-contact destination-address information. A permitted hostname could resolve behind the proxy to a prohibited address. An authority check cannot prove that address policy was applied. Local DNS may differ from the proxy's answer and disclose names on the access network; checking after CONNECT is too late to prevent contact.

The original proposal's synthetic reasoning used two proxy scripts accepting `target.example:443` with identical successful responses but different allowed/prohibited selected addresses. It was reasoning, not an executed conformance test or evidence of production exposure. The same visibility gap applies to redirects and mixed proxy-side resolution sets.

## Maintainer Disposition

**Accepted direction:** refuse hostname CONNECT before contact, retaining explicit-IP destinations only where the registered test, matched registrations and local address policy permit them. No host assertion or task field can enable hostname tunnels. This narrows coverage while retaining Barometer's enforcement responsibility and avoiding added DNS traffic.

The prepared normative text makes the following behavior explicit:

- [REQ-PROXY-0043](../library/proxy.md#REQ-PROXY-0043) replaces REQ-PROXY-0019: explicit-IP destination authorities only, checked before every tunnel; no hostname lookup, rewriting or direct fallback to make the operation eligible. TLS SNI inside an explicit-IP tunnel remains separate from the CONNECT destination.
- [REQ-PROXY-0044](../library/proxy.md#REQ-PROXY-0044) replaces REQ-PROXY-0026: HTTP-01 proxy execution requires `address_family: auto` and an explicit-IP URL host; bootstrap-IP resolver tests retain their existing TLS hostname authentication; NET-05 rejects the whole profile if any step is incompatible.
- [REQ-PROXY-0045](../library/proxy.md#REQ-PROXY-0045) replaces REQ-PROXY-0023: a proxy context endpoint with a hostname is unavailable without contact; one eligible explicit-IP fallback may be tried through the same proxy generation. Existing context-availability rules govern continuation. Direct hostname endpoints and initialization validity are unchanged.
- [REQ-CONTEXT-0043](../library/network-context.md#REQ-CONTEXT-0043) replaces REQ-CONTEXT-0020 with endpoint eligibility checks before primary/fallback requests and compliant-cache reuse.
- [REQ-PROXY-0046](../library/proxy.md#REQ-PROXY-0046) replaces REQ-PROXY-0042 with admission, pre-attempt and per-dial enforcement: initial incompatibility is `task_schema_invalid` at admission; an incompatible admitted task detected before an attempt is `not_run` / `proxy_path_unsupported`; a prohibited measurement dial ends with `proxy_path_unsupported` and state `not_run` or `incomplete` according to whether the test has started under REQ-RESULT-0051; refusal itself does not start it. The shared gate cannot be bypassed by a runner. Context lookup rejection alone follows the context rules.
- [REQ-HTTP-01-0051](../tests/http-01.md#REQ-HTTP-01-0051) makes hostname proxy redirects `redirect_rejected` without contact, using existing minimized observations. Direct HTTP-01 hostname behavior and authenticated TLS remain unchanged.

REQ-TRUST-0016 and REQ-PROXY-0037 remain active: no destination-policy guarantee is weakened. REQ-TRUST-0039 retains its class and step-8 precedence, with its reference updated to the replacement compatibility table. No new execution reason, admission error, serialized field or public capability is introduced.

## Compatibility, Version and Review

Draft `0.1.0` is retained under the public repository's current version policy and the coordination decision. Schema and test version values are unchanged. This is a deliberate narrowing of the Draft proxy contract; hosts, task producers and stored configurations must not assume unchanged compatibility. The retired IDs retain their anchors and catalog histories; no allocation is reused.

Proxy HTTP-01 coverage is reduced, including redirects to registered hostname destinations. Explicit-IP HTTPS still requires valid certificate authentication and all existing URL/registration rules; a hostname target cannot be rewritten to regain coverage. Hostname-based proxy context acquisition becomes unavailable, which may prevent tasks with required egress fields from running. Those missing observations must not be interpreted as censorship. No endpoint discovery, new network probe, identifier, retained address, telemetry or relaxed resource bound is introduced.

The maintainer selected the safety direction; this record does not assert that all required reviews passed. Before Go adoption, align internal trust/proxy/HTTP-01/context validation and record safety/privacy review of the narrowed compatibility, failure mapping and context consequences. Go implementation review must establish shared enforcement and no bypass. Binding/host review must assess affected configuration, task production and release ordering. Existing deployment legal/platform-policy gates remain applicable; this change authorizes no participant deployment.

Proxy-side enforcement is deferred because the current interface cannot establish it. Authority-only validation is rejected as the initial default because it accepts unobservable destination-policy risk. Local DNS and IP substitution are rejected because they change the path and may disclose target names. The existing compromised-host/proxy threat limitations remain: an explicit-IP request is not proof that a malicious proxy obeyed it.

## Ordering and Closure Evidence

1. Publish and merge the coordination decision, then merge this wording, requirement catalog changes and disposition. Final work approval, human-created PRs and immutable merge evidence remain pending.
2. Align required internal review and case plans against the merged public revision, recording review evidence rather than treating the direction selection as review completion.
3. Implement the Go shared execution/path gate, admission compatibility and failure mapping under DEV-659, with synthetic evidence for allowed/prohibited explicit IPs, blocked hostname initial and late dials, redirects, direct mixed-resolution cases, expiry/path restrictions, context fallback/unavailability, bounds/cancellation and no direct fallback. Run `make check` and update the Go finding against the accepted baseline.
4. Assess binding/host and producer adoption, and record bounded remaining work. A future proxy-side enforcement capability is separate work requiring another reviewed contract.

The production target-validation rows of `CC-PROXY-PRIVACY-SAFETY-AND-INTERPRETATION` remain pending. Proxy hostname cases must demonstrate refusal before contact, not claim inspection of proxy-side addresses. No whole-family, independent interpretation, platform, field or release claim is promoted. GO-SPEC-ISSUE-015 and DEV-659 remain open until required adoption and evidence exist; preparing or merging these documents alone does not complete them.
