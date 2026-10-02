# EP-05 Scheduling: user stories

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DEL-US-05 |
| Version | 1.2 |
| Status | Baselined |
| Owner | Business Analyst |
| Last updated | 2026-06-12 |
| Reviewers | Product Owner, Engineering Lead, QA Lead, UX Designer, Customer Success Lead |

## Purpose and scope

This file holds the user stories and acceptance criteria for EP-05. It covers recurring visit patterns, one-off visits, compliance checks, editing and cancelling visits, open shifts and the schedule board. Compliance checks are the main control for OBJ-05 and OBJ-06: they stop assignments that would break credential, authorization, exclusion, overlap or time-off rules before the visit exists.

## Epic

| Field | Value |
|---|---|
| Epic ID | EP-05 |
| Name | Scheduling |
| Module | SCH |
| Goal | Let Coordinators build and change compliant schedules quickly, with checks that stop unqualified, unauthorized or overlapping assignments before they happen and caregivers told of changes within a minute. |
| Objectives | OBJ-05 Credential lapses (to 0); OBJ-06 Authorization-overrun denials (to 1% or less); OBJ-01 EVV completeness (accurate schedules give EVV a visit to verify against). |
| Business need | BN-05 |
| Release | R1 |

## Story list

| Story | Title | Persona | Priority | Points | Sprint |
|---|---|---|---|---|---|
| US-020 | Create a recurring visit pattern | PER-02 Marcus Hale (AG-COORD) | Must | 8 | S3 |
| US-021 | See compliance checks before saving a visit | PER-02 Marcus Hale (AG-COORD) | Must | 8 | S3 |
| US-022 | Edit or cancel one visit or a series | PER-02 Marcus Hale (AG-COORD) | Must | 5 | S3 |
| US-023 | Claim an open shift | PER-01 Rosa Delgado (CG) | Should | 5 | S5 |
| US-024 | Use the schedule board | PER-02 Marcus Hale (AG-COORD) | Must | 5 | S3 |
| **Total** | | | | **31** | |

Shared test data: client C-10234 at 418 Birchwood Lane, Lakemont, OH 43999 with T1019 authorization PA-2026-55871 (480 units, 2026-09-01 to 2026-11-30); caregivers Rosa Delgado and E-2041 Maya Ortiz; location "Lakemont North"; time zone America/New_York.

## Stories

### US-020 · Create a recurring visit pattern

| Field | Value |
|---|---|
| Epic | EP-05 Scheduling |
| Persona | PER-02 Marcus Hale (AG-COORD) |
| Priority | Must |
| Estimate | 8 points |
| Sprint / Release | S3 / R1 |
| Requirements | FR-SCH-01, FR-SCH-07 |
| Business rules | BR-018 |
| Dependencies | US-013, US-017, US-049 |

**Story**
As a Care Coordinator, I want to set up a client's recurring visits once and have the system keep the next 8 weeks scheduled, so that I spend my time on exceptions instead of re-entering the same visits every week.

**Acceptance criteria**

```gherkin
Scenario: US-020-AC1 Materialize an open-ended pattern for 8 weeks
  Given today is 2026-09-04
  When Marcus creates a pattern for C-10234 with caregiver Rosa Delgado, service T1019 under PA-2026-55871, Monday, Wednesday and Friday 08:00 to 10:00, starting 2026-09-07 with no end date
  Then the horizon runs 8 weeks from 2026-09-07 to 2026-11-01
  And 24 visits are created with status "Scheduled", the first on 2026-09-07 and the last on 2026-10-30
  And each visit references the pattern and the authorization

Scenario: US-020-AC2 Extend the horizon nightly without duplicates
  Given the pattern above has visits up to 2026-10-30 and a horizon ending 2026-11-01
  When the nightly materialization job runs for 2026-09-08 and then runs again for the same date
  Then the horizon ends 2026-11-02 and exactly one new visit is created, on 2026-11-02
  And no visit is duplicated

Scenario: US-020-AC3 Respect the pattern end date
  When Marcus creates the same pattern with end date 2026-09-30
  Then exactly 11 visits are created, the last on 2026-09-30

Scenario: US-020-AC4 Editing a pattern changes only future, not-yet-started visits
  Given the pattern has visits from 2026-09-07 and today is 2026-09-11 at 08:30
  And Rosa is clocked in to the 2026-09-11 visit
  When Marcus changes the pattern time to 09:00 to 11:00 from 2026-09-11
  Then the 2026-09-07 and 2026-09-09 visits and the in-progress 2026-09-11 visit are unchanged
  And visits from 2026-09-14 onwards are 09:00 to 11:00

Scenario: US-020-AC5 Notify the caregiver within 1 minute without PHI
  When the pattern above is saved at 14:20:00
  Then Rosa receives one notification by 14:21:00 saying "You have 24 new visits. Open Tendwell to view your schedule."
  And the notification contains no client name or address

Scenario: US-020-AC6 Keep local times across a DST change
  Given the pattern materializes visits on 2026-10-30 and 2026-11-02
  When daylight saving time ends on 2026-11-01
  Then both visits show 08:00 to 10:00 America/New_York
  And both are stored in UTC with the correct offset (12:00Z and 13:00Z)
```

