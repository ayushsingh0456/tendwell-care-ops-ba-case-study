# Test cases

## Document control

| Field | Value |
|---|---|
| Document ID | TW-QA-02 |
| Version | 1.4 |
| Status | Baselined |
| Owner | Business Analyst (co-authored with the QA Lead) |
| Last updated | 2026-09-28 |
| Reviewers | QA Lead, Engineering Lead, Product Owner, Clinical SME (RN advisor), Compliance and Privacy Officer |

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-05-22 | R1 system test cases for SIT |
| 1.1 | 2026-06-12 | Boundary rows from requirement-gap defects (DEF-012, DEF-022, DEF-025, DEF-050, DEF-052); SRS v1.2 |
| 1.2 | 2026-06-26 | Last Result updated from the R1 final regression |
| 1.3 | 2026-08-28 | Device-matrix and accuracy cases after INC-2026-011 |
| 1.4 | 2026-09-28 | TC-EVV-004 (CR-004), TC-BIL-007 (CR-005), TC-NTF-003 (CR-006); Last Result from the R1.1 regression cycle |

## Purpose and scope

[test-cases.csv](test-cases.csv) is the test case specification for Tendwell R1 and R1.1: 118 cases that cover every functional requirement and business rule in the [SRS](../02-requirements/SRS.md), plus 19 non-functional cases. This guide explains how to read the file, summarizes coverage, and writes out 15 cases in full. These are the cases where the arithmetic or the timing is the point, and where a reviewer should be able to check the expected result by hand.

## How to read the CSV

