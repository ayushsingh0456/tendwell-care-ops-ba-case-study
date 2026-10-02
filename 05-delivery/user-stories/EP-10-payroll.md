# EP-10 Payroll Preparation: user stories

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DEL-US-10 |
| Version | 1.2 |
| Status | Baselined |
| Owner | Business Analyst |
| Last updated | 2026-06-12 |
| Reviewers | Product Owner, Engineering Lead, QA Lead, Customer Success Lead |

## Purpose and scope

This file holds the user stories and acceptance criteria for EP-10. It covers pay periods, the calculation of regular, overtime, holiday, travel, PTO and mileage lines from Verified visits, the pre-export review, the configurable CSV export that locks the period, and adjustments for late changes. Tendwell prepares payroll and exports it to the agency's payroll provider; it does not process payroll, withhold tax or issue pay stubs (ADR-005, CR-008). The rules are designed to support FLSA overtime and the DOL Home Care Rule on travel time between clients; the agency remains responsible for its pay practices.

## Epic

| Field | Value |
|---|---|
| Epic ID | EP-10 |
| Name | Payroll Preparation |
| Module | PAY |
| Goal | Turn Verified visits and approved time into a reviewed, accurate payroll file that the agency imports into its payroll provider, cutting preparation from 14 hours to 3 hours or less per pay period. |
| Objectives | OBJ-02 Payroll preparation time (14 h to 3 h or less per pay period per agency). |
| Business need | BN-10 |
| Release | R1 |

## Story list

| Story | Title | Persona | Priority | Points | Sprint |
|---|---|---|---|---|---|
| US-041 | Calculate pay-period hours and pay lines | PER-04 Denise Carter (AG-FIN) | Must | 13 | S5 |
| US-042 | Review and export payroll | PER-04 Denise Carter (AG-FIN) | Must | 5 | S6 |
| US-043 | Carry late changes into the next period as adjustments | System (SYS) | Must | 5 | S6 |
| **Total** | | | | **23** | |

Canonical worked example (used in US-041-AC1): caregiver E-2041 Maya Ortiz, hourly $19.50, overtime-, holiday- and mileage-eligible; workweek Monday 2026-09-07 to Sunday 2026-09-13; Monday 2026-09-07 is the tenant holiday Labor Day; tenant mileage rate $0.70 per mile; Harborview Home Care pays bi-weekly, pay period 2026-08-31 to 2026-09-13.

## Stories

### US-041 · Calculate pay-period hours and pay lines

| Field | Value |
|---|---|
| Epic | EP-10 Payroll Preparation |
| Persona | PER-04 Denise Carter (AG-FIN) |
| Priority | Must |
| Estimate | 13 points |
| Sprint / Release | S5 / R1 |
| Requirements | FR-PAY-01, FR-PAY-02, FR-PAY-03 |
| Business rules | BR-028, BR-041, BR-042, BR-043, BR-044, BR-045 |
| Dependencies | US-019, US-029, US-040 |

**Story**
As a Billing & Payroll Specialist, I want Tendwell to calculate each caregiver's regular, overtime, holiday, travel, PTO and mileage lines from Verified visits, so that I review exceptions instead of rebuilding timesheets by hand.

**Acceptance criteria**

