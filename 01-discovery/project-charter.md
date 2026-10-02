# Project Charter: Tendwell Release 1

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DIS-01 |
| Version | 1.1 |
| Status | Approved |
| Owner | Business Analyst |
| Last updated | 2026-04-17 |
| Reviewers | Executive Sponsor, Product Owner, Engineering Lead, Compliance and Privacy Officer, Clinical SME (RN advisor), Customer Success Lead |

| Version | Date | Author | Change |
|---|---|---|---|
| 0.3 | 2026-02-20 | Business Analyst | Draft for steering review after the third discovery workshop |
| 1.0 | 2026-02-27 | Business Analyst | Approved at steering committee; baseline for the SRS v1.0 (2026-03-02) |
| 1.1 | 2026-04-17 | Business Analyst | Scope updated for CR-003 (Family Portal deferred to Release 2); milestones re-confirmed |

### Purpose and scope of this document

This charter authorizes the Tendwell Release 1 (R1) project, states why it exists, and sets the objectives, scope boundaries, milestones, budget envelope and governance that every later artifact traces to. The Business Analyst drafted it from discovery evidence (see [discovery workshop notes](discovery-workshop-notes.md)) and maintains it; the Executive Sponsor and Product Owner approve it. Detailed requirements live in the [BRD](../02-requirements/BRD.md) and [SRS](../02-requirements/SRS.md), not here.

All organizations, people and figures in this case study are fictional.

## 1. Vision statement

> For home and community-based care agencies that run on phone calls, paper timesheets and MAR binders, **Tendwell** is a multi-tenant operations platform that connects every authorized hour of care to a verified visit, a documented dose, a correct paycheck and a clean invoice. Unlike generic scheduling tools, Tendwell treats EVV, medication safety and payroll and billing rules as one connected chain, so agency staff spend their time on care rather than on reconciliation.

## 2. Problem statement

| Element | Statement |
|---|---|
| The problem of | Care delivery data captured on paper and by phone, then re-keyed into spreadsheets for payroll and billing |
| Affects | Caregivers, Care Coordinators, Clinical Supervisors, Billing and Payroll Specialists and agency owners at small and mid-size agencies (10 to 250 caregivers) |
| The impact of which is | 19% of visits lack complete EVV data, 4.6% of medication doses go undocumented, payroll takes 14 hours per pay period, invoices take 9 days to issue, 6.1% of billed dollars are denied for authorization overrun, and caregivers work with expired blocking credentials 23 times per quarter |
| A successful solution would | Capture each visit once at the point of care (online or offline), apply EVV, eMAR, payroll and billing rules consistently, and produce payroll and billing outputs without re-keying |

The baseline figures come from discovery at the three pilot agencies: document analysis of two pay periods of paper timesheets, three months of MAR binders, billing denial reports, and time-and-motion observation of payroll preparation.

## 3. Business objectives and KPIs

Each objective maps one-to-one to a baseline KPI. The Business Analyst defined each measurement method with the objective's owner so that baseline and target are measured the same way; the full definitions are in the [BRD](../02-requirements/BRD.md). The Product Owner reports progress to steering.

| ID | Objective | KPI | Baseline | Target | Measurement method (summary) | Owner role |
|---|---|---|---|---|---|---|
| OBJ-01 | EVV completeness | Visits with complete EVV data | 81% | 97% or more | Completed visits with all six EVV data elements (BR-020) divided by all completed visits; EVV compliance report (FR-RPT-02), with the manual-correction rate reported alongside | Product Owner |
| OBJ-02 | Payroll preparation time | Payroll preparation time per pay period per agency | 14 h | 3 h or less | Working time from opening the pre-export review (FR-PAY-04) to export (FR-PAY-05), cross-checked by a time log for two periods | Customer Success Lead |
| OBJ-03 | Undocumented doses | Undocumented medication doses | 4.6% | 0.5% or less | Dose tasks still Missed - undocumented 24 h after their scheduled time divided by all scheduled dose tasks; MAR compliance report | Clinical SME (RN advisor) |
| OBJ-04 | Days to invoice | Days to issue monthly invoices | 9 | 2 business days or fewer | Median business days from period end to invoice issue | Customer Success Lead |
| OBJ-05 | Credential lapses | Caregivers working with an expired blocking credential | 23 instances per quarter | 0 | Verified visits where the caregiver held an Expired Blocking credential on the visit date; reviewed quarterly | Compliance and Privacy Officer |
| OBJ-06 | Authorization-overrun denials | Billing denials caused by authorization overrun | 6.1% | 1% or less | Denied dollars with an authorization-related denial reason divided by billed dollars; agency remittance data supplied monthly | Product Owner |

