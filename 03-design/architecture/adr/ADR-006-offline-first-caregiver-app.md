# ADR-006: Offline-first Caregiver Mobile App with an encrypted command outbox

## Document control

| Field | Value |
|---|---|
| Document ID | ADR-006 |
| Version | 1.1 |
| Status | Accepted |
| Owner | Business Analyst |
| Last updated | 2026-06-12 |
| Reviewers | Engineering Lead, mobile developer, Clinical SME (RN advisor), Compliance and Privacy Officer, QA Lead |

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-03-04 | Accepted before Sprint S1 |
| 1.1 | 2026-06-12 | Conflict rules for doses and cancelled visits clarified in UAT; capacity table re-measured |

## Status

**Accepted, 2026-03-04.** Deciders: Engineering Lead, mobile developer, Business Analyst. Consulted: Clinical SME (RN advisor), Compliance and Privacy Officer, pilot caregivers (PER-01 profile).

## Context and problem statement

Discovery observed that caregivers lose signal in rural Ohio counties, basement apartments and some supported-living homes. In the baseline, only 81% of visits had complete EVV data (target 97% or more). An app that needs a connection at clock-in would turn every dead zone into a missing punch.

NFR-AVL-02 requires the app to capture EVV with no server connectivity for up to 72 hours of punches. FR-EVV-05 requires encrypted storage on the device and sync on reconnect, with punches synced more than 24 hours after capture flagged. BR-025 requires the device capture time to be kept as the punch time and the server receipt time separately. NFR-MOB-02 requires the offline queue to be encrypted and local data to be wiped remotely on deactivation. The app must stay under 60 MB and usable at 400 kbps (NFR-MOB-01), and the caregiver must clock in within 3 taps (NFR-USE-01).

Care documentation (tasks, doses, vitals, notes) happens during the same visits, so offline support for punches alone would leave the clinical record incomplete.

How should the Caregiver Mobile App work without connectivity while keeping the server authoritative and PHI protected on the device?

## Decision drivers

1. Zero data loss for up to 72 hours offline, including app restarts and reboots (NFR-AVL-02).
2. Server authority over evidence and clinical rules (BR-021, BR-024); the device records, the server decides.
3. PHI on the device is encrypted, minimal and wipeable (NFR-MOB-02, NFR-PRIV-01).
4. Predictable, explainable conflict handling that never silently overwrites a human decision or a clinical record.
5. Feasible for one mobile developer within the R1 timeline.

## Considered options

### Option 1: Online-only with request retry

| Pros | Cons |
|---|---|
| Simplest; no local PHI | Fails NFR-AVL-02 outright; recreates the 81% baseline problem |
| | Retries without durable storage lose data on app kill |

### Option 2: Offline punch queue only

The app caches today's visits and queues clock-in and clock-out; everything else needs a connection.

| Pros | Cons |
|---|---|
| Small scope; covers the EVV minimum | Tasks, doses, vitals and notes cannot be documented offline, so FR-EVV-06 (task statuses at clock-out) and eMAR documentation fail in dead zones |
| | Caregivers would have to remember and enter care later, raising undocumented-dose risk (OBJ-03) |

### Option 3: Offline-first read cache plus an ordered command outbox, server-authoritative (chosen)

The app keeps an encrypted local read model of the caregiver's assigned work and records every user action as a command in an ordered outbox. The server replays commands, applies all rules and returns results.

| Pros | Cons |
|---|---|
| Covers the whole visit flow offline | More client code: cache refresh, outbox, replay, conflict messaging |
| The server stays the single source of truth; device logic is limited to capture and display | Some rules can be applied only after sync (geofence, identity, PRN limits across caregivers) |
| Commands are idempotent by client-generated ID | Local PHI on the device must be protected and minimized |

### Option 4: Bi-directional database replication or CRDT sync engine

| Pros | Cons |
|---|---|
| General-purpose; handles arbitrary edits | Merging clinical records automatically is unsafe (for example two caregivers documenting the same dose) |
| | Heavy dependency and learning curve for one mobile developer |
| | Replicates more data to the device than the caregiver needs |

## Decision outcome

**Chosen option: Option 3, offline-first read cache plus an ordered, encrypted command outbox with server-authoritative replay.** It meets the 72-hour capture requirement for the whole visit flow (driver 1) while keeping every rule decision on the server (driver 2) and limiting device data to what the caregiver needs (driver 3).

