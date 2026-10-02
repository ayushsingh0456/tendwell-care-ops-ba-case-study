# Feature Specification: Offline EVV Capture

## Document control

| Field | Value |
|---|---|
| Document ID | TW-SPEC-001 |
| Version | 1.3 |
| Status | Approved |
| Owner | Business Analyst |
| Last updated | 2026-09-24 |
| Reviewers | Product Owner, Engineering Lead, mobile developer, QA Lead, Clinical SME (RN advisor), Compliance and Privacy Officer |

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-04-08 | First draft generated with `/specify` from the input below; reviewed and edited by the Business Analyst |
| 1.1 | 2026-04-14 | Clarification sessions 1 and 2; all `[NEEDS CLARIFICATION]` markers resolved; approved for Sprint 4 |
| 1.2 | 2026-06-12 | UAT session: conflict rules aligned with ADR-006 v1.1 |
| 1.3 | 2026-09-24 | Aligned with SRS v1.3: Low GPS accuracy (CR-004) applies to synced offline punches; no-fix rule added |

**Feature Branch**: `001-offline-evv-capture`
**Created**: 2026-04-08
**Status**: Approved; implemented in Sprint 4 (2026-04-20 to 2026-05-01), released with the pilot on 2026-07-06
**Input**: User description: "Offline EVV capture for the Caregiver Mobile App. Caregivers must be able to clock in and out of assigned visits with no connectivity for up to 72 hours of punches. Punches are stored encrypted on the device and synced when connectivity returns. The device capture time is the punch time and the server receipt time is kept separately. Punches received more than 24 hours after capture are flagged Late offline sync. Sources: US-027, FR-EVV-05, BR-025, NFR-AVL-02, ADR-006. Mark anything not covered by these sources as [NEEDS CLARIFICATION]."

### Purpose and scope

This specification defines what offline EVV capture must do, for whom and why, in testable terms. It follows the GitHub Spec Kit format: this file is the output of `/specify` and the clarification sessions, [plan.md](plan.md) is the output of `/plan`, and [tasks.md](tasks.md) is the output of `/tasks`. An AI assistant produced the first draft; the Business Analyst owns the content, every requirement ID mapping and every clarification decision (see [AI-assisted BA](../../README.md)).

In scope: clock-in and clock-out captured without connectivity, care-plan task statuses and the visit note captured at offline clock-out, the encrypted on-device outbox, sync, and the server-side handling of punches that arrive late or after the visit changed. Out of scope here: offline dose outcomes, vitals and incident reports, which use the same outbox (ADR-006) but whose rules are owned by US-032 to US-035 and US-037; they are referenced only where they interact with punches.

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story

Rosa Delgado (PER-01), a home health aide, visits a client in a rural farmhouse with no cellular signal. She opens the Tendwell app at the door, taps "Clock in" on the next-visit card, delivers care, marks each care-plan task and writes her note, and taps "Clock out". The app confirms each step immediately with "Saved on this phone. It will sync when you are back online." Twenty minutes later, driving into town, her phone reconnects and the punches sync without her doing anything. Her Coordinator sees a normal visit with source MobileOffline, the server has computed the distance to the client's address, and the visit becomes Verified and counts for her pay.

### Acceptance Scenarios

Scenarios use the shared synthetic test data: client C-10234 at 418 Birchwood Lane, Lakemont, OH 43999, geofence radius 150 m; caregiver Rosa Delgado; visit 08:00 to 10:00 America/New_York under T1019; care plan version 3 with three tasks and "Requires visit note" = Yes.