## 4. Scope summary

### In scope (Release 1)

| Epic | Capability | Business need |
|---|---|---|
| EP-01 | Agency onboarding and subscription (self-service sign-up, trial and promo codes, seat billing, read-only state) | BN-01 |
| EP-02 | Identity and access management (MFA, role templates, permission overrides, support access grants) | BN-02 |
| EP-03 | Client records, service authorizations and versioned care plans | BN-03 |
| EP-04 | Caregiver workforce, credentials and pay profiles | BN-04 |
| EP-05 | Scheduling, compliance checks and open shifts | BN-05 |
| EP-06 | Electronic Visit Verification, including offline capture and exception review | BN-06 |
| EP-07 | Medication administration (eMAR) and vitals | BN-07 |
| EP-08 | Visit notes and client incidents | BN-08 |
| EP-09 | Time off and holidays | BN-09 |
| EP-10 | Payroll preparation and CSV export | BN-10 |
| EP-11 | Client billing, invoicing, payment links and claim batch export | BN-11 |
| EP-12 | Notifications and escalation ladders | BN-12 |
| EP-13 | Operations dashboard, standard reports and audit log | BN-13 |

Service lines: `HOME_VISIT`, `ADULT_DAY` and `SUPPORTED_LIVING`. Applications: Agency Web App, Caregiver Mobile App (offline-capable), Platform Console and public sign-up site.

### Out of scope (Release 1)

| Item | Disposition |
|---|---|
| EP-14 Family Portal (BN-14) | Deferred to Release 2 by CR-003 (charter v1.1) |
| Payroll processing (tax withholding, pay stubs, direct deposit) | Not built; Tendwell exports payroll to the agency's payroll provider (FR-PAY-05). Later confirmed by the rejection of CR-008 |
| EDI 837 claim submission | Not built in R1; claim batches are CSV for the agency's clearinghouse (FR-BIL-06) |
| State-specific EVV aggregator formats | R2; R1 provides a configurable aggregator CSV (NFR-CMP-02) |
| Spanish caregiver app | R2 (NFR-I18N-01); strings are externalized in R1 |
| Clinical assessments (OASIS), skilled nursing visit documentation | Not planned; Tendwell targets non-medical and paraprofessional care with eMAR support |

### Assumptions and constraints

- Each agency remains the HIPAA covered entity; Tendwell Labs acts as a business associate and signs a BAA with each agency (NFR-CMP-01).
- R1 is built by one cross-functional team in six two-week sprints; scope changes go through change control (section 9).
- Compliance features are designed to support agency obligations. The agency remains responsible for its own regulatory compliance.

## 5. Key stakeholders

The full register, power/interest grid and RACI are in the [stakeholder register and RACI](stakeholder-register-raci.md).

| Group | Roles |
|---|---|
| Sponsor and product | Executive Sponsor (Tendwell Labs), Product Owner |
| Delivery team | Business Analyst, Engineering Lead, 4 developers (2 backend, 1 web, 1 mobile), QA Lead and 1 QA engineer, UX Designer |
| Domain and assurance | Clinical SME (RN advisor), Compliance and Privacy Officer |
| Customer-facing | Customer Success Lead (pilot), Platform Support |
| Pilot agencies | TEN-001 Harborview Home Care, TEN-002 Cedar Lane Adult Day Center, TEN-003 Northgate Supported Living |
| External parties | Identity verification vendor, payment provider, state EVV aggregator, agencies' claims clearinghouses and payroll providers |

## 6. Milestones