**Notes**
- The horizon is 8 weeks (56 days, inclusive) from the later of today and the pattern start date.
- A pattern can be saved without a caregiver; its visits are created as open shifts (US-023).
- Every materialized occurrence runs the compliance checks of US-021; conflicting occurrences are listed by date before saving.
- UX: recurring-visit creation is the scenario used for NFR-USE-02 (90% of new Coordinators complete it unaided after 30 minutes of training).
- Nightly materialization is single-flight (ADR-003).

### US-021 · See compliance checks before saving a visit

| Field | Value |
|---|---|
| Epic | EP-05 Scheduling |
| Persona | PER-02 Marcus Hale (AG-COORD) |
| Priority | Must |
| Estimate | 8 points |
| Sprint / Release | S3 / R1 |
| Requirements | FR-SCH-03 |
| Business rules | BR-009, BR-010, BR-014, BR-016, BR-017, BR-039 |
| Dependencies | US-012, US-013, US-018 |

**Story**
As a Care Coordinator, I want every visit I create or edit checked against credentials, authorizations, exclusions, overlaps, travel time and approved time off, so that I catch problems before a caregiver is sent or a claim is denied.

**Acceptance criteria**

```gherkin
Scenario Outline: US-021-AC1 Classify each check as a hard block or a warning
  Given Rosa Delgado is the proposed caregiver for a visit to C-10234 on 2026-09-23 from 10:30 to 12:00
  And <condition>
  When Marcus saves the visit
  Then the check "<check>" returns "<result>"

  Examples:
    | condition                                                                                   | check               | result     |
    | Rosa has another visit on 2026-09-23 from 09:00 to 11:00                                    | Caregiver overlap   | Hard block |
    | Rosa's previous visit ends at 10:20 at a different address                                  | Travel buffer       | Warning    |
    | Rosa's previous visit ends at 10:15 at a different address                                  | Travel buffer       | Pass       |
    | Rosa's Blocking CPR certification expired on 2026-09-22                                     | Blocking credential | Hard block |
    | C-10234 has Rosa recorded as Excluded                                                       | Client exclusion    | Hard block |
    | the only T1019 authorization ended on 2026-09-22                                            | Authorization       | Hard block |
    | the only active authorization is for service line ADULT_DAY                                 | Authorization       | Hard block |
    | the T1019 authorization has 4 units remaining and the visit needs 6                         | Remaining units     | Warning    |
    | Rosa has approved time off on 2026-09-23                                                    | Time off            | Hard block |

Scenario: US-021-AC2 Return all results in one response
  Given a proposed visit fails the overlap check and the remaining-units check
  When Marcus selects "Check" (POST /v1/visits/compliance-checks)
  Then both results are returned together with a plain-language message and a suggested fix for each
  And the dry run creates no visit

Scenario: US-021-AC3 Save past a warning only with an override reason
  Given the only result is the warning "Exceeds remaining authorized units by 2"
  When Marcus saves without a reason
  Then the save is rejected with "Enter a reason to schedule beyond the remaining authorized units."
  When he enters "Reauthorization requested on 2026-09-18" and saves
  Then the visit is saved and the override reason, Marcus and the timestamp are audited

Scenario: US-021-AC4 Nobody can override a hard block
  Given a proposed visit returns the hard block "Client exclusion"
  When Tom Brennan (AG-ADM) tries to save it
  Then the save is rejected and no override option is shown

Scenario: US-021-AC5 Checks rerun on every edit
  Given a saved visit passed all checks
  When Marcus moves it to a date on which Rosa has approved time off
  Then the edit is rejected with the hard block "Time off"

Scenario: US-021-AC6 Checks are fast enough for interactive use
  Given a tenant with 250 caregivers and 4,000 visits in the 8-week horizon
  When Marcus runs a dry-run check for a single visit
  Then results return within 800 ms at p95
```

