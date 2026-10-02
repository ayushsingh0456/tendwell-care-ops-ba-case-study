# UAT plan and scripts

## Document control

| Field | Value |
|---|---|
| Document ID | TW-QA-03 |
| Version | 1.2 |
| Status | Closed (UAT complete; signed off 2026-06-25) |
| Owner | Business Analyst |
| Last updated | 2026-06-26 |
| Reviewers | Product Owner, QA Lead, Customer Success Lead, Clinical SME (RN advisor), Compliance and Privacy Officer |

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-05-29 | Plan and 12 scripts approved by the Product Owner and the Clinical SME |
| 1.1 | 2026-06-12 | Scripts aligned with SRS v1.2 clarifications (zero-minute escalation step; Overdue dose alerts are urgent) |
| 1.2 | 2026-06-26 | Round 1 and round 2 results, sign-off and go decision recorded |

## Purpose and scope

User acceptance testing (UAT) is where the three pilot agencies confirm that Tendwell R1 supports their real work before the pilot go-live on 2026-07-06. SIT has already proven that each requirement works as specified ([test strategy](test-strategy-and-plan.md)). UAT asks a different question: can an agency's own staff run a full day, a pay period and a month-end with it, and do the results match what the agency would expect? The 12 scenarios below follow the core value chain end to end: authorization, schedule, EVV and care documentation, verified visit, payroll export and client billing.

In scope: R1 functionality across the Agency Web App, the Caregiver Mobile App and the public sign-up site. Out of scope: the Family Portal (R2, CR-003), the agencies' payroll providers and clearinghouses (agencies import the export files themselves after UAT), and performance and security, which were accepted in SIT.

## 1. Objectives

1. Confirm that each pilot agency can complete its critical workflows without workarounds that would put care, pay or billing at risk.
2. Confirm that calculated results (pay lines, invoices, dose escalations, deadlines) match the agency's own expectations on canonical data.
3. Find gaps between the specified behavior and real practice, and route them as defects, clarifications or enhancements.
4. Get a documented acceptance decision from each agency and from the Clinical SME and the Compliance and Privacy Officer for their areas.

## 2. Participants

Participants are pilot staff, by role, using synthetic accounts. Personas (PER-01 to PER-05) describe the archetype each scenario is written for.

| Tenant | Role | Count | Scenarios |
|---|---|---|---|
| TEN-001 Harborview Home Care (HOME_VISIT) | Agency Administrator (AG-ADM) | 1 | UAT-02, UAT-03, UAT-10 |
| | Care Coordinator (AG-COORD) | 2 | UAT-02 to UAT-06, UAT-09 |
| | Clinical Supervisor, RN (AG-SUPV) | 1 | UAT-02 |
| | Billing & Payroll Specialist (AG-FIN) | 1 | UAT-03, UAT-10, UAT-11 |
| | Caregivers (CG): 2 Android, 2 iOS | 4 | UAT-04, UAT-05, UAT-06, UAT-09 |
| TEN-002 Cedar Lane Adult Day Center (ADULT_DAY) | Agency Administrator | 1 | UAT-01, UAT-12 |
| | Care Coordinator | 1 | UAT-12 |
| | Billing & Payroll Specialist | 1 | UAT-11 |
| | Day-program staff (CG) | 2 | UAT-11 (attendance check-ins) |
| TEN-003 Northgate Supported Living (SUPPORTED_LIVING, HOME_VISIT) | Agency Administrator | 1 | UAT-08, UAT-12 |
| | Clinical Supervisor, RN | 1 | UAT-07, UAT-08 |
| | Care Coordinator | 1 | UAT-07, UAT-08 |
| | Billing & Payroll Specialist | 1 | UAT-11 |
| | Direct support staff (CG) | 3 | UAT-07, UAT-08 |
| **Total** | | **21** | |

**Tendwell facilitators:** Business Analyst (UAT lead, scripts, triage of findings), Customer Success Lead (scheduling, agency liaison), QA Engineer (environment, data resets, device support), UX Designer (observer), Clinical SME (eMAR and incident scenarios), Compliance and Privacy Officer (UAT-02 PHI reveal and UAT-12). A separate moderated usability session on 2026-06-16 with 10 office staff new to Tendwell measured NFR-USE-02 (TC-NFR-018).

## 3. Schedule (June 2026)

