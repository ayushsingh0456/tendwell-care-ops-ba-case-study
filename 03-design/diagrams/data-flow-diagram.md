# Data Flow Diagram

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DGM-04 |
| Version | 1.3 |
| Status | Approved |
| Owner | Business Analyst |
| Last updated | 2026-09-28 |
| Reviewers | Compliance and Privacy Officer, Engineering Lead, QA Lead |

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-03-02 | Baseline with SRS v1.0 |
| 1.2 | 2026-06-12 | Offline store and identity capture flows detailed for UAT privacy review |
| 1.3 | 2026-09-28 | Email and notification flows re-verified after INC-2026-015 (CR-006); invoice email content per SRS TBD-13 |

### Purpose and scope

This document shows where Tendwell data comes from, where it is processed and stored, and where it leaves, with trust boundaries and PHI flows marked. It is the basis for the privacy review, the HIPAA security risk analysis and threat modelling. Level 0 shows Tendwell as a single process with its external entities; level 1 decomposes it into processes and data stores, drawn as two views (care delivery, then back office) for readability.

Classifications follow the [data classification and retention](../data/data-classification-and-retention.md) scheme: **PHI**, **PII**, **Confidential** and **Internal**, where the highest class of any field in a flow wins. Interface IDs (IF-01 to IF-10) are those in the [SRS](../../02-requirements/SRS.md).

### Notation

| Symbol | Meaning |
|---|---|
| Rectangle (E-number) | External entity: a person, organization or system outside Tendwell's control |
| Circle (P-number) | Process that transforms data |
| Cylinder (D-number) | Data store |
| Thick arrow `==>` | Flow that carries PHI or biometric data |
| Solid arrow `-->` | Flow that carries PII, Confidential or Internal data but no PHI |
| Dotted arrow `-.->` | Flow that never carries PHI by design (notification channels, payment provider, maps) |
| Labelled subgraph (TB-number) | Trust boundary; every crossing is authenticated and encrypted in transit |

Flow labels start with the flow ID used in the inventory in section 4.

## 1. Level 0: context

```mermaid
flowchart LR
  classDef ent fill:#f2f2f2,stroke:#555555,color:#222222
  classDef proc fill:#1f4e79,stroke:#0b2540,color:#ffffff

  subgraph TB1["TB1: user devices and browsers on the internet"]
    E1["E1 Agency office staff<br/>AG-ADM, AG-COORD, AG-SUPV, AG-FIN"]:::ent
    E2["E2 Caregiver with mobile app"]:::ent
    E3["E3 Tendwell Labs staff<br/>PLT-ADM, PLT-SUP"]:::ent
    E4["E4 Prospective agency owner"]:::ent
    E5["E5 Responsible party, private pay"]:::ent
  end
  subgraph TB2["TB2: Tendwell AWS production account under BAA"]
    P0(("0<br/>Tendwell<br/>platform")):::proc
  end
  subgraph TB3["TB3: sub-processors under BAA"]
    E6["E6 Identity verification vendor"]:::ent
    E7["E7 OIDC identity provider"]:::ent
  end
  subgraph TB4["TB4: vendors that never receive PHI by design"]
    E8["E8 Stripe"]:::ent
    E9["E9 Twilio SMS"]:::ent
    E10["E10 Amazon SES email"]:::ent
    E11["E11 FCM / APNs push"]:::ent
    E12["E12 Google Maps Platform"]:::ent
  end
  subgraph TB5["Outside Tendwell: file recipients, reached by agency users"]
    E13["E13 Payroll provider"]:::ent
    E14["E14 Clearinghouse and payers"]:::ent
    E15["E15 State EVV aggregator"]:::ent
  end

  E1 ==>|"F01 client, schedule, clinical, billing input"| P0
  P0 ==>|"F02 masked views, reveals, reports"| E1
  E2 ==>|"F03 punches with GPS, tasks, doses, vitals, notes, incidents"| P0
  P0 ==>|"F04 assigned visits, tasks, due doses"| E2
  E3 -->|"F05 plans, promo codes, grant requests"| P0
  P0 ==>|"F06 tenant data under an Active grant, masked"| E3
  E4 -->|"F07 sign-up details, EIN"| P0
  P0 ==>|"F08 identity capture package"| E6
  E6 -->|"F09 liveness result, match score"| P0
  P0 -->|"F10 sign-in, MFA, token validation"| E7
  P0 -.->|"F11 amount, invoice number, payer email"| E8
  E8 -.->|"F12 signed payment webhooks"| P0
  P0 -.->|"F13 generic SMS and deep link"| E9
  P0 -.->|"F14 generic email and deep link"| E10
  P0 -.->|"F15 generic push and deep link"| E11
  P0 -.->|"F16 address or coordinates, no identifiers"| E12
  E10 -.->|"F17 invoice notice with payment link"| E5
  E5 -.->|"F18 card or ACH payment"| E8
  P0 -->|"F19 payroll CSV via AG-FIN"| E13
  P0 ==>|"F20 claim batch CSV via AG-FIN"| E14
  P0 ==>|"F21 EVV export CSV"| E15
```