**Notes**
- The travel buffer warning applies only to consecutive visits at different addresses with less than 15 minutes between them (BR-016); exactly 15 minutes passes.
- Units for the remaining-units check use the scheduled duration and the BR-047 rounding rule: 90 minutes is 6 units.
- Every message follows NFR-USE-03: problem plus fix, no raw error codes.
- Analytics: hard blocks and overrides per check type per week; a rising override rate on remaining units is a signal to chase reauthorizations.

### US-022 · Edit or cancel one visit or a series

| Field | Value |
|---|---|
| Epic | EP-05 Scheduling |
| Persona | PER-02 Marcus Hale (AG-COORD) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S3 / R1 |
| Requirements | FR-SCH-02, FR-SCH-04 |
| Business rules | BR-018, BR-019 |
| Dependencies | US-020, US-021 |

**Story**
As a Care Coordinator, I want to add one-off visits and change or cancel a single occurrence or the rest of a series, so that the schedule matches what the client actually needs this week.

**Acceptance criteria**

```gherkin
Scenario: US-022-AC1 Create a one-off visit
  When Marcus creates a one-off visit for C-10234 with Rosa on Saturday 2026-09-19 from 10:00 to 12:00 under PA-2026-55871
  Then the visit is saved with status "Scheduled" and no pattern
  And the compliance checks run before it is saved

Scenario: US-022-AC2 Edit only this occurrence
  Given the Monday-Wednesday-Friday pattern for C-10234
  When Marcus moves the 2026-09-23 visit to 13:00 to 15:00 and chooses "This visit only"
  Then only the 2026-09-23 visit changes
  And the pattern and all other visits are unchanged

Scenario: US-022-AC3 Edit this and following occurrences
  When Marcus changes the caregiver to Maya Ortiz from 2026-09-28 and chooses "This and following visits"
  Then the original pattern ends on 2026-09-27
  And a new pattern starts on 2026-09-28 with Maya
  And visits before 2026-09-28 still show Rosa

Scenario Outline: US-022-AC4 Cancellation requires a reason code
  When Marcus cancels the 2026-09-25 visit with reason "<reason>" and note "<note>"
  Then the result is "<result>"

  Examples:
    | reason                 | note                          | result                                                         |
    | Client hospitalized    |                               | Cancelled                                                      |
    | Client request         |                               | Cancelled                                                      |
    | Caregiver unavailable  |                               | Cancelled and offered as an open shift                         |
    | Other                  | Family visiting from Toledo   | Cancelled                                                      |
    | Other                  |                               | Rejected: add a note when the reason is Other                  |
    | (none)                 |                               | Rejected: select a cancellation reason                         |

Scenario Outline: US-022-AC5 Allowed changes depend on visit status
  Given a visit with status "<status>"
  When Marcus tries to <action>
  Then the result is "<result>"

  Examples:
    | status     | action          | result                                                                       |
    | Scheduled  | change the time | Saved                                                                        |
    | InProgress | cancel it       | Rejected: the caregiver is clocked in; resolve the visit after clock-out     |
    | Completed  | change the time | Rejected: use a time correction in the exception queue                       |
    | Verified   | cancel it       | Rejected: a verified visit cannot be cancelled                               |
    | Missed     | cancel it       | Rejected: a missed visit stays on record; add a note instead                 |
```

**Notes**
- Caregiver notifications for changed or cancelled visits follow FR-SCH-07 (implemented in US-020): within 1 minute and without PHI.
- "Caregiver unavailable" automatically republishes the visit as an open shift; other reasons do not.
- Time corrections for completed visits are handled in US-029 so that punches stay append-only (BR-026).

### US-023 · Claim an open shift

| Field | Value |
|---|---|
| Epic | EP-05 Scheduling |
| Persona | PER-01 Rosa Delgado (CG) |
| Priority | Should |
| Estimate | 5 points |
| Sprint / Release | S5 / R1 |
| Requirements | FR-SCH-05 |
| Business rules | BR-014, BR-016, BR-017 |
| Dependencies | US-021, US-049 |

**Story**
As a caregiver, I want to see and claim open shifts I am eligible for, so that I can pick up extra hours and clients are not left without a visit.

**Acceptance criteria**

