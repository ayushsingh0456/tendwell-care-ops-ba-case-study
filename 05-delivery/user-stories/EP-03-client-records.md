# EP-03 Client Records & Care Plans: user stories

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DEL-US-03 |
| Version | 1.2 |
| Status | Baselined |
| Owner | Business Analyst |
| Last updated | 2026-06-12 |
| Reviewers | Product Owner, Engineering Lead, QA Lead, Clinical SME, Compliance and Privacy Officer |

## Purpose and scope

This file holds the user stories and acceptance criteria for EP-03. It covers client admission, duplicate detection, service authorizations and remaining units, versioned care plans with Clinical Supervisor approval, PHI masking and reveal, and client discharge. The client record is the anchor for scheduling (EP-05), EVV location checks (EP-06), eMAR (EP-07) and billing (EP-11).

## Epic

| Field | Value |
|---|---|
| Epic ID | EP-03 |
| Name | Client Records & Care Plans |
| Module | CLI |
| Goal | Keep one accurate, PHI-protected record per client, with the authorizations and approved care plan that drive scheduling, visit verification and billing. |
| Objectives | OBJ-06 Authorization-overrun denials (6.1% to 1% or less); OBJ-01 EVV completeness (a geocoded service address is a precondition of the location check). |
| Business need | BN-03 |
| Release | R1 |

## Story list

| Story | Title | Persona | Priority | Points | Sprint |
|---|---|---|---|---|---|
| US-012 | Admit a new client | PER-02 Marcus Hale (AG-COORD) | Must | 8 | S2 |
| US-013 | Record a service authorization and track remaining units | PER-02 Marcus Hale (AG-COORD) | Must | 5 | S2 |
| US-014 | Approve a versioned care plan | PER-03 Priya Raman, RN (AG-SUPV) | Must | 5 | S2 |
| US-015 | Reveal masked PHI with a reason | PER-02 Marcus Hale (AG-COORD) | Must | 3 | S2 |
| US-016 | Discharge a client | PER-02 Marcus Hale (AG-COORD) | Must | 3 | S4 |
| **Total** | | | | **24** | |

Shared test data: tenant Harborview Home Care (TEN-001), location "Lakemont North", client C-10234 (born 1948-04-11, Medicaid ID ZZ48105522, service address 418 Birchwood Lane, Lakemont, OH 43999), payer "Lakemont County Medicaid".

## Stories

### US-012 · Admit a new client

| Field | Value |
|---|---|
| Epic | EP-03 Client Records & Care Plans |
| Persona | PER-02 Marcus Hale (AG-COORD) |
| Priority | Must |
| Estimate | 8 points |
| Sprint / Release | S2 / R1 |
| Requirements | FR-CLI-01, FR-CLI-02, FR-CLI-08 |
| Business rules | BR-011, BR-017 |
| Dependencies | US-009 |

**Story**
As a Care Coordinator, I want to admit a new client with demographics, a verified service address, contacts, clinical basics, payer details and caregiver preferences, so that the client can be scheduled and visited safely from day one.

**Acceptance criteria**