| Date | Activity | Tenants |
|---|---|---|
| 2026-06-08 to 06-10 | Participant training: 30 minutes per role, on the UAT tenants in demo mode | All |
| 2026-06-10 | UAT readiness review (entry criteria) | Tendwell |
| 2026-06-11 (Thu) | Round 1: UAT-01, UAT-12, UAT-11 adult-day part; UAT-07 medication pass | TEN-002, TEN-003 |
| 2026-06-12 (Fri) | Round 1: UAT-08, UAT-11 fixed-monthly part; UAT-02, UAT-03. SRS v1.2 baselined with UAT clarifications | TEN-003, TEN-001 |
| 2026-06-15 (Mon) | Round 1: UAT-04, UAT-05, UAT-06, UAT-09 | TEN-001 |
| 2026-06-16 (Tue) | Round 1: UAT-10; UAT-07 month-end MAR review; usability session | TEN-001, TEN-003 |
| 2026-06-17 (Wed) | Round 1: UAT-11 hourly part; round 1 review | TEN-001 |
| 2026-06-18 | Build v1.0.0-rc.5 with UAT fixes deployed | |
| 2026-06-18 to 06-22 | Round 2: TEN-001 retests and full pass | TEN-001 |
| 2026-06-23 | Round 2: TEN-002 | TEN-002 |
| 2026-06-24 | Round 2: TEN-003 | TEN-003 |
| 2026-06-25 | Sign-off | All |
| 2026-06-26 | Go/no-go | Steering group |

## 4. Environment and data

| Item | Detail |
|---|---|
| Environment | Staging, build v1.0.0-rc.4 (round 1) and v1.0.0-rc.5 (round 2) |
| Tenants | Three UAT tenants modeled on TEN-001, TEN-002 and TEN-003 and seeded from the [synthetic test data set](test-data/README.md); same record keys (C-10234, E-2041) |
| Data | Synthetic only. No agency brought real client, staff or payroll data into UAT; agencies compared outputs against their own expectations on the synthetic records |
| Business date | Scenarios that close a period run on a simulated business calendar: the QA Engineer sets the UAT tenant's virtual clock before the session (shown in a banner). UAT-10 runs at 2026-09-14 07:00 to process the Labor Day workweek; UAT-11 at 2026-10-01 06:00; UAT-07 and UAT-08 move through the day in steps |
| Field scenarios | Service addresses of the UAT clients used in UAT-05 and UAT-06 point to each agency's training room, so caregivers can clock in on site; a second address 212 m away is used for the mismatch step |
| Devices | Participants' own phones with the UAT build (TestFlight and Play internal testing), plus 4 loaner devices from the [device matrix](test-strategy-and-plan.md#34-mobile-device-os-and-condition-matrix) |
| Integrations | Payments in test mode, SMS test sub-account, email sandbox, identity verification vendor sandbox |

## 5. Entry and exit criteria

| Entry criteria (checked at the readiness review on 2026-06-10) | Status |
|---|---|
| SIT exit met: pass rate of executed cases at least 95%, no open S1 or S2 | Met (SIT cycle 2: 95.5%, 0 S1, 0 S2) |
| UAT tenants seeded; seed validation passed | Met |
| Scripts approved by the Product Owner and the Clinical SME | Met (2026-05-29) |
| Participants trained and accounts issued; devices enrolled | Met (21 of 21) |
| Defect and feedback process briefed to participants | Met |

| Exit criteria | Status at sign-off |
|---|---|
| All 12 scenarios passed | Met (round 2) |
| No open S1 or S2 defects | Met |
| Every open S3 or S4 has a workaround, an owner and a target release | Met (4 known issues) |
| Sign-off from each pilot agency, the Clinical SME and the Compliance and Privacy Officer | Met (2026-06-25) |

## 6. Defect and feedback handling

- Participants record each finding in the UAT feedback form (scenario, step, what they expected, what happened, screenshot). The facilitator in the room helps, so nobody needs to learn the defect tool.
- The Business Analyst classifies each finding the same day as a **defect** (behavior differs from the SRS), a **clarification** (the SRS is silent or ambiguous) or an **enhancement** (new need). Defects go into the defect log with severity and enter the 09:30 daily triage; S1 and S2 defects are fixed for round 2.
- Clarifications are resolved by the Business Analyst with the Product Owner, and with the Clinical SME or the Compliance and Privacy Officer when care or privacy is involved. Two UAT clarifications changed behavior and were baselined in SRS v1.2 on 2026-06-12 (DEF-050, DEF-052).
- Enhancements go to the product backlog with the participant's words attached. They do not block acceptance.
- Each failed step is retested in round 2 by the participant who found it, if possible.

