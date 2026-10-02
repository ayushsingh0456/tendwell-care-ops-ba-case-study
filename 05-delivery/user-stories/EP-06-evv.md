# EP-06 Electronic Visit Verification (EVV): user stories

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DEL-US-06 |
| Version | 1.3 |
| Status | Baselined |
| Owner | Business Analyst |
| Last updated | 2026-09-24 |
| Reviewers | Product Owner, Engineering Lead, QA Lead, UX Designer, Compliance and Privacy Officer |

## Purpose and scope

This file holds the user stories and acceptance criteria for EP-06. It covers clock-in and clock-out, geofence and GPS-accuracy checks, optional identity verification, offline capture, task completion at clock-out, the exception review queue, auto-close and visit verification. The capability is designed to support capture of the six EVV data elements in Section 12006 of the 21st Century Cures Act; the agency remains responsible for submitting EVV data to its state.

Version 1.3 aligns US-025 and US-029 with CR-004 (SRS v1.3, raised from INC-2026-011): Low GPS accuracy is a separate exception from Location mismatch, the app requests precise location, and Coordinators can bulk-resolve low-accuracy exceptions.

## Epic

| Field | Value |
|---|---|
| Epic ID | EP-06 |
| Name | Electronic Visit Verification (EVV) |
| Module | EVV |
| Goal | Capture all six EVV data elements for every visit with minimal caregiver effort, flag anomalies without ever blocking care, and turn clean visits into Verified visits that payroll and billing can trust. |
| Objectives | OBJ-01 EVV completeness (81% to 97% or more); OBJ-02 Payroll preparation time (fewer manual timesheet fixes); OBJ-04 Days to invoice (Verified visits bill without rework). |
| Business need | BN-06 |
| Release | R1 |

## Story list

| Story | Title | Persona | Priority | Points | Sprint |
|---|---|---|---|---|---|
| US-025 | Clock in at the client's home | PER-01 Rosa Delgado (CG) | Must | 8 | S3 |
| US-026 | Confirm my identity with a selfie check | PER-01 Rosa Delgado (CG) | Should | 5 | S4 |
| US-027 | Clock in and out without signal | PER-01 Rosa Delgado (CG) | Must | 8 | S4 |
| US-028 | Clock out with tasks and note | PER-01 Rosa Delgado (CG) | Must | 5 | S3 |
| US-029 | Resolve EVV exceptions with reason codes | PER-02 Marcus Hale (AG-COORD) | Must | 8 | S4 |
| US-030 | Auto-close visits left open | System (SYS) | Must | 3 | S5 |
| **Total** | | | | **37** | |

Shared test data: client C-10234 at 418 Birchwood Lane, Lakemont, OH 43999, geofence radius 150 m; visit for Rosa Delgado scheduled 08:00 to 10:00 America/New_York under T1019; care plan version 3 with tasks "Bathing assistance", "Mobility support" and "Meal preparation", "Requires visit note" = Yes.

## Stories

### US-025 · Clock in at the client's home

| Field | Value |
|---|---|
| Epic | EP-06 Electronic Visit Verification (EVV) |
| Persona | PER-01 Rosa Delgado (CG) |
| Priority | Must |
| Estimate | 8 points |
| Sprint / Release | S3 / R1 |
| Requirements | FR-EVV-01, FR-EVV-02, FR-EVV-03 |
| Business rules | BR-020, BR-021, BR-022, BR-023 |
| Dependencies | US-020, US-012 |

**Story**
As a caregiver, I want to clock in to my visit with one tap when I arrive at the client's home, so that my time and location are recorded correctly without paperwork or calls to the office.

**Acceptance criteria**