```gherkin
Scenario: US-012-AC1 Admit a client with complete data
  Given Marcus is assigned to "Lakemont North"
  When he enters first and last name, date of birth 1948-04-11, gender, primary language "English", phone "+1-614-555-0187", service address "418 Birchwood Lane, Lakemont, OH 43999", allergy "Penicillin", primary diagnosis "I10", an emergency contact and payer "Lakemont County Medicaid" with Medicaid ID "ZZ48105522"
  And he saves the record
  Then the client is created with the next client number, for example "C-10234", status "Active" and the admission date
  And the address is geocoded to latitude and longitude and the geofence radius is set to the tenant default of 150 m
  And date of birth, Medicaid ID, diagnoses, phone and service address are stored with field-level encryption and shown masked

Scenario: US-012-AC2 Confirm the map pin when geocoding is imprecise
  Given the geocoder returns an approximate (non-rooftop) result for "1 County Road 9, Lakemont, OH 43999"
  When Marcus tries to save the client
  Then he must confirm or move the map pin before saving
  And the record stores that the location was confirmed manually, by whom and when

Scenario Outline: US-012-AC3 Warn of a possible duplicate client
  Given an Active client exists with first name "Ruth", last name "Kimball", date of birth 1950-02-03 and Medicaid ID "ZZ30115874"
  When Marcus admits a client with <new data>
  Then <outcome>

  Examples:
    | new data                                                     | outcome                                                       |
    | "Ruth", "Kimball", 1950-02-03, Medicaid ID "ZZ99001234"      | a duplicate warning is shown and confirmation is required     |
    | "Ruthie", "Kimbel", 1949-07-19, Medicaid ID "ZZ30115874"     | a duplicate warning is shown and confirmation is required     |
    | "Ruth", "Kimball", 1961-09-30, Medicaid ID "ZZ71180036"      | no warning is shown                                           |

Scenario: US-012-AC4 Confirming a duplicate warning is audited
  Given a duplicate warning is shown for a new client
  When Marcus confirms "This is a different person" and saves
  Then the client is created
  And the audit log records the override with the matched client number and Marcus as actor
  When instead Marcus chooses "Cancel"
  Then no client is created

Scenario Outline: US-012-AC5 Validate diagnoses as ICD-10-CM codes
  When Marcus adds the diagnosis code "<code>"
  Then the result is "<result>"

  Examples:
    | code   | result                                                          |
    | I10    | accepted with description "Essential (primary) hypertension"    |
    | E11.9  | accepted with description "Type 2 diabetes mellitus without complications" |
    | XYZ    | rejected: enter a valid ICD-10-CM code, for example I10         |

Scenario: US-012-AC6 Record caregiver preferences and exclusions
  When Marcus records caregiver Rosa Delgado as "Preferred" and caregiver Jordan Pike as "Excluded" with reason "Family declined"
  Then scheduling suggestions for this client list Rosa first
  And any attempt to assign Jordan Pike to this client is a hard block in compliance checks
  And an exclusion cannot be saved without a reason
```

**Notes**
- Exactly one diagnosis is marked primary; the first diagnosis entered is primary by default.
- UX: the address field uses autocomplete; the map preview shows the 150 m geofence circle so the Coordinator can see whether the pin sits on the right building.
- Data: allergies are free text in R1 and are shown on the eMAR order form (US-031); coded allergy lists are out of scope.
- Issue ISS-01 (approximate geocoding during migration) led to AC2.

### US-013 · Record a service authorization and track remaining units

| Field | Value |
|---|---|
| Epic | EP-03 Client Records & Care Plans |
| Persona | PER-02 Marcus Hale (AG-COORD) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S2 / R1 |
| Requirements | FR-CLI-03, FR-CLI-04 |
| Business rules | BR-009, BR-010 |
| Dependencies | US-012 |

**Story**
As a Care Coordinator, I want to record each payer authorization and see how many units remain, so that we never schedule or bill care the payer has not authorized.

**Acceptance criteria**

```gherkin
Scenario: US-013-AC1 Record an hourly authorization
  When Marcus records for C-10234 an authorization from "Lakemont County Medicaid" with auth number "PA-2026-55871", service line HOME_VISIT, service code T1019, billing model Hourly, unit type Unit15Min, rate $7.25, 480 units, period 2026-09-01 to 2026-11-30
  Then the authorization is saved with status "Active"
  And it is listed on the client's Authorizations tab with 480 units remaining

Scenario: US-013-AC2 Compute remaining units from scheduled and delivered visits
  Given the T1019 authorization for C-10234 has 480 units
  And Verified and Completed visits used 200 units
  And future Scheduled visits will use 232 units
  When Marcus opens the authorization
  Then remaining units show 48
  And utilization shows 90% with the flag "90% or more used"

Scenario Outline: US-013-AC3 Flag high utilization or near expiry
  Given today is 2026-11-16
  And an authorization has utilization <utilization> and period end <end date>
  Then the authorization <flag>

  Examples:
    | utilization | end date   | flag                                      |
    | 89%         | 2026-12-31 | is not flagged                            |
    | 90%         | 2026-12-31 | is flagged "90% or more used"             |
    | 50%         | 2026-12-01 | is not flagged                            |
    | 50%         | 2026-11-30 | is flagged "Expires in 14 days"           |

Scenario Outline: US-013-AC4 Validate authorization data
  When Marcus saves an authorization with <invalid data>
  Then it is rejected with "<message>"

  Examples:
    | invalid data                                                  | message                                                                     |
    | period end 2026-08-31 before period start 2026-09-01          | The period end must be on or after the period start.                        |
    | billing model Daily with unit type Unit15Min                  | Daily billing needs unit type Day.                                          |
    | 0 units authorized                                            | Enter the number of units authorized, 1 or more.                            |
    | same payer and service code T1019 overlapping 2026-10-01 to 2026-12-31 | An active T1019 authorization from this payer already covers these dates. |

Scenario: US-013-AC5 Expire authorizations automatically
  Given the T1019 authorization period ends 2026-11-30
  When the nightly job runs on 2026-12-01 at 00:05 America/New_York
  Then the authorization status is "Expired"
  And new visits after 2026-11-30 cannot be scheduled against it
```

