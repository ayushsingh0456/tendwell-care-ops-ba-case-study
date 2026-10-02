# ADR-001: Multi-tenancy with a shared schema and PostgreSQL row-level security

## Document control

| Field | Value |
|---|---|
| Document ID | ADR-001 |
| Version | 1.1 |
| Status | Accepted |
| Owner | Business Analyst |
| Last updated | 2026-06-12 |
| Reviewers | Engineering Lead, Compliance and Privacy Officer, QA Lead |

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-02-20 | Accepted at architecture review before the SRS baseline |
| 1.1 | 2026-06-12 | Support-grant context and the CI isolation suite added after UAT |

## Status

**Accepted, 2026-02-20.** Deciders: Engineering Lead, backend developers, Compliance and Privacy Officer. Consulted: Business Analyst, QA Lead.

## Context and problem statement

Tendwell is a multi-tenant SaaS product. Each agency (tenant) is a HIPAA covered entity whose client records, care documentation and payroll data must never be visible to another agency. BR-001 requires that isolation is enforced in the database, not only in the user interface or application code. At the same time the platform must scale to 500 tenants, 50,000 caregivers and 2 million visits per month (NFR-SCL-01) with a delivery team of two backend developers, and support per-tenant export within 5 business days and deletion within 90 days of cancellation (NFR-PRIV-03).

Pilot tenants range from 14 staff (TEN-002 Cedar Lane Adult Day Center) to 62 caregivers and 180 clients (TEN-001 Harborview Home Care). Most future tenants are similar in size, so per-tenant infrastructure would be mostly idle.

How should Tendwell partition tenant data so that isolation is enforced by the database while the system stays affordable and operable by a small team?

## Decision drivers

1. Isolation enforced below the application layer (BR-001, FR-IAM-06), so a single missing `WHERE` clause cannot leak data.
2. Operability by a small team: one schema to migrate, monitor and back up (NFR-MNT-02).
3. Scale to 500 tenants without redesign (NFR-SCL-01) and predictable cost per tenant.
4. Per-tenant export and deletion (NFR-PRIV-03) and support for time-boxed support access (FR-IAM-07).
5. Cross-tenant platform operations (plans, anomaly detection, scheduled jobs) without weakening isolation.

## Considered options

### Option 1: Shared schema with `tenant_id` and PostgreSQL row-level security (chosen)

Every tenant-owned table carries `tenant_id`; RLS policies restrict reads and writes to the tenant set in the transaction context.

| Pros | Cons |
|---|---|
| Isolation enforced by PostgreSQL on every query, including ad hoc reports and background jobs | RLS adds a predicate to every query; indexes must lead with `tenant_id` |
| One schema, one migration path, one backup; fits the team size | Noisy-neighbour risk on shared compute; needs per-tenant rate limits and statement timeouts |
| Lowest cost per tenant; scales to 500 tenants on one Multi-AZ cluster with read capacity headroom | Per-tenant deletion is a set of `DELETE` jobs rather than dropping a database; backups keep deleted data until they expire |
| Cross-tenant platform queries are possible through a separate, audited platform role | Requires discipline: forced RLS, non-owner application role, `SET LOCAL` with pooled connections |

### Option 2: Schema per tenant

Each tenant gets its own PostgreSQL schema with identical tables; the application switches `search_path`.

| Pros | Cons |
|---|---|
| Logical separation is visible to operators; per-tenant drop is simple | 500 schemas x about 60 tables = about 30,000 tables; catalog bloat and slow migrations |
| No `tenant_id` predicate needed in queries | Isolation still depends on the application setting `search_path` correctly; a pooled connection with a stale `search_path` leaks data, so BR-001 is not enforced by the database itself |
| | Every migration runs 500 times; partial failure leaves tenants on different schema versions, conflicting with zero-downtime deployments (NFR-MNT-02) |

### Option 3: Database per tenant

Each tenant gets its own database (or RDS instance).

| Pros | Cons |
|---|---|
| Strongest isolation; per-tenant restore, encryption key and deletion are trivial | Cost: an RDS Multi-AZ instance per tenant is uneconomic for 14-staff agencies; shared instances with many databases reintroduce connection-pool and routing complexity |
| Noisy neighbours are physically separated | Provisioning on sign-up becomes slow and failure-prone (FR-ONB-04 expects activation in about a minute) |
| | 500 databases to patch, monitor, back up and test restores for; not operable by the team |

### Option 4: Shared schema with application-level filtering only

ORM scopes add `tenant_id` filters; no database policies.

