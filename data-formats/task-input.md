# Input Format

**Status:** Draft  
**Version:** 0.1.0

Runtime JSON values follow the shared [strict decoding contract](json-decoding.md) in addition to this document's schema, limits, and validation rules.

The `input` object defines the concrete subject of a measurement.

<a id="REQ-INPUT-0001"></a>

**REQ-INPUT-0001:**

Input fields are test-specific. Their structure and meaning are defined by the input schema associated with the task's `test_id` and `test_version`.

The generic task format does not define individual input fields.

## Input Model

<a id="REQ-INPUT-0002"></a>

**REQ-INPUT-0002:**

The input schema must be available locally with the test implementation. Task validation must not depend on downloading a remote schema.

## JSON Structure

<a id="REQ-INPUT-0003"></a>

**REQ-INPUT-0003:**

`input` is always a JSON object:

```json
{
  "input": {}
}
```

<a id="REQ-INPUT-0004"></a>

**REQ-INPUT-0004:**

A test that does not require external input uses an empty object. `null`, arrays, strings, numbers, and booleans are not valid top-level input values.

## Test-Specific Examples

TCP-01 requires an `ip_address` and `port` that form a registered public target. A generic document cannot supply a deployment-approved address, so the shape is shown without presenting it as an executable JSON example:

```text
input.ip_address = <registered public IPv4 or IPv6 address>
input.port = <registered TCP port>
```

DNS resolution input:

```json
{
  "test_id": "DNS-01",
  "test_version": "0.1.0",
  "input": {
    "hostname": "example.org",
    "record_type": "A"
  }
}
```

HTTP request input:

```json
{
  "test_id": "HTTP-01",
  "test_version": "0.1.0",
  "input": {
    "url": "https://example.org/health"
  }
}
```

These examples satisfy the registered structural schemas. Target registration and local policy remain separate admission requirements.

## Input Schema Requirements

<a id="REQ-INPUT-0005"></a>

**REQ-INPUT-0005:**

Each test input schema must define:

- required properties
- accepted JSON types
- whether empty values are allowed
- string and array length limits
- numeric ranges
- allowed protocols, address types, and ports
- normalization rules
- semantic validation rules
- whether additional properties are allowed

<a id="REQ-INPUT-0006"></a>

**REQ-INPUT-0006:**

Unknown properties are rejected unless a versioned test explicitly defines otherwise.

<a id="REQ-INPUT-0007"></a>

**REQ-INPUT-0007:**

The complete `input` object must not exceed 49,152 encoded UTF-8 bytes.

Rejecting unknown properties detects misspellings and prevents `input` from becoming an undocumented configuration channel.

<a id="REQ-INPUT-0008"></a>

**REQ-INPUT-0008:**

Default values should be defined by the versioned test schema or implementation. Required measurement subjects must not be supplied through implicit or environment-dependent defaults.

## Validation

<a id="REQ-INPUT-0009"></a>

**REQ-INPUT-0009:**

Input validation occurs when the probe accepts a task, before the task is scheduled.

<a id="REQ-INPUT-0010"></a>

**REQ-INPUT-0010:**

A task is invalid when:

- `test_id` is unknown or unsupported

<a id="REQ-INPUT-0027"></a>

**REQ-INPUT-0027:**

- `test_version` is unknown or unsupported

<a id="REQ-INPUT-0028"></a>

**REQ-INPUT-0028:**

- the selected input schema is unavailable

<a id="REQ-INPUT-0029"></a>

**REQ-INPUT-0029:**

- `input` is not a JSON object

<a id="REQ-INPUT-0030"></a>

**REQ-INPUT-0030:**

- a required input field is missing

<a id="REQ-INPUT-0031"></a>

**REQ-INPUT-0031:**

- an input field has an invalid type or value

<a id="REQ-INPUT-0032"></a>

**REQ-INPUT-0032:**

- an unknown property is present when the schema disallows it

<a id="REQ-INPUT-0033"></a>

**REQ-INPUT-0033:**

- a declared size or count limit is exceeded

<a id="REQ-INPUT-0034"></a>

**REQ-INPUT-0034:**

- the configured target violates local safety policy