*Figure 1. Level 0 context DFD. PHI crosses TB1 only to authenticated users of the owning tenant and crosses TB3 only to the identity verification vendor under a BAA. Nothing in TB4 receives PHI (BR-056, FR-NTF-05). Supports NFR-PRIV-01, NFR-CMP-01 and NFR-SEC-01.*

## 2. Level 1: care delivery

```mermaid
flowchart LR
  classDef ent fill:#f2f2f2,stroke:#555555,color:#222222
  classDef proc fill:#1f4e79,stroke:#0b2540,color:#ffffff
  classDef store fill:#dce8f5,stroke:#2f5d8a,color:#10263d

  E1["E1 Agency office staff"]:::ent
  E2["E2 Caregiver"]:::ent
  E4["E4 Prospective agency owner"]:::ent
  E6["E6 Identity vendor"]:::ent
  E7["E7 OIDC provider"]:::ent
  E8["E8 Stripe"]:::ent
  E12["E12 Google Maps"]:::ent

  subgraph TBD["TB6: caregiver device"]
    D11[("D11 Offline store<br/>SQLCipher outbox and cache")]:::store
  end

  subgraph TB2["TB2: Tendwell AWS production account"]
    P1(("P1 Onboard<br/>and subscribe")):::proc
    P2(("P2 Authenticate<br/>and authorize")):::proc
    P3(("P3 Manage clients<br/>and care plans")):::proc
    P4(("P4 Schedule and<br/>manage workforce")):::proc
    P5(("P5 Capture and<br/>verify EVV")):::proc
    P6(("P6 Document doses,<br/>vitals, notes, incidents")):::proc
    D1[("D1 Tenants, users, access")]:::store
    D2[("D2 Client records<br/>field-encrypted PHI")]:::store
    D3[("D3 Workforce, schedule, time off")]:::store
    D4[("D4 EVV punches and exceptions")]:::store
    D5[("D5 Clinical documentation")]:::store
    D10[("D10 S3 documents and photos")]:::store
    D9[("D9 Audit log")]:::store
  end

  E4 -->|"F07"| P1
  P1 -->|"F22 tenant, subscription"| D1
  P1 -.->|"F23 seats, plan, billing contact"| E8
  E7 -->|"F10 tokens"| P2
  P2 -->|"F24 sessions, sign-in events"| D1
  E1 ==>|"F01 intake, authorizations, care plans"| P3
  P3 ==>|"F25 encrypted PHI fields"| D2
  P3 -.->|"F16 address only"| E12
  E1 -->|"F26 patterns, credentials, time off"| P4
  P4 -->|"F27 visits, credentials"| D3
  D2 ==>|"F28 authorizations, exclusions"| P4
  E2 ==>|"F29 offline captures"| D11
  D11 ==>|"F30 ordered sync"| P5
  E2 ==>|"F03 online punches"| P5
  P5 ==>|"F08 capture package"| E6
  E6 -->|"F09 result"| P5
  D2 ==>|"F31 geofence center, radius"| P5
  P5 ==>|"F32 punches, exceptions"| D4
  P5 ==>|"F33 exception queue"| E1
  E2 ==>|"F34 doses, vitals, notes, incidents"| P6
  P6 ==>|"F35 clinical records"| D5
  P6 ==>|"F36 incident photos"| D10
  P3 -->|"F37 audit events"| D9
  P5 -->|"F37 audit events"| D9
  P6 -->|"F37 audit events"| D9
```