**Notes**
- Units on scheduled visits use the scheduled duration and the same rounding rule as billing (BR-047); delivered units use verified durations.
- Overlapping authorizations for the same payer and service code are blocked so that billing can always find exactly one matching authorization (FR-BIL-02).
- Analytics: authorizations flagged per week feed the operations dashboard tile (US-051).
- Out of scope: electronic authorization intake from payers (R2 candidate).

### US-014 · Approve a versioned care plan

| Field | Value |
|---|---|
| Epic | EP-03 Client Records & Care Plans |
| Persona | PER-03 Priya Raman, RN (AG-SUPV) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S2 / R1 |
| Requirements | FR-CLI-05 |
| Business rules | BR-012 |
| Dependencies | US-012 |

**Story**
As a Clinical Supervisor, I want to review and approve each care plan version before caregivers use it, so that every visit follows a plan a registered nurse has signed off.

**Acceptance criteria**

```gherkin
Scenario: US-014-AC1 Approve the first care plan
  Given Marcus created care plan version 1 for C-10234 with ADL tasks "Bathing assistance" and "Mobility support" and IADL task "Light housekeeping"
  And he set "Requires visit note" to Yes and submitted it
  When Priya opens the plan and approves it
  Then version 1 status changes from "PendingApproval" to "Active"
  And the plan records Priya as approver and the approval timestamp

Scenario: US-014-AC2 Change an Active plan through a new version
  Given version 1 is Active
  When Marcus adds the task "Meal preparation" and submits
  Then version 2 is created with status "PendingApproval"
  And version 1 stays Active and is used by visits until version 2 is approved
  When Priya approves version 2
  Then version 2 is Active and version 1 is "Superseded" and read-only

Scenario: US-014-AC3 Visits keep the version that was Active at clock-in
  Given Rosa clocked in to a visit for C-10234 at 08:58 while version 1 was Active
  When Priya approves version 2 at 09:30
  Then Rosa's current visit still shows the version 1 task list at clock-out
  And the next visit, clocking in at 13:00, uses version 2

Scenario: US-014-AC4 Only a Clinical Supervisor can approve
  Given Marcus holds the AG-COORD role
  When he opens a care plan in "PendingApproval"
  Then no Approve action is shown
  And a direct call to POST /v1/care-plans/{carePlanId}/approve returns 403

Scenario: US-014-AC5 Return a plan with comments
  When Priya returns version 2 with the comment "Add transfer instructions for the bathing task"
  Then version 2 goes back to "Draft" with the comment visible to Marcus
  And version 1 stays Active
```

**Notes**
- Care-plan tasks are grouped by visit type so that a morning and an evening visit can carry different task lists.
- Clinical SME review: the plan shows the approver's name and credentials (RN) on the caregiver's task screen.
- Out of scope: e-signature by the client or legal representative on the care plan (R2 candidate).

### US-015 · Reveal masked PHI with a reason

| Field | Value |
|---|---|
| Epic | EP-03 Client Records & Care Plans |
| Persona | PER-02 Marcus Hale (AG-COORD) |
| Priority | Must |
| Estimate | 3 points |
| Sprint / Release | S2 / R1 |
| Requirements | FR-CLI-06 |
| Business rules | BR-011, BR-057 |
| Dependencies | US-012, US-009 |

**Story**
As a Care Coordinator, I want PHI masked by default and revealed only when I give a reason, so that I see the minimum necessary and every exception is accountable.

**Acceptance criteria**

