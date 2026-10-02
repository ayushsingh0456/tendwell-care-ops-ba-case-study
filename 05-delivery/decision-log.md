# Decision log

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DEL-008 |
| Version | 1.6 |
| Status | Living document |
| Owner | Business Analyst |
| Last updated | 2026-09-24 |
| Reviewers | Product Owner, Engineering Lead, Clinical SME (RN advisor), Compliance and Privacy Officer |

## Purpose and scope

This log records the product and delivery decisions that shape Tendwell, with their context, the options considered and the reasoning, so that later readers can tell why the product works the way it does. Architecture decisions are recorded in full in the ADRs; this log keeps a product-level summary and links to them. Change request outcomes that set direction are also logged here. Decisions are not reopened without new evidence; a reversal gets a new DEC ID that references the original.

## Summary

| ID | Date | Decision | Decided by | Links |
|---|---|---|---|---|
| DEC-01 | 2026-02-05 | Shared-schema multi-tenancy with PostgreSQL row-level security | Engineering Lead, Product Owner | ADR-001, BR-001 |
| DEC-02 | 2026-02-10 | React Native (Expo), offline-first Caregiver app | Engineering Lead, Product Owner | ADR-006, NFR-AVL-02 |
| DEC-03 | 2026-02-12 | Append-only EVV punch ledger | Engineering Lead, Business Analyst | ADR-002, BR-026 |
| DEC-04 | 2026-02-17 | Export payroll; do not process it | Product Owner | ADR-005, CR-008 |
| DEC-05 | 2026-02-19 | 150 m geofence default, configurable 50-500 m, computed on the server | Product Owner, Business Analyst | BR-021, CR-004 |
| DEC-06 | 2026-02-24 | 15-minute billing units with 8-minute rounding | Product Owner | BR-047 |
| DEC-07 | 2026-02-26 | Identity verification optional per tenant, behind a vendor adapter | Product Owner | ADR-004, FR-EVV-04 |
| DEC-08 | 2026-02-27 | Read-only status never blocks care delivery | Product Owner | BR-003 |
| DEC-09 | 2026-04-15 | Family Portal deferred to Release 2 | Product Owner (change control board) | CR-003 |
| DEC-10 | 2026-06-17 | Undocumented doses are never auto-cancelled | Product Owner, on Clinical SME and Compliance advice | CR-007, BR-031 |
| DEC-11 | 2026-06-26 | Pilot go-live approved with conditions | Product Owner, Engineering Lead, QA Lead, Customer Success Lead | Release and sprint plan |
| DEC-12 | 2026-07-30 | Billing idempotency enforced in the database, with a pre-issue duplicate check | Product Owner, Engineering Lead | CR-005, ADR-003 |

---

### DEC-01 · Shared-schema multi-tenancy with row-level security

| Field | Value |
|---|---|
| Date | 2026-02-05 |
| Decision | All tenants share one PostgreSQL schema. Every business table carries `tenant_id`, and row-level security policies enforce isolation in the database for every query. |
| Context | Tendwell must scale to 500 tenants (NFR-SCL-01), most of them small agencies, at a low cost per tenant. BR-001 requires that isolation is enforced in the database, not only in the UI. |
| Options considered | (1) Database per tenant. (2) Schema per tenant. (3) Shared schema with row-level security. (4) Shared schema with application-level filtering only. |
| Rationale | Option 3 gives database-enforced isolation with one migration path and low operating cost. Options 1 and 2 multiply migrations, connections and backups at 500 tenants. Option 4 was rejected because one missing filter in one query would expose PHI across tenants. |
| Decided by | Engineering Lead and Product Owner; Compliance and Privacy Officer consulted |
| Links | ADR-001, BR-001, FR-IAM-06, NFR-SCL-01, US-009 |

### DEC-02 · React Native (Expo), offline-first Caregiver app