*Figure 2. Level 1, care delivery. The device store (TB6) holds only the caregiver's assigned work for 72 hours and syncs in capture order (ADR-006). Client coordinates move from D2 to P5 inside TB2 only; the API never returns them. Supports FR-CLI-01, FR-CLI-06, FR-EVV-02, FR-EVV-04, FR-EVV-05, BR-011, BR-021 and NFR-MOB-02.*

## 3. Level 1: back office, notifications and reporting

```mermaid
flowchart LR
  classDef ent fill:#f2f2f2,stroke:#555555,color:#222222
  classDef proc fill:#1f4e79,stroke:#0b2540,color:#ffffff
  classDef store fill:#dce8f5,stroke:#2f5d8a,color:#10263d

  E1["E1 Agency office staff"]:::ent
  E2["E2 Caregiver"]:::ent
  E8["E8 Stripe"]:::ent
  E9["E9 Twilio"]:::ent
  E10["E10 Amazon SES"]:::ent
  E11["E11 FCM / APNs"]:::ent
  E13["E13 Payroll provider"]:::ent
  E14["E14 Clearinghouse"]:::ent
  E15["E15 State EVV aggregator"]:::ent

  subgraph TB2["TB2: Tendwell AWS production account"]
    D1[("D1 Tenants, users, access")]:::store
    D3[("D3 Workforce, schedule, time off")]:::store
    D4[("D4 EVV punches and exceptions")]:::store
    D2[("D2 Client records")]:::store
    P7(("P7 Prepare<br/>payroll")):::proc
    P8(("P8 Bill and<br/>collect")):::proc
    P9(("P9 Notify and<br/>escalate")):::proc
    P10(("P10 Report, audit<br/>and export")):::proc
    D6[("D6 Payroll lines and exports")]:::store
    D7[("D7 Invoices, payments, claims")]:::store
    D8[("D8 Event outbox and notifications")]:::store
    D9[("D9 Audit log")]:::store
    D10[("D10 S3 export files")]:::store
  end

  D4 ==>|"F38 effective times of Verified visits"| P7
  D3 -->|"F39 pay profiles, approved time off"| P7
  P7 -->|"F40 payroll lines"| D6
  P7 -->|"F41 payroll CSV, watermarked"| D10
  D10 -->|"F19 download by AG-FIN"| E13
  D4 ==>|"F42 Verified visits"| P8
  D2 ==>|"F43 authorizations, payer"| P8
  P8 ==>|"F44 invoices and lines"| D7
  P8 -.->|"F11 payment link request"| E8
  E8 -.->|"F12 webhooks"| P8
  P8 ==>|"F45 claim batch CSV"| D10
  D10 ==>|"F20 download by AG-FIN"| E14
  D8 -->|"F46 domain events, IDs only"| P9
  D1 -->|"F47 active users, roles, preferences"| P9
  P9 -.->|"F13 generic SMS"| E9
  P9 -.->|"F14 generic email"| E10
  P9 -.->|"F15 generic push"| E11
  P9 ==>|"F48 in-app detail after sign-in"| E1
  P9 ==>|"F48 in-app detail after sign-in"| E2
  D4 ==>|"F49 visit data"| P10
  D7 ==>|"F49 financial data"| P10
  P10 ==>|"F02 dashboards and reports, masked"| E1
  P10 ==>|"F21 EVV export CSV"| E15
  P10 -->|"F37 export audit events"| D9
```