```gherkin
Scenario: US-025-AC1 Clock in inside the geofence
  Given Rosa is assigned to the 08:00 to 10:00 visit for C-10234
  And her phone reports a location 40 m from the service address with 12 m accuracy
  When she opens the app at 07:52 and taps "Clock in" on the next-visit card
  Then a punch of type In and source Mobile is recorded with GPS coordinates, accuracy, device time, server receipt time and device ID
  And the server computes the distance as 40 m and raises no exception
  And the visit status becomes "In progress"
  And the clock-in takes no more than 3 taps from app open and completes within 2 s at p95

Scenario Outline: US-025-AC2 Clock-in window and Late start tolerance
  Given the visit is scheduled 08:00 to 10:00
  When Rosa tries to clock in at <time>
  Then the result is "<result>"

  Examples:
    | time  | result                                                                         |
    | 07:44 | Clock in is disabled with "Clock-in opens at 07:45"                            |
    | 07:45 | Clocked in, no exception                                                       |
    | 08:10 | Clocked in, no exception                                                       |
    | 08:11 | Clocked in, Late start exception raised                                        |
    | 10:00 | Clocked in, Late start exception raised                                        |
    | 10:01 | Clock in is unavailable with "This visit has ended. Contact your coordinator." |

Scenario Outline: US-025-AC3 Location and accuracy decide the exception, never the punch
  Given the client's geofence radius is <radius> m
  When Rosa clocks in with a fix <distance> m from the service address and <accuracy> accuracy
  Then the punch is recorded
  And the exception raised is "<exception>"

  Examples:
    | radius | distance | accuracy | exception         |
    | 150    | 212      | 18 m     | LOCATION_MISMATCH |
    | 150    | 95       | 3,400 m  | LOW_GPS_ACCURACY  |
    | 150    | 40       | 12 m     | none              |
    | 150    | 150      | 20 m     | none              |
    | 150    | 151      | 20 m     | LOCATION_MISMATCH |
    | 150    | 60       | 100 m    | none              |
    | 150    | 60       | 101 m    | LOW_GPS_ACCURACY  |
    | 150    | (0,0)    | 5 m      | LOW_GPS_ACCURACY  |
    | 300    | 212      | 18 m     | none              |

Scenario: US-025-AC4 The server ignores a device-declared distance
  Given Rosa's phone is 212 m from the service address
  When the clock-in request includes a field "distanceM" with the value 5
  Then the server ignores the field and computes 212 m from the coordinates
  And a LOCATION_MISMATCH exception is raised

Scenario: US-025-AC5 Cannot clock in to someone else's visit
  Given the 08:00 visit for C-10234 is assigned to Maya Ortiz
  When Rosa calls POST /v1/visits/{visitId}/clock-in for that visit
  Then the request returns 403 and no punch is recorded
  And Rosa's app offers "Start an unscheduled visit", which raises UNSCHEDULED_VISIT for Coordinator review

Scenario: US-025-AC6 Ask for precise location before clocking in
  Given Rosa's iPhone has Precise Location turned off for Tendwell
  When she taps "Clock in"
  Then the app explains why precise location is needed and offers to open Settings
  And if she continues without it and the fix is 95 m from the address with 3,400 m accuracy, the punch is recorded and LOW_GPS_ACCURACY is raised instead of LOCATION_MISMATCH
```

**Notes**
- Version history: AC3 rows for accuracy worse than 100 m and AC6 were revised by CR-004 (SRS v1.3) after INC-2026-011, when approximate iOS locations (about 3-5 km accuracy) produced 1,180 false Location mismatch exceptions in 3 days.
- QA device matrix must include iOS "Precise Location: Off" and Android "Approximate location" settings.
- Analytics: exception rate by code, app version and OS; NFR-OBS-02 alerts when the EVV exception rate exceeds 2x the 7-day baseline.
- UX: the next-visit card shows the client's first name and last initial, the time window and a single primary button; the address opens in the maps app.
- Out of scope: blocking a punch for location reasons. Exceptions are reviewed after the fact so that care is never delayed.

### US-026 · Confirm my identity with a selfie check

| Field | Value |
|---|---|
| Epic | EP-06 Electronic Visit Verification (EVV) |
| Persona | PER-01 Rosa Delgado (CG) |
| Priority | Should |
| Estimate | 5 points |
| Sprint / Release | S4 / R1 |
| Requirements | FR-EVV-04 |
| Business rules | BR-024 |
| Dependencies | US-025, DEP-02 |

**Story**
As a caregiver at an agency that requires identity verification, I want a quick selfie check at clock-in, so that the agency can show it was really me who delivered the visit.

**Acceptance criteria**

