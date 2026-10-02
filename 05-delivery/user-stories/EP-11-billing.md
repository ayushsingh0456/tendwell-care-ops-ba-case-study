# EP-11 Client Billing & Invoicing: user stories

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DEL-US-11 |
| Version | 1.3 |
| Status | Baselined |
| Owner | Business Analyst |
| Last updated | 2026-09-24 |
| Reviewers | Product Owner, Engineering Lead, QA Lead, Customer Success Lead, Compliance and Privacy Officer |

## Purpose and scope

This file holds the user stories and acceptance criteria for EP-11. It covers billing runs, pricing by billing model with authorization caps, the invoice lifecycle, online payment for private-pay invoices, overdue reminders, payer claim batch export and credit notes. Claims are exported as CSV for the agency's clearinghouse; there is no EDI 837 in R1.

Version 1.3 aligns US-044 with CR-005 (SRS v1.3, raised from INC-2026-007): the billing idempotency key is enforced by a database unique constraint, and a pre-issue duplicate check runs before any invoice is issued.

## Epic

| Field | Value |
|---|---|
| Epic ID | EP-11 |
| Name | Client Billing & Invoicing |
| Module | BIL |
| Goal | Turn Verified visits into correct, authorization-capped invoices and claim files within 2 business days of period end, collect private-pay balances online, and make duplicate invoices impossible. |
| Objectives | OBJ-04 Days to invoice (9 to 2 business days or fewer); OBJ-06 Authorization-overrun denials (6.1% to 1% or less). |
| Business need | BN-11 |
| Release | R1 |

## Story list

| Story | Title | Persona | Priority | Points | Sprint |
|---|---|---|---|---|---|
| US-044 | Run monthly billing safely | PER-04 Denise Carter (AG-FIN) | Must | 8 | S6 |
| US-045 | Price visits by billing model and authorization cap | System (SYS) | Must | 8 | S6 |
| US-046 | Collect private-pay invoices online | PER-04 Denise Carter (AG-FIN) | Must | 5 | S6 |
| US-047 | Export a payer claim batch | PER-04 Denise Carter (AG-FIN) | Should | 5 | S6 |
| US-048 | Issue a credit note | PER-04 Denise Carter (AG-FIN) | Must | 3 | S6 |
| **Total** | | | | **29** | |

Canonical worked example (used in US-045): client C-10234, authorization T1019 at $7.25 per 15-minute unit; visits A 127 minutes, B 113 minutes, C 120 minutes.

## Stories

### US-044 · Run monthly billing safely

| Field | Value |
|---|---|
| Epic | EP-11 Client Billing & Invoicing |
| Persona | PER-04 Denise Carter (AG-FIN) |
| Priority | Must |
| Estimate | 8 points |
| Sprint / Release | S6 / R1 |
| Requirements | FR-BIL-01, FR-BIL-04 |
| Business rules | BR-028, BR-050, BR-051 |
| Dependencies | US-045, US-029 |

**Story**
As a Billing & Payroll Specialist, I want to run billing for a period and get exactly one draft invoice per client per payer from Verified visits, so that I can approve and issue invoices within two days without hunting for duplicates or gaps.

**Acceptance criteria**