```gherkin
Scenario: US-015-AC1 Mask PHI in lists and detail views
  When Marcus opens the client list and the detail page of C-10234
  Then date of birth shows "**/**/****", Medicaid ID shows "ZZ****5522", phone shows "+1-614-555-**87", service address shows "Lakemont, OH" and diagnoses show "1 diagnosis (masked)"
  And client name and client number are shown unmasked

Scenario Outline: US-015-AC2 Reveal a field only with a reason
  Given Marcus holds the permission "clients:reveal_phi"
  When he selects Reveal on "<field>" and chooses the reason "<reason>" with note "<note>"
  Then <result>

  Examples:
    | field         | reason              | note                               | result                                                   |
    | Phone         | Care coordination   |                                    | the full phone number is shown                           |
    | Medicaid ID   | Billing inquiry     |                                    | the full Medicaid ID is shown                            |
    | Date of birth | Other               | Confirming identity with hospital  | the full date of birth is shown                          |
    | Date of birth | Other               |                                    | the reveal is refused: add a note when the reason is Other |

Scenario: US-015-AC3 Reveal is limited to one field and one page view
  Given Marcus revealed the phone number of C-10234
  Then the Medicaid ID and date of birth stay masked
  And when he leaves the page and returns, the phone number is masked again

Scenario: US-015-AC4 Users without the permission cannot reveal
  Given a user without "clients:reveal_phi"
  When they view C-10234
  Then no Reveal action is shown
  And a direct call to POST /v1/clients/{clientId}/phi-reveals returns 403 and is audited as a denied attempt

Scenario: US-015-AC5 Every reveal is audited
  When Marcus reveals the phone number of C-10234 with reason "Care coordination"
  Then an audit event is written with action "phi.reveal", the client, the field, the reason, Marcus as actor, IP address, device and timestamp
  And the event appears in the audit log search for the Agency Administrator
```

**Notes**
- The revealed value is returned only in the response of the reveal call and is never cached in the browser's storage.
- Reason codes are tenant-configurable; "Other" always needs a note.
- Analytics: reveals per user per month in the quarterly access review (NFR-SEC-04).

### US-016 · Discharge a client

| Field | Value |
|---|---|
| Epic | EP-03 Client Records & Care Plans |
| Persona | PER-02 Marcus Hale (AG-COORD) |
| Priority | Must |
| Estimate | 3 points |
| Sprint / Release | S4 / R1 |
| Requirements | FR-CLI-07 |
| Business rules | BR-013 |
| Dependencies | US-022, US-049 |

**Story**
As a Care Coordinator, I want to discharge a client with a date and reason, so that future visits are cancelled, caregivers are told, and the record is kept read-only for the retention period.

**Acceptance criteria**

```gherkin
Scenario: US-016-AC1 Discharge with immediate effect
  Given C-10234 has Scheduled visits on 2026-09-21, 2026-09-23 and 2026-09-25
  When Marcus discharges C-10234 on 2026-09-21 with discharge date 2026-09-21 and reason "Moved to skilled nursing facility"
  Then the client status is "Discharged"
  And the visits on 2026-09-23 and 2026-09-25 are Cancelled with reason "Client discharged"
  And the visit on 2026-09-21 is not cancelled
  And each affected caregiver receives a notification without PHI within 1 minute

Scenario: US-016-AC2 Future-dated discharge
  Given today is 2026-10-03
  When Marcus discharges C-10234 with discharge date 2026-10-15
  Then the client stays "Active" until 2026-10-15 and becomes "Discharged" on 2026-10-16 at 00:00 America/New_York
  And visits after 2026-10-15 are cancelled now and the visit patterns end on 2026-10-15

Scenario: US-016-AC3 Visits already in progress or completed are untouched
  Given Rosa is clocked in to a visit for C-10234
  When Marcus discharges C-10234 with today's date
  Then the in-progress visit can still be clocked out, verified, paid and billed

Scenario Outline: US-016-AC4 Validate discharge data
  When Marcus discharges a client admitted on 2026-03-02 with <input>
  Then it is rejected with "<message>"

  Examples:
    | input                                    | message                                                  |
    | discharge date 2026-03-01                | The discharge date cannot be before the admission date.  |
    | no reason                                | Select a discharge reason.                               |

Scenario: US-016-AC5 Discharged records are read-only and retained
  Given C-10234 is Discharged
  When any user tries to edit the client's demographics or add a visit
  Then the change is rejected with "This client is discharged. The record is read-only."
  And the record cannot be deleted before the retention period of 7 years after discharge ends
```

**Notes**
- Readmission creates a new admission episode on the same client record; it is out of scope for R1 and handled by Customer Success on request.
- Seats: a discharged client still counts as an active seat in the cycle where they had a visit (BR-002).
- Retention defaults to 7 years and is configurable to the tenant's state requirement (BR-013).

## Related documents

- [Epics overview](../epics.md)
- [Story map](../story-map.md)
- [Software requirements specification](../../02-requirements/SRS.md)
- [Business rules catalog](../../02-requirements/business-rules.md)
- [Data classification and retention](../../03-design/data/data-classification-and-retention.md)
- [Data dictionary](../../03-design/data/data-dictionary.md)
- [State machines](../../03-design/diagrams/state-machines.md)
- [Wireframes index](../../03-design/wireframes/README.md)
- [Test cases](../../06-quality/test-cases.md)