```gherkin
Scenario: US-026-AC1 Pass the identity check and clock in
  Given Harborview Home Care has identity verification turned on
  And Rosa enrolled her reference selfie with recorded consent
  When she taps "Clock in" and completes the selfie liveness check
  Then the server matches the selfie against her enrolled reference through the identity verification adapter
  And the check result is "Pass" with liveness passed and a match score
  And the In punch references the identity check ID
  And the identity check completes within 4 s at p95

Scenario Outline: US-026-AC2 A passed check is valid for 90 seconds
  Given Rosa passed an identity check at 07:55:00
  When the clock-in punch reaches the server at <time>
  Then the result is "<result>"

  Examples:
    | time     | result                                                       |
    | 07:56:29 | Clocked in using the check                                   |
    | 07:56:30 | Clocked in using the check                                   |
    | 07:56:31 | Rejected: "Your check expired. Take a new selfie."           |

Scenario: US-026-AC3 A check is used for one punch only
  Given Rosa's check was consumed by her clock-in at 07:56
  When the same check ID is sent with her clock-out or with a clock-in to another visit
  Then the punch is rejected with "Take a new selfie to continue."

Scenario: US-026-AC4 Failed checks never block care
  Given the liveness check or the face match fails
  When Rosa has failed 3 attempts
  Then the app lets her clock in without a passed check
  And the visit gets an IDENTITY_CHECK_FAILED exception for Coordinator review

Scenario: US-026-AC5 No selfie step when the tenant has not enabled it
  Given Cedar Lane Adult Day Center has identity verification turned off
  When a caregiver clocks in
  Then no selfie step is shown and no biometric data is captured

Scenario: US-026-AC6 Offline clock-in on an identity-enabled tenant
  Given Harborview has identity verification on and Rosa has no connectivity
  When she clocks in offline
  Then the punch is stored without an identity check
  And on sync the visit gets IDENTITY_CHECK_FAILED with the reason "Not performed (offline)"
```

**Notes**
- Identity verification is optional per tenant (DEC-07) and sits behind the `IdentityVerificationPort` adapter (ADR-004) so the vendor can be replaced.
- Privacy: the vendor deletes selfie images after the match under the BAA; Tendwell stores only the result, liveness flag, match score and timestamps. Biometric consent is captured at enrollment; the agency remains responsible for any state biometric privacy obligations.
- Delivery: carried over from S4 to S5 because the vendor's sandbox credentials arrived late (ISS-02, DEP-02).
- Out of scope: offline face matching on the device.

### US-027 · Clock in and out without signal

| Field | Value |
|---|---|
| Epic | EP-06 Electronic Visit Verification (EVV) |
| Persona | PER-01 Rosa Delgado (CG) |
| Priority | Must |
| Estimate | 8 points |
| Sprint / Release | S4 / R1 |
| Requirements | FR-EVV-05 |
| Business rules | BR-025 |
| Dependencies | US-025, US-028 |

**Story**
As a caregiver who often works in homes with no signal, I want to clock in and out offline and have my punches sync later, so that my visits count and I am paid without calling the office.

**Acceptance criteria**

```gherkin
Scenario: US-027-AC1 Clock in with no connectivity
  Given Rosa's phone has no network connection
  When she taps "Clock in" at 08:02 device time at the client's home
  Then the punch is stored in the encrypted on-device queue with GPS coordinates, accuracy, device time and device ID
  And the app shows "Saved on this phone. It will sync when you are back online."
  And the visit shows "In progress" in the app

Scenario: US-027-AC2 Sync keeps capture time and receipt time separately
  Given Rosa's offline clock-in was captured at 08:02 and her clock-out at 10:01
  When her phone reconnects at 11:40
  Then both punches are sent in one batch to POST /v1/evv/punches/sync
  And each punch keeps its device capture time as the punch time and 11:40 as the server receipt time
  And each punch has source "MobileOffline" and the server computes its distance
  And no LATE_OFFLINE_SYNC exception is raised

Scenario Outline: US-027-AC3 Flag punches synced more than 24 hours after capture
  Given a punch was captured offline on 2026-09-15 at 08:02
  When the server receives it at <received>
  Then LATE_OFFLINE_SYNC is <raised>

  Examples:
    | received          | raised     |
    | 2026-09-16 08:01  | not raised |
    | 2026-09-16 08:02  | not raised |
    | 2026-09-16 08:03  | raised     |

Scenario: US-027-AC4 Resending a batch never duplicates punches
  Given a sync batch was accepted but the response was lost
  When the app resends the same batch with the same punch IDs
  Then the server returns success and stores no duplicate punches

Scenario: US-027-AC5 Hold 72 hours of punches and protect them on sign-out
  Given Rosa worked 18 visits over 72 hours with no connectivity
  Then all 36 punches are kept on the device and sync in capture order when she reconnects
  And if she tries to sign out with unsynced punches, the app warns "You have 36 visits that have not synced. Stay signed in until you are online."

Scenario: US-027-AC6 Sync a visit that changed while offline
  Given the Coordinator reassigned the 08:00 visit to Maya while Rosa was offline and Rosa delivered it anyway
  When Rosa's punches sync
  Then her punches are kept and linked to an unscheduled visit for Rosa
  And UNSCHEDULED_VISIT is raised so the Coordinator can reconcile the two visits
```

