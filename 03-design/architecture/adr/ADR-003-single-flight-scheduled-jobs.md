# ADR-003: Single-flight scheduled jobs and database-enforced billing idempotency

## Document control

| Field | Value |
|---|---|
| Document ID | ADR-003 |
| Version | 1.1 |
| Status | Accepted |
| Owner | Business Analyst |
| Last updated | 2026-09-24 |
| Reviewers | Engineering Lead, QA Lead, Product Owner, Customer Success Lead |

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-07-28 | Accepted after the INC-2026-007 post-incident review |
| 1.1 | 2026-09-24 | Linked to CR-005 as baselined in SRS v1.3 (BR-050, FR-BIL-01) |

## Status

**Accepted, 2026-07-28.** Supersedes the earlier "leader election only" scheduling approach, which was used from the build phase until INC-2026-007 and was never recorded as an ADR.

Deciders: Engineering Lead, backend developers. Consulted: Business Analyst, QA Lead, Product Owner, Customer Success Lead.

## Context and problem statement

The Worker runs scheduled jobs: nightly visit materialization, dose generation and per-minute escalation, auto-close of open visits, credential status, subscription lifecycle, overdue invoices and the nightly billing run that refreshes draft invoices. Until July 2026 single execution relied on leader election only: one Worker task held a lock in Redis with a time-to-live and was the only task allowed to start scheduled jobs. The billing job itself used an application-level check-then-insert to avoid duplicate invoices, with no database unique constraint on the invoice idempotency key.

**INC-2026-007 (SEV-2, 2026-07-21).** During a blue/green deployment overlap, two scheduler Workers both took leadership. The outgoing Worker held a 30-second Redis lock renewed every 10 seconds, but its renewal timer shared the event loop with CPU-heavy invoice pricing; the lock lapsed while the job was still running, and the incoming Worker acquired it and started the same nightly billing job. Both runs passed the "does a draft exist?" check before either inserted. Impact: 214 duplicate draft invoices across 9 tenants; 3 tenants had auto-issue enabled for private pay, so 37 duplicates were emailed; 6 clients paid twice and $2,914.50 was refunded. A customer support ticket detected it; no alert fired.

The incident showed that a lock is a performance optimization, not a correctness guarantee. Blue/green deployments (NFR-MNT-02) guarantee periods where two task sets run, and Redis locks cannot fence a process that has paused or is still finishing work. BR-050 already required that re-running a period never creates a second invoice for the same key, but nothing in the database enforced it. CR-005 (approved, SRS v1.3) carries the requirement changes.

How should scheduled and queued jobs execute exactly once in effect, even when two Workers attempt the same job?

## Decision drivers

1. Correctness under concurrency must be enforced by PostgreSQL, the system of record, not by timing (BR-050, FR-BIL-01).
2. Zero-downtime blue/green deployments must stay possible; overlap is normal, not exceptional (NFR-MNT-02).
3. Jobs must be safe to retry after a crash without manual cleanup.
4. Duplicates that slip through any layer must be detected by an alert, not by customers (NFR-OBS-02).
5. Minimal new infrastructure; the team already runs PostgreSQL, Redis and BullMQ.

## Considered options

### Option 1: Keep leader election only, with fixes (status quo plus)

Lengthen the Redis lock TTL, add lock renewal on a separate timer and stop the old task set before starting the new one.

| Pros | Cons |
|---|---|
| Smallest code change | Still timing-based: a paused process (GC, CPU starvation, network partition) can act after losing the lock |
| | Stopping the old task set before the new one starts gives up zero-downtime deployments |
| | Does nothing for the check-then-insert race inside a job or for duplicate queue delivery |

### Option 2: PostgreSQL advisory locks per job

`pg_try_advisory_lock(hash(job, window))` held for the job's duration.

| Pros | Cons |
|---|---|
| Enforced by the database; no extra table | Session-scoped: lost on connection drop or failover, after which a second runner can start while the first still writes |
| Cheap | Leaves no durable record of what ran, when and with what outcome; no basis for retries or the job-freshness alert |
| | Incompatible with transaction-mode connection pooling unless transaction-scoped, which cannot span a long job |

### Option 3: Durable job claims in `job_executions` plus business unique keys (chosen)

Every job attempt first claims a row in `job_executions` with a unique `idempotency_key`; every job output that must be unique has its own database unique key and is written by upsert.

| Pros | Cons |
|---|---|
| The claim is a durable fact with status and timings; only one insert can win | Each job needs a well-designed idempotency key |
| Business keys make the job safe even if the claim layer is bypassed or a bug reruns it | Business tables need unique keys and upsert logic designed per job |
| Works with any number of Workers and with overlapping deployments | Stale claims from crashed Workers need a takeover rule |
| Gives metrics for freshness and duplicate attempts | |

### Option 4: External single scheduler (for example EventBridge Scheduler) invoking one job

| Pros | Cons |
|---|---|
| One trigger per schedule | Delivery is at-least-once, so duplicates remain possible; idempotency is still needed downstream |
| | Adds a moving part and splits job definitions across code and infrastructure |

## Decision outcome

**Chosen option: Option 3, durable job claims plus database-enforced business idempotency**, in four layers. Correctness never depends on an upper layer: if layers 1 and 2 both failed, layer 3 would still prevent a duplicate invoice. Leader election is removed; any Worker may attempt any job, and PostgreSQL decides.

### Layer 1: Queue de-duplication (efficiency)