```gherkin
Scenario: US-041-AC1 Calculate the canonical workweek for E-2041
  Given Maya Ortiz (E-2041) has 40.5 hours of Verified visits in the workweek 2026-09-07 to 2026-09-13, of which 6.0 hours are on Monday 2026-09-07 (Labor Day)
  And she has 2.5 hours of paid travel between consecutive visits, none of it on Monday
  And she drove 46.2 miles between consecutive visits
  When the pay-period summary for 2026-08-31 to 2026-09-13 is calculated
  Then her hours worked for the workweek total 43.0 and the overtime hours are the last 3.0 hours worked, on Sunday 2026-09-13
  And her lines for the workweek are:
    | line     | hours   | rate   | amount  |
    | Holiday  | 6.0     | $29.25 | $175.50 |
    | Regular  | 31.5    | $19.50 | $614.25 |
    | Travel   | 2.5     | $19.50 | $48.75  |
    | Overtime | 3.0     | $29.25 | $87.75  |
    | Mileage  | 46.2 mi | $0.70  | $32.34  |
  And total wages are $926.25 and total payable is $958.59
  And the Mileage line is a reimbursement that adds no hours

Scenario Outline: US-041-AC2 Paid travel between consecutive visits
  Given Maya's visit ends at 10:00 and her next visit, at a different address, starts after a gap of <gap>
  And the estimated drive time is <drive>
  Then the paid travel time is <paid>

  Examples:
    | gap        | drive  | paid       |
    | 45 min     | 20 min | 30 min     |
    | 25 min     | 20 min | 25 min     |
    | 2 h 00 min | 35 min | 45 min     |
    | 2 h 01 min | 35 min | 0 min      |

Scenario Outline: US-041-AC3 Daily overtime profile when the tenant enables it
  Given the tenant has the daily overtime profile switched on
  When Maya works <hours> hours of Verified visits on one day in a week with fewer than 40 hours worked
  Then that day is paid as <regular> regular, <ot> overtime at 1.5x and <dt> double time at 2.0x

  Examples:
    | hours | regular | ot  | dt  |
    | 8.0   | 8.0     | 0.0 | 0.0 |
    | 10.0  | 8.0     | 2.0 | 0.0 |
    | 13.0  | 8.0     | 4.0 | 1.0 |

Scenario: US-041-AC4 No stacking of overtime and holiday multipliers
  Given Maya's 40th hour of the week ends at 14:00 on a tenant holiday and she works until 16:00 that day
  Then the 2.0 hours from 14:00 to 16:00 are paid once at 1.5x as Holiday or Overtime, not at 2.25x
  And the line type used is the one with the higher multiplier, or Overtime when both are equal

Scenario: US-041-AC5 Merge overlapping time so no minute is paid twice
  Given Maya has a Verified visit from 08:00 to 10:00 and approved non-visit training time from 09:30 to 11:00
  When the summary is calculated
  Then 3.0 hours are counted, not 3.5
  And hours are held to the second and rounded to 2 decimals only for display and export

Scenario Outline: US-041-AC6 Count only eligible time
  Given in the workweek Maya has <time>
  Then <result>

  Examples:
    | time                                                       | result                                                                    |
    | a Completed visit with an open LATE_START exception        | the visit is excluded and listed for review                               |
    | 8.0 hours of approved PTO and 36.0 hours worked            | PTO is paid as 8.0 PTO hours and no overtime is calculated                |
    | 30.0 hours worked and mileage-eligible set to No           | no Mileage line is created                                                |
```

**Notes**
- The workweek is the tenant's FLSA workweek (Monday to Sunday by default) and is independent of the pay period; weekly, bi-weekly and semi-monthly periods are supported (FR-PAY-01).
- Holiday hours count toward the 40-hour overtime threshold because they are hours worked; the canonical example was confirmed with the pilot agencies (ISS-03).
- The daily overtime profile (AC3) was added by CR-001 in SRS v1.1 and increased the estimate from 10 to 13 points. When both daily and weekly overtime apply, hours already paid as daily overtime are not counted again toward weekly overtime.
- Estimated drive time comes from the distance matrix at the time the visit is verified and is stored, so that a recalculation produces the same result.
- Performance: the summary for 250 caregivers completes within 60 s (NFR-PERF-04).

### US-042 · Review and export payroll

| Field | Value |
|---|---|
| Epic | EP-10 Payroll Preparation |
| Persona | PER-04 Denise Carter (AG-FIN) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S6 / R1 |
| Requirements | FR-PAY-04, FR-PAY-05 |
| Business rules | BR-046 |
| Dependencies | US-041 |

**Story**
As a Billing & Payroll Specialist, I want to see what still needs attention before I export, and then export a file my payroll provider accepts, so that payroll is right the first time and the period is locked.

**Acceptance criteria**

