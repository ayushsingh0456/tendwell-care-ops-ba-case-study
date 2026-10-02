# EP-07 Medication Administration (eMAR) & Vitals: user stories

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DEL-US-07 |
| Version | 1.2 |
| Status | Baselined |
| Owner | Business Analyst |
| Last updated | 2026-06-19 |
| Reviewers | Product Owner, Clinical SME (RN advisor), Engineering Lead, QA Lead, Compliance and Privacy Officer |

## Purpose and scope

This file holds the user stories and acceptance criteria for EP-07. It covers medication orders and their approval, dose tasks, dose documentation, missed-dose escalation, PRN safety limits, vital signs and out-of-range alerts, and the monthly MAR grid. The Clinical SME reviewed every acceptance criterion in this file. Tendwell records and escalates; clinical decisions remain with the agency's licensed staff.

Version 1.2 records the outcome of CR-007 (auto-cancel undocumented doses at midnight), which was rejected on 2026-06-17. US-033-AC3 makes that decision testable.

## Epic

| Field | Value |
|---|---|
| Epic ID | EP-07 |
| Name | Medication Administration (eMAR) & Vitals |
| Module | MAR |
| Goal | Make every scheduled dose visible, documented and escalated when it is missed, keep PRN doses inside safe limits, and get abnormal vital signs in front of a nurse at once. |
| Objectives | OBJ-03 Undocumented medication doses (4.6% to 0.5% or less). |
| Business need | BN-07 |
| Release | R1 |

## Story list

| Story | Title | Persona | Priority | Points | Sprint |
|---|---|---|---|---|---|
| US-031 | Enter and approve a medication order | PER-03 Priya Raman, RN (AG-SUPV) | Must | 5 | S4 |
| US-032 | Document a scheduled dose | PER-01 Rosa Delgado (CG) | Must | 8 | S4 |
| US-033 | Be alerted to missed and repeatedly refused doses | PER-03 Priya Raman, RN (AG-SUPV) | Must | 5 | S4 |
| US-034 | Give a PRN dose safely | PER-01 Rosa Delgado (CG) | Must | 3 | S5 |
| US-035 | Record vitals and trigger out-of-range alerts | PER-01 Rosa Delgado (CG) | Must | 5 | S5 |
| **Total** | | | | **26** | |

Shared test data: client C-10234; scheduled order Lisinopril 10 mg tablet, 1 tablet by mouth at 08:00 daily, administration window 60 minutes, prescriber "Dr. Alan Pierce" (NPI 1234567893); PRN order Acetaminophen 500 mg tablet, 1 tablet by mouth for pain, maximum 4 doses per 24 hours, minimum interval 240 minutes. Time zone America/New_York.

## Stories

### US-031 · Enter and approve a medication order

| Field | Value |
|---|---|
| Epic | EP-07 Medication Administration (eMAR) & Vitals |
| Persona | PER-03 Priya Raman, RN (AG-SUPV) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S4 / R1 |
| Requirements | FR-MAR-01 |
| Business rules | None |
| Dependencies | US-012 |

**Story**
As a Clinical Supervisor, I want medication orders entered in full and activated only after I approve them, so that caregivers never see a dose that a nurse has not checked against the prescription.

**Acceptance criteria**

