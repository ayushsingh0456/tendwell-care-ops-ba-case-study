# EP-13 Reporting & Audit: user stories

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DEL-US-13 |
| Version | 1.2 |
| Status | Baselined |
| Owner | Business Analyst |
| Last updated | 2026-06-12 |
| Reviewers | Product Owner, Engineering Lead, QA Lead, Compliance and Privacy Officer |

## Purpose and scope

This file holds the user stories and acceptance criteria for EP-13. It covers the operations dashboard, the standard report set with CSV and PDF export, the immutable audit log and export watermarking. The dashboard and reports are also how the six business objectives (OBJ-01 to OBJ-06) are measured after go-live.

## Epic

| Field | Value |
|---|---|
| Epic ID | EP-13 |
| Name | Reporting & Audit |
| Module | RPT |
| Goal | Give agency leaders a live picture of today's operations and the standard reports they need, and give auditors an immutable trail of who did what, when and to which record. |
| Objectives | Measurement for OBJ-01 to OBJ-06 (EVV compliance, MAR compliance, authorization utilization and AR ageing reports provide the KPI values). Guardrail: 100% of exports watermarked and audited. |
| Business need | BN-13 |
| Release | R1 |

## Story list

| Story | Title | Persona | Priority | Points | Sprint |
|---|---|---|---|---|---|
| US-051 | See the operations dashboard and standard reports | PER-05 Tom Brennan (AG-ADM) | Must | 8 | S6 |
| US-052 | Search and export the audit log | PER-05 Tom Brennan (AG-ADM) | Must | 5 | S3 |
| **Total** | | | | **13** | |

## Stories

### US-051 · See the operations dashboard and standard reports

| Field | Value |
|---|---|
| Epic | EP-13 Reporting & Audit |
| Persona | PER-05 Tom Brennan (AG-ADM) |
| Priority | Must |
| Estimate | 8 points |
| Sprint / Release | S6 / R1 |
| Requirements | FR-RPT-01, FR-RPT-02 |
| Business rules | None |
| Dependencies | US-029, US-033, US-018, US-013, US-044 |

**Story**
As an agency owner, I want one dashboard for today's operations and a standard set of reports I can filter and export, so that I can manage by exception and show regulators and payers our numbers.

**Acceptance criteria**

```gherkin
Scenario: US-051-AC1 Show today's operations at a glance
  When Tom opens the operations dashboard at 09:30
  Then he sees tiles for today's visits by status, open EVV exceptions, missed doses, credentials expiring within 30 days, authorizations at 90% or more utilization, and unbilled Verified visits
  And each tile shows an "as of" time no more than 5 minutes old
  And selecting a tile opens the filtered list behind it

Scenario: US-051-AC2 Scope the dashboard to the user's locations
  Given Marcus is assigned only to "Lakemont North"
  When he opens the dashboard
  Then every tile counts only "Lakemont North" records
  And Tom, with access to all locations, can filter the dashboard by location

Scenario Outline: US-051-AC3 Run and export each standard report
  When Tom runs the report "<report>" for 2026-09-01 to 2026-09-30 and location "Lakemont North"
  Then the report shows the filtered results
  And he can export it as CSV and as PDF

  Examples:
    | report                     |
    | EVV compliance             |
    | Visit history              |
    | Caregiver hours            |
    | Authorization utilization  |
    | MAR compliance             |
    | Incident log               |
    | AR ageing                  |

Scenario: US-051-AC4 Calculate EVV compliance consistently
  Given in September 2026 "Lakemont North" had 1,000 Completed or Verified visits
  And 968 of them have all six EVV data elements captured electronically with no Manual time or location punch
  When Tom runs the EVV compliance report
  Then the report shows 96.8% complete EVV data
  And lists the 32 visits that were not complete, with the reason for each

Scenario: US-051-AC5 Mask PHI in report output
  When Tom exports the Visit history report
  Then client date of birth, Medicaid ID, phone, address and diagnoses are not included
  And the export carries the watermark and creates an audit event as required for every export
```