**Notes**
- On-device storage uses SQLCipher with a key held in the iOS Keychain or Android Keystore (NFR-MOB-02); the queue is wiped remotely on deactivation (US-017).
- 72-hour offline capacity implements NFR-AVL-02; the spec in [08-ai-assisted-ba](../../08-ai-assisted-ba/specs/001-offline-evv-capture/spec.md) elaborates the edge cases.
- Device clock: the app records elapsed time since its last server time sync so that the server can detect device clocks set manually; mismatches over 5 minutes are logged for review in R1 and become an exception candidate for R2.
- Analytics: share of punches synced offline and median sync delay per tenant.

### US-028 · Clock out with tasks and note

| Field | Value |
|---|---|
| Epic | EP-06 Electronic Visit Verification (EVV) |
| Persona | PER-01 Rosa Delgado (CG) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S3 / R1 |
| Requirements | FR-EVV-06 |
| Business rules | BR-012 |
| Dependencies | US-014, US-025 |

**Story**
As a caregiver, I want to mark each care-plan task and write the visit note as I clock out, so that the agency has a complete record of the care I gave.

**Acceptance criteria**

```gherkin
Scenario: US-028-AC1 Clock out with every task recorded
  Given Rosa is clocked in to the 08:00 visit using care plan version 3
  When she marks "Bathing assistance" and "Mobility support" as Done and "Meal preparation" as Not done with reason "Client declined"
  And she submits the visit note and taps "Clock out" at 09:58
  Then a punch of type Out is recorded with GPS coordinates, accuracy, device time, server receipt time and device ID
  And the visit status becomes "Completed"

Scenario: US-028-AC2 Every task needs a status
  Given "Meal preparation" has no status
  When Rosa taps "Clock out"
  Then clock-out is not recorded
  And the app highlights "Meal preparation" with "Mark this task Done or Not done before clocking out."

Scenario Outline: US-028-AC3 Not done needs a reason
  When Rosa marks a task Not done with reason "<reason>" and note "<note>"
  Then the result is "<result>"

  Examples:
    | reason                 | note                         | result                                            |
    | Client declined        |                              | accepted                                          |
    | Supplies unavailable   |                              | accepted                                          |
    | Not enough time        |                              | accepted                                          |
    | Other                  | Client asleep, family asked  | accepted                                          |
    | Other                  |                              | rejected: add a note when the reason is Other     |
    | (none)                 |                              | rejected: select a reason                         |

Scenario Outline: US-028-AC4 Visit note required only when the care plan says so
  Given the care plan's "Requires visit note" is <setting>
  When Rosa clocks out without a note
  Then the result is "<result>"

  Examples:
    | setting | result                                                     |
    | Yes     | Blocked: "Write the visit note before clocking out."       |
    | No      | Clocked out                                                |

Scenario: US-028-AC5 Use the task list from the version Active at clock-in
  Given Rosa clocked in while care plan version 3 was Active
  When version 4 with an extra task is approved during her visit
  Then her clock-out screen shows the version 3 tasks only

Scenario Outline: US-028-AC6 Early end tolerance
  Given the visit is scheduled to end at 10:00
  When Rosa clocks out at <time>
  Then EARLY_END is <raised>

  Examples:
    | time  | raised     |
    | 09:49 | raised     |
    | 09:50 | not raised |
    | 10:20 | not raised |
```