### Local store and encryption

- SQLCipher (AES-256) database; a random 256-bit key is generated on first sign-in and stored in iOS Keychain or Android Keystore (hardware-backed where available), accessible only after device unlock.
- The app re-authenticates the caregiver with device PIN or biometrics after 12 hours (FR-IAM-04); this works offline.
- Photos for incidents are stored as separately encrypted files referenced from the outbox.
- No PHI in push payloads, logs or crash reports (BR-056, NFR-OBS-01).

### Read cache (minimum necessary)

- Assigned visits from now to now + 72 hours, the client's first name, last initial, client number and full service address for navigation (no geocoded coordinates, which the API never returns), Active care-plan tasks, due dose tasks with order details, allergies, vital ranges and emergency contact phone.
- Refreshed on app open, on push "schedule changed" signals and every 15 minutes while online.
- Client data is removed from the device 24 hours after the caregiver's last cached visit with that client, provided its outbox is fully synced.

### Command outbox

Every action is stored before the UI confirms it. Each command carries:

| Field | Purpose |
|---|---|
| `commandId` (UUID v4) | Idempotency; becomes `evv_punches.id` for punches |
| `type` | Punch In or Out (with the identity capture package when required), task result, dose outcome, PRN administration, vital reading, note, incident |
| `visitId`, payload | Business data, including GPS latitude, longitude and accuracy for punches |
| `deviceCapturedAt` | Device wall-clock time with UTC offset; becomes `punch_time` (BR-025) |
| `monotonicMs`, `bootId` | Elapsed time since boot and boot session, for clock-skew estimation |
| `serverOffsetMs` | Last known difference between device and server time, measured on each successful API response |
| `sequence` | Per-device order of capture |

**Sync.** On connectivity, the app sends punches first through `POST /evv/punches/sync` (batches of up to 50, in `sequence` order), then dose outcomes, vitals, task results, notes and finally photos, each through its regular endpoint with `Idempotency-Key = commandId`. Each item returns accepted, duplicate or rejected-with-reason; the app removes accepted and duplicate items and shows rejected items to the caregiver. A dropped connection mid-batch is retried safely.

### Device time and server time

- `punch_time` is the device capture time and `received_at` is the server receipt time (BR-025); both are stored in UTC.
- A punch received more than 24 hours after `punch_time` raises LATE_OFFLINE_SYNC; one exception per visit.
- The server estimates the true capture time from `monotonicMs`, `bootId` and `serverOffsetMs`. If the device clock differs from the estimate by more than 5 minutes, the server writes a note on the punch at insert ("Device clock differs from server estimate by N min") for Coordinator review; no new exception code is added (SRS TBD-04 working assumption). If the device rebooted while offline, the estimate is unavailable and the note says so. The punch time itself is not altered.
- Late-entry and note-lock rules evaluate the device capture time for records captured offline, so a dose documented on time but synced late is not labelled Late entry; the receipt time remains visible.

### Conflict rules

| Situation | Rule | Refs |
|---|---|---|
| Same command sent twice | Second is acknowledged as duplicate; no second record | BR-026 |
| Visit marked Missed on the server while punches waited on the device | Punches with a capture time inside the clock-in window move the visit from Missed to In progress or Completed and are evaluated normally | BR-019, BR-023 |
| Visit cancelled while the caregiver delivered care offline | Punches are accepted on a new visit for the same client, caregiver and authorization, with UNSCHEDULED_VISIT; the cancelled visit stays Cancelled and is linked in history | FR-EVV-07 |
| Visit reassigned while offline and both caregivers clock in | The current assignee's punches attach to the visit; the other caregiver's punches attach to a new visit with UNSCHEDULED_VISIT; nothing is paid or billed until Verified | BR-028 |
| Late device clock-out for an auto-closed visit | Device punch supersedes the System placeholder; AUTO_CLOSED still needs Coordinator resolution | BR-027, ADR-002 |
| Device punch after a Coordinator's Manual correction | Stored and shown; does not override the Manual punch | ADR-002 |
| Care plan changed while offline | The visit uses the version Active at the clock-in punch time | BR-012 |
| Dose already documented by another caregiver | First outcome received stands; the second is rejected, the caregiver sees why, and the Clinical Supervisor is alerted to check for a double administration | FR-MAR-03 |
| PRN given offline beyond limits recorded by a colleague | Device blocks using its cached PRN history; the server re-checks on sync and alerts the Clinical Supervisor if limits were exceeded; the record is kept because it describes what happened | BR-033 |
| Note captured before lock but synced after | Accepted as the note if captured before clock-out + 24 h; otherwise saved as an addendum | BR-035 |
| Out-of-range vital captured offline | Device shows the care-plan instruction immediately from cached ranges; the urgent alert is sent on sync with the capture time visible | FR-MAR-08, BR-034 |
| Identity verification required but device offline | Capture package stored with the punch and matched at sync; validity measured on the device clock; a failed or missing match raises IDENTITY_CHECK_FAILED | ADR-004, SRS TBD-03 |