1. **Given** Rosa's phone has no network connection, **When** she taps "Clock in" at 08:02 device time at the client's home, **Then** the punch is stored in the encrypted outbox with GPS coordinates, accuracy, device time and device ID, the app shows "Saved on this phone. It will sync when you are back online.", and the visit shows "In progress" in the app. (US-027-AC1)
2. **Given** Rosa's offline clock-in was captured at 08:02 and her clock-out at 10:01, **When** her phone reconnects at 11:40, **Then** both punches are sent in one batch to `POST /v1/evv/punches/sync`, each keeps its device capture time as the punch time and 11:40 as the server receipt time, each has source MobileOffline, the server computes each distance, and no LATE_OFFLINE_SYNC exception is raised. (US-027-AC2)
3. **Given** a punch was captured offline on 2026-09-15 at 08:02, **When** the server receives it at 2026-09-16 08:01 or 08:02, **Then** LATE_OFFLINE_SYNC is not raised; **When** it receives it at 2026-09-16 08:03, **Then** LATE_OFFLINE_SYNC is raised. (US-027-AC3)
4. **Given** a sync batch was accepted but the response was lost, **When** the app resends the same batch with the same punch IDs, **Then** the server returns each punch as duplicate and stores no new punches. (US-027-AC4)
5. **Given** Rosa worked 18 visits over 72 hours with no connectivity, **Then** all 36 punches are kept on the device and sync in capture order when she reconnects; **and if** she tries to sign out with unsynced punches, **Then** the app warns "You have 36 visits that have not synced. Stay signed in until you are online." and keeps her signed in. (US-027-AC5)
6. **Given** the Coordinator reassigned the 08:00 visit to Maya while Rosa was offline and Rosa delivered it anyway, **When** Rosa's punches sync, **Then** her punches are kept and linked to an unscheduled visit for Rosa, and UNSCHEDULED_VISIT is raised so the Coordinator can reconcile the two visits. (US-027-AC6)
7. **Given** Rosa is clocked in offline using cached care plan version 3, **When** she taps "Clock out" with one task unmarked, **Then** clock-out is not recorded and the task is highlighted; **When** every task has a status and the note is written, **Then** clock-out is stored in the outbox. (FR-EVV-06, BR-012)
8. **Given** offline punches synced with fixes at 212 m (accuracy 18 m), 95 m (accuracy 3,400 m) and 40 m (accuracy 12 m) from the service address, **When** the server evaluates them, **Then** the results are LOCATION_MISMATCH, LOW_GPS_ACCURACY and no exception respectively, exactly as for online punches. (BR-021, BR-022)
9. **Given** the tenant requires identity verification and Rosa's phone is offline, **When** she clocks in, **Then** the punch is captured without an identity check and, on sync, IDENTITY_CHECK_FAILED is raised with the note "Not performed: device offline". (FR-EVV-04, ADR-004)
10. **Given** the Coordinator cancelled the 08:00 visit while Rosa was offline and Rosa delivered care, **When** her punches sync, **Then** they are accepted on a new visit for the same client, caregiver and authorization with UNSCHEDULED_VISIT, and the cancelled visit stays Cancelled and is linked in the visit history. (ADR-006)
11. **Given** the server marked the 08:00 visit Missed at 10:00 because no clock-in had arrived, **When** Rosa's offline punches captured at 08:02 and 10:01 sync at 11:40, **Then** the visit moves from Missed to Completed and is evaluated normally. (BR-019, BR-023)
12. **Given** a visit was auto-closed 14 hours after an offline clock-in with the scheduled end as a System placeholder, **When** Rosa's device clock-out syncs later, **Then** the device punch supersedes the placeholder and the AUTO_CLOSED exception remains open for Coordinator resolution. (BR-027, BR-026)
13. **Given** the pay period containing the visit was exported and locked, **When** an offline punch for that visit syncs and the visit becomes Verified, **Then** an adjustment line is created in the next open period referencing the original visit. (BR-046, FR-PAY-06)
14. **Given** Rosa's device clock was set 9 minutes fast while offline, **When** her punches sync, **Then** the punch time is stored as captured and the visit history shows "Device clock differs by 9 min" to the Coordinator. (BR-025, ADR-006)
15. **Given** Rosa's account was deactivated while her phone held unsynced punches, **When** the phone next connects, **Then** the outbox is uploaded once under a sync-only scope and the app then deletes its local data and key. (NFR-MOB-02, FR-WRK-06)

