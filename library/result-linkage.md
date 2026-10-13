# Result Linkage and Private State

**Status:** Draft  
**Version:** 0.1.0

Runtime JSON values follow the shared [strict decoding contract](../data-formats/json-decoding.md) in addition to this document's schema, limits, and validation rules.

## Overview

Barometer can optionally correlate Result Bundles produced by the same library installation during a limited rotation epoch. It does this with a random installation secret held in non-synchronizing platform-protected storage and a token derived locally from that secret.

This mechanism is pseudonymous, not anonymous. It deliberately does not identify a person, host application account, device, or access network. The default mode is no cross-bundle linkage.

The serialized bundle representation is defined in [`data-formats/result-bundle.md`](../data-formats/result-bundle.md).

## Goals and Non-goals

The mechanism supports:

- grouping multiple task results in one packet without persistent identity;
- optional correlation of different packets for a limited period;
- rotation that prevents ordinary correlation across epochs;
- explicit deletion through Barometer and host application clear-data behavior;
- Flutter integration using plain serializable initialization values and simple methods.

The mechanism does not support:

- identifying or counting unique people;
- correlating installations across applications, deployments, devices, reinstalls, or data resets;
- restoring linkage through a user account, platform backup, or cloud synchronization;
- remotely selecting a particular installation for tasks;
- stable or permanent identifiers in the initial version.

## Initialization Configuration

The host may enable rotating installation linkage with an ordinary serializable object:

```json
{
  "result_linkage": {
    "mode": "rotating_installation",
    "scope": "org.example.app.production",
    "rotation_period_seconds": 604800
  }
}
```

| Field | Type | Required | Constraints | Description |
|---|---|:---:|---|---|
| `mode` | string | Yes | `none` or `rotating_installation` | Whether separate bundles can be correlated within an epoch. |
| `scope` | string | Conditional | Required for `rotating_installation`; 1–128 lowercase ASCII letters, digits, `.`, `_`, or `-`; fixed for the deployment and not user-specific. | Domain separator preventing cross-deployment token equality. |
| `rotation_period_seconds` | integer | Conditional | Required for `rotating_installation`; 86,400 through 604,800. | Length of a linkage epoch. |

If `result_linkage` is absent, Barometer behaves as if `mode` were `none`. In `none` mode, `scope` and `rotation_period_seconds` are rejected.

The scope identifies a reviewed Barometer deployment, such as one application environment. It must not contain or be derived from a user, account, installation, device, access network, proxy endpoint, experiment participant, or other high-cardinality value.

The first version does not permit tasks, server responses, or runtime task configuration to enable linkage, change its scope, or lengthen its rotation. A host configuration change requires library reinitialization. Local safety policy may disable linkage regardless of initialization input.

## Installation Secret

When rotating linkage is enabled and no valid key exists, the platform storage implementation creates a new cryptographically random 256-bit installation secret. The secret:

- is owned exclusively by Barometer's private-state subsystem;
- is never returned through the Go, gomobile, Flutter, Dart, host application, task, result, logging, analytics, or diagnostic APIs;
- is never sent to the collector, Network Context endpoint, proxy, measurement target, or another service;
- is non-exportable when the platform permits the required HMAC operation inside protected storage;
- is excluded from backup, restore, migration, and cloud synchronization;
- is deleted by explicit Barometer data clearing and by the platform clear-data lifecycle defined below.

Barometer must generate a new secret rather than deriving one from an advertising ID, vendor ID, device serial, hardware property, push token, application account, operating-system account, SIM, phone number, email address, pre-existing analytics identifier, or host-provided value.

## Token Derivation

For a bundle created in rotation epoch `E`, Barometer derives:

```text
message = "barometer-result-linkage-v1" || 0x00 ||
          scope || 0x00 ||
          decimal(E)

token = HMAC-SHA-256(installation_secret, message)
```

`E` is the non-negative integer obtained by dividing trusted wall-clock Unix time by `rotation_period_seconds` and taking the floor. The encoded epoch in the result is the same integer used in the HMAC input.

The fixed purpose string and separators provide domain separation. Tokens derived for different scopes or epochs are different even when the installation secret is unchanged.

The 32-byte token is encoded as unpadded base64url. The secret and intermediate HMAC state must be cleared from ordinary process memory where the implementation and platform allow it.