**Notes**
- Clock-out works offline (US-027); task statuses and the note are queued with the punch.
- The visit note itself is specified in US-036; this story enforces its presence at clock-out.
- UX: tasks are listed in care-plan order with large Done and Not done buttons; the reason picker opens only for Not done.

### US-029 · Resolve EVV exceptions with reason codes

| Field | Value |
|---|---|
| Epic | EP-06 Electronic Visit Verification (EVV) |
| Persona | PER-02 Marcus Hale (AG-COORD) |
| Priority | Must |
| Estimate | 8 points |
| Sprint / Release | S4 / R1 |
| Requirements | FR-EVV-07, FR-EVV-08, FR-EVV-10 |
| Business rules | BR-026, BR-028 |
| Dependencies | US-025, US-028 |

**Story**
As a Care Coordinator, I want one queue of visit exceptions where I can correct times with a reason while the original punches stay visible, so that visits become Verified quickly and our records stand up to an audit.

**Acceptance criteria**

```gherkin
Scenario: US-029-AC1 Work the exception queue
  Given "Lakemont North" has 14 open exceptions
  When Marcus opens the exception queue
  Then exceptions are listed oldest first with visit, client, caregiver, exception code, punch times and computed distance
  And he can filter by exception code, caregiver, client and date range

Scenario: US-029-AC2 Correct a missing clock-out without changing the original punches
  Given Rosa's 08:00 visit has a clock-in at 07:58 and an open MISSING_CLOCK_OUT exception
  When Marcus adds a clock-out at 10:02 with reason code "Caregiver forgot to clock out" and note "Confirmed by phone with Rosa at 10:40"
  Then a new punch of source "Manual" is added with the reason code, note and Marcus as creator
  And the original clock-in punch is unchanged
  And the visit history shows both punches with their sources
  And the exception status is "Resolved"

Scenario Outline: US-029-AC3 A correction needs a reason code and a note
  When Marcus submits a time correction with reason code "<reason>" and note "<note>"
  Then the result is "<result>"

  Examples:
    | reason                          | note                              | result                                   |
    | Caregiver forgot to clock out   | Confirmed by phone with Rosa      | accepted                                 |
    | (none)                          | Confirmed by phone with Rosa      | rejected: select a reason code           |
    | Caregiver forgot to clock out   |                                   | rejected: add a note                     |

Scenario Outline: US-029-AC4 Verify a visit only when it is complete and clean
  Given a Completed visit with all six EVV data elements
  And its only exception is <exception state>
  Then the visit status is "<status>"

  Examples:
    | exception state                      | status       |
    | none                                 | Verified     |
    | LATE_START, Open                     | Needs review |
    | LATE_START, Resolved                 | Verified     |
    | LOCATION_MISMATCH, Waived with reason| Verified     |

Scenario: US-029-AC5 Bulk-resolve exceptions caused by low GPS accuracy
  Given 40 open exceptions raised from 2026-08-18 to 2026-08-20 whose punches report accuracy worse than 100 m
  And they are coded LOW_GPS_ACCURACY, or LOCATION_MISMATCH where they were raised before R1.1
  When Marcus selects them, chooses reason code "GPS accuracy issue confirmed" and enters one note
  Then each exception is resolved with that reason and note
  And each resolution is audited individually with Marcus as actor
  And an exception whose punch accuracy is 100 m or better cannot be included in the bulk action

Scenario: US-029-AC6 Only Verified visits reach payroll and billing
  Given Rosa has 10 Completed visits in the pay period, of which 9 are Verified and 1 is Needs review
  When the pay-period summary and the billing run are calculated
  Then both use only the 9 Verified visits
  And the Needs review visit is listed as excluded with its open exception
```

**Notes**
- Manual punches use `supersedes_punch_id` when they replace an earlier punch; nothing is updated or deleted (ADR-002).
- AC5 formalizes in R1.1 (CR-004) the bulk-resolve tool first shipped during the INC-2026-011 response. It is limited to punches with accuracy worse than 100 m so that genuine Location mismatch exceptions are still reviewed one by one.
- Analytics: median time from exception raised to resolved, and the share of visits with a Manual punch (an input to the EVV compliance report).
- Reason codes are provisioned per tenant (FR-ONB-04) and can be mapped to state aggregator codes in R2.

