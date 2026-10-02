# EP-08 Care Documentation & Client Incidents: user stories

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DEL-US-08 |
| Version | 1.2 |
| Status | Baselined |
| Owner | Business Analyst |
| Last updated | 2026-06-12 |
| Reviewers | Product Owner, Clinical SME (RN advisor), Compliance and Privacy Officer, QA Lead |

## Purpose and scope

This file holds the user stories and acceptance criteria for EP-08. It covers visit notes that lock 24 hours after clock-out, signed addenda, field reporting of client incidents, immediate notification of serious incidents, investigation and closure, and tracking of external reporting deadlines. Deadlines are tenant-configurable defaults; the agency remains responsible for meeting its state's reporting rules.

## Epic

| Field | Value |
|---|---|
| Epic ID | EP-08 |
| Name | Care Documentation & Client Incidents |
| Module | DOC |
| Goal | Give every visit a tamper-evident note and every client incident a closed loop, from field report to investigation, corrective action and on-time external report. |
| Objectives | OBJ-01 EVV completeness (visits whose care plan requires a note cannot complete without one); compliance guardrail: 100% of reportable incidents have an external report reference before their deadline. |
| Business need | BN-08 |
| Release | R1 |

## Story list

| Story | Title | Persona | Priority | Points | Sprint |
|---|---|---|---|---|---|
| US-036 | Write a visit note that locks after 24 hours | PER-01 Rosa Delgado (CG) | Must | 3 | S3 |
| US-037 | Report a client incident from the field | PER-01 Rosa Delgado (CG) | Must | 5 | S5 |
| US-038 | Investigate and close a client incident | PER-03 Priya Raman, RN (AG-SUPV) | Must | 5 | S5 |
| **Total** | | | | **13** | |

## Stories

### US-036 · Write a visit note that locks after 24 hours

| Field | Value |
|---|---|
| Epic | EP-08 Care Documentation & Client Incidents |
| Persona | PER-01 Rosa Delgado (CG) |
| Priority | Must |
| Estimate | 3 points |
| Sprint / Release | S3 / R1 |
| Requirements | FR-DOC-01, FR-DOC-02 |
| Business rules | BR-035 |
| Dependencies | US-025 |

**Story**
As a caregiver, I want to write a short structured visit note with a narrative and fix it for a day if needed, so that the record is complete and, once locked, cannot be quietly changed.

**Acceptance criteria**

```gherkin
Scenario: US-036-AC1 Write and submit a visit note
  Given Rosa is clocked in to the 08:00 visit for C-10234
  When she records mood "Calm", appetite "Ate half of breakfast", skin "No concerns", a change in condition "None" and the narrative "Client walked to the mailbox with the walker. Reported mild knee pain."
  And she clocks out at 09:58
  Then the note is linked to the visit with status "Submitted" and Rosa as author

Scenario Outline: US-036-AC2 The note locks 24 hours after clock-out
  Given Rosa clocked out on 2026-09-15 at 10:00
  When she edits the note at <time>
  Then the result is "<result>"

  Examples:
    | time             | result                                                         |
    | 2026-09-16 09:59 | saved, with the previous text kept in the note history         |
    | 2026-09-16 10:00 | rejected: "This note is locked. Add an addendum instead."      |

Scenario: US-036-AC3 Add a signed addendum to a locked note
  Given the note is "Locked"
  When Rosa adds the addendum "Correction: client used the cane, not the walker." and re-enters her PIN to sign
  Then the addendum is saved with Rosa as author, a timestamp and her electronic signature
  And the original note text is unchanged and shown above the addendum

Scenario Outline: US-036-AC4 Who can add an addendum
  Given the note is "Locked"
  When a user with role <role> tries to add an addendum
  Then the result is "<result>"

  Examples:
    | role                             | result    |
    | CG (the note's author)           | allowed   |
    | AG-SUPV                          | allowed   |
    | CG (another caregiver)           | rejected  |
    | AG-COORD                         | rejected  |

Scenario: US-036-AC5 Draft notes survive loss of signal
  Given Rosa has no connectivity
  When she writes the note and clocks out
  Then the note is queued with the clock-out punch and submitted on sync
  And the 24-hour lock is measured from the clock-out punch time, not the sync time
```

**Notes**
- The lock is enforced by a scheduled job and checked again on every write, so an edit cannot slip through between job runs.
- UX: structured fields are pick lists with a free-text "Other"; the narrative has speech-to-text from the phone keyboard.
- Out of scope: client or family signature on the visit note.

### US-037 · Report a client incident from the field

| Field | Value |
|---|---|
| Epic | EP-08 Care Documentation & Client Incidents |
| Persona | PER-01 Rosa Delgado (CG) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S5 / R1 |
| Requirements | FR-DOC-03, FR-DOC-04 |
| Business rules | BR-036, BR-053 |
| Dependencies | US-050 |

**Story**
As a caregiver, I want to report a client incident from my phone while the details are fresh, so that the nurse and the agency can act at once and nothing is lost on paper.

**Acceptance criteria**