```gherkin
Scenario: US-044-AC1 Create one draft invoice per client per payer
  Given C-10234 has Verified visits in September 2026 under "Lakemont County Medicaid" and under private pay
  When Denise starts the billing run for 2026-09-01 to 2026-09-30 with an Idempotency-Key header
  Then two Draft invoices are created for C-10234, one per payer, numbered like "INV-2026-000123"
  And each invoice carries the idempotency key tenant + client + payer + period

Scenario: US-044-AC2 Re-running a period updates drafts and never duplicates
  Given the September run created a Draft invoice for C-10234 and "Lakemont County Medicaid"
  And 2 more of the client's September visits became Verified afterwards
  When Denise re-runs billing for September
  Then the existing Draft invoice is updated with the 2 visits
  And no second invoice exists for the same tenant, client, payer and period
  And invoices that are already Approved or Issued are not changed and are listed as "Skipped: already approved"

Scenario: US-044-AC3 Concurrent runs cannot create duplicate invoices
  Given two scheduler workers start the September billing run for the same tenant at the same moment
  When both try to insert an invoice for C-10234 and "Lakemont County Medicaid"
  Then the database unique constraint on the idempotency key allows exactly one invoice
  And the second worker's insert becomes an update of that Draft, with no error shown to users
  And the run summary shows the same invoice count as a single run

Scenario: US-044-AC4 Check for duplicates before issuing
  Given a non-void invoice INV-2026-000123 already exists for C-10234, "Lakemont County Medicaid" and September 2026
  When Denise tries to issue another invoice for the same client, payer and period
  Then issuing is blocked with "Possible duplicate of INV-2026-000123. Void one of them before issuing."
  And the block applies to automatic issuing of private-pay invoices as well

Scenario Outline: US-044-AC5 Enforce the invoice lifecycle
  Given an invoice with status "<status>"
  When Denise tries to <action>
  Then the result is "<result>"

  Examples:
    | status        | action                     | result                                                              |
    | Draft         | approve it                 | status Approved                                                     |
    | Approved      | issue it                   | status Issued, issue date set, due date 30 days later               |
    | Issued        | edit a line                | rejected: "Issued invoices cannot be edited. Use a credit note."    |
    | Issued        | void it, unpaid            | status Void                                                         |
    | PartiallyPaid | void it                    | rejected: "Invoices with payments cannot be voided. Use a credit note." |
    | Draft         | issue it without approval  | rejected: "Approve the invoice before issuing it."                  |

Scenario: US-044-AC6 Bill only Verified visits
  Given C-10234 has 12 Completed visits in September, of which 11 are Verified and 1 is Needs review
  When billing runs for September
  Then the invoice includes the 11 Verified visits
  And the Needs review visit appears in the run summary as "Unbilled: pending verification"
```

**Notes**
- AC3 and AC4 were added in R1.1 by CR-005 after INC-2026-007, when a deployment overlap let two scheduler workers run the nightly billing run; the application-level check-then-insert raced and 214 duplicate drafts were created across 9 tenants.
- NFR-OBS-02 raises an alert when a run's invoice count deviates by more than 20% from the previous run.
- Billing runs are single-flight (ADR-003); the database constraint is the last line of defense if single-flight fails.
- Performance: a run for 1,000 clients completes within 10 minutes (NFR-PERF-04).

### US-045 · Price visits by billing model and authorization cap

| Field | Value |
|---|---|
| Epic | EP-11 Client Billing & Invoicing |
| Persona | System (SYS) |
| Priority | Must |
| Estimate | 8 points |
| Sprint / Release | S6 / R1 |
| Requirements | FR-BIL-02, FR-BIL-03 |
| Business rules | BR-047, BR-048, BR-049 |
| Dependencies | US-013, US-029 |

**Story**
As the billing engine, I want to price each Verified visit with the billing model of its matching authorization and cap units at what remains authorized, so that invoices match what the payer will pay and authorization overruns never reach a claim.

**Acceptance criteria**

```gherkin
Scenario: US-045-AC1 Price hourly visits in 15-minute units
  Given C-10234's authorization T1019 is Hourly at $7.25 per 15-minute unit with enough units remaining
  And visits A, B and C lasted 127, 113 and 120 Verified minutes
  When the visits are priced
  Then the invoice lines are:
    | visit | minutes | calculation            | units |
    | A     | 127     | 8 r7, no round-up      | 8     |
    | B     | 113     | 7 r8, round up         | 8     |
    | C     | 120     | 8 r0                   | 8     |
  And the total is 24 units = $174.00

Scenario Outline: US-045-AC2 Round units at the 8-minute boundary
  When a Verified hourly visit lasts <minutes> minutes
  Then it is billed as <units> units

  Examples:
    | minutes | units |
    | 7       | 0     |
    | 8       | 1     |
    | 15      | 1     |
    | 22      | 1     |
    | 23      | 2     |
    | 127     | 8     |
    | 113     | 8     |

Scenario: US-045-AC3 Cap billed units at the remaining authorization
  Given only 20 units remain on C-10234's T1019 authorization
  When visits A, B and C (24 units) are priced
  Then 20 units are billable for $145.00
  And 4 units appear on a line "Not billable - exceeds authorization" that is excluded from the invoice total

Scenario: US-045-AC4 Price a daily rate once per calendar day
  Given an adult day participant's authorization S5102 is Daily at $78.00 per day
  And the participant attended on 14 days in September 2026, with two check-ins on 2026-09-15
  When September is priced
  Then 14 daily charges are billed for $1,092.00
  And 2026-09-15 is charged once

Scenario: US-045-AC5 Prorate a fixed monthly rate in the month of admission
  Given a supported-living resident's authorization is Fixed monthly at $6,200.00
  And the resident was admitted on 2026-09-10, so active 21 of 30 days in September
  When September is priced
  Then the charge is $4,340.00 (6,200 x 21/30)

Scenario Outline: US-045-AC6 Per-visit pricing and visits without a matching authorization
  Given a Verified visit with <authorization>
  Then the invoice line is <line>

  Examples:
    | authorization                                   | line                                                         |
    | a Per visit authorization at $55.00, 47 minutes | 1 unit at $55.00, billable                                   |
    | a Per visit authorization at $55.00, 95 minutes | 1 unit at $55.00, billable                                   |
    | no active authorization covering the visit date | 0 billable, non-billable reason "No matching authorization"  |
```

