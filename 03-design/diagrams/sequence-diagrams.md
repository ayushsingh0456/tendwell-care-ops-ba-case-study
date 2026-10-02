# Sequence Diagrams

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DGM-02 |
| Version | 1.3 |
| Status | Approved |
| Owner | Business Analyst |
| Last updated | 2026-09-28 |
| Reviewers | Engineering Lead, QA Lead, Compliance and Privacy Officer |

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-03-02 | Baseline with SRS v1.0 |
| 1.2 | 2026-07-28 | Billing run rewritten for job claims and invoice unique key (ADR-003, INC-2026-007) |
| 1.3 | 2026-09-28 | Low GPS accuracy evaluated before mismatch (CR-004); send-time recipient resolution and dispatch guard (CR-006) |

### Purpose and scope

These sequence diagrams show how containers and modules collaborate for the seven interactions where ordering, idempotency or security matters most. They complement the [process flows](process-flows.md) (who does what) and the [state machines](state-machines.md) (which states change). Endpoint names follow the [OpenAPI specification](../../04-api/openapi.yaml); request and response bodies are abbreviated. Times are America/New_York unless marked UTC. All data is fictional.

## 1. Clock-in with identity check and geofence evaluation

```mermaid
sequenceDiagram
  autonumber
  actor CG as Caregiver (Rosa Delgado)
  participant App as Caregiver Mobile App
  participant SDK as Vendor SDK on device
  participant API as API, evv module
  participant IDV as IdentityVerificationPort adapter
  participant DB as PostgreSQL

  CG->>App: Tap Clock in on 08:00-10:00 visit, client C-10289
  App->>App: Request precise location fix, read accuracy
  Note right of App: Shows accuracy only. The app holds no client<br/>coordinates and never sends a distance (BR-021).
  opt Tenant requires identity verification (FR-EVV-04)
    App->>SDK: Start guided selfie capture
    SDK-->>App: Encrypted, vendor-signed capture package
    App->>API: POST /visits/{visitId}/identity-checks
    API->>IDV: verify(enrollmentRef, capturePackage)
    IDV-->>API: livenessPassed true, matchScore 0.97
    API->>DB: INSERT identity_checks result Pass, expires_at now + 90 s
    API-->>App: 201 identityCheckId, expiresAt
    Note over API,IDV: Capture package held in memory only, never stored or logged
  end
  App->>API: POST /visits/{visitId}/clock-in with lat, lng, accuracyM, deviceTime, deviceId, identityCheckId
  API->>DB: BEGIN, SET LOCAL app.tenant_id
  API->>DB: Visit assigned to caller, status Scheduled, now between start - 15 min and scheduled end
  API->>DB: UPDATE identity_checks SET consumed_at = now() WHERE unused, unexpired, same caregiver and visit
  alt Check consumed
    Note over API: identity_check_id stored on the punch (BR-024)
  else Missing, expired, reused, or Fail after three attempts
    API->>DB: INSERT visit_exceptions IDENTITY_CHECK_FAILED
  end
  API->>API: distance_m = great-circle distance from fix to client lat, lng
  alt accuracy_m over 100 or coordinates 0,0
    API->>DB: INSERT visit_exceptions LOW_GPS_ACCURACY
  else distance_m over geofence radius 150 m
    API->>DB: INSERT visit_exceptions LOCATION_MISMATCH
  else Within radius with usable accuracy
    Note over API: No location exception
  end
  opt punch_time later than scheduled start + 10 min
    API->>DB: INSERT visit_exceptions LATE_START
  end
  API->>DB: INSERT evv_punches type In, source Mobile, punch_time, received_at, lat, lng, accuracy_m, distance_m
  API->>DB: UPDATE visits status InProgress, care_plan_version = Active version
  API->>DB: INSERT audit_events, COMMIT
  API-->>App: 201 punchId, visit InProgress, exceptions list
  App-->>CG: Clocked in 08:03, 14 m from the address, tasks shown
```