| Field | Value |
|---|---|
| Date | 2026-02-10 |
| Decision | Build the Caregiver app in React Native with Expo, with an encrypted SQLite (SQLCipher) queue for offline punches, dose outcomes, notes and incidents. |
| Context | Caregivers use both Android (for example PER-01) and iOS phones; homes often have no signal; the team has one mobile developer and a React web team. The app must capture 72 hours of punches offline (NFR-AVL-02). |
| Options considered | (1) Separate native iOS and Android apps. (2) React Native with Expo. (3) Progressive web app. (4) Flutter. |
| Rationale | One codebase suits one mobile developer, and web developers can contribute. The required device APIs (location with accuracy, secure storage, background sync) are available. The progressive web app was rejected because of iOS limits on background work and storage, which make reliable encrypted offline capture difficult. Flutter was rejected because of the skills gap. |
| Decided by | Engineering Lead and Product Owner |
| Links | ADR-006, NFR-AVL-02, NFR-MOB-01, NFR-MOB-02, US-027, RSK-09 |

### DEC-03 · Append-only EVV punch ledger

| Field | Value |
|---|---|
| Date | 2026-02-12 |
| Decision | EVV punches are never updated or deleted. A correction adds a new punch of source Manual, with reason code, note and editor, that supersedes the earlier punch. |
| Context | Time corrections are frequent (forgotten clock-outs, device problems). Auditors and payers need to see the original evidence and every change to it. |
| Options considered | (1) Editable punches with a separate audit log. (2) Append-only punches with superseding records. |
| Rationale | Option 2 keeps the original evidence in the operational data, makes the visit history self-explanatory and lets payroll and billing compute from the effective punches without consulting the audit log. |
| Decided by | Engineering Lead and Business Analyst; Compliance and Privacy Officer consulted |
| Links | ADR-002, BR-026, FR-EVV-08, US-029, US-030 |

### DEC-04 · Export payroll; do not process it

| Field | Value |
|---|---|
| Date | 2026-02-17; reaffirmed 2026-05-22 |
| Decision | Tendwell calculates pay lines and exports a CSV with a configurable column mapping. It does not withhold tax, move money or issue pay stubs. |
| Context | Discovery showed that the 14 hours of payroll preparation per period (OBJ-02) go into assembling and checking hours, not into running payroll. Agencies already use payroll providers (ASM-02). |
| Options considered | (1) CSV export with mapping. (2) API integrations with major payroll providers. (3) Full payroll processing. |
| Rationale | Option 1 removes the preparation work at low risk and cost. Option 3 brings tax-engine, filing and money-movement liabilities outside Tendwell's core. Option 2 stays on the Later roadmap. CR-008 asked for option 3 and was rejected on 2026-05-22 for the same reasons. |
| Decided by | Product Owner |
| Links | ADR-005, FR-PAY-05, CR-008, US-042, ASM-02 |

### DEC-05 · 150 m geofence default, computed on the server

| Field | Value |
|---|---|
| Date | 2026-02-19; revisited 2026-08-26 |
| Decision | Each service address has a geofence radius of 150 m by default, configurable from 50 to 500 m. Distance is computed on the server from the punch coordinates; the device cannot declare it. A location outside the radius raises an exception and never blocks the punch. |
| Context | A discovery field test of 120 clock-ins at 40 Lakemont addresses found 96% within 150 m of the geocoded address when the fix was accurate to 50 m or better. Rural driveways and large apartment complexes needed more. A radius that is too small floods Coordinators with false exceptions; too large weakens verification. |
| Options considered | (1) 100 m fixed. (2) 150 m default, configurable per address. (3) 250 m fixed. (4) Tenant-level setting only. |
| Rationale | Option 2 balances verification strength and noise, and per-address configuration covers the known edge cases. Computing distance on the server prevents tampering. After INC-2026-011 the radius was reviewed and kept: the failure came from treating inaccurate fixes as mismatches, which CR-004 fixes separately (BR-022). |
| Decided by | Product Owner and Business Analyst; Customer Success Lead consulted |
| Links | BR-021, BR-022, FR-EVV-03, US-025, CR-004 |

### DEC-06 · 15-minute billing units with 8-minute rounding

