# EP-04 Caregiver Workforce & Credentials: user stories

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DEL-US-04 |
| Version | 1.2 |
| Status | Baselined |
| Owner | Business Analyst |
| Last updated | 2026-06-12 |
| Reviewers | Product Owner, Engineering Lead, QA Lead, Customer Success Lead |

## Purpose and scope

This file holds the user stories and acceptance criteria for EP-04. It covers caregiver profiles and app invitations, deactivation, credential tracking with Blocking and Advisory types, expiry reminders, and effective-dated pay profiles. Credential status feeds the scheduling compliance checks (US-021) and pay profiles feed payroll (US-041).

## Epic

| Field | Value |
|---|---|
| Epic ID | EP-04 |
| Name | Caregiver Workforce & Credentials |
| Module | WRK |
| Goal | Keep an accurate caregiver roster with current credentials and effective-dated pay profiles, so that only qualified staff are scheduled and everyone is paid at the right rate. |
| Objectives | OBJ-05 Credential lapses (23 instances per quarter to 0); OBJ-02 Payroll preparation time (correct pay profiles remove manual rate lookups). |
| Business need | BN-04 |
| Release | R1 |

## Story list

| Story | Title | Persona | Priority | Points | Sprint |
|---|---|---|---|---|---|
| US-017 | Onboard a caregiver and invite them to the app | PER-02 Marcus Hale (AG-COORD) | Must | 5 | S2 |
| US-018 | Track caregiver credentials and expiry | PER-02 Marcus Hale (AG-COORD) | Must | 5 | S2 |
| US-019 | Maintain an effective-dated pay profile | PER-04 Denise Carter (AG-FIN) | Must | 3 | S2 |
| **Total** | | | | **13** | |

Shared test data: caregiver E-2041 Maya Ortiz (`maya.ortiz@example.com`, +1-614-555-0163), caregiver Rosa Delgado (`rosa.delgado@example.com`, +1-614-555-0108), location "Lakemont North".

## Stories

### US-017 · Onboard a caregiver and invite them to the app

| Field | Value |
|---|---|
| Epic | EP-04 Caregiver Workforce & Credentials |
| Persona | PER-02 Marcus Hale (AG-COORD) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S2 / R1 |
| Requirements | FR-WRK-01, FR-WRK-06 |
| Business rules | None |
| Dependencies | US-009 |

**Story**
As a Care Coordinator, I want to create a caregiver profile and send the mobile app invitation in one step, so that new hires can receive visits on their first day; and when someone leaves, their access ends at once without losing visit data.

**Acceptance criteria**

```gherkin
Scenario: US-017-AC1 Create a caregiver profile and send the invitation
  When Marcus creates caregiver "Maya Ortiz" with employee number "E-2041", email "maya.ortiz@example.com", phone "+1-614-555-0163", employment type "FullTime", hire date 2026-02-16, location "Lakemont North", skills "Hoyer lift" and languages "English, Spanish"
  Then the caregiver is saved with status "Active" and a linked user with status "Invited"
  And an invitation is sent by SMS and email with a single-use link to install the app and set a password
  And neither message contains client information

Scenario Outline: US-017-AC2 Reject duplicate identifiers
  Given caregiver E-2041 exists with email "maya.ortiz@example.com"
  When Marcus creates a caregiver with <duplicate>
  Then it is rejected with "<message>"

  Examples:
    | duplicate                               | message                                                       |
    | employee number "E-2041"                | Employee number E-2041 is already used by another caregiver.  |
    | email "MAYA.ORTIZ@example.com"          | This email is already used by another user in your agency.    |

Scenario: US-017-AC3 Resend the invitation
  Given Maya has not accepted her invitation
  When Marcus selects "Resend invitation"
  Then a new link is sent and the earlier link stops working

Scenario: US-017-AC4 Deactivate a caregiver
  Given Maya has 6 future Scheduled visits and is signed in on her phone
  When Tom Brennan (AG-ADM) deactivates Maya with reason "Resigned" effective immediately
  Then her sessions and refresh tokens are revoked and her next API call returns 401
  And her 6 future visits move to the Open Shifts queue with the Coordinator notified
  And the caregiver status is "Inactive" and the user status is "Deactivated"

Scenario: US-017-AC5 Keep offline punches captured before deactivation
  Given Maya captured a clock-out offline at 16:02 and was deactivated at 16:30
  When her phone reconnects at 17:10
  Then the sync accepts punches captured before 16:30 from her registered device
  And the app then wipes its local data and signs out
  And punches captured after 16:30 are rejected and reported to the Coordinator

Scenario: US-017-AC6 Only Agency Administrators can deactivate
  Given Marcus holds only the AG-COORD role
  When he opens Maya's profile
  Then no Deactivate action is shown
  And a direct call to POST /v1/caregivers/{caregiverId}/deactivate returns 403
```

**Notes**
- FR-WRK-06 (deactivation) sits in this story because invitation and deactivation are two ends of the same account lifecycle. Per FR-WRK-06 the actor for deactivation is the Agency Administrator, not the Coordinator.
- A visit in progress at deactivation is not reassigned; it is flagged for Coordinator review.
- Remote wipe on deactivation implements NFR-MOB-02.
- Out of scope: background-check and I-9 workflows (handled outside Tendwell in R1).

### US-018 · Track caregiver credentials and expiry

| Field | Value |
|---|---|
| Epic | EP-04 Caregiver Workforce & Credentials |
| Persona | PER-02 Marcus Hale (AG-COORD) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S2 / R1 |
| Requirements | FR-WRK-02, FR-WRK-03, FR-WRK-04 |
| Business rules | BR-014 |
| Dependencies | US-017, US-049 |