```gherkin
Scenario: US-037-AC1 Report a fall with photos
  Given Rosa is on a visit for C-10234
  When she reports category "Fall", severity "Medium", occurred 2026-09-15 08:40, place "Bathroom", description, people involved "Client only", immediate actions "Helped client to chair, checked for injuries, none visible" and 2 photos taken in the app
  Then the incident is saved with status "Reported" and linked to the visit
  And the photos are stored encrypted and are not saved to the phone's photo gallery
  And the incident appears in the Clinical Supervisor's incident queue

Scenario Outline: US-037-AC2 Notify immediately for serious incidents
  When Rosa reports an incident with category "<category>" and severity "<severity>"
  Then the Clinical Supervisor and the Agency Administrator <notification>

  Examples:
    | category              | severity | notification                                            |
    | Fall                  | High     | are notified immediately as an urgent event             |
    | SuspectedAbuseNeglect | Low      | are notified immediately as an urgent event             |
    | Fall                  | Medium   | see it in the queue and receive a standard notification |
    | PropertyDamage        | Low      | see it in the queue and receive a standard notification |

Scenario: US-037-AC3 Urgent incident notifications bypass quiet hours
  Given the time is 23:40, inside quiet hours
  When Rosa reports category "SuspectedAbuseNeglect"
  Then Priya and Tom receive push and SMS notifications within 1 minute
  And the notification text is "Urgent: a client incident needs review. Sign in to Tendwell." with no client name, initials or category

Scenario: US-037-AC4 Start the deadline clock for suspected abuse or neglect
  When Rosa reports category "SuspectedAbuseNeglect" that occurred 2026-09-14 13:00
  Then the incident is flagged reportable with report deadline 2026-09-15 13:00

Scenario: US-037-AC5 Report while offline
  Given Rosa has no connectivity
  When she reports a High severity fall
  Then the incident is queued on the device with its photos, encrypted
  And it is submitted and the urgent notifications are sent as soon as the phone reconnects
  And the incident keeps its original occurred and reported times

Scenario: US-037-AC6 Required fields
  When Rosa submits an incident without a description or immediate actions
  Then it is rejected with "Describe what happened and what you did right away."
```

**Notes**
- Notification text was tightened by CR-006 after INC-2026-015: no client name, initials or incident category in any SMS, push or email body.
- Office staff (AG-COORD) can report incidents from the Agency Web App with the same fields.
- Up to 5 photos per incident, 10 MB each; images are scaled on the device before upload to work at 400 kbps (NFR-MOB-01).

### US-038 · Investigate and close a client incident

| Field | Value |
|---|---|
| Epic | EP-08 Care Documentation & Client Incidents |
| Persona | PER-03 Priya Raman, RN (AG-SUPV) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S5 / R1 |
| Requirements | FR-DOC-05, FR-DOC-06 |
| Business rules | BR-036, BR-037 |
| Dependencies | US-037 |

**Story**
As a Clinical Supervisor, I want to investigate each incident, assign corrective actions and track external reporting deadlines, so that every incident is closed properly and reported on time.

**Acceptance criteria**

```gherkin
Scenario: US-038-AC1 Record the investigation and corrective actions
  Given the fall reported by Rosa is "Reported"
  When Priya records investigation notes, root cause "Wet floor, no bath mat" and the corrective action "Install non-slip bath mat" owned by Marcus Hale and due 2026-09-18
  Then the incident status is "ActionsOpen"
  And Marcus sees the action on his task list

Scenario Outline: US-038-AC2 Close only when every action is Done or Waived
  Given the incident has 2 corrective actions with statuses <statuses>
  When Priya closes the incident
  Then the result is "<result>"

  Examples:
    | statuses                                          | result                                                         |
    | Done, Done                                        | Closed                                                         |
    | Done, Waived with reason "Family declined mat"    | Closed                                                         |
    | Done, Open                                        | rejected: "Complete or waive every corrective action first."   |
    | Done, Waived without a reason                     | rejected: "Enter a reason for each waived action."             |

Scenario: US-038-AC3 Only a Clinical Supervisor can close
  Given Tom Brennan holds only the AG-ADM role
  When he calls POST /v1/client-incidents/{incidentId}/close
  Then the request returns 403

Scenario Outline: US-038-AC4 Alert at 50% and 90% of the reporting deadline
  Given an incident of type <type> occurred 2026-09-14 13:00 and is flagged reportable with no external reference
  Then Priya and Tom are alerted at <alert 50> and at <alert 90>
  And the report deadline is <deadline>

  Examples:
    | type                         | deadline         | alert 50         | alert 90         |
    | Suspected abuse or neglect   | 2026-09-15 13:00 | 2026-09-15 01:00 | 2026-09-15 10:36 |
    | Serious injury               | 2026-09-15 13:00 | 2026-09-15 01:00 | 2026-09-15 10:36 |
    | Medication error with harm   | 2026-09-17 13:00 | 2026-09-16 01:00 | 2026-09-17 05:48 |

Scenario: US-038-AC5 Recording the external report stops deadline alerts
  Given a reportable incident with deadline 2026-09-15 13:00
  When Priya records external reference "LKM-APS-2026-0912" at 2026-09-15 09:15
  Then no 90% alert is sent
  And the incident shows "Reported externally 2026-09-15 09:15"

Scenario: US-038-AC6 Use the tenant's state deadline when configured
  Given the tenant set the deadline for "Medication error with harm" to 48 hours
  When a medication error with harm occurred 2026-09-14 13:00 is flagged reportable
  Then the report deadline is 2026-09-16 13:00
```

**Notes**
- The Supervisor flags an incident reportable and chooses the reporting type (Suspected abuse or neglect, Serious injury, Medication error with harm); for category SuspectedAbuseNeglect the flag is set automatically at report time (US-037).
- The deadline alert goes to the Supervisor and the Agency Administrator and is urgent (BR-053).
- Out of scope: electronic submission to state incident systems.

## Related documents

- [Epics overview](../epics.md)
- [Change request log](../change-request-log.md)
- [Software requirements specification](../../02-requirements/SRS.md)
- [Business rules catalog](../../02-requirements/business-rules.md)
- [Compliance mapping](../../02-requirements/compliance-mapping.md)
- [State machines](../../03-design/diagrams/state-machines.md)
- [INC-2026-015 Escalation email to a deactivated user](../../07-operations/incidents/INC-2026-015-escalation-email-to-deactivated-user.md)
- [Test cases](../../06-quality/test-cases.md)