*Figure 1. Online clock-in. Supports FR-EVV-01 to FR-EVV-04, FR-EVV-07, BR-021 to BR-024 and NFR-PERF-02 (2 s p95 round trip, 4 s p95 identity check). The punch is never blocked by location or identity results (FR-EVV-03); accuracy is evaluated before distance so an imprecise fix cannot create a false mismatch (CR-004, INC-2026-011).*

Geofence evaluation with the canonical examples (radius 150 m, accuracy threshold 100 m):

| Distance (server-computed) | Reported accuracy | Evaluation | Result |
|---|---|---|---|
| 212 m | 18 m | Accuracy usable; 212 m is over 150 m | LOCATION_MISMATCH |
| 95 m | 3,400 m | Accuracy worse than 100 m, so distance is not trusted | LOW_GPS_ACCURACY (not mismatch) |
| 40 m | 12 m | Accuracy usable; within radius | No exception |

## 2. Offline punch capture and later sync, including Late offline sync

```mermaid
sequenceDiagram
  autonumber
  actor CG as Caregiver (Rosa Delgado)
  participant App as Caregiver Mobile App
  participant OS as Offline store (SQLCipher outbox)
  participant W as Worker
  participant API as API, evv module
  participant DB as PostgreSQL

  Note over App: Sun 2026-09-13, no connectivity at client C-10301, visit 09:00-11:00
  CG->>App: Tap Clock in
  App->>App: GPS fix, deviceCapturedAt 09:00:40, monotonicMs, bootId, serverOffsetMs
  App->>OS: INSERT command punch In, commandId P1, source MobileOffline
  App-->>CG: Saved on device. It will sync automatically.
  CG->>App: Task statuses, dose outcome, note
  App->>OS: INSERT commands in capture sequence
  CG->>App: Tap Clock out at 11:02
  App->>OS: INSERT command punch Out, commandId P2
  W->>DB: 11:00 missed-visit check, no clock-in received
  W->>DB: UPDATE visits status Missed
  Note over W,DB: Coordinator sees Missed and may call the caregiver (ADR-006)
  Note over App: Mon 2026-09-14 10:30, connectivity returns
  App->>API: POST /auth/refresh
  API-->>App: New access token
  App->>API: POST /evv/punches/sync with P1 and P2 in sequence order
  API->>DB: BEGIN, SET LOCAL app.tenant_id
  loop Each punch
    API->>DB: INSERT evv_punches id = commandId ON CONFLICT (id) DO NOTHING
    API->>API: received_at = now(), compute distance, evaluate accuracy and timing
  end
  Note over API: P1 received 25 h 29 min after capture, over 24 h<br/>P2 received 23 h 28 min after capture, under 24 h
  API->>DB: INSERT visit_exceptions LATE_OFFLINE_SYNC, one per visit
  API->>DB: UPDATE visits Missed to Completed, then NeedsReview (open exception)
  API->>DB: COMMIT
  API-->>App: 200 P1 accepted, P2 accepted, exceptions LATE_OFFLINE_SYNC
  App->>OS: DELETE acknowledged commands P1, P2
  App->>API: Replay dose outcome, task results, note with Idempotency-Key = commandId
  alt Connection drops before the sync response arrives
    App->>API: POST /evv/punches/sync with the same P1 and P2
    API-->>App: 200 P1 duplicate, P2 duplicate
  end
```

*Figure 2. Offline capture and sync. Supports FR-EVV-05, FR-EVV-07, BR-019, BR-025 and NFR-AVL-02. `punch_time` keeps the device capture time and `received_at` the server receipt time; the 24-hour test applies per punch, the exception is raised once per visit.*

## 3. Idempotent billing run