*Figure 3. Level 1, back office. Payroll and billing read only Verified visits (BR-028). Notification bodies leaving TB2 are generic; detail is shown in-app after sign-in (BR-056). Recipients are resolved from D1 at send time (BR-054, CR-006). Exports carry watermarks and audit events (BR-058). Supports FR-PAY-05, FR-BIL-01, FR-BIL-05, FR-BIL-06, FR-NTF-01 to FR-NTF-05, FR-RPT-02 to FR-RPT-04 and NFR-CMP-02.*

## 4. Data flow inventory

| Flow | From | To | Data | Classification | Protection |
|---|---|---|---|---|---|
| F01 | E1 Agency staff | P0 / P3 | Client demographics, diagnoses, authorizations, care plans, schedules, billing actions | PHI | TLS 1.2+; OIDC JWT; permission guard; RLS; field encryption on write |
| F02 | P0 / P10 | E1 Agency staff | Masked lists and details; revealed fields on request; reports | PHI | Masking by default; audited reveal (FR-CLI-06); `Cache-Control: no-store`; location scope |
| F03 | E2 Caregiver | P0 / P5 | Online punches with GPS, accuracy, device ID; task statuses | PHI | TLS with certificate pinning; JWT; server-side distance (BR-021) |
| F04 | P0 | E2 Caregiver | Assigned visits, client first name and last initial, service address, tasks, due doses, allergies | PHI | Only assigned visits, 72 h window; stored in SQLCipher |
| F05 | E3 Platform staff | P0 | Plans, promo codes, support grant requests | Confidential | WAF IP allowlist; MFA (BR-006) |
| F06 | P0 | E3 Platform staff | Tenant data under an Active grant | PHI (masked) | Grant approval, 4 h maximum, read-only default, no reveal, audited with grant ID (BR-008) |
| F07 | E4 Owner | P1 | Owner contact, agency legal details, EIN, plan | PII, Confidential | TLS; EIN encrypted on receipt; card data goes to Stripe, never to Tendwell |
| F08 | P5 | E6 Identity vendor (IF-06) | Encrypted capture package, enrollment reference | PII (biometric) | BAA; in-memory only on the server; vendor deletes after match (ADR-004) |
| F09 | E6 | P5 | Liveness result, match score, vendor transaction ID | PII | Server-side; result valid 90 s, single use (BR-024) |
| F10 | P2 / P0 | E7 OIDC provider (IF-10) | Email, MFA factors, tokens | PII | OIDC with PKCE; JWKS validation; 15 min access tokens |
| F11 | P8 / P0 | E8 Stripe (IF-01) | Invoice number, amount, currency, responsible party email, tenant and invoice IDs | Confidential (no PHI) | Payload allowlist; no client name, service code or diagnosis |
| F12 | E8 | P8 / P0 | Payment events | Confidential | HMAC-SHA256 signature, 5-minute tolerance, event ID claimed once (ADR-003) |
| F13 | P9 | E9 Twilio (IF-02) | Phone number, generic text, deep link | PII (no PHI) | Templates have no PHI placeholders (template lint in CI); BR-056 |
| F14 | P9 | E10 Amazon SES (IF-03) | Email address, generic text, deep link | PII (no PHI) | Same template control; recipients resolved at send time; dispatch guard re-checks user status (BR-054) |
| F15 | P9 | E11 FCM / APNs (IF-04) | Device token, generic title and body, deep link | PII (no PHI) | Same template control; payload size check |
| F16 | P3 | E12 Google Maps (IF-05) | Address string at intake; coordinate pairs for drive time | Confidential (no identifiers) | Adapter allowlist sends no name, client number or Medicaid ID |
| F17 | E10 | E5 Responsible party | Invoice number, amount, due date, payment link | Confidential (no PHI) | Itemized invoice only behind the link after verification; no attachment (SRS TBD-13) |
| F18 | E5 | E8 Stripe | Card or bank details | Confidential (cardholder data) | Stripe-hosted page; outside Tendwell's PCI scope |
| F19 | D10 | E13 Payroll provider (IF-07) | Employee number, hours, rates, amounts, mileage | PII, Confidential | Pre-signed URL 15 min; watermark in file name and manifest; SHA-256 recorded; period lock (BR-046, BR-058) |
| F20 | D10 | E14 Clearinghouse (IF-08) | Medicaid ID, authorization number, HCPCS code, dates, units, charges, diagnosis codes | PHI | Pre-signed URL; watermark; audit event; agency transmits through its own clearinghouse account |
| F21 | P10 | E15 State EVV aggregator (IF-09) | Six EVV elements, punch sources, exception and reason codes | PHI | Configurable CSV; watermark; audit event (NFR-CMP-02) |
| F22 | P1 | D1 | Tenant, subscription, settings | Confidential | RLS on tenant tables; EIN field-encrypted |
| F23 | P1 | E8 Stripe | Seats, plan, billing contact | Confidential | Payload allowlist |
| F24 | P2 | D1 | Sessions, `sign_in_events` | PII | Append-only; 7-year audit retention |
| F25 | P3 | D2 | Client record with encrypted DOB, Medicaid ID, phone, address, diagnoses | PHI | Envelope encryption with per-tenant keys in KMS; blind indexes for duplicate checks |
| F26 | E1 | P4 | Visit patterns, caregiver profiles, credentials, time-off decisions | PII | Permission guard; compliance checks (FR-SCH-03) |
| F27 | P4 | D3 | Visits, credentials, pay profiles, time off | PII, Confidential | RLS; effective-dated pay profiles |
| F28 | D2 | P4 | Authorization coverage, client exclusions | PHI | Internal read within TB2 |
| F29 | E2 | D11 | Offline punches, identity capture packages, clinical entries, photos | PHI, PII (biometric) | SQLCipher AES-256; key in Keychain or Keystore; wipe on deactivation (NFR-MOB-02) |
| F30 | D11 | P5 | Ordered outbox commands with device and monotonic time | PHI | Idempotent by command ID; LATE_OFFLINE_SYNC after 24 h (BR-025) |
| F31 | D2 | P5 | Client coordinates and geofence radius | PHI | Never returned by the API; used for server-side distance only |
| F32 | P5 | D4 | Append-only punches, exceptions, identity check results | PHI | Insert-only grants (ADR-002) |
| F33 | P5 | E1 | Exception queue entries | PHI | Location scope; masked client fields |
| F34 | E2 | P6 | Dose outcomes, PRN records, vitals, notes, incidents | PHI | Reason required for Refused, Held, Not available (BR-032); note lock after 24 h (BR-035) |
| F35 | P6 | D5 | eMAR, vitals, notes, addenda, incidents | PHI | Append-only addenda; RLS |
| F36 | P6 | D10 | Incident photos | PHI | SSE-KMS; pre-signed upload; no public access |
| F37 | P3, P5, P6, P10 | D9 | Audit events with actor, action, entity, before and after, IP, device | PHI (in before and after values) | Append-only; Object Lock archive for 7 years (BR-057, NFR-PRIV-02) |
| F38 | D4 | P7 | Effective start and end of Verified visits | PHI | Read through the effective-time view (ADR-002) |
| F39 | D3 | P7 | Pay profiles, approved time off, holidays | PII, Confidential | RLS; AG-FIN permission |
| F40 | P7 | D6 | Payroll lines | PII, Confidential | Locked on export; adjustments only (FR-PAY-06) |
| F41 | P7 | D10 | Payroll CSV | PII, Confidential | Watermark; SHA-256 in `payroll_exports` |
| F42 | D4 | P8 | Verified visits | PHI | Only Verified visits (BR-028) |
| F43 | D2 | P8 | Authorizations, rates, payer | PHI | Units capped (BR-049) |
| F44 | P8 | D7 | Invoices and lines | PHI | Unique idempotency key over non-void invoices (BR-050, ADR-003) |
| F45 | P8 | D10 | Claim batch CSV | PHI | Watermark; audit |
| F46 | D8 | P9 | Domain events with entity IDs only | Internal | No PHI in event payloads or job queues |
| F47 | D1 | P9 | Active users with target role and location, channel preferences | PII | Resolved at send time; deactivated users excluded (BR-054) |
| F48 | P9 | E1, E2 | In-app notification detail | PHI | Shown only after sign-in, under RLS and permissions |
| F49 | D2 to D7 | P10 | Visit, clinical and financial data for reports | PHI | Location scope; masked output; export watermark (FR-RPT-04) |

