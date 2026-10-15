# Result Bundle Format

**Status:** Draft  
**Version:** 0.1.0

Runtime JSON values follow the shared [strict decoding contract](json-decoding.md) in addition to this document's schema, limits, and validation rules.

## Overview

A Result Bundle groups one or more task results into one bounded submission packet. It allows a collector to associate results produced together without assigning a persistent identifier to a person, device, application account, or installation.

<a id="REQ-BUNDLE-0001"></a>

**REQ-BUNDLE-0001:**

Every bundle has a random, single-use `bundle_id`. Optional correlation between different bundles is provided separately by the rotating installation linkage defined in [`library/result-linkage.md`](../library/result-linkage.md).

<a id="REQ-BUNDLE-0002"></a>

**REQ-BUNDLE-0002:**

Each object in `results` must comply with the common [`Measurement Result`](measurement-result.md) envelope and the Output schema registered by its test and result version.

## JSON Structure

```json
{
  "schema_version": "0.1.0",
  "bundle_id": "7JfX95yXWZQ2qkr9A2YwTg",
  "linkage": {
    "mode": "rotating_installation",
    "scope": "org.example.app.production",
    "epoch": 2948,
    "token": "R4-xY8pTwAvC0dYp38HBZ24CpAU3RgcEhT3OUb6qOaQ"
  },
  "results": [
    {
      "schema_version": "0.1.0",
      "task_id": "task-1",
      "run_id": "6M6wP59YYK7YxvM9mMVXwA",
      "attempt": 1,
      "test": {
        "id": "TCP-01",
        "version": "0.1.0",
        "result_version": "0.1.0"
      },
      "implementation": {
        "library_version": "0.1.0",
        "platform": "android"
      },
      "time": {
        "started_at": "2026-07-28T14:32:00Z",
        "precision": "minute",
        "duration_ms": 500
      },
      "execution": {
        "state": "completed"
      },
      "network_context": {
        "access": {
          "network_type": "cellular",
          "vpn_state": "not_detected",
          "ipv4_available": "yes",
          "ipv6_available": "yes",
          "validated": "yes",
          "network_changed": false
        },
        "egress": {
          "status": "unavailable",
          "lookup_source": "none",
          "network_path": "direct"
        }
      },
      "measurement": {
        "outcome": "connected",
        "observations": [
          {
            "type": "tcp_connect",
            "status": "succeeded",
            "duration_ms": 500,
            "details": {
              "address_family": "ipv4"
            }
          }
        ]
      }
    }
  ]
}
```

<a id="REQ-BUNDLE-0003"></a>

**REQ-BUNDLE-0003:**

When linkage is disabled, `linkage` is omitted:

```json
{
  "schema_version": "0.1.0",
  "bundle_id": "7JfX95yXWZQ2qkr9A2YwTg",
  "results": [
    {
      "schema_version": "0.1.0",
      "task_id": "task-1",
      "run_id": "6M6wP59YYK7YxvM9mMVXwA",
      "attempt": 1,
      "test": {
        "id": "TCP-01",
        "version": "0.1.0",
        "result_version": "0.1.0"
      },
      "implementation": {
        "library_version": "0.1.0",
        "platform": "ios"
      },
      "time": {
        "started_at": "2026-07-28T14:32:00Z",
        "precision": "minute",
        "duration_ms": 0
      },
      "execution": {
        "state": "not_run",
        "reason": "constraints_unsatisfied"
      }
    }
  ]
}
```

## Top-level Fields

<a id="REQ-BUNDLE-0004"></a>

**REQ-BUNDLE-0004:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `schema_version` | string | Yes | `0.1.0` | Version of the Result Bundle schema. |
| `bundle_id` | string | Yes | Base64url without padding encoding exactly 16 random bytes. | Single-use identifier for this logical bundle. |
| `linkage` | object | No | Present only when locally configured rotating installation linkage is active. | Pseudonymous correlation metadata for a limited epoch. |
| `results` | array | Yes | 1–16 valid Measurement Results; complete encoded bundle maximum 262,144 bytes. | Attempt results carried by this bundle. |

<a id="REQ-BUNDLE-0005"></a>