```mermaid
sequenceDiagram
  autonumber
  actor FIN as AG-FIN (Denise Carter)
  participant Web as Agency Web App
  participant API as API, billing module
  participant R as Redis / BullMQ
  participant WA as Worker task A (green)
  participant WB as Worker task B (blue, draining)
  participant DB as PostgreSQL
  participant AL as Alerting

  FIN->>Web: Run billing for 2026-08-01 to 2026-08-31
  Web->>API: POST /billing-runs, Idempotency-Key k-7f3a
  API->>R: Look up cached response for k-7f3a
  API->>DB: INSERT billing_runs status Running
  Note over API,DB: Partial unique index on tenant and period WHERE status Running.<br/>A second concurrent run returns the existing billingRunId.
  API->>R: Enqueue billing-run with a deterministic jobId per billingRunId
  API-->>Web: 202 billingRunId
  Web->>API: Client timeout retry with the same Idempotency-Key k-7f3a
  API-->>Web: 202 same billingRunId from cache
  par Deployment overlap delivers the job twice
    R-->>WA: billing-run job for billingRunId
  and
    R-->>WB: billing-run job for billingRunId
  end
  WA->>DB: INSERT job_executions key billing-run:{tenantId}:2026-08:{billingRunId} ON CONFLICT DO NOTHING RETURNING id
  DB-->>WA: 1 row, claim won
  WB->>DB: Same INSERT
  DB-->>WB: 0 rows
  WB->>WB: Exit, increment jobs_duplicate_claim_total
  loop Each client and payer with Verified visits
    WA->>DB: Read Verified visits, price by billing model, cap at remaining units
    WA->>DB: INSERT invoices ON CONFLICT (idempotency_key) WHERE status not Void DO UPDATE WHERE status = Draft
    WA->>DB: Lock invoice row, replace invoice_lines, COMMIT
  end
  Note over WA,DB: idempotency_key = tenantId:clientId:payerId:2026-08-01:2026-08-31<br/>Approved or Issued invoices are skipped and reported, never changed
  WA->>DB: UPDATE billing_runs Completed, job_executions Succeeded
  WA->>DB: Compare invoice count with the tenant's previous run
  alt Deviation over 20 percent
    WA->>AL: billing_invoice_count_deviation, pause auto-issue for this run
  else Within tolerance
    WA->>API: Run summary ready
  end
  API-->>FIN: In-app notification, drafts ready for review
```

*Figure 3. Billing run safe under retries and overlapping Workers. Supports FR-BIL-01 to FR-BIL-03, BR-047 to BR-050, NFR-MNT-02 and NFR-OBS-02. This is the design adopted in ADR-003 after INC-2026-007 and baselined through CR-005.*

## 4. Payment link and Stripe webhook

```mermaid
sequenceDiagram
  autonumber
  actor FIN as AG-FIN
  participant API as API, billing module
  participant DB as PostgreSQL
  participant ST as Stripe
  participant SES as Amazon SES
  actor RP as Responsible party (private pay)

  FIN->>API: POST /invoices/{invoiceId}/payment-links, Idempotency-Key
  API->>DB: Invoice INV-2026-000187 is Issued, balance 64000 cents
  API->>ST: Create checkout session, amount 64000, invoice number, metadata tenantId and invoiceId
  Note over API,ST: No client name, service code or clinical detail is sent
  ST-->>API: Session URL and provider reference
  API->>DB: Store provider reference, INSERT audit_events
  API->>SES: Email with invoice number, amount $640.00, due date 2026-10-15 and payment link only
  Note over API,SES: No itemized lines or PDF attachment in email (SRS TBD-13)
  RP->>ST: Pay $640.00 by card
  ST->>API: POST /webhooks/payments with Stripe-Signature header (timestamp, v1 signature)
  API->>API: Compute HMAC-SHA256 over timestamp and raw payload, constant-time compare
  alt Signature invalid
    API-->>ST: 400, security event logged without payload
  else Timestamp older than 5 min tolerance
    API-->>ST: 400, replay rejected
  else Valid
    API->>DB: INSERT job_executions key stripe-event:{eventId} ON CONFLICT DO NOTHING
    alt Event already processed
      API-->>ST: 200, duplicate ignored
    else New event
      API->>DB: SET LOCAL app.tenant_id from metadata, confirm invoice, amount and currency
      API->>DB: INSERT payments provider_ref (unique), method Card, 64000 cents, status Succeeded
      API->>DB: UPDATE invoices paid_cents, balance_cents 0, status Paid
      API->>DB: INSERT audit_events, COMMIT
      API-->>ST: 200
    end
  end
  Note over ST,API: ACH: a processing event records a Pending payment and a later<br/>succeeded or failed event completes or reverses it. Stripe retries non-2xx<br/>responses with backoff, so every handler is idempotent.
```