### Edge Cases

| Edge case | Expected behavior | Covered by |
|---|---|---|
| App killed or phone rebooted while offline | Outbox and cache persist; nothing is lost; sync resumes on next connectivity | SPEC-FR-002 |
| Connection drops mid-batch | Batch is retried with the same punch IDs; accepted items return duplicate | SPEC-FR-006 |
| More than 72 hours offline | Capture continues while storage allows; banner after 48 hours asks the caregiver to find a connection or call the office | SPEC-FR-011, SPEC-FR-012, C-01 |
| Free device storage below 100 MB | Warning shown; capture continues | SPEC-FR-012 |
| No GPS fix within 10 seconds | Punch stored without coordinates; server raises LOW_GPS_ACCURACY with note "No location fix" | SPEC-FR-003, C-11 |
| Visit not in the cache (assigned while offline) | Caregiver can start an unscheduled visit for a cached client; UNSCHEDULED_VISIT on sync | SPEC-FR-013 |
| Caregiver crosses a DST change while offline | Device time carries its UTC offset; durations computed in UTC (NFR-DAT-01) | SPEC-FR-003 |
| Same punch ID re-sent with different content | Rejected as a payload mismatch; original kept; mobile error report without PHI | SPEC-FR-006 |
| Dose documented offline while the server marks it Missed - undocumented | Outside this spec's rules; the outcome syncs with its capture time and the Missed - undocumented history is kept (BR-031) | C-12 |
| Coordinator recorded a Manual correction before the device punch arrived | Device punch stored and shown; does not override the Manual punch | SPEC-FR-015 |

---

## Requirements *(mandatory)*

### Functional Requirements

Each requirement maps to the canonical requirement or rule it elaborates, shown in parentheses. SPEC-FR IDs are local to this feature and never appear in the SRS; the canonical IDs remain the traceability anchor.