**REQ-BUNDLE-0005:**

Unknown top-level fields are rejected.

## Bundle Identifier

<a id="REQ-BUNDLE-0006"></a>

**REQ-BUNDLE-0006:**

Barometer generates `bundle_id` from a cryptographically secure random source when it creates a new logical bundle. A task, collector, egress endpoint, proxy, measurement target, or host account must not supply or influence it.

<a id="REQ-BUNDLE-0007"></a>

**REQ-BUNDLE-0007:**

The same `bundle_id` may be reused only for an exact retransmission of the same logical bundle. Adding, removing, or modifying a result creates a new bundle and a new `bundle_id`.

<a id="REQ-BUNDLE-0008"></a>

**REQ-BUNDLE-0008:**

The collector may use `bundle_id` for idempotent ingestion and duplicate suppression. It must not use the identifier for cross-bundle profiling, task selection, or individual targeting. Barometer deletes the bundle and its identifier immediately after durable acknowledgement processing or after the 86,400-second pending-retention maximum.

<a id="REQ-BUNDLE-0009"></a>

**REQ-BUNDLE-0009:**

`bundle_id` must not be included in DNS queries, proxy requests, network-context requests, measurement HTTP headers, measurement payloads, or other traffic visible to measurement targets.

## Linkage Object

<a id="REQ-BUNDLE-0010"></a>

**REQ-BUNDLE-0010:**

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `mode` | string | Yes | `rotating_installation` | Linkage mechanism used for this bundle. |
| `scope` | string | Yes | Same validated deployment scope configured locally at initialization. | Prevents correlation across unrelated deployments. |
| `epoch` | integer | Yes | Non-negative integer derived from the configured rotation period. | Identifies the coarse rotation window; it is not an installation counter. |
| `token` | string | Yes | Base64url without padding encoding exactly 32 bytes. | HMAC-derived pseudonymous token for this scope and epoch. |

<a id="REQ-BUNDLE-0011"></a>

**REQ-BUNDLE-0011:**

Unknown linkage fields are rejected. The initial format does not define a stable or non-rotating installation mode.

<a id="REQ-BUNDLE-0012"></a>

**REQ-BUNDLE-0012:**

The token represents an installation of the Barometer integration, not a person. One person can have multiple installations, and one installation or device can be used by multiple people. Implementations and collectors must not label it `user_id`.

## Result Membership

The host or scheduler may place related task results in one bundle when doing so serves an explicit measurement purpose. Typical examples include:

- the results from one bounded scheduler run;
- direct and proxy attempts intentionally performed as one comparison;
- one or more complete or partial `NET-05` composite results.

<a id="REQ-BUNDLE-0013"></a>

**REQ-BUNDLE-0013:**

Bundling does not change the meaning of an individual result. A negative measurement, not-run attempt, cancellation, and incomplete attempt remain distinguishable through `measurement.outcome` and `execution`.

<a id="REQ-BUNDLE-0014"></a>

**REQ-BUNDLE-0014:**

Each result retains Network Context according to the conditional rules in the Measurement Result and applicable test Output schemas. Identical snapshots may be represented once and referenced within the same bundle only if a future result schema defines an unambiguous bundle-local reference. Such a reference must never be reusable across bundles.

## Construction and Delivery

<a id="REQ-BUNDLE-0015"></a>

**REQ-BUNDLE-0015:**

Barometer must:

1. finish or terminate the bounded attempts selected for the logical bundle;
2. validate every result and remove data prohibited by the applicable result format;
3. generate a new random `bundle_id`;
4. add linkage only when enabled by trusted local initialization policy;
5. encode and persist the exact retryable bundle within the 262,144-byte bundle and local pending-storage limits;
6. submit the bundle through the configured ingestion path;
7. retransmit the exact same bytes or semantically identical canonical object with the same `bundle_id` after an ambiguous delivery failure;
8. delete the local bundle immediately after durable acknowledgement processing or after at most 86,400 seconds without acknowledgement.

<a id="REQ-BUNDLE-0016"></a>

**REQ-BUNDLE-0016:**

Changing linkage mode, epoch, token, result membership, or result content during a retry is not an exact retransmission and requires a new bundle identifier.

