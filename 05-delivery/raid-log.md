# RAID log

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DEL-007 |
| Version | 2.1 |
| Status | Living document (reviewed weekly) |
| Owner | Business Analyst |
| Last updated | 2026-10-02 |
| Reviewers | Product Owner, Engineering Lead, QA Lead, Customer Success Lead, Compliance and Privacy Officer |

## Purpose and scope

This log tracks the risks, assumptions, issues and dependencies for Tendwell Release 1 and R1.1, with items for Release 2 that are already known. The BA facilitates a weekly review with the Product Owner and Engineering Lead. Each item links to the requirements, stories, change requests and incidents it affects.

**Scoring.** Probability (P) and impact (I) are each scored 1 (very low) to 5 (very high). Score = P x I. A score of 15 or more is Red, 8 to 14 is Amber and 7 or less is Green. Scores shown are the latest assessment. For realized risks, the score shown is the one before realization.

## Risks

| ID | Description | P | I | Score | Owner | Mitigation | Trigger | Status |
|---|---|---|---|---|---|---|---|---|
| RSK-01 | The identity verification vendor's contract and BAA are not signed in time, so US-026 (FR-EVV-04) cannot be built against a real service in S4. | 3 | 3 | 9 | Product Owner | Build against a vendor mock behind the IdentityVerificationPort adapter (ADR-004); make the feature optional per tenant (DEC-07); escalate the contract weekly. | Sandbox credentials not received by 2026-04-20 (DEP-02) | Realized as ISS-02; closed 2026-05-05 |
| RSK-02 | GPS fixes with poor accuracy produce false Location mismatch exceptions, which erode caregiver trust and delay payroll (BR-021, BR-022, FR-EVV-03). | 3 | 4 | 12 | Engineering Lead | Server-side distance only; accuracy captured on every punch; device matrix testing; exception-rate alert (NFR-OBS-02). | EVV exception rate above 2x the 7-day baseline | Realized as INC-2026-011 (2026-08-18). The device matrix lacked the approximate-location setting. CR-004 in R1.1; open until release |
| RSK-03 | Scheduled jobs run twice across a deployment and create duplicate financial records: invoices, payroll lines or notifications (ADR-003, BR-050). | 2 | 5 | 10 | Engineering Lead | Single-flight jobs through `job_executions` with a unique idempotency key; zero-downtime deployments (NFR-MNT-02). | Two workers holding leadership; duplicate keys in a run | Realized as INC-2026-007 (2026-07-21). Single-flight alone was not enough; CR-005 adds a database constraint. Open until R1.1 |
| RSK-04 | PHI is disclosed through notification channels (SMS, push, email) or to recipients who should no longer receive it (BR-054, BR-056, NFR-PRIV-01). | 2 | 5 | 10 | Compliance and Privacy Officer | Generic message text with sign-in deep links; vendor BAAs (DEP-01); deactivation revokes sessions. | Any notification to a deactivated user or containing client identifiers | Realized as INC-2026-015 (2026-09-09). Recipients were cached and email allowed partial identifiers; CR-006 in R1.1. Open until release |
| RSK-05 | Pilot data migration quality (addresses, authorizations, credentials) causes false exceptions, blocked schedules or wrong bills at go-live (DEP-03). | 4 | 4 | 16 | Customer Success Lead | Two migration dry runs; reconciliation report; confirmed map pins (US-012-AC2); agency sign-off on migrated data. | Reconciliation below 100% for active records 7 days before go-live | Closed 2026-07-17. 9 TEN-003 addresses were pinned manually (go/no-go condition) |
| RSK-06 | Caregivers do not adopt the app consistently because of limited digital confidence, older phones, shared devices or poor signal, which keeps EVV completeness below target (OBJ-01). | 3 | 4 | 12 | Customer Success Lead | 3-tap clock-in (NFR-USE-01); offline capture (NFR-AVL-02); in-person training with bilingual quick guides; Spanish UI in R2 (NFR-I18N-01). | Weekly EVV completeness below 90% for any pilot agency | Open; monitored weekly since go-live |
| RSK-07 | Payroll calculation errors (overtime, holiday, travel, mileage) damage trust and create wage-and-hour exposure for agencies (BR-041 to BR-045). | 3 | 5 | 15 | Product Owner | Canonical worked example (E-2041) signed off; every BR has automated tests (NFR-MNT-01); two-period parallel run per pilot agency. | Any unexplained variance in the parallel run | Closed 2026-08-14 after parallel runs with no unexplained variance |
| RSK-08 | The SRS v1.0 backlog (288 points) equals 100% of the planned capacity of 6 x 48 points, leaving no buffer for discovery or defects. | 4 | 4 | 16 | Product Owner | Defer the lowest-value epic (CR-003); schedule Should stories late; track the burn-up weekly. | Velocity below 48 points in S1 or S2 | Closed 2026-04-17. CR-003 restored a 6-point buffer |
| RSK-09 | The single mobile developer is a key-person dependency for EVV, offline sync and eMAR in the Caregiver app. | 3 | 4 | 12 | Engineering Lead | Web developer pairs on React Native one day per sprint; offline design documented in spec 001; Engineering Lead reviews every mobile pull request; a vetted contractor is on standby. | Mobile developer unavailable for more than 3 days in a sprint | Open (R2 adds Spanish UI and Family Portal work on mobile) |
| RSK-10 | Clinical Supervisors get so many urgent alerts (missed doses, vitals, incidents) that real alerts are ignored (BR-030, BR-034, BR-053). | 3 | 4 | 12 | Clinical SME (RN advisor) | Alerts only at BR thresholds; deduplication (BR-055); per-client vital ranges; escalation stops on resolution; monthly review of alerts per Supervisor per shift. | More than 15 urgent alerts per Supervisor per shift, or median acknowledgment above 30 minutes | Open; TEN-003 at 6 alerts per shift in September |

