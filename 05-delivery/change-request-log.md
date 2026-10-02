# Change request log

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DEL-006 |
| Version | 1.5 |
| Status | Living document |
| Owner | Business Analyst |
| Last updated | 2026-09-24 |
| Reviewers | Product Owner, Engineering Lead, QA Lead, Clinical SME (RN advisor), Compliance and Privacy Officer |

## Purpose and scope

This log records every change requested against the baselined requirements (SRS v1.0 of 2026-03-02 and later versions), how each was assessed and what was decided. It includes a completed change request form for CR-005 as a worked example, and a short write-up on why CR-007 was rejected.

**Change control process.** Anyone may raise a change request. The BA logs it within 1 business day and completes the impact analysis within 3 business days, covering scope, schedule, cost, risk and every affected artifact. The change control board decides. The Product Owner chairs it, with the Engineering Lead and BA as standing members, and the Clinical SME or the Compliance and Privacy Officer join when a change touches clinical or privacy rules. Approved changes go into the next SRS revision, the traceability matrix and the affected stories.

**Cost basis.** Cost is estimated at USD 1,600 per story point. This is the blended delivery cost of the team per sprint divided by the planned velocity of 48 points.

## Log

| CR | Title | Requested by | Date raised | Reason | Impact (scope / schedule / cost / risk) | Affected artifacts | Decision | Decision date | Approver | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| CR-001 | Daily overtime profile for states with daily OT rules | Product Owner | 2026-03-25 | Agencies in states with daily overtime rules cannot use a weekly-only calculation, which blocks the payroll module in those markets. The Ohio pilot agencies do not need it. | **Scope:** optional tenant profile (over 8 h/day at 1.5x, over 12 h/day at 2.0x); US-041 re-estimated from 10 to 13 points.<br>**Schedule:** +3 points absorbed in S5; 0 days.<br>**Cost:** USD 4,800.<br>**Risk:** more pay combinations; mitigated by worked examples and BR-level tests. | BR-041, FR-PAY-02, US-041, NFR-MNT-01 | Approved | 2026-04-15 | Product Owner (change control board) | Implemented in R1 (SRS v1.1) |
| CR-002 | Optional Coordinator confirmation on open-shift claims | Customer Success Lead (for TEN-001 Coordinators) | 2026-04-07 | Coordinators wanted to confirm client-caregiver fit (language, lift skills) before a claim is final; first-claim-wins alone was a barrier to adopting open shifts. | **Scope:** tenant setting (default Off) and a pending-claim state; US-023 re-estimated from 3 to 5 points.<br>**Schedule:** +2 points in S5; 0 days.<br>**Cost:** USD 3,200.<br>**Risk:** slower fill time when enabled; tracked by time-to-confirm analytics. | FR-SCH-05, US-023 | Approved | 2026-04-15 | Product Owner (change control board) | Implemented in R1 (SRS v1.1) |
| CR-003 | Family Portal deferred to Release 2 | Product Owner (from BA capacity and risk analysis) | 2026-04-08 | The v1.0 backlog (288 points) equaled 100% of capacity (RSK-08). The family consent model had not had a privacy review. Pilot agencies ranked the portal lowest. | **Scope:** EP-14 moved to R2.<br>**Schedule:** -11 points; with CR-001 and CR-002, R1 scope becomes 282 points with a 6-point buffer.<br>**Cost:** USD 17,600 moved from R1 to R2.<br>**Risk:** pilot family expectations; managed by communicating the R2 timeline. | EP-14, FR-FAM-01, FR-FAM-02, FR-FAM-03, US-053, US-054 | Approved (scope deferral) | 2026-04-15 | Product Owner (change control board) | Closed: deferred to R2 (SRS v1.1); see DEC-09 |
| CR-004 | Separate Low GPS accuracy exception from Location mismatch | Customer Success Lead (from INC-2026-011 review) | 2026-08-21 | INC-2026-011: 41% of iOS clock-ins flagged over 3 days, 1,180 false exceptions across 11 tenants, and payroll export delayed 1 day for 2 tenants. The server treated an inaccurate fix as a mismatch, and the app did not request precise location. | **Scope:** accuracy worse than 100 m or (0,0) always raises LOW_GPS_ACCURACY; precise-location prompt in the app; bulk resolve for exceptions on punches with accuracy worse than 100 m; device matrix expanded.<br>**Schedule:** 8 points in R1.1.<br>**Cost:** USD 12,800.<br>**Risk:** reduces false exceptions; residual risk that caregivers decline the prompt, monitored by the exception-rate alert. | BR-022, FR-EVV-03, FR-EVV-07, FR-EVV-08, US-025, US-029, NFR-OBS-02, NFR-MOB-01 | Approved | 2026-08-26 | Product Owner (change control board) | Approved: in R1.1 regression test (SRS v1.3) |
| CR-005 | DB-enforced billing idempotency and pre-issue duplicate check | Engineering Lead (from INC-2026-007 review) | 2026-07-23 | INC-2026-007: the nightly billing run executed twice during a deployment overlap and created 214 duplicate draft invoices across 9 tenants. 37 were emailed, and 6 clients paid twice ($2,914.50 refunded). There was no alert. | **Scope:** unique database constraint on the invoice idempotency key, with upsert behavior; pre-issue duplicate check; invoice-count anomaly alert.<br>**Schedule:** 7 points in R1.1.<br>**Cost:** USD 11,200.<br>**Risk:** the migration must clean up legacy duplicates first; expand-and-contract migration (NFR-MNT-02). | BR-050, FR-BIL-01, FR-BIL-04, US-044, NFR-MNT-02, NFR-OBS-02 | Approved | 2026-07-30 | Product Owner with Engineering Lead | Approved: in R1.1 regression test (SRS v1.3); see DEC-12 |
| CR-006 | Resolve notification recipients at send time; no PHI in email bodies | Compliance and Privacy Officer (from INC-2026-015) | 2026-09-11 | INC-2026-015: an escalation email reached a deactivated former Coordinator's mailbox, which forwarded it to a personal address. Recipients had been cached at ladder configuration, and the email included the client's first name, last initial and incident category. | **Scope:** ladders store roles only; recipients are resolved from active users at send time, with fallback to Agency Administrators; email added to the no-PHI rule; deactivated-recipient alert.<br>**Schedule:** 6 points in R1.1.<br>**Cost:** USD 9,600.<br>**Risk:** generic text may feel less urgent; mitigated by an "Urgent" prefix and the deep link. | BR-054, BR-056, FR-NTF-03, FR-NTF-05, US-037, US-049, US-050, NFR-PRIV-01, NFR-OBS-02 | Approved | 2026-09-15 | Product Owner and Compliance and Privacy Officer | Approved: in R1.1 regression test (SRS v1.3) |
| CR-007 | Auto-cancel undocumented doses at midnight | Agency Administrator (TEN-003, during UAT) | 2026-06-10 | Overdue and Missed doses from the previous day cluttered the morning handover view; the requester wanted a "clean slate" each day. | **Scope if approved:** nightly job, new Cancelled dose status, change to BR-031.<br>**Schedule:** 3 points.<br>**Cost:** USD 4,800.<br>**Risk:** High. It would hide clinical events, compromise the MAR as a record and distort the OBJ-03 measure. | BR-030, BR-031, FR-MAR-04, US-033 | **Rejected** | 2026-06-17 | Product Owner, on the recommendation of the Clinical SME and the Compliance and Privacy Officer | Closed: rejected. The need is met by the Missed - undocumented status and escalation (BR-030, BR-031); see DEC-10 |
| CR-008 | Full in-app payroll processing (tax withholding, pay stubs) | Agency Administrator (TEN-001) | 2026-05-18 | After the S5 review, the requester wanted to drop the agency's separate payroll provider. | **Scope if approved:** tax engine (federal, state, local), filings, garnishments, direct deposit, pay stubs, year-end forms.<br>**Schedule:** 120 points or more (at least 2.5 sprints), which would delay the pilot by at least 6 weeks.<br>**Cost:** USD 192,000 or more, plus tax-engine licensing and ongoing compliance.<br>**Risk:** High regulatory and financial liability outside the core product. | FR-PAY-05, US-042, ADR-005 | **Rejected / deferred** | 2026-05-22 | Product Owner (change control board) | Closed: kept in the backlog for review after R2. Export to the payroll provider stays (FR-PAY-05); see DEC-04 |