## 5. Flows that never carry PHI

These flows cross into systems that are either not covered for PHI or not appropriate for it. Each has a design control and a test, not only a policy.

| Flow | Channel | Control | Verification |
|---|---|---|---|
| F13, F14, F15 | SMS, email, push | Notification templates contain only generic text and a sign-in deep link; the template schema rejects client, diagnosis, medication and address placeholders; content is reviewed by the Compliance and Privacy Officer | CI template lint; automated test per event type (BR-056, FR-NTF-05); privacy review after INC-2026-015 |
| F14 recipients | Email | Recipients resolved at send time from active users; dispatch guard re-checks status immediately before send | Business anomaly alert on any notification to a deactivated user (NFR-OBS-02) |
| F11, F23 | Stripe | Payload builder allowlist: amounts, invoice number, tenant and invoice IDs, billing contact | Contract test asserts the exact field set |
| F16 | Google Maps | Adapter sends address string or coordinates only, never names or client identifiers | Contract test on adapter requests |
| F17 | Invoice email | Invoice number, amount, due date and link only; itemization behind verification | Template test (SRS TBD-13) |
| F46 | Event outbox and job queue | Events and job payloads carry IDs; consumers load data under RLS | Schema test on event types |
| Logs, traces, errors | CloudWatch, Grafana, Sentry | Allowlist serializers; body logging disabled; Sentry scrubbing; daily canary scan | SAST rule; canary scan alert (NFR-OBS-01) |