<a id="REQ-INPUT-0011"></a>

**REQ-INPUT-0011:**

The probe must not apply an input schema from a different test version or attempt best-effort execution of an invalid input.

<a id="REQ-INPUT-0012"></a>

**REQ-INPUT-0012:**

Input validation failure is a task-validation failure. It is not a measurement outcome and must not be interpreted as evidence of censorship.

## Normalization

<a id="REQ-INPUT-0013"></a>

**REQ-INPUT-0013:**

Normalization is test-specific and must be deterministic for a given `test_version`.

Examples include:

- canonical representation of IP addresses
- case normalization where a protocol defines values as case-insensitive
- internationalized domain-name handling
- URL normalization required by the test

<a id="REQ-INPUT-0014"></a>

**REQ-INPUT-0014:**

Normalization must not silently change the intended measurement subject. If an input is ambiguous or cannot be normalized safely, the task must be rejected.

<a id="REQ-INPUT-0015"></a>

**REQ-INPUT-0015:**

The test result should make clear which normalized input was used when the result schema permits that information to be retained.

## Target Safety

Schema validation establishes that an input is structurally valid. It does not establish that executing the input is safe.

<a id="REQ-INPUT-0016"></a>

**REQ-INPUT-0016:**

The probe must evaluate configured targets against the registered test definition and local safety policy.

<a id="REQ-INPUT-0017"></a>

**REQ-INPUT-0017:**

Targets requiring explicit test and local-policy support include:

- loopback addresses
- link-local addresses
- private-network addresses
- local device services
- unsupported URL schemes
- URLs containing embedded credentials
- targets reached after a redirect

<a id="REQ-INPUT-0018"></a>

**REQ-INPUT-0018:**

Redirect targets must be evaluated before they are contacted. Approval of an initial target must not automatically authorize a redirect to a locally prohibited destination.

A syntactically valid hostname, address, or URL may still be rejected for safety reasons.

## Sensitive and Dynamic Input

<a id="REQ-INPUT-0019"></a>

**REQ-INPUT-0019:**

Input must not contain:

- user credentials
- cookies or authentication tokens
- user, account, installation, or device identifiers
- unrelated application data
- arbitrary local file paths
- placeholders requesting device, user, application, or network data

<a id="REQ-INPUT-0020"></a>

**REQ-INPUT-0020:**

Implementations must not perform runtime interpolation of input values.

For example, the following value must remain literal or cause task rejection according to local policy.

**Expected: rejected by the initial input policy.**

```json
{
  "input": {
    "hostname": "${current_network_domain}"
  }
}
```

## Multiple Targets

Prefer one target per task or measurement run.

A single target simplifies:

- safety evaluation
- resource limits
- retry behavior
- result interpretation
- correlation with independent observations

<a id="REQ-INPUT-0021"></a>

**REQ-INPUT-0021:**

When a test supports multiple targets, its input schema must define a conservative maximum number of entries and bound the size of each entry.

<a id="REQ-INPUT-0022"></a>

**REQ-INPUT-0022:**

No initial primitive test accepts a generic `hostnames` array. A future multiple-target test must register its exact array field, item schema, and maximum before publishing a JSON example.

<a id="REQ-INPUT-0023"></a>

**REQ-INPUT-0023:**

Input arrays must never be unbounded.

## Result Propagation

The input format does not determine whether input values appear in measurement results or reports.

The applicable test Output schema and common [`Measurement Result`](measurement-result.md) format define whether the result retains:

- the original input
- a normalized input
- a safe target identifier
- a minimized or redacted representation
- no input value

<a id="REQ-INPUT-0024"></a>

**REQ-INPUT-0024:**

Inputs must not automatically be copied into reports. Retention must be limited to what is necessary for interpreting the measurement and must follow local privacy and safety policy.

## Implementation Authority

<a id="REQ-INPUT-0025"></a>

**REQ-INPUT-0025:**

The registered test schema is authoritative for the structure of `input`.

<a id="REQ-INPUT-0026"></a>

**REQ-INPUT-0026:**

The probe may enforce stricter local validation and safety restrictions. A task cannot weaken schema validation, expand supported input types, or override local safety policy.
