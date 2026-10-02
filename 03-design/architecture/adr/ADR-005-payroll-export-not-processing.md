# ADR-005: Export payroll to the agency's payroll provider; do not process payroll

## Document control

| Field | Value |
|---|---|
| Document ID | ADR-005 |
| Version | 1.1 |
| Status | Accepted |
| Owner | Business Analyst |
| Last updated | 2026-09-24 |
| Reviewers | Product Owner, Engineering Lead, Customer Success Lead, Compliance and Privacy Officer |

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-02-26 | Accepted during discovery; scope boundary for EP-10 |
| 1.1 | 2026-09-24 | Re-confirmed after the CR-008 assessment (Rejected / deferred to backlog) |

## Status

**Accepted, 2026-02-26; re-confirmed after CR-008 was assessed.** Deciders: Product Owner, Engineering Lead, Business Analyst. Consulted: Customer Success Lead, pilot agency finance staff (PER-04 profile).

## Context and problem statement

Discovery found that payroll preparation takes 14 hours per pay period per agency (target 3 hours or less). The time goes into collecting timesheets, reconciling them with schedules, calculating overtime, holiday and travel time, and keying hours into the agency's payroll provider. It does not go into tax withholding or payment, which every pilot agency already outsources to a payroll provider.

Tendwell owns the data that determines hours worked: Verified visits (BR-028), travel between visits (BR-043, consistent with the DOL Home Care Rule under the FLSA), holidays (BR-042), overtime (BR-041, including the daily profile from CR-001) and PTO (BR-040). Payroll processing (gross-to-net, federal, state and local tax withholding, garnishments, benefits deductions, direct deposit, pay stubs, W-2 and quarterly filings) is a regulated product category in its own right.

After the baseline, CR-008 requested full in-app payroll processing with tax withholding and pay stubs. It was rejected and deferred to the backlog as out of scope, with export to a payroll provider retained (FR-PAY-05).

Where should Tendwell's payroll responsibility end?

## Decision drivers

1. Hit the payroll-preparation KPI (14 h to 3 h or less) in Release 1.
2. Keep Tendwell out of regulated money movement and tax filing it is not staffed or licensed to operate.
3. Accuracy and traceability of hours and rates (FR-PAY-02, FR-PAY-03, BR-045).
4. Work with whatever payroll provider each agency already uses.
5. Delivery capacity: payroll is one epic among fourteen.

## Considered options

### Option 1: CSV export with configurable column mapping, period lock and adjustments (chosen)

| Pros | Cons |
|---|---|
| Removes the time-consuming work (collection, reconciliation, calculation, keying) | Agency still uploads the file to its provider each period |
| Works with any provider that imports CSV | Column mappings must be maintained per provider format |
| Clear responsibility boundary: Tendwell prepares hours and amounts, the provider pays and files | No pay stub in Tendwell for caregivers |
| Small, testable scope; worked examples verify every rule | |

### Option 2: Direct API integrations with selected payroll providers

| Pros | Cons |
|---|---|
| No file handling; status visible in Tendwell | One integration per provider; pilot agencies use different providers |
| | Provider APIs, partner agreements and certification take months each |
| | Hours data would still need the same calculation engine as Option 1 |

### Option 3: Embedded payroll through a white-label payroll partner

| Pros | Cons |
|---|---|
| Caregivers get pay stubs in the app; possible revenue stream | Makes Tendwell responsible to agencies for payroll outcomes it does not control |
| | Agencies would have to migrate payroll mid-year (tax filings, year-to-date balances) |
| | Large scope: onboarding, KYC, funding flows, support for tax notices |

### Option 4: Build in-house payroll processing (the CR-008 scope)

| Pros | Cons |
|---|---|
| Full control and single product experience | Requires tax-table maintenance for every state and locality, filings, money transmission controls and a payroll operations team |
| | Liability for wage and tax errors; outside the company's competence |
| | Would consume more than the entire R1 delivery capacity |

