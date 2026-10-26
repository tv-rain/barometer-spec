# Options Format

**Status:** Draft  
**Version:** 0.1.0

Runtime JSON values follow the shared [strict decoding contract](json-decoding.md) in addition to this document's schema, limits, and validation rules.

The `options` object defines test-specific configuration controlling how a measurement is performed.

<a id="REQ-OPTIONS-0001"></a>

**REQ-OPTIONS-0001:**

Options are interpreted by the test implementation selected by `test_id` and `test_version`.

<a id="REQ-OPTIONS-0002"></a>

**REQ-OPTIONS-0002:**

Options are distinct from execution constraints. Test options control operations inside a measurement, while the probe scheduler enforces the outer execution envelope.

## JSON Structure

<a id="REQ-OPTIONS-0003"></a>

**REQ-OPTIONS-0003:**

`options` is always a JSON object:

```json
{
  "options": {}
}
```

<a id="REQ-OPTIONS-0004"></a>

**REQ-OPTIONS-0004:**

Individual option properties may be optional, but the `options` object is required to provide a stable task structure.

<a id="REQ-OPTIONS-0005"></a>

**REQ-OPTIONS-0005:**

A test that uses only its documented defaults receives an empty object. `null`, arrays, strings, numbers, and booleans are not valid top-level option values.

## Complete Boundary Example

```json
{
  "schema_version": "0.1.0",
  "task_id": "network-state-options-boundary",
  "test_id": "NET-01",
  "test_version": "0.1.0",
  "input": {},
  "options": {},
  "schedule": {
    "not_after": "2026-07-30T00:00:00Z",
    "repeat": {
      "mode": "none"
    },
    "limits": {
      "max_runs": 1
    }
  },
  "execution": {
    "limits": {
      "max_duration_ms": 30000
    }
  },
  "safety": {
    "risk_level": "low",
    "requires_user_consent": false
  }
}
```

NET-01 version `0.1.0` accepts no test-specific options. The 30-second execution limit is a hard deadline for the entire execution attempt.

## Test-Specific Examples

Possible HTTP options:

```json
{
  "test_id": "HTTP-01",
  "test_version": "0.1.0",
  "options": {
    "follow_redirects": true,
    "max_redirects": 2
  }
}
```

Possible DNS options:

```json
{
  "test_id": "DNS-01",
  "test_version": "0.1.0",
  "options": {
    "resolver_mode": "direct",
    "transport": "udp",
    "collect_additional_responses": true,
    "additional_response_window_ms": 1000
  }
}
```

These examples comply with the version `0.1.0` option shapes. The registered schema for each test remains authoritative.

## Options Schema

<a id="REQ-OPTIONS-0006"></a>

**REQ-OPTIONS-0006:**

Each registered test version must define the schema and semantics of its options.

<a id="REQ-OPTIONS-0007"></a>

**REQ-OPTIONS-0007:**

The options schema must be available locally with the test implementation. Validation must not depend on downloading a remote schema.

<a id="REQ-OPTIONS-0008"></a>

**REQ-OPTIONS-0008:**

Each options schema must define:

- accepted properties and JSON types
- required properties, if any
- default values
- numeric ranges
- string and array limits
- supported enumerations
- relationships between properties
- compatibility with test inputs
- whether additional properties are allowed

<a id="REQ-OPTIONS-0009"></a>

**REQ-OPTIONS-0009:**

Unknown properties are rejected unless a versioned test explicitly defines otherwise.

<a id="REQ-OPTIONS-0010"></a>

**REQ-OPTIONS-0010:**

The complete `options` object must not exceed 8,192 encoded UTF-8 bytes.

Rejecting unknown properties detects misspellings and prevents `options` from becoming an undocumented control channel.

## Validation

<a id="REQ-OPTIONS-0011"></a>

**REQ-OPTIONS-0011:**

Options are validated when the probe accepts a task, before the task is scheduled.

<a id="REQ-OPTIONS-0012"></a>

**REQ-OPTIONS-0012:**

Validation includes:

```text
options is a JSON object
AND options match the registered test schema
AND options are supported by this implementation
AND options are consistent with input
AND options fit within execution constraints
AND options do not violate local safety policy
```

<a id="REQ-OPTIONS-0013"></a>

**REQ-OPTIONS-0013:**

A task is invalid when:

- `test_id` or `test_version` is unsupported

<a id="REQ-OPTIONS-0025"></a>

**REQ-OPTIONS-0025:**

- the selected options schema is unavailable