**Story**
As a Care Coordinator, I want each caregiver's credentials tracked with automatic status and reminders, so that nobody is scheduled with an expired blocking credential.

**Acceptance criteria**

```gherkin
Scenario: US-018-AC1 Record a credential with its document
  Given the credential type "CPR certification" is Blocking with a validity of 24 months
  When Marcus records Maya's CPR certification issued 2025-11-02 expiring 2027-11-02 and uploads the certificate PDF
  Then the credential is saved with status "Valid"
  And the document is stored encrypted and opened only through a short-lived link

Scenario Outline: US-018-AC2 Recompute status daily
  Given today is 2026-10-03 and the nightly status job has run
  When a credential expires on <expiry date>
  Then its status is "<status>"

  Examples:
    | expiry date | status   |
    | 2026-11-03  | Valid    |
    | 2026-11-02  | Expiring |
    | 2026-10-03  | Expiring |
    | 2026-10-02  | Expired  |

Scenario Outline: US-018-AC3 Send reminders 30, 14 and 1 days before expiry
  Given Maya's TB screening expires on 2026-11-02
  When the reminder job runs on <run date>
  Then a reminder is <sent> to Maya and to the Coordinators of "Lakemont North"

  Examples:
    | run date   | sent     |
    | 2026-10-03 | sent     |
    | 2026-10-04 | not sent |
    | 2026-10-19 | sent     |
    | 2026-11-01 | sent     |

Scenario: US-018-AC4 Expired blocking credential blocks new assignments
  Given Maya's Blocking "CPR certification" expired on 2026-10-02
  And she has 4 future visits
  When Marcus tries to assign Maya to a new visit
  Then the compliance check returns a hard block "Maya Ortiz has an expired CPR certification."
  And her 4 future visits are flagged "Credential expired" on the schedule board

Scenario: US-018-AC5 Expired advisory credential only warns
  Given the credential type "Driver's license" is Advisory and Maya's expired on 2026-10-02
  When Marcus assigns Maya to a new visit
  Then the compliance check returns a warning and the visit can be saved

Scenario: US-018-AC6 Renewal clears flags and stops reminders
  Given Maya's CPR certification is Expired and her future visits are flagged
  When Marcus records a renewed CPR certification expiring 2028-10-05
  Then the credential status is "Valid", the flags are removed and no further reminders are sent for the old credential
```

**Notes**
- Reminders are deduplicated by credential, recipient and reminder day (BR-055), so a rerun of the job sends nothing new.
- Caregivers can view their own credentials and expiry dates in the app; uploads by caregivers are out of scope for R1.
- Analytics: count of caregivers with an Expired Blocking credential and at least one future visit is the leading indicator for OBJ-05 (target 0).

### US-019 · Maintain an effective-dated pay profile

| Field | Value |
|---|---|
| Epic | EP-04 Caregiver Workforce & Credentials |
| Persona | PER-04 Denise Carter (AG-FIN) |
| Priority | Must |
| Estimate | 3 points |
| Sprint / Release | S2 / R1 |
| Requirements | FR-WRK-05 |
| Business rules | BR-015 |
| Dependencies | US-017 |

**Story**
As a Billing & Payroll Specialist, I want each caregiver's pay rate and eligibility flags kept with effective dates, so that every visit is paid at the rate that applied on the visit date.

**Acceptance criteria**

```gherkin
Scenario: US-019-AC1 Create a pay profile
  When Denise sets Maya's (E-2041) pay profile effective 2026-01-01: pay type Hourly, base rate $19.50, overtime-eligible Yes, holiday-eligible Yes, mileage-eligible Yes
  Then the profile is saved and shown as current

Scenario Outline: US-019-AC2 Pay visits at the rate effective on the visit date
  Given Maya's rate is $19.50 effective 2026-01-01
  And Denise added a rate of $20.25 effective 2026-09-14 on 2026-09-20
  When pay is calculated for a visit on <visit date>
  Then the base rate used is <rate>

  Examples:
    | visit date | rate   |
    | 2026-09-13 | $19.50 |
    | 2026-09-14 | $20.25 |

Scenario: US-019-AC3 New profiles close the previous one
  Given Maya's current profile is effective from 2026-01-01 with no end date
  When Denise adds a profile effective 2026-09-14
  Then the earlier profile ends on 2026-09-13
  And no date is covered by two profiles

Scenario: US-019-AC4 Retroactive change in a locked period creates adjustments
  Given the pay period 2026-08-31 to 2026-09-13 is exported and locked
  When Denise adds a profile with rate $20.25 effective 2026-09-07
  Then the locked period's lines are unchanged
  And adjustment lines for the rate difference on visits from 2026-09-07 to 2026-09-13 are created in the next open period

Scenario: US-019-AC5 Restrict who can see and change pay rates
  Given Marcus holds only the AG-COORD role
  When he opens Maya's profile
  Then the Pay tab is not shown
  And a direct call to PUT /v1/caregivers/{caregiverId}/pay-profiles returns 403
  And every change Denise makes is audited with before and after values
```

**Notes**
- Overtime eligibility means the caregiver is non-exempt under the FLSA; the agency remains responsible for classifying employees correctly.
- Adjustments in AC4 are produced by US-043.
- Out of scope: client-specific pay rates and shift differentials (backlog).

## Related documents

- [Epics overview](../epics.md)
- [Story map](../story-map.md)
- [Software requirements specification](../../02-requirements/SRS.md)
- [Business rules catalog](../../02-requirements/business-rules.md)
- [Data dictionary](../../03-design/data/data-dictionary.md)
- [EP-05 Scheduling stories](EP-05-scheduling.md)
- [EP-10 Payroll stories](EP-10-payroll.md)
- [Test cases](../../06-quality/test-cases.md)