## Decision outcome

**Chosen option: Option 1, payroll preparation and CSV export**, because it removes the work that drives the 14-hour baseline (driver 1) while keeping Tendwell out of money movement and tax filing (driver 2). Option 2 stays a candidate for a later release if several tenants share a provider. Options 3 and 4 are out of scope; CR-008 is recorded as Rejected / deferred in the change request log.

Scope of Tendwell's payroll module:

1. Pay periods (weekly, bi-weekly, semi-monthly) per tenant (FR-PAY-01).
2. Pay calculation from Verified visits and approved time only, merging overlapping time to the second (FR-PAY-02, FR-PAY-03, BR-045), producing payroll lines of type Regular, Overtime, DoubleTime, Holiday, Travel, PTO, Mileage and Adjustment.
3. Pre-export review of caregivers with open exceptions or unverified visits (FR-PAY-04).
4. CSV export with a tenant-configured column mapping (provider employee ID, earnings codes, hours, rate, amount); the period locks on export and the file's SHA-256 and row count are stored in `payroll_exports` (FR-PAY-05, BR-046).
5. Later changes to a locked period become adjustment lines in the next open period that reference the original visit (FR-PAY-06).
6. Every export is audited and watermarked (BR-058). Because providers reject unexpected rows, the watermark is carried in the file name (tenant, period, user, UTC timestamp) and in an export manifest stored with the file; an optional trailer row is off by default (SRS TBD-14 working assumption).

Canonical check (US-041): caregiver E-2041 Maya Ortiz, workweek 2026-09-07 to 2026-09-13, hourly $19.50, produces Holiday 6.0 h at $29.25 = $175.50, Regular 31.5 h = $614.25, Travel 2.5 h = $48.75 and Overtime 3.0 h at $29.25 = $87.75, for total wages of $926.25, plus mileage reimbursement of 46.2 mi at $0.70 = $32.34, for a total payable of $958.59. Overtime falls on the last 3.0 hours chronologically (Sunday), and no minute is paid at both the holiday and overtime multipliers (BR-042).

## Consequences

**Positive**

- R1 attacks the actual cost driver; Customer Success measures preparation time per period against the 3-hour target.
- Responsibility is explicit: Tendwell is designed to support FLSA hours-worked calculations, and the agency remains responsible for wage-and-hour compliance and for running payroll.
- The export file is reproducible and verifiable by hash, which supports audits and disputes.

**Negative**

- Caregivers do not see pay stubs in Tendwell; they see hours and pay-line summaries only.
- Provider column mappings need maintenance; Customer Success owns a library of mapping templates.
- A requested in-app payroll capability (CR-008) remains unmet; it is tracked in the backlog for market validation.
- File-based handoff can be mishandled by users (wrong file uploaded); the lock, file name watermark and hash reduce but do not remove that risk.

## Compliance and requirements links

| Type | IDs |
|---|---|
| Functional requirements | FR-PAY-01 to FR-PAY-06, FR-TOF-05 |
| Business rules | BR-015, BR-028, BR-040, BR-041, BR-042, BR-043, BR-044, BR-045, BR-046, BR-058 |
| Change requests | CR-008 (Rejected / deferred), CR-001 (daily overtime profile) |
| User stories | US-041, US-042, US-043 |
| Non-functional requirements | NFR-PERF-04, NFR-MNT-01 |
| Regulation (designed to support) | FLSA and the DOL Home Care Rule (travel time between clients is hours worked) |

## Related documents

- [Change request log](../../../05-delivery/change-request-log.md)
- [EP-10 Payroll user stories](../../../05-delivery/user-stories/EP-10-payroll.md)
- [State machines: pay period](../../diagrams/state-machines.md)
- [Wireframe web-03 payroll pre-export review](../../wireframes/README.md)
- [Business rules](../../../02-requirements/business-rules.md)
- [Decision log](../../../05-delivery/decision-log.md)
