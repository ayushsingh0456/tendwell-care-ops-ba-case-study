# EP-09 Time Off & Holidays: user stories

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DEL-US-09 |
| Version | 1.2 |
| Status | Baselined |
| Owner | Business Analyst |
| Last updated | 2026-06-12 |
| Reviewers | Product Owner, Engineering Lead, QA Lead, Customer Success Lead |

## Purpose and scope

This file holds the user stories and acceptance criteria for EP-09. It covers time-off requests from the Caregiver app, short-notice flags, leave balances and accrual, the approver's impact view, reassignment of affected visits, and the tenant holiday calendar used by scheduling and payroll.

## Epic

| Field | Value |
|---|---|
| Epic ID | EP-09 |
| Name | Time Off & Holidays |
| Module | TOF |
| Goal | Let caregivers request time off in seconds and let Coordinators see and cover the impact before they approve, so that no client visit is silently dropped and payroll receives accurate PTO and holiday data. |
| Objectives | OBJ-01 EVV completeness (fewer Missed visits from uncovered absences); OBJ-02 Payroll preparation time (PTO and holidays arrive in the pay calculation automatically). |
| Business need | BN-09 |
| Release | R1 |

## Story list

| Story | Title | Persona | Priority | Points | Sprint |
|---|---|---|---|---|---|
| US-039 | Request time off | PER-01 Rosa Delgado (CG) | Must | 3 | S5 |
| US-040 | Approve time off and reassign affected visits | PER-02 Marcus Hale (AG-COORD) | Must | 5 | S5 |
| **Total** | | | | **8** | |

## Stories

### US-039 · Request time off

| Field | Value |
|---|---|
| Epic | EP-09 Time Off & Holidays |
| Persona | PER-01 Rosa Delgado (CG) |
| Priority | Must |
| Estimate | 3 points |
| Sprint / Release | S5 / R1 |
| Requirements | FR-TOF-01, FR-TOF-02, FR-TOF-04 |
| Business rules | BR-038, BR-040 |
| Dependencies | US-017 |

**Story**
As a caregiver, I want to request time off from the app and see my leave balance, so that I can plan my life without phoning the office and know what I have left.

**Acceptance criteria**

```gherkin
Scenario: US-039-AC1 Submit a PTO request
  Given today is 2026-09-14 and Rosa's PTO balance is 32.0 hours
  When she requests PTO from 2026-09-28 to 2026-09-29 with partial-day hours 4.0 on 2026-09-29 and note "Family event"
  Then the request is saved with status "Pending" and 12.0 hours requested
  And the Coordinators of her location are notified

Scenario Outline: US-039-AC2 Flag short-notice requests
  Given today is 2026-09-14
  When Rosa requests <leave type> starting <start date>
  Then the request is <flag>

  Examples:
    | leave type  | start date | flag                     |
    | PTO         | 2026-09-21 | not flagged              |
    | PTO         | 2026-09-20 | flagged "Short notice"   |
    | Unpaid      | 2026-09-16 | flagged "Short notice"   |
    | Bereavement | 2026-09-15 | flagged "Short notice"   |
    | Sick        | 2026-09-14 | not flagged              |

Scenario Outline: US-039-AC3 Accrue PTO from hours worked up to the cap
  Given Rosa's PTO balance is <balance> hours
  When a pay period with <worked> hours worked is calculated
  Then her PTO balance becomes <new balance> hours

  Examples:
    | balance | worked | new balance |
    | 32.0    | 45.0   | 33.5        |
    | 79.0    | 45.0   | 80.0        |
    | 80.0    | 60.0   | 80.0        |
    | 32.0    | 29.0   | 32.97       |

Scenario: US-039-AC4 Requests above the balance are allowed but flagged
  Given Rosa's PTO balance is 8.0 hours
  When she requests 16.0 hours of PTO
  Then the request is saved as "Pending" with the flag "Exceeds PTO balance by 8.0 hours" for the approver

Scenario: US-039-AC5 Cancel a request
  Given Rosa has a "Pending" request
  When she cancels it
  Then the status is "Cancelled" and the Coordinator is notified
  And a request that is already "Approved" can be cancelled only by the Coordinator
```

**Notes**
- Accrual uses hours worked, including paid travel, but not PTO hours taken; accrual is held to the second and shown to 2 decimals (29.0 hours accrues 0.9667, shown as 0.97).
- The accrual rate and cap are tenant-configurable; the defaults are 1 hour per 30 hours worked, capped at 80 hours (BR-040).
- Out of scope: leave policies per employment type (backlog); sick-leave accrual laws, which the agency configures as a separate leave type.

### US-040 · Approve time off and reassign affected visits

| Field | Value |
|---|---|
| Epic | EP-09 Time Off & Holidays |
| Persona | PER-02 Marcus Hale (AG-COORD) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S5 / R1 |
| Requirements | FR-TOF-03, FR-TOF-05 |
| Business rules | BR-039 |
| Dependencies | US-039, US-023, US-021 |

**Story**
As a Care Coordinator, I want to see which visits a time-off request affects before I decide, and have approved absences move those visits to Open Shifts, so that every client still gets a caregiver.

**Acceptance criteria**

```gherkin
Scenario: US-040-AC1 See the impact before deciding
  Given Rosa requested PTO from 2026-09-28 to 2026-09-29
  When Marcus opens the request
  Then he sees the 5 affected visits with date, time, client first name and last initial, and service
  And he sees Rosa's PTO balance and any "Short notice" or "Exceeds PTO balance" flag

Scenario: US-040-AC2 Approve and move affected visits to Open Shifts
  When Marcus approves the request
  Then the status is "Approved" with Marcus and the decision time recorded
  And the 5 affected visits move to Open Shifts and eligible caregivers are notified
  And Rosa is notified of the decision without PHI

Scenario: US-040-AC3 Decline with a reason
  When Marcus declines the request with reason "Two other aides already off that week"
  Then the status is "Declined" and the 5 visits stay assigned to Rosa
  And Rosa sees the reason in the app

Scenario: US-040-AC4 Approved time off blocks new assignments
  Given Rosa's PTO for 2026-09-28 is Approved
  When Marcus tries to assign Rosa to a visit on 2026-09-28
  Then the compliance check returns the hard block "Rosa Delgado has approved time off on 2026-09-28."

Scenario: US-040-AC5 Maintain the holiday calendar
  When Tom Brennan (AG-ADM) adds the holiday "Labor Day" on 2026-09-07
  Then the schedule board marks 2026-09-07 as a holiday
  And payroll applies the holiday multiplier to hours worked that day by holiday-eligible caregivers
  And a user without the AG-ADM role cannot add, edit or remove holidays

Scenario: US-040-AC6 Approve only for assigned locations
  Given Marcus is assigned only to "Lakemont North"
  When a caregiver from "Lakemont South" requests time off
  Then the request does not appear in Marcus's approval queue
  And a direct call to POST /v1/time-off-requests/{requestId}/decision returns 404
```

**Notes**
- FR-TOF-05 (holiday calendar) is configured by the Agency Administrator; it sits in this story because the calendar is set up and tested together with time-off approval.
- Partial-day requests affect only visits that overlap the requested hours.
- Analytics: share of affected visits re-covered before their start time; median decision time.

## Related documents

- [Epics overview](../epics.md)
- [Software requirements specification](../../02-requirements/SRS.md)
- [Business rules catalog](../../02-requirements/business-rules.md)
- [EP-05 Scheduling stories](EP-05-scheduling.md)
- [EP-10 Payroll stories](EP-10-payroll.md)
- [Test cases](../../06-quality/test-cases.md)