**Notes**
- KPI definitions: the EVV compliance report measures OBJ-01, MAR compliance measures OBJ-03, authorization utilization and denial-related reasons support OBJ-06, and AR ageing plus the invoice issue dates support OBJ-04.
- Reports with PHI columns (for example, a claim-ready visit list) need the export permission and the reveal permission; standard reports exclude PHI by default.
- The missed-doses tile defaults to the last 24 hours; older Missed - undocumented doses stay in the Clinical Supervisor's review queue (US-033). This default was the agreed answer to the need behind the rejected CR-007.
- Out of scope: a custom report builder and BI connectors (R2 candidates).

### US-052 · Search and export the audit log

| Field | Value |
|---|---|
| Epic | EP-13 Reporting & Audit |
| Persona | PER-05 Tom Brennan (AG-ADM) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S3 / R1 |
| Requirements | FR-RPT-03, FR-RPT-04 |
| Business rules | BR-057, BR-058 |
| Dependencies | US-009 |

**Story**
As an Agency Administrator, I want to search and export a tamper-proof audit log, so that I can answer "who saw or changed this record, and when" for an auditor, a payer or a client complaint.

**Acceptance criteria**

```gherkin
Scenario: US-052-AC1 Search the audit log
  When Tom filters the audit log by entity "Client C-10234", action "phi.reveal" and dates 2026-09-01 to 2026-09-30
  Then he sees each matching event with actor, action, entity, IP address, device and timestamp
  And for update events he sees the before and after values side by side

Scenario Outline: US-052-AC2 Record every auditable action
  When <action> happens
  Then an audit event with action "<audit action>" is written

  Examples:
    | action                                               | audit action               |
    | Marcus creates a client                              | client.create              |
    | Marcus edits a visit's time                          | visit.update               |
    | Marcus cancels a visit                               | visit.cancel               |
    | Marcus reveals a client's phone number               | phi.reveal                 |
    | Denise exports payroll                               | export.create              |
    | Rosa signs in                                        | auth.sign_in               |
    | Tom changes Marcus's permission overrides            | access.permissions_update  |
    | a support agent views a client under a grant         | support.read               |

Scenario: US-052-AC3 The audit log is append-only
  Given an audit event exists
  When any user, including a Platform Administrator, tries to update or delete it through the API
  Then the API offers no such operation and returns 405
  And the application's database role has no UPDATE or DELETE privilege on the audit table

Scenario: US-052-AC4 Export with a watermark and audit the export
  When Tom exports the filtered audit log as CSV
  Then the file name and the first line carry the watermark "Exported by Tom Brennan, Harborview Home Care, 2026-10-02 14:05 America/New_York"
  And an audit event "export.create" records the export, its filters and its row count

Scenario: US-052-AC5 Support actions show the grant
  Given a support agent acted under grant SAG-0042
  When Tom filters the audit log by actor type "Support"
  Then each event shows the grant ID SAG-0042 and the support agent's name

Scenario: US-052-AC6 Tenants see only their own events
  When an Agency Administrator of Cedar Lane Adult Day Center searches the audit log
  Then no event from Harborview Home Care is returned
```

**Notes**
- Retention: audit events are kept for 7 years (BR-057, NFR-PRIV-02). How this interacts with tenant deletion after cancellation (NFR-PRIV-03) is set out in the data classification and retention document, which the Compliance and Privacy Officer owns.
- Delivered early (S3) so that every later story could rely on the audit service; FR-RPT-04 watermarking is reused by all exports.
- Performance: a 30-day search for one tenant returns the first page within 2 s at p95 using cursor pagination.

## Related documents

- [Epics overview](../epics.md)
- [Software requirements specification](../../02-requirements/SRS.md)
- [Business rules catalog](../../02-requirements/business-rules.md)
- [Non-functional requirements](../../02-requirements/non-functional-requirements.md)
- [Data classification and retention](../../03-design/data/data-classification-and-retention.md)
- [Project charter](../../01-discovery/project-charter.md)
- [Test cases](../../06-quality/test-cases.md)