| Column | Meaning |
|---|---|
| TC ID | `TC-<MOD>-NNN`; MOD is the FR module code (ONB, IAM, CLI, WRK, SCH, EVV, MAR, DOC, TOF, PAY, BIL, NTF, RPT, FAM) or NFR |
| Title | What the case proves. "(DEF-nnn regression)" marks a case extended after that defect; "(CR-00n)" or an INC ID marks a case added or changed for a change request or incident |
| Module, Type | Type is one of Functional, Negative, Boundary, Integration, Security, Performance, Accessibility, Usability |
| Technique | Design technique (see the [test strategy](test-strategy-and-plan.md#4-test-design-techniques)) |
| Priority | P1 runs in every release and blocks release on failure; P2 runs in every release; P3 runs in full regression only |
| Preconditions | State before step 1, including the virtual-clock time where it matters |
| Test Data | `file: record IDs` from [test-data](test-data/README.md); `api-fixtures.json: section.key` for request bodies; "Postman: folder" when the case is automated in the collection |
| Steps | Numbered, one per line |
| Expected Result | Numbered to match the steps where steps have different outcomes |
| Requirement IDs, Business Rule IDs | FR and NFR IDs; BR IDs. All IDs come from the SRS and business rules |
| User Story IDs | Stories whose requirements the case covers |
| Automation | Automated (runs in CI or nightly), Manual, or Candidate (automation planned) |
| Last Result | Result in the R1.1 regression cycle, 2026-09-28 to 2026-10-02, build v1.1.0-rc.2 |

Conventions:

- Times are America/New_York, 24-hour. A case that needs a specific "now" says so in Preconditions; the tester sets the tenant's virtual clock (non-production only).
- Money is shown in USD in the CSV; the API carries integer cents.
- Records are referenced by readable key (C-10234, VIS-0201). The API uses the deterministic UUIDs described in the test data README.
- Fail, Blocked and Not run results are linked to a defect or a reason: TC-SCH-007 (DEF-061), TC-MAR-009 (DEF-055) and TC-NFR-010 (DEF-059) fail on known S3/S4 issues; TC-EVV-006 is blocked by the identity vendor sandbox; TC-FAM-001 and TC-FAM-002 are R2; TC-NFR-015 waits for the quarterly restore.

## Coverage summary

| Module | Cases | Functional | Negative | Boundary | Integration | Security | Performance | Accessibility | Usability | P1 | Automated | Requirements covered |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ONB | 6 | 3 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 4 | 6 | 8 of 8 FRs |
| IAM | 8 | 1 | 0 | 2 | 0 | 5 | 0 | 0 | 0 | 6 | 7 | 8 of 8 |
| CLI | 8 | 6 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 7 | 8 | 8 of 8 |
| WRK | 6 | 2 | 0 | 3 | 0 | 1 | 0 | 0 | 0 | 4 | 5 | 6 of 6 |
| SCH | 8 | 6 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 4 | 7 | 7 of 7 |
| EVV | 12 | 4 | 1 | 5 | 0 | 2 | 0 | 0 | 0 | 9 | 10 | 10 of 10 |
| MAR | 9 | 4 | 2 | 3 | 0 | 0 | 0 | 0 | 0 | 7 | 8 | 9 of 9 |
| DOC | 4 | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 2 | 3 | 6 of 6 |
| TOF | 4 | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 5 of 5 |
| PAY | 11 | 9 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 9 | 11 | 6 of 6 |
| BIL | 12 | 7 | 0 | 3 | 2 | 0 | 0 | 0 | 0 | 8 | 12 | 8 of 8 |
| NTF | 5 | 2 | 0 | 1 | 0 | 2 | 0 | 0 | 0 | 4 | 5 | 5 of 5 |
| RPT | 4 | 3 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 3 | 4 of 4 |
| FAM (R2) | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 of 3 (drafted, not run) |
| NFR | 19 | 3 | 0 | 1 | 5 | 3 | 4 | 1 | 2 | 14 | 10 | 25 NFRs |
| **Total** | **118** | **56** | **5** | **28** | **7** | **15** | **4** | **1** | **2** | **79** | **99** | |

| Coverage measure | Result |
|---|---|
| Functional requirements with at least one case | 93 of 93 (FR-FAM-01 to FR-FAM-03 by R2 drafts) |
| Business rules with at least one case | 58 of 58 |
| Business rules with at least one automated case (NFR-MNT-01) | 58 of 58 |
| User stories linked to at least one case | 54 of 54 |
| Non-functional requirements covered by a case | 27 of 29. NFR-MNT-01 is verified by the CI coverage gate; NFR-CMP-01 by the Compliance and Privacy Officer's BAA register review |
| Last Result | Pass 111, Fail 3, Blocked 1, Not run 3 |

The coverage numbers are produced by the generator that writes the CSV. The generator stops if any FR or BR ID is missing, if a case cites an ID that is not in the requirements, or if a cited test-data record does not exist.

## Featured test cases

Each featured case shows its inputs, the expected result at every boundary, and the arithmetic behind it.

### 1. TC-EVV-003 and TC-EVV-004: geofence and GPS accuracy boundaries

| Field | Value |
|---|---|
| Requirements | FR-EVV-02, FR-EVV-03, FR-EVV-07 |
| Business rules | BR-021 (radius 150 m default, 50-500 m, distance computed on the server), BR-022 (accuracy worse than 100 m, or (0,0), raises LOW_GPS_ACCURACY instead of Location mismatch) |
| Stories | US-025 (AC3, AC4, AC6) |
| Data | VIS-0205 (C-10262, radius 150 m), VIS-0206 (C-10295, radius 50 m); coordinates in `api-fixtures.json` `evv.geofenceBva`, `evv.accuracyBva`, `evv.geofence50mBva`, `evv.zeroCoordinates` |
| Technique | BVA, then a decision table for the two conditions together |

The fixture coordinates are placed so that the server's haversine distance (mean Earth radius 6,371,008.8 m) is exactly the target at 0.1 m. Reset the visit to Scheduled between iterations.

**Distance (accuracy held at 20 m):**

| Radius | Distance | Expected | Why |
|---|---|---|---|
| 150 m | 149.0 m | No exception | Inside |
| 150 m | 150.0 m | No exception | Mismatch only when distance is greater than the radius |
| 150 m | 151.0 m | LOCATION_MISMATCH, punch accepted (201) | Outside; the punch is never blocked |
| 50 m | 49.0 m | No exception | |
| 50 m | 50.0 m | No exception | |
| 50 m | 51.0 m | LOCATION_MISMATCH | |

**Accuracy (distance held at 151.0 m, outside the 150 m radius):**

| Accuracy | Expected | Why |
|---|---|---|
| 99 m | LOCATION_MISMATCH | Accurate fix outside the fence |
| 100 m | LOCATION_MISMATCH | 100 m is not "worse than 100 m" |
| 101 m | LOW_GPS_ACCURACY only | The fix cannot prove the caregiver was elsewhere |
| 5 m at (0,0) | LOW_GPS_ACCURACY only | Null-island coordinates are a device fault |
| 3,400 m at 95.0 m (canonical, iOS Precise Location Off) | LOW_GPS_ACCURACY only | INC-2026-011 regression (CR-004) |

Also checked: a request carrying `"distanceM": 5` is ignored, and the server returns the computed distance (TC-EVV-002).

### 2. TC-EVV-001: clock-in window

| Field | Value |
|---|---|
| Requirements | FR-EVV-01, FR-EVV-07 |
| Business rule | BR-023: clock-in opens 15 min before the scheduled start; Late start and Early end are raised beyond a 10-minute tolerance |
| Story | US-025 (AC2) |
| Data | VIS-0204: C-10278, E-2017, scheduled 2026-09-16 13:00-15:00; caregiver 20 m from the address with 8 m accuracy |
| Technique | BVA with the virtual clock; one iteration per row, visit reset between iterations |

| Attempt | Offset from start | Expected |
|---|---|---|
| 12:44:00 | -16 min | Disabled: "Clock-in opens at 12:45" |
| 12:44:30 | -15 min 30 s | Disabled (DEF-004: the window compares full timestamps, not minutes) |
| 12:45:00 | -15 min | Clocked in, no exception |
| 13:00:00 | +0 min | Clocked in, no exception |
| 13:10:00 | +10 min | Clocked in, no exception (within tolerance) |
| 13:11:00 | +11 min | Clocked in, LATE_START |
| 15:00:00 | scheduled end | Clocked in, LATE_START |
| 15:01:00 | end + 1 min | "This visit has ended. Contact your coordinator." |

### 3. TC-BIL-002: 15-minute units at the 7 and 8-minute remainder

| Field | Value |
|---|---|
| Requirement | FR-BIL-02 |
| Business rule | BR-047: units = floor(minutes / 15), plus 1 if the remainder is 8 minutes or more |
| Story | US-045 |
| Technique | BVA on the remainder |

| Verified duration | floor(min / 15) | Remainder | Units |
|---|---|---|---|
| 7 min | 0 | 7 | 0 |
| 8 min | 0 | 8 | 1 |
| 112 min | 7 | 7 | 7 |
| 113 min (canonical visit B) | 7 | 8 | 8 |
| 120 min (visit C) | 8 | 0 | 8 |
| 127 min (visit A) | 8 | 7 | 8 |
| 128 min | 8 | 8 | 9 |
| 112 min 50 s | 7 | 7 | 7 (seconds are truncated before rounding; SRS v1.2 clarification after DEF-012) |

### 4. TC-PAY-003: the E-2041 payroll calculation

| Field | Value |
|---|---|
| Requirements | FR-PAY-02, FR-PAY-03 |
| Business rules | BR-028, BR-041, BR-042, BR-043, BR-044, BR-045 |
| Story | US-041 |
| Data | E-2041 Maya Ortiz, Hourly $19.50, OT-, holiday- and mileage-eligible (PPR-0001); VIS-0001 to VIS-0013; `distance_matrix_stub.csv`; oracle `expected_payroll_E-2041_2026-09-07.csv` |
| Technique | Oracle comparison (automated in the Postman Payroll folder) |

Workweek Monday 2026-09-07 to Sunday 2026-09-13; Monday is Labor Day (H-001). Hours worked accumulate in time order, visits and paid travel together:

| Day | Verified visit time | Paid travel | Hours worked that day | Cumulative |
|---|---|---|---|---|
| Mon 09-07 (holiday) | 6 h 00 min | 0 | 6 h 00 min | 6.00 h |
| Tue 09-08 | 6 h 00 min (127 + 233 min) | 28 min | 6 h 28 min | 12.47 h |
| Wed 09-09 | 6 h 00 min | 30 min | 6 h 30 min | 18.97 h |
| Thu 09-10 | 6 h 00 min (113 + 120 + 127 min) | 50 min | 6 h 50 min | 25.80 h |
| Fri 09-11 | 6 h 00 min | 25 min | 6 h 25 min | 32.22 h |
| Sat 09-12 | 6 h 00 min | 17 min | 6 h 17 min | 38.50 h |
| Sun 09-13 | 4 h 30 min (08:00-12:30) | 0 | 4 h 30 min | 43.00 h |

40.00 h is reached at 09:30 on Sunday, so the last 3.0 h (09:30-12:30) are overtime. Paid travel per leg is min(gap, drive + 10 min) with every gap at 33 minutes or less: 28 + 30 + 25 + 25 + 25 + 17 = 150 min.

| Line | Hours | Rate | Amount | Derivation |
|---|---|---|---|---|
| Holiday | 6.00 | $29.25 | $175.50 | Monday visit time at 1.5 x $19.50 |
| Regular | 31.50 | $19.50 | $614.25 | 40.5 visit h - 6.0 holiday - 3.0 overtime |
| Travel | 2.50 | $19.50 | $48.75 | 150 min, all before 40 h |
| Overtime | 3.00 | $29.25 | $87.75 | Sunday 09:30-12:30 at 1.5x |
| **Total wages** | 43.00 | | **$926.25** | |
| Mileage (reimbursement) | 46.2 mi | $0.70 | $32.34 | 8.4 + 9.6 + 8.4 + 6.8 + 9.6 + 3.4 |
| **Total payable** | | | **$958.59** | |

Expected API values: `wagesCents` 92625, `reimbursementCents` 3234, `payableCents` 95859.

### 5. TC-PAY-004: overtime and holiday do not stack

| Field | Value |
|---|---|
| Requirements | FR-PAY-02, FR-TOF-05 |
| Business rules | BR-041, BR-042 (a minute that is both overtime and holiday is paid at the higher multiplier only) |
| Story | US-041 |
| Data | `api-fixtures.json` `engineCases.payrollRuleCases` PR-01 to PR-05; base rate $18.00 (1.5x = $27.00, 2.0x = $36.00) |
| Technique | Decision table (the premium-selection table added to business rules after DEF-019) |

| Case | Week | Holiday-eligible | OT-eligible | Daily profile | Expected lines | Wages |
|---|---|---|---|---|---|---|
| PR-01 | Mon 2026-09-07 (holiday) 8 h, Tue-Fri 8 h, Sat 2 h = 42 h | Yes | Yes | Off | Holiday 8.0, Regular 32.0, Overtime 2.0 | $846.00 |
| PR-02 | Mon-Thu 2026-12-21 to 12-24 8.5 h, Fri 12-25 (holiday) 8 h = 42 h | Yes | Yes | Off | Regular 34.0, Holiday 6.0, Overtime 2.0 at $27.00 | **$828.00** |
| PR-03 | Same as PR-02 | No | Yes | Off | Regular 40.0, Overtime 2.0 | $774.00 |
| PR-04 | Same as PR-02 | Yes | No | Off | Regular 34.0, Holiday 8.0 | $828.00 |
| PR-05 | Mon-Wed 2026-11-23 to 11-25 6 h; Thu 11-26 (Thanksgiving) 13 h = 31 h | Yes | Yes | On | Regular 18.0, Holiday 8.0, Overtime 4.0, DoubleTime 1.0 | $684.00 |

PR-02 is the regression for DEF-019. The last 2.0 h of Friday are both holiday and overtime: they are paid once at 1.5x and reported on the Overtime line (tie rule). The defective engine paid them at 1.5 x 1.5 = 2.25x ($40.50 per hour), giving $855.00. In PR-05, hours 8 to 12 of the holiday tie at 1.5x (reported as Overtime) and hour 13 takes the higher 2.0x (DoubleTime).

### 6. TC-PAY-005: daily overtime profile at 8 and 12 hours

| Field | Value |
|---|---|
| Requirement | FR-PAY-02 |
| Business rule | BR-041: optional daily profile, over 8 h per day at 1.5x and over 12 h at 2.0x (CR-001) |
| Story | US-041 |
| Data | PR-06, PR-07, PR-08a to PR-08d; tenant TEN-T01 with the daily profile On; rate $18.00 |
| Technique | BVA on daily hours |

| Hours in one day | Regular | Overtime 1.5x | DoubleTime 2.0x | Amount |
|---|---|---|---|---|
| 8 h 00 min | 8.00 | 0 | 0 | $144.00 |
| 8 h 01 min | 8.00 | 1 min | 0 | $144.45 |
| 12 h 00 min | 8.00 | 4.00 | 0 | $252.00 |
| 12 h 01 min | 8.00 | 4.00 | 1 min | $252.60 |

Week interaction (regression for DEF-025): Monday to Thursday 10 h each plus Friday 4 h = 44 h.

| Profile | Regular | Overtime | Wages |
|---|---|---|---|
| Daily On (PR-06) | 36.0 | 8.0 (2 h per 10-hour day) | $864.00 |
| Weekly only (PR-07) | 40.0 | 4.0 | $828.00 |

With the daily profile, hours already paid as daily overtime do not count toward the weekly 40 h. The defective engine counted them, paid another 4.0 h of weekly overtime on Friday, and produced $900.00.

### 7. TC-PAY-006: paid travel at the 2-hour boundary

| Field | Value |
|---|---|
| Requirement | FR-PAY-02 |
| Business rule | BR-043: paid travel = min(actual gap, estimated drive time + 10 min), only when the gap is 2 h or less |
| Story | US-041 |
| Data | `engineCases.travelCases` TR-20 to TR-121; estimated drive 25 min (cap 35 min); rate $18.00 |
| Technique | BVA on the gap |

| Case | Gap between visits | min(gap, 25 + 10) | Paid | Amount |
|---|---|---|---|---|
| TR-20 | 20 min | 20 | 20 min | $6.00 |
| TR-35 | 35 min | 35 | 35 min | $10.50 |
| TR-119 | 119 min | 35 | 35 min | $10.50 |
| TR-120 | 120 min | 35 | 35 min | $10.50 |
| TR-121 | 121 min | n/a | 0 (off duty) | $0.00 |

### 8. TC-MAR-004: missed-dose timeline with a controlled clock

| Field | Value |
|---|---|
| Requirements | FR-MAR-04, FR-NTF-02, FR-NTF-03 |
| Business rules | BR-030 (reminder, Overdue, Missed - undocumented), BR-031 (late entry up to 24 h; never deleted), BR-053 (urgent events bypass quiet hours) |
| Story | US-033 |
| Data | DT-0004: metformin (MO-0001) for C-30015 at 2026-09-15 20:00, window +/-60 min (19:00-21:00); E-3108 on VIS-3014; U-3003 Coordinator; U-3002 Clinical Supervisor |
| Technique | State transition with the TEN-003 virtual clock |

| Virtual clock | Dose status | Notification | Note |
|---|---|---|---|
| 19:59:59 | Due | None | |
| 20:00:00 | Due | Reminder to E-3108 | Scheduled time |
| 20:59:59 | Due | None | Window still open |
| 21:00:00 | Overdue | Alert to E-3108 and U-3003, sent at once | Quiet hours have started; dose alerts are urgent (SRS v1.2 after DEF-052) |
| 21:59:59 | Overdue | None | |
| 22:00:00 | Missed - undocumented | Urgent alert to U-3002 | 60 min after the window closed |
| 2026-09-16 19:59:59 | Given recorded (administered 20:10 the day before) | Escalation closed | Labelled Late entry |
| 2026-09-16 20:00:01 (fresh seed) | Missed - undocumented | | 422 MAR_LATE_ENTRY_WINDOW_EXPIRED; only U-3002 can annotate |

Alternate path: documenting the dose at 21:30 records it as a Late entry and stops the escalation, so no supervisor alert is sent at 22:00. TC-MAR-005 confirms that no midnight job ever cancels or deletes the dose (CR-007 was rejected).

### 9. TC-MAR-007: PRN maximum per 24 hours and minimum interval

| Field | Value |
|---|---|
| Requirement | FR-MAR-05 |
| Business rule | BR-033: blocked if it would exceed the maximum in any rolling 24 hours, or fall inside the minimum interval |
| Story | US-034 |
| Data | MO-0003 acetaminophen 500 mg PRN, max 4 per 24 h, minimum interval 240 min; seeded doses PRN-0001 (2026-09-14 22:00), PRN-0002 (2026-09-15 02:00), PRN-0003 (06:00) |
| Technique | BVA on both limits with the virtual clock |

The rolling window is the 24 hours before the new dose, excluding a dose given exactly 24 hours earlier: (t - 24 h, t]. This was clarified in SRS v1.2 after DEF-022.

| Attempt (2026-09-15) | Doses in window before this one | Minutes since last dose | Expected |
|---|---|---|---|
| 09:59 | 3 | 239 | 422 MAR_PRN_MIN_INTERVAL_NOT_MET; next allowed 10:00 |
| 10:00 | 3 | 240 | 201; 4th dose recorded |
| 14:00 | 4 (22:00, 02:00, 06:00, 10:00) | 240 | 422 MAR_PRN_MAX_DOSES_EXCEEDED; next allowed 22:00 |
| 21:59 | 4 | 719 | 422 MAR_PRN_MAX_DOSES_EXCEEDED |
| 22:00 | 3 (the 2026-09-14 22:00 dose is exactly 24 h old) | 720 | 201 |
| Any time, no indication | | | 422 MAR_PRN_INDICATION_REQUIRED |

The Postman eMAR folder checks the same rule on MO-0011 (maximum 3, already 3 in the window at 08:55): 422 with `nextAllowedAt` 2026-09-15T14:00:00-04:00.

### 10. TC-BIL-006 and TC-BIL-007: billing re-run idempotency

| Field | Value |
|---|---|
| Requirement | FR-BIL-01 (plus NFR-MNT-02, NFR-OBS-02 for TC-BIL-007) |
| Business rule | BR-050: idempotency key = tenant + client + payer + period; a re-run updates Drafts and never creates a second invoice for the same key |
| Story | US-044 |
| Data | TEN-001, period 2026-09-01 to 2026-09-30, seed `base`; Postman Billing folder |
| Technique | State transition (TC-BIL-006); concurrency and fault injection (TC-BIL-007, INC-2026-007 regression, CR-005) |

**TC-BIL-006**

| Step | Action | Expected |
|---|---|---|
| 1 | POST /billing-runs with Idempotency-Key K1 | 7 Draft invoices: C-10234 $174.00, C-10251 $348.00, C-10262 $285.60, C-10278 $261.00, C-10289 $174.00, C-10333 $29.00, C-10358 $190.00 (total $1,461.60) |
| 2 | Waive EXC-0001 so VIS-0101 becomes Verified; issue the C-10358 invoice | |
| 3 | POST /billing-runs for the same period with a new key K2 | Same 7 invoice IDs. C-10262 Draft updated from 42 to 50 units ($285.60 to $340.00: 8 more units at $6.80). C-10358 invoice unchanged; no second invoice for its key |
| 4 | Replay step 1 with K1 | The stored response of the first run; nothing re-executed |

**TC-BIL-007:** force two scheduler workers to take leadership and start the nightly run on both at the same instant, 50 times. Every iteration ends with exactly 7 invoices; the second insert hits the unique idempotency key and is reported as "already exists"; `job_executions` has one completed row per key. A forced duplicate Draft is stopped by the pre-issue duplicate check. A run injected to produce 9 invoices against the previous 7 (+28.6%) fires the NFR-OBS-02 anomaly alert.

### 11. TC-IAM-007: cross-tenant access is denied by row-level security

| Field | Value |
|---|---|
| Requirement | FR-IAM-06 |
| Business rule | BR-001: data is never readable across tenants; isolation is enforced in the database |
| Story | US-009 (AC4) |
| Data | C-10234 (TEN-001, UUID `c1000000-0000-4000-8000-000000010234`); `tenantBAccessToken` for U-2002 (TEN-002) |
| Technique | Negative testing at the API and in SQL |

| Step | Action | Expected |
|---|---|---|
| 1 | GET /clients/{C-10234} with the TEN-002 token | 404 problem+json; the body contains no name, Medicaid ID or address |
| 2 | GET /visits?clientId={C-10234} with the TEN-002 token | 200 with an empty `items` array |
| 3 | PATCH /clients/{C-10234}; POST /clients/{C-10234}/phi-reveals | 404 for both; nothing changed |
| 4 | SQL below as the application role; then insert a visit carrying TEN-001's `tenant_id` through the test helper | 0 rows selected and 0 updated; the insert fails the RLS WITH CHECK policy |
| 5 | `SET row_security = off` as the application role | Permission denied (the role does not have BYPASSRLS) |

```sql
SET ROLE tendwell_app;
SELECT set_config('app.tenant_id', '7e000000-0000-4000-8000-000000000002', false);  -- act as TEN-002
SELECT id FROM clients WHERE id = 'c1000000-0000-4000-8000-000000010234';            -- expect 0 rows
UPDATE clients SET primary_language = 'Spanish'
 WHERE id = 'c1000000-0000-4000-8000-000000010234';                                   -- expect UPDATE 0
```

The API returns 404, not 403, so a caller cannot learn that the record exists. TC-NFR-008 repeats step 4 for every table with a `tenant_id` column.

### 12. TC-NTF-003: a deactivated user never receives an escalation (INC-2026-015 regression)

| Field | Value |
|---|---|
| Requirements | FR-NTF-03, FR-NTF-05, NFR-OBS-02 |
| Business rules | BR-054 (recipients resolved at send time from active users holding the role in the location), BR-056 (no PHI in SMS, push or email) |
| Story | US-050 |
| Data | Ladder CLIENT_INCIDENT_REPORTED for TEN-001, configured while U-1005 Lena Marsh was an active AG-COORD in Lakemont North; U-1005 deactivated 2026-09-01; active Lakemont North coordinators U-1002 and U-1007; supervisor U-1003 |
| Technique | State transition (CR-006) |

| Step | Action | Expected |
|---|---|---|
| 1 | Raise a High incident for C-10234 | Step 1 goes to U-1003 |
| 2 | Advance past the step 2 delay (AG-COORD, Lakemont North) | Step 2 goes to U-1002 and U-1007 only |
| 3 | On a fresh run, deactivate U-1007 between step 1 and step 2 | Step 2 goes to U-1002 only |
| 4 | Query `notifications` and the anomaly metric | No row for U-1005 in any channel. The email body is generic ("A client incident needs your review. Sign in to Tendwell to view it.") with a deep link that requires sign-in. `notifications_to_deactivated_users` = 0 |

Before CR-006 the ladder cached recipients when it was configured, so step 2 would have gone to U-1005.

### 13. TC-NFR-011: overnight visits across DST

| Field | Value |
|---|---|
| Requirements | NFR-DAT-01, FR-EVV-02, FR-PAY-02 |
| Business rule | BR-045 (time held to the second; overlapping time merged) |
| Data | VIS-3001 and VIS-3002 (C-30012, E-3108 at $17.50); TEN-003 in America/New_York; pay periods PP-T3-2026-10-16 and PP-T3-2026-11-01 |
| Technique | BVA around the DST transitions with the virtual clock |

| Visit | Local start and end | Stored UTC | Elapsed | Split by local day | Pay at $17.50 |
|---|---|---|---|---|---|
| VIS-3001 (DST ends 2026-11-01) | 2026-10-31 22:00 EDT to 2026-11-01 06:00 EST | 02:00Z to 11:00Z | **9.00 h** | 2.00 h on 10-31 (period ending 10-31), 7.00 h on 11-01 | $157.50 |
| VIS-3002 (DST starts 2027-03-14) | 2027-03-13 22:00 EST to 2027-03-14 06:00 EDT | 03:00Z to 10:00Z | **7.00 h** | 2.00 h on 03-13, 5.00 h on 03-14 | $122.50 |

A wall-clock subtraction gives 8.00 h for both visits, which is the defect this case guards against. The trap is easy to fall into: for example, subtracting two Python datetimes that share the same tzinfo object returns wall-clock time, not elapsed time. The case also confirms that the 14-hour auto-close threshold is measured in elapsed time, and that the schedule board shows both visits as 22:00 to 06:00 with the correct offsets.

### 14. TC-BIL-004: billing capped at the remaining authorization

| Field | Value |
|---|---|
| Requirement | FR-BIL-03 |
| Business rule | BR-049: billed units are capped at the remaining authorized units; the excess is shown but not charged |
| Story | US-045 |
| Data | Seed `auth-cap`: SA-1002 (PA-2026-41207), 480 T1019 units, 460 billed June to August, 20 remaining; visits A, B, C; oracle `expected_billing_C-10234_2026-09.csv` |
| Technique | BVA on remaining units |

| Visit | Minutes | Units delivered | Remaining before | Billable | Not billable | Amount |
|---|---|---|---|---|---|---|
| A, VIS-0002 (2026-09-08) | 127 | 8 | 20 | 8 | 0 | $58.00 |
| B, VIS-0006 (2026-09-10) | 113 | 8 | 12 | 8 | 0 | $58.00 |
| C, VIS-0011 (2026-09-12) | 120 | 8 | 4 | 4 | 4, "Not billable - exceeds authorization" | $29.00 |
| **Total** | | **24** | | **20** | **4** | **$145.00** |

The uncapped invoice on SA-1001 is 24 units = $174.00 (TC-BIL-003). The cap is applied in visit date order, so the excess falls on the latest visit.

### 15. TC-SCH-003: caregiver overlap and travel buffer

| Field | Value |
|---|---|
| Requirement | FR-SCH-03 |
| Business rule | BR-016: overlapping visits are a hard block; consecutive visits at different addresses less than 15 minutes apart are a warning |
| Story | US-021 |
| Data | E-2033 already has VIS-0201 at C-10262, 2026-09-15 09:00-11:00; `api-fixtures.json` `scheduling.complianceOverlap` |
| Technique | BVA, via POST /visits/compliance-checks (dry run) |

| Proposed visit for E-2033 | Expected result |
|---|---|
| C-10289, 10:00-11:30 | SCH_CAREGIVER_OVERLAP, `hardBlock: true`, `canSave: false` |
| C-10289, 10:59-12:00 | SCH_CAREGIVER_OVERLAP, hard block |
| C-10262 (same address), 11:00-12:00 | Pass: intervals are half-open (DEF-007) |
| C-10289, 11:14-12:30 | SCH_TRAVEL_BUFFER_SHORT warning (14 min) |
| C-10289, 11:15-12:30 | Pass (exactly 15 min) |

No visit is created by a dry run, and every message states the problem and the fix (NFR-USE-03).

## Related documents

- [Test strategy and plan](test-strategy-and-plan.md)
- [Test cases (CSV)](test-cases.csv)
- [Test data](test-data/README.md)
- [Postman collection](api-tests/tendwell.postman_collection.json)
- [UAT plan and scripts](uat-plan-and-scripts.md)
- [Defect log](defect-log.csv) and [defect report example](defect-report-example.md)
- [Software requirements specification](../02-requirements/SRS.md)
- [Business rules](../02-requirements/business-rules.md)
- [Requirements traceability matrix (CSV)](../02-requirements/requirements-traceability-matrix.csv)
- [User stories: EVV](../05-delivery/user-stories/EP-06-evv.md), [eMAR](../05-delivery/user-stories/EP-07-emar-vitals.md), [Payroll](../05-delivery/user-stories/EP-10-payroll.md), [Billing](../05-delivery/user-stories/EP-11-billing.md)