*Figure 4. Private-pay collection. Supports FR-BIL-05, BR-051, BR-052 and BR-056. Signature verification and the time tolerance stop forged and replayed events; the `job_executions` claim and the unique `payments.provider_ref` stop double recording.*

## 5. Missed-dose escalation job and notification dedupe

```mermaid
sequenceDiagram
  autonumber
  participant J as Worker, dose escalation job
  participant API as API, emar module
  participant DB as PostgreSQL
  participant N as Notifications module
  participant Q as BullMQ dispatch queue
  participant P as FCM / APNs
  participant T as Twilio SMS
  actor CG as Caregiver (Tasha Greene)
  actor SU as Clinical Supervisor (Janet Kowalski, RN)

  Note over J,DB: Tue 2026-09-15, Metformin order for client C-30015 scheduled 08:00, window 07:00-09:00
  loop Every minute
    J->>DB: INSERT job_executions key dose-escalation:{minuteUtc} ON CONFLICT DO NOTHING
  end
  J->>DB: 08:00 select Due tasks at scheduled time without a step 1 notice
  J->>N: DoseDue event E1, step 1
  N->>DB: Resolve recipients now: caregiver clocked in to the covering visit, user Active
  N->>DB: INSERT notifications dedupe_key E1:Tasha:1:Push ON CONFLICT DO NOTHING
  N->>Q: Enqueue send
  Q->>P: "A medication task is due. Open Tendwell to review." with deep link
  J->>DB: 09:00 window closed with no outcome, status Overdue
  J->>N: DoseOverdue event E2, step 2
  N->>DB: Resolve recipients now: caregiver and active AG-COORD users for the client's location
  N->>DB: INSERT notifications for each recipient with step 2 dedupe keys
  J->>N: Re-evaluation in a retried job emits E2 step 2 again
  N->>DB: INSERT with the same dedupe keys returns 0 rows
  Note over N: No second message (BR-055)
  alt Caregiver records the outcome at 09:20
    CG->>API: POST /dose-tasks/{doseTaskId}/outcome Given, administered 08:05
    API->>DB: Status Given, is_late_entry true (recorded after window closed)
    API->>N: DoseDocumented event, escalation condition resolved
    N->>DB: Mark queued later-step notifications Suppressed, stop the ladder
  else No outcome by 10:00
    J->>DB: Status MissedUndocumented
    J->>N: DoseMissed event E3, step 3, urgent
    N->>DB: Resolve recipients now: active AG-SUPV users for the location
    N->>DB: Dispatch guard re-checks user status immediately before send
    N->>P: Urgent push, bypasses quiet hours
    N->>T: Urgent SMS "A medication dose needs review. Sign in to Tendwell."
    T-->>N: Delivery failed
    N->>Q: Retry at +1, +4 and +16 min, at most 3 attempts
    SU->>API: Signs in from the deep link, GET /dose-tasks for the client
  end
```

*Figure 5. Dose escalation ladder with dedupe. Supports FR-MAR-04, FR-NTF-02 to FR-NTF-05, BR-030, BR-031, BR-053 to BR-056. Recipients are resolved at send time and re-checked by the dispatch guard (CR-006, INC-2026-015); message bodies carry no client name, drug or diagnosis.*

## 6. Support access grant: request, approve and auto-expire