```gherkin
Scenario: US-042-AC1 Review open items before export
  Given the pay period 2026-08-31 to 2026-09-13 has 3 caregivers with 5 visits that are Needs review or not yet Verified
  When Denise opens the pre-export review
  Then she sees each caregiver, visit, status and open exception code
  And each visit links to the exception queue

Scenario: US-042-AC2 Export with open items only after acknowledgement
  Given the pre-export review lists 5 open visits
  When Denise exports without acknowledging them
  Then the export is not started and she sees "5 visits are not Verified and will not be paid in this period. Review them or confirm to continue."
  When she confirms
  Then the export runs and the 5 visits are listed in the export summary as excluded

Scenario: US-042-AC3 Export with the tenant's column mapping
  Given the tenant mapped employee number to "EmpNo", line types to earning codes REG, OT, DT, HOL, TRV, PTO, MIL and ADJ, and hours to 2 decimals
  When Denise previews and exports the file
  Then the preview shows the first 10 rows exactly as they will be exported
  And the CSV is UTF-8 with a header row and one row per caregiver per line type
  And the export records the row count, the SHA-256 of the file, Denise and the timestamp

Scenario: US-042-AC4 Exporting locks the period
  When the export completes
  Then the pay period status is "Locked"
  And re-downloading the export returns the identical file with the same SHA-256
  And later changes to visits in the period create adjustments in the next open period instead of changing the locked lines

Scenario: US-042-AC5 Only users with the export permission can export
  Given Marcus holds only the AG-COORD role
  When he calls POST /v1/pay-periods/{periodId}/exports
  Then the request returns 403
```

**Notes**
- The export watermark (BR-058) is carried in the file name and in the audit event, not as a data row, so that the payroll provider's import is not broken (agreed with the Compliance and Privacy Officer, 2026-05-20).
- Tendwell does not calculate tax withholding or produce pay stubs; full payroll processing was requested in CR-008 and rejected (DEC-04).
- Analytics: time from period end to export per tenant is the measure for OBJ-02.

### US-043 · Carry late changes into the next period as adjustments

| Field | Value |
|---|---|
| Epic | EP-10 Payroll Preparation |
| Persona | System (SYS) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S6 / R1 |
| Requirements | FR-PAY-06 |
| Business rules | BR-046 |
| Dependencies | US-042 |

**Story**
As the payroll calculation service, I want changes that affect a locked period to become adjustment lines in the next open period, so that exported payroll is never rewritten and every correction is traceable to its visit.

**Acceptance criteria**

```gherkin
Scenario: US-043-AC1 Turn a time correction into an adjustment
  Given the pay period 2026-08-31 to 2026-09-13 is Locked
  And Maya's Verified visit on 2026-09-10 lasted 2.0 hours in a week where she worked 38.0 hours
  When on 2026-09-16 the Coordinator corrects the visit to 2.5 hours
  Then an Adjustment line of +0.5 hours at $19.50 ($9.75) is created in the open period 2026-09-14 to 2026-09-27
  And the line references the original visit and the line it adjusts
  And the locked period's lines and export are unchanged

Scenario: US-043-AC2 Recalculate overtime for the original workweek
  Given Maya's workweek 2026-09-07 to 2026-09-13 already totals 43.0 hours worked
  When a visit in that week is corrected from 2.0 to 2.5 hours after the period is locked
  Then the adjustment is +0.5 hours of Overtime at $29.25, amount $14.63
  And the amount is rounded half-up to the cent

Scenario: US-043-AC3 Create a negative adjustment
  Given a Verified visit in a locked period is corrected from 2.5 to 2.0 hours in a week under 40 hours
  Then an Adjustment line of -0.5 hours at $19.50 (-$9.75) is created in the next open period

Scenario: US-043-AC4 Pay a visit verified after the period was locked
  Given a visit on 2026-09-11 was Needs review when the period was exported
  When the Coordinator resolves its exception on 2026-09-17 and the visit becomes Verified
  Then its hours are added as adjustment lines in the period 2026-09-14 to 2026-09-27, priced with the rate effective on 2026-09-11

Scenario: US-043-AC5 Process each change once
  Given the adjustment for a correction was created
  When the same change event is delivered again
  Then no second adjustment line is created
```

**Notes**
- Adjustments use the multipliers of the original workweek, so overtime is calculated where it was earned (BR-041).
- If the next period does not yet exist, it is created from the tenant's pay frequency before the adjustment is written.
- Adjustment lines export with earning code ADJ, or with the mapped code of the adjusted line type if the tenant chooses that option.

## Related documents

- [Epics overview](../epics.md)
- [Change request log](../change-request-log.md)
- [Decision log](../decision-log.md)
- [Software requirements specification](../../02-requirements/SRS.md)
- [Business rules catalog](../../02-requirements/business-rules.md)
- [ADR-005 Payroll export, not processing](../../03-design/architecture/adr/ADR-005-payroll-export-not-processing.md)
- [Test data](../../06-quality/test-data/README.md)
- [Test cases](../../06-quality/test-cases.md)