## 6. Trust boundaries

| Boundary | Contains | Controls on crossing |
|---|---|---|
| TB1 User devices and browsers | Office staff browsers, caregiver phones, platform staff browsers, sign-up visitors, responsible parties | TLS 1.2+; OIDC tokens; MFA for privileged roles (BR-006); WAF; idle timeout and mobile re-authentication (FR-IAM-04) |
| TB2 Tendwell AWS production account | API, Worker, PostgreSQL, Redis, S3, KMS | Private subnets; security groups; RLS (BR-001); KMS envelope encryption; no standing human access |
| TB3 Sub-processors under BAA | Identity verification vendor, OIDC provider | BAA; minimum data; vendor deletion terms; contract review annually (NFR-CMP-01) |
| TB4 Vendors that never receive PHI | Stripe, Twilio, Amazon SES, FCM/APNs, Google Maps | Payload allowlists and template controls (section 5) |
| TB5 File recipients | Payroll provider, clearinghouse, state EVV aggregator | Files downloaded by authorized agency users; watermark and audit; the agency remains responsible for onward transmission |
| TB6 Caregiver device | Offline store, cached assigned work, outbox | SQLCipher, device authentication, certificate pinning, sync-then-wipe on deactivation (ADR-006) |

## Related documents

- [System context and containers](../architecture/system-context-and-containers.md)
- [Deployment and security](../architecture/deployment-and-security.md)
- [Data classification and retention](../data/data-classification-and-retention.md)
- [Data dictionary](../data/data-dictionary.md)
- [Sequence diagrams](sequence-diagrams.md)
- [Compliance mapping](../../02-requirements/compliance-mapping.md)
- [Events and webhooks](../../04-api/events-and-webhooks.md)
- [INC-2026-015 escalation email to a deactivated user](../../07-operations/incidents/INC-2026-015-escalation-email-to-deactivated-user.md)
