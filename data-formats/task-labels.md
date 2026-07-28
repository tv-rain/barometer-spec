# Labels Format

**Status:** Draft  
**Version:** 0.1.0

The `labels` object contains optional metadata used to group, filter, and analyze tasks and their results.

Labels are opaque annotations. They do not modify measurement behavior, scheduling, execution constraints, or safety requirements.

If metadata affects probe behavior, it must be represented as a typed field in the appropriate task object rather than as a label.

## JSON Structure

```json
{
  "labels": {
    "campaign": "connectivity-july-2026",
    "measurement_group": "baseline",
    "deployment": "mobile-production"
  }
}
```

`labels` is a flat JSON object whose keys and values are strings.

An omitted `labels` field and an empty object are equivalent:

```json
{
  "labels": {}
}
```

## Constraints

| Constraint | Limit |
|---|---:|
| Maximum number of labels | 16 |
| Maximum key length | 64 bytes |
| Maximum value length | 128 bytes |
| Maximum encoded object size | 2048 bytes |

The encoded object size is the size of the `labels` JSON object in UTF-8, including keys, values, quotes, separators, and braces.

Labels exceeding any limit make the task invalid.

## Keys

Label keys must match:

```text
^[a-z][a-z0-9_.-]{0,63}$
```

Keys:

- start with a lowercase ASCII letter
- contain only lowercase ASCII letters, digits, underscores, hyphens, and periods
- are case-sensitive
- must be unique within the object

Examples of valid keys:

```text
campaign
measurement_group
deployment.environment
partner-project
```

Examples of invalid keys:

```text
Campaign
1campaign
measurement group
.internal
```

Duplicate keys are invalid, even when the JSON parser would otherwise retain only one value.

### Reserved Namespace

Keys beginning with `barometer.` are reserved for fields defined by the Barometer specification.

**Expected: rejected because the reserved key is not registered.**

```json
{
  "labels": {
    "barometer.example": "value"
  }
}
```

A task must not use an unknown key in the `barometer.` namespace. Implementations must not assign special meaning to unreserved label keys.

## Values

Label values must be strings.

```json
{
  "labels": {
    "campaign": "connectivity-july-2026"
  }
}
```

Values:

- are case-sensitive
- may contain UTF-8 text
- must not contain control characters
- must not be interpreted as templates or executable expressions

Numbers, booleans, arrays, objects, and `null` are not valid label values.

Invalid examples:

**Expected: rejected because label values must be strings.**

```json
{
  "labels": {
    "priority": 1,
    "production": true,
    "groups": [
      "baseline",
      "pilot"
    ]
  }
}
```

Applications that require numeric or boolean metadata must encode it as an agreed string value:

```json
{
  "labels": {
    "priority": "1",
    "production": "true"
  }
}
```

Labels remain strings during comparison and filtering. Implementations must not automatically coerce them to other data types.

## Privacy and Safety

Labels are task-provided metadata. They must not contain or be expanded with information obtained from the device, user, host application, or current network.

Labels must not contain:

- user, account, installation, advertising, or device identifiers
- IP addresses
- network names, SSIDs, or BSSIDs
- precise location
- authentication data, credentials, or secrets
- free-form user-provided content
- unrelated application activity
- identifiers derived from a device or household

Labels must not use placeholders that request runtime substitution.

For example, an implementation must not expand:

**Expected: rejected by local policy because the values request runtime interpolation.**

```json
{
  "labels": {
    "device": "${device_id}",
    "network": "${current_ssid}"
  }
}
```

The values must remain literal strings or the task must be rejected according to local policy.

Task and run identifiers should be represented by their defined schema fields and must not be duplicated in labels.

Local privacy or safety policy may reject or remove labels even when they satisfy the structural constraints.

## Processing

The probe treats label keys and values as opaque.

Labels may be used by authorized components for:

- grouping tasks into campaigns or cohorts
- filtering tasks or results
- associating results with a deployment
- aggregate analysis

Labels must not:

- select a measurement implementation
- change measurement input or options
- alter scheduling or retry behavior
- weaken execution constraints
- change risk or consent evaluation
- select a reporting destination or delivery policy

Unknown unreserved labels do not make a task unsupported.

The initial [`Measurement Result`](measurement-result.md) format does not copy labels. An authorized collector may associate a result with the accepted task by `task_id`. A future result or reporting version that copies labels must define that behavior explicitly; copied labels must remain unchanged and must not be enriched with local device, user, or network data.

## Validation

A `labels` object is valid only when:

```text
labels is a JSON object
AND every key is unique and matches the key syntax
AND every value is a string
AND no key or value exceeds its size limit
AND the object does not exceed the total size limit
AND no unknown reserved key is present
```

An invalid label is a task-validation failure. It is not a measurement result and must not be interpreted as evidence of censorship.

## Complete Example

```json
{
  "labels": {
    "campaign": "connectivity-july-2026",
    "measurement_group": "baseline",
    "deployment": "mobile-production"
  }
}
```
