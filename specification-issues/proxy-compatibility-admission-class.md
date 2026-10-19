# Proposal: Admission Class for Proxy-Incompatible Task Parameters

**Disposition:** In review; maintainer disposition pending
**Date:** October 19, 2026
**Related task:** [DEV-598 — Record GO-SPEC-ISSUE-009 and obtain public disposition for the proxy-compatibility admission class](https://app.clickup.com/t/124kk1zcbfb)

This record asks public maintainers to decide what admission does with a task that selects `network_path: proxy` when its test, input or options cannot run through HTTP CONNECT. REQ-TRUST-0017 requires admission to validate proxy compatibility, but no requirement assigns an admission error class to a failure, and the execution states already define `proxy_path_unsupported` for the same condition. It proposes reusing `task_schema_invalid`. It adds no admission class or serialized field and makes no support claim. Opening this record does not accept its proposal, and no requirement text changes until a maintainer disposition is recorded.

## Identity and Ownership

- Local finding: `GO-SPEC-ISSUE-009` in the Go [specification-issue record](https://github.com/tv-rain/barometer-go/blob/main/docs/specification-issues.md#go-spec-issue-009-admission-class-for-proxy-incompatible-task-parameters), raised October 19, 2026 while implementing target registration matching at admission step 8 (DEV-588).
- Public identity: this Markdown record, once reviewed through a public PR. Responsible maintainer: the project owner, Lev.
- Reporter: the Go implementation agent under the task owner's instruction. Public maintainers own disposition and wording. The Go implementation owner owns adoption in DEV-599 of the Admission and local policy sub-epic.
- Duplicates: none found. [Admission Error Classes](admission-error-classes.md) mapped path refusal by issuer authority, local policy and the matched target registration, but not proxy compatibility.

## Affected Baselines and Requirements

- Public Draft `0.1.0` at immutable revision [`d93aff93cbc17e7c065fb40d8f6e2e01a697bf35`](https://github.com/tv-rain/barometer-spec/tree/d93aff93cbc17e7c065fb40d8f6e2e01a697bf35).
- Admission:
  - [REQ-TRUST-0017](https://github.com/tv-rain/barometer-spec/blob/d93aff93cbc17e7c065fb40d8f6e2e01a697bf35/library/task-trust.md#REQ-TRUST-0017) step 8 validates "all input, options, proxy compatibility, target tuples, redirect registrations, and composite steps atomically".
  - [REQ-PROXY-0022](https://github.com/tv-rain/barometer-spec/blob/d93aff93cbc17e7c065fb40d8f6e2e01a697bf35/library/proxy.md#REQ-PROXY-0022) makes a `proxy` task eligible only when the complete test configuration is compatible.
  - [REQ-PROXY-0026](https://github.com/tv-rain/barometer-spec/blob/d93aff93cbc17e7c065fb40d8f6e2e01a697bf35/library/proxy.md#REQ-PROXY-0026) lists compatibility per test. It says NET-01 with `network_path: proxy` is "rejected" and that a NET-05 profile with an incompatible step is "rejected before execution".
  - [REQ-PROXY-0027](https://github.com/tv-rain/barometer-spec/blob/d93aff93cbc17e7c065fb40d8f6e2e01a697bf35/library/proxy.md#REQ-PROXY-0027) requires validation before network activity and forbids running a compatible subset.
- Classes: [REQ-TRUST-0034](https://github.com/tv-rain/barometer-spec/blob/d93aff93cbc17e7c065fb40d8f6e2e01a697bf35/library/task-trust.md#REQ-TRUST-0034) and [REQ-TRUST-0036](https://github.com/tv-rain/barometer-spec/blob/d93aff93cbc17e7c065fb40d8f6e2e01a697bf35/library/task-trust.md#REQ-TRUST-0036) define the classes. The [REQ-TRUST-0037](https://github.com/tv-rain/barometer-spec/blob/d93aff93cbc17e7c065fb40d8f6e2e01a697bf35/library/task-trust.md#REQ-TRUST-0037) table has two step-8 rows, for paths refused by issuer authority or local policy and by the matched target registration, and none for proxy compatibility.
- Execution:
  - [REQ-PROXY-0028](https://github.com/tv-rain/barometer-spec/blob/d93aff93cbc17e7c065fb40d8f6e2e01a697bf35/library/proxy.md#REQ-PROXY-0028) and [REQ-RESULT-0020](https://github.com/tv-rain/barometer-spec/blob/d93aff93cbc17e7c065fb40d8f6e2e01a697bf35/data-formats/measurement-result.md#REQ-RESULT-0020) define the execution state `proxy_path_unsupported` for a test configuration that HTTP CONNECT cannot provide.
  - [REQ-EXECUTION-0008](https://github.com/tv-rain/barometer-spec/blob/d93aff93cbc17e7c065fb40d8f6e2e01a697bf35/data-formats/task-execution.md#REQ-EXECUTION-0008) checks compatibility before a proxy attempt starts, and [REQ-EXECUTION-0010](https://github.com/tv-rain/barometer-spec/blob/d93aff93cbc17e7c065fb40d8f6e2e01a697bf35/data-formats/task-execution.md#REQ-EXECUTION-0010) requires an explicit non-censorship execution state for an incompatible proxy.
- Implementation: `tv-rain/barometer-go` at `2a142c111c013982d9a5cd9d09efb5b577b5b74d`. The registry gives each registered test a proxy-compatibility rule, but admission does not evaluate it. Step-8 input and options failures use `task_schema_invalid` in the Go admission design. No proxy execution exists. No binding, native or platform behavior is implemented or validated.

## Finding and Reproduction

The public text requires admission to validate proxy compatibility and REQ-PROXY-0026 calls incompatible tasks rejected, but no requirement names the admission class. The execution requirements describe the same condition as an execution state recorded for an attempt. A reader cannot tell whether an incompatible task:

- is rejected at admission, and with which class; or
- is admitted and then ends each attempt with `proxy_path_unsupported`.

Examples of incompatible tasks under REQ-PROXY-0026: DNS-01 with `resolver_mode: system` or UDP transport, HTTP-01 with an `address_family` other than `auto`, DNS-03 or DNS-04 without an approved `bootstrap_ip`, NET-01 or NET-03 with `network_path: proxy`, and a NET-05 profile containing any of these.

Evidence: document review only, at the baselines above. No synthetic, runtime or device reproduction is claimed.

Affected work: the proxy-compatibility part of admission step 8 and the Go conformance cases that assert its class. Interim handling: no class is chosen; the Go admission does not evaluate proxy compatibility, and no proxy execution exists. Unaffected: the other step-8 rows of REQ-TRUST-0037 and the rest of admission.

## Impact and Required Reviews

- Safety/privacy: every alternative makes no contact through an incompatible path, so the direct safety difference is small. Admitting an incompatible task schedules attempts that can never run; hosts and analysts may read the resulting stream of `proxy_path_unsupported` states as proxy or network trouble. No destination, traffic, retained data or identifier is added. Error classes remain code-only (REQ-TRUST-0035).
- Measurement/interpretation: an admission error is not a Measurement Result and not evidence of censorship (REQ-TRUST-0033). Compatibility depends only on the task's own fields, because the first version supports one HTTP CONNECT proxy; it says nothing about the proxy, the circumvention method or the network.
- Compatibility: the proposal adds no class and no field. Hosts that expected per-attempt `proxy_path_unsupported` for such tasks would instead see an admission rejection. No external producers, hosts or stored tasks are known; this is an assumption, not assessed deployment evidence.
- Required reviews: public maintainer disposition; safety review of the mapping, which is required and not completed. Host integration review applies when a binding exposes admission classes. No privacy, legal or platform-policy effect is identified. No specialist review is claimed complete.

## Alternatives and Proposed Public Resolution

1. **(a) Reject with `task_schema_invalid` (proposed).** Compatibility is a public rule over the task's own fields that every conforming implementation applies the same way, so an incompatible task is invalid for its selected path rather than unsupported by one implementation. Step 8 groups it with input and options validation. No vocabulary change. The class name refers to a schema, although the rule is a cross-field constraint stated in REQ-PROXY-0026 rather than in a JSON Schema; hosts read it as a malformed issuer task, which is accurate.
2. (b) Reject with `task_unsupported`. REQ-TRUST-0036 says the class "describes the implementation, not the task's validity". Using it would mean every conforming implementation reports a spec-defined incompatibility as a missing capability. It remains the right class when a combination REQ-PROXY-0026 allows is not provided through the proxy by a particular implementation.
3. (c) Reject with `target_not_registered`. A registration can permit the proxy path while the parameters are still incompatible; this conflates registration authority with protocol capability.
4. (d) Reject with `task_issuer_not_authorized`. The class reports a failure of the effective-authority intersection (REQ-TRUST-0010); compatibility is not an authority question.
5. (e) Add a class such as `task_path_incompatible`. Most precise, but extends the vocabulary again, needs a version decision and gives hosts a class they would handle like `task_schema_invalid`.
6. (f) Admit and record `proxy_path_unsupported` per attempt. Matches the execution-state text literally, but contradicts REQ-TRUST-0017 step 8 and the rejection language of REQ-PROXY-0026 and REQ-PROXY-0027, and produces attempts that cannot run.

Retaining the current text without disposition leaves implementations free to diverge between (a) to (f).

Proposed wording, subject to maintainer review:

- In `library/task-trust.md`, after REQ-TRUST-0038, a new requirement:

  > At step 8 of REQ-TRUST-0017, a task with `network_path: proxy` whose test, input or options are not compatible with HTTP CONNECT under REQ-PROXY-0026, including a `NET-05` profile with any incompatible step, is rejected with `task_schema_invalid`. Within step 8, proxy compatibility is evaluated after input and options and before path authority and target registration. A combination that REQ-PROXY-0026 permits but the implementation does not provide through the proxy is rejected with `task_unsupported` under REQ-TRUST-0036.

- In `library/proxy.md`, after REQ-PROXY-0027, a new requirement:

  > An incompatible task is rejected at admission (REQ-TRUST-0039) and is not admitted to fail at execution. `proxy_path_unsupported` records an incompatibility that the pre-attempt check of REQ-EXECUTION-0008 finds in an admitted task; execution then makes no contact.

The proposed intra-step order places proxy compatibility next to input and options, where REQ-TRUST-0017 lists it, so that a task invalid for its selected path is reported as such before authority is consulted. The public text does not otherwise order the conditions inside step 8; this proposal orders only proxy compatibility.

Related observation, not proposed here: no public requirement names the class for a step-8 input or options failure either. Implementations use `task_schema_invalid` by its name. Maintainers may cover it in the same row or leave it for a separate record.

Proposed requirement-ID lifecycle: REQ-TRUST-0017, REQ-TRUST-0037, REQ-PROXY-0026 to REQ-PROXY-0028, REQ-RESULT-0020, REQ-EXECUTION-0008 and REQ-EXECUTION-0010 remain active and unchanged. The new obligations receive new allocations above the current maxima: REQ-TRUST-0039 and REQ-PROXY-0042, reconciled against the target branch before merge. Proposed version decision: retain Draft `0.1.0`, because no class, field or schema value is added; this does not assert that every existing host remains compatible.

Expected cases: a DNS-01 task with `resolver_mode: system` and `network_path: proxy` is rejected with `task_schema_invalid`; the same task with `network_path: direct` is not rejected for compatibility; HTTP-01 with `address_family: auto` through the proxy passes the compatibility check; a NET-05 profile with one incompatible step is rejected as a whole; a task that is both proxy-incompatible and not permitted the proxy path by local policy receives `task_schema_invalid`; a task with invalid options receives `task_schema_invalid` before compatibility is evaluated. Every rejection occurs with no network activity, run or attempt. These remain proposals until the wording is accepted and merged.

## Ordering and Public Disposition

- Coordination decision: not needed; no architecture or responsibility boundary changes.
- Order: maintainer disposition; if text changes, merge the wording, catalog allocations and version decision together with this record's disposition in one public change. Then align the internal task-trust review if its validation plan names the class. Then update the Go `GO-SPEC-ISSUE-009` entry, admission design and case plans, and implement the check in DEV-599. Bindings and hosts follow.
- Internal alignment: expected to be required, because the internal task-trust review validation plan covers the REQ-TRUST-0037 table; to be confirmed at disposition.
- Maintainer disposition, rationale and date: pending.

## Adoption and Closure Evidence

- Closure requires: the maintainer disposition and, if text changes, the merged wording revision with its requirement allocations and version decision; internal review alignment or the reason it does not apply; Go adoption evidence (admission tests asserting the class, the intra-step order and NET-05 whole-profile rejection, and traceability citing them); and the Go record linking all of these.
- Binding and host adoption are outside the current Go tasks and remain to be assessed when those components exist.
