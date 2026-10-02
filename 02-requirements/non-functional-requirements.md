# Non-Functional Requirements: Tendwell

## Document control

| Field | Value |
|---|---|
| Document ID | TW-REQ-NFR |
| Version | 1.3 (aligned with SRS v1.3) |
| Status | Approved (baselined) |
| Owner | Business Analyst |
| Last updated | 2026-09-24 |
| Reviewers | Engineering Lead; QA Lead; UX Designer; Compliance and Privacy Officer; Product Owner |

**Purpose and scope.** This document elaborates the 29 canonical non-functional requirements summarized in [SRS section 3.4](SRS.md#34-non-functional-requirements). Each has:
- an ISO/IEC 25010 quality classification;
- a fit criterion, so pass or fail is unambiguous;
- the verification method and tool;
- a priority;
- the rationale, including the production incidents that shaped it.

The requirement wording is canonical and must not be paraphrased elsewhere.

## 1. Conventions

| Term | Meaning in this document |
|---|---|
| Quality classification | ISO/IEC 25010:2011 characteristic and sub-characteristic, written in US spelling. The 2023 revision renames Usability to Interaction capability and Portability to Flexibility, and adds Safety. The mapping will be refreshed when the team adopts it; the fit criteria do not change. |
| p95 | 95th percentile over the measurement window, measured server-side at the load balancer unless the criterion says "device" or "browser". |
| Tenant cluster | The set of API containers, workers and the database serving a group of tenants. R1 runs one cluster. |
| Reference devices | Mobile: an Android 10 device with 3 GB RAM and an iPhone on iOS 16. Web: a 4-core, 8 GB laptop running current Chrome. |
| Network profiles | Field: 1.5 Mbps and 150 ms round-trip time. Constrained: 400 kbps and 300 ms (NFR-MOB-01). Office: 25 Mbps and 40 ms. |
| Large-tenant dataset | Synthetic: 1,000 clients, 250 caregivers, 12 months of visits at about 15 visits per client per month. Built from the generators in [test data](../06-quality/test-data/README.md). |
| Priority | MoSCoW, as for functional requirements. A Must NFR that fails its fit criterion blocks release unless the Product Owner records a risk acceptance. |
| Verification methods | Inspection, Analysis, Demonstration, Test (ISO/IEC/IEEE 29148:2018). |

## 2. Summary

| ID | Category | ISO/IEC 25010 | Priority | Verification |
|---|---|---|---|---|
| NFR-PERF-01 | Performance | Performance efficiency: time behavior | Must | Test: k6 load test; production SLO |
| NFR-PERF-02 | Performance | Performance efficiency: time behavior | Must | Test: Detox timing on device farm; mobile tracing |
| NFR-PERF-03 | Performance | Performance efficiency: time behavior | Must | Test: Playwright performance marks |
| NFR-PERF-04 | Performance | Performance efficiency: time behavior, resource utilization | Must | Test: timed batch runs |
| NFR-AVL-01 | Availability | Reliability: availability | Must | Analysis: synthetic probes, monthly SLO report |
| NFR-AVL-02 | Availability | Reliability: fault tolerance | Must | Test: 72 h airplane-mode run; field demonstration |
| NFR-DR-01 | Disaster recovery | Reliability: recoverability | Must | Test: quarterly restore drill |
| NFR-SEC-01 | Security | Security: confidentiality, integrity | Must | Test: testssl.sh; Inspection: AWS Config, schema |
| NFR-SEC-02 | Security | Security (all sub-characteristics) | Must | Test: OWASP ZAP, SAST; Analysis: penetration test |
| NFR-SEC-03 | Security | Security: confidentiality | Must | Test: canary secret; Inspection: repo settings |
| NFR-SEC-04 | Security | Security: confidentiality, accountability | Must | Test: generated authorization tests; Demonstration: access review |
| NFR-PRIV-01 | Privacy | Security: confidentiality | Must | Test: template allow-list; Inspection: masking checklist |
| NFR-PRIV-02 | Privacy | Security: accountability, non-repudiation | Must | Inspection: retention configuration; Test: retrieval |
| NFR-PRIV-03 | Privacy | Portability: replaceability; Security: confidentiality | Must | Demonstration: export drill; Inspection: deletion certificate |
| NFR-USE-01 | Usability | Usability: operability | Must | Test: tap count; Demonstration: usability test |
| NFR-USE-02 | Usability | Usability: learnability | Should | Demonstration: moderated usability test |
| NFR-USE-03 | Usability | Usability: user error protection | Must | Inspection: content review; Test: UI assertions |
| NFR-ACC-01 | Accessibility | Usability: accessibility | Must | Test: axe-core; Demonstration: manual screen-reader test |
| NFR-SCL-01 | Scalability | Performance efficiency: capacity | Should | Analysis: capacity model; Test: k6 soak |
| NFR-OBS-01 | Observability | Maintainability: analyzability | Must | Test: log PHI scanner; Inspection: alert rules |
| NFR-OBS-02 | Observability | Maintainability: analyzability; Reliability: maturity | Must | Test: synthetic anomaly injection |
| NFR-MOB-01 | Mobile | Portability: adaptability, installability | Must | Test: device matrix, size budget, network shaping |
| NFR-MOB-02 | Mobile | Security: confidentiality | Must | Test: deactivation with queued punches; Inspection: storage |
| NFR-MNT-01 | Maintainability | Maintainability: testability | Must | Test: coverage gate; Inspection: RTM check |
| NFR-MNT-02 | Maintainability | Maintainability: modifiability; Reliability: availability | Must | Test: deploy-during-job test; migration compatibility test |
| NFR-CMP-01 | Compliance | Security: confidentiality | Must | Inspection: service inventory, BAA register |
| NFR-CMP-02 | Compliance | Compatibility: interoperability | Must | Test: golden files; Demonstration: aggregator validation |
| NFR-I18N-01 | Internationalization | Portability: adaptability | Must | Test: lint, pseudo-localization |
| NFR-DAT-01 | Data | Functional suitability: functional correctness | Must | Test: DST and boundary unit tests |

## 3. Performance

### NFR-PERF-01

| Attribute | Specification |
|---|---|
| Requirement | API p95 latency is at most 400 ms for reads and at most 800 ms for writes, at 300 concurrent users per tenant cluster. |
| ISO/IEC 25010 | Performance efficiency: time behavior |
| Fit criterion | k6 run: 5-minute ramp, then 30 minutes steady at 300 concurrent virtual users on one tenant cluster with the large-tenant dataset. Workload mix taken from pilot traffic: 75% reads, 25% writes. Pass: p95 at most 400 ms for GET, p95 at most 800 ms for POST, PUT and PATCH, error rate below 0.5%. Excluded: exports, billing runs and payroll summaries (NFR-PERF-04), and identity checks (NFR-PERF-02). The same thresholds are production SLOs over a rolling 28 days. |
| Verification | Test: k6 in the performance environment on every release candidate. Production SLO dashboards from OpenTelemetry traces in Grafana. |
| Priority | Must |
| Rationale | Coordinators work the schedule board and exception queue all day, often while on the phone with a caregiver. In discovery, screens that paused for more than a second pushed staff back to spreadsheets. |
| Related | FR-SCH-06, FR-EVV-08, NFR-SCL-01 |

### NFR-PERF-02

| Attribute | Specification |
|---|---|
| Requirement | Online clock-in/out round trip p95 is at most 2 s, excluding identity check. Identity check p95 is at most 4 s. |
| ISO/IEC 25010 | Performance efficiency: time behavior |
| Fit criterion | Measured on each reference device over the field network profile, 200 attempts per device. Clock-in or clock-out: from the tap on Clock in to the confirmation shown, p95 at most 2 s. Identity check: from selfie capture to result, p95 at most 4 s. Offline punches confirm locally and are not part of this measure. |
| Verification | Test: Detox end-to-end timing on a device farm with network shaping. Production: mobile trace spans per app version and OS. |
| Priority | Must |
| Rationale | Caregivers clock in at the client's door. A slow clock-in gets skipped or delayed, which shows up as Late start exceptions and manual corrections, working against OBJ-01. |
| Related | FR-EVV-01, FR-EVV-02, FR-EVV-04, IF-06 |

### NFR-PERF-03

| Attribute | Specification |
|---|---|
| Requirement | Schedule board week view with 500 visits loads in at most 2.5 s p95. |
| ISO/IEC 25010 | Performance efficiency: time behavior |
| Fit criterion | Week view of one location with 500 visits, browser cache cleared, from navigation to all visits rendered and interactive: p95 at most 2.5 s over 30 runs on the reference laptop with the office network profile. Changing a filter re-renders within 1 s p95. |
| Verification | Test: Playwright with performance marks, run nightly against the performance environment. |
| Priority | Must |
| Rationale | The schedule board is the Coordinator's home screen (PER-02). 500 visits is the busiest single-location week expected in the first year; larger agencies filter by location or service line. |
| Related | FR-SCH-06, NFR-USE-02 |

### NFR-PERF-04

| Attribute | Specification |
|---|---|
| Requirement | Billing run for 1,000 clients completes in at most 10 min. Payroll summary for 250 caregivers completes in at most 60 s. |
| ISO/IEC 25010 | Performance efficiency: time behavior, resource utilization |
| Fit criterion | Billing run: 1,000 clients and one month of Verified visits (about 15,000) take at most 10 minutes from job start to the last Draft invoice committed. Payroll summary: 250 caregivers for a bi-weekly period take at most 60 s from request to rendered summary. Both are measured on an environment sized like production. |
| Verification | Test: timed batch tests in the performance environment; durations read from `job_executions`. Production job-duration metrics alert at 80% of the budget. |
| Priority | Must |
| Rationale | Billing runs nightly and on demand at month end (OBJ-04). The payroll summary is interactive for the Billing & Payroll Specialist on period-end day (OBJ-02). |
| Related | FR-BIL-01, FR-PAY-02, FR-PAY-04 |

## 4. Availability and disaster recovery

### NFR-AVL-01

| Attribute | Specification |
|---|---|
| Requirement | 99.9% monthly availability (web and API). Planned maintenance is at most 4 h per month, announced 72 h ahead and kept outside 06:00-22:00 ET. |
| ISO/IEC 25010 | Reliability: availability |
| Fit criterion | Monthly availability is the share of minutes in which synthetic probes succeed, excluding announced maintenance. It must be at least 99.9%, which allows 43.2 minutes of unplanned downtime in a 30-day month. Probes run every 60 s from two locations: sign-in, a read API call and the clock-in health endpoint. Maintenance: at most 4 h a month, announced in-app and by email at least 72 h ahead, and scheduled outside 06:00-22:00 ET. |
| Verification | Analysis: monthly SLO report from probe data. Demonstration: the maintenance announcement flow. |
| Priority | Must |
| Rationale | Supported-living homes operate 24 hours a day, and Coordinators resolve exceptions in real time. The offline queue protects field capture (NFR-AVL-02) but not office work. The window is defined in ET, so for a Pacific-time tenant it falls 19:00-03:00 local. For that reason, maintenance never takes the punch sync endpoint offline. |
| Related | NFR-AVL-02, NFR-MNT-02 |

### NFR-AVL-02

| Attribute | Specification |
|---|---|
| Requirement | The mobile app captures EVV with no server connectivity for up to 72 hours of punches. |
| ISO/IEC 25010 | Reliability: fault tolerance |
| Fit criterion | With the network disabled for 72 h, the app captures at least 80 punches (40 visits) with their task results, notes, dose outcomes, vitals and up to 20 incident photos. Nothing is lost across app restarts, OS memory kills or device reboots. After reconnection, all items sync in capture order with their original capture times and no duplicates (idempotent by punch UUID). Punch data syncs within 60 s at 400 kbps; photos follow in the background. |
| Verification | Test: Detox with the network disabled, the device clock advanced 72 h and a reboot mid-run. Demonstration: field test on rural pilot routes. |
| Priority | Must |
| Rationale | Rural service areas, basements and apartment interiors lose signal. Blocking a clock-in for lack of signal would push caregivers back to paper. See [ADR-006](../03-design/architecture/adr/ADR-006-offline-first-caregiver-app.md) and [spec 001](../08-ai-assisted-ba/specs/001-offline-evv-capture/spec.md). |
| Related | FR-EVV-05, BR-025, NFR-MOB-02, TBD-03, TBD-04 |

### NFR-DR-01

| Attribute | Specification |
|---|---|
| Requirement | RPO at most 15 min and RTO at most 4 h; restores are tested quarterly. |
| ISO/IEC 25010 | Reliability: recoverability |
| Fit criterion | Quarterly drill restoring the database to a point in time, plus versioned S3 objects, into an isolated recovery account. Pass: measured data loss at most 15 minutes, and sign-in, schedule board and punch sync restored within 4 h of declaring the incident. Scenarios rotate across the year: accidental deletion or corruption, loss of an availability zone, and loss of the primary region. A failed drill opens a CAPA. |
| Verification | Test: restore drill. Analysis: drill report with timings, filed with the [incident management process](../07-operations/incident-management-process.md). |
| Priority | Must |
| Rationale | EVV, MAR and audit records are legal records. The mobile app keeps acknowledged punches for 24 h, so after a restore the server can ask devices to re-send them. This closes most of the 15-minute RPO gap for EVV. |
| Related | NFR-AVL-01, NFR-PRIV-02 |

## 5. Security

### NFR-SEC-01

| Attribute | Specification |
|---|---|
| Requirement | TLS 1.2+ in transit and AES-256 at rest. PHI uses field-level encryption with KMS keys rotated annually. |
| ISO/IEC 25010 | Security: confidentiality, integrity |
| Fit criterion | External scan of every public endpoint: only TLS 1.2 and 1.3 enabled, no weak cipher suites, HSTS max-age at least one year. All database instances, snapshots, S3 buckets and volumes encrypted with KMS keys (AWS Config rules 100% compliant). Every PHI field in the [data classification](../03-design/data/data-classification-and-retention.md) is envelope-encrypted. Automatic annual rotation is enabled on every customer-managed key. |
| Verification | Test: weekly testssl.sh scan in the pipeline. Inspection: AWS Config conformance pack and a schema review of encrypted columns. |
| Priority | Must |
| Rationale | Implements the HIPAA addressable encryption specifications (45 CFR 164.312(a)(2)(iv) and (e)(2)(ii)). Field-level encryption limits what a database read compromise exposes (BR-011). |
| Related | BR-011, NFR-MOB-02, [compliance mapping](compliance-mapping.md) |

### NFR-SEC-02

| Attribute | Specification |
|---|---|
| Requirement | Controls meet OWASP ASVS v4.0.3 Level 2. There is an annual third-party penetration test, and no open Critical or High findings at release. |
| ISO/IEC 25010 | Security: confidentiality, integrity, non-repudiation, accountability, authenticity |
| Fit criterion | ASVS 4.0.3 Level 2 checklist completed for each major release; every applicable requirement is Pass or has a risk acceptance from the Compliance and Privacy Officer. A third-party penetration test at least annually and before GA. Zero open Critical or High findings from the penetration test, SAST, DAST or dependency scanning at release. |
| Verification | Test: OWASP ZAP baseline scan in CI on every merge and an authenticated full scan weekly on staging; SAST and dependency scanning in CI. Inspection: ASVS checklist. Analysis: penetration test report and retest. |
| Priority | Must |
| Rationale | A multi-tenant PHI platform is a high-value target, and agency security questionnaires ask for ASVS evidence. ASVS 5.0 was published in 2025. R1 stays pinned to 4.0.3 for a stable baseline; the move is assessed for R2. |
| Related | NFR-SEC-01, NFR-SEC-04 |

### NFR-SEC-03

| Attribute | Specification |
|---|---|
| Requirement | No secrets in source control; CI secret scanning blocks the merge. |
| ISO/IEC 25010 | Security: confidentiality |
| Fit criterion | Push protection for secret scanning is enabled on every repository. A secret scanner runs on every pull request and blocks the merge on any finding. A canary secret planted in a quarterly control test is detected. A quarterly scan of full history finds zero live secrets. Runtime secrets come only from the cloud secrets manager. |
| Verification | Test: canary secret. Inspection: repository settings and pipeline configuration. |
| Priority | Must |
| Rationale | A leaked cloud key is one of the fastest paths to bulk PHI exposure in SaaS. Prevention at merge time is cheaper than rotation after the fact. |
| Related | NFR-SEC-02 |

### NFR-SEC-04

| Attribute | Specification |
|---|---|
| Requirement | Permissions default to deny, and Agency Administrators get a quarterly access-review report. |
| ISO/IEC 25010 | Security: confidentiality, accountability |
| Fit criterion | (a) Every operation in [openapi.yaml](../04-api/openapi.yaml) declares a required permission, and CI fails if one does not. Generated tests show a 403 for every operation when the caller lacks the permission. Cross-tenant reads return 404, so the existence of a record is not confirmed. (b) New role templates start with no permissions. (c) Within 5 business days of each quarter end, every Agency Administrator receives an access-review report listing users, roles, overrides, locations and last sign-in, flagging users inactive for more than 90 days. The administrator's attestation is written to the audit log. |
| Verification | Test: generated authorization tests. Demonstration: the access-review report and attestation. |
| Priority | Must |
| Rationale | Overrides and role assignments accumulate. INC-2026-015 showed that references to people outlive their need: there, a deactivated user was still cached as a notification recipient. CR-006 removed person references from escalation ladders; the access review catches the human side. |
| Related | FR-IAM-05, FR-IAM-06, BR-005, BR-054 |

## 6. Privacy

### NFR-PRIV-01

| Attribute | Specification |
|---|---|
| Requirement | Minimum necessary. PHI is masked in lists and notifications carry no PHI. |
| ISO/IEC 25010 | Security: confidentiality |
| Fit criterion | (a) Every list view masks date of birth, Medicaid ID, phone and address (UI inspection checklist). (b) SMS, push and email templates render only allow-listed variables: a test that injects a client name into every variable finds no occurrence in the rendered output. (c) The log scanner (NFR-OBS-01) finds no PHI. (d) Roles without a clinical need have no eMAR or clinical-documentation permission ([SRS section 3.3](SRS.md#33-role-permission-matrix)). |
| Verification | Test: template allow-list test and log scanner. Inspection: masking checklist and permission matrix. |
| Priority | Must |
| Rationale | HIPAA minimum necessary (45 CFR 164.502(b), 164.514(d)). INC-2026-015 sent an email containing a client's first name, last initial and incident category to a deactivated user's mailbox. CR-006 extended BR-056 to email bodies. |
| Related | FR-CLI-06, FR-NTF-05, BR-011, BR-056 |

### NFR-PRIV-02

| Attribute | Specification |
|---|---|
| Requirement | The PHI access audit trail is retained for 7 years. |
| ISO/IEC 25010 | Security: accountability, non-repudiation |
| Fit criterion | Audit events, including PHI reveals with their reasons and exports, are retained at least 7 years. The application's database role has no UPDATE or DELETE on `audit_events`. Monthly partitions are archived to object storage with a compliance-mode retention lock of 7 years. Any event is retrievable within 1 business day. |
| Verification | Inspection: database grants and storage retention configuration. Test: an annual retrieval test of a 6-year-old event from the archive (using seeded archive data until production data is that old). |
| Priority | Must |
| Rationale | Seven years exceeds the six-year HIPAA documentation retention period and matches the default client-record retention (BR-013). An append-only, locked store makes the trail credible in an investigation. How retention interacts with tenant deletion is TBD-17. |
| Related | FR-RPT-03, BR-057, NFR-PRIV-03 |

### NFR-PRIV-03

| Attribute | Specification |
|---|---|
| Requirement | A full tenant data export is delivered within 5 business days of request. Data is deleted within 90 days of cancellation, with a deletion certificate. |
| ISO/IEC 25010 | Portability: replaceability (export); Security: confidentiality (deletion) |
| Fit criterion | Export: on request by an Agency Administrator, or automatically at cancellation, a complete export (every table in CSV and JSON, every document and photo, a manifest and SHA-256 checksums) is ready to download within 5 business days. Deletion: primary data is deleted on day 90 after cancellation, and backups expire within the following 35 days. A deletion certificate lists what was deleted, the backup expiry date and anything retained, and why (TBD-17). |
| Verification | Demonstration: a quarterly export drill with a test tenant. Inspection: deletion job logs and the certificate. |
| Priority | Must |
| Rationale | The BAA requires PHI to be returned or destroyed at termination. Agencies must be able to leave with their records, and doing so is part of their own retention obligation. |
| Related | FR-ONB-07, BR-013, NFR-PRIV-02 |

## 7. Usability and accessibility

### NFR-USE-01

| Attribute | Specification |
|---|---|
| Requirement | A caregiver clocks in within 3 taps from app open for the next visit today. |
| ISO/IEC 25010 | Usability: operability |
| Fit criterion | From launching the app (signed in, inside the 12-hour window) on the Today screen, the next visit today is clocked in with at most 3 taps: open the visit card, Clock in, confirm. OS permission prompts and the selfie capture are excluded. In a usability test with at least 8 caregivers, 90% or more complete it unaided, including at 200% font size. |
| Verification | Test: automated tap-count test. Demonstration: usability test. |
| Priority | Must |
| Rationale | PER-01 clocks in on a doorstep with one hand free. Every extra tap is a reason to clock in later. |
| Related | FR-EVV-01, NFR-PERF-02, NFR-ACC-01 |

### NFR-USE-02

| Attribute | Specification |
|---|---|
| Requirement | After 30 minutes or less of training, at least 90% of new Coordinators schedule a recurring visit unaided in usability testing. |
| ISO/IEC 25010 | Usability: learnability |
| Fit criterion | Moderated test with at least 10 participants who have scheduling experience but are new to Tendwell, after a standard training session of 30 minutes or less. Task: create a Monday, Wednesday and Friday 08:00-10:00 pattern for client C-10234 with caregiver E-2041 for 8 weeks, and resolve one compliance warning. Success means saved correctly within 10 minutes with no facilitator help. Pass: 90% or more succeed. Secondary measure: a System Usability Scale score of 70 or more. |
| Verification | Demonstration: usability test run by the UX Designer; results in the test summary report. |
| Priority | Should |
| Rationale | Coordinator turnover is high, and onboarding time is a cost the agency feels directly. |
| Related | FR-SCH-01, FR-SCH-03, US-020 |

### NFR-USE-03

| Attribute | Specification |
|---|---|
| Requirement | Every validation message states the problem and the fix, and no raw error codes are shown. |
| ISO/IEC 25010 | Usability: user error protection |
| Fit criterion | Every validation and error message in the string catalog states the problem and the fix; the UX Designer and Business Analyst sign this off each release. Every API error code in [api-guidelines.md](../04-api/api-guidelines.md) maps to a user-facing message. Automated UI tests assert that no displayed error contains an HTTP status number, an error-code constant or a stack trace. |
| Verification | Inspection: content review. Test: UI assertions. |
| Priority | Must |
| Rationale | A caregiver cannot call the office for every error. Pilot support tickets clustered on messages that named a problem without saying what to do. The field specifications in [SRS section 3.2](SRS.md#32-functional-requirements) are the reference wording. |
| Related | All field-level specifications in the SRS |

### NFR-ACC-01

| Attribute | Specification |
|---|---|
| Requirement | The web app meets WCAG 2.2 AA. The mobile app supports 200% font scaling and screen readers. |
| ISO/IEC 25010 | Usability: accessibility |
| Fit criterion | **Web:** zero axe-core violations for WCAG 2.2 A and AA rules on every route in CI, and a manual audit each release of 12 critical journeys, keyboard-only and with NVDA and VoiceOver. The criteria new in WCAG 2.2 are tested explicitly: 2.4.11 Focus Not Obscured (Minimum), 2.5.7 Dragging Movements (the schedule board's drag-and-drop has a menu alternative), 2.5.8 Target Size (Minimum), 3.3.7 Redundant Entry, and 3.3.8 Accessible Authentication (Minimum), with paste allowed in password and code fields. **Mobile:** every screen is usable at 200% system font size without truncated actions, and every flow works with TalkBack and VoiceOver. An Accessibility Conformance Report is published per release. |
| Verification | Test: axe-core through Playwright. Demonstration: manual screen-reader and keyboard audit. |
| Priority | Must |
| Rationale | The caregiver workforce includes older workers and people with low vision. The HHS Section 504 rule of 2024 adopts WCAG 2.1 AA for the web content and mobile apps of recipients of HHS funding, which includes many agencies; WCAG 2.2 AA exceeds it. See the [compliance mapping](compliance-mapping.md). |
| Related | NFR-USE-01, SRS section 3.1.1 |

## 8. Scalability

### NFR-SCL-01

| Attribute | Specification |
|---|---|
| Requirement | Scales to 500 tenants, 50,000 caregivers and 2 million visits per month without redesign. |
| ISO/IEC 25010 | Performance efficiency: capacity |
| Fit criterion | A capacity model, reviewed quarterly, shows headroom for each component at the target. At 2 million visits a month, that is about 66,700 visits and 133,000 punches a day. Assuming 20% of punches in the peak hour and a 5x burst at the top of the hour, the peak is about 37 punches per second. Nightly materialization adds about 67,000 visits. `evv_punches` and `audit_events` are partitioned monthly. A k6 soak test at 20% of target shows linear scaling. "Without redesign" means no change to the tenancy model, primary keys or API contract. |
| Verification | Analysis: capacity model. Test: k6 soak test at 20% scale. |
| Priority | Should |
| Rationale | The target is the three-year growth plan after GA. Proving the shape now avoids a rewrite of the tenancy and partitioning design later. |
| Related | NFR-PERF-01, [ADR-001](../03-design/architecture/adr/ADR-001-multi-tenancy-row-level-security.md) |

## 9. Observability

### NFR-OBS-01

| Attribute | Specification |
|---|---|
| Requirement | Structured logs carry correlation IDs and no PHI. Every request is traced, and alerts fire on SLO burn rate. |
| ISO/IEC 25010 | Maintainability: analyzability |
| Fit criterion | Every inbound request carries W3C trace context, propagated to logs, jobs and outbound calls. Logs are structured JSON with correlation ID, tenant ID and user ID (UUIDs only). A scanner runs in CI on test logs and daily on a production sample, and finds no match for PHI patterns (the Medicaid ID format, date-of-birth fields, and the names of a canary client). SLO burn-rate alerts use multiple windows (for example 2% of the error budget in 1 h, or 5% in 6 h) and page on-call through PagerDuty. |
| Verification | Test: the log scanner and the alert rules, with a synthetic burn. Inspection: logging configuration. |
| Priority | Must |
| Rationale | Logs are copied into more tools than the database is, so they must never become a PHI store. Tracing makes support possible without looking at client data. |
| Related | NFR-PRIV-01, NFR-OBS-02 |

### NFR-OBS-02

| Attribute | Specification |
|---|---|
| Requirement | Business anomaly alerts fire when: a billing run's invoice count deviates more than 20% from the previous run; or the EVV exception rate exceeds 2x the 7-day baseline; or a notification goes to a deactivated user (target is 0). |
| ISO/IEC 25010 | Maintainability: analyzability; Reliability: maturity |
| Fit criterion | Each condition has an alert rule that fires within 10 minutes. (a) Invoice count for a tenant's billing run deviates by more than 20% from that tenant's previous run: page on-call and pause auto-issue for the run until acknowledged. (b) EVV exception rate above 2x the 7-day baseline, computed per tenant and per app version and OS: page on-call. (c) Any notification addressed to a deactivated user: block the send and page on-call as SEV-2; the target count is 0. Each rule is tested quarterly by injecting a synthetic anomaly in staging. |
| Verification | Test: synthetic anomaly injection and a game day. |
| Priority | Must |
| Rationale | Business failures can look healthy to technical monitoring. INC-2026-007 (duplicate invoices) was found through a customer support ticket after 37 duplicates were emailed and 6 clients paid twice ($2,914.50 refunded). INC-2026-011 flagged 41% of iOS clock-ins for 3 days (1,180 exceptions) before anyone saw the pattern. INC-2026-015 sent PHI to a deactivated user. Each would have paged within minutes under this NFR. |
| Related | FR-BIL-01, FR-EVV-07, FR-NTF-03, CR-004, CR-005, CR-006 |

## 10. Mobile

### NFR-MOB-01

| Attribute | Specification |
|---|---|
| Requirement | The mobile app supports iOS 16+ and Android 10+, is 60 MB or smaller, and is usable at 400 kbps or more. |
| ISO/IEC 25010 | Portability: adaptability, installability; Performance efficiency: resource utilization |
| Fit criterion | Release regression passes on a matrix of at least 10 devices, covering iOS 16 to current and Android 10 to current, including a low-end Android device with 3 GB RAM. The matrix covers every location permission state: precise, approximate (iOS Precise Location off; Android approximate only), denied, and ask-next-time. Download size is at most 60 MB as reported by the stores. Core flows (sign-in, Today list, clock-in and out, dose outcome, sync) complete at 400 kbps and 300 ms with no timeouts. |
| Verification | Test: device farm regression, network shaping, and a size budget check in CI. |
| Priority | Must |
| Rationale | INC-2026-011 got through because the QA device matrix lacked the approximate-location setting. PER-01 uses a mid-range Android phone on a limited data plan. |
| Related | FR-EVV-02, BR-022, CR-004 |

### NFR-MOB-02

| Attribute | Specification |
|---|---|
| Requirement | The offline queue is encrypted, and local data is remotely wiped on deactivation. |
| ISO/IEC 25010 | Security: confidentiality |
| Fit criterion | The offline queue is stored only in SQLCipher (AES-256), with its key in iOS Keychain or Android Keystore. There is no PHI in plain files or OS logs, and the screen is obscured in the app switcher. On deactivation, the server revokes tokens at once. At the device's next contact, the app first uploads pending punches captured before the deactivation time, then wipes the database, keys and cached files within 60 s. |
| Verification | Test: deactivate a user who has queued offline punches, and confirm sync then wipe. Inspection: storage and key configuration; mobile penetration test. |
| Priority | Must |
| Rationale | Phones get lost and staff leave. Uploading before wiping protects the EVV record of work already done. Residual risk: a device that never reconnects keeps encrypted data for its assigned visits, behind the device lock. Mobile device management is the agency's responsibility (45 CFR 164.310(d)(1)). |
| Related | FR-WRK-06, FR-EVV-05, NFR-AVL-02 |

## 11. Maintainability

### NFR-MNT-01

| Attribute | Specification |
|---|---|
| Requirement | Domain modules (EVV, payroll, billing, eMAR) have at least 80% line coverage, and every BR has at least one automated test. |
| ISO/IEC 25010 | Maintainability: testability |
| Fit criterion | A CI gate requires line coverage of at least 80% in each of the EVV, payroll, billing and eMAR modules. An RTM check in CI fails the release candidate if any business rule from BR-001 to BR-058 lacks a linked automated test that passed on that candidate. |
| Verification | Test: coverage tooling. Inspection: the [traceability matrix](requirements-traceability-matrix.md) check. |
| Priority | Must |
| Rationale | These modules carry money and clinical risk, and their rules change by CR. Coverage alone does not prove correctness; the link from rule to test is the stronger half. |
| Related | All BRs; [test strategy](../06-quality/test-strategy-and-plan.md) |

### NFR-MNT-02

| Attribute | Specification |
|---|---|
| Requirement | Deployments have zero downtime. Migrations are backward-compatible for one release, and scheduled jobs are single-flight across deployments. |
| ISO/IEC 25010 | Maintainability: modifiability; Reliability: availability |
| Fit criterion | (a) No failed synthetic-probe request attributable to a deployment over a quarter. (b) Every migration follows expand and contract: CI runs the previous release's test suite against the new schema. (c) Single-flight test: start two scheduler workers during a deployment and trigger the billing run for the same tenant and period. Exactly one `job_executions` row completes; the other exits with no side effects. The unique constraint on `invoices.idempotency_key` would reject a second insert anyway (defense in depth, CR-005). |
| Verification | Test: a deploy-during-job test and a migration compatibility test. |
| Priority | Must |
| Rationale | INC-2026-007: two scheduler workers both took leadership during a deployment overlap and ran billing twice. See [ADR-003](../03-design/architecture/adr/ADR-003-single-flight-scheduled-jobs.md). |
| Related | FR-BIL-01, BR-050, NFR-OBS-02 |

## 12. Compliance

### NFR-CMP-01

| Attribute | Specification |
|---|---|
| Requirement | Only HIPAA-eligible services are used, under a BAA, and Tendwell Labs signs a BAA with each agency. |
| ISO/IEC 25010 | Security: confidentiality |
| Fit criterion | (a) A per-release inventory check confirms every cloud service that stores or processes PHI is on the provider's HIPAA-eligible list. (b) The vendor register shows a signed BAA for every subprocessor that receives PHI (hosting, email, identity verification vendor). Vendors designed to receive no PHI (push, SMS bodies, maps, payments) are listed with the control that keeps it out ([SRS section 3.1.3](SRS.md#313-software-interfaces)). (c) A signed BAA exists for every tenant before activation; it is accepted at sign-up and the version is stored. |
| Verification | Inspection: service inventory, vendor register and BAA register. |
| Priority | Must |
| Rationale | Tendwell Labs is a business associate of each agency (45 CFR 164.502(e), 164.504(e)). Keeping PHI out of a channel by design is stronger than relying on a vendor's BAA. |
| Related | IF-01 to IF-10, BR-056 |

### NFR-CMP-02

| Attribute | Specification |
|---|---|
| Requirement | EVV data export is available in a configurable aggregator CSV format. State-specific formats come in R2. |
| ISO/IEC 25010 | Compatibility: interoperability |
| Fit criterion | The EVV export produces a CSV in a tenant-configured layout (column order, headers, date and time format and zone, delimiter, code mappings). It contains the six Cures Act elements, visit status, exceptions and reason codes. Each layout has a golden-file test. For the pilot state's aggregator, a sample month passes the aggregator's validation with zero rejected rows. State-specific formats are R2 (TBD-12). |
| Verification | Test: golden files. Demonstration: aggregator validation with a pilot agency. |
| Priority | Must |
| Rationale | Agencies must submit EVV to their state. A configurable layout serves the pilot without committing R1 to every state's format. |
| Related | BR-020, IF-09, [compliance mapping](compliance-mapping.md) |

## 13. Internationalization and data

### NFR-I18N-01

| Attribute | Specification |
|---|---|
| Requirement | UI strings are externalized. R1 is English; Spanish for the caregiver app comes in R2. |
| ISO/IEC 25010 | Portability: adaptability |
| Fit criterion | A lint rule blocks hard-coded user-facing strings in web and mobile code (zero violations). A pseudo-localized build (40% longer strings, accented characters) passes visual review on the 20 most-used screens with no truncation and no untranslated text. Dates, numbers and currency are formatted through locale APIs. R2 adds es-US to the caregiver app. |
| Verification | Test: lint and pseudo-localization. Inspection: visual review. |
| Priority | Must |
| Rationale | Many caregivers are bilingual or Spanish-first (PER-01). Externalizing strings in R1 makes R2 a translation task, not a refactor. |
| Related | SRS section 3.1.1 |

### NFR-DAT-01

| Attribute | Specification |
|---|---|
| Requirement | Timestamps are stored in UTC and shown in the tenant time zone. Durations that cross DST changes are computed correctly. |
| ISO/IEC 25010 | Functional suitability: functional correctness |
| Fit criterion | Every timestamp column is stored in UTC. The API returns ISO 8601 with an offset, and the UI renders in the tenant time zone. Tests in America/New_York: (a) 2026-10-31 22:00 to 2026-11-01 07:00 is 10.0 h worked and 40 billing units; (b) 2026-03-07 22:00 to 2026-03-08 07:00 is 8.0 h; (c) a pattern start of 02:30 on 2026-03-08, which does not exist, moves to 03:00 with a warning, and 01:30 on 2026-11-01 resolves to the first occurrence; (d) holidays, workweeks and pay periods use tenant-local dates. |
| Verification | Test: unit and property-based tests on time arithmetic. |
| Priority | Must |
| Rationale | FLSA pays actual hours and payers pay actual units. DST errors are silent: an overnight shift paid 9 h instead of 10 is underpayment nobody sees. |
| Related | BR-041, BR-045, BR-047 |

## 14. NFRs shaped by production incidents

| Incident | NFR | What changed |
|---|---|---|
| INC-2026-007, duplicate client invoices (SEV-2) | NFR-OBS-02 (a); NFR-MNT-02 (c) | Invoice-count anomaly alert with auto-issue pause; a single-flight test under deployment overlap. With CR-005 (database uniqueness). |
| INC-2026-011, false Location mismatch exceptions (SEV-2) | NFR-OBS-02 (b); NFR-MOB-01 | Exception-rate alert sliced by app version and OS; approximate location added to the device matrix. With CR-004. |
| INC-2026-015, escalation email to a deactivated user (SEV-1, privacy) | NFR-OBS-02 (c); NFR-PRIV-01; NFR-SEC-04 | Send-time block and alert; the template allow-list covers email; the access review flags inactive users. With CR-006. |

Post-incident reviews: [INC-2026-007](../07-operations/incidents/INC-2026-007-duplicate-client-invoices.md), [INC-2026-011](../07-operations/incidents/INC-2026-011-false-location-mismatch-exceptions.md), [INC-2026-015](../07-operations/incidents/INC-2026-015-escalation-email-to-deactivated-user.md).

## Related documents

- [Software Requirements Specification](SRS.md)
- [Business rules](business-rules.md)
- [Compliance mapping](compliance-mapping.md)
- [Glossary](glossary.md)
- [Requirements traceability matrix](requirements-traceability-matrix.md)
- [Deployment and security architecture](../03-design/architecture/deployment-and-security.md)
- [Data classification and retention](../03-design/data/data-classification-and-retention.md)
- [Test strategy and plan](../06-quality/test-strategy-and-plan.md)
- [Incident management process](../07-operations/incident-management-process.md)
