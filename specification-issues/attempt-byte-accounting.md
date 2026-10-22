# Proposal: Bytes Counted Toward Attempt Byte Limits

**Disposition:** Accepted; adoption pending: alternative (a) counting every byte Barometer writes to or reads from a TCP stream, the plaintext side of a TLS session, or a UDP datagram payload, including HTTP headers, DNS messages and length prefixes, and excluding TLS, TCP/IP and proxy transport framing, the loopback `CONNECT` exchange, platform resolver traffic and Network Context acquisition
**Date:** October 22, 2026
**Related task:** [DEV-580 — Obtain public disposition for GO-SPEC-ISSUE-005 (bytes counted toward attempt byte limits)](https://app.clickup.com/t/124kk1zcaaf)

This record asks public maintainers which bytes count toward `max_bytes_sent` and `max_bytes_received` and toward the NET-05 aggregate byte limits. The current text excludes HTTP and DNS "overhead", although HTTP headers and DNS messages are the data several tests send. It changes no registered number, field, state or reason and makes no support claim. Opening this record did not accept its proposal; the [maintainer disposition](#maintainer-disposition--october-22-2026) below did. Sections before it are the proposal as reviewed. The accepted wording is included in the same public change as this record.

## Identity and Ownership

- Local finding: [GO-SPEC-ISSUE-005](https://github.com/tv-rain/barometer-go/blob/d53bb1477169b31563c46b0b2a2106422702ea85/docs/specification-issues.md#go-spec-issue-005-which-bytes-count-toward-attempt-byte-limits) in the Go specification-issue record, raised October 16, 2026 under DEV-573 from the DEV-572 case-plan triage.
- Public identity: this Markdown record, once reviewed through a public PR. Responsible maintainer: the project owner, Lev.
- Reporter: the Go implementation agent under the task owner's instruction. Public maintainers own disposition and wording. The Go implementation owner owns adoption.
- Related: [Proxy compatibility admission class](proxy-compatibility-admission-class.md) concerns proxy admission, not byte accounting. Duplicates: none found.

## Affected Baselines and Requirements

- Public Draft `0.1.0` at immutable revision [`a7647504979d479905e495e46d6d473ff7b06994`](https://github.com/tv-rain/barometer-spec/tree/a7647504979d479905e495e46d6d473ff7b06994). The finding was raised against [`a944ed6`](https://github.com/tv-rain/barometer-spec/tree/a944ed6c389fec9f0d089f0044ead6fe845328b1); the cited text is unchanged between the two revisions.
- Requirements at `a764750`:
  - [REQ-LIMIT-0003](https://github.com/tv-rain/barometer-spec/blob/a7647504979d479905e495e46d6d473ff7b06994/library/registered-limits.md#REQ-LIMIT-0003): byte limits refer to "encoded application data" and are not exact on-wire limits because DNS, TCP, TLS, HTTP and proxy layers may add overhead.
  - [REQ-LIMIT-0006](https://github.com/tv-rain/barometer-spec/blob/a7647504979d479905e495e46d6d473ff7b06994/library/registered-limits.md#REQ-LIMIT-0006) and [REQ-EXECUTION-0012](https://github.com/tv-rain/barometer-spec/blob/a7647504979d479905e495e46d6d473ff7b06994/data-formats/task-execution.md#REQ-EXECUTION-0012): `max_bytes_sent` counts "application bytes supplied to network APIs, excluding lower-layer framing"; `max_bytes_received` counts "application bytes accepted from network APIs before parsing stops".
  - [REQ-EXECUTION-0014](https://github.com/tv-rain/barometer-spec/blob/a7647504979d479905e495e46d6d473ff7b06994/data-formats/task-execution.md#REQ-EXECUTION-0014): the byte limits exclude DNS, TCP, TLS, HTTP, proxy and operating-system framing that the application cannot count portably.
  - [REQ-LIMIT-0014](https://github.com/tv-rain/barometer-spec/blob/a7647504979d479905e495e46d6d473ff7b06994/library/registered-limits.md#REQ-LIMIT-0014) and [REQ-LIMIT-0016](https://github.com/tv-rain/barometer-spec/blob/a7647504979d479905e495e46d6d473ff7b06994/library/registered-limits.md#REQ-LIMIT-0016): separate DNS message, response-header (16,384 bytes), body and NET-03 prefix bounds.
  - [REQ-LIMIT-0019](https://github.com/tv-rain/barometer-spec/blob/a7647504979d479905e495e46d6d473ff7b06994/library/registered-limits.md#REQ-LIMIT-0019) and [REQ-LIMIT-0020](https://github.com/tv-rain/barometer-spec/blob/a7647504979d479905e495e46d6d473ff7b06994/library/registered-limits.md#REQ-LIMIT-0020): NET-05 aggregate application byte limits and the declared-maxima admission check.
  - [REQ-PROXY-0017](https://github.com/tv-rain/barometer-spec/blob/a7647504979d479905e495e46d6d473ff7b06994/library/proxy.md#REQ-PROXY-0017): the `CONNECT` exchange with the loopback proxy endpoint, while `max_connections` counts `CONNECT` tunnels.
  - [REQ-CONTEXT-0015](https://github.com/tv-rain/barometer-spec/blob/a7647504979d479905e495e46d6d473ff7b06994/library/network-context.md#REQ-CONTEXT-0015) and [REQ-CONTEXT-0025](https://github.com/tv-rain/barometer-spec/blob/a7647504979d479905e495e46d6d473ff7b06994/library/network-context.md#REQ-CONTEXT-0025): context acquisition is part of the bounded attempt and has its own 4,096-byte response bound, without saying whether its traffic counts toward the attempt byte limits.
- Affected tests: HTTP-01, NET-03, DNS-01, DNS-03 (DoH), DNS-04 (DoT) and the NET-05 aggregate. TCP-01 and TLS-01 send no application data after connection and handshake.
- Implementation: `tv-rain/barometer-go` at `d53bb1477169b31563c46b0b2a2106422702ea85` decodes and bounds the four `execution.limits` fields. No byte-budget accounting or enforcement exists. No binding, native or platform behavior is implemented or validated.

## Finding and Reproduction

REQ-LIMIT-0003 and REQ-EXECUTION-0014 place HTTP and DNS among the layers whose framing is not counted. For HTTP-01, NET-03 and DNS-03, the HTTP request line and headers are what the test supplies to its HTTP client, and for DNS tests the DNS message is the payload. The text does not say whether the following count:

- HTTP request lines and headers, and HTTP response headers, which already have a separate 16,384-byte bound;
- DoH HTTP framing and DoT or DNS-over-TCP two-byte length prefixes;
- the proxy `CONNECT` exchange, which REQ-LIMIT-0003 names as proxy overhead;
- traffic for Network Context acquisition, which is part of the attempt.

Two conforming implementations could therefore stop the same task at different points or let it send different amounts. Observed behavior: none, because no implementation enforces the budget. Unresolved before this disposition: all four items.

Reproduction: none is required; the gap is in the text. Synthetic cases are listed under the proposed resolution.

Affected work that must stop: byte-budget accounting in Go for HTTP-01, NET-03, DNS-01, DNS-03, DNS-04 and the NET-05 aggregate (DEV-562 and the per-protocol work under DEV-454), and the expected boundary values in the `CC-LIMIT-PURPOSE` case plan. Interim handling: no accounting layer is chosen; the open question stays visible in the `RV-CC-LIMIT-PURPOSE` review case. Unaffected: connection, duration, body, prefix and header bounds, which have their own units, and plain TCP stream accounting on loopback.

## Impact and Required Reviews

- Safety/privacy: under-counting lets a task send or receive more than a reviewer approved; with headers excluded, each HTTP response could add up to 16,384 uncounted bytes. Over-counting can make tasks with small registered targets fail before their check is decidable. No destination, identifier or retained field changes; `max_bytes_*` values and counters are still not added to results ([REQ-LIMIT-0029](../library/registered-limits.md#REQ-LIMIT-0029)). The counting rule is internal to the device and does not by itself change traffic, so it creates no new distinctive traffic.
- Measurement/interpretation: a byte-limit stop is an execution bound, not evidence of interference. Large headers, CDN error pages, captive portals, middleboxes and proxies can all consume the budget. Counting headers makes such stops earlier and more consistent across implementations.
- Compatibility: Draft `0.1.0` wording change. Registered numbers are unchanged, but which tasks reach a limit changes: a task whose limits fitted only body bytes may now stop earlier. NET-05 profiles are checked against the same declared maxima under REQ-LIMIT-0020; headers now consume part of each primitive's declared budget at runtime, so a profile with small primitive budgets may stop where it previously would not.
- Required reviews: public maintainer disposition. Resource and traffic-distinctiveness review of the overall byte bounds remains with the registered-limits validation plan; this change narrows ambiguity and does not raise any maximum, so the threat-model review required by [REQ-LIMIT-0031](../library/registered-limits.md#REQ-LIMIT-0031) for increases does not apply. No legal or platform-policy effect is identified.
- Public-safe summary: this record is complete without private material.

## Alternatives and Proposed Public Resolution

1. **(a) Count everything Barometer exchanges with a TCP stream, the plaintext side of a TLS session or a UDP datagram payload (proposed; accepted).** HTTP request lines, headers, bodies and HTTP/2 framing, DNS messages and retransmissions sent by Barometer, length prefixes and the complete DoH exchange count. TLS handshake and records, TCP/IP and UDP/IP headers, operating-system retransmissions and proxy transport framing do not. One mechanically observable boundary applies to every test, it bounds the traffic a reviewer approves, and it can be validated with scripted transports.
2. (b) Count only HTTP bodies and DNS payloads. Matches the literal "overhead" reading of REQ-LIMIT-0003, but leaves up to 16,384 header bytes per response, request headers, redirects and length prefixes uncounted, so a task can exceed reviewed traffic. Rejected for safety.
3. (c) Per-test accounting tables. Precise per protocol but inconsistent across tests, harder to validate, and must be extended for every new test. Rejected; (a) covers all nine initial tests with one rule.

Retaining the current text leaves implementations free to diverge.

Related decisions under (a):

- **`CONNECT` exchange:** not counted. It is exchanged with the loopback proxy endpoint under REQ-PROXY-0017, not with the measured network, and `max_connections` already counts tunnels. Bytes inside the tunnel count as on a direct path, so the same task has the same budget on direct and proxy paths. Counting it would make proxied tasks fail earlier for reasons unrelated to the target.
- **Platform resolver:** hostname resolution delegated to a platform or system resolver API that does not expose its messages is not counted, because it cannot be counted portably. DNS messages that Barometer sends itself count.
- **Network Context acquisition:** not counted. It is bounded separately by REQ-CONTEXT-0015 and the attempt deadline, and counting it would make a task's budget depend on deployment context endpoints.
- **Read-ahead and stopping:** bytes returned by a read count when read, even if parsing stops before them, and each read requests no more than the remaining budget, so the counted total never exceeds the limit. A write that would exceed the remaining sent budget is not issued.
- **Narrower bounds:** bytes under the header, body, prefix or DNS message bounds also count toward the attempt limits.

Proposed wording, included in this change:

- `library/registered-limits.md`: [REQ-LIMIT-0033](../library/registered-limits.md#REQ-LIMIT-0033) replacing the general byte-limit statement of REQ-LIMIT-0003, new [REQ-LIMIT-0034](../library/registered-limits.md#REQ-LIMIT-0034) defining the counted boundary, and an editorial pointer in the REQ-LIMIT-0006 "Meaning" column.
- `data-formats/task-execution.md`: [REQ-EXECUTION-0032](../data-formats/task-execution.md#REQ-EXECUTION-0032) replacing REQ-EXECUTION-0014, and an editorial pointer in the REQ-EXECUTION-0012 field table.

Proposed requirement-ID lifecycle: REQ-LIMIT-0003 is retired with successors REQ-LIMIT-0033 and REQ-LIMIT-0034, and REQ-EXECUTION-0014 with successor REQ-EXECUTION-0032, because their obligations change materially. REQ-LIMIT-0006 and REQ-EXECUTION-0012 keep their IDs: their numbers, defaults and field roles are unchanged, and their descriptions now point to the counting rule instead of restating it. All other IDs remain active and unchanged. Proposed version decision: retain Draft `0.1.0`; no serialized field, state, reason or limit value changes.

Expected cases, synthetic only, with scripted transports:

- HTTP-01 sends a request whose request line and headers are 400 bytes: 400 bytes are counted as sent before any body.
- HTTP-01 receives 1,200 bytes of status line and headers and a 4,096-byte body: 5,296 bytes are counted as received; the header bytes also count toward the 16,384-byte header bound.
- A task with `max_bytes_received` smaller than the response headers stops when the limit is reached, before the body, under REQ-LIMIT-0027.
- DNS-04 sends a 40-byte query on DoT: 42 bytes are counted as sent, including the length prefix; TLS records are not counted.
- DNS-01 retransmits a 40-byte UDP query once: 80 bytes are counted as sent.
- DNS-03 sends a DoH `POST`: request line, headers and DNS message body are counted; the response status line, headers and DNS message body are counted as received.
- HTTP-01 over the proxy path: the `CONNECT` request and response are not counted; the HTTP exchange inside the tunnel is counted as on the direct path.
- A read buffer of 4,096 bytes with 100 bytes of budget left: the read requests at most 100 bytes.
- Egress-context acquisition before the test starts: its bytes are not counted toward the attempt limits.
- A NET-05 profile: bytes from every primitive step, including headers, count toward the aggregate limits.

These remain proposals until the wording is merged.

## Ordering and Public Disposition

- Coordination decision: not needed; no architecture or responsibility boundary changes.
- Order: merge this record together with the wording and catalog changes in one public change. Then record internal review alignment. Then adopt in Go: the Go record cites the merged revision, byte-budget accounting is implemented at the counted boundary with scripted-transport cases (DEV-562 and the per-protocol work under DEV-454), and the traceability mapping is rebaselined to replace references to the retired IDs. Bindings and hosts follow.
- Maintainer disposition, rationale and date: see [Maintainer Disposition](#maintainer-disposition--october-22-2026).
- Remaining open question outside this change: REQ-PROXY-0017 bounds the `CONNECT` request but registers no byte bound for the proxy's `CONNECT` response; it is limited only by the deadline and syntactic validity. Because the exchange is not counted toward the attempt limits, a registered response bound should be considered separately.

## Adoption and Closure Evidence

- Closure requires: the merged wording revision with its catalog changes; internal review alignment or its recorded non-applicability; and Go adoption evidence: byte-budget accounting at the counted boundary for each affected test, the `CC-LIMIT-PURPOSE` case plan with expected boundary values, scripted-transport results, and traceability citing the new IDs.
- Go cites REQ-LIMIT-0003 and REQ-EXECUTION-0014 against its pinned baseline; those references remain valid for that baseline until rebaselined. Binding and host adoption are outside the current tasks.

## Maintainer Disposition — October 22, 2026

The project owner and public maintainer, Lev, accepted the recommended resolution on October 22, 2026, in the DEV-580 task review, including the exclusion of Network Context acquisition traffic. The public PR review records confirmation of the wording.

- **Rule:** the attempt byte limits and the NET-05 aggregate byte limits count every byte Barometer writes to or reads from a TCP stream, the plaintext side of a TLS session or a UDP datagram payload for the test, including HTTP request lines, headers and framing, DNS messages and length prefixes, and the complete DoH exchange. TLS handshake and records, TCP/IP and UDP/IP headers, operating-system retransmissions, proxy transport framing, the loopback `CONNECT` exchange, resolution through a platform resolver API that does not expose its messages, and Network Context acquisition are not counted.
- **Rationale:** one boundary applies to every test, bounds the traffic a reviewer approves, can be validated with scripted transports, and gives the same task the same budget on direct and proxy paths.
- **Wording:** accepted as proposed: REQ-LIMIT-0033 and REQ-LIMIT-0034 in `library/registered-limits.md` and REQ-EXECUTION-0032 in `data-formats/task-execution.md`, with editorial pointers in REQ-LIMIT-0006 and REQ-EXECUTION-0012.
- **Requirement IDs:** REQ-LIMIT-0003 is retired with successors REQ-LIMIT-0033 and REQ-LIMIT-0034, and REQ-EXECUTION-0014 with successor REQ-EXECUTION-0032, in the [requirement catalog](../requirements/catalog.json). REQ-LIMIT-0033, REQ-LIMIT-0034 and REQ-EXECUTION-0032 are new allocations. No ID is reused.
- **Version:** Draft `0.1.0` is retained. No registered number, schema field, state or reason changes, and no release or runtime support claim is made.
- **Effect:** the merged immutable revision of this change becomes the accepted baseline for internal alignment and Go adoption; it is recorded as evidence on DEV-580 after merge.