```gherkin
Scenario: US-031-AC1 Enter an order that waits for approval
  When Marcus enters for C-10234 the order Lisinopril, strength 10 mg, form tablet, dose 1 tablet, route by mouth, schedule time 08:00, start 2026-09-01, no end date, prescriber "Dr. Alan Pierce" with NPI 1234567893 and instructions "Hold if systolic BP below 100"
  Then the order is saved with status "PendingApproval"
  And no dose task is generated and caregivers do not see the order

Scenario: US-031-AC2 Approve an order
  Given the Lisinopril order is "PendingApproval"
  When Priya compares it with the prescription and approves it
  Then the order status is "Active" with Priya as approver
  And dose tasks are generated from the next scheduled time

Scenario Outline: US-031-AC3 Validate the order before saving
  When an order is saved with <issue>
  Then it is rejected with "<message>"

  Examples:
    | issue                                               | message                                                                 |
    | no route                                            | Select a route, for example by mouth.                                   |
    | a scheduled order with no schedule time             | Add at least one schedule time, or mark the order as PRN.               |
    | a PRN order without an indication                   | Enter the PRN indication, for example "pain".                           |
    | a PRN order without a maximum per 24 hours          | Enter the maximum number of PRN doses in 24 hours.                      |
    | end date 2026-08-31 before start date 2026-09-01    | The end date must be on or after the start date.                        |
    | an administration window of 14 minutes              | Set the window between 15 and 120 minutes.                              |
    | an administration window of 121 minutes             | Set the window between 15 and 120 minutes.                              |

Scenario: US-031-AC4 Only a Clinical Supervisor approves
  Given Marcus holds only the AG-COORD role
  When he opens a "PendingApproval" order
  Then no Approve action is shown
  And a direct call to POST /v1/medication-orders/{orderId}/approve returns 403

Scenario: US-031-AC5 Discontinue an order
  Given the Lisinopril order is Active and today's 08:00 dose is Overdue
  When Priya discontinues the order effective 2026-09-20 12:00 with reason "Changed by prescriber"
  Then the order status is "Discontinued"
  And no dose task is generated for any time after 2026-09-20 12:00 and future tasks leave the caregiver's due list
  And today's Overdue 08:00 dose stays on the due list and must still be documented
```

**Notes**
- Allergies recorded on the client (US-012) are displayed on the order form; automated drug-allergy and drug-interaction screening is out of scope because R1 has no drug knowledge base (Clinical SME agreed 2026-04-21).
- An order change (dose, time, route) is entered as a discontinue plus a new order so that the MAR shows exactly what was active when.
- Out of scope: e-prescribing and pharmacy integration.

### US-032 · Document a scheduled dose

| Field | Value |
|---|---|
| Epic | EP-07 Medication Administration (eMAR) & Vitals |
| Persona | PER-01 Rosa Delgado (CG) |
| Priority | Must |
| Estimate | 8 points |
| Sprint / Release | S4 / R1 |
| Requirements | FR-MAR-02, FR-MAR-03, FR-MAR-09 |
| Business rules | BR-029, BR-032 |
| Dependencies | US-031, US-025 |

**Story**
As a caregiver, I want the doses due during my visit listed on my visit screen and recorded with one tap, so that every dose I give, or cannot give, is documented at the time.

**Acceptance criteria**

```gherkin
Scenario: US-032-AC1 Generate dose tasks for a rolling 7 days
  Given the Lisinopril order became Active on 2026-09-14 at 15:00
  Then dose tasks exist for 08:00 on each day from 2026-09-15 to 2026-09-21
  When the nightly job runs on 2026-09-15 and then runs again
  Then exactly one task is added, for 2026-09-22, and no task is duplicated

Scenario: US-032-AC2 Show due doses on the visit screen and record Given
  Given Rosa is clocked in to the 07:30 to 09:30 visit for C-10234 on 2026-09-15
  When she opens the visit screen
  Then she sees "Lisinopril 10 mg tablet, 1 tablet by mouth, due 08:00 (07:00 to 09:00)"
  When she records "Given" at 08:05
  Then the dose task status is "Given" with administration time 08:05 and Rosa as recorder

Scenario Outline: US-032-AC3 Administration window from the order setting
  Given a dose is scheduled at 20:00 and the order's window is <window> minutes
  Then the administration window is <start> to <end>

  Examples:
    | window | start | end   |
    | 60     | 19:00 | 21:00 |
    | 15     | 19:45 | 20:15 |
    | 120    | 18:00 | 22:00 |

Scenario Outline: US-032-AC4 Outcomes that need a reason
  When Rosa records the outcome "<outcome>" with reason "<reason>"
  Then the result is "<result>"

  Examples:
    | outcome                              | reason                            | result                                    |
    | Given                                |                                   | accepted                                  |
    | Refused                              | Client said she felt nauseous     | accepted                                  |
    | Refused                              |                                   | rejected: enter the reason for Refused    |
    | Held                                 | Systolic BP 96, per instructions  | accepted                                  |
    | Held                                 |                                   | rejected: enter the reason for Held       |
    | Not available                        |                                   | rejected: enter the reason for Not available |
    | Self-administered with supervision   |                                   | accepted                                  |

Scenario: US-032-AC5 Document doses offline
  Given Rosa has no connectivity during the visit
  When she records "Given" at 08:05
  Then the outcome is queued with the EVV punches and shows "Saved on this phone"
  And on sync the server keeps 08:05 as the administration time

Scenario: US-032-AC6 Print the monthly MAR grid
  Given C-10234 had 30 scheduled Lisinopril doses and 2 PRN acetaminophen doses in August 2026
  When Priya opens GET /v1/clients/{clientId}/mar?month=2026-08 and prints it
  Then the grid shows one row per order and scheduled time and one column per day, with the outcome code and recorder initials in each cell
  And late entries are marked "LE" and Missed - undocumented doses are marked "MU"
  And PRN administrations are listed with time, indication and recorder
  And the printout carries a watermark with Priya's name, the tenant and the print timestamp
```