| Milestone | Planned | Actual / status | Exit criterion |
|---|---|---|---|
| Discovery start | 2026-01-05 | Done | Elicitation plan approved |
| Discovery workshops 1-3 | 2026-01-21, 2026-02-04, 2026-02-17 | Done | Workshop records signed off by attendees |
| Charter approved | 2026-02-27 | Done | Steering approval (section 11) |
| SRS baseline v1.0 | 2026-03-02 | Done | Sign-off by Product Owner, Engineering Lead, QA Lead, Clinical SME, Compliance and Privacy Officer |
| Sprint 1 start | 2026-03-09 | Done | Definition of Ready met for S1 stories |
| SRS v1.1 (CR-001, CR-002, CR-003) | 2026-04-17 | Done | CCB approval recorded |
| Sprint 6 end (build complete) | 2026-05-29 | Done | All Must stories meet Definition of Done |
| Hardening and UAT | 2026-06-01 to 2026-06-30 | Done | UAT sign-off by pilot agency representatives; no open Critical or High defects or security findings |
| SRS v1.2 (UAT clarifications) | 2026-06-12 | Done | CCB approval recorded |
| Pilot go-live | 2026-07-06 | Done | Go/no-go checklist passed; BAAs signed with TEN-001, TEN-002, TEN-003 |
| Early-access wave | from 2026-07-13 | Done | Up to 15 self-registered agencies admitted on pilot terms |
| General availability | 2026-09-01 | Done | Pilot exit review; KPI trend positive for OBJ-01 and OBJ-03 |

The pilot runs with the three design-partner agencies from 2026-07-06. An early-access wave of self-registered agencies joins from 2026-07-13 so that multi-tenant behavior is exercised before general availability.

## 7. Budget envelope (illustrative)

Figures are fictional and shown only to illustrate how the envelope was framed for steering. They cover R1 through general availability.

| Line item | Basis | Amount (USD) |
|---|---|---|
| Discovery (Jan-Feb 2026) | Product Owner, Business Analyst, UX Designer, Clinical SME part-time, travel to pilot sites | $96,000 |
| Build (S1-S6) | Full delivery team, 12 weeks | $612,000 |
| Hardening and UAT (June 2026) | Full team, UAT facilitation, pilot training | $118,000 |
| Pilot and early-access support (Jul-Aug 2026) | Customer Success Lead, on-call rotation, fixes | $104,000 |
| Cloud and third-party services to GA | HIPAA-eligible AWS services, SMS, email, maps, identity vendor, error tracking | $46,000 |
| Security and compliance | Third-party penetration test (NFR-SEC-02), BAA and policy review | $38,000 |
| Contingency (12%) | Held by Executive Sponsor; release requires steering approval | $121,700 |
| **Total envelope** | | **$1,135,700** |

Tolerance: the Product Owner may re-allocate up to 5% between lines; anything beyond that, or any draw on contingency, goes to steering.

## 8. High-level risks

Risks are tracked in detail, with owners and responses, in the [RAID log](../05-delivery/raid-log.md). The charter-level view is:

| Risk | Likelihood | Impact | Response | Owner |
|---|---|---|---|---|
| Caregivers lack signal in rural client homes, so EVV data is lost or late | High | High | Offline-first mobile capture (FR-EVV-05, NFR-AVL-02, ADR-006) | Engineering Lead |
| Low caregiver adoption of the mobile app (age, tech comfort, language) | Medium | High | Three-tap clock-in (NFR-USE-01), prototype testing with caregivers, field champions per agency | UX Designer |
| Medication rules implemented incorrectly create clinical risk | Medium | High | Clinical SME approval of every eMAR rule (BR-029 to BR-034); dedicated UAT scenarios | Clinical SME |
| PHI exposure through notifications, exports or support access | Medium | High | Minimum-necessary design (NFR-PRIV-01), audited support grants (BR-008), export watermarks (BR-058) | Compliance and Privacy Officer |
| Payroll rule complexity (overtime, holiday, travel, state daily overtime) | High | Medium | Worked examples agreed with payroll staff; every BR covered by an automated test (NFR-MNT-01) | Business Analyst |
| Billing errors damage agency trust with clients and payers | Medium | High | Idempotent billing runs (BR-050), authorization cap (BR-049), invoice approval step | Product Owner |
| Pilot agencies cannot spare staff for UAT during operations | Medium | Medium | UAT sessions scheduled outside peak hours; scripted scenarios; Customer Success Lead on site | Customer Success Lead |
| Third-party dependency outage (identity vendor, SMS, payment provider) | Medium | Medium | Adapter pattern (ADR-004), fallbacks so care is never blocked, vendor status monitoring | Engineering Lead |