## 7. UAT scripts

Each script records the round 2 result (v1.0.0-rc.5). Comments note round 1 failures and the defects behind them. Pass/Fail is set by the participant; the facilitator records it.

### UAT-01: Register a new agency and complete the setup checklist

| Field | Value |
|---|---|
| Business scenario | An agency owner signs up online with a trial code and gets the agency ready for its first visit without help from Tendwell |
| Persona | PER-05 Tom Brennan (AG-ADM) |
| Participants | TEN-002 Agency Administrator |
| Preconditions | Public sign-up site on staging; trial code TRIAL21 and promo codes LAKEMONT20 and WELCOME50 active; plan Core at $14.00 per active client seat |
| Linked stories / requirements | US-001, US-002, US-003, US-004 / FR-ONB-01 to FR-ONB-06 |

| Step | Action | Expected result | Pass/Fail | Comments |
|---|---|---|---|---|
| 1 | Open the sign-up link with TRIAL21; enter owner details and agency legal details (EIN, address in Lakemont, OH 43999, time zone America/New_York); select Core and ADULT_DAY | Price summary shows "21-day free trial, no payment method required"; tenant created as Pending; verification email received | Pass | |
| 2 | Open the verification link from the email | Signed in; tenant in Trial with an end date 21 days out; checklist shows "0 of 6 complete" | Pass | |
| 3 | Add the location, confirm the service line, add payer "Lakemont County Medicaid", add one caregiver, admit one client, schedule one visit | Each item ticks itself; checklist shows "6 of 6 complete" | Pass | Participant: "faster than our current onboarding call" |
| 4 | In a second sandbox sign-up, apply LAKEMONT20, then WELCOME50 | $11.20 per active client seat (20% off); then a prompt to replace LAKEMONT20 with WELCOME50 | Pass | |
| 5 | Open Settings > Subscription | Plan, seats, next invoice date and estimate; card shown only as brand and last 4 digits | Pass | |

### UAT-02: Admit a client with an authorization and an approved care plan

| Field | Value |
|---|---|
| Business scenario | A new client is accepted for service; the coordinator admits the client, records the payer authorization and the care plan, and the RN approves the plan before the first visit |
| Persona | PER-02 Marcus Hale (AG-COORD); PER-03 Priya Raman, RN (AG-SUPV) |
| Participants | TEN-001 Care Coordinator, Clinical Supervisor, Agency Administrator |
| Preconditions | Lakemont North location; payer Lakemont County Medicaid; existing client C-10301 Ruth Kimball (DOB 1950-02-03) |
| Linked stories / requirements | US-012, US-013, US-014, US-015 / FR-CLI-01 to FR-CLI-06, FR-CLI-08 |

| Step | Action | Expected result | Pass/Fail | Comments |
|---|---|---|---|---|
| 1 | Admit "Ruth Kimball", DOB 1950-02-03, Medicaid ID ZZ99001234, address 342 Old Mill Road | Duplicate warning naming C-10301; nothing saved until the coordinator confirms "This is a different person" | Pass | Coordinator confirmed the warning would have caught 2 real duplicates last year |
| 2 | Confirm and save; add allergy, primary diagnosis I10, emergency contact; record "Rosa Delgado" as Preferred | Client created with the next client number; PHI masked; map pin shows the 150 m geofence | Pass | |
| 3 | Record a T1019 authorization: 480 units at $7.25, 2026-09-01 to 2026-11-30 | Authorization Active; 480 units remaining | Pass | |
| 4 | Create care plan v1 (Bathing assistance, Mobility support, Light housekeeping; visit note required) and submit | Status PendingApproval; the coordinator has no Approve action | Pass | |
| 5 | Clinical Supervisor approves the plan | v1 Active with approver and timestamp | Pass | |
| 6 | Coordinator reveals the client's phone with reason "Care coordination" | Full phone shown for this view only; audit event visible to the Agency Administrator | Pass | Compliance and Privacy Officer observed |

### UAT-03: Onboard a caregiver, track credentials and stop an expired blocking credential