**Notes**
- FR-MAR-09 (monthly MAR grid, used by the Clinical Supervisor) is delivered in this story because it reads the same dose data; the Supervisor is the user of AC6.
- The caregiver sees only doses for the client she is currently visiting, and only from 60 minutes before the window opens.
- Accessibility: outcome buttons meet a 44 x 44 pt target size and work with 200% font scaling (NFR-ACC-01).
- Analytics: the undocumented-dose rate (OBJ-03) = Missed - undocumented doses / scheduled doses, per tenant per month.

### US-033 · Be alerted to missed and repeatedly refused doses

| Field | Value |
|---|---|
| Epic | EP-07 Medication Administration (eMAR) & Vitals |
| Persona | PER-03 Priya Raman, RN (AG-SUPV) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S4 / R1 |
| Requirements | FR-MAR-04, FR-MAR-06 |
| Business rules | BR-030, BR-031, BR-032 |
| Dependencies | US-032, US-050 |

**Story**
As a Clinical Supervisor, I want an escalation when a dose goes undocumented and an alert when a client keeps refusing or having a medication held, so that I can act on a clinical risk the same day.

**Acceptance criteria**

```gherkin
Scenario Outline: US-033-AC1 Escalate an undocumented dose step by step
  Given a Lisinopril dose is scheduled at 08:00 with a 60-minute window (07:00 to 09:00)
  And no outcome has been recorded
  When the time reaches <time>
  Then the dose status is "<status>"
  And <notification>

  Examples:
    | time  | status               | notification                                                              |
    | 08:00 | Due                  | Rosa receives a reminder                                                  |
    | 09:00 | Overdue              | Rosa and the Coordinator receive an Overdue alert                         |
    | 09:59 | Overdue              | no new alert is sent                                                      |
    | 10:00 | MissedUndocumented   | Priya receives an urgent alert that bypasses quiet hours                  |

Scenario Outline: US-033-AC2 Late entry within 24 hours of the scheduled time
  Given the 08:00 dose on 2026-09-15 is "MissedUndocumented"
  When Rosa records "Given" with administration time 08:10 at <entry time>
  Then the result is "<result>"

  Examples:
    | entry time       | result                                                                               |
    | 2026-09-15 11:30 | accepted, status "Given", labelled "Late entry"                                      |
    | 2026-09-16 08:00 | accepted, status "Given", labelled "Late entry"                                      |
    | 2026-09-16 08:01 | rejected: "The late-entry window has closed. Ask your Clinical Supervisor to annotate this dose." |

Scenario: US-033-AC3 Undocumented doses are never cancelled automatically
  Given the 20:00 dose on 2026-09-15 is "MissedUndocumented" at 23:59
  When the date changes to 2026-09-16 and every nightly job has run
  Then the dose is still "MissedUndocumented" and still appears on the MAR and in Priya's review queue
  And no job or user can delete it; Priya can only add an annotation after the late-entry window

Scenario: US-033-AC4 Escalation stops once the dose is documented
  Given the 08:00 dose became "Overdue" at 09:00
  When Rosa records "Given" at 09:30 with administration time 08:50
  Then the dose status is "Given" and no MissedUndocumented status or Supervisor alert follows
  And the Overdue alert for the Coordinator is marked resolved

Scenario Outline: US-033-AC5 Alert after 2 consecutive Refused or Held outcomes for the same order
  Given the last recorded outcomes for <order> are <outcomes>, oldest first
  Then Priya <alert>

  Examples:
    | order                    | outcomes                      | alert                                  |
    | Lisinopril               | Refused, Refused              | receives a repeated-refusal alert      |
    | Lisinopril               | Held, Refused                 | receives a repeated-refusal alert      |
    | Lisinopril               | Refused, Given, Refused       | receives no alert                      |
    | Lisinopril then Metformin| Refused, Refused              | receives no alert                      |
```