**Notes**
- Minutes are the Verified duration between the effective clock-in and clock-out, after any Manual corrections (BR-026).
- Unit rounding applies per visit, not to the monthly total (BR-047); the rule is tenant-configurable, with 8-minute rounding as the default (DEC-06).
- Non-billable lines are kept on the invoice for transparency and excluded from totals and claim batches.
- Remaining units for the cap are recalculated per run in visit date order, so earlier visits are billed first.

### US-046 · Collect private-pay invoices online

| Field | Value |
|---|---|
| Epic | EP-11 Client Billing & Invoicing |
| Persona | PER-04 Denise Carter (AG-FIN) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S6 / R1 |
| Requirements | FR-BIL-05, FR-BIL-08 |
| Business rules | BR-052 |
| Dependencies | US-044, DEP-05 |

**Story**
As a Billing & Payroll Specialist, I want private-pay invoices sent with a card or ACH payment link and their status updated automatically, so that families can pay in minutes and I stop chasing checks.

**Acceptance criteria**

```gherkin
Scenario: US-046-AC1 Send an invoice with a payment link and no PHI
  Given INV-2026-000141 for $174.00 is Approved for a private-pay client whose legal representative is "jamie.kimball@example.org"
  When Denise issues it
  Then an email is sent to "jamie.kimball@example.org" with the agency name, the invoice number, the amount due $174.00, the due date and a payment link
  And the email body contains no client name, service description, diagnosis or address

Scenario: US-046-AC2 Record a payment from the provider's webhook
  When the payment provider sends a signed "payment succeeded" webhook for $174.00 on INV-2026-000141
  Then a payment is recorded with method Card and the provider reference
  And the invoice status is "Paid" with balance $0.00

Scenario: US-046-AC3 Ignore duplicate and unsigned webhooks
  Given the webhook event "evt_0001" was already processed
  When the same event is delivered again
  Then the server returns 200 and records no second payment
  When a webhook arrives with an invalid signature
  Then the server returns 400, changes nothing and logs a security event

Scenario: US-046-AC4 Record a partial payment
  When a signed webhook reports a payment of $100.00 on the $174.00 invoice
  Then the invoice status is "PartiallyPaid" with balance $74.00

Scenario Outline: US-046-AC5 Mark overdue and send reminders
  Given INV-2026-000141 was issued 2026-10-01 with net 30 terms, due 2026-10-31, and is unpaid
  When the daily job runs on <date>
  Then <result>

  Examples:
    | date       | result                                          |
    | 2026-10-31 | the invoice is Issued and no reminder is sent   |
    | 2026-11-01 | the invoice is Overdue and reminder 1 is sent   |
    | 2026-11-07 | reminder 2 is sent                              |
    | 2026-11-14 | reminder 3 is sent                              |
    | 2026-11-15 | no reminder is sent                             |

Scenario: US-046-AC6 Handle a failed ACH payment
  Given INV-2026-000141 was marked Paid from an ACH payment
  When the provider reports the ACH payment as failed
  Then the payment status is "Failed", the balance returns to $174.00 and the invoice status returns to Overdue or Issued based on the due date
  And Denise receives an in-app notification
```

**Notes**
- Payment pages are hosted by the payment provider; Tendwell never handles card or bank details (PCI DSS scope stays with the provider).
- An invoice paid before a reminder date receives no further reminders.
- Out of scope: autopay, payment plans and payer remittance (835) import.

### US-047 · Export a payer claim batch

| Field | Value |
|---|---|
| Epic | EP-11 Client Billing & Invoicing |
| Persona | PER-04 Denise Carter (AG-FIN) |
| Priority | Should |
| Estimate | 5 points |
| Sprint / Release | S6 / R1 |
| Requirements | FR-BIL-06 |
| Business rules | None |
| Dependencies | US-044 |

**Story**
As a Billing & Payroll Specialist, I want to export a claim batch file per payer and period, so that I can submit claims through our clearinghouse without retyping them.

**Acceptance criteria**