## 9. Governance

### Steering and working cadence

| Forum | Cadence | Chair | Members | Decides |
|---|---|---|---|---|
| Steering committee | Every 2 weeks (at sprint review); monthly during pilot | Executive Sponsor | Product Owner, Business Analyst, Engineering Lead, Compliance and Privacy Officer, Customer Success Lead | Scope boundaries, budget, milestone changes, go-live |
| Change Control Board (CCB) | Weekly, or ad hoc for urgent changes | Product Owner | Business Analyst (secretary), Engineering Lead, QA Lead, Clinical SME, Compliance and Privacy Officer, Customer Success Lead | Change requests |
| Backlog refinement | Weekly | Product Owner | Business Analyst, Engineering Lead, UX Designer, QA Lead | Story readiness and ordering |
| Pilot agency council | Every 2 weeks from June 2026 | Customer Success Lead | Pilot agency administrators, Business Analyst, Product Owner | Feedback and UAT priorities |

### Change control

1. Anyone may raise a change; the Business Analyst records it as a CR in the [change request log](../05-delivery/change-request-log.md).
2. The Business Analyst performs impact analysis: affected FR, BR, NFR and US IDs, test cases, data and API changes, effort, schedule and compliance impact.
3. The CCB decides: Approved, Rejected, or Deferred. Clinical and privacy changes need the Clinical SME or Compliance and Privacy Officer respectively to concur.
4. Approved CRs update the SRS revision history and the [traceability matrix](../02-requirements/requirements-traceability-matrix.md). The Business Analyst publishes the new SRS version.
5. Changes affecting milestones or budget beyond tolerance escalate to steering.

Emergency changes raised during a production incident follow the [incident management process](../07-operations/incident-management-process.md): the Incident Commander may authorize a hotfix, and the Business Analyst raises the CR within 2 business days so the requirement change is reviewed and baselined.

## 10. Success criteria

The project is successful when:

1. All six objective KPIs (section 3) trend toward target by general availability and meet target at the 90-day readout after pilot go-live (due 2026-10-05).
2. All R1 Must requirements are delivered and traced to passing tests in the traceability matrix.
3. UAT is signed off by representatives of all three pilot agencies.
4. No Critical or High security findings are open at release (NFR-SEC-02), and BAAs are in place with every tenant.
5. Availability meets 99.9% monthly (NFR-AVL-01) during the pilot.
6. At least 85% of pilot caregivers complete clock-in and clock-out in the app (not by manual correction) within 30 days of go-live.

## 11. Approval

| Role | Decision | Date |
|---|---|---|
| Executive Sponsor | Approved | 2026-02-27 |
| Product Owner | Approved | 2026-02-27 |
| Engineering Lead | Approved | 2026-02-27 |
| Compliance and Privacy Officer | Approved | 2026-02-27 |
| Clinical SME (RN advisor) | Approved | 2026-02-27 |
| Business Analyst (author) | Prepared | 2026-02-26 |

Version 1.1 (CR-003 scope change) was re-approved by the Executive Sponsor and Product Owner on 2026-04-17.

## Related documents

- [Stakeholder register and RACI](stakeholder-register-raci.md)
- [Personas](personas.md)
- [Current vs future state](current-vs-future-state.md)
- [Discovery workshop notes](discovery-workshop-notes.md)
- [Business requirements document](../02-requirements/BRD.md)
- [Software requirements specification](../02-requirements/SRS.md)
- [Product roadmap](../05-delivery/product-roadmap.md)
- [Release and sprint plan](../05-delivery/release-and-sprint-plan.md)
- [Change request log](../05-delivery/change-request-log.md)
- [RAID log](../05-delivery/raid-log.md)