| Field | Value |
|---|---|
| Business scenario | A new aide is hired; the office records credentials and pay; an aide whose CPR has lapsed cannot be scheduled |
| Persona | PER-02 Marcus Hale (AG-COORD); PER-04 Denise Carter (AG-FIN) |
| Participants | TEN-001 Care Coordinator, Billing & Payroll Specialist, Agency Administrator |
| Preconditions | Credential types: CPR certification (Blocking, 24 months), Driver's license (Advisory); caregiver E-2052 with CPR expired 2026-08-31; virtual clock 2026-09-15 |
| Linked stories / requirements | US-017, US-018, US-019 / FR-WRK-01 to FR-WRK-05, FR-SCH-03 |

| Step | Action | Expected result | Pass/Fail | Comments |
|---|---|---|---|---|
| 1 | Create a caregiver with employee number, phone, email, hire date and location; send the invitation | Caregiver Active; user Invited; SMS and email with a single-use link and no client information | Pass | |
| 2 | Record CPR certification expiring 2026-10-15 and upload the PDF | Status Expiring (30 days); 30-day reminder queued to the caregiver and the location's coordinators | Pass | |
| 3 | Try to assign E-2052 to a new visit | Hard block: "Grace Whitaker has an expired CPR certification." No override offered | Pass | |
| 4 | Open the schedule board for 2026-09-17 | E-2052's existing visit flagged "Credential expired" | Pass | |
| 5 | Billing & Payroll Specialist sets the new caregiver's pay profile effective 2026-09-21: Hourly $18.00, OT-, holiday- and mileage-eligible | Saved and audited; the coordinator cannot see the Pay tab | Pass | |

### UAT-04: Build the week with recurring visits, compliance checks and open shifts

| Field | Value |
|---|---|
| Business scenario | The coordinator sets up recurring visits for a new client, is warned before creating conflicts, and fills a gap through open shifts |
| Persona | PER-02 Marcus Hale (AG-COORD); PER-01 Rosa Delgado (CG) |
| Participants | TEN-001 Care Coordinators, 2 caregivers |
| Preconditions | Client from UAT-02 with an Active authorization; open-shift confirmation On; open shift VIS-0114 |
| Linked stories / requirements | US-020, US-021, US-022, US-023, US-024 / FR-SCH-01 to FR-SCH-07 |

| Step | Action | Expected result | Pass/Fail | Comments |
|---|---|---|---|---|
| 1 | Create a Mon/Wed/Fri 08:00-10:00 pattern with Rosa, no end date | Visits created for the rolling 8 weeks; Rosa gets one push within 1 minute with no client name | Pass | |
| 2 | Add a one-off visit for Rosa that overlaps an existing visit | Hard block "Caregiver overlap" with a suggested fix; nothing saved | Pass | |
| 3 | Add a visit at another address starting 10 min after Rosa's previous visit ends | Travel buffer warning; save allowed | Pass | |
| 4 | Cancel one occurrence with reason "Caregiver unavailable" | Cancelled and republished as an open shift | Pass | |
| 5 | Two caregivers tap Claim on the same open shift | One claim Pending confirmation; the other sees "This shift was just taken." Coordinator confirms | Pass | |
| 6 | Filter the board by service line and caregiver; switch day/week | Filters combine and persist; each status shown with label and color | Pass | Round 2 (2026-06-22): open-shift lane count did not refresh after the claim until reload. Logged as DEF-061 (S4); accepted as a known issue |

### UAT-05: Deliver a home visit from clock-in to Verified

| Field | Value |
|---|---|
| Business scenario | A caregiver arrives, clocks in, completes the care plan tasks, writes the note and clocks out; the visit becomes Verified with no office follow-up |
| Persona | PER-01 Rosa Delgado (CG) |
| Participants | TEN-001: 4 caregivers (2 Android, 2 iOS); Care Coordinator observing |
| Preconditions | Visit scheduled for the session time at a client whose service address is the training room; care plan with 3 tasks and visit note required; identity verification On |
| Linked stories / requirements | US-025, US-026, US-028, US-036 / FR-EVV-01 to FR-EVV-04, FR-EVV-06, FR-EVV-10, FR-DOC-01, FR-DOC-02 |