| Field | Value |
|---|---|
| Date | 2026-02-24 |
| Decision | Hourly services bill in 15-minute units per visit: units = floor(minutes / 15), plus 1 if the remainder is 8 minutes or more. This is the tenant default; the rounding rule is configurable to match payer contracts. |
| Context | Payer service codes such as T1019 are billed per 15-minute unit. The pilot agencies rounded in different ways, which produced billing disputes and recoupment risk. |
| Options considered | (1) Always round down. (2) Round up at 8 minutes or more (the 8-minute rule). (3) Bill exact minutes pro rata. |
| Rationale | Option 2 matches common payer practice for 15-minute units and treats both sides fairly. Per-visit rounding is transparent on the invoice, as in the C-10234 example (127, 113 and 120 minutes give 24 units, $174.00). The agency remains responsible for matching each payer's contract rules. |
| Decided by | Product Owner; Billing & Payroll Specialists at the pilot agencies consulted |
| Links | BR-047, FR-BIL-02, US-045 |

### DEC-07 · Identity verification optional per tenant, behind a vendor adapter

| Field | Value |
|---|---|
| Date | 2026-02-26 |
| Decision | Selfie liveness and face match at clock-in is a tenant setting, off by default. The vendor sits behind an `IdentityVerificationPort` adapter. A failed check never blocks care; it raises IDENTITY_CHECK_FAILED. |
| Context | The Cures Act EVV elements do not require biometric checks. Some agencies want to deter buddy punching; others worry about cost per check and caregiver privacy, and some states regulate biometric data. |
| Options considered | (1) Mandatory for all tenants. (2) Optional per tenant. (3) Not in R1. |
| Rationale | Option 2 serves agencies that want it without imposing cost and privacy concerns on the rest. The adapter avoids vendor lock-in. Results are valid for 90 seconds and one punch only (BR-024). |
| Decided by | Product Owner; Compliance and Privacy Officer consulted |
| Links | FR-EVV-04, BR-024, ADR-004, US-026, DEP-02 |

### DEC-08 · Read-only status never blocks care delivery

| Field | Value |
|---|---|
| Date | 2026-02-27; clarified 2026-05-19 |
| Decision | When a tenant becomes Read-only (7 days after trial expiry or after the third failed payment retry), office users can view and export but not create or edit. The full caregiver visit flow stays available: clock-in and clock-out, tasks, eMAR, vitals, notes and incident reports. |
| Context | Collections pressure must never put a client at risk or create an EVV gap that the agency cannot fix. |
| Options considered | (1) Full lockout. (2) Read-only with EVV clock-in only. (3) Read-only for office work; caregiver visit flow untouched. |
| Rationale | Option 3 protects clients and EVV compliance while still giving the agency a strong reason to pay. The 2026-05-19 clarification extended BR-003's "EVV clock-in stays available" to the whole visit flow, because blocking a dose record or an incident report would also block care. |
| Decided by | Product Owner; Clinical SME consulted |
| Links | BR-003, FR-ONB-07, US-006 |

### DEC-09 · Family Portal deferred to Release 2

| Field | Value |
|---|---|
| Date | 2026-04-15 |
| Decision | EP-14 Family Portal (US-053, US-054; FR-FAM-01 to FR-FAM-03) moves from R1 to R2. |
| Context | The SRS v1.0 backlog equaled 100% of capacity (RSK-08). Family consent and minimum-necessary scope had not had a privacy review, and the pilot agencies ranked the portal lowest of the R1 features. |
| Options considered | (1) Keep it in R1 and accept the risk. (2) Ship a read-only schedule view only. (3) Defer the whole epic to R2. |
| Rationale | Option 3 created a buffer for CR-001 and CR-002 and gave time to design consent properly. Option 2 would still have needed the full consent model. |
| Decided by | Product Owner (change control board) |
| Links | CR-003, EP-14, US-053, US-054, RSK-08 |

### DEC-10 · Undocumented doses are never auto-cancelled