**Summary of R1 scope movement:** SRS v1.0 288 points; CR-001 +3; CR-002 +2; CR-003 -11; R1 baseline (v1.1) 282 points. R1.1 (CR-004, CR-005, CR-006) adds 21 points of change outside the R1 baseline.

---

## Change request form: CR-005

### 1. Request details

| Field | Value |
|---|---|
| CR ID | CR-005 |
| Title | DB-enforced billing idempotency and pre-issue duplicate check |
| Requested by | Engineering Lead |
| Date raised | 2026-07-23 |
| Source | Post-incident review of INC-2026-007 (SEV-2, 2026-07-21) |
| Category | Requirement change arising from a production incident |
| Priority | High; financial accuracy and customer trust |
| Requirements baseline | SRS v1.2 (2026-06-12) |
| Analyst | Business Analyst |

### 2. Background

On 2026-07-21 the nightly billing run executed twice during a deployment overlap, when two scheduler workers both took leadership. BR-050 already said that a billing run is idempotent per tenant, client, payer and period, but it was implemented as an application-level check-then-insert. Both workers checked at the same time, found no invoice and inserted one. The database had no unique constraint on the invoice idempotency key to stop the second insert.

- 214 duplicate draft invoices were created across 9 tenants.
- 3 tenants had auto-issue enabled for private pay, so 37 duplicates were emailed to responsible parties.
- 6 clients paid twice; $2,914.50 was refunded.
- The problem was detected through a customer support ticket. No alert fired.