| Step | Action | Expected result | Pass/Fail | Comments |
|---|---|---|---|---|
| 1 | Open the app 10 minutes before the visit and tap Clock in | Clock-in in 3 taps or fewer; selfie check passes; visit In progress; no exception | Pass | Round 2 (2026-06-18): at 200% font on a 5.5-inch Android 10 phone the button sat below the fold (4 interactions). DEF-059 (S3), accepted with the sticky-button workaround |
| 2 | Mark two tasks Done and one Not done without a reason | Blocked: a reason is required | Pass | |
| 3 | Choose reason "Client declined"; try to clock out without the note | Blocked: "Write the visit note before clocking out." | Pass | |
| 4 | Write the note and clock out | Out punch recorded; visit Completed, then Verified | Pass | |
| 5 | Coordinator opens the visit | Both punches with device time, server time, distance and accuracy; visit Verified | Pass | |
| 6 | Next day after the 24-hour lock, the caregiver adds an addendum | Original note unchanged; addendum signed and time-stamped | Pass | Run on the virtual clock |

### UAT-06: Work the EVV exception queue

| Field | Value |
|---|---|
| Business scenario | The coordinator clears the morning's EVV exceptions with reason codes, so every visit can be paid and billed, without editing original punches |
| Persona | PER-02 Marcus Hale (AG-COORD); PER-01 Rosa Delgado (CG) |
| Participants | TEN-001 Care Coordinators; 2 caregivers |
| Preconditions | Visits for the session; one caregiver phone in airplane mode; second address 212 m from the service address |
| Linked stories / requirements | US-027, US-029, US-030 / FR-EVV-05, FR-EVV-07, FR-EVV-08, FR-EVV-09 |

| Step | Action | Expected result | Pass/Fail | Comments |
|---|---|---|---|---|
| 1 | A caregiver clocks in from the address 212 m away | Punch accepted; Location mismatch exception in the queue | Pass | |
| 2 | Coordinator waives it with reason and note | Visit Verified; waiver audited | Pass | |
| 3 | The offline caregiver clocks in and out, reconnects the next day (virtual clock 25 h later) | Punches keep device time; LATE_OFFLINE_SYNC raised | Pass | |
| 4 | A caregiver forgets to clock out; coordinator adds a clock-out with reason "Caregiver forgot to clock out" and a note | New Manual punch with reason, note and coordinator; original punches unchanged in the history | Pass | |
| 5 | Leave another visit open; advance the clock 14 h after clock-in | Auto-closed with the scheduled end as placeholder; Auto-closed exception; excluded from pay and billing until resolved | Pass | |

Note: the separate Low GPS accuracy exception did not exist in R1. It was added in R1.1 (CR-004) after INC-2026-011 and is covered by TC-EVV-004.

### UAT-07: Medication pass in a supported-living home

| Field | Value |
|---|---|
| Business scenario | Staff give scheduled medications across a day and evening; refusals, PRN doses and an undocumented evening dose are escalated to the RN in time |
| Persona | PER-03 Priya Raman, RN (AG-SUPV); direct support staff (CG) |
| Participants | TEN-003 Clinical Supervisor, Care Coordinator, 3 direct support staff; Clinical SME observing |
| Preconditions | Resident C-30015 at Aspen House with orders MO-0001 to MO-0004 and MO-0008; virtual clock moved in steps; quiet hours 21:00-07:00 |
| Linked stories / requirements | US-031, US-032, US-033, US-034 / FR-MAR-01 to FR-MAR-06, FR-MAR-09, FR-NTF-02 |

| Step | Action | Expected result | Pass/Fail | Comments |
|---|---|---|---|---|
| 1 | Coordinator enters a new order; Clinical Supervisor approves it | Active only after approval; dose tasks for the next 7 days appear | Pass | |
| 2 | Staff record the 08:00 doses: Given, and Refused for lisinopril (reason required) | Refused rejected without a reason; accepted with one | Pass | |
| 3 | Next morning, lisinopril refused again | Clinical Supervisor alerted for 2 consecutive refusals | Pass | |
| 4 | Give acetaminophen PRN with an indication; try another dose 2 hours later | Second dose blocked by the 240-minute interval, with the next allowed time | Pass | |
| 5 | Leave the 20:00 metformin dose undocumented; move the clock to 21:00 and 22:00 | 21:00 Overdue alert to staff and coordinator sent at once; 22:00 Missed - undocumented and urgent alert to the Clinical Supervisor | Pass | Round 1 (2026-06-11): the 21:00 Overdue alert was held by quiet hours until 07:00. DEF-052 (requirement gap): dose alerts confirmed urgent in SRS v1.2; retested 2026-06-24 |
| 6 | Next morning, staff document the missed dose | Accepted within 24 hours and labelled Late entry; dose never deleted | Pass | Clinical SME: "matches our policy" |
| 7 | Clinical Supervisor prints the September MAR grid | Grid with every dose and status code, printable on Letter landscape | Pass | 2026-06-16: day-31 column cut for 31-day months. DEF-055 (S4); workaround: print on Legal |

