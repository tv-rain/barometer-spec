# Runtime JSON Decoding

**Status:** Draft
**Version:** 0.1.0

## Scope

These rules apply whenever a Barometer runtime component decodes a public task, input, option, schedule, execution, safety, label, result, observation, bundle, network-context response, or host-configuration JSON value. Nested objects and array elements follow the same rules. Development artifacts such as requirement catalogs and traceability manifests are outside this runtime contract. Trusted internal capabilities and source context do not become public serialized models through this document.

## Complete Input and Text

<a id="REQ-JSON-0001"></a>

**REQ-JSON-0001:**

Accept exactly one complete JSON value of the type required by the selected schema. Only JSON whitespace (space, tab, carriage return, and line feed) may precede or follow it. Reject empty input, trailing values or non-whitespace content, comments, trailing commas, and a byte-order mark. An object schema rejects a top-level array, scalar, or null.

<a id="REQ-JSON-0002"></a>

**REQ-JSON-0002:**

The complete input must be valid UTF-8. Every decoded JSON string and member name must consist of Unicode scalar values. Reject invalid UTF-8, malformed escapes, and unpaired UTF-16 surrogate escapes rather than replacing them. Decode valid surrogate pairs to the corresponding scalar value. Do not case-fold or apply Unicode normalization. Schema-specific normalization and control-character restrictions apply only after this decoding step.

## Object Names and Unknown Fields

<a id="REQ-JSON-0003"></a>

**REQ-JSON-0003:**

Every decoded member name must be unique within its JSON object. Repetition rejects the complete model even when repeated values are equal. Compare after decoding JSON escapes: test_id and test_\u0069d are duplicates in the same object. Names in different objects do not conflict. Canonically equivalent but distinct Unicode scalar sequences are not duplicates unless an applicable schema expressly defines normalization and collision handling.

<a id="REQ-JSON-0004"></a>

**REQ-JSON-0004:**

Match fixed schema fields exactly and case-sensitively after decoding escapes. Reject unknown fields wherever the selected schema rejects them. Explicit dynamic-key objects, such as labels, retain their own key syntax and namespace rules; valid unreserved label keys are not unknown fixed fields. Do not discard unknown fields to make a closed schema valid.

## Types, Presence, and Numbers

<a id="REQ-JSON-0005"></a>

**REQ-JSON-0005:**

Preserve distinctions between missing, null, empty, and zero until the schema determines their meaning. A required field must be present and have its declared JSON type. Accept null only where the field contract explicitly permits it; null is not an implicit default. Do not coerce strings, booleans, or numbers into another JSON type. Defaults apply only as defined by the selected schema.

<a id="REQ-JSON-0006"></a>

**REQ-JSON-0006:**

An integer field must use a JSON number token matching the entire pattern 0|-?[1-9][0-9]*. Reject negative zero (-0), decimal points, fractions, and exponent notation for integer fields, including numerically integral spellings such as 1.0 and 1e0. Leading plus signs and leading zeros are invalid JSON and are rejected. Field sign/range constraints still apply; lexical validity does not authorize a negative value in a non-negative field.

<a id="REQ-JSON-0007"></a>

**REQ-JSON-0007:**

Decode and compare integers exactly, without intermediate floating-point conversion, rounding, truncation, wrapping, or clamping. Reject values outside the declared field range or the implementation's documented exact representation. That representation must cover the field's entire declared bounded domain; a narrower type does not authorize rejecting valid domain values. Where a field lacks a finite upper bound, document and review the finite exact representation before claiming support.

Accept other numeric forms only when the selected schema explicitly defines a non-integer number field and its range/precision rules. This contract introduces no such fields, does not permit NaN or infinity, and does not make generic floating-point conversion a schema. Numeric tokens must not silently change value before validation.

## Schema and Version Selection

<a id="REQ-JSON-0008"></a>

**REQ-JSON-0008:**

Select the exact supported schema/test version using declared version fields or trusted containing context. Do not add version fields to formats that have none. Versionless host configuration and nested objects use their explicitly selected integration or containing-model contract. Reject missing required, wrong-type, malformed, or unsupported versions. Never try another version, latest schema, or compatible-looking model as a fallback. Task input/options use the exact test_id and test_version selected by the task.

## Bounds and Failure

<a id="REQ-JSON-0009"></a>

**REQ-JSON-0009:**

Apply registered complete-input and nested-object byte/count limits, with stricter reviewed local bounds where allowed. Count original encoded UTF-8 bytes, including whitespace and unknown fields, before reserialization. Stop parsing once the complete-input maximum is exceeded. Unknown/unsupported versions do not authorize larger allocations. Models without a registered complete-input maximum require a finite reviewed local input bound before decoding is enabled.

<a id="REQ-JSON-0010"></a>

**REQ-JSON-0010:**

Use bounded memory and work, including for malformed or deeply nested input. Do not publish a usable partially decoded model after any error. Fail atomically before admission, scheduling, network activity, or other behavior requiring validated data. Structural success establishes no provenance, issuer authority, registered target, local-policy permission, replay eligibility, or safe execution.

<a id="REQ-JSON-0011"></a>

**REQ-JSON-0011:**

Return bounded operational errors without echoing input values, input-supplied field names, targets, labels, credentials, verification/linkage material, or raw parser/platform error strings. Errors are not Measurement Results or evidence of censorship. No particular parser or cross-language diagnostic precedence is mandated; each implementation must behave deterministically for fixed input and the same schema/local-policy baseline.