The single-flight scheduler (ADR-003) was the first line of defense and failed during the overlap. The requirement had no second line of defense and no detection.

### 3. Current vs proposed behavior

| Aspect | Current (SRS v1.2) | Proposed (SRS v1.3) |
|---|---|---|
| Idempotency enforcement | Application checks for an existing invoice, then inserts | Unique database constraint on `invoices.idempotency_key` (tenant + client + payer + period); inserts use insert-or-update, so a concurrent second write updates the existing Draft |
| Re-run of a period | Updates Draft invoices (BR-050) | Unchanged; now guaranteed under concurrency |
| Issuing an invoice | Allowed for any Approved invoice; private-pay auto-issue runs after the billing run | Before any issue, manual or automatic, the system checks for another non-void invoice with the same client, payer and period, and blocks the issue with a message naming the possible duplicate |
| Detection | None | Alert when a run's invoice count deviates more than 20% from the previous run (NFR-OBS-02); alert on any blocked duplicate issue |
| Legacy data | 214 duplicates voided manually during incident response | Migration verifies that no duplicate keys remain before adding the constraint |

### 4. Impact analysis by artifact

| Artifact | Change | Effort | Owner |
|---|---|---|---|
| BR-050 (business rules catalog) | Add: "The key is enforced by a database unique constraint; a concurrent duplicate becomes an update of the existing Draft. No invoice is issued while another non-void invoice exists for the same client, payer and period." | Included | Business Analyst |
| FR-BIL-01 (SRS) | Revise the acceptance criteria to include concurrent runs and the pre-issue check | Included | Business Analyst |
| FR-BIL-04 (SRS) | Add the duplicate check as a precondition of the Approved-to-Issued transition | Included | Business Analyst |
| US-044 | Add US-044-AC3 (concurrent runs) and US-044-AC4 (pre-issue duplicate check); story notes reference INC-2026-007 | 1 point (refinement and test design) | Business Analyst, QA Lead |
| Data model (ERD, data dictionary) | `invoices.idempotency_key` marked UNIQUE; migration notes | Included in the migration | Engineering Lead |
| Database migration | Expand and contract: verify there are no duplicate keys, then create the unique index concurrently, then switch the code path; backward-compatible for one release (NFR-MNT-02) | 3 points | Backend developers |
| API (OpenAPI) | `POST /invoices/{invoiceId}/issue` returns 409 with problem type `possible-duplicate-invoice`; `POST /billing-runs` behavior documented under concurrency | 1 point | Backend developers |
| Observability (NFR-OBS-02) | Invoice-count deviation alert and blocked-duplicate alert routed to on-call | 2 points | Engineering Lead |
| ADR-003 | Amendment: the database constraint is the required last line of defense for any job that creates financial records | Included | Engineering Lead |
| Test cases and regression suite | New concurrency test with two workers; pre-issue block tests for manual and automatic issue | Included in the points above | QA Lead |
| Traceability matrix | BR-050, FR-BIL-01 and FR-BIL-04 rows updated with new AC and test links | Included | Business Analyst |
| Runbook | Response steps for the new alerts | Included | Engineering Lead |
| **Total** | | **7 points (USD 11,200)** | |

No other story is affected. Payroll export (US-042) already locks periods with a single record per export, and the Definition of Done now requires a two-worker test for every scheduled job.

### 5. Options considered

| Option | Description | Effort | Pros | Cons |
|---|---|---|---|---|
| A | Fix scheduler leader election only | 2 points | Cheapest; fixes the trigger of this incident | Leaves no protection against any other concurrent path, such as a manual re-run during the nightly run or a retried job; no detection |
| B | Database unique constraint with insert-or-update, pre-issue duplicate check and anomaly alert, plus the leader-election fix already shipped during incident response | 7 points | Defense in depth: prevents, blocks before money moves and detects; matches the intent of BR-050 | Needs a careful migration; slightly more complex issue flow |
| C | Serialize all billing runs through one queue worker per tenant | 5 points | Simple mental model | Slower runs (NFR-PERF-04 at risk); does not protect against bugs outside the run; no detection |
| D | Disable private-pay auto-issue permanently | 1 point | Removes the email impact | Loses a valued feature; does not prevent duplicate drafts |

### 6. Recommendation