### Capacity (72-hour design case)

| Item | Per visit | 72 h capacity | Size each | Total |
|---|---|---|---|---|
| Cached visits with client summary, tasks and doses | n/a | 30 visits | 6 KB | 180 KB |
| Punches | 2 | 60 | 1 KB | 60 KB |
| Task results | 8 | 240 | 0.3 KB | 72 KB |
| Dose outcomes and PRN records | 4 | 120 | 0.5 KB | 60 KB |
| Vital readings | 2 | 60 | 0.3 KB | 18 KB |
| Visit notes | 1 | 30 | 8 KB | 240 KB |
| Incident photos (compressed) | n/a | 15 | 0.8 MB | 12 MB |
| **Total** | | | | **about 13 MB** |

At 400 kbps, the non-photo records (about 0.6 MB) sync in under 15 seconds and photos in about 4 minutes. The app reserves 50 MB and warns when free device storage drops below 100 MB. The offline banner shows the time since the last sync and the number of queued items; after 48 hours offline it asks the caregiver to find a connection or call the office.

### Remote wipe

On caregiver deactivation (FR-WRK-06), sessions are revoked. When the device next contacts the server, it receives a wipe instruction that allows one final upload of the outbox under a sync-only scope, then the app deletes the database, photo files and key. If the device never reconnects, the data stays encrypted behind device authentication; the Coordinator records the affected visits with Manual punches and reason codes.

## Consequences

**Positive**

- EVV capture no longer depends on coverage, which supports the 97% complete-EVV target.
- Every rule is evaluated once, on the server, with full context; the device cannot fabricate a geofence pass or identity result.
- Retries, reboots and partial syncs are safe by construction.

**Negative**

- Coordinators see Missed visits and Clinical Supervisors may receive missed-dose escalations for work that was documented offline but not yet synced; the app warns offline caregivers that the office may call, and the alerts stop as soon as records sync.
- Some safety checks (PRN limits across caregivers, double documentation) can only be confirmed after sync.
- PHI resides on devices, so device loss is a privacy event to assess; encryption and wipe limit the exposure.
- The outbox, replay and conflict messaging add test effort; the QA device matrix includes airplane-mode, reboot-while-offline and clock-change cases.

## Compliance and requirements links

| Type | IDs |
|---|---|
| Functional requirements | FR-EVV-05, FR-EVV-06, FR-EVV-07, FR-IAM-04, FR-WRK-06, FR-MAR-03, FR-MAR-08, FR-DOC-02 |
| Business rules | BR-012, BR-019, BR-021, BR-025, BR-026, BR-027, BR-033, BR-035, BR-056 |
| Non-functional requirements | NFR-AVL-02, NFR-MOB-01, NFR-MOB-02, NFR-USE-01, NFR-PRIV-01, NFR-DAT-01 |
| User stories | US-027 |
| Regulation (designed to support) | 21st Century Cures Act s.12006 (complete EVV data); HIPAA Security Rule 45 CFR 164.312(a)(2)(iv) encryption |

## Related documents

- [Offline EVV capture spec](../../../08-ai-assisted-ba/specs/001-offline-evv-capture/spec.md)
- [Sequence diagrams: offline capture and sync](../../diagrams/sequence-diagrams.md)
- [ADR-002 Append-only EVV punch ledger](ADR-002-append-only-evv-punch-ledger.md)
- [ADR-004 Identity verification vendor adapter](ADR-004-identity-verification-vendor-adapter.md)
- [Wireframes cg-01 and cg-02](../../wireframes/README.md)
- [EP-06 EVV user stories](../../../05-delivery/user-stories/EP-06-evv.md)
