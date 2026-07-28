# Input Format

**Status:** Draft  
**Version:** 0.1.0

The `input` object defines the concrete subject of a measurement.

Input fields are test-specific. Their structure and meaning are defined by the input schema associated with the task's `test_id` and `test_version`.

The generic task format does not define individual input fields.

## Input Model

The input schema must be available locally with the test implementation. Task validation must not depend on downloading a remote schema.

## JSON Structure

`input` is always a JSON object:

```json
{
  "input": {}
}
```

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

Unknown properties are rejected unless a versioned test explicitly defines otherwise.

The complete `input` object must not exceed 49,152 encoded UTF-8 bytes.

Rejecting unknown properties detects misspellings and prevents `input` from becoming an undocumented configuration channel.

Default values should be defined by the versioned test schema or implementation. Required measurement subjects must not be supplied through implicit or environment-dependent defaults.

## Validation

Input validation occurs when the probe accepts a task, before the task is scheduled.

A task is invalid when:

- `test_id` is unknown or unsupported
- `test_version` is unknown or unsupported
- the selected input schema is unavailable
- `input` is not a JSON object
- a required input field is missing
- an input field has an invalid type or value
- an unknown property is present when the schema disallows it
- a declared size or count limit is exceeded
- the configured target violates local safety policy

The probe must not apply an input schema from a different test version or attempt best-effort execution of an invalid input.

Input validation failure is a task-validation failure. It is not a measurement outcome and must not be interpreted as evidence of censorship.

## Normalization

Normalization is test-specific and must be deterministic for a given `test_version`.

Examples include:

- canonical representation of IP addresses
- case normalization where a protocol defines values as case-insensitive
- internationalized domain-name handling
- URL normalization required by the test

Normalization must not silently change the intended measurement subject. If an input is ambiguous or cannot be normalized safely, the task must be rejected.

The test result should make clear which normalized input was used when the result schema permits that information to be retained.

## Target Safety

Schema validation establishes that an input is structurally valid. It does not establish that executing the input is safe.

The probe must evaluate configured targets against the registered test definition and local safety policy.

Targets requiring explicit test and local-policy support include:

- loopback addresses
- link-local addresses
- private-network addresses
- local device services
- unsupported URL schemes
- URLs containing embedded credentials
- targets reached after a redirect

Redirect targets must be evaluated before they are contacted. Approval of an initial target must not automatically authorize a redirect to a locally prohibited destination.

A syntactically valid hostname, address, or URL may still be rejected for safety reasons.

## Sensitive and Dynamic Input

Input must not contain:

- user credentials
- cookies or authentication tokens
- user, account, installation, or device identifiers
- unrelated application data
- arbitrary local file paths
- placeholders requesting device, user, application, or network data

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

When a test supports multiple targets, its input schema must define a conservative maximum number of entries and bound the size of each entry.

No initial primitive test accepts a generic `hostnames` array. A future multiple-target test must register its exact array field, item schema, and maximum before publishing a JSON example.

Input arrays must never be unbounded.

## Result Propagation

The input format does not determine whether input values appear in measurement results or reports.

The applicable test Output schema and common [`Measurement Result`](measurement-result.md) format define whether the result retains:

- the original input
- a normalized input
- a safe target identifier
- a minimized or redacted representation
- no input value

Inputs must not automatically be copied into reports. Retention must be limited to what is necessary for interpreting the measurement and must follow local privacy and safety policy.

## Implementation Authority

The registered test schema is authoritative for the structure of `input`.

The probe may enforce stricter local validation and safety restrictions. A task cannot weaken schema validation, expand supported input types, or override local safety policy.