- **SPEC-FR-001**: The Caregiver Mobile App MUST let a caregiver clock in and clock out of an assigned visit with no network connectivity. (FR-EVV-05, FR-EVV-01)
- **SPEC-FR-002**: The app MUST write each offline punch to an encrypted on-device outbox before confirming it on screen, and the outbox MUST survive app restarts and device reboots. (FR-EVV-05, NFR-MOB-02)
- **SPEC-FR-003**: Each offline punch MUST capture GPS latitude, longitude and accuracy, the device capture time with its UTC offset, the device ID, a client-generated punch ID, a per-device sequence number and clock-skew data (monotonic elapsed time, boot ID, last known server offset). If no fix is available within 10 seconds, the punch is stored without coordinates. (FR-EVV-02, BR-020, BR-025)
- **SPEC-FR-004**: The server MUST store the device capture time as the punch time and its own receipt time separately, both in UTC, with source MobileOffline. (BR-025, NFR-DAT-01)
- **SPEC-FR-005**: The app MUST sync queued punches automatically when connectivity returns, in capture sequence, in batches of at most 50, before any other queued record type. (FR-EVV-05)
- **SPEC-FR-006**: Sync MUST be idempotent per punch ID: a re-sent punch with identical content returns duplicate and creates no record; a re-sent punch ID with different content is rejected. (BR-026, FR-EVV-05)
- **SPEC-FR-007**: The server MUST compute distance and apply location exceptions for synced punches exactly as for online punches; the device MUST NOT evaluate or display a geofence result. (BR-021, BR-022, FR-EVV-03)
- **SPEC-FR-008**: The server MUST raise LATE_OFFLINE_SYNC when a punch's receipt time is more than 24 hours after its punch time, at most once per visit. (BR-025, FR-EVV-07)
- **SPEC-FR-009**: The app MUST enforce the clock-in window offline (from 15 minutes before the scheduled start to the scheduled end) using the cached schedule and device time; the server MUST evaluate Late start and Early end from the punch time. (FR-EVV-01, BR-023)
- **SPEC-FR-010**: At offline clock-out the app MUST require a status for each task and a visit note where required, using the care plan version that was Active at the clock-in punch time. (FR-EVV-06, BR-012)
- **SPEC-FR-011**: The app MUST cache the caregiver's assigned visits for the next 72 hours with minimum necessary client data, and MUST hold at least 72 hours of punches offline. (NFR-AVL-02, NFR-PRIV-01)
- **SPEC-FR-012**: The app MUST show sync status at all times: number of queued items, time since last successful sync, a banner after 48 hours offline and a warning when free storage is below 100 MB. Messages state the problem and what to do. (FR-EVV-05, NFR-USE-03)
- **SPEC-FR-013**: When a visit changed on the server while punches waited on the device, the server MUST apply the conflict rules: a cancelled or reassigned visit yields a new visit with UNSCHEDULED_VISIT for the caregiver who delivered care; a Missed visit with punches captured inside the clock-in window returns to In progress or Completed. (FR-EVV-07, BR-019, BR-026)
- **SPEC-FR-014**: For tenants that require identity verification, a punch captured offline MUST be accepted without an identity check and MUST raise IDENTITY_CHECK_FAILED with the note "Not performed: device offline". Selfie images MUST NOT be stored on the device. (FR-EVV-04, BR-024)
- **SPEC-FR-015**: A device clock-out for an auto-closed visit MUST supersede the System placeholder punch while the AUTO_CLOSED exception stays open; a device punch arriving after a Coordinator's Manual correction MUST be stored and shown without overriding it. (BR-027, BR-026)
- **SPEC-FR-016**: When a synced punch changes pay for a visit in a locked pay period, the system MUST create an adjustment line in the next open period referencing the original visit. (BR-046, FR-PAY-06)
- **SPEC-FR-017**: When the estimated true capture time differs from the device capture time by more than 5 minutes, the server MUST show "Device clock differs by N min" in the visit history and exception queue, and MUST NOT alter the punch time. (BR-025)
- **SPEC-FR-018**: The app MUST NOT discard unsynced items on sign-out, and on caregiver deactivation MUST upload the outbox once under a sync-only scope before wiping local data and the key. (NFR-MOB-02, FR-WRK-06)
- **SPEC-FR-019**: Every accepted punch and every conflict outcome MUST create an audit event with actor, action, entity and timestamp. (BR-057, FR-RPT-03)
- **SPEC-FR-020**: Sync logs, metrics, crash reports and push payloads MUST NOT contain PHI. (BR-056, NFR-OBS-01)

### Key Entities

| Entity | Where | What it represents | Key attributes |
|---|---|---|---|
| Outbox command | Device only | One captured action awaiting sync | Punch or command ID, type, visit ID, payload, device capture time with offset, monotonic time, boot ID, server offset, sequence, local status (Queued, Sent, Accepted, Duplicate, Rejected) |
| Cached visit | Device only | An assigned visit available offline for the next 72 hours | Visit ID, scheduled start and end, client first name and last initial, client number, service address, geofence radius, care plan version and tasks |
| Sync state | Device only | The device's view of the last successful exchange | Last sync time, last server offset, queued count |
| EVV punch | Server (`evv_punches`) | An immutable clock-in or clock-out record | ID (client-generated punch ID), visit, type, source MobileOffline, punch time, receipt time, coordinates, accuracy, server-computed distance, device ID |
| Visit exception | Server (`visit_exceptions`) | A condition for Coordinator review | Codes used here: LATE_OFFLINE_SYNC, UNSCHEDULED_VISIT, IDENTITY_CHECK_FAILED, LOCATION_MISMATCH, LOW_GPS_ACCURACY, AUTO_CLOSED |
| Visit | Server (`visits`) | The scheduled service the punches belong to | Status (Scheduled, In progress, Completed, Needs review, Verified, Cancelled, Missed), caregiver, care plan version |

