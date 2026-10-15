# Labels Format

**Status:** Draft  
**Version:** 0.1.0

Runtime JSON values follow the shared [strict decoding contract](json-decoding.md) in addition to this document's schema, limits, and validation rules.

The `labels` object contains optional metadata used to group, filter, and analyze tasks and their results.

<a id="REQ-LABEL-0001"></a>

**REQ-LABEL-0001:**

Labels are opaque annotations. They do not modify measurement behavior, scheduling, execution constraints, or safety requirements.

<a id="REQ-LABEL-0002"></a>

**REQ-LABEL-0002:**

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

<a id="REQ-LABEL-0003"></a>

**REQ-LABEL-0003:**

`labels` is a flat JSON object whose keys and values are strings.

<a id="REQ-LABEL-0004"></a>

**REQ-LABEL-0004:**

An omitted `labels` field and an empty object are equivalent:

```json
{
  "labels": {}
}
```

## Constraints

<a id="REQ-LABEL-0005"></a>

**REQ-LABEL-0005:**

| Constraint | Limit |
|---|---:|
| Maximum number of labels | 16 |
| Maximum key length | 64 bytes |
| Maximum value length | 128 bytes |
| Maximum encoded object size | 2048 bytes |

<a id="REQ-LABEL-0006"></a>

**REQ-LABEL-0006:**

The encoded object size is the size of the `labels` JSON object in UTF-8, including keys, values, quotes, separators, and braces.

<a id="REQ-LABEL-0007"></a>

**REQ-LABEL-0007:**

Labels exceeding any limit make the task invalid.

## Keys

<a id="REQ-LABEL-0008"></a>

**REQ-LABEL-0008:**

Label keys must match:

```text
^[a-z][a-z0-9_.-]{0,63}$
```

<a id="REQ-LABEL-0009"></a>

**REQ-LABEL-0009:**

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

<a id="REQ-LABEL-0010"></a>

**REQ-LABEL-0010:**

Duplicate keys are invalid, even when the JSON parser would otherwise retain only one value.

### Reserved Namespace

<a id="REQ-LABEL-0011"></a>

**REQ-LABEL-0011:**

Keys beginning with `barometer.` are reserved for fields defined by the Barometer specification.

**Expected: rejected because the reserved key is not registered.**

```json
{
  "labels": {
    "barometer.example": "value"
  }
}
```

<a id="REQ-LABEL-0012"></a>

**REQ-LABEL-0012:**

A task must not use an unknown key in the `barometer.` namespace. Implementations must not assign special meaning to unreserved label keys.

## Values

<a id="REQ-LABEL-0013"></a>

**REQ-LABEL-0013:**

Label values must be strings.

```json
{
  "labels": {
    "campaign": "connectivity-july-2026"
  }
}
```

<a id="REQ-LABEL-0014"></a>

**REQ-LABEL-0014:**

Values:

- are case-sensitive
- may contain UTF-8 text
- must not contain control characters
- must not be interpreted as templates or executable expressions

<a id="REQ-LABEL-0015"></a>

**REQ-LABEL-0015:**

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

<a id="REQ-LABEL-0016"></a>

**REQ-LABEL-0016:**

Applications that require numeric or boolean metadata must encode it as an agreed string value:

```json
{
  "labels": {
    "priority": "1",
    "production": "true"
  }
}
```

<a id="REQ-LABEL-0017"></a>

**REQ-LABEL-0017:**

Labels remain strings during comparison and filtering. Implementations must not automatically coerce them to other data types.

## Privacy and Safety

<a id="REQ-LABEL-0018"></a>

**REQ-LABEL-0018:**

Labels are task-provided metadata. They must not contain or be expanded with information obtained from the device, user, host application, or current network.

<a id="REQ-LABEL-0019"></a>

**REQ-LABEL-0019:**

Labels must not contain:

- user, account, installation, advertising, or device identifiers
- IP addresses
- network names, SSIDs, or BSSIDs
- precise location
- authentication data, credentials, or secrets
- free-form user-provided content
- unrelated application activity
- identifiers derived from a device or household

<a id="REQ-LABEL-0020"></a>

**REQ-LABEL-0020:**

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

<a id="REQ-LABEL-0021"></a>

**REQ-LABEL-0021:**

The values must remain literal strings or the task must be rejected according to local policy.

<a id="REQ-LABEL-0022"></a>

**REQ-LABEL-0022:**

Task and run identifiers should be represented by their defined schema fields and must not be duplicated in labels.

<a id="REQ-LABEL-0023"></a>

**REQ-LABEL-0023:**

Local privacy or safety policy may reject or remove labels even when they satisfy the structural constraints.

## Processing

<a id="REQ-LABEL-0024"></a>

**REQ-LABEL-0024:**

The probe treats label keys and values as opaque.

Labels may be used by authorized components for:

- grouping tasks into campaigns or cohorts
- filtering tasks or results
- associating results with a deployment
- aggregate analysis

<a id="REQ-LABEL-0025"></a>

**REQ-LABEL-0025:**

Labels must not:

- select a measurement implementation
- change measurement input or options
- alter scheduling or retry behavior
- weaken execution constraints
- change risk or consent evaluation
- select a reporting destination or delivery policy

<a id="REQ-LABEL-0026"></a>

**REQ-LABEL-0026:**

Unknown unreserved labels do not make a task unsupported.

<a id="REQ-LABEL-0027"></a>

**REQ-LABEL-0027:**

The initial [`Measurement Result`](measurement-result.md) format does not copy labels. An authorized collector may associate a result with the accepted task by `task_id`. A future result or reporting version that copies labels must define that behavior explicitly; copied labels must remain unchanged and must not be enriched with local device, user, or network data.

## Validation

<a id="REQ-LABEL-0028"></a>

**REQ-LABEL-0028:**

A `labels` object is valid only when:

```text
labels is a JSON object
AND every key is unique and matches the key syntax
AND every value is a string
AND no key or value exceeds its size limit
AND the object does not exceed the total size limit
AND no unknown reserved key is present
```

<a id="REQ-LABEL-0029"></a>

**REQ-LABEL-0029:**

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