## Assumptions

| ID | Assumption | Impact if wrong | Owner | Validation | Status |
|---|---|---|---|---|---|
| ASM-01 | Caregivers have a smartphone meeting iOS 16+ or Android 10+ (NFR-MOB-01); agencies supply devices to the few who do not. | EVV completeness target unreachable at some agencies | Customer Success Lead | Device survey at each pilot agency | Validated: 94% personal devices; agencies supplied the rest |
| ASM-02 | Agencies keep their existing payroll provider and import a CSV file (ADR-005). | Demand for in-app payroll processing | Product Owner | Discovery interviews; CR-008 outcome | Validated (CR-008 rejected with agency agreement) |
| ASM-03 | Agencies submit claims through their existing clearinghouse, and a CSV claim batch is acceptable in R1 (no EDI 837). | Manual re-keying of claims; OBJ-04 at risk | Product Owner | Clearinghouse template review with TEN-001 and TEN-003 | Validated |
| ASM-04 | The pilot state's EVV aggregator accepts agency file submission, and the configurable aggregator CSV is enough for R1 (NFR-CMP-02). | State-specific format needed earlier than R2 | Compliance and Privacy Officer | Agency confirmation; aggregator documentation | Validated for the pilot; state formats planned for R2 (DEP-04) |
| ASM-05 | Each agency is the HIPAA covered entity and Tendwell Labs is its business associate. Tendwell signs a BAA with each agency and holds BAAs with every subprocessor that handles PHI (NFR-CMP-01). | Contracting delays block go-live | Compliance and Privacy Officer | Contract register | Validated; BAAs in place before go-live |
| ASM-06 | Service addresses geocode to rooftop precision for at least 95% of clients; the rest are confirmed manually (US-012-AC2). | False Location mismatch exceptions at go-live | Business Analyst | Migration sample geocoding test (ISS-01) | Partly validated: 89% rooftop in the first sample; manual pin step added |
| ASM-07 | Each agency has a Clinical Supervisor (RN) who can approve care plans and medication orders within 1 business day. | Care plans and orders stuck in PendingApproval; eMAR unusable | Customer Success Lead | Pilot agency staffing confirmation | Validated for TEN-001 and TEN-003; TEN-002 uses a contracted RN |
| ASM-08 | The default PTO accrual (1 hour per 30 hours worked, 80-hour cap) and a Monday-to-Sunday workweek suit the pilot agencies; any differences are handled by configuration. | Payroll rework or new rules | Business Analyst | Pay-policy review with each pilot agency | Validated; TEN-002 uses a 60-hour cap through configuration |

## Issues

| ID | Date raised | Issue | Impact | Owner | Resolution | Date resolved | Status |
|---|---|---|---|---|---|---|---|
| ISS-01 | 2026-03-18 | In a 200-address migration sample from TEN-001, 11% of addresses geocoded to approximate (non-rooftop) results, some more than 150 m from the home. | False Location mismatch exceptions; ASM-06 at risk | Business Analyst | Added a confirm-pin step to client admission when the geocoder returns a non-rooftop result (US-012-AC2) and a geocode-precision column to the migration reconciliation report. | 2026-04-02 | Closed |
| ISS-02 | 2026-04-22 | The identity verification vendor did not issue sandbox credentials because the BAA was still in legal review. | US-026 could not meet the Definition of Done in S4 (5 points carried over) | Product Owner | Escalated to both legal teams; BAA countersigned 2026-05-05; US-026 completed in S5 against the sandbox. | 2026-05-05 | Closed |
| ISS-03 | 2026-05-07 | Pilot agencies disagreed on whether hours worked on a holiday count toward the 40-hour weekly overtime threshold. | US-041 acceptance criteria could not be finalized; risk to S5 | Business Analyst | Hours worked on a holiday are hours worked and count toward the threshold; a minute that is both overtime and holiday is paid once at the higher multiplier (BR-042). Confirmed with the Product Owner and all three agencies against the E-2041 worked example ($958.59 total payable). | 2026-05-12 | Closed |
| ISS-04 | 2026-07-21 | INC-2026-007: 214 duplicate draft invoices across 9 tenants; 37 emailed; 6 clients paid twice ($2,914.50 refunded). | Customer trust, refunds, support load; OBJ-04 at risk | Engineering Lead | Duplicates voided and refunds completed during incident response; post-incident review held; CR-005 approved 2026-07-30. | 2026-07-30 (containment); permanent fix in R1.1 | Open until R1.1 is released |
| ISS-05 | 2026-08-18 | INC-2026-011: false Location mismatch exceptions after Caregiver app v1.6.0 (41% of iOS clock-ins over 3 days; 1,180 exceptions in 11 tenants). | Payroll export delayed 1 day for 2 tenants; Coordinator workload | Engineering Lead | Bulk resolution of affected exceptions with an audited reason; post-incident review; CR-004 approved 2026-08-26; device matrix expanded. | 2026-08-26 (containment); permanent fix in R1.1 | Open until R1.1 is released |
| ISS-06 | 2026-09-09 | INC-2026-015: a client-incident escalation email went to a deactivated former Coordinator's mailbox and was forwarded to a personal address. | Privacy event; covered entity notified within 24 hours under the BAA | Compliance and Privacy Officer | Recipient confirmed deletion in writing; HIPAA breach risk assessment (four factors, 45 CFR 164.402) completed by the Privacy Officer, with the final determination resting with the covered entity; cached recipients cleared; CR-006 approved 2026-09-15. | 2026-09-15 (containment); permanent fix in R1.1 | Open until R1.1 is released |