## Validation

<a id="REQ-BUNDLE-0017"></a>

**REQ-BUNDLE-0017:**

- `bundle_id` must decode to exactly 128 bits and must not be all zeroes.

<a id="REQ-BUNDLE-0021"></a>

**REQ-BUNDLE-0021:**

- `results` must contain 1–16 entries and the complete bundle must not exceed 262,144 encoded bytes.

<a id="REQ-BUNDLE-0022"></a>

**REQ-BUNDLE-0022:**

- Each result must pass the common Measurement Result schema and its exact registered test Output schema.

<a id="REQ-BUNDLE-0023"></a>

**REQ-BUNDLE-0023:**

- `linkage` must be absent when linkage is disabled or unavailable.

<a id="REQ-BUNDLE-0024"></a>

**REQ-BUNDLE-0024:**

- `linkage.mode` must be `rotating_installation`.

<a id="REQ-BUNDLE-0025"></a>

**REQ-BUNDLE-0025:**

- `linkage.scope` must equal the locally configured scope; it must not be accepted from a task or collector response.

<a id="REQ-BUNDLE-0026"></a>

**REQ-BUNDLE-0026:**

- `linkage.token` must decode to exactly 256 bits.

<a id="REQ-BUNDLE-0027"></a>

**REQ-BUNDLE-0027:**

- Unknown fields, invalid encodings, or partially populated linkage objects invalidate the bundle before submission.

<a id="REQ-BUNDLE-0028"></a>

**REQ-BUNDLE-0028:**

- The library retains at most 32 pending bundles and 4,194,304 aggregate pending bytes.

## Privacy and Safety Requirements

<a id="REQ-BUNDLE-0018"></a>

**REQ-BUNDLE-0018:**

- The default configuration omits `linkage`.

<a id="REQ-BUNDLE-0029"></a>

**REQ-BUNDLE-0029:**

- A bundle must not contain advertising IDs, vendor IDs, device serials, hardware IDs, push tokens, account IDs, email addresses, phone numbers, SIM or subscriber identifiers, host application user IDs, or identifiers derived from them.

<a id="REQ-BUNDLE-0030"></a>

**REQ-BUNDLE-0030:**

- `bundle_id` and `linkage.token` must never be copied into measurement traffic or sent to the Network Context endpoint.

<a id="REQ-BUNDLE-0031"></a>

**REQ-BUNDLE-0031:**

- Linkage must not affect which tasks are delivered to or executed by a particular installation.

<a id="REQ-BUNDLE-0032"></a>

**REQ-BUNDLE-0032:**

- The collector must treat linkage tokens as sensitive pseudonymous data rather than anonymous data.

<a id="REQ-BUNDLE-0033"></a>

**REQ-BUNDLE-0033:**

- Collection infrastructure should avoid retaining a source IP address, precise arrival time, or transport logs together with a linkage token. Where feasible, ingestion should separate transport handling from research storage.

<a id="REQ-BUNDLE-0034"></a>

**REQ-BUNDLE-0034:**

- Access to raw linkage tokens must be restricted, audited, and limited in retention.

<a id="REQ-BUNDLE-0035"></a>

**REQ-BUNDLE-0035:**

- Analysis and publication must aggregate combinations of linkage, time, region, ASN, network type, and `connection_code` because those values can become identifying in combination.

<a id="REQ-BUNDLE-0036"></a>

**REQ-BUNDLE-0036:**

- Hashing a host or platform identifier does not make it acceptable. The token must be derived from a random Barometer installation secret as defined by the library specification.

## Interpretation

<a id="REQ-BUNDLE-0019"></a>

**REQ-BUNDLE-0019:**

Matching tokens establish only that bundles were produced with the same locally stored Barometer installation secret, deployment scope, and rotation epoch. They do not establish that the same person, device owner, account, physical location, or access network produced the bundles.

<a id="REQ-BUNDLE-0020"></a>

**REQ-BUNDLE-0020:**

A missing or changed token may result from disabled linkage, epoch rotation, application data clearing, reinstall detection, key loss, storage failure, migration to another device, or an explicit privacy reset. It must not be interpreted as a new person.