### UAT-08: Out-of-range vitals and a client incident with a reporting deadline

| Field | Value |
|---|---|
| Business scenario | Staff record vitals and report an incident at night; the RN is alerted at once, investigates and closes the incident only when all actions are done |
| Persona | PER-03 Priya Raman, RN (AG-SUPV) |
| Participants | TEN-003 Clinical Supervisor, Agency Administrator, Care Coordinator, 2 direct support staff |
| Preconditions | Resident C-30029 at Cypress House; glucose high limit 250 mg/dL for this resident; virtual clock 2026-09-14 22:00 |
| Linked stories / requirements | US-035, US-037, US-038 / FR-MAR-07, FR-MAR-08, FR-DOC-03 to FR-DOC-06 |

| Step | Action | Expected result | Pass/Fail | Comments |
|---|---|---|---|---|
| 1 | Report a suspected neglect concern at 22:15 with immediate actions | Clinical Supervisor and Agency Administrator notified at once despite quiet hours; message has no client details; deadline 2026-09-15 22:15 | Pass | |
| 2 | Record SpO2 91% at 22:30 | Out of range; urgent alert to the Clinical Supervisor; staff see the care-plan instruction | Pass | |
| 3 | Record glucose 251 mg/dL at 22:40 | Out of range under the resident's 250 limit (the 300 default would not alert) | Pass | |
| 4 | Advance to 10:15 and 19:51 the next day | 50% and 90% deadline alerts | Pass | |
| 5 | Clinical Supervisor records investigation, root cause, reportable flag and external reference; tries to close with one action open | Close blocked until the action is Done or Waived with a reason | Pass | |
| 6 | Complete the action and close | Incident Closed by the Clinical Supervisor | Pass | |

### UAT-09: Time off and holidays

| Field | Value |
|---|---|
| Business scenario | A caregiver requests time off; the coordinator sees the visits it affects before approving, and the visits move to open shifts |
| Persona | PER-01 Rosa Delgado (CG); PER-02 Marcus Hale (AG-COORD) |
| Participants | TEN-001 caregivers and Care Coordinators |
| Preconditions | Virtual clock 2026-09-15 09:00; caregiver with visits on both days of the request |
| Linked stories / requirements | US-039, US-040 / FR-TOF-01 to FR-TOF-05 |

| Step | Action | Expected result | Pass/Fail | Comments |
|---|---|---|---|---|
| 1 | Request PTO for 2026-09-21 | Flagged Short notice (6 days) | Pass | |
| 2 | Request Sick leave for 2026-09-16 | Not flagged | Pass | |
| 3 | Request PTO for 2026-09-16 to 2026-09-17; coordinator opens the impact view | Every visit on both dates listed, including the end date | Pass | Round 1 (2026-06-15): the 2026-09-17 visit was missing. DEF-054 (S2); retested 2026-06-19 |
| 4 | Approve | Affected visits move to Open Shifts; scheduling the caregiver on those dates is a hard block | Pass | |
| 5 | Open the holiday calendar and the board for 2026-09-07 | Labor Day shown; used by payroll as a holiday | Pass | |

### UAT-10: Labor Day pay period review and export

| Field | Value |
|---|---|
| Business scenario | The payroll specialist reviews the pay period, clears open items and exports a file the agency's payroll provider can import, with Labor Day, overtime, travel and mileage paid correctly |
| Persona | PER-04 Denise Carter (AG-FIN) |
| Participants | TEN-001 Billing & Payroll Specialist; Agency Administrator for the parallel comparison |
| Preconditions | Virtual clock 2026-09-14 07:00; pay period 2026-08-31 to 2026-09-13; E-2041's 13 visits; payroll column mapping set to the agency's payroll provider layout |
| Linked stories / requirements | US-041, US-042, US-043 / FR-PAY-01 to FR-PAY-06 |