**Notes**
- CR-007 (auto-cancel undocumented doses at midnight) was rejected on clinical-safety and audit grounds; AC3 encodes the decision. See the change request log and DEC-10.
- Overdue and Missed alerts belong to the missed-dose event family and are urgent under BR-053, so a 22:00 dose in a supported-living home escalates at night (Clinical SME, 2026-04-28).
- Escalation steps use the ladder engine of US-050, with recipients resolved at send time (BR-054).
- Analytics: Missed - undocumented doses per 100 scheduled doses, by location and shift.

### US-034 · Give a PRN dose safely

| Field | Value |
|---|---|
| Epic | EP-07 Medication Administration (eMAR) & Vitals |
| Persona | PER-01 Rosa Delgado (CG) |
| Priority | Must |
| Estimate | 3 points |
| Sprint / Release | S5 / R1 |
| Requirements | FR-MAR-05 |
| Business rules | BR-033 |
| Dependencies | US-031, US-032 |

**Story**
As a caregiver, I want the app to check PRN limits before I record an as-needed dose, so that I never give more than the prescriber allowed.

**Acceptance criteria**

```gherkin
Scenario: US-034-AC1 Record a PRN dose with an indication
  Given the acetaminophen PRN order is Active and no PRN dose was given in the last 24 hours
  When Rosa records a PRN dose at 10:00 with indication "Knee pain 6/10"
  Then the administration is saved with time, indication and Rosa as recorder
  And the app prompts for a follow-up note on effect before clock-out

Scenario: US-034-AC2 An indication is required
  When Rosa records a PRN dose without an indication
  Then it is rejected with "Enter why this PRN dose is needed."

Scenario Outline: US-034-AC3 Enforce the minimum interval
  Given the last PRN dose was given at 10:00 and the minimum interval is 240 minutes
  When Rosa tries to record a PRN dose at <time>
  Then the result is "<result>"

  Examples:
    | time  | result                                                                |
    | 13:59 | blocked: "Too soon. The next dose is allowed from 14:00."             |
    | 14:00 | accepted                                                              |

Scenario Outline: US-034-AC4 Enforce the rolling 24-hour maximum
  Given PRN doses were given on 2026-09-14 at 06:00, 10:00, 14:00 and 18:00 and the maximum is 4 per 24 hours
  When Rosa tries to record a PRN dose at <time>
  Then the result is "<result>"

  Examples:
    | time             | result                                                                      |
    | 2026-09-15 05:59 | blocked: "Maximum of 4 doses in 24 hours reached. Next dose allowed 06:00." |
    | 2026-09-15 06:00 | accepted                                                                    |

Scenario: US-034-AC5 Blocks cannot be overridden by the caregiver
  Given a PRN dose is blocked
  Then the app offers no override and shows "Contact your Clinical Supervisor"
  And the blocked attempt is recorded in the audit log

Scenario: US-034-AC6 Conflict found when an offline dose syncs
  Given Rosa recorded a PRN dose offline at 13:30 while Maya had recorded one online at 12:00 for the same client
  When Rosa's dose syncs
  Then the administration is kept because it happened
  And Priya receives an urgent alert "PRN limit exceeded" with both administrations
```

**Notes**
- Rolling 24 hours counts doses with an administration time later than 24 hours before the proposed dose; a dose exactly 24 hours earlier no longer counts.
- Offline, the app checks limits against the PRN history it last synced and warns that other staff may have given a dose.
- Out of scope: PRN effectiveness scoring and trend charts.

