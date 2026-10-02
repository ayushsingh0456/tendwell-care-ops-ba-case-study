# Release and sprint plan

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DEL-004 |
| Version | 1.4 |
| Status | Approved (R1 closed; actuals recorded) |
| Owner | Business Analyst |
| Last updated | 2026-09-24 |
| Reviewers | Product Owner, Engineering Lead, QA Lead, Customer Success Lead |

## Purpose and scope

This plan covers the delivery of Release 1: team capacity and velocity assumptions, the six build sprints, hardening, user acceptance testing (UAT), the go/no-go decision, the pilot and general availability (GA). It started as the baseline plan on 2026-03-06 and now records actuals, carry-overs and retrospective takeaways. R1.1 and R2 timing is in the [product roadmap](product-roadmap.md).

## Team, capacity and velocity assumptions

| Role | People | Allocation to Tendwell | Counted in velocity |
|---|---|---|---|
| Product Owner | 1 | 60% | No |
| Business Analyst | 1 | 100% | No |
| Engineering Lead | 1 | 100% (about 30% hands-on code, the rest reviews and architecture) | No |
| Backend developers | 2 | 100% | Yes |
| Web developer | 1 | 100% | Yes |
| Mobile developer | 1 | 100% | Yes |
| QA Lead and QA engineer | 2 | 100% | No (testing is inside each story's Definition of Done) |
| UX Designer | 1 | 60% | No |
| Clinical SME (RN advisor) | 1 | About 4 hours per week; 2 days per sprint in S4 and S5 | No |
| Compliance and Privacy Officer | 1 | About 4 hours per week | No |
| Customer Success Lead | 1 | From S5 (pilot preparation) | No |

**Velocity assumption: 48 points per sprint.**

- Basis: 4 developers at about 12 points each per 2-week sprint, the average the same core team achieved over its last 8 sprints on a comparable product.
- Calibration: reference stories were sized in discovery planning poker. US-008 (password reset) is the 2-point reference and US-025 (clock-in) the 8-point reference. Stories above 8 points need a worked example before sprint planning; 13 is the largest allowed size.
- Adjustments: S1 is planned at 44 points for environment, CI and row-level-security setup. S6 is planned at 45 firm points because of Memorial Day (2026-05-25).
- Buffer: the SRS v1.0 backlog was 288 points against 288 points of capacity, so there was no buffer (RSK-08). CR-003 restored a 6-point buffer in v1.1.

**Cadence.** Sprints run Monday to Friday of the following week. Planning happens on day 1. The BA-led backlog refinement takes place on day 3, and the BA keeps at least 1.5 sprints of stories meeting the Definition of Ready. The sprint review is on day 10 with pilot agency representatives from S3 onwards, and the retrospective follows the review.

## Sprint calendar

| Sprint | Start | End | Planned capacity | Committed points | Sprint goal (short) |
|---|---|---|---|---|---|
| S1 | 2026-03-09 | 2026-03-20 | 44 | 44 | Sign up, sign in, roles |
| S2 | 2026-03-23 | 2026-04-03 | 48 | 44 | Clients, caregivers, notifications |
| S3 | 2026-04-06 | 2026-04-17 | 48 | 47 | Schedule and clock in |
| S4 | 2026-04-20 | 2026-05-01 | 48 | 50 (45 firm + 5 at risk) | Offline EVV, exceptions, eMAR |
| S5 | 2026-05-04 | 2026-05-15 | 48 | 47 + 5 carried in | Payroll calculation and safety alerts |
| S6 | 2026-05-18 | 2026-05-29 | 45 | 50 (45 firm + 5 stretch) | Billing, payroll export, dashboard |
| Hardening | 2026-06-01 | 2026-06-12 | n/a | 5 carried in | Regression, security, performance |
| UAT | 2026-06-08 | 2026-06-26 | n/a | n/a | Pilot agency acceptance |

## Sprint plans and outcomes

### S1 (2026-03-09 to 2026-03-20)

| Item | Detail |
|---|---|
| Goal | An agency can sign up, verify its email, sign in with MFA and give staff the right roles, on a tenant isolated by row-level security. |
| Committed stories | US-001 (8), US-002 (3), US-003 (5), US-004 (5), US-005 (5), US-007 (5), US-008 (2), US-009 (8), US-010 (3) |
| Points | 44 committed, 44 completed |
| Key risks | Row-level-security performance unknown (time-boxed spike on day 1); payment provider test account (DEP-05, done 2026-03-12) |
| Demo outcome | Tom Brennan registered Harborview with code TRIAL21, verified his email, enrolled TOTP and gave Marcus Hale the AG-COORD role; a TEN-002 user requesting a TEN-001 client received 404. The audit-event writer was built as a technical enabler inside US-009, so every later story could write audit events. |

### S2 (2026-03-23 to 2026-04-03)

| Item | Detail |
|---|---|
| Goal | Coordinators can admit clients with authorizations and approved care plans, and onboard caregivers with credentials and pay profiles. |
| Committed stories | US-011 (5), US-012 (8), US-013 (5), US-014 (5), US-015 (3), US-017 (5), US-018 (5), US-019 (3), US-049 (5) |
| Points | 44 committed, 44 completed |
| Key risks | Approximate geocoding found in the migration sample (ISS-01); SMS vendor BAA needed before real phone numbers are used (DEP-01, signed 2026-03-27) |
| Demo outcome | Marcus admitted C-10234 with T1019 authorization PA-2026-55871 and saw 480 units remaining; Priya Raman approved care plan version 1; E-2041 Maya Ortiz received her app invitation; a PHI reveal appeared in the audit trail. |

### S3 (2026-04-06 to 2026-04-17)

| Item | Detail |
|---|---|
| Goal | A visit can be scheduled with compliance checks and delivered with an online clock-in and clock-out. |
| Committed stories | US-020 (8), US-021 (8), US-022 (5), US-024 (5), US-025 (8), US-028 (5), US-036 (3), US-052 (5) |
| Points | 47 committed, 47 completed |
| Key risks | Field accuracy of GPS fixes (RSK-02); schedule board performance at 500 visits (NFR-PERF-03); mobile developer bottleneck (RSK-09) |
| Demo outcome | A Monday-Wednesday-Friday pattern created 24 visits; an overlap was hard-blocked; Rosa Delgado clocked in 40 m from the address with no exception and a test fix at 212 m raised Location mismatch; Tom searched the audit log. CR-001, CR-002 and CR-003 were approved during the sprint (SRS v1.1, 2026-04-17). |

### S4 (2026-04-20 to 2026-05-01)

| Item | Detail |
|---|---|
| Goal | Visits can be captured offline and verified through the exception queue; medication orders and doses are documented and escalated. |
| Committed stories | US-016 (3), US-026 (5, at risk on DEP-02), US-027 (8), US-029 (8), US-031 (5), US-032 (8), US-033 (5), US-050 (8) |
| Points | 50 committed, 45 completed; US-026 carried to S5 |
| Key risks | Identity vendor sandbox credentials not issued (RSK-01, realized as ISS-02); offline sync edge cases; Clinical SME availability for eMAR acceptance criteria |
| Demo outcome | In airplane mode, Rosa clocked in and out; the punches synced with capture and receipt times kept separately. Marcus corrected a missing clock-out with a Manual punch while the original stayed visible. A missed-dose escalation ran on a test clock: Overdue at the window close, then Missed - undocumented 60 minutes later. US-026 ran against the vendor mock only and did not meet the Definition of Done. |

### S5 (2026-05-04 to 2026-05-15)

| Item | Detail |
|---|---|
| Goal | Payroll hours are calculated correctly, and time off, incidents, PRN doses and vitals are handled safely. |
| Committed stories | US-023 (5), US-030 (3), US-034 (3), US-035 (5), US-037 (5), US-038 (5), US-039 (3), US-040 (5), US-041 (13); carried in: US-026 (5) |
| Points | 52 committed (47 + 5 carried), 52 completed. About 2 points of effort remained on US-026 because the adapter and UI were built in S4. |
| Key risks | Interpretation of holiday hours and overtime (ISS-03, resolved 2026-05-12); 13-point story size |
| Demo outcome | The E-2041 worked example reproduced exactly: 43.0 hours worked, total wages $926.25, mileage $32.34, total payable $958.59. An SpO2 of 89% at 22:30 alerted Priya despite quiet hours. A suspected-neglect incident got a 24-hour deadline with alerts at 50% and 90%. US-026 passed against the vendor sandbox. CR-008 (full payroll processing) was raised after this review. |

### S6 (2026-05-18 to 2026-05-29)

| Item | Detail |
|---|---|
| Goal | Agencies can export payroll, bill under all four billing models, collect payments online and see the operations dashboard. |
| Committed stories | US-006 (3), US-042 (5), US-043 (5), US-044 (8), US-045 (8), US-046 (5), US-047 (5, stretch), US-048 (3), US-051 (8) |
| Points | 50 committed (45 firm + 5 stretch), 45 completed; US-047 finished in hardening on 2026-06-03 |
| Key risks | All billing stories in one sprint (QA bottleneck); Memorial Day capacity; payment webhook signature handling |
| Demo outcome | C-10234 was billed 24 units for $174.00, and $145.00 with a 4-unit Not billable line when only 20 units remained. The adult day participant was billed $1,092.00, and the supported-living resident $4,340.00 prorated. A payroll export locked its period. The walking skeleton ran end to end on staging. |

## Burn-up and actuals

| Sprint | Committed | Completed | Carried over | Cumulative completed | R1 scope | Notes |
|---|---|---|---|---|---|---|
| S1 | 44 | 44 | 0 | 44 | 288 | Baseline SRS v1.0 includes EP-14 (11 points) |
| S2 | 44 | 44 | 0 | 88 | 288 | |
| S3 | 47 | 47 | 0 | 135 | 282 | SRS v1.1: CR-001 +3, CR-002 +2, CR-003 -11 |
| S4 | 50 | 45 | US-026 (5) | 180 | 282 | Identity vendor sandbox delay |
| S5 | 52 | 52 | 0 | 232 | 282 | Includes carried US-026 |
| S6 | 50 | 45 | US-047 (5) | 277 | 282 | Stretch item not finished |
| Hardening | 5 | 5 | 0 | 282 | 282 | US-047 done 2026-06-03 |

Average velocity over the six sprints was 47.0 points (282 / 6), 2% below the 48-point assumption. Every Must story was done by the end of S6.

## Retrospective takeaways

| Sprint | What we learned | Action taken |
|---|---|---|
| S1 | Acceptance criteria that state the exact user-facing message text removed most QA-developer back-and-forth. Environment setup used 2 developer-days. | The BA writes message text into every validation scenario; reduced first-sprint capacity is now standard for new teams. |
| S2 | Checking data and PHI classification in refinement caught that credential documents needed the same encryption and short-lived links as client PHI. | The PHI classification check was added to the Definition of Ready. |
| S3 | A field test at three Lakemont addresses showed geocodes up to 180 m off, which proved the value of the confirmed-pin step in US-012. The QA device matrix was set at 6 devices. | The device matrix was agreed. In hindsight it did not include the iOS approximate-location setting, the gap INC-2026-011 exposed in August. |
| S4 | A vendor dependency with no "needed by" date in the plan caused the only carry-over. | Every external dependency now has a needed-by date and an owner in the RAID log and is reviewed weekly. |
| S5 | The 13-point payroll story finished on day 9 only because the worked example was agreed before the sprint (ISS-03). | No story above 8 points enters a sprint without a signed-off worked example. |
| S6 | Five billing stories in one sprint created a QA bottleneck on days 8 to 10, and the stretch item slipped. | Future plans sequence shared engines first (pricing before invoicing) and cap stretch items at 5 points. |

## Hardening (2026-06-01 to 2026-06-12)

- Completed US-047 (2026-06-03).
- Full regression: the automated suite plus manual exploratory charters for EVV offline, eMAR escalation and billing.
- Performance tests against NFR-PERF-01 to NFR-PERF-04 at three times pilot volume.
- Third-party penetration test against OWASP ASVS Level 2 (NFR-SEC-02). Two High findings were fixed and retested by 2026-06-11.
- Disaster-recovery restore test (NFR-DR-01).
- WCAG 2.2 AA accessibility audit of the Agency Web App (NFR-ACC-01).
- First data migration dry run for TEN-001 (DEP-03).
- Caregiver app submitted to both app stores (DEP-06).

## User acceptance testing (2026-06-08 to 2026-06-26)

| Item | Detail |
|---|---|
| Participants | TEN-001 Harborview Home Care: Agency Administrator, 2 Care Coordinators, Billing & Payroll Specialist, 3 caregivers. TEN-002 Cedar Lane Adult Day Center: administrator and 2 program staff. TEN-003 Northgate Supported Living: RN Clinical Supervisor, Coordinator and 3 direct-care staff. |
| Approach | Scripted UAT scenarios per persona on a UAT tenant with synthetic data, followed by a week of "day in the life" sessions run by the agencies themselves |
| Entry criteria | All R1 Must stories meet the Definition of Done; regression passed; no open Critical defects; UAT data loaded |
| Exit criteria | 100% of Must-priority UAT scenarios passed; no open Critical or High defects; every open Medium defect has an agreed workaround |
| Outcomes | SRS v1.2 (2026-06-12) recorded UAT clarifications, including one charge per day for adult day participants with two check-ins and when MISSING_CLOCK_OUT is raised. CR-007 (auto-cancel undocumented doses) was raised by TEN-003 and rejected on 2026-06-17. Exit criteria were met on 2026-06-26. |

## Go/no-go (2026-06-26)

| # | Criterion | Evidence | Result |
|---|---|---|---|
| 1 | All R1 Must stories Done; Should stories Done or formally deferred | Jira release report | Met (52 of 52 stories Done) |
| 2 | Walking skeleton runs end to end on production-like staging | S6 review recording, test run log | Met |
| 3 | UAT exit criteria met | UAT sign-off from each pilot agency | Met |
| 4 | No open Critical or High security findings (NFR-SEC-02) | Penetration test retest letter | Met |
| 5 | Performance NFRs met at three times pilot volume | Performance test report | Met |
| 6 | Restore tested within RPO 15 min and RTO 4 h (NFR-DR-01) | DR test record | Met (restore completed in 2 h 10 min) |
| 7 | BAAs in place with hosting, SMS, email, identity vendors and each pilot agency (NFR-CMP-01) | Contract register | Met |
| 8 | Data migration dry run reconciled 100% of active clients, authorizations, caregivers and credentials | Reconciliation report (DEP-03) | Met with condition: 9 TEN-003 addresses needed manual pins |
| 9 | Caregiver app approved in both app stores | Store approvals (DEP-06) | Met (2026-06-24) |
| 10 | At least 90% of pilot users trained; NFR-USE-02 usability target met | Training log, usability report | Met |
| 11 | Runbooks, on-call rotation and incident process ready | Operations readiness checklist | Met |
| 12 | Payroll parallel-run plan agreed with each pilot agency | Signed plan | Met |

**Decision: Go with conditions (DEC-11).**

1. TEN-003 starts eMAR at one home on 2026-07-06 and extends to all three homes by 2026-07-20 after a Clinical SME review of the first two weeks.
2. Each pilot agency runs payroll in parallel (old process and Tendwell export) for its first two pay periods.
3. Identity verification is enabled only at TEN-001 during the pilot.
4. Hypercare runs for two weeks, with daily defect triage led by the QA Lead and the BA.

## Pilot, early access (2026-07-06 to 2026-08-31) and general availability

| Date | Event |
|---|---|
| 2026-07-06 | Pilot go-live for TEN-001, TEN-002 and TEN-003 (one TEN-003 home on eMAR) |
| 2026-07-13 | Early-access wave opens: invite-code sign-up for up to 15 additional agencies on pilot terms, so multi-tenant behavior is exercised before GA (9 joined by 2026-07-21, 14 by 2026-08-18) |
| 2026-07-20 | TEN-003 eMAR extended to all three homes |
| 2026-07-21 | INC-2026-007 duplicate client invoices (SEV-2); CR-005 raised 2026-07-23 |
| 2026-08-14 | Payroll parallel runs completed for all three agencies with no unexplained variances (RSK-07 closed) |
| 2026-08-18 | INC-2026-011 false Location mismatch exceptions (SEV-2); CR-004 raised 2026-08-21 |
| 2026-08-27 | Pilot exit review |
| 2026-09-01 | General availability |
| 2026-09-09 | INC-2026-015 escalation email to a deactivated user (SEV-1, privacy); CR-006 raised 2026-09-11 |

| Pilot exit criterion (for GA) | Result |
|---|---|
| Two consecutive pay periods exported from Tendwell per agency with no unexplained variance against the parallel run | Met |
| July and August invoices issued within 2 business days of period end | Met for TEN-001 and TEN-002; TEN-003 took 3 business days in July (fixed-monthly proration review) and 2 in August |
| Visits with complete EVV data at 95% or more over 2026-08-17 to 2026-08-30, after bulk resolution of INC-2026-011's false exceptions | Met |
| No open SEV-1 or SEV-2 incident without an approved corrective change request | Met (CR-004 and CR-005 approved) |
| Written go-ahead from each pilot agency's administrator | Met |

The 97% EVV completeness target (OBJ-01) and the other KPI targets are measured at the 90-day readout (see the roadmap).

## Related documents

- [Product roadmap](product-roadmap.md)
- [Epics](epics.md)
- [Story map](story-map.md)
- [Definition of Ready and Done](definition-of-ready-and-done.md)
- [Change request log](change-request-log.md)
- [RAID log](raid-log.md)
- [Decision log](decision-log.md)
- [Test strategy and plan](../06-quality/test-strategy-and-plan.md)
- [UAT plan and scripts](../06-quality/uat-plan-and-scripts.md)
- [Incident register](../07-operations/incident-register.csv)
- [Project charter](../01-discovery/project-charter.md)
