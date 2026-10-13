# Execution Format

**Status:** Draft  
**Version:** 0.1.0

Runtime JSON values follow the shared [strict decoding contract](json-decoding.md) in addition to this document's schema, limits, and validation rules.

The `execution` object defines the selected network path, runtime constraints, and environmental requirements for a measurement run.

Execution constraints are evaluated immediately before a run starts. If one or more constraints are not satisfied, the probe may delay or skip execution according to the task schedule.

The selected network path changes how connections are established but does not change the registered protocol operation performed by the test. Other test-specific behavior belongs to the `options` object.

Canonical defaults and maxima are defined in [`Registered Initial Limits`](../library/registered-limits.md#attempt-limits).

## Execution Model

Execution constraints are evaluated for every execution attempt.

```
Task
    │
    ▼
Schedule determines a run is due
    │
    ▼
Evaluate execution constraints
    │
    ├── constraints satisfied
    │       │
    │       ▼
    │    Execute run
    │
    └── constraints not satisfied
            │
            ▼
    	Delay or skip execution
```

Execution constraints never create new runs.

## JSON Structure

```json
{
  "execution": {
    "network_path": "direct",
    "limits": {
      "max_duration_ms": 30000,
      "max_bytes_sent": 32768,
      "max_bytes_received": 131072,
      "max_connections": 8
    },
    "network": {},
    "device": {},
    "concurrency": {}
  }
}
```

## Fields

| Field | Required | Description |
|--------|:--------:|-------------|
| `network_path` | No | Network path used for the attempt. Default: `direct`. |
| `limits` | Yes | Runtime limits for a single execution attempt. |
| `network` | No | Required network conditions. |
| `device` | No | Device state requirements. |
| `concurrency` | No | Rules for concurrent execution with other tasks. |

### Network Path

`network_path` selects whether the test uses the device's direct network path or the single proxy currently configured by the host application.

Supported values:

| Value | Description |
|---|---|
| `direct` | Establish test connections without the host-configured proxy. This is the default. |
| `proxy` | Require the host-configured proxy for every proxy-compatible network operation in the attempt. |

Example:

```json
{
  "network_path": "proxy"
}
```

The task selects only `direct` or `proxy`. It cannot provide a proxy endpoint, `connection_code`, credentials, proxy identifier, or fallback behavior. Host configuration and proxy lifecycle are defined in [`library/proxy.md`](../library/proxy.md).

Before a proxy attempt starts, the probe must confirm that:

- a valid host proxy is configured;
- local policy permits the task to use it;
- the test and its concrete input and options are compatible with HTTP CONNECT;
- the proxy configuration can be held stable for the attempt.

The probe snapshots the selected path and current proxy configuration when the attempt starts. Every compatible network operation in that attempt must use the snapshot. A `NET-05` run must use one snapshot for all steps.

The probe must never silently fall back from `proxy` to `direct`. An absent, invalid, incompatible, unavailable, rejected, or reconfigured proxy produces an explicit non-censorship execution state.

### Limits

Runtime limits apply to a single execution attempt.

Example:

```json
{
  "limits": {
    "max_duration_ms": 30000,
    "max_bytes_sent": 32768,
    "max_bytes_received": 131072,
    "max_connections": 8
  }
}
```

#### Fields

| Field | Required | Description |
|--------|:--------:|-------------|
| `max_duration_ms` | No | Maximum runtime for one execution attempt; default 30,000 and maximum 60,000. |
| `max_bytes_sent` | No | Maximum application bytes supplied to network APIs; default 32,768 and maximum 65,536. |
| `max_bytes_received` | No | Maximum application bytes accepted from network APIs; default 131,072 and maximum 262,144. |
| `max_connections` | No | Maximum TCP connections or HTTP CONNECT tunnels opened; default 8 and maximum 12. |

Omitted fields receive the registered defaults. A task may request lower positive values. Values above a registered or stricter local limit are rejected rather than clamped.

The byte limits exclude DNS, TCP, TLS, HTTP, proxy, and operating-system framing that the application cannot count portably. Implementations must still stop reads and writes promptly at the application boundary and document buffering limitations.

### Network

Defines required network conditions.

Network conditions may not always be detectable, depending on the platform. In such cases, the task may not run.

Example:

```json
{
  "network": {
    "allowed_transports": [
      "wifi",
      "cellular"
    ],
    "vpn_policy": "any",
    "require_validated": true,
    "context": {
      "required_fields": [
        "country_code"
      ],
      "allowed_country_codes": [
        "RU"
      ]
    }
  }
}
```

#### Fields

| Field | Required | Description |
|--------|:--------:|-------------|
| `allowed_transports` | No | Base network transports on which the task may execute. |
| `vpn_policy` | No | Defines whether detected VPN usage affects execution eligibility. Default: any |
| `require_validated` | No | Require confirmed Internet connectivity, system method will be used to check when available, lib internal check will be called otherwise. |
| `context` | No | Requirements evaluated against the selected path's normalized Network Context. |

Initial network transports:

- wifi
- cellular

##### VPN Policy

Supported values:

| Value | Description |
|---|---|
| `any` | VPN state does not restrict execution. |
| `exclude` | Execute only when the probe determines that no VPN is active. |
| `require` | Execute only when the probe determines that a VPN is active. |

The probe may observe VPN state as:

```text
detected
not_detected
unknown
```

An unknown state must not be treated as `not_detected`.

VPN eligibility is evaluated as follows:

| VPN policy | Detected | Not detected | Unknown |
|---|:---:|:---:|:---:|
| `any` | Run | Run | Run |
| `exclude` | Do not run | Run | Do not run |
| `require` | Run | Do not run | Do not run |

##### Network Context Requirements

`context` defines coarse metadata that must be available before execution. Acquisition, caching, endpoint fallback, and privacy requirements are defined in [`library/network-context.md`](../library/network-context.md). Field normalization is defined in [`network-context.md`](network-context.md).

Example:

```json
{
  "context": {
    "required_fields": [
      "country_code",
      "asn"
    ],
    "allowed_country_codes": [
      "RU"
    ]
  }
}
```

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `required_fields` | array of strings | No | Unique values from `country_code`, `region_code`, and `asn`. | Egress fields that must be available before execution. |
| `allowed_country_codes` | array of strings | No | Non-empty, unique ISO 3166-1 alpha-2 uppercase codes. | Execute only when the selected path's egress country is in the list. |

Requirements always apply to the same `network_path` selected for the measurement. Tasks cannot request a context lookup through another path or configure the primary or fallback endpoint.

Evaluation rules:

- A missing, invalid, or unavailable required field makes the constraint unsatisfied.
- `allowed_country_codes` implicitly requires `country_code`.
- An `unknown` value must not match an allowlist.
- Endpoint failure after bounded cache and fallback handling records `network_context_unavailable` when a required field cannot be satisfied; it is not evidence of censorship.
- Region, ASN, provider, and operator allowlists are not supported in the initial task format.
- Local deployment policy may impose stricter eligibility and always retains the final decision.

When `context` is absent, failure to obtain egress context does not by itself block the measurement. The result records the unavailable context if local policy permits execution.

### Device

Defines device requirements.

Example:

```json
{
  "device": {
    "minimum_battery_percent": 20,
    "allow_charging_only": false
  }
}
```

#### Fields

| Field | Required | Description |
|--------|:--------:|-------------|
| `minimum_battery_percent` | No | Minimum battery level required. |
| `allow_charging_only` | No | Execute only while charging. |

The probe may enforce stricter local policies.

### Concurrency

Defines whether this task may execute alongside other measurements.

Example:

```json
{
  "concurrency": {
    "mode": "exclusive"
  }
}
```

Supported modes:

| Mode | Description |
|------|-------------|
| `shared` | May execute with other measurements. |
| `exclusive` | Must execute alone. |

Exclusive execution is useful for measurements whose timing or bandwidth would be affected by other network activity.

## Constraint Evaluation

A run may start only if all execution constraints are satisfied.

Example:

```
battery >= minimum
AND network type allowed
AND selected network path available
AND required network context available and allowed
AND runtime limits available
AND concurrency rules satisfied
```

The probe always has the final decision.

It may reject execution because of additional local policy, operating-system restrictions, or user preferences.

## Example

```json
{
  "execution": {
    "network_path": "proxy",
    "limits": {
      "max_duration_ms": 30000,
      "max_bytes_sent": 32768,
      "max_bytes_received": 131072,
      "max_connections": 8
    },
    "network": {
      "allowed_transports": [
        "wifi"
      ],
      "vpn_policy": "any",
      "require_validated": true,
      "context": {
        "required_fields": [
          "country_code"
        ],
        "allowed_country_codes": [
          "RU"
        ]
      }
    },
    "device": {
      "minimum_battery_percent": 20
    },
    "concurrency": {
      "mode": "shared"
    }
  }
}
```