| Step | Action | Expected result | Pass/Fail | Comments |
|---|---|---|---|---|
| 1 | Open the pre-export review | "No open items" for the period; E-2041 shows 13 Verified visits | Pass | |
| 2 | Open E-2041's summary | Holiday 6.00 h x $29.25 = $175.50; Regular 31.50 h x $19.50 = $614.25; Travel 2.50 h x $19.50 = $48.75; Overtime 3.00 h x $29.25 = $87.75; wages $926.25; mileage 46.2 mi = $32.34; payable $958.59 | Pass | Matched the agency's own spreadsheet calculation to the cent |
| 3 | Export with the agency's column mapping | CSV downloaded with a watermark; period Locked; export audited | Pass | Agency imported the file into its payroll provider's sandbox after UAT without changes |
| 4 | Export again | Rejected: the period is locked | Pass | |
| 5 | Correct a visit in the locked period (clock-out 1 h earlier) | Adjustment line of -1.00 h x $29.25 = -$29.25 in the next open period, referencing the visit | Pass | |

### UAT-11: Month-end billing across three billing models

| Field | Value |
|---|---|
| Business scenario | Each agency runs month-end billing and gets correct drafts on the first run: hourly units within the authorization, daily attendance and fixed monthly with proration, and a safe re-run |
| Persona | PER-04 Denise Carter (AG-FIN) |
| Participants | Billing & Payroll Specialists of TEN-001, TEN-002 and TEN-003; 2 TEN-002 day-program staff for check-ins |
| Preconditions | Virtual clock 2026-10-01 06:00 (TEN-001, TEN-003) and 2026-09-01 06:00 (TEN-002, August); seed scenarios `base` and `auth-cap` |
| Linked stories / requirements | US-044, US-045, US-046, US-047, US-048 / FR-BIL-01 to FR-BIL-08 |

| Step | Action | Expected result | Pass/Fail | Comments |
|---|---|---|---|---|
| 1 | TEN-001: run September billing; open C-10234 | 3 lines of 8 units (127, 113, 120 min) = 24 units = $174.00 | Pass | |
| 2 | TEN-001, scenario `auth-cap` (20 units left): run again | 20 billable units = $145.00; 4 units shown as "Not billable - exceeds authorization" | Pass | |
| 3 | TEN-002: staff check C-20011 in and out twice on 2026-08-19; run August billing | 14 days x $78.00 = $1,092.00; one charge on 2026-08-19 | Pass | Round 1 (2026-06-11): two charges on 2026-08-19. DEF-051 (S2); retested 2026-06-23 |
| 4 | TEN-003: run September billing for C-30007 (admitted 2026-09-10) | $6,200.00 x 21/30 = $4,340.00 | Pass | Round 1 (2026-06-12): $4,200.00 (31-day divisor). DEF-053 (S2); retested 2026-06-24 |
| 5 | TEN-001: re-run September billing | Same invoice numbers; no new invoices | Pass | |
| 6 | Approve and issue the private-pay invoice; send the payment link; pay $100.00 in test mode | Invoice Partially paid, balance $90.00 | Pass | |
| 7 | Issue a credit note with a reason; export the Medicaid claim batch | Balance recalculated; claim CSV with a watermark | Pass | |

### UAT-12: Notifications, escalations, audit and support access

| Field | Value |
|---|---|
| Business scenario | The administrator sets up escalations that respect staff quiet hours, checks the dashboard and audit log, and controls when Tendwell Support can see agency data |
| Persona | PER-05 Tom Brennan (AG-ADM) |
| Participants | Agency Administrators of TEN-002 and TEN-003; TEN-002 Care Coordinator; Platform Support Agent (Tendwell); Compliance and Privacy Officer observing |
| Preconditions | Default escalation ladders provisioned; virtual clock 2026-09-15 20:55 |
| Linked stories / requirements | US-049, US-050, US-051, US-052, US-011 / FR-NTF-01 to FR-NTF-05, FR-RPT-01 to FR-RPT-04, FR-IAM-07 |