```gherkin
Scenario: US-047-AC1 Export a claim batch for a payer and period
  Given "Lakemont County Medicaid" has 62 Approved or Issued invoices for September 2026
  When Denise exports a claim batch for that payer and period
  Then a CSV is created with one row per billable invoice line, including Medicaid ID, authorization number, service code, service dates, units, unit rate and amount
  And the batch records the claim count and the total
  And the export carries a watermark with Denise's name, the tenant and the timestamp and creates an audit event

Scenario: US-047-AC2 Exclude lines that cannot be claimed
  Given the September invoices include 3 "Not billable - exceeds authorization" lines and 1 Draft invoice
  When the batch is exported
  Then none of those lines are in the file

Scenario: US-047-AC3 Report claims with missing data
  Given 2 invoices belong to a client with no Medicaid ID on file
  When Denise exports the batch
  Then those 2 invoices are left out and listed in an error report "Medicaid ID missing"
  And the batch is created for the other 60 invoices

Scenario: US-047-AC4 Warn before exporting the same period twice
  Given a batch for "Lakemont County Medicaid" and September 2026 was exported on 2026-10-02
  When Denise exports the same payer and period again
  Then she is warned "A batch for this payer and period was exported on 2026-10-02. Exporting again may create duplicate claims."
  And the export runs only after she confirms
```

**Notes**
- The column layout is configurable per payer so that each clearinghouse template can be matched without code changes.
- The file contains PHI; it is downloaded through a short-lived link and audited as a PHI export.
- Delivery: S6 stretch item, completed in hardening week 1 on 2026-06-03 (see the release and sprint plan).
- Out of scope: EDI 837 generation and clearinghouse APIs (backlog).

### US-048 · Issue a credit note

| Field | Value |
|---|---|
| Epic | EP-11 Client Billing & Invoicing |
| Persona | PER-04 Denise Carter (AG-FIN) |
| Priority | Must |
| Estimate | 3 points |
| Sprint / Release | S6 / R1 |
| Requirements | FR-BIL-07 |
| Business rules | BR-051 |
| Dependencies | US-044 |

**Story**
As a Billing & Payroll Specialist, I want to correct an issued invoice with a credit note and a reason, so that the client's balance is right while the original invoice stays untouched for audit.

**Acceptance criteria**

```gherkin
Scenario: US-048-AC1 Issue a credit note against an issued invoice
  Given INV-2026-000123 for $174.00 is Issued and unpaid
  When Denise issues a credit note of $14.50 with reason "Visit B time corrected: 2 units overbilled"
  Then the credit note is saved with its own number, the reason and Denise as issuer
  And the invoice balance is $159.50
  And the invoice lines and total stay unchanged

Scenario Outline: US-048-AC2 Validate the credit amount
  Given INV-2026-000123 totals $174.00 with no earlier credits
  When Denise enters a credit of <amount>
  Then the result is "<result>"

  Examples:
    | amount  | result                                                               |
    | $0.00   | rejected: enter an amount greater than $0.00                         |
    | $174.00 | accepted, balance $0.00                                              |
    | $174.01 | rejected: the credit cannot exceed the uncredited total of $174.00   |

Scenario: US-048-AC3 A reason is required
  When Denise issues a credit note without a reason
  Then it is rejected with "Enter the reason for this credit note."

Scenario Outline: US-048-AC4 Credit notes only on issued invoices
  Given an invoice with status "<status>"
  When Denise tries to issue a credit note
  Then the result is "<result>"

  Examples:
    | status | result                                                       |
    | Draft  | rejected: "Edit the draft instead of issuing a credit note." |
    | Void   | rejected: "This invoice is void."                            |
    | Paid   | accepted, and the balance shows the credit due to the payer  |
```

**Notes**
- A credit on a Paid invoice creates a credit balance shown as "Credit due"; refunds are handled in the payment provider and recorded against the invoice.
- Credit notes are included in AR ageing (US-051) and in the audit log.

## Related documents

- [Epics overview](../epics.md)
- [Change request log](../change-request-log.md)
- [Decision log](../decision-log.md)
- [Software requirements specification](../../02-requirements/SRS.md)
- [Business rules catalog](../../02-requirements/business-rules.md)
- [ADR-003 Single-flight scheduled jobs](../../03-design/architecture/adr/ADR-003-single-flight-scheduled-jobs.md)
- [Events and webhooks](../../04-api/events-and-webhooks.md)
- [INC-2026-007 Duplicate client invoices](../../07-operations/incidents/INC-2026-007-duplicate-client-invoices.md)
- [Test cases](../../06-quality/test-cases.md)