Approve Option B for R1.1. The incident showed that one control was not enough for a process that creates financial records and emails customers. Option B adds a structural guarantee (the constraint), a check before money can move (the pre-issue check) and detection (the anomaly alert), for 5 more points than the cheapest option. Interim containment applied during incident response stays in place until R1.1 is released.

### 7. Approval

| Role | Decision | Date |
|---|---|---|
| Product Owner (chair) | Approved | 2026-07-30 |
| Engineering Lead | Approved | 2026-07-30 |
| QA Lead | Consulted; test approach agreed | 2026-07-29 |
| Business Analyst | Impact analysis complete | 2026-07-28 |
| Customer Success Lead | Informed; tenant communication drafted | 2026-07-30 |

**Target release:** R1.1 (target 2026-10-14). **SRS revision:** v1.3 (2026-09-24).

### 8. Verification

- US-044-AC3 passes with two workers started at the same moment in staging, 50 runs in a row, with zero duplicate keys.
- US-044-AC4 passes for manual and automatic issue.
- The invoice-count alert fires in a production-like test when the count is forced 25% above the previous run.
- After release, Customer Success confirms zero duplicate invoices for two consecutive monthly runs.

---

## CR-007 rejection: clinical safety write-up

**The request.** During UAT on 2026-06-10, the Agency Administrator of TEN-003 Northgate Supported Living asked for doses still undocumented at midnight to be cancelled automatically. Each morning the night-to-day handover view in the three homes showed the previous day's Overdue and Missed - undocumented doses, and staff found the list noisy.

**Separating the need from the solution.** The BA ran a short follow-up session with the requester, the TEN-003 RN supervisor and the Clinical SME. The underlying need was a clear handover: "show me what needs doing this shift." The proposed solution was to make yesterday's undocumented doses disappear. These are two different things: the first is a presentation problem, the second changes the clinical record.

**Why auto-cancel is unsafe.**

1. **It hides a clinical event.** An undocumented dose may have been given and not recorded, or not given at all. Either case needs a nurse's attention: a missed antihypertensive or anticonvulsant can harm the client. Cancelling turns "we don't know" into "nothing to see."
2. **It corrupts the record.** The MAR is the legal record of administration. "Cancelled" would mean the dose was not due, which is false. BR-031 says doses are never auto-cancelled or deleted for this reason.
3. **It defeats escalation.** BR-030 escalates to the Clinical Supervisor 60 minutes after the window closes. A midnight cancel would remove late-evening doses from the Supervisor's queue before anyone reviewed them.
4. **It distorts the outcome measure.** OBJ-03 tracks undocumented doses (target 0.5% or less). Auto-cancel would make the number look better while care got worse.
5. **It creates audit exposure.** Surveyors and payers look for documentation gaps; silently cancelled doses look like concealment, and the agency remains responsible for its records.

**Decision.** The Clinical SME and the Compliance and Privacy Officer recommended rejection. The Product Owner rejected CR-007 on 2026-06-17 (DEC-10).

**How the real need was met without changing the rules.**

- The caregiver's due list already shows only doses for the current visit (US-032), so night staff do not see yesterday's doses.
- The office missed-doses tile defaults to the last 24 hours (US-051), and older items sit in the Clinical Supervisor's review queue (US-033), where Priya annotates them after the 24-hour late-entry window.
- US-033-AC3 makes the decision testable: an undocumented dose is still Missed - undocumented after midnight and after every nightly job.

**Follow-up.** TEN-003's Missed - undocumented rate and the median time to Supervisor annotation are reviewed monthly. A repeat request will be judged against the same safety test: does the change hide, alter or delete a clinical event?

## Related documents

- [Decision log](decision-log.md)
- [RAID log](raid-log.md)
- [Release and sprint plan](release-and-sprint-plan.md)
- [Software requirements specification](../02-requirements/SRS.md)
- [Business rules catalog](../02-requirements/business-rules.md)
- [Requirements traceability matrix](../02-requirements/requirements-traceability-matrix.md)
- [ADR-003 Single-flight scheduled jobs](../03-design/architecture/adr/ADR-003-single-flight-scheduled-jobs.md)
- [ADR-005 Payroll export, not processing](../03-design/architecture/adr/ADR-005-payroll-export-not-processing.md)
- [INC-2026-007 Duplicate client invoices](../07-operations/incidents/INC-2026-007-duplicate-client-invoices.md)
- [INC-2026-011 False Location mismatch exceptions](../07-operations/incidents/INC-2026-011-false-location-mismatch-exceptions.md)
- [INC-2026-015 Escalation email to a deactivated user](../07-operations/incidents/INC-2026-015-escalation-email-to-deactivated-user.md)
- [EP-07 eMAR and vitals stories](user-stories/EP-07-emar-vitals.md)
- [EP-11 Billing stories](user-stories/EP-11-billing.md)