## Dependencies

| ID | Dependency | Type | Needed by | Provider | Owner | Affects | Status |
|---|---|---|---|---|---|---|---|
| DEP-01 | BAA with the SMS vendor, signed before any message is sent to a real phone number | External (contract) | 2026-04-03 (end of S2) | SMS vendor | Compliance and Privacy Officer | US-007, US-049, FR-NTF-01 | Done 2026-03-27 |
| DEP-02 | Identity verification vendor contract, BAA and sandbox credentials | External (contract and technical) | 2026-04-20 (start of S4) | Liveness and face-match vendor | Product Owner | US-026, FR-EVV-04, ADR-004 | Done 2026-05-05, 15 days late (ISS-02) |
| DEP-03 | Pilot agency data migration: client, authorization, caregiver, credential and pay-profile data from TEN-001, TEN-002 and TEN-003 spreadsheets, with two dry runs | External (customer data) | Dry run 2026-06-08; final load 2026-07-02 | Pilot agencies with Customer Success | Customer Success Lead | Pilot go-live; US-012, US-013, US-018, US-019 | Done 2026-07-02 |
| DEP-04 | State EVV aggregator specifications for state-specific export formats | External (regulator or aggregator) | 2026-12-01 (R2 discovery) | State EVV aggregators | Compliance and Privacy Officer | NFR-CMP-02, R2 roadmap item | Open; specifications requested 2026-09-15 |
| DEP-05 | Payment provider account, webhook endpoints and production approval for subscriptions and invoice payment links | External (vendor) | 2026-03-12 (S1) for test mode; 2026-06-26 for production | Payment provider | Engineering Lead | US-001, US-004, US-046, FR-ONB-06, FR-BIL-05 | Done (test mode 2026-03-12; production 2026-06-19) |
| DEP-06 | Caregiver app review and approval in the Apple App Store and Google Play | External (platform) | 2026-06-26 | Apple, Google | Engineering Lead | Pilot go-live; all CG stories | Done 2026-06-24 |

## Review history

| Date | Change |
|---|---|
| 2026-03-06 | Baseline: RSK-01 to RSK-09, ASM-01 to ASM-08, DEP-01 to DEP-06 |
| 2026-04-17 | RSK-08 closed after CR-003 |
| 2026-05-05 | ISS-02 closed; RSK-01 closed |
| 2026-05-12 | ISS-03 closed |
| 2026-06-19 | RSK-10 added after UAT feedback from TEN-003 |
| 2026-08-14 | RSK-07 closed after the payroll parallel runs |
| 2026-09-15 | ISS-06 logged; RSK-04 marked realized |
| 2026-10-02 | Weekly review; R1.1 items remain open until release |

## Related documents

- [Release and sprint plan](release-and-sprint-plan.md)
- [Change request log](change-request-log.md)
- [Decision log](decision-log.md)
- [Product roadmap](product-roadmap.md)
- [Stakeholder register and RACI](../01-discovery/stakeholder-register-raci.md)
- [Compliance mapping](../02-requirements/compliance-mapping.md)
- [Deployment and security architecture](../03-design/architecture/deployment-and-security.md)
- [Incident register](../07-operations/incident-register.csv)
- [INC-2026-007 Duplicate client invoices](../07-operations/incidents/INC-2026-007-duplicate-client-invoices.md)
- [INC-2026-011 False Location mismatch exceptions](../07-operations/incidents/INC-2026-011-false-location-mismatch-exceptions.md)
- [INC-2026-015 Escalation email to a deactivated user](../07-operations/incidents/INC-2026-015-escalation-email-to-deactivated-user.md)