---

## Clarifications

The first `/specify` draft contained 13 `[NEEDS CLARIFICATION]` markers. The Business Analyst removed 2 that the sources answered outright (listed at the end of this section), kept 11 as C-01 to C-10 and C-12, and added C-11 in version 1.3. Each was resolved with the role that owns the decision.

### Session 2026-04-09 (Product Owner, Engineering Lead, Clinical SME, Business Analyst)

| ID | Marker in the draft | Decision | Decided by | Affects |
|---|---|---|---|---|
| C-01 | [NEEDS CLARIFICATION: what happens after 72 hours offline?] | 72 hours is the guaranteed capacity, designed for 30 visits. Capture continues beyond it while storage allows; banner after 48 hours; storage warning below 100 MB free. Care is never blocked | Product Owner, Engineering Lead | SPEC-FR-011, SPEC-FR-012 |
| C-02 | [NEEDS CLARIFICATION: which time is the official punch time?] | Confirmed from BR-025 and NFR-DAT-01: device capture time is the punch time; receipt time is stored separately; both in UTC | Business Analyst, confirmed by Compliance and Privacy Officer | SPEC-FR-004 |
| C-04 | [NEEDS CLARIFICATION: should the device check the geofence offline to warn the caregiver?] | No. Distance is computed only on the server (BR-021). The app shows no geofence verdict, online or offline | Engineering Lead, Business Analyst | SPEC-FR-007 |
| C-06 | [NEEDS CLARIFICATION: are care-plan tasks and the note available offline?] | Yes. The cache holds the Active care-plan tasks for cached visits. The visit uses the version Active at the clock-in punch time; FR-EVV-06 applies offline | Clinical SME | SPEC-FR-010, SPEC-FR-011 |

### Session 2026-04-14 (Product Owner, Compliance and Privacy Officer, Engineering Lead, Clinical SME, pilot Billing and Payroll Specialist, Business Analyst)

| ID | Marker in the draft | Decision | Decided by | Affects |
|---|---|---|---|---|
| C-03 | [NEEDS CLARIFICATION: how do we handle a device clock that is wrong or changed?] | The server estimates true capture time from monotonic time, boot ID and last server offset. A difference over 5 minutes shows an indicator to the Coordinator; the punch time is never altered. Promotion to an exception is an R2 candidate | Product Owner, Engineering Lead, Compliance and Privacy Officer | SPEC-FR-003, SPEC-FR-017 |
| C-05 | [NEEDS CLARIFICATION: how does the identity check work offline?] | Not available offline. The punch is accepted and raises IDENTITY_CHECK_FAILED with "Not performed: device offline", so airplane mode cannot be used to skip the check. Storing selfies on the device for later matching was rejected | Compliance and Privacy Officer, Product Owner | SPEC-FR-014 |
| C-08 | [NEEDS CLARIFICATION: what if a late punch lands in a locked pay period?] | Adjustment line in the next open period, referencing the original visit (BR-046) | Product Owner, pilot Billing and Payroll Specialist | SPEC-FR-016 |
| C-09 | [NEEDS CLARIFICATION: what happens to unsynced punches when a caregiver is deactivated?] | One final upload under a sync-only scope, then wipe. If the device never reconnects, the Coordinator records Manual punches with reason codes | Compliance and Privacy Officer, Engineering Lead | SPEC-FR-018 |
| C-10 | [NEEDS CLARIFICATION: can a caregiver sign out with unsynced punches?] | Sign-out warns and keeps the caregiver signed in; the outbox is never cleared by sign-out | Product Owner, UX Designer | SPEC-FR-018 |
| C-12 | [NEEDS CLARIFICATION: are dose outcomes in scope?] | Out of scope for this spec; the outbox is shared. An outcome captured on time but synced late is not labelled Late entry, and any Missed - undocumented history stays visible (BR-031). Rules owned by US-032 and US-033 | Clinical SME, Product Owner | Scope |

