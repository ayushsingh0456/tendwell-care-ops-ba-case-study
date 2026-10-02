# ADR-002: Append-only EVV punch ledger with supersession

## Document control

| Field | Value |
|---|---|
| Document ID | ADR-002 |
| Version | 1.1 |
| Status | Accepted |
| Owner | Business Analyst |
| Last updated | 2026-09-24 |
| Reviewers | Engineering Lead, Compliance and Privacy Officer, QA Lead, Product Owner |

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-03-04 | Accepted before Sprint S1 |
| 1.1 | 2026-09-24 | Bulk resolution (CR-004) confirmed to act on exceptions only, never on punches |

## Status

**Accepted, 2026-03-04.** Deciders: Engineering Lead, backend developers, Business Analyst. Consulted: Compliance and Privacy Officer, Customer Success Lead (pilot agencies).

## Context and problem statement

An EVV punch is evidence that care was delivered at a place and time. Under the 21st Century Cures Act (Section 12006), each visit must capture six data elements (BR-020), and state Medicaid programs and auditors expect that any change to visit times is explainable: who changed it, when, why, and what the original value was. Pay (FR-PAY-02) and billing (FR-BIL-01) are derived from these times, so an undetected edit changes wages and claims.

Punch data arrives from three paths: online clock-in and clock-out, offline capture synced hours later (FR-EVV-05, BR-025), and Coordinator time corrections in the exception queue (FR-EVV-08). The system also writes a placeholder clock-out when it auto-closes a visit left open for 14 hours (BR-027). BR-026 states that punches are append-only and that a correction adds a new Manual punch with reason code, note and editor identity while the original stays visible.

How should Tendwell store punches so that corrections are possible, history is tamper-evident and the "effective" times used for pay and billing are unambiguous?

## Decision drivers

1. Auditability: the original and every correction remain visible with actor, reason and time (BR-026, BR-057).
2. Unambiguous effective times for verification, payroll and billing (FR-EVV-10, BR-028).
3. Safe handling of late and duplicate offline submissions (BR-025, NFR-AVL-02).
4. Simplicity for a small team; no exotic infrastructure.
5. Query performance for the schedule board and payroll at 2 million visits per month (NFR-PERF-03, NFR-SCL-01).

## Considered options

### Option 1: Mutable visit times plus audit log

`visits` holds `actual_start` and `actual_end`; corrections update them and `audit_events` records before and after values.

| Pros | Cons |
|---|---|
| Simple reads: the visit row has the answer | The evidence (GPS, device, accuracy) of the original punch is lost or must be duplicated into the audit log |
| Familiar CRUD pattern | Integrity depends on every code path writing the audit event; a missed path silently rewrites history |
| | Late offline punches overwrite Coordinator decisions unless special-cased |

### Option 2: Append-only punch ledger with `supersedes_punch_id` (chosen)

Each punch is a row in `evv_punches`. Rows are never updated or deleted. A correction inserts a new punch that references the punch it replaces.

| Pros | Cons |
|---|---|
| History is structural, not dependent on audit code paths | Reads need an "effective punch" rule (view or materialized columns) |
| Each punch keeps its own evidence: source, coordinates, accuracy, device, identity check, reason, note, author | More rows (about 2.3 punches per visit on average) |
| Late and duplicate submissions are naturally additive and idempotent by punch ID | Requires clear precedence rules when human and device punches compete |
| Database grants can enforce insert-only | |

### Option 3: Full event sourcing of the visit aggregate

All visit changes (scheduled, reassigned, punched, corrected, verified) are events; projections build current state.

| Pros | Cons |
|---|---|
| Complete history of every visit change, replayable | Large conceptual and tooling cost for a team of two backend developers |
| Natural fit for audit and analytics | Every read model (board, payroll, billing) becomes a projection to build, version and rebuild |
| | Scheduling changes already have adequate history in `audit_events`; the evidence problem is specific to punches |

### Option 4: Trigger-based temporal history table

Keep mutable punch rows; a trigger copies the old row to `evv_punches_history` on update.

| Pros | Cons |
|---|---|
| Transparent to application code | History lives in a second table that reports and auditors must join; the "current" row is still mutable |
| | Triggers are easy to disable during maintenance and hard to reason about in migrations |
| | Does not express intent (which punch replaced which, and why) |

## Decision outcome

**Chosen option: Option 2, an append-only punch ledger with supersession**, because it makes the evidence trail structural (driver 1), keeps effective-time logic explicit (driver 2) and handles offline sync additively (driver 3) without the cost of full event sourcing (driver 4).

Rules:

1. **Insert only.** The application role has `INSERT` and `SELECT` on `evv_punches`, no `UPDATE` or `DELETE`. A trigger rejects updates and deletes as defense in depth.
2. **Punch identity.** Device punches carry a client-generated UUID as `id`; resubmission of the same ID is a no-op (`ON CONFLICT (id) DO NOTHING`), which makes offline retries idempotent.
3. **Supersession.** A correction inserts a punch with `source = Manual`, `reason_code`, `note`, `created_by` and `supersedes_punch_id` set to the punch it replaces. A unique index on `supersedes_punch_id` lets each punch be superseded at most once, so corrections form a single chain; two Coordinators correcting the same punch at once get one success and one 409 conflict.
4. **Adding a missing punch.** A Manual punch with `supersedes_punch_id` null adds a clock-out that never arrived (for example after MISSING_CLOCK_OUT).
5. **Effective punch.** For each visit and punch type, candidates are punches that no other punch supersedes. Precedence among candidates is `Manual` over `Mobile` or `MobileOffline` over `System`; ties go to the latest `received_at`. Pay, billing, verification and the EVV export read effective punches through the `visit_effective_times` view.
6. **Humans are not overridden by devices.** A device punch that arrives after a Manual punch for the same visit and type is stored and shown in the visit history but does not become effective. A Coordinator who wants the device time records a new Manual punch that supersedes the previous Manual punch.
7. **System placeholders yield to evidence.** When a late device clock-out arrives for an auto-closed visit, the server sets its `supersedes_punch_id` to the System placeholder punch. The AUTO_CLOSED exception still needs Coordinator resolution before the visit can be Verified (BR-027).
8. **Times.** `punch_time` is the device capture time for device punches (BR-025) and the corrected time for Manual punches; `received_at` is always server receipt time. Both are stored in UTC (NFR-DAT-01).
9. **Exceptions are separate.** Resolving or bulk-resolving exceptions (FR-EVV-08, CR-004) changes `visit_exceptions` only; it never inserts or alters punches unless the Coordinator also records a time correction.

Worked example (visit VIS-0106 in the synthetic test data, 2026-09-14 07:00-11:00, client C-10320, caregiver E-2041; times in America/New_York):

| Punch | Type | Source | `punch_time` | `supersedes_punch_id` | Effective |
|---|---|---|---|---|---|
| P1 | In | Mobile | 2026-09-14 07:02 | null | Yes |
| P2 | Out | System | 2026-09-14 11:00 (scheduled-end placeholder written by auto-close at 21:02) | null | No, superseded by P3 |
| P3 | Out | Manual, reason "Caregiver forgot to clock out", note recorded | 2026-09-14 11:05 | P2 | Yes |

## Consequences

**Positive**

- Every number in a payroll export or claim can be traced to specific punches and corrections, with author and reason.
- Offline sync, retries and late arrivals cannot overwrite human decisions or each other.
- State auditors and agency compliance staff can see original and corrected values side by side (BR-026).

**Negative**

- Every consumer must use the effective-time view; querying `evv_punches` directly for times is a code-review rejection reason.
- Storage grows with corrections; `evv_punches` is partitioned by month on `punch_time` and kept for the client record retention period.
- The precedence rule must be explained in training: a late device punch shown in history may not be the time that is paid.
- Locked pay periods are unaffected by later corrections; those flow as adjustment lines in the next open period (FR-PAY-06, BR-046).

## Compliance and requirements links

| Type | IDs |
|---|---|
| Business rules | BR-020, BR-021, BR-025, BR-026, BR-027, BR-028, BR-046, BR-057 |
| Functional requirements | FR-EVV-02, FR-EVV-05, FR-EVV-07, FR-EVV-08, FR-EVV-09, FR-EVV-10, FR-PAY-06 |
| Non-functional requirements | NFR-AVL-02, NFR-DAT-01, NFR-SCL-01, NFR-PRIV-02 |
| Change requests and incidents | CR-004, INC-2026-011 (bulk resolution acts on exceptions only) |
| Regulation (designed to support) | 21st Century Cures Act s.12006; HIPAA Security Rule 45 CFR 164.312(c)(1) integrity |

## Related documents

- [State machines: visit and visit exception](../../diagrams/state-machines.md)
- [Sequence diagrams: clock-in and offline sync](../../diagrams/sequence-diagrams.md)
- [ADR-006 Offline-first caregiver app](ADR-006-offline-first-caregiver-app.md)
- [Data dictionary](../../data/data-dictionary.md)
- [Business rules](../../../02-requirements/business-rules.md)
- [EP-06 EVV user stories](../../../05-delivery/user-stories/EP-06-evv.md)