### US-035 · Record vitals and trigger out-of-range alerts

| Field | Value |
|---|---|
| Epic | EP-07 Medication Administration (eMAR) & Vitals |
| Persona | PER-01 Rosa Delgado (CG) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S5 / R1 |
| Requirements | FR-MAR-07, FR-MAR-08 |
| Business rules | BR-034, BR-053 |
| Dependencies | US-025, US-050 |

**Story**
As a caregiver, I want to record vital signs during the visit and be told what to do when a reading is out of range, so that the nurse knows at once and I follow the care plan.

**Acceptance criteria**

```gherkin
Scenario: US-035-AC1 Record an in-range reading
  When Rosa records blood pressure 128/82 mmHg, method "Sitting, left arm, automatic cuff", at 08:15
  Then the reading is saved with time, method, Rosa as recorder and the visit
  And it is not flagged out of range

Scenario Outline: US-035-AC2 Default alert ranges
  Given C-10234 has no client-specific ranges
  When Rosa records <type> <value>
  Then the reading is <flag>

  Examples:
    | type          | value      | flag          |
    | systolic BP   | 89 mmHg    | out of range  |
    | systolic BP   | 90 mmHg    | in range      |
    | systolic BP   | 180 mmHg   | in range      |
    | systolic BP   | 181 mmHg   | out of range  |
    | diastolic BP  | 110 mmHg   | in range      |
    | diastolic BP  | 111 mmHg   | out of range  |
    | pulse         | 49 bpm     | out of range  |
    | pulse         | 121 bpm    | out of range  |
    | temperature   | 100.3 F    | in range      |
    | temperature   | 100.4 F    | out of range  |
    | SpO2          | 92%        | in range      |
    | SpO2          | 91%        | out of range  |
    | blood glucose | 69 mg/dL   | out of range  |
    | blood glucose | 300 mg/dL  | in range      |
    | blood glucose | 301 mg/dL  | out of range  |

Scenario: US-035-AC3 Out-of-range readings alert the nurse at any hour
  Given the time is 22:30, inside quiet hours
  When Rosa records SpO2 89%
  Then Priya receives an urgent alert by push and SMS within 1 minute
  And the alert text has no PHI: "Urgent: vital sign alert at Lakemont North. Sign in to review."
  And Rosa sees the care-plan instruction "Recheck in 5 minutes at rest. If still below 92%, call the on-call nurse."

Scenario: US-035-AC4 Client-specific ranges override the defaults
  Given Priya set the SpO2 low limit for C-10234 to 88% because of COPD
  When Rosa records SpO2 89%
  Then the reading is in range and no alert is sent
  When Rosa records SpO2 87%
  Then the reading is out of range and Priya is alerted

Scenario Outline: US-035-AC5 Reject implausible values
  When Rosa records <type> <value>
  Then it is rejected with "<message>"

  Examples:
    | type        | value | message                                         |
    | SpO2        | 101%  | Enter an SpO2 value from 50 to 100.             |
    | pain score  | 11    | Enter a pain score from 0 to 10.                |
    | pulse       | 0 bpm | Enter a pulse from 20 to 250 bpm.               |

Scenario: US-035-AC6 Only a Clinical Supervisor sets client ranges
  Given Marcus holds only the AG-COORD role
  When he calls PUT /v1/clients/{clientId}/vital-ranges
  Then the request returns 403
```

**Notes**
- Default ranges come from BR-034 and were confirmed by the Clinical SME; agencies can change client ranges, not the platform defaults.
- Readings are queued offline like dose outcomes; the alert is sent when the reading syncs and shows the capture time.
- Out of scope: Bluetooth device integration for vitals (R2 candidate).

## Related documents

- [Epics overview](../epics.md)
- [Change request log](../change-request-log.md)
- [Decision log](../decision-log.md)
- [Software requirements specification](../../02-requirements/SRS.md)
- [Business rules catalog](../../02-requirements/business-rules.md)
- [State machines](../../03-design/diagrams/state-machines.md)
- [Process flows](../../03-design/diagrams/process-flows.md)
- [Test cases](../../06-quality/test-cases.md)
- [UAT plan and scripts](../../06-quality/uat-plan-and-scripts.md)