### Session 2026-06-12 (UAT, pilot Care Coordinators, Product Owner, Business Analyst)

| ID | Marker | Decision | Decided by | Affects |
|---|---|---|---|---|
| C-07 | [NEEDS CLARIFICATION: what if the visit was cancelled, reassigned or marked Missed while the caregiver was offline?] | Conflict rules as in ADR-006 v1.1: cancelled or reassigned visits yield a new visit with UNSCHEDULED_VISIT; Missed visits with in-window punches are reopened. Originally "reject and ask the caregiver to call", changed in UAT because Coordinators preferred never to lose evidence of care delivered | Product Owner, pilot Care Coordinators | SPEC-FR-013 |

### Update 2026-09-24 (SRS v1.3 alignment)

| ID | Question | Decision | Decided by | Affects |
|---|---|---|---|---|
| C-11 | What if the device has no GPS fix at all? | Treated like coordinates (0,0) under BR-022: the punch is stored without coordinates and LOW_GPS_ACCURACY is raised with "No location fix". Before SRS v1.3 this raised LOCATION_MISMATCH with a note | Business Analyst, Compliance and Privacy Officer | SPEC-FR-003, SPEC-FR-007 |

Removed markers (answered by sources): the batch size question (answered by ADR-006: 50 punches) and the encryption question (answered by NFR-MOB-02 and ADR-006: SQLCipher with a hardware-backed key).

---

## Review & Acceptance Checklist

### Content Quality

- [x] No implementation details in requirements (languages, frameworks, APIs are in plan.md)
- [x] Focused on caregiver and agency value and on compliance needs
- [x] Written for non-technical stakeholders (reviewed by pilot Care Coordinators in UAT)
- [x] All mandatory sections completed

### Requirement Completeness

- [x] No `[NEEDS CLARIFICATION]` markers remain open (C-01 to C-12 resolved)
- [x] Requirements are testable and unambiguous; each maps to a canonical FR, BR or NFR
- [x] Success criteria are measurable: 72-hour capacity, 24-hour late sync threshold, 5-minute skew indicator, 50-punch batches
- [x] Scope is clearly bounded (offline dose, vitals and incident rules excluded)
- [x] Dependencies and assumptions identified (ADR-002, ADR-004, ADR-006; US-025, US-028)

### Business Analyst sign-off checks

- [x] Every SPEC-FR traces to an existing canonical ID; no new FR, BR or US IDs created
- [x] Acceptance scenarios 1 to 6 match US-027-AC1 to US-027-AC6 in substance
- [x] Clinical SME confirmed scenario 7 and C-06, C-12
- [x] Compliance and Privacy Officer confirmed C-03, C-05, C-09 and SPEC-FR-020
- [x] AI-drafted content reviewed line by line; corrections recorded in the [AI-assisted BA README](../../README.md)

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

## Related documents

- [Implementation plan](plan.md)
- [Tasks](tasks.md)
- [AI-assisted BA README](../../README.md)
- [EP-06 EVV user stories (US-027)](../../../05-delivery/user-stories/EP-06-evv.md)
- [ADR-006 Offline-first caregiver app](../../../03-design/architecture/adr/ADR-006-offline-first-caregiver-app.md)
- [ADR-004 Identity verification vendor adapter](../../../03-design/architecture/adr/ADR-004-identity-verification-vendor-adapter.md)
- [ADR-002 Append-only EVV punch ledger](../../../03-design/architecture/adr/ADR-002-append-only-evv-punch-ledger.md)
- [Software requirements specification](../../../02-requirements/SRS.md)
- [Non-functional requirements](../../../02-requirements/non-functional-requirements.md)
- [Discovery workshop notes](../../../01-discovery/discovery-workshop-notes.md)