```gherkin
Scenario: US-023-AC1 Claim an eligible open shift
  Given an open shift for a client in "Lakemont North" on 2026-09-24 from 14:00 to 16:00
  And Rosa works in "Lakemont North", has no overlapping visit, no expired Blocking credential and is not excluded by the client
  When Rosa opens Open Shifts and taps "Claim"
  Then the visit is assigned to Rosa with status "Scheduled"
  And the shift disappears from the Open Shifts list of every other caregiver

Scenario: US-023-AC2 First committed claim wins
  Given Rosa and Maya both see the same open shift
  When both tap "Claim" within the same second and Rosa's claim is committed first
  Then the visit is assigned to Rosa
  And Maya sees "This shift was just taken. Pull to refresh for other open shifts."

Scenario Outline: US-023-AC3 Ineligible caregivers cannot claim
  Given <condition>
  Then the open shift is not listed for Rosa
  And a direct claim request returns 409 with the reason "<reason>"

  Examples:
    | condition                                                       | reason                                        |
    | Rosa has a visit from 13:30 to 15:00 on 2026-09-24              | You already have a visit at this time.        |
    | Rosa's Blocking CPR certification expired on 2026-09-20         | Your CPR certification has expired.           |
    | the client has Rosa recorded as Excluded                        | You are not eligible for this shift.          |

Scenario: US-023-AC4 Coordinator confirmation when the tenant enables it
  Given the tenant setting "Coordinator confirms open-shift claims" is On
  When Rosa claims the open shift
  Then her claim shows "Pending confirmation" and the shift is hidden from other caregivers
  When Marcus confirms the claim
  Then the visit is assigned to Rosa and she is notified
  When instead Marcus declines it with a reason
  Then the shift returns to Open Shifts and Rosa is notified

Scenario: US-023-AC5 Travel buffer is a warning, not a block
  Given Rosa's previous visit ends at 13:50 at a different address
  When she claims the 14:00 open shift
  Then the claim succeeds
  And the visit shows the travel buffer warning on the Coordinator's schedule board
```

**Notes**
- Coordinator confirmation (AC4) was added by CR-002 in SRS v1.1; the story was re-estimated from 3 to 5 points.
- The exclusion reason is never shown to the caregiver; the message is deliberately generic.
- Analytics: time from publish to claim, and share of open shifts filled by claim versus by the Coordinator.

### US-024 · Use the schedule board

| Field | Value |
|---|---|
| Epic | EP-05 Scheduling |
| Persona | PER-02 Marcus Hale (AG-COORD) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S3 / R1 |
| Requirements | FR-SCH-06 |
| Business rules | BR-019 |
| Dependencies | US-020 |

**Story**
As a Care Coordinator, I want a day and week schedule board with filters and clear visit status, so that I can spot gaps and problems for my roughly 70 clients at a glance.

**Acceptance criteria**

```gherkin
Scenario: US-024-AC1 Filter the board
  Given Marcus is assigned to "Lakemont North"
  When he opens the week view for 2026-09-21 to 2026-09-27 and filters by service line HOME_VISIT and caregiver Rosa Delgado
  Then only Rosa's HOME_VISIT visits in "Lakemont North" for that week are shown
  And the filters combine with AND and stay applied when he switches to the day view

Scenario Outline: US-024-AC2 Show each status with color and text
  Given a visit with status "<status>"
  Then the visit card shows the label "<label>" and its status color
  And the status is also conveyed by the label, so color is not the only indicator

  Examples:
    | status      | label        |
    | Scheduled   | Scheduled    |
    | InProgress  | In progress  |
    | Completed   | Completed    |
    | NeedsReview | Needs review |
    | Verified    | Verified     |
    | Cancelled   | Cancelled    |
    | Missed      | Missed       |

Scenario: US-024-AC3 Mark a visit Missed after its scheduled end
  Given a visit from 08:00 to 10:00 has no clock-in
  When the time reaches 10:00
  Then the visit shows "Missed" on the board by 10:05

Scenario: US-024-AC4 Load a busy week fast
  Given the week view contains 500 visits
  When Marcus opens it
  Then the board is fully rendered within 2.5 s at p95

Scenario: US-024-AC5 Show only the minimum necessary
  When Marcus hovers over a visit card
  Then he sees client name, client number, caregiver, times and status
  And no service address, diagnosis or Medicaid ID is shown on the board
```

**Notes**
- Unassigned open shifts are shown in a separate lane at the top of each day.
- Accessibility: the board is keyboard navigable and meets WCAG 2.2 AA, including 1.4.1 Use of Color and 2.4.11 Focus Not Obscured.
- Out of scope: drag-and-drop reassignment (R2 candidate); route optimization.

## Related documents

- [Epics overview](../epics.md)
- [Story map](../story-map.md)
- [Software requirements specification](../../02-requirements/SRS.md)
- [Business rules catalog](../../02-requirements/business-rules.md)
- [Process flows](../../03-design/diagrams/process-flows.md)
- [State machines](../../03-design/diagrams/state-machines.md)
- [Wireframes index](../../03-design/wireframes/README.md)
- [Change request log](../change-request-log.md)
- [Test cases](../../06-quality/test-cases.md)