Repeatable BullMQ jobs use deterministic job IDs per schedule window, so the queue rarely holds the same window twice. This layer reduces wasted work only; correctness never depends on it.

### Layer 2: `job_executions` claim (single-flight)

Before doing any work, the Worker runs:

```sql
INSERT INTO job_executions (id, job_name, idempotency_key, status, started_at)
VALUES (gen_random_uuid(), 'billing-nightly', 'billing-nightly:<tenant_id>:2026-07-21', 'Running', now())
ON CONFLICT (idempotency_key) DO NOTHING
RETURNING id;
```

No row returned means another Worker owns the window; the job exits and increments `jobs_duplicate_claim_total`.

| Job | Idempotency key pattern |
|---|---|
| Nightly billing draft refresh | `billing-nightly:{tenantId}:{runDate}` |
| On-demand billing run (`POST /billing-runs`) | `billing-run:{tenantId}:{period}:{billingRunId}` |
| Visit materialization | `materialize-visits:{tenantId}:{runDate}` |
| Dose escalation (every minute) | `dose-escalation:{minuteUtc}` |
| Auto-close open visits (every 5 min) | `auto-close:{windowUtc}` |
| Subscription lifecycle | `tenant-lifecycle:{runDate}` |
| Stripe webhook event | `stripe-event:{eventId}` |

Every key embeds the job, the tenant where the job is tenant-scoped, and the business window. The on-demand billing key also carries the run ID, because BR-050 allows a period to be re-run deliberately; each re-run is a new claim that upserts the same Drafts.

**Retry and takeover.** A failed job sets `status = 'Failed'`. A retry, or a takeover of a claim whose Worker died, uses one conditional update that only one Worker can win:

```sql
UPDATE job_executions
SET status = 'Running', started_at = now()
WHERE idempotency_key = $1
  AND (status = 'Failed' OR (status = 'Running' AND started_at < now() - $max_runtime));
```

### Layer 3: Business unique keys and upserts (correctness of outputs)

- `invoices.idempotency_key` = `{tenantId}:{clientId}:{payerId}:{periodStart}:{periodEnd}` (BR-050), enforced by a database unique index over all non-void invoices, as BR-050 states in SRS v1.3. The index excludes `Void` rows only so that the void-and-reissue path in BR-051 can create a replacement invoice for the same key; at any moment at most one non-void invoice exists per key.
- Drafts are written with `INSERT ... ON CONFLICT (idempotency_key) WHERE status <> 'Void' DO UPDATE ... WHERE invoices.status = 'Draft'`. An invoice that is already Approved or Issued is never changed by a run; the run reports it as "skipped, already approved or issued".
- Each invoice and its lines are rebuilt in one transaction that locks the invoice row, so two runs for the same period serialize per invoice and produce the same result.
- A partial unique index on `billing_runs (tenant_id, period_start, period_end) WHERE status = 'Running'` stops two concurrent on-demand runs for the same period; the second request returns the existing run.
- The same pattern protects other outputs: `notifications.dedupe_key` (BR-055), dose tasks unique on `(order_id, scheduled_at)`, materialized visits unique on `(pattern_id, scheduled_start)`, payments unique on `provider_ref`.

### Layer 4: Pre-issue duplicate check and detection

- Before an invoice moves to Issued (manually or by private-pay auto-issue), the system checks for another non-void invoice for the same tenant, client and payer whose period overlaps; if one exists, issue is blocked with a message that names both invoices (CR-005).
- After every billing run, the anomaly check compares the invoice count with the tenant's previous run; a deviation of more than 20% alerts and pauses auto-issue for that run (NFR-OBS-02).

## Consequences

**Positive**

- A repeat of INC-2026-007 cannot produce duplicate invoices: the second insert becomes an update of the same Draft, and an issued invoice is never touched.
- Deployments keep zero downtime; overlapping Workers are expected and harmless.
- `job_executions` gives an auditable record of every scheduled run and feeds the job-freshness alert.
- Other jobs (lifecycle, escalation, materialization) gained the same guarantee; US-006-AC6 tests the lifecycle job against two concurrent Workers.

**Negative**

- Every new job needs a reviewed idempotency key and an upsert or unique key on its outputs; this is now a Definition of Done item for backend stories.
- The partial unique index on invoices must be documented carefully, because "unique" applies to non-void invoices only.
- `job_executions` grows by roughly 2,000 rows per day per environment; rows older than 90 days are archived.
- During blue/green windows the duplicate-claim metric is non-zero by design, so that alert routes to a ticket rather than a page.

## Compliance and requirements links

| Type | IDs |
|---|---|
| Business rules | BR-050, BR-051, BR-055, BR-003 |
| Functional requirements | FR-BIL-01, FR-BIL-04, FR-BIL-05, FR-NTF-04, FR-ONB-07 |
| Non-functional requirements | NFR-MNT-02, NFR-OBS-02, NFR-PERF-04 |
| Change requests and incidents | CR-005; INC-2026-007 |
| User stories | US-044, US-006 |

## Related documents

- [INC-2026-007 post-incident review](../../../07-operations/incidents/INC-2026-007-duplicate-client-invoices.md)
- [Change request log](../../../05-delivery/change-request-log.md)
- [Sequence diagrams: idempotent billing run](../../diagrams/sequence-diagrams.md)
- [State machines: invoice](../../diagrams/state-machines.md)
- [Deployment and security: business anomaly alerts](../deployment-and-security.md)
- [EP-11 Billing user stories](../../../05-delivery/user-stories/EP-11-billing.md)