### US-030 · Auto-close visits left open

| Field | Value |
|---|---|
| Epic | EP-06 Electronic Visit Verification (EVV) |
| Persona | System (SYS) |
| Priority | Must |
| Estimate | 3 points |
| Sprint / Release | S5 / R1 |
| Requirements | FR-EVV-09 |
| Business rules | BR-027 |
| Dependencies | US-029 |

**Story**
As the visit lifecycle job, I want to close visits that were never clocked out and hold them from pay and billing, so that forgotten clock-outs do not inflate hours or invoices.

**Acceptance criteria**

```gherkin
Scenario Outline: US-030-AC1 Auto-close 14 hours after clock-in
  Given Rosa clocked in at 08:03 to a visit scheduled 08:00 to 10:00 and has not clocked out
  When the job runs at <time>
  Then the visit is <result>

  Examples:
    | time  | result                                                                                          |
    | 10:10 | still In progress with no MISSING_CLOCK_OUT exception                                           |
    | 10:11 | still In progress with an open MISSING_CLOCK_OUT exception                                      |
    | 22:02 | still In progress                                                                               |
    | 22:03 | auto-closed with a System clock-out at 10:00 (the scheduled end) and an open AUTO_CLOSED exception |

Scenario: US-030-AC2 Auto-closed visits are not paid or billed until resolved
  Given a visit was auto-closed and its AUTO_CLOSED exception is Open
  When the pay-period summary and the billing run are calculated
  Then the visit is excluded from both and listed as "Excluded: auto-closed"

Scenario: US-030-AC3 Resolve with the actual clock-out
  Given an auto-closed visit with a placeholder clock-out at 10:00
  When Marcus adds a Manual clock-out at 09:57 with reason code "Caregiver forgot to clock out" and a note
  Then the placeholder stays in the visit history and is superseded by the Manual punch
  And the AUTO_CLOSED exception is Resolved and the visit can be Verified

Scenario: US-030-AC4 A late offline clock-out does not resolve the exception by itself
  Given the visit was auto-closed at 22:03
  When Rosa's offline clock-out captured at 10:04 syncs at 23:30
  Then the real clock-out is added to the visit history
  And the AUTO_CLOSED exception stays Open for the Coordinator to confirm
  And LATE_OFFLINE_SYNC is not raised because the punch arrived 13 h 26 min after capture

Scenario: US-030-AC5 The job is single-flight
  Given two workers run the auto-close job at the same time
  Then each eligible visit is closed once and gets exactly one AUTO_CLOSED exception
```

**Notes**
- MISSING_CLOCK_OUT is raised once the scheduled end plus the 10-minute tolerance passes without a clock-out (UAT clarification agreed with the Product Owner on 2026-06-10).
- The job runs every 5 minutes, single-flight via `job_executions` (ADR-003).
- The placeholder clock-out is source "System" and is never treated as caregiver-attested time.

## Related documents

- [Epics overview](../epics.md)
- [Story map](../story-map.md)
- [Change request log](../change-request-log.md)
- [Software requirements specification](../../02-requirements/SRS.md)
- [Business rules catalog](../../02-requirements/business-rules.md)
- [Compliance mapping](../../02-requirements/compliance-mapping.md)
- [ADR-002 Append-only EVV punch ledger](../../03-design/architecture/adr/ADR-002-append-only-evv-punch-ledger.md)
- [ADR-004 Identity verification vendor adapter](../../03-design/architecture/adr/ADR-004-identity-verification-vendor-adapter.md)
- [ADR-006 Offline-first caregiver app](../../03-design/architecture/adr/ADR-006-offline-first-caregiver-app.md)
- [Sequence diagrams](../../03-design/diagrams/sequence-diagrams.md)
- [INC-2026-011 False Location mismatch exceptions](../../07-operations/incidents/INC-2026-011-false-location-mismatch-exceptions.md)
- [Offline EVV capture spec](../../08-ai-assisted-ba/specs/001-offline-evv-capture/spec.md)
- [Test cases](../../06-quality/test-cases.md)
