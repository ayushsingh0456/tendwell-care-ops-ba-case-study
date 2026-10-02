# Glossary: Tendwell

## Document control

| Field | Value |
|---|---|
| Document ID | TW-REQ-GLO |
| Version | 1.3 (aligned with SRS v1.3) |
| Status | Approved (baselined) |
| Owner | Business Analyst |
| Last updated | 2026-09-24 |
| Reviewers | Product Owner; Clinical SME (RN advisor); Compliance and Privacy Officer; Engineering Lead |

**Purpose and scope.** This glossary defines 114 domain, regulatory and technical terms used across the Tendwell case study, so that requirements, stories, tests and conversations mean the same thing.
- Where a term is governed by a business rule or requirement, the definition cites it, and the rule wins if they ever differ.
- Regulatory definitions are summarized for readability. The cited regulation is authoritative.
- Requirement IDs follow the conventions in [SRS section 1.4](SRS.md#14-definitions-acronyms-and-conventions).

**Index:** [0-9](#0-9) | [A](#a) | [B](#b) | [C](#c) | [D](#d) | [E](#e) | [F](#f) | [G](#g) | [H](#h) | [I](#i) | [K](#k) | [L](#l) | [M](#m) | [N](#n) | [O](#o) | [P](#p) | [Q](#q) | [R](#r) | [S](#s) | [T](#t) | [U](#u) | [V](#v) | [W](#w)

### 0-9

| Term | Definition |
|---|---|
| **837P** | The HIPAA X12 electronic claim transaction for professional services. Out of R1 scope; Tendwell exports a claim batch CSV for the agency's clearinghouse instead (FR-BIL-06). |

### A

| Term | Definition |
|---|---|
| **Accrual** | Leave earned in proportion to time worked. The Tendwell default is 1 h of PTO per 30 h worked, capped at an 80 h balance (BR-040). |
| **Addendum** | A signed, time-stamped addition to a locked visit note that never changes the original text (BR-035). Plural: addenda. |
| **ADL (activities of daily living)** | Basic self-care tasks: bathing, dressing, toileting, transferring, continence and eating. Care-plan tasks are categorized ADL, IADL or Clinical. |
| **Administration window** | The period around a scheduled dose in which documenting it counts as on time. Scheduled time plus or minus 60 minutes by default, configurable per order from 15 to 120 minutes (BR-029). |
| **Advisory credential** | A credential type whose expiry produces scheduling warnings but never blocks assignment (FR-WRK-03). Contrast: blocking credential. |
| **Append-only** | A storage pattern in which records are added but never updated or deleted. Used for EVV punches, audit events and note addenda (ADR-002). |
| **AR ageing** | An accounts receivable report that groups unpaid invoice balances by days past due (FR-RPT-02). |
| **Audit event** | An immutable record of who did what to which record, when, from which IP address and device, with before and after values. Retained 7 years (BR-057). |
| **Authorization overrun** | Delivering or billing more units than a service authorization allows. A leading cause of payer denials (OBJ-06). |
| **Auto-close** | The automatic closing of a visit still open 14 hours after clock-in, with the scheduled end as a placeholder clock-out and an Auto-closed exception that holds it out of pay and billing (BR-027). |

### B

| Term | Definition |
|---|---|
| **BA** | In this repository BA means Business Analyst. "Business associate" is always written out to avoid confusion. |
| **BAA (business associate agreement)** | The contract HIPAA requires before a business associate handles PHI for a covered entity, and between a business associate and its own subcontractors. Tendwell Labs signs one with each agency (NFR-CMP-01). |
| **Billing model** | How an authorization is priced: Hourly (15-minute units), Per visit, Daily or Fixed monthly (BR-047, BR-048). |
| **Billing run** | A batch job that creates or updates Draft invoices for a period from Verified visits. Idempotent per tenant, client, payer and period (BR-050). |
| **Blocking credential** | A credential type that, once Expired, stops the caregiver from being assigned new visits (FR-WRK-03, BR-014). |
| **Breach (HIPAA)** | An acquisition, access, use or disclosure of PHI not permitted by the Privacy Rule that compromises its security or privacy. It is presumed to be a breach unless a four-factor risk assessment shows a low probability of compromise (45 CFR 164.402). |
| **Business associate** | A person or organization that creates, receives, maintains or transmits PHI on behalf of a covered entity. Tendwell Labs is a business associate of each agency. |

### C

| Term | Definition |
|---|---|
| **CAPA (corrective and preventive action)** | Actions that remove the cause of a problem and prevent it recurring. Used for client incidents (FR-DOC-05) and for failed recovery drills. |
| **Care plan** | The versioned, supervisor-approved set of tasks a client receives per visit type. A visit uses the version that was Active at clock-in (BR-012). |
| **Care-plan task** | An ADL, IADL or clinical task that the caregiver marks Done, or Not done with a reason, at clock-out (FR-EVV-06). |
| **Claim batch** | A CSV file of billable services for one payer and period, submitted by the agency through its clearinghouse (FR-BIL-06). |
| **Clearinghouse** | An intermediary that checks healthcare claims and forwards them from providers to payers, then returns payer responses. |
| **Client incident** | An event that affects a client's safety or wellbeing (fall, injury, medication error, behavioral event, suspected abuse or neglect, property damage) reported under FR-DOC-03. Not the same as a production incident (INC-), which is a service failure. |
| **Clock-in and clock-out** | The EVV punches that start and end a visit, each with time, location, accuracy and device data (FR-EVV-01, FR-EVV-02). |
| **Correlation ID** | An identifier carried on every log line and trace span of one request so it can be followed across services (NFR-OBS-01). |
| **Covered entity** | A health plan, a healthcare clearinghouse, or a healthcare provider that transmits health information electronically in a HIPAA standard transaction. Care agencies that bill Medicaid electronically are covered entities. |
| **Credential** | A license, certification, screening or training record with an issue date and, usually, an expiry date. Examples: CPR certification, TB test, background check (FR-WRK-02). |
| **Credit note** | A document that reduces the balance of an issued invoice, with a reason. With void-and-reissue, the only way to correct an issued invoice (BR-051). |

### D

| Term | Definition |
|---|---|
| **Daily overtime profile** | An optional tenant setting for states with daily overtime rules: over 8 h a day at 1.5x and over 12 h at 2.0x (CR-001, BR-041). |
| **Decision table** | A table that maps combinations of input conditions to outcomes, with a stated hit policy (Unique, First or Collect). See business-rules.md. |
| **Deduplication key** | Event ID plus recipient plus escalation step. A notification whose key has already been sent is suppressed (BR-055). |
| **Deep link** | A link that opens a specific screen and requires sign-in, so a message can point to PHI without containing it (BR-056). |
| **DOL Home Care Rule** | The US Department of Labor's 2013 final rule, effective 2015, that extended FLSA minimum wage and overtime to most home care workers employed by third-party agencies. |
| **DST (daylight saving time)** | The seasonal clock change. In 2026, America/New_York changes on 2026-03-08 and 2026-11-01. Tendwell computes durations on elapsed time (NFR-DAT-01). |

### E

| Term | Definition |
|---|---|
| **Effective permissions** | Role-template permissions, plus granted overrides, minus denied overrides; a deny always wins (BR-005). |
| **Effective-dated** | Valid from a given date, so history keeps the value in force at the time. Used for pay rates (BR-015). |
| **eMAR** | Electronic medication administration record: Tendwell's digital record of medication orders, scheduled doses and their outcomes (EP-07). |
| **Envelope encryption** | Encrypting data with a data key that is itself encrypted by a master key held in a key management service. Used for PHI fields (NFR-SEC-01). |
| **ePHI** | Electronic protected health information: PHI created, received, maintained or transmitted electronically. The subject of the HIPAA Security Rule. |
| **Escalation ladder** | A tenant-configured sequence of notification steps for one event type, each with a delay, recipient role and channels. It stops when the triggering condition resolves (FR-NTF-03). |
| **EVV aggregator** | A state system that collects EVV data from agencies' own EVV systems. Tendwell exports a configurable CSV for it (NFR-CMP-02). |
| **EVV (electronic visit verification)** | Electronic capture of the six data elements that the 21st Century Cures Act section 12006 requires for Medicaid personal care and home health services: type of service, individual receiving it, date, location, individual providing it, and begin and end time (BR-020). |
| **EVV exception** | A flag on a visit that must be resolved or waived, with a reason code, before the visit can be Verified. Examples: Late start, Location mismatch, Low GPS accuracy (FR-EVV-07). |

### F

| Term | Definition |
|---|---|
| **FLSA** | The Fair Labor Standards Act: the federal law on minimum wage, overtime and hours worked. |

### G

| Term | Definition |
|---|---|
| **Geocoding** | Converting an address into latitude and longitude (IF-05). |
| **Geofence** | A circle around the client's service address (default radius 150 m, configurable 50-500 m) used to evaluate punch location on the server (BR-021). |
| **GPS accuracy** | The horizontal accuracy radius a device reports with a location fix. Worse than 100 m raises Low GPS accuracy instead of Location mismatch (BR-022). |

### H

| Term | Definition |
|---|---|
| **Hard block** | A scheduling compliance result that prevents saving and cannot be overridden (FR-SCH-03). Contrast: warning. |
| **HCBS (home and community-based services)** | Medicaid long-term services delivered in a person's home or community rather than in an institution. |
| **HCPCS** | Healthcare Common Procedure Coding System. Level II codes identify services on authorizations and claims; for example T1019 (personal care, per 15 minutes), S5125 (attendant care, per 15 minutes) and S5102 (adult day care, per diem). SL-DAY in the samples is an agency-defined code, not HCPCS. |
| **HIPAA** | The Health Insurance Portability and Accountability Act of 1996. Its Privacy, Security and Breach Notification Rules (45 CFR Parts 160 and 164) govern PHI. |
| **Holiday-worked hours** | Hours worked on a tenant holiday, paid at 1.5x by default for holiday-eligible caregivers, never stacked with overtime (BR-042). |

### I

| Term | Definition |
|---|---|
| **IADL (instrumental activities of daily living)** | Tasks needed to live independently: meal preparation, housekeeping, laundry, shopping, medication reminders and arranging transport. |
| **ICD-10-CM** | The International Classification of Diseases, 10th Revision, Clinical Modification: the US diagnosis code set recorded on client records and claims (FR-CLI-01). |
| **Idempotency** | The property that repeating an operation has the same effect as doing it once. Tendwell uses an Idempotency-Key header on unsafe POSTs, a unique key per billing run (BR-050) and per scheduled job (ADR-003). |
| **Identity check** | A selfie liveness and face-match check against the caregiver's enrolled reference. A pass is valid for 90 seconds and one punch (FR-EVV-04, BR-024). |

### K

| Term | Definition |
|---|---|
| **KMS (key management service)** | A managed service that holds the master keys used for envelope encryption. Keys are rotated annually (NFR-SEC-01). |

### L

| Term | Definition |
|---|---|
| **Late entry** | A dose outcome recorded after its administration window closed but within 24 hours of the scheduled time. It is labelled as such on the MAR (BR-031). |
| **Late offline sync** | The exception raised when a punch reaches the server more than 24 hours after it was captured (BR-025). |
| **Liveness** | A check that a selfie comes from a live person in front of the camera, not a photo, screen or mask. |
| **Location** | An agency branch or office. Clients, staff and data are scoped to locations (FR-IAM-06). |
| **Location scoping** | Limiting a user's data to the locations assigned to them (FR-IAM-06). |

### M

| Term | Definition |
|---|---|
| **MAR** | Medication administration record: the per-client record of each scheduled dose and its outcome. Tendwell prints a monthly MAR grid (FR-MAR-09). |
| **Medicaid ID** | The state-issued member identifier for a Medicaid client. PHI; synthetic samples use ZZ followed by 8 digits. |
| **MFA (multi-factor authentication)** | Sign-in with a second factor, either an authenticator-app TOTP or an SMS code. Mandatory for the roles listed in BR-006. |
| **Mileage reimbursement** | Miles between consecutive visits times the tenant's rate, for mileage-eligible caregivers. A reimbursement, not wages; it never changes hours (BR-044). |
| **Minimum necessary** | The HIPAA standard that limits PHI uses, disclosures and requests to the minimum needed for the purpose (45 CFR 164.502(b), 164.514(d)). |
| **Missed - undocumented** | The dose status set when no outcome is recorded 60 minutes after the administration window closes. It sends an urgent alert to the Clinical Supervisor (BR-030). |
| **MoSCoW** | The prioritization scheme Must, Should, Could, Won't (this release). |

### N

| Term | Definition |
|---|---|
| **Net 30** | Payment due 30 days after the invoice date; the Tendwell default (BR-052). |
| **NIST SP 800-63B** | The NIST guideline on authentication and authenticator management; the basis of Tendwell's password rules (BR-007). |
| **Non-exempt** | An employee entitled to FLSA minimum wage and overtime. Agency-employed caregivers are non-exempt under the DOL Home Care Rule; in Tendwell this is the pay profile's overtime-eligible flag. |

### O

| Term | Definition |
|---|---|
| **OIDC (OpenID Connect)** | An identity layer on OAuth 2.0. Used by Tendwell's managed identity provider (IF-10). |
| **Open shift** | An unassigned visit offered to eligible caregivers to claim. The first eligible claim wins, optionally confirmed by a Coordinator (FR-SCH-05, CR-002). |
| **Overtime** | Hours worked over 40 in the workweek, paid at 1.5x to overtime-eligible caregivers, plus optional daily overtime (BR-041). |
| **OWASP ASVS** | The OWASP Application Security Verification Standard. Tendwell targets version 4.0.3, Level 2 (NFR-SEC-02). |

### P

| Term | Definition |
|---|---|
| **Pay period** | The span of a payroll run (weekly, bi-weekly or semi-monthly per tenant). It is locked when exported (FR-PAY-01, BR-046). |
| **Payer** | An organization that pays for client services: Medicaid, Medicaid managed care, long-term care insurance, private pay or the VA. |
| **Per diem** | (1) A daily billing unit, such as adult day care billed per day (Daily billing model). (2) An employment type for as-needed staff with no fixed hours. |
| **PHI (protected health information)** | Individually identifiable health information held or transmitted by a covered entity or business associate, in any form. In Tendwell: client names linked to services, date of birth, Medicaid ID, diagnoses, medications, service address and incident details. |
| **PHI reveal** | Unmasking a masked PHI field after entering a reason. Every reveal is audited (FR-CLI-06). |
| **Platform Console** | The web application Tendwell Labs staff use to manage plans, promo codes and the tenant lifecycle. |
| **Pre-signed URL** | A time-limited URL that grants access to one stored object without other credentials. Used for documents and photos. |
| **PRN (pro re nata)** | "As needed": medication given for a stated indication, limited by a maximum number of doses in any 24 hours and a minimum interval (FR-MAR-05, BR-033). |
| **Problem details (RFC 9457)** | The standard JSON error format (`application/problem+json`) that the Tendwell API returns. |
| **Proration** | Charging part of a fixed monthly rate for a partial month: rate times active days divided by days in the month (BR-048). |
| **Punch** | One EVV record of type In or Out in the append-only punch ledger, from source Mobile, MobileOffline, Manual or System. |

### Q

| Term | Definition |
|---|---|
| **Quiet hours** | 21:00-07:00 tenant local time, during which non-urgent push, SMS and email notifications are held (BR-053). |

### R

| Term | Definition |
|---|---|
| **Read-only state** | The tenant state that starts 7 days after trial expiry or after the third failed payment retry. Users can view and export but not create or edit; care is never blocked (BR-003). |
| **Reason code** | A tenant-defined code that explains a correction, waiver, cancellation or not-done task. |
| **Reportable incident** | A client incident that must be reported to an external authority within a deadline (BR-036). |
| **RLS (row-level security)** | A PostgreSQL feature that filters rows per session. Used to isolate tenants (BR-001, ADR-001). |
| **Role template** | A default set of permissions for a role, provisioned when a tenant is activated (FR-ONB-04) and adjustable per user through overrides. |
| **RPO and RTO** | Recovery point objective (maximum data loss, 15 minutes) and recovery time objective (maximum time to restore service, 4 hours) (NFR-DR-01). |

### S

| Term | Definition |
|---|---|
| **Seat** | The unit of the Tendwell subscription: one active client, meaning a client with at least one scheduled visit in the billing cycle (BR-002). |
| **Service authorization** | A payer's approval for a client to receive a service: payer, service code, units, unit type, period, billing model and rate (FR-CLI-03). |
| **Service line** | One of the three kinds of care Tendwell supports: HOME_VISIT, ADULT_DAY or SUPPORTED_LIVING. |
| **SEV (severity level)** | The severity of a production incident; SEV-1 is the most severe. Levels are defined in the incident management process. INC-2026-015 was SEV-1 (privacy); INC-2026-007 and INC-2026-011 were SEV-2. |
| **Short notice** | The flag on a time-off request made less than 7 days ahead, except Sick leave (BR-038). |
| **Single-flight** | The guarantee that a scheduled job runs once per idempotency key, even with several workers or during a deployment (ADR-003, NFR-MNT-02). |
| **SLO (service level objective)** | A target for a reliability measure, such as monthly availability or p95 latency. |
| **Support access grant** | Time-boxed access (at most 4 hours), approved by the Agency Administrator, that lets a Platform Support Agent see tenant data. Read-only by default and audited with the grant ID (BR-008). |
| **Supported living** | Homes staffed 24 hours a day where people live with support (SUPPORTED_LIVING). |

### T

| Term | Definition |
|---|---|
| **Tenant** | One customer agency and all of its data, isolated from every other tenant (BR-001). |
| **TOTP (time-based one-time password)** | A short-lived code generated by an authenticator app (RFC 6238). |
| **Travel time** | Time between consecutive visits on the same day. FLSA treats it as hours worked; Tendwell pays min(gap, estimated drive time + 10 minutes) when the gap is 2 hours or less (BR-043). |

### U

| Term | Definition |
|---|---|
| **Unit** | The billable quantity on an authorization: a 15-minute unit, a visit, a day or a month. Hourly units are floor(minutes / 15), plus 1 if the remainder is 8 minutes or more (BR-047). |

### V

| Term | Definition |
|---|---|
| **Verified visit** | A visit with a clock-in, a clock-out, all six EVV elements and no open exception. The only kind that is paid or billed (FR-EVV-10, BR-028). |
| **Visit pattern** | A recurring schedule definition that materializes visits nightly for a rolling 8 weeks (BR-018). |

### W

| Term | Definition |
|---|---|
| **Warning** | A scheduling compliance result that allows saving once a Coordinator gives a reason (FR-SCH-03). Contrast: hard block. |
| **WCAG** | The Web Content Accessibility Guidelines. Tendwell targets version 2.2, Level AA (NFR-ACC-01). |
| **Webhook** | An HTTP callback one system sends to another when an event happens. Tendwell receives signed payment webhooks (IF-01). |
| **Workweek** | A fixed, recurring period of 168 hours (seven consecutive 24-hour periods), set per tenant, over which FLSA overtime is calculated. |

## Related documents

- [Software Requirements Specification](SRS.md)
- [Business Requirements Document](BRD.md)
- [Business rules](business-rules.md)
- [Non-functional requirements](non-functional-requirements.md)
- [Compliance mapping](compliance-mapping.md)
- [Data dictionary](../03-design/data/data-dictionary.md)
- [Personas](../01-discovery/personas.md)