| Field | Value |
|---|---|
| Date | 2026-06-17 |
| Decision | CR-007 is rejected. A dose with no outcome becomes Missed - undocumented 60 minutes after its window closes, escalates to the Clinical Supervisor and stays on the MAR. Late entry is allowed for 24 hours; after that only a Clinical Supervisor can annotate it. No job or user can cancel or delete it. |
| Context | TEN-003 asked for a "clean slate" at midnight because the previous day's doses cluttered the handover view. |
| Options considered | (1) Auto-cancel at midnight. (2) Hide from the caregiver after the late-entry window (already the behavior). (3) Default the office missed-doses tile to the last 24 hours and route older items to the Supervisor's review queue. |
| Rationale | Auto-cancel would hide clinical events, corrupt the MAR and flatter OBJ-03. Options 2 and 3 meet the real need, a clear handover, without changing the record. See the CR-007 write-up in the change request log. |
| Decided by | Product Owner, on the recommendation of the Clinical SME and the Compliance and Privacy Officer |
| Links | CR-007, BR-030, BR-031, FR-MAR-04, US-033, US-051 |

### DEC-11 · Pilot go-live approved with conditions

| Field | Value |
|---|---|
| Date | 2026-06-26 |
| Decision | Go for pilot go-live on 2026-07-06, with four conditions: TEN-003 phases eMAR in (one home first, all three by 2026-07-20); a two-period payroll parallel run per agency; identity verification only at TEN-001; two weeks of hypercare with daily triage. |
| Context | All 12 go/no-go criteria were met. Criterion 8 (data migration) was met with a condition, because 9 TEN-003 addresses needed manual pins. eMAR in 24-hour homes and payroll were the highest-consequence areas. |
| Options considered | (1) Go without conditions. (2) Go with conditions. (3) Delay 2 weeks for more UAT. |
| Rationale | The conditions contain the two highest-consequence risks (RSK-07 payroll, clinical risk in eMAR) without delaying value for TEN-001 and TEN-002. A two-week delay would have cost two weeks of pilot learning before GA on 2026-09-01, with no new evidence expected because the UAT exit criteria were already met. |
| Decided by | Product Owner, Engineering Lead, QA Lead and Customer Success Lead; Clinical SME consulted |
| Links | Release and sprint plan (go/no-go), RSK-05, RSK-07, DEP-03, DEP-06 |

### DEC-12 · Billing idempotency enforced in the database

| Field | Value |
|---|---|
| Date | 2026-07-30 |
| Decision | Approve CR-005: a unique database constraint on the invoice idempotency key (tenant + client + payer + period), insert-or-update behavior for concurrent writes, a pre-issue duplicate check for manual and automatic issue, and an invoice-count anomaly alert. |
| Context | INC-2026-007: two scheduler workers ran the nightly billing run during a deployment overlap; an application-level check-then-insert raced and created 214 duplicate drafts in 9 tenants. Single-flight jobs (ADR-003) were the only control. |
| Options considered | (1) Fix leader election only. (2) Database constraint plus pre-issue check plus anomaly alert. (3) Serialize billing through one worker per tenant. (4) Disable private-pay auto-issue. |
| Rationale | Defense in depth for any process that creates financial records: prevent (constraint), block before money moves (pre-issue check) and detect (alert). The Definition of Done now requires a two-worker test for every scheduled job. |
| Decided by | Product Owner and Engineering Lead |
| Links | CR-005, BR-050, FR-BIL-01, FR-BIL-04, US-044, ADR-003, NFR-OBS-02, INC-2026-007 |

## Related documents

- [Change request log](change-request-log.md)
- [RAID log](raid-log.md)
- [Release and sprint plan](release-and-sprint-plan.md)
- [Product roadmap](product-roadmap.md)
- [ADR-001 Multi-tenancy with row-level security](../03-design/architecture/adr/ADR-001-multi-tenancy-row-level-security.md)
- [ADR-002 Append-only EVV punch ledger](../03-design/architecture/adr/ADR-002-append-only-evv-punch-ledger.md)
- [ADR-003 Single-flight scheduled jobs](../03-design/architecture/adr/ADR-003-single-flight-scheduled-jobs.md)
- [ADR-004 Identity verification vendor adapter](../03-design/architecture/adr/ADR-004-identity-verification-vendor-adapter.md)
- [ADR-005 Payroll export, not processing](../03-design/architecture/adr/ADR-005-payroll-export-not-processing.md)
- [ADR-006 Offline-first caregiver app](../03-design/architecture/adr/ADR-006-offline-first-caregiver-app.md)
- [Business rules catalog](../02-requirements/business-rules.md)