```mermaid
sequenceDiagram
  autonumber
  actor SUP as PLT-SUP (Platform Console)
  participant API as API, iam module
  participant DB as PostgreSQL
  participant N as Notifications module
  actor ADM as AG-ADM (Tom Brennan)
  participant W as Worker, grant expiry job

  SUP->>API: POST /support-access-grants tenant TEN-001, scope ReadOnly, reason with ticket number, 120 min
  API->>API: Require MFA session, duration 240 min or less
  API->>DB: INSERT support_access_grants status Requested, INSERT audit_events
  API->>N: Notify AG-ADM users of TEN-001, generic text
  alt AG-ADM approves
    ADM->>API: POST /support-access-grants/{grantId}/approve
    API->>DB: status Active, starts_at 12:32, expires_at 14:32, approved_by
    API->>DB: INSERT audit_events
    API->>N: Notify requester, grant active until 14:32
  else AG-ADM declines
    ADM->>API: Decline with reason
    API->>DB: status Declined
  end
  SUP->>API: GET /visits for 2026-09-15 with grant context
  API->>DB: Grant Active, expires_at later than now, tenant matches
  API->>DB: SET LOCAL app.tenant_id, app.support_grant_id, app.access_mode read_only
  API->>DB: Query under RLS, INSERT audit_events actor_type Support with support_grant_id
  API-->>SUP: 200, PHI masked, no reveal permission
  SUP->>API: PATCH /visits/{visitId}
  API-->>SUP: 403 problem details, grant is read-only
  alt AG-ADM revokes early
    ADM->>API: POST /support-access-grants/{grantId}/revoke
    API->>DB: status Revoked, revoked_at
  else Expiry time reached
    W->>DB: Every minute, status Expired where Active and expires_at passed
  end
  SUP->>API: Any request after 14:32
  API-->>SUP: 403 grant expired, enforced on each request even if the job runs late
```

*Figure 6. Time-boxed support access. Supports FR-IAM-07, BR-008 and BR-057, NFR-PRIV-02. Expiry is enforced on every request; the job only updates the status for reporting.*

## 7. PHI reveal with audit

```mermaid
sequenceDiagram
  autonumber
  actor CO as AG-COORD (Marcus Hale)
  participant Web as Agency Web App
  participant API as API, clients module
  participant G as Permission guard
  participant DB as PostgreSQL
  participant K as AWS KMS

  CO->>Web: Open client C-10234 (Harold Jennings)
  Web->>API: GET /clients/{clientId}
  API->>DB: SELECT under RLS
  API-->>Web: 200 masked: dob ****-**-** Age 78, medicaidId ZZ****5522, phone +1-***-***-0187
  CO->>Web: Reveal Medicaid ID, reason "Eligibility check with payer for October"
  Web->>API: POST /clients/{clientId}/phi-reveals fields medicaidId, reason of 10 or more characters
  API->>G: clients:reveal_phi in effective permissions and client in user's locations?
  alt Not permitted
    G-->>API: Deny
    API->>DB: INSERT audit_events client.phi_reveal_denied
    API-->>Web: 403 "You do not have permission to view this field. Ask your administrator."
  else Permitted
    API->>DB: BEGIN, read medicaid_id_enc and wrapped tenant data key
    API->>K: Decrypt data key with encryption context tenant and column
    K-->>API: Data key, cached in memory for 5 min
    API->>API: AES-256-GCM decrypt field
    API->>DB: INSERT audit_events client.phi_revealed with field names and reason, never values
    API->>DB: COMMIT
    Note over API,DB: The audit insert commits before the value is returned.<br/>If auditing fails, the reveal fails (fail closed).
    API-->>Web: 200 medicaidId ZZ48105522, Cache-Control no-store
    Web-->>CO: Value shown, masked again after 5 min, never stored in the browser
  end
```

*Figure 7. Masked-by-default PHI with audited reveal. Supports FR-CLI-06, FR-RPT-03, BR-005, BR-011, BR-057, NFR-PRIV-01 and NFR-PRIV-02.*

## Related documents

- [Process flows](process-flows.md)
- [State machines](state-machines.md)
- [Data flow diagram](data-flow-diagram.md)
- [System context and containers](../architecture/system-context-and-containers.md)
- [ADR-002 Append-only EVV punch ledger](../architecture/adr/ADR-002-append-only-evv-punch-ledger.md)
- [ADR-003 Single-flight scheduled jobs](../architecture/adr/ADR-003-single-flight-scheduled-jobs.md)
- [ADR-004 Identity verification vendor adapter](../architecture/adr/ADR-004-identity-verification-vendor-adapter.md)
- [ADR-006 Offline-first caregiver app](../architecture/adr/ADR-006-offline-first-caregiver-app.md)
- [Events and webhooks](../../04-api/events-and-webhooks.md)
- [API guidelines](../../04-api/api-guidelines.md)