<a id="REQ-OPTIONS-0026"></a>

**REQ-OPTIONS-0026:**

- `options` is not a JSON object

<a id="REQ-OPTIONS-0027"></a>

**REQ-OPTIONS-0027:**

- an option has an invalid type or value

<a id="REQ-OPTIONS-0028"></a>

**REQ-OPTIONS-0028:**

- an unknown property is present when the schema disallows it

<a id="REQ-OPTIONS-0029"></a>

**REQ-OPTIONS-0029:**

- a declared size or count limit is exceeded

<a id="REQ-OPTIONS-0030"></a>

**REQ-OPTIONS-0030:**

- a required relationship between options is not satisfied

<a id="REQ-OPTIONS-0031"></a>

**REQ-OPTIONS-0031:**

- the options are incompatible with the task input

<a id="REQ-OPTIONS-0032"></a>

**REQ-OPTIONS-0032:**

- the options cannot operate meaningfully within the execution envelope

<a id="REQ-OPTIONS-0014"></a>

**REQ-OPTIONS-0014:**

The probe must not apply an options schema from a different test version.

<a id="REQ-OPTIONS-0015"></a>

**REQ-OPTIONS-0015:**

An options-validation failure is a task-validation failure. It is not a measurement outcome and must not be interpreted as evidence of censorship.

## Execution Precedence

<a id="REQ-OPTIONS-0016"></a>

**REQ-OPTIONS-0016:**

Options cannot extend or override an execution limit.

For example, if a test operation is still running when `execution.limits.max_duration_ms` is reached, the probe may terminate the execution attempt even when the option-level timeout has not expired.

Clearly inconsistent tasks should be rejected during validation. For example, a timeout for a single mandatory operation that exceeds the entire execution deadline is normally invalid.

<a id="REQ-OPTIONS-0017"></a>

**REQ-OPTIONS-0017:**

The test implementation must not treat an outer execution deadline as if it were a protocol-level measurement outcome.

## No Silent Rewriting

<a id="REQ-OPTIONS-0018"></a>

**REQ-OPTIONS-0018:**

The probe and test implementation should not silently clamp, coerce, or replace explicitly supplied options.

Silently changing an option can alter measurement semantics and make results from different probes difficult to compare.

<a id="REQ-OPTIONS-0019"></a>

**REQ-OPTIONS-0019 (retired):**

The historical rule said that when requested options are unsupported, invalid, or unsafe, the probe should reject or skip the task with an appropriate task or execution status. [REQ-OPTIONS-0033](#REQ-OPTIONS-0033) replaces it: such options are rejected at admission with a named class, and the task is not skipped. This text is historical, not a current obligation; historical revisions remain available.

<a id="REQ-OPTIONS-0033"></a>

**REQ-OPTIONS-0033:**

Options that are invalid for the registered test or prohibited by this document are rejected at admission with the class named by [REQ-TRUST-0056](../library/task-trust.md#REQ-TRUST-0056). A valid option value that requires a capability the implementation does not provide is rejected with `task_unsupported` under [REQ-TRUST-0036](../library/task-trust.md#REQ-TRUST-0036). Options that local policy does not permit are rejected with the class [REQ-TRUST-0047](../library/task-trust.md#REQ-TRUST-0047) lists for that condition. Such a task is not admitted to be skipped or to fail at execution.

<a id="REQ-OPTIONS-0020"></a>

**REQ-OPTIONS-0020:**

Applying a documented default for an omitted option is not silent rewriting.

## Security and Safety

<a id="REQ-OPTIONS-0021"></a>

**REQ-OPTIONS-0021:**

Options must not:

- select an implementation other than the registered `test_id`
- introduce executable code or scripts
- reference arbitrary local files
- contain credentials, cookies, authentication tokens, or secrets
- request device, user, application, or network data through placeholders
- override scheduling or execution limits
- weaken risk or consent requirements
- select reporting behavior
- act as undocumented measurement input

<a id="REQ-OPTIONS-0022"></a>

**REQ-OPTIONS-0022:**

Some registered measurements may intentionally exercise unusual protocol behavior. Such behavior must be represented by explicit, bounded options in a versioned, safety-reviewed test schema.

<a id="REQ-OPTIONS-0023"></a>

**REQ-OPTIONS-0023:**

An arbitrary option must not disable security controls outside the registered behavior of the test.

<a id="REQ-OPTIONS-0024"></a>

**REQ-OPTIONS-0024:**

The probe may enforce stricter local safety restrictions. A task cannot use options to weaken local policy.
