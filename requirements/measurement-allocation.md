# Measurement Requirement Allocation

## Scope and Authority

This allocation identifies existing obligations in the nine Draft `0.1.0` measurement specifications. The marked test text remains authoritative; this guide records allocation scope and source reuse, without adding measurement behavior or claiming implementation, conformance, platform support, or field validation. The catalog contains identity metadata only.

The allocation extends public baseline `47d75925b3829fccfb6954b545c15f695375b76f`. Existing `REQ-TCP-01-0001` is retained without changing its obligation. The other 392 IDs are new allocations. Downstream manifests must select the immutable reviewed public commit containing these allocations; the unchanged `0.1.0` label cannot identify that commit.

| Test and canonical source | Allocated units | Namespace |
|---|---:|---|
| [NET-01](../tests/net-01.md) | 38 | `NET-01` |
| [NET-03](../tests/net-03.md) | 40 | `NET-03` |
| [NET-05](../tests/net-05.md) | 60 | `NET-05` |
| [DNS-01](../tests/dns-01.md) | 52 | `DNS-01` |
| [DNS-03](../tests/dns-03.md) | 39 | `DNS-03` |
| [DNS-04](../tests/dns-04.md) | 39 | `DNS-04` |
| [TCP-01](../tests/tcp-01.md) | 37 | `TCP-01` |
| [TLS-01](../tests/tls-01.md) | 38 | `TLS-01` |
| [HTTP-01](../tests/http-01.md) | 50 | `HTTP-01` |
| **Total** | **393** | |

Each namespace uses consecutive IDs from `0001` through its unit count. Public specification maintainers own their allocation and lifecycle under the [requirement convention](README.md).

## Unit Boundaries and Dispositions

Inputs and options include each complete named object schema, its required/conditional fields, types, enums, defaults, bounds, and rejection rules. Nested schemas have separate units. A table marker covers the complete named schema or registered vector, rather than a representative row; downstream validation must exercise every row and conditional relation. Empty-object declarations and closed-schema tables retain their separate source-local identity where both are stated.

Ordered procedures and ordered observation lists are coupled units: order, preconditions, termination, and permitted omissions must be checked together. Failure and outcome tables identify complete mappings, requiring every row to be exercised. Resource tables identify the complete registered bound vector and its reached-bound behavior. These units do not permit testing one example as coverage of an entire table or sequence.

Adjacent normative paragraphs and independently testable validation, precondition, and safety list items receive their own IDs. The Output version declarations identify the applicable result envelope and result version. Registered status/version/category metadata remains metadata; it is not a runtime-support assertion. Non-goals and interpretation statements constrain permitted behavior and claims. Stronger-interpretation evidence lists identify review criteria; they do not authorize automatic follow-up measurements or add those measurements to a run.

The baseline risk table identifies the registered risk declaration, including its host/local-policy qualification. The risk-factor table identifies the registered factor levels and stated mitigations as a review vector. Explanatory risk rationales remain explanatory; annotation does not turn them into new telemetry or runtime fields. Normative safety actions and the probe's final authority are separately identified. `Requires user consent: false` retains its existing host/local-policy qualification and is not a deployment-specific legal conclusion.

Overview summaries, measurement questions, headings and table/list introductions, illustrative examples and their explanations, alternative explanations, and descriptive residual-risk or repetition-risk statements have no separate obligation allocation. They remain relevant context. Repetition-risk statements containing a scheduling constraint are allocated. The normative restrictions summarized in an Overview are identified in the corresponding method, output, safety, and interpretation sections. Examples remain subordinate to those sections.

The repeated Measurement Limitations applicability sentence reuses the canonical [Measurement Limitations](../measurement-limitations.md); it does not allocate a second copy of that document. Threat-model and cross-cutting limitations allocation, full semantic completeness review, implementation, and executed conformance remain separate work. Passing identifier validation establishes structural integrity and allocation history, not those properties.

## Reused Contracts

All measurements use the shared [task](../data-formats/task.md), [execution](../data-formats/task-execution.md), [result](../data-formats/measurement-result.md), [observations](../data-formats/measurement-observations.md), [JSON decoding](../data-formats/json-decoding.md), [trust/local policy](../library/task-trust.md), [registered limits](../library/registered-limits.md), [proxy/path](../library/proxy.md), and [interpretation limitations](../measurement-limitations.md) contracts where applicable. Measurement-specific restrictions continue to narrow those shared contracts. Source-local repeated obligations do not constitute independent conformance evidence.

| Measurement | Additional reused authority and composition boundary |
|---|---|
| NET-01 | Shared [access object](../data-formats/network-context.md#access-object) and [Network Context lifecycle](../library/network-context.md); no egress collection or traffic. |
| NET-03 | NET-01 context and shared DNS/TCP/TLS/HTTP observation objects. Its HTTP-or-HTTPS validation request and redirect prohibition belong to NET-03; HTTP-01's HTTPS-only schema does not replace them. |
| NET-05 | Exact versioned [DNS-01](../tests/dns-01.md), [TCP-01](../tests/tcp-01.md), [TLS-01](../tests/tls-01.md), and [HTTP-01](../tests/http-01.md) input/options/output contracts. NET-01 and NET-03 supply context under NET-05's stated policy. Atomic profile admission, outer bounds, sequence, and partial-result rules remain NET-05 obligations. |
| DNS-01 | Shared DNS observations and Network Context. System and direct modes retain their distinct visibility, transport, and collection limits. |
| DNS-03 | Shared DNS/TCP/TLS/HTTP observations; bootstrap and authenticated DoH protocol composition remain DNS-03 behavior. Reusing HTTP machinery does not import HTTP-01's GET-only measurement schema. |
| DNS-04 | Shared DNS/TCP/TLS observations; bootstrap and authenticated length-prefixed DoT exchange remain DNS-04 behavior. |
| TCP-01 | Shared TCP observation and network/path constraints; no DNS or application payload. |
| TLS-01 | Shared TCP/TLS observations, trust and network/path constraints; explicit destination, authenticated server name, no application payload. |
| HTTP-01 | Shared DNS/TCP/TLS/HTTP observations, network/path and registered-target checks; redirect and bounded response-check behavior remain HTTP-01 obligations. |

Implementation mappings should link these canonical sources and their allocated IDs. Reusing a protocol implementation or a conformance case does not make one registered measurement inherit another measurement's schema or establish that either is supported.