| Step | Action | Expected result | Pass/Fail | Comments |
|---|---|---|---|---|
| 1 | Configure the client-incident ladder: step 1 at 0 minutes to the Clinical Supervisor, step 2 at 30 minutes to the Agency Administrator | Saved | Pass | Round 1 (2026-06-11): 0 minutes rejected. DEF-050 (requirement gap): immediate first step confirmed in SRS v1.2; retested 2026-06-23 |
| 2 | Send a schedule change at 21:05 and an urgent vital alert at 21:10 | Schedule change held until 07:00 (in-app shown at once); vital alert delivered at once | Pass | |
| 3 | Read the SMS, push and email texts | Generic text and a sign-in link; no client names, diagnoses or addresses | Pass | Compliance and Privacy Officer reviewed every template |
| 4 | Open the operations dashboard | Today's visits by status, open exceptions, missed doses, expiring credentials, authorization alerts and unbilled visits | Pass | |
| 5 | Search the audit log for PHI reveals and export it | Results filtered; export watermarked and itself audited | Pass | |
| 6 | Support agent requests 2 hours of read-only access; administrator approves, then revokes after 10 minutes | Access only between approval and revocation; every action audited with the grant ID | Pass | |

## 8. Sign-off

| Party | Signatory role | Decision | Known issues acknowledged | Date | Signature |
|---|---|---|---|---|---|
| TEN-001 Harborview Home Care | Agency Administrator | Accept with known issues | DEF-059, DEF-061 | 2026-06-25 | Signed (e-signature on file) |
| TEN-002 Cedar Lane Adult Day Center | Agency Administrator | Accept | None affecting adult day | 2026-06-25 | Signed (e-signature on file) |
| TEN-003 Northgate Supported Living | Agency Administrator and Clinical Supervisor | Accept with known issues | DEF-055 | 2026-06-25 | Signed (e-signature on file) |
| Tendwell Labs | Clinical SME (RN advisor), for UAT-07 and UAT-08 | Accept | DEF-055 | 2026-06-25 | Signed (e-signature on file) |
| Tendwell Labs | Compliance and Privacy Officer, for UAT-02 and UAT-12 | Accept | None | 2026-06-25 | Signed (e-signature on file) |
| Tendwell Labs | Product Owner | Accept; recommends Go | All 4 UAT known issues | 2026-06-25 | Signed (e-signature on file) |

## 9. UAT outcome summary

| Measure | Result |
|---|---|
| Scenarios | 12 of 12 passed in round 2. In round 1, 8 passed and 4 failed (UAT-07, UAT-09, UAT-11, UAT-12) |
| Findings raised | 23: 12 defects, 7 clarification questions, 4 enhancement requests |
| Defects by severity | S1 0, S2 4, S3 3, S4 5 |
| Defects that were requirement gaps | 2 (DEF-050, DEF-052), both clarified in SRS v1.2 on 2026-06-12 |
| Clarifications | 7 answered by the Business Analyst from the SRS with no change, for example whether a discharged client still counts as a seat in the current cycle (yes, BR-002) |
| Enhancements to the backlog | 4: bulk reassignment of a caregiver's visits from the board; Spanish SMS templates (planned with NFR-I18N-01 in R2); a payroll column-mapping preset per payroll provider; transport tracking for adult day |
| Closed before sign-off | 8 defects |
| Accepted with known issues | 4: DEF-059 (S3, clock-in button at 200% font), DEF-055 (S4, MAR day-31 column), DEF-061 (S4, open-shift count refresh) and one more S4 cosmetic issue, each with a workaround, an owner and a target of R1.2 |

**Go decision.** At the go/no-go meeting on **2026-06-26** the steering group accepted the Product Owner's recommendation of **Go** for the pilot go-live on 2026-07-06. There were no open S1 or S2 defects, all three agencies had signed off, and the 8 known issues across SIT and UAT (3 S3, 5 S4) had workarounds. Conditions:

1. TEN-001 runs payroll in parallel with its current process for the first two pay periods.
2. Daily hypercare review with all three pilot agencies until 2026-07-31.
3. The known issues are listed in the release notes with their workarounds.

## Related documents

- [Test strategy and plan](test-strategy-and-plan.md)
- [Test cases guide](test-cases.md) and [test cases (CSV)](test-cases.csv)
- [Test data](test-data/README.md)
- [Defect log](defect-log.csv)
- [Personas](../01-discovery/personas.md)
- [Software requirements specification](../02-requirements/SRS.md)
- [Business rules](../02-requirements/business-rules.md)
- [Story map](../05-delivery/story-map.md)
- [Release and sprint plan](../05-delivery/release-and-sprint-plan.md)
- [Decision log](../05-delivery/decision-log.md)