| Pros | Cons |
|---|---|
| Simplest to build; no RLS overhead | Fails BR-001: one forgotten scope, raw SQL query or reporting job leaks data |
| | No defense in depth; audit and pen-test findings would be likely (NFR-SEC-02) |

## Decision outcome

**Chosen option: Option 1, shared schema with `tenant_id` on every tenant-owned table and forced PostgreSQL row-level security**, because it is the only option that enforces isolation in the database (driver 1) while remaining operable and affordable for the team at the target scale (drivers 2 and 3).

Implementation rules:

1. **Every tenant-owned table has `tenant_id uuid NOT NULL`**, including child tables such as `evv_punches`, `visit_exceptions`, `dose_tasks`, `invoice_lines` and `care_plan_tasks`. The value is copied from the parent and protected by a composite foreign key `(tenant_id, parent_id)`, so a child row can never point to another tenant's parent. Global tables without tenant data (`plans`, `promo_codes`, `permissions`, `job_executions`) have no RLS.
2. **Policies** on each table: `USING (tenant_id = current_setting('app.tenant_id', true)::uuid)` and the same expression in `WITH CHECK`, so writes cannot target another tenant. `ALTER TABLE ... FORCE ROW LEVEL SECURITY` applies policies even to the table owner.
3. **Roles.** The application connects as `tendwell_app`, which owns no tables and has no `BYPASSRLS`. Migrations run as `tendwell_owner` in the pipeline only. Platform jobs that must iterate tenants connect as `tendwell_app` and set the context per tenant; there is no bypass role in the application.
4. **Context.** The `tenancy` module opens every transaction with `SET LOCAL app.tenant_id = <tenant from JWT>` and, for platform support, `SET LOCAL app.support_grant_id`. Because `SET LOCAL` ends with the transaction, pooled connections (RDS Proxy in transaction mode) cannot carry a stale context. If the setting is missing, `current_setting(..., true)` returns null and policies return no rows: the system fails closed.
5. **Support access.** Under an Active grant (BR-008), the context is the granted tenant; a read-only grant sets `app.access_mode = 'read_only'`, and write policies reject rows when that mode is set, in addition to the permission guard.
6. **Users.** `users.tenant_id` is nullable for platform staff; platform users never receive tenant rows except through a grant.
7. **Performance.** Composite indexes lead with `tenant_id`; high-volume tables (`visits`, `evv_punches`, `dose_tasks`, `audit_events`, `notifications`) are range-partitioned by month; per-tenant API rate limits and a 15 s statement timeout limit noisy neighbours.
8. **Verification.** A CI isolation suite enumerates every table with a `tenant_id` column from the catalog, seeds two tenants and asserts that reads, updates and inserts across tenants fail. A new table without a policy fails the build.

## Consequences

**Positive**

- A missing filter in application code returns zero foreign rows instead of leaking data; the guarantee covers reports, exports and jobs alike (BR-001).
- One schema keeps migrations, backups and restore tests simple enough for quarterly rehearsal (NFR-DR-01).
- Cost per tenant stays low enough for small adult day centers.
- The audit trail can attribute support activity to a grant through `app.support_grant_id` (BR-008, BR-057).

**Negative**

- Every child table carries a denormalized `tenant_id`, which the data model must show explicitly; the core entity list in the SRS omits it on some child tables for brevity.
- Tenant deletion (NFR-PRIV-03) runs as an ordered set of deletes per table followed by verification; deleted data persists in backups until they expire (35 days), which the deletion certificate states.
- Developers must use the tenancy helper for all database access; raw connections outside it are blocked by a lint rule and the RLS guard alert.
- A very large tenant could need its own cluster later; the `tenant_id` key keeps that migration possible (tenant-level logical replication) but it is not designed now.

## Compliance and requirements links

| Type | IDs |
|---|---|
| Business rules | BR-001, BR-008, BR-011, BR-057 |
| Functional requirements | FR-IAM-06, FR-IAM-07, FR-ONB-04, FR-RPT-03 |
| Non-functional requirements | NFR-SCL-01, NFR-SEC-02, NFR-SEC-04, NFR-PRIV-03, NFR-MNT-02, NFR-DR-01 |
| Regulation (designed to support) | HIPAA Security Rule 45 CFR 164.312(a)(1) access control |

## Related documents

- [System context and containers](../system-context-and-containers.md)
- [Deployment and security](../deployment-and-security.md)
- [ERD](../../data/erd.md)
- [Data dictionary](../../data/data-dictionary.md)
- [Business rules](../../../02-requirements/business-rules.md)
- [Non-functional requirements](../../../02-requirements/non-functional-requirements.md)
- [Sequence diagrams: support access grant](../../diagrams/sequence-diagrams.md)