If the platform clock is unavailable, outside supported bounds, or moves backwards into an earlier epoch during one initialized library lifetime, Barometer omits linkage until it can establish a non-decreasing valid epoch. It must not reuse an earlier emitted epoch to extend tracking.

## Rotation Semantics

All bundles created in the same scope and epoch have the same token. Bundles created after the epoch changes use the newly derived token.

The collector can correlate bundles only within an epoch unless it possesses other identifying data. Barometer must not send a mapping between old and new tokens. The collector must not ask the library to prove continuity across epochs.

Rotation period selection is a deployment privacy decision. It must be from 86,400 through 604,800 seconds and should be no longer than the shortest period needed for the documented analysis. Linkage must not be silently extended for operational convenience.

## Go Core and Mobile Binding Architecture

Barometer's measurement and bundle logic remains in Go. Platform-protected storage is exposed to the Go core through a small internal capability, conceptually:

```go
type LinkageKeyStore interface {
    DeriveHMACSHA256(message []byte) ([32]byte, error)
    Delete() error
}
```

The interface is internal to the Barometer implementation. It must not be accepted from Flutter or from the host application, and the raw installation secret is not part of the interface. `DeriveHMACSHA256` creates the protected key when necessary and performs derivation without exporting it when supported.

The Android and Apple library bindings own the concrete storage adapter and connect it to the Go core during native initialization. A Flutter-facing package passes only the plain `result_linkage` configuration object and exposes lifecycle methods such as:

```dart
await Barometer.initialize({
  "result_linkage": {
    "mode": "rotating_installation",
    "scope": "org.example.app.production",
    "rotation_period_seconds": 604800
  }
});

await Barometer.clearMeasurementData();
```

The exact exported method names may follow binding conventions, but the semantics must be equivalent. Flutter does not pass a callback, native interface, key handle, byte array containing the secret, or platform storage object.

Desktop and test builds may provide an explicitly marked ephemeral in-memory implementation. Such an implementation loses linkage on process exit and must not be used as an unnoticed fallback on mobile.

## Clear-data Contract

`clearMeasurementData` is a privacy operation. It must:

1. stop admission of new measurements and bundle construction;
2. cancel running measurements using bounded cleanup;
3. delete pending and acknowledged local result bundles;
4. delete the installation secret or protected key;
5. delete linkage epoch state, reinstall sentinels, network-context cache, and other Barometer-owned persistent state;
6. clear in-memory linkage material and cached tokens;
7. return only after deletion succeeds or return an explicit error identifying incomplete clearing;
8. create no replacement secret until a later operation actually requires linkage.

The method must be safe to call repeatedly. It must not upload pending results before deletion, and clearing must not itself send a network request.

The host application must connect every user-visible “clear local data,” “reset privacy data,” “delete downloaded/offline data,” or equivalent action that promises to remove Barometer data to `clearMeasurementData`. Logging out of a host account should call it when the product describes logout as removing local user data. Barometer must not infer account semantics itself.

If the host deletes its storage without first calling Barometer, platform lifecycle behavior must still remove or invalidate the secret as described below. The integration guide and release validation must test both the explicit API and operating-system data clearing.

## Android Storage

The Android binding should use an application-scoped Android Keystore HMAC-SHA-256 key that is non-exportable where supported. Associated non-secret state must be stored in the application's no-backup private directory, such as `Context.getNoBackupFilesDir()`, and must not be stored in shared preferences or files eligible for Auto Backup, device-to-device transfer, external storage, or host analytics storage.

The binding must not enable cloud or cross-device synchronization for Barometer private state. Backup rules should explicitly exclude all Barometer state even when it is already placed in the no-backup directory, providing defense in depth.

Android application data clearing and uninstall normally remove application-private data and application-scoped Keystore entries. The binding must verify on initialization that its no-backup state and protected key belong to the same Barometer state generation. If one exists without the other, it deletes any orphaned material and creates a new secret only when linkage is next required.

The Android implementation must test at minimum:

- explicit `clearMeasurementData`;
- system Settings “Clear storage” or “Clear data”;
- uninstall followed by reinstall;
- application backup and restore to the same and a different device where supported;
- device-to-device migration;
- interrupted deletion and orphaned-key recovery.

No test may rely on a stable token surviving any of these reset, restore, or migration cases.

## Apple Platform Storage

The Apple binding should store the installation secret as a Keychain item with `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` when background derivation is required, set `kSecAttrSynchronizable` to false, and use an application-private access group. An integration that never derives tokens in the background may use the more restrictive `kSecAttrAccessibleWhenUnlockedThisDeviceOnly`. The item must not be shared with unrelated applications, extensions, analytics components, or host account services.

`ThisDeviceOnly` prevents migration through backups, but Keychain items can survive application uninstall. Therefore the binding must also maintain a non-secret reinstall sentinel in the application's ordinary sandbox container. On initialization:

1. if both the sentinel and Keychain item exist, the existing installation state may continue;
2. if the sentinel is absent, the binding treats the application as newly installed, deletes any surviving Barometer Keychain item, creates the sentinel, and creates a new secret only when linkage is required;
3. if the sentinel exists but the Keychain item is absent or invalid, the binding removes inconsistent linkage state and creates a new secret only when required.

The sentinel must not be placed in Keychain, iCloud key-value storage, CloudKit, a shared app group, `NSUbiquitousKeyValueStore`, or another synchronizing store. Backup and restore behavior must be tested so a restored sentinel cannot cause an old or migrated Keychain identity to be accepted. If the target platform cannot reliably distinguish a restored container from the original installation, the integration must prefer resetting linkage over preserving it.

The Apple implementation must test at minimum:

- explicit `clearMeasurementData`;
- uninstall followed by reinstall;
- encrypted and unencrypted backup/restore where applicable;
- migration to another device;
- iCloud Keychain enabled and disabled;
- missing sentinel, missing Keychain item, and interrupted deletion.

No test may rely on a stable token surviving reinstall, restore, or migration.

## Storage Failure

If protected, non-synchronizing storage is unavailable, locked beyond the bounded operation, inconsistent, or fails validation, Barometer must omit the `linkage` object and continue with single-use `bundle_id` grouping when local policy permits. It must not:

- fall back to an exported secret in ordinary preferences or files;
- ask Flutter or the host to persist the secret;
- generate a host-visible stable identifier;
- retain one constant token in memory indefinitely;
- block result deletion.

The library may expose a coarse local diagnostic such as `linkage_unavailable`. The diagnostic must not contain key aliases, platform account information, token material, or persistent identifiers, and it is not evidence of censorship.

## Ingestion Separation

Linkage safety depends on the complete delivery path, not only token derivation. Collectors should separate the network-facing ingress component from research storage so transport metadata is removed before a bundle reaches analysis.

The ingress component should:

- avoid or minimize source-IP logging;
- remove forwarding headers and other transport identifiers;
- avoid application account authentication on the bundle endpoint where the deployment permits;
- retain `bundle_id` only as long as required for idempotency and retry handling;
- enforce size, rate, and schema limits without building a persistent device profile.

If the host delivers bundles through an API already authenticated to a user account, rotating linkage does not prevent the backend from associating results with that account. Such an integration requires a separate privacy and safety review and must not be described as anonymous.

## Privacy and Safety Requirements

- Linkage is disabled by default.
- Enabling linkage is trusted local deployment policy, not task-controlled behavior.
- The token is installation-scoped and must never be called a user identifier.
- Raw secrets and tokens must not be logged, placed in crash reports, or exposed to analytics.
- Linkage must not be used for per-installation task selection, retaliation, access control, advertising, product analytics, or account enforcement.
- Network Context acquisition must never receive `bundle_id`, scope, epoch, or token.
- Measurement targets and proxies must never receive linkage material.
- Raw token retention must be bounded to the documented research need.
- Combining a token with precise timestamps, source IP addresses, rare ASN and region combinations, or host account data increases re-identification risk and must be prevented or separately reviewed.
- The host must provide an explicit reset path wherever linkage is enabled.

## Known Limitations

- Secure storage reduces secret exposure but does not make an uploaded token anonymous.
- A compromised device, host application, binding, collector, or operating system may observe or misuse linkage.
- Installations cannot be equated with people, and installation counts cannot be presented as unique-user counts.
- Clock changes can shorten an epoch or make linkage temporarily unavailable.
- Platform storage and backup behavior can change between operating-system versions and requires release testing.
- A collector that retains transport identifiers can defeat the privacy benefit of rotating tokens.
