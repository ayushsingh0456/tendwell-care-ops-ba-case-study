# Tendwell Data Dictionary

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DSN-DATA-02 |
| Version | 1.3 |
| Status | Baselined (aligned to SRS v1.3) |
| Owner | Business Analyst |
| Last updated | 2026-09-24 |
| Reviewers | Engineering Lead (approver), Backend Developers, Compliance and Privacy Officer, Clinical SME (RN advisor), QA Lead |

## 1. Purpose and scope

This dictionary defines every Release 1 table in the Tendwell PostgreSQL 16 database:
- its purpose, owning module and expected row volume;
- each column's type, nullability, key or constraint, data classification, description and a fictional example.

It also lists the enumerations and the index and constraint highlights that the business rules depend on.

The entity relationships are drawn in the [ERD](erd.md). Handling, encryption and retention rules for each classification are in [data classification and retention](data-classification-and-retention.md). API field names are the camelCase form of these snake_case columns, for example `amount_cents` becomes `amountCents` (see the [OpenAPI specification](../../04-api/openapi.yaml)).

## 2. Conventions

| Item | Convention |
|---|---|
| Names | snake_case, plural table names, singular column names. Foreign keys are `<entity>_id`. Encrypted columns end in `_enc` where the SRS names them that way. |
| Types | PostgreSQL types. `uuid` keys; `timestamptz` instants stored in UTC; `date` for business dates in tenant time; `bigint` cents for money; `text` plus a `CHECK` constraint for enumerations, so values can be added in backward-compatible migrations (NFR-MNT-02). |
| Null | `N` = `NOT NULL`, `Y` = nullable. |
| Key / constraint | `PK`, `FK -> table`, `UK` (unique), `CHECK`, `ENC` (field-level envelope encryption, ciphertext stored as `bytea`), `BIDX` (keyed HMAC blind index). |
| Class | `PHI`, `PII`, `Confidential` or `Internal`, as defined in [data classification and retention](data-classification-and-retention.md#2-classification-scheme). A whole row of a client-linked table is PHI when joined to the client. The column class decides masking, encryption and logging. |
| Volume | Estimated for TEN-001 Harborview Home Care: 180 clients, 62 caregivers, about 15 office users, 2 locations, about 900 visits per week, about 60 clients with eMAR orders, bi-weekly pay periods. |
| Design addition | Marked **(added)**. These are columns or tables not in the SRS core entity list; the reason for each is in [ERD section 7.10](erd.md#710-additions-to-the-srs-entity-list). |

### 2.1 Canonical example identifiers

The examples below and in the OpenAPI specification reuse these fictional values.

| Record | Business key | UUID |
|---|---|---|
| Tenant | TEN-001 Harborview Home Care | `7c1e4a52-3b9d-4f0e-9a61-2d8f5b3c1a01` |
| Location | Lakemont Main Office | `1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c01` |
| Client | C-10234 | `5b2e8f14-6c3a-4d9b-a7e2-c10234000001` |
| Caregiver | E-2041 Maya Ortiz | `9d4f1a37-2b6c-4e8a-b5d3-e20410000001` |
| Service authorization | T1019, $7.25 per 15-minute unit | `6e1d9c42-5a7b-4f3e-8c2d-a01019000001` |
| Payer | Lakemont County Medicaid | `2c7a9e51-4b3d-4e6f-8a1c-9d0e1f2a3b01` |
| Visit | C-10234 with E-2041, 2026-09-08 09:00-11:00 | `a1f3c5e7-0b2d-4c6e-8f1a-20260908a001` |
| Pay period | Weekly, 2026-09-07 to 2026-09-13 | `8f3a1c5e-7b9d-4e2f-a6c8-202609070001` |
| Invoice | INV-2026-000123 | `b4e2d6f8-1a3c-4e5b-9d7f-000000000123` |

## 3. Common columns

Every table has the columns below in addition to those listed per entity, unless the entity says otherwise. Append-only tables have no `updated_at`, `updated_by` or `row_version`.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| tenant_id | uuid | N | FK -> tenants; RLS policy column | Internal | Owning tenant. Present on every tenant-scoped table, including child tables (BR-001). Shown again in each entity table only where it forms part of a key or is nullable. | `7c1e4a52-3b9d-4f0e-9a61-2d8f5b3c1a01` |
| created_at | timestamptz | N | default `now()` | Internal | Row creation instant, in UTC. | `2026-09-08T12:56:10Z` |
| created_by | uuid | Y | FK -> users | Internal | Acting user; `NULL` for `SYS` jobs. | `3d9b6c3a-5b2e-4f14-a7e2-c0000000a001` |
| updated_at | timestamptz | N | default `now()` | Internal | Last change instant, in UTC. | `2026-09-08T15:04:22Z` |
| updated_by | uuid | Y | FK -> users | Internal | Last acting user. | `3d9b6c3a-5b2e-4f14-a7e2-c0000000a001` |
| row_version | integer | N | default 1, incremented on update | Internal | Optimistic concurrency token, exposed as the API `ETag`. | `4` |
| deleted_at | timestamptz | Y | configuration tables only | Internal | Soft delete marker for `credential_types`, `reason_codes` and `escalation_ladders`. | `NULL` |

## 4. Entity index

| # | Entity | Domain | Owner module | Rows (TEN-001) | Highest class |
|---|---|---|---|---|---|
| 1 | tenants | A | ONB | 1 | Confidential |
| 2 | tenant_settings **(added)** | A | ONB | 1 | Confidential |
| 3 | plans | A | ONB (platform) | 4 platform-wide | Confidential |
| 4 | promo_codes | A | ONB (platform) | about 30 platform-wide | Confidential |
| 5 | subscriptions | A | ONB | 1 current, plus history | Confidential |
| 6 | users | A | IAM | about 80 active, 110 after one year | PII |
| 7 | roles | A | IAM | 8 | Internal |
| 8 | permissions | A | IAM (platform) | about 95 platform-wide | Internal |
| 9 | role_permissions | A | IAM | about 420 | Internal |
| 10 | user_roles | A | IAM | about 90 | Internal |
| 11 | user_permission_overrides | A | IAM | about 15 | Internal |
| 12 | user_locations | A | IAM | about 95 | Internal |
| 13 | support_access_grants | A | IAM | about 10 per year | Confidential |
| 14 | sign_in_events | A | IAM | about 45,000 per year | PII |
| 15 | locations | A | ONB | 2 | Internal |
| 16 | service_lines | A | ONB | 1 | Internal |
| 17 | clients | B | CLI | 180 active, plus about 70 discharged per year | PHI |
| 18 | client_diagnoses | B | CLI | about 540 | PHI |
| 19 | client_contacts | B | CLI | about 400 | PHI |
| 20 | client_caregiver_prefs | B | CLI | about 150 | PHI |
| 21 | payers | B | CLI | 6 | Confidential |
| 22 | service_authorizations | B | CLI | about 400 per year | PHI |
| 23 | care_plans | B | CLI | about 400 versions per year | PHI |
| 24 | care_plan_tasks | B | CLI | about 3,200 per year | PHI |
| 25 | caregivers | C | WRK | 62 active, about 90 after one year | PII |
| 26 | credential_types | C | WRK | 8 | Internal |
| 27 | caregiver_credentials | C | WRK | about 450 per year | PII |
| 28 | pay_profiles | C | WRK | about 120 | Confidential |
| 29 | visit_patterns | C | SCH | about 380 active | PHI |
| 30 | visits | C | SCH | about 46,800 per year | PHI |
| 31 | evv_punches | C | EVV | about 98,000 per year | PHI |
| 32 | identity_checks | C | EVV | about 100,000 per year when enabled | PII |
| 33 | visit_exceptions | C | EVV | about 3,500 per year | PHI |
| 34 | visit_task_results | C | EVV | about 330,000 per year | PHI |
| 35 | medication_orders | C | MAR | about 500 per year | PHI |
| 36 | dose_tasks | C | MAR | about 100,000 per year | PHI |
| 37 | prn_administrations | C | MAR | about 1,200 per year | PHI |
| 38 | vital_readings | C | MAR | about 25,000 per year | PHI |
| 39 | vital_ranges | C | MAR | about 250 | PHI |
| 40 | visit_notes | C | DOC | about 33,000 per year | PHI |
| 41 | note_addenda | C | DOC | about 400 per year | PHI |
| 42 | client_incidents | C | DOC | about 50 per year | PHI |
| 43 | incident_actions | C | DOC | about 100 per year | PHI |
| 44 | time_off_requests | D | TOF | about 400 per year | PII |
| 45 | leave_balances | D | TOF | about 250 | PII |
| 46 | holidays | D | TOF | about 10 per year | Internal |
| 47 | pay_periods | D | PAY | 52 per year | Internal |
| 48 | payroll_lines | D | PAY | about 60,000 per year | Confidential |
| 49 | payroll_exports | D | PAY | about 55 per year | Confidential |
| 50 | billing_runs | D | BIL | about 14 per year | Internal |
| 51 | invoices | D | BIL | about 2,400 per year | PHI |
| 52 | invoice_lines | D | BIL | about 47,000 per year | PHI |
| 53 | credit_notes | D | BIL | about 40 per year | PHI |
| 54 | payments | D | BIL | about 450 per year | Confidential |
| 55 | claim_batches | D | BIL | about 48 per year | Confidential |
| 56 | notifications | D | NTF | about 300,000 per year | Internal |
| 57 | notification_preferences | D | NTF | about 1,200 | Internal |
| 58 | escalation_ladders | D | NTF | about 12 | Internal |
| 59 | audit_events | D | RPT | about 1.5 million per year | PHI |
| 60 | job_executions | D | Platform | about 4,000 per tenant per year | Internal |
| 61 | documents **(added)** | Support | WRK, DOC | about 1,500 per year | PHI |
| 62 | reason_codes **(added)** | Support | EVV, SCH | about 60 | Internal |
| 63 | event_outbox **(added)** | Support | Platform | about 35,000 at any time (30-day purge) | PHI |

## 5. Entities

### 5.A Tenancy, subscription and access

#### tenants
- **Purpose:** One row per agency (tenant). This is the root of tenant isolation and holds the tenant lifecycle state (FR-ONB-01, FR-ONB-07).
- **Owner module:** ONB
- **Volume:** 1 row for TEN-001. Up to 500 platform-wide (NFR-SCL-01).
- **Notes:** This table has no `tenant_id` column. Its RLS policy is `id = current_setting('app.tenant_id')`.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Tenant identifier. | `7c1e4a52-3b9d-4f0e-9a61-2d8f5b3c1a01` |
| code **(added)** | text | N | UK | Internal | Human-readable tenant code. | `TEN-001` |
| legal_name | text | N | | Internal | Agency legal name from sign-up. | `Harborview Home Care LLC` |
| ein_enc | bytea | N | ENC | Confidential | Employer Identification Number. Shown masked as `**-***4821`. | ciphertext |
| registered_address **(added)** | jsonb | N | | Confidential | Registered business address (FR-ONB-01). | `{"line1":"200 Harbor Point Dr","city":"Lakemont","state":"OH","postalCode":"43999"}` |
| time_zone | text | N | CHECK valid IANA zone | Internal | Default time zone for display and business dates. | `America/New_York` |
| state_code | char(2) | N | CHECK US state or DC | Internal | State of operation. Drives the default retention and incident deadlines. | `OH` |
| status | text | N | CHECK `tenant_status` | Internal | Lifecycle: `Pending` until email verified, then `Trial`, `Active`, `ReadOnly` or `Cancelled` (BR-003). | `Active` |

#### tenant_settings (added)
- **Purpose:** Holds the tenant configuration provisioned at activation (FR-ONB-04), including the CR-001 daily overtime profile and the CR-002 open-shift claim confirmation flag.
- **Owner module:** ONB
- **Volume:** 1 row per tenant.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| tenant_id | uuid | N | PK, FK -> tenants | Internal | Owning tenant. | `7c1e4a52-…-2d8f5b3c1a01` |
| settings | jsonb | N | JSON Schema validated by the API | Confidential | Configuration document. Defaults come from the SRS configuration defaults table. | `{"geofenceRadiusM":150,"gpsAccuracyThresholdM":100,"identityVerification":true,"dailyOvertimeProfile":false,"openShiftClaimConfirmation":true,"mileageRateCents":70,"ptoAccrual":{"perHoursWorked":30,"capHours":80},"quietHours":{"start":"21:00","end":"07:00"},"clientRetentionYears":7}` |

#### plans
- **Purpose:** Subscription plans that Tendwell Labs sells (FR-ONB-08).
- **Owner module:** ONB (platform-managed by PLT-ADM)
- **Volume:** 4 rows platform-wide.
- **Notes:** This is a platform-global table with no `tenant_id`.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Plan identifier. | `0d1e2f3a-4b5c-4d6e-8f7a-9b0c1d2e3f01` |
| code | text | N | UK | Internal | Stable plan code. | `CARE-OPS-STD` |
| name | text | N | | Internal | Display name. | `Care Ops Standard` |
| price_per_seat_cents | bigint | N | CHECK >= 0 | Confidential | Monthly price per active client seat (BR-002). | `1200` |
| status | text | N | CHECK `plan_status` | Internal | `Active` or `Retired`. A retired plan stays on existing subscriptions. | `Active` |

#### promo_codes
- **Purpose:** Trial and discount codes validated at sign-up (FR-ONB-03, BR-004).
- **Owner module:** ONB (platform-managed)
- **Volume:** About 30 rows platform-wide.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Promo code identifier. | `5e6f7a8b-9c0d-4e1f-a2b3-c4d5e6f7a801` |
| code | citext | N | UK | Confidential | Code the customer types; matching is case-insensitive. | `LAKEMONT21` |
| kind | text | N | CHECK `promo_kind` | Internal | `Trial` or `Discount`. | `Trial` |
| discount_type | text | Y | CHECK `discount_type`; required when `kind = 'Discount'` | Internal | `Percent` or `Fixed`. | `NULL` |
| value | numeric(10,2) | Y | CHECK > 0 | Confidential | Percentage (0-100) or fixed amount in cents per seat. | `NULL` |
| trial_days | smallint | Y | required when `kind = 'Trial'` | Internal | Trial length in days (default 21). | `21` |
| max_redemptions | integer | Y | CHECK > 0 | Internal | Redemption cap; `NULL` means unlimited. | `50` |
| redemptions | integer | N | CHECK `redemptions <= max_redemptions` | Internal | Redemptions so far, incremented atomically. | `17` |
| expires_at | timestamptz | N | | Internal | Code expiry. | `2026-12-31T23:59:59Z` |
| eligible_plan_ids | uuid[] | Y | | Internal | Plans the code applies to; `NULL` means all plans. | `{0d1e2f3a-…-9b0c1d2e3f01}` |
| status | text | N | CHECK `promo_status` | Internal | `Active` or `Retired`. `Expired` is derived from `expires_at` and is not stored. | `Active` |

#### subscriptions
- **Purpose:** A tenant's subscription to a plan, synchronized with the payment provider (FR-ONB-06, FR-ONB-07).
- **Owner module:** ONB
- **Volume:** 1 current row per tenant, plus history.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Subscription identifier. | `c3d4e5f6-a7b8-4c9d-8e0f-1a2b3c4d5e01` |
| tenant_id | uuid | N | FK -> tenants; partial UK where `status <> 'Cancelled'` | Internal | Owning tenant. | `7c1e4a52-…-2d8f5b3c1a01` |
| plan_id | uuid | N | FK -> plans | Internal | Subscribed plan. | `0d1e2f3a-…-9b0c1d2e3f01` |
| promo_code_id | uuid | Y | FK -> promo_codes | Internal | Redeemed code; at most one per subscription (BR-004). | `5e6f7a8b-…-c4d5e6f7a801` |
| seats | integer | N | CHECK >= 1 | Confidential | Billed client seats for the current cycle. | `180` |
| status | text | N | CHECK `subscription_status` | Internal | `Trialing`, `Active`, `PastDue`, `ReadOnly` or `Cancelled`. | `Active` |
| trial_ends_at | timestamptz | Y | | Internal | End of trial (21 days by default). | `2026-07-27T03:59:59Z` |
| current_period_start | timestamptz | Y | | Internal | Start of the current billing cycle. | `2026-09-01T04:00:00Z` |
| current_period_end | timestamptz | Y | | Internal | End of the current billing cycle. | `2026-10-01T03:59:59Z` |
| provider_ref | text | Y | UK | Confidential | Payment provider subscription ID. | `sub_1PzT9wLakemont01` |

#### users
- **Purpose:** Every person who signs in: agency staff, caregivers and platform staff (FR-IAM-01).
- **Owner module:** IAM
- **Volume:** About 80 active users (62 caregivers, about 15 office staff). About 110 after one year of turnover.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | User identifier, also the JWT `sub`. | `4e8a9d4f-1a37-4b6c-95d3-a20410000001` |
| tenant_id | uuid | Y | FK -> tenants | Internal | Tenant; `NULL` for `PLT-ADM` and `PLT-SUP`. | `7c1e4a52-…-2d8f5b3c1a01` |
| email | citext | N | UK (platform-wide) | PII | Sign-in email. | `maya.ortiz@example.com` |
| phone | text | Y | CHECK E.164 | PII | Mobile number for the SMS second factor and SMS notifications. | `+1-614-555-0158` |
| first_name | text | N | | PII | Given name. | `Maya` |
| last_name | text | N | | PII | Family name. | `Ortiz` |
| status | text | N | CHECK `user_status` | Internal | `Invited`, `Active`, `Locked` or `Deactivated`. | `Active` |
| mfa_enabled | boolean | N | default false | Internal | A second factor is enrolled. Mandatory for the roles in BR-006. | `false` |
| last_login_at | timestamptz | Y | | PII | Last successful sign-in. | `2026-09-08T12:41:03Z` |

#### roles
- **Purpose:** Named permission bundles. Tenant roles are copied from platform role templates at provisioning (FR-ONB-04, FR-IAM-05).
- **Owner module:** IAM
- **Volume:** 8 rows (7 templates and 1 custom role).

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Role identifier. | `e1f2a3b4-c5d6-4e7f-8a9b-0c1d2e3f4a05` |
| tenant_id | uuid | Y | FK -> tenants; UK (`tenant_id`, `code`) | Internal | `NULL` for platform roles and master templates. | `7c1e4a52-…-2d8f5b3c1a01` |
| code | text | N | | Internal | Role code from the role catalog. | `AG-COORD` |
| name | text | N | | Internal | Display name. | `Care Coordinator` |
| is_template | boolean | N | | Internal | `true` for provisioned default templates; `false` for custom roles. | `true` |

#### permissions
- **Purpose:** Catalog of permission strings in `resource:action` form (FR-IAM-05).
- **Owner module:** IAM (platform-global, no `tenant_id`)
- **Volume:** About 95 rows.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| code | text | N | PK; CHECK `^[a-z_]+:[a-z_]+$` | Internal | Permission string. | `clients:reveal_phi` |
| module | text | N | | Internal | Owning module code. | `CLI` |
| description | text | N | | Internal | What the permission allows. | `Reveal masked PHI fields with a reason` |

#### role_permissions
- **Purpose:** Joins roles to permissions.
- **Owner module:** IAM
- **Volume:** About 420 rows.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| role_id | uuid | N | PK, FK -> roles | Internal | Role. | `e1f2a3b4-…-0c1d2e3f4a05` |
| permission_code | text | N | PK, FK -> permissions | Internal | Permission granted by the role. | `visits:create` |

#### user_roles
- **Purpose:** Assigns roles to users (FR-IAM-05).
- **Owner module:** IAM
- **Volume:** About 90 rows.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| user_id | uuid | N | PK, FK -> users | Internal | User. | `3d9b6c3a-…-c0000000a001` |
| role_id | uuid | N | PK, FK -> roles | Internal | Assigned role. | `e1f2a3b4-…-0c1d2e3f4a05` |

#### user_permission_overrides
- **Purpose:** Per-user grant or deny of a single permission. A deny always wins (BR-005).
- **Owner module:** IAM
- **Volume:** About 15 rows.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| user_id | uuid | N | PK, FK -> users | Internal | User. | `3d9b6c3a-…-c0000000a001` |
| permission_code | text | N | PK, FK -> permissions | Internal | Permission overridden. | `invoices:approve` |
| effect | text | N | CHECK `override_effect` | Internal | `Grant` or `Deny`. | `Deny` |

#### user_locations
- **Purpose:** Location scoping for users (FR-IAM-06).
- **Owner module:** IAM
- **Volume:** About 95 rows.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| user_id | uuid | N | PK, FK -> users | Internal | User. | `3d9b6c3a-…-c0000000a001` |
| location_id | uuid | N | PK, FK -> locations | Internal | Location the user may access. | `1a2b3c4d-…-0e1f2a3b4c01` |

#### support_access_grants
- **Purpose:** Time-boxed, agency-approved access for Platform Support Agents (FR-IAM-07, BR-008).
- **Owner module:** IAM
- **Volume:** About 10 rows per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Grant identifier, stamped on audit events. | `f0e1d2c3-b4a5-4968-8776-655443322101` |
| requested_by | uuid | N | FK -> users (platform user) | Internal | Requesting `PLT-SUP` user. | `aa11bb22-cc33-4d44-8e55-ff6600770001` |
| approved_by | uuid | Y | FK -> users | Internal | Approving `AG-ADM` user. | `b7c8d9e0-f1a2-4b3c-8d4e-5f6a7b8c9d01` |
| scope | text | N | CHECK `support_grant_scope`; default `ReadOnly` | Internal | `ReadOnly` or `ReadWrite`. | `ReadOnly` |
| reason | text | N | length 10-500 | Confidential | Ticket reference and purpose. | `Ticket 4471: payroll export column mapping error` |
| starts_at | timestamptz | Y | | Internal | Set on approval. | `2026-09-15T14:00:00Z` |
| expires_at | timestamptz | Y | CHECK `expires_at <= starts_at + interval '4 hours'` | Internal | Hard expiry. | `2026-09-15T16:00:00Z` |
| revoked_at | timestamptz | Y | | Internal | Early revocation instant. | `NULL` |
| status | text | N | CHECK `support_grant_status` | Internal | `Requested`, `Active`, `Expired`, `Revoked` or `Declined`. | `Active` |

#### sign_in_events
- **Purpose:** Records every sign-in attempt with its outcome (FR-IAM-08) and feeds lockout (FR-IAM-03).
- **Owner module:** IAM
- **Volume:** About 45,000 rows per year.
- **Notes:** Append-only.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Event identifier. | `0a9b8c7d-6e5f-4a3b-9c1d-0e9f8a7b6c01` |
| tenant_id | uuid | Y | FK -> tenants | Internal | Resolved tenant, if any. | `7c1e4a52-…-2d8f5b3c1a01` |
| user_id | uuid | Y | FK -> users | Internal | Matched user; `NULL` when the email is unknown. | `4e8a9d4f-…-a20410000001` |
| email_attempted | citext | N | indexed | PII | Email as typed. Lockout counts by this value, so unknown emails lock too. | `maya.ortiz@example.com` |
| outcome | text | N | CHECK `sign_in_outcome` | Internal | `Success`, `BadPassword`, `MfaFailed` or `Locked`. | `Success` |
| ip | inet | N | | PII | Client IP address. | `198.51.100.24` |
| device | text | Y | | PII | User agent or device model and app version. | `Tendwell Caregiver 1.6.2 (Android 14)` |
| occurred_at | timestamptz | N | | Internal | Attempt instant. | `2026-09-08T12:41:03Z` |

#### locations
- **Purpose:** Agency branches or homes. These are the unit of location scoping and can override the tenant time zone.
- **Owner module:** ONB
- **Volume:** 2 rows.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Location identifier. | `1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c01` |
| name | text | N | UK (`tenant_id`, `name`) | Internal | Display name. | `Lakemont Main Office` |
| address | jsonb | N | | Internal | Business address. | `{"line1":"200 Harbor Point Dr","city":"Lakemont","state":"OH","postalCode":"43999"}` |
| time_zone | text | N | CHECK valid IANA zone | Internal | Location time zone. | `America/New_York` |

#### service_lines
- **Purpose:** Service lines the tenant offers (FR-ONB-01).
- **Owner module:** ONB
- **Volume:** 1 row for TEN-001. TEN-003 has 2.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Service line identifier. | `7d8e9f0a-1b2c-4d3e-8f4a-5b6c7d8e9f01` |
| code | text | N | CHECK `service_line_code`; UK (`tenant_id`, `code`) | Internal | `HOME_VISIT`, `ADULT_DAY` or `SUPPORTED_LIVING`. | `HOME_VISIT` |

### 5.B Clients, authorizations and care plans

#### clients
- **Purpose:** The person receiving care. Holds demographics, the geocoded service address and the geofence (FR-CLI-01).
- **Owner module:** CLI
- **Volume:** 180 active rows, plus about 70 discharged per year, retained for 7 years after discharge (BR-013).

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Client identifier. | `5b2e8f14-6c3a-4d9b-a7e2-c10234000001` |
| location_id | uuid | N | FK -> locations | Internal | Managing location (scoping). | `1a2b3c4d-…-0e1f2a3b4c01` |
| client_number | text | N | UK (`tenant_id`, `client_number`) | PHI | Agency-assigned client number (a record number). | `C-10234` |
| first_name | text | N | | PHI | Given name. | `Evelyn` |
| last_name | text | N | | PHI | Family name. | `Marsh` |
| dob_enc | bytea | N | ENC | PHI | Date of birth. Masked by default (BR-011). | ciphertext of `1946-03-14` |
| dob_bidx **(added)** | bytea | N | BIDX, indexed | PHI | Blind index for the duplicate check (FR-CLI-02). | HMAC bytes |
| gender | text | Y | | PHI | Gender as recorded. | `Female` |
| primary_language | text | N | ISO 639-1 | PHI | Primary language. | `en` |
| phone_enc | bytea | Y | ENC | PHI | Client phone. Masked by default. | ciphertext of `+1-614-555-0137` |
| service_address_enc | bytea | N | ENC | PHI | Service address. Masked by default. | ciphertext of `418 Juniper Hollow Rd, Lakemont, OH 43999` |
| lat | numeric(9,6) | Y | CHECK -90..90 | PHI | Geocoded latitude. Kept plaintext for server-side distance computation and never returned by the API. | `39.961842` |
| lng | numeric(9,6) | Y | CHECK -180..180 | PHI | Geocoded longitude. | `-82.998734` |
| geofence_radius_m | smallint | N | CHECK 50-500; default 150 | Internal | Geofence radius (BR-021). | `150` |
| medicaid_id_enc | bytea | Y | ENC | PHI | Medicaid ID. Masked by default. | ciphertext of `ZZ40218837` |
| medicaid_id_bidx **(added)** | bytea | Y | BIDX, indexed | PHI | Blind index for the duplicate check. | HMAC bytes |
| allergies | text[] | N | default `{}` | PHI | Allergies, shown to the assigned caregiver for safety. | `{Penicillin,Latex}` |
| status | text | N | CHECK `client_status` | Internal | `Active`, `OnHold` or `Discharged`. | `Active` |
| admitted_on | date | N | | PHI | Admission date. | `2025-11-03` |
| discharged_on | date | Y | CHECK `>= admitted_on` | PHI | Discharge date (FR-CLI-07). | `NULL` |
| discharge_reason | text | Y | required when `Discharged` | PHI | Discharge reason. | `NULL` |

#### client_diagnoses
- **Purpose:** ICD-10-CM diagnoses per client (FR-CLI-01).
- **Owner module:** CLI
- **Volume:** About 540 rows.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id **(added)** | uuid | N | PK | Internal | Surrogate key; ciphertext cannot be part of a key. | `0b1c2d3e-4f5a-4b6c-8d7e-9f0a1b2c3d01` |
| client_id | uuid | N | FK -> clients | Internal | Client. | `5b2e8f14-…-c10234000001` |
| icd10_code | bytea | N | ENC | PHI | ICD-10-CM code (BR-011). | ciphertext of `I10` |
| icd10_code_bidx **(added)** | bytea | N | BIDX; UK (`client_id`, `icd10_code_bidx`) | PHI | Uniqueness per client. | HMAC bytes |
| description | bytea | N | ENC | PHI | Diagnosis description. | ciphertext of `Essential (primary) hypertension` |
| is_primary | boolean | N | partial UK (`client_id`) where true | PHI | Primary diagnosis flag. | `true` |

#### client_contacts
- **Purpose:** Family, emergency and legal-representative contacts (FR-CLI-01).
- **Owner module:** CLI
- **Volume:** About 400 rows.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Contact identifier. | `1c2d3e4f-5a6b-4c7d-8e9f-0a1b2c3d4e01` |
| client_id | uuid | N | FK -> clients | Internal | Client. | `5b2e8f14-…-c10234000001` |
| name | text | N | | PHI | Contact name (a relative's identifier is PHI of the client). | `Daniel Marsh` |
| relationship | text | N | | PHI | Relationship to the client. | `Son` |
| phone | text | Y | CHECK E.164 | PHI | Contact phone. | `+1-614-555-0119` |
| email | citext | Y | | PHI | Contact email. | `daniel.marsh@example.org` |
| is_emergency | boolean | N | | Internal | Emergency contact flag. | `true` |
| is_legal_rep | boolean | N | | Internal | Authorized representative flag (future Family Portal, Release 2). | `true` |

#### client_caregiver_prefs
- **Purpose:** Client preferences for, and exclusions of, specific caregivers (FR-CLI-08, BR-017).
- **Owner module:** CLI
- **Volume:** About 150 rows.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| client_id | uuid | N | PK, FK -> clients | Internal | Client. | `5b2e8f14-…-c10234000001` |
| caregiver_id | uuid | N | PK, FK -> caregivers | Internal | Caregiver. | `9d4f1a37-…-e20410000001` |
| kind | text | N | CHECK `pref_kind` | Internal | `Preferred` (sorting only) or `Excluded` (hard block). | `Preferred` |
| reason | text | Y | required when `Excluded` | PHI | Reason given by the client or family. | `Client prefers a Spanish-speaking caregiver` |

#### payers
- **Purpose:** Organizations or people responsible for payment.
- **Owner module:** CLI
- **Volume:** 6 rows.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Payer identifier. | `2c7a9e51-4b3d-4e6f-8a1c-9d0e1f2a3b01` |
| name | text | N | UK (`tenant_id`, `name`) | Confidential | Payer name. | `Lakemont County Medicaid` |
| payer_type | text | N | CHECK `payer_type` | Internal | `Medicaid`, `ManagedCare`, `LTCInsurance`, `PrivatePay` or `VA`. | `Medicaid` |

#### service_authorizations
- **Purpose:** Payer authorizations that permit and cap services (FR-CLI-03, FR-CLI-04, BR-009, BR-010).
- **Owner module:** CLI
- **Volume:** About 400 rows per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Authorization identifier. | `6e1d9c42-5a7b-4f3e-8c2d-a01019000001` |
| client_id | uuid | N | FK -> clients | Internal | Client. | `5b2e8f14-…-c10234000001` |
| payer_id | uuid | N | FK -> payers | Internal | Authorizing payer. | `2c7a9e51-…-9d0e1f2a3b01` |
| service_line_id | uuid | N | FK -> service_lines | Internal | Covered service line. | `7d8e9f0a-…-5b6c7d8e9f01` |
| auth_number | text | N | | PHI | Payer authorization number. | `PA-2026-55810` |
| service_code | text | N | | PHI | HCPCS or agency service code. | `T1019` |
| billing_model | text | N | CHECK `billing_model` | Internal | `Hourly`, `PerVisit`, `Daily` or `FixedMonthly`. | `Hourly` |
| unit_type | text | N | CHECK `unit_type`; consistent with `billing_model` | Internal | `Unit15Min`, `Visit`, `Day` or `Month`. | `Unit15Min` |
| rate_cents | bigint | N | CHECK >= 0 | Confidential | Rate per unit. | `725` |
| units_authorized | numeric(10,2) | N | CHECK > 0 | PHI | Authorized units for the period. | `480.00` |
| period_start | date | N | | PHI | First authorized date. | `2026-07-01` |
| period_end | date | N | CHECK `>= period_start`; exclusion constraint on active overlaps | PHI | Last authorized date. | `2026-12-31` |
| status | text | N | CHECK `authorization_status` | Internal | `Active`, `Expired` or `Suspended`. | `Active` |

Remaining units are not stored. They are computed as `units_authorized` minus units on scheduled visits minus units on delivered visits (BR-010) and served by the API as `unitsRemaining`.

#### care_plans
- **Purpose:** Versioned care plans. A version becomes `Active` only after Clinical Supervisor approval (FR-CLI-05, BR-012).
- **Owner module:** CLI
- **Volume:** About 400 versions per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Care plan version identifier. | `2d3e4f5a-6b7c-4d8e-9f0a-1b2c3d4e5f01` |
| client_id | uuid | N | FK -> clients; partial UK where `status = 'Active'` | Internal | Client. | `5b2e8f14-…-c10234000001` |
| version | integer | N | UK (`client_id`, `version`) | Internal | Sequential version number. | `3` |
| status | text | N | CHECK `care_plan_status` | Internal | `Draft`, `PendingApproval`, `Active` or `Superseded`. | `Active` |
| requires_visit_note | boolean | N | default false | Internal | Clock-out requires a note (FR-EVV-06). | `true` |
| approved_by | uuid | Y | FK -> users (`AG-SUPV`) | Internal | Approving Clinical Supervisor. | `c8d9e0f1-a2b3-4c4d-8e5f-6a7b8c9d0e01` |
| approved_at | timestamptz | Y | required when `Active` or `Superseded` | Internal | Approval instant. | `2026-08-28T18:20:00Z` |

#### care_plan_tasks
- **Purpose:** ADL, IADL and clinical tasks within a care plan version.
- **Owner module:** CLI
- **Volume:** About 3,200 rows per year (about 8 per version).

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Task identifier. | `3e4f5a6b-7c8d-4e9f-8a0b-1c2d3e4f5a01` |
| care_plan_id | uuid | N | FK -> care_plans | Internal | Care plan version. | `2d3e4f5a-…-1b2c3d4e5f01` |
| category | text | N | CHECK `task_category` | Internal | `ADL`, `IADL` or `Clinical`. | `ADL` |
| name | text | N | | PHI | Task name. | `Assist with shower` |
| instructions | text | Y | | PHI | Instructions for the caregiver. | `Use shower chair; client needs standby assist for transfers` |

### 5.C Workforce, scheduling, EVV, eMAR and documentation

#### caregivers
- **Purpose:** Field staff profile, linked to a user account (FR-WRK-01).
- **Owner module:** WRK
- **Volume:** 62 active rows, about 90 after one year including inactive.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Caregiver identifier. | `9d4f1a37-2b6c-4e8a-b5d3-e20410000001` |
| user_id | uuid | N | FK -> users; UK | Internal | Sign-in account. | `4e8a9d4f-…-a20410000001` |
| employee_number | text | N | UK (`tenant_id`, `employee_number`) | PII | Payroll employee number. | `E-2041` |
| first_name | text | N | | PII | Given name. | `Maya` |
| last_name | text | N | | PII | Family name. | `Ortiz` |
| phone | text | N | CHECK E.164 | PII | Work mobile number. | `+1-614-555-0158` |
| email | citext | N | | PII | Work email. | `maya.ortiz@example.com` |
| hire_date | date | N | | PII | Hire date. | `2024-05-20` |
| employment_type | text | N | CHECK `employment_type` | PII | `FullTime`, `PartTime` or `PerDiem`. | `FullTime` |
| status | text | N | CHECK `caregiver_status` | Internal | `Active` or `Inactive` (FR-WRK-06). | `Active` |
| home_lat | numeric(9,6) | Y | | PII | Home location, used for open-shift distance and travel estimates. Never returned to other users. | `39.948211` |
| home_lng | numeric(9,6) | Y | | PII | Home longitude. | `-83.011540` |
| skills | text[] | N | default `{}` | PII | Skills used for matching. | `{Hoyer lift,Dementia care}` |
| languages | text[] | N | default `{en}` | PII | Languages (ISO 639-1). | `{en,es}` |
| identity_enrolled | boolean | N | default false | PII | A reference selfie is enrolled with the identity vendor (FR-EVV-04). | `true` |

#### credential_types
- **Purpose:** Tenant-defined credential types, each either Blocking or Advisory (FR-WRK-03).
- **Owner module:** WRK
- **Volume:** 8 rows.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Credential type identifier. | `4f5a6b7c-8d9e-4f0a-9b1c-2d3e4f5a6b01` |
| name | text | N | UK (`tenant_id`, `name`) | Internal | Name. | `CPR and First Aid` |
| is_blocking | boolean | N | | Internal | When true, an expired credential blocks scheduling (BR-014). | `true` |
| validity_months | smallint | Y | CHECK > 0 | Internal | Default validity, used to suggest an expiry date. | `24` |

#### caregiver_credentials
- **Purpose:** Credentials held by a caregiver. Status is recomputed daily (FR-WRK-02).
- **Owner module:** WRK
- **Volume:** About 450 rows per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Credential identifier. | `5a6b7c8d-9e0f-4a1b-8c2d-3e4f5a6b7c01` |
| caregiver_id | uuid | N | FK -> caregivers | Internal | Holder. | `9d4f1a37-…-e20410000001` |
| credential_type_id | uuid | N | FK -> credential_types | Internal | Type. | `4f5a6b7c-…-2d3e4f5a6b01` |
| issued_on | date | N | | PII | Issue date. | `2025-10-21` |
| expires_on | date | Y | CHECK `> issued_on` | PII | Expiry date; `NULL` means it does not expire. | `2027-10-21` |
| document_id | uuid | Y | FK -> documents | PII | Scanned certificate. | `6b7c8d9e-0f1a-4b2c-9d3e-4f5a6b7c8d01` |
| status | text | N | CHECK `credential_status` | Internal | `Valid`; `Expiring` when 30 days or fewer remain; `Expired` after the expiry date (BR-014). | `Valid` |

#### pay_profiles
- **Purpose:** Effective-dated pay terms per caregiver (FR-WRK-05, BR-015).
- **Owner module:** WRK
- **Volume:** About 120 rows.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Profile identifier. | `7c8d9e0f-1a2b-4c3d-8e4f-5a6b7c8d9e01` |
| caregiver_id | uuid | N | FK -> caregivers | Internal | Caregiver. | `9d4f1a37-…-e20410000001` |
| effective_from | date | N | UK (`caregiver_id`, `effective_from`) | Confidential | First date the profile applies. | `2026-01-01` |
| pay_type | text | N | CHECK `pay_type` | Confidential | `Hourly` or `Salaried`. | `Hourly` |
| base_rate_cents | bigint | N | CHECK > 0 | Confidential | Base hourly rate. | `1950` |
| ot_eligible | boolean | N | | Confidential | Non-exempt; overtime applies (BR-041). | `true` |
| holiday_eligible | boolean | N | | Confidential | Holiday multiplier applies (BR-042). | `true` |
| mileage_eligible | boolean | N | | Confidential | Mileage reimbursement applies (BR-044). | `true` |

#### visit_patterns
- **Purpose:** Recurring schedules that materialize visits for a rolling 8-week horizon (FR-SCH-01, BR-018).
- **Owner module:** SCH
- **Volume:** About 380 active rows.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Pattern identifier. | `8d9e0f1a-2b3c-4d4e-9f5a-6b7c8d9e0f01` |
| client_id | uuid | N | FK -> clients | Internal | Client. | `5b2e8f14-…-c10234000001` |
| caregiver_id | uuid | Y | FK -> caregivers | Internal | Default caregiver; `NULL` publishes open shifts. | `9d4f1a37-…-e20410000001` |
| service_authorization_id | uuid | N | FK -> service_authorizations | Internal | Authorization the visits use. | `6e1d9c42-…-a01019000001` |
| weekdays | smallint[] | N | CHECK values 1-7 (ISO, Monday = 1) | PHI | Days of the week. | `{2,4,6}` |
| start_time | time | N | | PHI | Local start time. | `09:00` |
| end_time | time | N | CHECK `<> start_time`; may cross midnight | PHI | Local end time. | `11:00` |
| starts_on | date | N | | PHI | First date. | `2026-09-01` |
| ends_on | date | Y | CHECK `>= starts_on` | PHI | Last date; `NULL` means open-ended. | `NULL` |

#### visits
- **Purpose:** A scheduled or delivered visit. This is the hub of EVV, payroll and billing.
- **Owner module:** SCH (status transitions after clock-in are owned by EVV)
- **Volume:** About 46,800 rows per year, about 330,000 at the 7-year retention. Partitioned monthly by `scheduled_start`.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Visit identifier. | `a1f3c5e7-0b2d-4c6e-8f1a-20260908a001` |
| pattern_id | uuid | Y | FK -> visit_patterns | Internal | Source pattern; `NULL` for one-off and unscheduled visits. | `8d9e0f1a-…-6b7c8d9e0f01` |
| client_id | uuid | N | FK -> clients | Internal | Client (EVV element: individual receiving the service). | `5b2e8f14-…-c10234000001` |
| caregiver_id | uuid | Y | FK -> caregivers; exclusion constraint on overlap | Internal | Caregiver (EVV element: individual providing the service). | `9d4f1a37-…-e20410000001` |
| service_authorization_id | uuid | Y | FK -> service_authorizations | Internal | Matching authorization (BR-009). | `6e1d9c42-…-a01019000001` |
| service_line_id | uuid | N | FK -> service_lines | Internal | Service line (EVV element: type of service, with the authorization's service code). | `7d8e9f0a-…-5b6c7d8e9f01` |
| scheduled_start | timestamptz | N | | PHI | Scheduled start. | `2026-09-08T13:00:00Z` |
| scheduled_end | timestamptz | N | CHECK `> scheduled_start` | PHI | Scheduled end. | `2026-09-08T15:00:00Z` |
| status | text | N | CHECK `visit_status` | Internal | Lifecycle (BR-019). | `Verified` |
| cancel_reason_code | text | Y | FK -> reason_codes; required when `Cancelled` | Internal | Cancellation reason (FR-SCH-04). | `NULL` |
| care_plan_version | integer | Y | set at clock-in | Internal | Care plan version active at clock-in (BR-012). | `3` |
| is_open_shift | boolean | N | default false | Internal | Published to the open-shift queue (FR-SCH-05). | `false` |

#### evv_punches
- **Purpose:** The append-only ledger of clock-in and clock-out events, including corrections (FR-EVV-02, BR-025, BR-026).
- **Owner module:** EVV
- **Volume:** About 98,000 rows per year. Partitioned monthly by `punch_time`.
- **Notes:** Append-only. Has no `updated_*` or `row_version` columns.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Client-generated `punchId`; the idempotency key for online retries and offline sync. | `e3a1c9f2-7b4d-4e8a-9c6f-1d2b3a4c5e01` |
| visit_id | uuid | N | FK -> visits | Internal | Visit. | `a1f3c5e7-…-20260908a001` |
| type | text | N | CHECK `punch_type` | Internal | `In` or `Out`. | `In` |
| source | text | N | CHECK `punch_source` | Internal | `Mobile`, `MobileOffline`, `Manual` or `System` (auto-close). | `Mobile` |
| punch_time | timestamptz | N | | PHI | Device capture time (EVV elements: date and begin or end time). | `2026-09-08T12:56:10Z` |
| received_at | timestamptz | N | default `now()` | Internal | Server receipt time. More than 24 hours after `punch_time` raises `LATE_OFFLINE_SYNC`. | `2026-09-08T12:56:11Z` |
| lat | numeric(9,6) | Y | `NULL` for `Manual` and `System` | PHI | Device latitude (EVV element: location). | `39.963650` |
| lng | numeric(9,6) | Y | | PHI | Device longitude. | `-82.997880` |
| accuracy_m | numeric(8,1) | Y | CHECK >= 0 | Internal | Reported horizontal accuracy. Worse than 100 m raises `LOW_GPS_ACCURACY` (BR-022). | `18.0` |
| distance_m | numeric(8,1) | Y | server-computed | PHI | Distance to the service address; the device cannot set it (BR-021). | `212.0` |
| device_id | text | Y | | PII | Registered device identifier. | `and-5f2c9e81b7a4` |
| identity_check_id | uuid | Y | FK -> identity_checks; UK where not null | Internal | Single-use identity check consumed by this punch (BR-024). | `f4b2d0a3-8c5e-4f9b-8d7a-2e3c4b5d6f01` |
| reason_code | text | Y | FK -> reason_codes; required when `Manual` | Internal | Correction reason. | `NULL` |
| note | text | Y | required when `Manual` | PHI | Correction note. | `NULL` |
| created_by | uuid | N | FK -> users | Internal | Caregiver for device punches; Coordinator for corrections; the system user for auto-close. | `4e8a9d4f-…-a20410000001` |
| supersedes_punch_id | uuid | Y | FK -> evv_punches | Internal | Punch this row corrects. | `NULL` |

#### identity_checks
- **Purpose:** Results of selfie liveness and face-match checks (FR-EVV-04, BR-024).
- **Owner module:** EVV
- **Volume:** About 100,000 rows per year where the tenant enables identity verification.
- **Notes:** Selfie images and face templates are not stored in Tendwell. The vendor adapter (ADR-004) receives the image, returns a result and deletes the image.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Check identifier. | `f4b2d0a3-8c5e-4f9b-8d7a-2e3c4b5d6f01` |
| caregiver_id | uuid | N | FK -> caregivers | Internal | Caregiver checked. | `9d4f1a37-…-e20410000001` |
| visit_id | uuid | N | FK -> visits | Internal | Visit the check is for. | `a1f3c5e7-…-20260908a001` |
| result | text | N | CHECK `identity_result` | PII | `Pass` or `Fail`. | `Pass` |
| match_score | numeric(5,4) | Y | CHECK 0-1 | PII | Vendor similarity score (biometric-derived). Not exposed to caregivers. | `0.9731` |
| liveness_passed | boolean | N | | PII | Liveness result. | `true` |
| expires_at | timestamptz | N | `created_at + 90 seconds` | Internal | End of validity. | `2026-09-08T12:57:32Z` |
| consumed_at | timestamptz | Y | set once | Internal | When a punch used the check. | `2026-09-08T12:56:10Z` |

#### visit_exceptions
- **Purpose:** EVV exceptions for Coordinator review (FR-EVV-07, FR-EVV-08).
- **Owner module:** EVV
- **Volume:** About 3,500 rows per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Exception identifier. | `0c1d2e3f-4a5b-4c6d-9e7f-8a9b0c1d2e01` |
| visit_id | uuid | N | FK -> visits; partial UK (`visit_id`, `code`) where `Open` | Internal | Visit. | `a1f3c5e7-…-20260908a001` |
| code | text | N | CHECK `exception_code` | Internal | Exception type. | `LOCATION_MISMATCH` |
| status | text | N | CHECK `exception_status` | Internal | `Open`, `Resolved` or `Waived`. | `Resolved` |
| resolution_reason_code | text | Y | FK -> reason_codes; required unless `Open` | Internal | Resolution reason. | `SERVICE_AT_ALTERNATE_LOCATION` |
| note | text | Y | required unless `Open` | PHI | Resolution note. | `Client was at daughter's home 200 m away; confirmed by phone.` |
| resolved_by | uuid | Y | FK -> users | Internal | Resolving Coordinator. | `3d9b6c3a-…-c0000000a001` |
| resolved_at | timestamptz | Y | | Internal | Resolution instant. | `2026-09-08T17:22:40Z` |

#### visit_task_results
- **Purpose:** Per-task outcome recorded at clock-out (FR-EVV-06).
- **Owner module:** EVV
- **Volume:** About 330,000 rows per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| visit_id | uuid | N | PK, FK -> visits | Internal | Visit. | `a1f3c5e7-…-20260908a001` |
| care_plan_task_id | uuid | N | PK, FK -> care_plan_tasks | Internal | Task from the stamped care plan version. | `3e4f5a6b-…-1c2d3e4f5a01` |
| status | text | N | CHECK `task_result_status` | PHI | `Done` or `NotDone`. | `NotDone` |
| reason | text | Y | CHECK required when `NotDone` | PHI | Why the task was not done. | `Client declined shower today` |

#### medication_orders
- **Purpose:** Medication orders. An order becomes `Active` only after Clinical Supervisor approval (FR-MAR-01).
- **Owner module:** MAR
- **Volume:** About 250 active rows, about 500 new per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Order identifier. | `1d2e3f4a-5b6c-4d7e-8f9a-0b1c2d3e4f01` |
| client_id | uuid | N | FK -> clients | Internal | Client. | `5b2e8f14-…-c10234000001` |
| drug_name | text | N | | PHI | Drug name. | `Lisinopril` |
| strength | text | N | | PHI | Strength. | `10 mg` |
| form | text | N | | PHI | Dosage form. | `Tablet` |
| dose | text | N | | PHI | Amount per administration. | `1 tablet` |
| route | text | N | | PHI | Route. | `By mouth` |
| schedule_times | time[] | Y | required unless PRN | PHI | Local administration times. | `{08:00}` |
| start_date | date | N | | PHI | First date. | `2026-08-29` |
| end_date | date | Y | CHECK `>= start_date` | PHI | Last date. | `NULL` |
| prescriber_name | text | N | | PII | Prescriber. | `Dr. Alan Brooks` |
| prescriber_npi | text | Y | CHECK 10 digits | PII | Prescriber NPI (fictional). | `1999999984` |
| instructions | text | Y | | PHI | Administration instructions. | `Hold if systolic BP below 100; notify supervisor` |
| is_prn | boolean | N | | PHI | As-needed order. | `false` |
| prn_indication | text | Y | required when PRN | PHI | Approved indication. | `NULL` |
| prn_max_per_24h | smallint | Y | required when PRN | PHI | Maximum doses in any rolling 24 hours (BR-033). | `NULL` |
| prn_min_interval_min | integer | Y | required when PRN | PHI | Minimum minutes between doses. | `NULL` |
| window_minutes | smallint | N | CHECK 15-120; default 60 | Internal | Plus or minus window (BR-029). | `60` |
| status | text | N | CHECK `medication_order_status` | Internal | `PendingApproval`, `Active` or `Discontinued`. | `Active` |
| approved_by | uuid | Y | FK -> users (`AG-SUPV`) | Internal | Approving Clinical Supervisor. | `c8d9e0f1-…-6a7b8c9d0e01` |

#### dose_tasks
- **Purpose:** Scheduled doses generated for a rolling 7-day window, with their outcomes and escalation status (FR-MAR-02 to FR-MAR-04).
- **Owner module:** MAR
- **Volume:** About 100,000 rows per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Dose task identifier. | `2e3f4a5b-6c7d-4e8f-9a0b-1c2d3e4f5a01` |
| order_id | uuid | N | FK -> medication_orders; UK (`order_id`, `scheduled_at`) | Internal | Order. | `1d2e3f4a-…-0b1c2d3e4f01` |
| client_id | uuid | N | FK -> clients (denormalized) | Internal | Client. | `5b2e8f14-…-c10234000001` |
| scheduled_at | timestamptz | N | | PHI | Scheduled time. | `2026-09-08T12:00:00Z` |
| window_start | timestamptz | N | | PHI | Window opens. | `2026-09-08T11:00:00Z` |
| window_end | timestamptz | N | | PHI | Window closes. | `2026-09-08T13:00:00Z` |
| status | text | N | CHECK `dose_status` | PHI | Outcome or escalation state. | `Given` |
| administered_at | timestamptz | Y | required for outcome statuses | PHI | Administration time. | `2026-09-08T12:58:00Z` |
| recorded_by | uuid | Y | FK -> users | Internal | Recorder. | `4e8a9d4f-…-a20410000001` |
| reason | text | Y | CHECK required for `Refused`, `Held`, `NotAvailable` | PHI | Reason (BR-032). | `NULL` |
| is_late_entry | boolean | N | default false | Internal | Recorded after the window but within 24 hours (BR-031). | `false` |

#### prn_administrations
- **Purpose:** As-needed (PRN) doses with their indication (FR-MAR-05).
- **Owner module:** MAR
- **Volume:** About 1,200 rows per year.
- **Notes:** Append-only.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Administration identifier. | `3f4a5b6c-7d8e-4f9a-8b0c-1d2e3f4a5b01` |
| order_id | uuid | N | FK -> medication_orders (PRN only) | Internal | PRN order. | `4a5b6c7d-8e9f-4a0b-9c1d-2e3f4a5b6c01` |
| administered_at | timestamptz | N | | PHI | Time given. | `2026-09-08T14:10:00Z` |
| indication | text | N | | PHI | Indication observed. | `Knee pain 6/10` |
| follow_up_note | text | Y | | PHI | Effect follow-up. | `Pain 3/10 after 45 minutes` |
| recorded_by | uuid | N | FK -> users | Internal | Recorder. | `4e8a9d4f-…-a20410000001` |

#### vital_readings
- **Purpose:** Vital sign readings with out-of-range evaluation (FR-MAR-07, FR-MAR-08).
- **Owner module:** MAR
- **Volume:** About 25,000 rows per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Reading identifier. | `5b6c7d8e-9f0a-4b1c-8d2e-3f4a5b6c7d01` |
| client_id | uuid | N | FK -> clients | Internal | Client. | `5b2e8f14-…-c10234000001` |
| visit_id | uuid | Y | FK -> visits | Internal | Visit, when taken during one. | `a1f3c5e7-…-20260908a001` |
| type | text | N | CHECK `vital_type` | PHI | Vital type. | `BP` |
| value_1 | numeric(7,2) | N | | PHI | Primary value (systolic for BP). | `186` |
| value_2 | numeric(7,2) | Y | required for `BP` | PHI | Secondary value (diastolic for BP). | `94` |
| unit | text | N | | Internal | Unit. | `mmHg` |
| method | text | Y | | PHI | Method or site. | `Automatic cuff, left arm, seated` |
| taken_at | timestamptz | N | | PHI | Time taken. | `2026-09-08T13:20:00Z` |
| recorded_by | uuid | N | FK -> users | Internal | Recorder. | `4e8a9d4f-…-a20410000001` |
| out_of_range | boolean | N | computed on insert | PHI | Outside the client's range or the BR-034 default. | `true` |

#### vital_ranges
- **Purpose:** Per-client alert ranges that override the BR-034 defaults (FR-MAR-08).
- **Owner module:** MAR
- **Volume:** About 250 rows.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| client_id | uuid | N | PK, FK -> clients | Internal | Client. | `5b2e8f14-…-c10234000001` |
| type | text | N | PK; CHECK `vital_type` | PHI | Vital type. | `BP` |
| low | numeric(7,2) | Y | | PHI | Lower limit for `value_1`. | `95` |
| high | numeric(7,2) | Y | CHECK `> low` | PHI | Upper limit for `value_1`. | `170` |
| low_2 **(added)** | numeric(7,2) | Y | `BP` only | PHI | Lower limit for diastolic. | `NULL` |
| high_2 **(added)** | numeric(7,2) | Y | `BP` only | PHI | Upper limit for diastolic. | `105` |
| set_by | uuid | N | FK -> users (`AG-SUPV`) | Internal | Clinical Supervisor who set the range. | `c8d9e0f1-…-6a7b8c9d0e01` |

#### visit_notes
- **Purpose:** The visit note, which locks 24 hours after clock-out (FR-DOC-01, FR-DOC-02).
- **Owner module:** DOC
- **Volume:** About 33,000 rows per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Note identifier. | `6c7d8e9f-0a1b-4c2d-9e3f-4a5b6c7d8e01` |
| visit_id | uuid | N | FK -> visits; UK | Internal | Visit. | `a1f3c5e7-…-20260908a001` |
| author_id | uuid | N | FK -> users | Internal | Author. | `4e8a9d4f-…-a20410000001` |
| structured | jsonb | N | JSON Schema validated by the API | PHI | Structured observations. | `{"mood":"Calm","appetite":"Fair","skinIntact":true}` |
| narrative | bytea | Y | ENC | PHI | Free-text narrative. | ciphertext |
| status | text | N | CHECK `note_status` | Internal | `Draft`, `Submitted` or `Locked`. | `Locked` |
| locked_at | timestamptz | Y | set at clock-out + 24 h | Internal | Lock instant (BR-035). | `2026-09-09T15:04:00Z` |

#### note_addenda
- **Purpose:** Signed addenda to a locked note (BR-035).
- **Owner module:** DOC
- **Volume:** About 400 rows per year.
- **Notes:** Append-only.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Addendum identifier. | `7d8e9f0a-1b2c-4d3e-8f4a-5b6c7d8e9f02` |
| note_id | uuid | N | FK -> visit_notes (`Locked` only) | Internal | Note. | `6c7d8e9f-…-4a5b6c7d8e01` |
| author_id | uuid | N | FK -> users | Internal | Signer. | `c8d9e0f1-…-6a7b8c9d0e01` |
| text | bytea | N | ENC | PHI | Addendum text. | ciphertext |
| signed_at | timestamptz | N | | Internal | Electronic signature time. | `2026-09-10T13:15:00Z` |

#### client_incidents
- **Purpose:** Client incident reports and their investigation (FR-DOC-03 to FR-DOC-06).
- **Owner module:** DOC
- **Volume:** About 50 rows per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Incident identifier. | `8e9f0a1b-2c3d-4e4f-9a5b-6c7d8e9f0a01` |
| client_id | uuid | N | FK -> clients | Internal | Client. | `5b2e8f14-…-c10234000001` |
| visit_id | uuid | Y | FK -> visits | Internal | Visit during which it occurred. | `a1f3c5e7-…-20260908a001` |
| reported_by | uuid | N | FK -> users | Internal | Reporter. | `4e8a9d4f-…-a20410000001` |
| occurred_at | timestamptz | N | | PHI | Time of occurrence. | `2026-09-08T14:35:00Z` |
| place **(added)** | text | Y | | PHI | Where it happened (FR-DOC-03). | `Bathroom` |
| category | text | N | CHECK `incident_category` | PHI | Category. | `Fall` |
| severity | text | N | CHECK `incident_severity` | PHI | Severity. | `Medium` |
| description | bytea | N | ENC | PHI | What happened. | ciphertext |
| people_involved **(added)** | text | Y | | PHI | People involved or present. | `Caregiver E-2041; client's son` |
| immediate_actions | text | N | | PHI | Actions taken at once. | `Assessed for injury, assisted to chair, called supervisor` |
| status | text | N | CHECK `incident_status` | Internal | `Reported`, `UnderReview`, `ActionsOpen` or `Closed`. | `UnderReview` |
| reportable | boolean | Y | set by `AG-SUPV` | PHI | Externally reportable. | `false` |
| report_deadline_at | timestamptz | Y | computed from category (BR-036) | Internal | External reporting deadline. | `NULL` |
| external_ref | text | Y | | PHI | External report reference. | `NULL` |
| investigation_notes **(added)** | bytea | Y | ENC | PHI | Investigation notes (FR-DOC-05). | ciphertext |
| root_cause | text | Y | required to close | PHI | Root cause. | `Wet floor; no bath mat` |

#### incident_actions
- **Purpose:** Corrective actions that must be `Done` or `Waived` before an incident can close (BR-037).
- **Owner module:** DOC
- **Volume:** About 100 rows per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Action identifier. | `9f0a1b2c-3d4e-4f5a-8b6c-7d8e9f0a1b01` |
| incident_id | uuid | N | FK -> client_incidents | Internal | Incident. | `8e9f0a1b-…-6c7d8e9f0a01` |
| description | text | N | | PHI | Action. | `Install non-slip bath mat and grab bar` |
| owner_id | uuid | N | FK -> users | Internal | Owner. | `3d9b6c3a-…-c0000000a001` |
| due_on | date | N | | Internal | Due date. | `2026-09-15` |
| status | text | N | CHECK `incident_action_status` | Internal | `Open`, `Done` or `Waived`. | `Open` |
| waiver_reason | text | Y | CHECK required when `Waived` | PHI | Waiver reason. | `NULL` |

### 5.D Time off, payroll, billing, notifications and audit

#### time_off_requests
- **Purpose:** Caregiver leave requests (FR-TOF-01 to FR-TOF-03).
- **Owner module:** TOF
- **Volume:** About 400 rows per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Request identifier. | `0a1b2c3d-4e5f-4a6b-9c7d-8e9f0a1b2c01` |
| caregiver_id | uuid | N | FK -> caregivers | Internal | Requester. | `9d4f1a37-…-e20410000001` |
| leave_type | text | N | CHECK `leave_type` | PII | `PTO`, `Sick`, `Unpaid` or `Bereavement`. | `PTO` |
| start_date | date | N | | PII | First day. | `2026-10-12` |
| end_date | date | N | CHECK `>= start_date` | PII | Last day. | `2026-10-14` |
| partial_hours | numeric(4,2) | Y | single-day requests only | PII | Hours for a partial day. | `NULL` |
| status | text | N | CHECK `time_off_status` | Internal | `Pending`, `Approved`, `Declined` or `Cancelled`. | `Approved` |
| short_notice | boolean | N | computed | Internal | Less than 7 days' notice and not `Sick` (BR-038). | `false` |
| decided_by | uuid | Y | FK -> users | Internal | Approver. | `3d9b6c3a-…-c0000000a001` |
| decided_at | timestamptz | Y | | Internal | Decision instant. | `2026-09-22T15:10:00Z` |

#### leave_balances
- **Purpose:** Leave balance per caregiver and leave type (FR-TOF-04, BR-040).
- **Owner module:** TOF
- **Volume:** About 250 rows.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| caregiver_id | uuid | N | PK, FK -> caregivers | Internal | Caregiver. | `9d4f1a37-…-e20410000001` |
| leave_type | text | N | PK; CHECK `leave_type` | PII | Leave type. | `PTO` |
| balance_hours | numeric(6,2) | N | CHECK 0 to the tenant cap (80 for PTO) | PII | Current balance. | `36.50` |

#### holidays
- **Purpose:** Tenant holiday calendar used by scheduling and payroll (FR-TOF-05, BR-042).
- **Owner module:** TOF
- **Volume:** About 10 rows per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| tenant_id | uuid | N | PK, FK -> tenants | Internal | Tenant. | `7c1e4a52-…-2d8f5b3c1a01` |
| date | date | N | PK | Internal | Holiday date. | `2026-09-07` |
| name | text | N | | Internal | Holiday name. | `Labor Day` |

#### pay_periods
- **Purpose:** Pay periods that are locked on export (FR-PAY-01, FR-PAY-05).
- **Owner module:** PAY
- **Volume:** 26 rows per year (TEN-001 pays bi-weekly).

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Period identifier. | `8f3a1c5e-7b9d-4e2f-a6c8-202609070001` |
| frequency | text | N | CHECK `pay_frequency` | Internal | `Weekly`, `BiWeekly` or `SemiMonthly`. | `Weekly` |
| start_date | date | N | UK (`tenant_id`, `start_date`); exclusion on overlap | Internal | First day. | `2026-09-07` |
| end_date | date | N | CHECK `>= start_date` | Internal | Last day. | `2026-09-13` |
| status | text | N | CHECK `pay_period_status` | Internal | `Open` or `Locked`. | `Locked` |
| locked_at | timestamptz | Y | | Internal | Lock instant (first export). | `2026-09-15T14:02:11Z` |

#### payroll_lines
- **Purpose:** Calculated pay lines per caregiver per period (FR-PAY-02, FR-PAY-03, FR-PAY-06).
- **Owner module:** PAY
- **Volume:** About 60,000 rows per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Line identifier. | `1b2c3d4e-5f6a-4b7c-8d9e-0f1a2b3c4d01` |
| pay_period_id | uuid | N | FK -> pay_periods | Internal | Period. | `8f3a1c5e-…-202609070001` |
| caregiver_id | uuid | N | FK -> caregivers | Internal | Caregiver. | `9d4f1a37-…-e20410000001` |
| line_type | text | N | CHECK `payroll_line_type` | Confidential | Line type. | `Holiday` |
| hours | numeric(12,6) | Y | `NULL` for `Mileage` | Confidential | Hours, computed from integer seconds (BR-045). | `6.000000` |
| miles **(added)** | numeric(8,1) | Y | `Mileage` only | Confidential | Reimbursable miles (BR-044). | `NULL` |
| rate_cents | bigint | N | | Confidential | Effective rate (base x multiplier, or mileage rate). | `2925` |
| amount_cents | bigint | N | | Confidential | Line amount. | `17550` |
| source_visit_id | uuid | Y | FK -> visits | Internal | Originating visit. | `a1f3c5e7-…-20260907a002` |
| adjusts_line_id | uuid | Y | FK -> payroll_lines | Internal | Line in a locked period that this adjustment corrects (BR-046). | `NULL` |

#### payroll_exports
- **Purpose:** Payroll CSV exports. The first export locks the period (FR-PAY-05).
- **Owner module:** PAY
- **Volume:** About 55 rows per year.
- **Notes:** Append-only.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Export identifier. | `2c3d4e5f-6a7b-4c8d-9e0f-1a2b3c4d5e02` |
| pay_period_id | uuid | N | FK -> pay_periods | Internal | Period. | `8f3a1c5e-…-202609070001` |
| file_key | text | N | | Confidential | S3 object key (SSE-KMS). | `tenants/7c1e4a52/payroll/2026-09-07/export-1.csv` |
| exported_by | uuid | N | FK -> users | Internal | Exporter (`AG-FIN`). | `d9e0f1a2-b3c4-4d5e-8f6a-7b8c9d0e1f01` |
| exported_at | timestamptz | N | | Internal | Export instant. | `2026-09-15T14:02:11Z` |
| row_count | integer | N | | Internal | Data rows in the file. | `62` |
| sha256 | text | N | CHECK 64 hex characters | Internal | File checksum. | `9f2c…e41a` |

#### billing_runs
- **Purpose:** One execution of the billing process for a period (FR-BIL-01).
- **Owner module:** BIL
- **Volume:** About 14 rows per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Run identifier. | `d7c9e1f3-5a7b-4c9d-8e1f-202609300001` |
| period_start | date | N | | Internal | Period start. | `2026-09-01` |
| period_end | date | N | | Internal | Period end. | `2026-09-30` |
| status | text | N | CHECK `billing_run_status` | Internal | `Running`, `Completed` or `Failed`. | `Completed` |
| started_by | uuid | Y | FK -> users | Internal | `AG-FIN` user, or `NULL` for a scheduled run. | `d9e0f1a2-…-7b8c9d0e1f01` |

#### invoices
- **Purpose:** Client invoices, one per client, payer and period (FR-BIL-01, FR-BIL-04, BR-050, BR-051).
- **Owner module:** BIL
- **Volume:** About 2,400 rows per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Invoice identifier. | `b4e2d6f8-1a3c-4e5b-9d7f-000000000123` |
| billing_run_id **(added)** | uuid | Y | FK -> billing_runs | Internal | Producing run. | `d7c9e1f3-…-202609300001` |
| client_id | uuid | N | FK -> clients | Internal | Client. | `5b2e8f14-…-c10234000001` |
| payer_id | uuid | N | FK -> payers | Internal | Payer. | `2c7a9e51-…-9d0e1f2a3b01` |
| number | text | N | UK (`tenant_id`, `number`) | PHI | Invoice number. | `INV-2026-000123` |
| period_start | date | N | | PHI | Service period start. | `2026-09-01` |
| period_end | date | N | | PHI | Service period end. | `2026-09-30` |
| status | text | N | CHECK `invoice_status` | Internal | Lifecycle (FR-BIL-04). | `Draft` |
| subtotal_cents | bigint | N | CHECK >= 0 | PHI | Billable lines total. | `17400` |
| credits_cents | bigint | N | default 0 | PHI | Credit notes total. | `0` |
| paid_cents | bigint | N | default 0 | PHI | Payments total. | `0` |
| balance_cents | bigint | N | CHECK `= subtotal - credits - paid` | PHI | Amount outstanding. | `17400` |
| due_date | date | Y | set at issue (net 30) | Internal | Due date (BR-052). | `NULL` |
| issued_at | timestamptz | Y | | Internal | Issue instant. | `NULL` |
| idempotency_key | text | N | **UK** over non-void rows (CR-005) | Internal | `tenant:client:payer:period_start:period_end` (BR-050). Unique among invoices whose status is not Void, so a voided invoice can be reissued under the same key (BR-051). | `7c1e4a52:5b2e8f14:2c7a9e51:2026-09-01:2026-09-30` |

#### invoice_lines
- **Purpose:** Priced lines, including not-billable excess (FR-BIL-02, FR-BIL-03).
- **Owner module:** BIL
- **Volume:** About 47,000 rows per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Line identifier. | `3d4e5f6a-7b8c-4d9e-8f0a-1b2c3d4e5f03` |
| invoice_id | uuid | N | FK -> invoices | Internal | Invoice. | `b4e2d6f8-…-000000000123` |
| visit_id | uuid | Y | FK -> visits | Internal | Visit priced; `NULL` for Fixed monthly. | `a1f3c5e7-…-20260915a001` |
| service_code | text | N | | PHI | Service code. | `T1019` |
| description | text | N | | PHI | Line text. | `Personal care, 15-min units, 2026-09-15 09:00-11:07 (127 min)` |
| units | numeric(10,4) | N | CHECK >= 0 | PHI | Units (BR-047, BR-048). | `8.0000` |
| unit_rate_cents | bigint | N | | Confidential | Rate per unit. | `725` |
| amount_cents | bigint | N | `0` when not billable | PHI | Amount charged. | `5800` |
| billable | boolean | N | | Internal | Counts toward the subtotal. | `true` |
| non_billable_reason | text | Y | CHECK `non_billable_reason`; required when not billable | Internal | Why the line is not charged (FR-BIL-03). | `NULL` |

#### credit_notes
- **Purpose:** Credits against issued invoices (FR-BIL-07, BR-051).
- **Owner module:** BIL
- **Volume:** About 40 rows per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Credit note identifier. | `4e5f6a7b-8c9d-4e0f-9a1b-2c3d4e5f6a04` |
| invoice_id | uuid | N | FK -> invoices (`Issued` or later) | Internal | Invoice. | `b4e2d6f8-…-000000000123` |
| amount_cents | bigint | N | CHECK > 0 and `<= balance` | PHI | Credit amount. | `1450` |
| reason | text | N | | PHI | Reason. | `Visit 2026-09-19 shortened by client request; 2 units credited` |
| issued_by | uuid | N | FK -> users | Internal | Issuer. | `d9e0f1a2-…-7b8c9d0e1f01` |

#### payments
- **Purpose:** Payments received against invoices, including payment-provider webhook updates (FR-BIL-05).
- **Owner module:** BIL
- **Volume:** About 450 rows per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Payment identifier. | `5f6a7b8c-9d0e-4f1a-8b2c-3d4e5f6a7b05` |
| invoice_id | uuid | N | FK -> invoices | Internal | Invoice. | `b4e2d6f8-…-000000000456` |
| amount_cents | bigint | N | CHECK > 0 | Confidential | Amount. | `31175` |
| method | text | N | CHECK `payment_method` | Internal | `Card`, `ACH`, `Check` or `Payer`. | `Card` |
| provider_ref | text | Y | UK | Confidential | Provider payment reference. | `pi_3PzX7aLakemont9` |
| status | text | N | CHECK `payment_status` | Internal | `Pending`, `Succeeded`, `Failed` or `Refunded`. | `Succeeded` |
| received_at | timestamptz | Y | | Internal | Settlement instant. | `2026-10-02T16:45:09Z` |

#### claim_batches
- **Purpose:** Payer claim batch CSV exports for the agency's clearinghouse (FR-BIL-06).
- **Owner module:** BIL
- **Volume:** About 48 rows per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Batch identifier. | `6a7b8c9d-0e1f-4a2b-9c3d-4e5f6a7b8c06` |
| payer_id | uuid | N | FK -> payers | Internal | Payer. | `2c7a9e51-…-9d0e1f2a3b01` |
| period_start | date | N | | Internal | Period start. | `2026-09-01` |
| period_end | date | N | | Internal | Period end. | `2026-09-30` |
| file_key | text | N | | Confidential | S3 object key. | `tenants/7c1e4a52/claims/2026-09/lcmw-1.csv` |
| claim_count | integer | N | CHECK > 0 | Internal | Claims in the file. | `112` |
| total_cents | bigint | N | | Confidential | Batch total. | `2318450` |

#### notifications
- **Purpose:** One delivery per recipient, channel and escalation step (FR-NTF-01 to FR-NTF-05).
- **Owner module:** NTF
- **Volume:** About 300,000 rows per year. Partitioned monthly.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Notification identifier. | `7b8c9d0e-1f2a-4b3c-8d4e-5f6a7b8c9d07` |
| event_id | uuid | N | logical reference to `event_outbox.id` (no FK; the outbox is purged) | Internal | Triggering event. | `0e1f2a3b-4c5d-4e6f-9a7b-8c9d0e1f2a08` |
| event_type | text | N | | Internal | Event type. | `dose.missed` |
| recipient_user_id | uuid | N | FK -> users; must be `Active` at send (BR-054) | Internal | Recipient resolved at send time. | `c8d9e0f1-…-6a7b8c9d0e01` |
| channel | text | N | CHECK `notification_channel` | Internal | `InApp`, `Push`, `Email` or `SMS`. | `SMS` |
| step | smallint | N | default 0 | Internal | Escalation step. | `0` |
| status | text | N | CHECK `notification_status` | Internal | `Queued`, `Held` (quiet hours), `Sent`, `Failed` or `Suppressed`. | `Sent` |
| dedupe_key | text | N | **UK** | Internal | `event_id:recipient_user_id:step:channel` (BR-055). | `0e1f2a3b…:c8d9e0f1…:0:SMS` |
| attempts | smallint | N | CHECK 0-4 | Internal | Delivery attempts (first plus 3 retries). | `1` |
| sent_at | timestamptz | Y | | Internal | Delivery instant. | `2026-09-08T14:00:04Z` |
| read_at **(added)** | timestamptz | Y | `InApp` only | Internal | When the user marked it read. | `NULL` |

Rendered message text is not stored. Templates hold generic, PHI-free text with a sign-in deep link (BR-056, CR-006).

#### notification_preferences
- **Purpose:** User channel choices per event type (FR-NTF-01).
- **Owner module:** NTF
- **Volume:** About 1,200 rows.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| user_id | uuid | N | PK, FK -> users | Internal | User. | `4e8a9d4f-…-a20410000001` |
| event_type | text | N | PK | Internal | Event type. | `visit.changed` |
| channels | text[] | N | CHECK values in `notification_channel`; `InApp` always included | Internal | Selected channels. | `{InApp,Push}` |

#### escalation_ladders
- **Purpose:** Escalation steps per event type (FR-NTF-03, BR-054).
- **Owner module:** NTF
- **Volume:** About 12 rows.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Ladder identifier. | `8c9d0e1f-2a3b-4c4d-9e5f-6a7b8c9d0e09` |
| event_type | text | N | UK (`tenant_id`, `event_type`) | Internal | Event type. | `dose.missed` |
| steps | jsonb | N | JSON Schema: role codes only, no user IDs (CR-006) | Internal | Ordered steps. | `[{"delay_min":0,"recipient_role":"AG-SUPV","channels":["Push","SMS"]},{"delay_min":30,"recipient_role":"AG-ADM","channels":["SMS","Email"]}]` |

#### audit_events
- **Purpose:** The immutable audit trail of creates, updates, deletes, PHI reveals, exports, sign-ins, permission changes and support access (FR-RPT-03, BR-057).
- **Owner module:** RPT
- **Volume:** About 1.5 million rows per year, about 10.5 million at the 7-year retention. Partitioned monthly.
- **Notes:** Append-only.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Event identifier. | `9d0e1f2a-3b4c-4d5e-8f6a-7b8c9d0e1f10` |
| tenant_id | uuid | Y | FK -> tenants | Internal | Tenant; `NULL` for platform-level actions. | `7c1e4a52-…-2d8f5b3c1a01` |
| actor_user_id | uuid | Y | FK -> users | Internal | Actor; `NULL` for `System`. | `3d9b6c3a-…-c0000000a001` |
| actor_type | text | N | CHECK `actor_type` | Internal | `User`, `System` or `Support`. | `User` |
| action | text | N | | Internal | Verb in `entity.verb` form. | `client.phi_revealed` |
| entity_type | text | N | | Internal | Table or aggregate. | `client` |
| entity_id | uuid | Y | logical reference | Internal | Entity. | `5b2e8f14-…-c10234000001` |
| before | jsonb | Y | PHI as ciphertext references | PHI | Prior values of changed fields. | `null` |
| after | jsonb | Y | PHI as ciphertext references | PHI | New values; for reveals, the field names and reason only. | `{"fields":["medicaidId"],"reason":"Eligibility check with payer"}` |
| ip | inet | Y | | PII | Client IP address. | `203.0.113.17` |
| device | text | Y | | PII | User agent. | `Chrome 129 / Windows 11` |
| support_grant_id | uuid | Y | FK -> support_access_grants | Internal | Grant in effect (BR-008). | `NULL` |
| occurred_at | timestamptz | N | | Internal | Event instant. | `2026-09-08T17:01:27Z` |

#### job_executions
- **Purpose:** The single-flight ledger for scheduled and webhook-triggered jobs (ADR-003, NFR-MNT-02).
- **Owner module:** Platform
- **Volume:** About 4,000 rows per tenant per year; purged after 90 days.
- **Notes:** This is a platform table. The tenant is embedded in `idempotency_key`.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Execution identifier. | `ae1f2a3b-4c5d-4e6f-9a7b-8c9d0e1f2a11` |
| job_name | text | N | | Internal | Job. | `billing-run` |
| idempotency_key | text | N | **UK** | Internal | Job, tenant and business period, or a provider event ID. | `billing-run:7c1e4a52:2026-09` |
| status | text | N | CHECK `job_execution_status` | Internal | `Running`, `Succeeded` or `Failed`. | `Succeeded` |
| started_at | timestamptz | N | | Internal | Start instant. | `2026-10-01T06:00:00Z` |
| finished_at | timestamptz | Y | | Internal | End instant. | `2026-10-01T06:01:52Z` |

### 5.E Supporting entities (added)

#### documents (added)
- **Purpose:** Metadata for files in S3: credential scans and incident photos.
- **Owner module:** WRK, DOC
- **Volume:** About 1,500 rows per year.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Document identifier. | `6b7c8d9e-0f1a-4b2c-9d3e-4f5a6b7c8d01` |
| owner_type | text | N | CHECK in (`caregiver_credential`, `client_incident`) | Internal | Owning entity type. | `caregiver_credential` |
| owner_id | uuid | N | logical reference | Internal | Owning entity. | `5a6b7c8d-…-3e4f5a6b7c01` |
| file_key | text | N | UK | Confidential | S3 key (SSE-KMS; pre-signed URLs valid for 5 minutes). | `tenants/7c1e4a52/docs/6b7c8d9e.pdf` |
| content_type | text | N | allow-list | Internal | MIME type. | `application/pdf` |
| size_bytes | integer | N | CHECK <= 10 MB | Internal | Size. | `248113` |
| sha256 | text | N | | Internal | Checksum. | `51d0…7c3b` |

#### reason_codes (added)
- **Purpose:** Tenant-configurable reason code lists provisioned by FR-ONB-04.
- **Owner module:** EVV, SCH
- **Volume:** About 60 rows.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Identifier. | `bf2a3b4c-5d6e-4f7a-8b9c-0d1e2f3a4b12` |
| list | text | N | CHECK in (`EVV_RESOLUTION`, `TIME_CORRECTION`, `VISIT_CANCELLATION`) | Internal | Code list. | `EVV_RESOLUTION` |
| code | text | N | UK (`tenant_id`, `list`, `code`) | Internal | Code value. | `SERVICE_AT_ALTERNATE_LOCATION` |
| label | text | N | | Internal | Display label. | `Service delivered at an alternate location` |
| is_active | boolean | N | | Internal | Selectable for new records. | `true` |

#### event_outbox (added)
- **Purpose:** The transactional outbox for domain events. Each event is written in the same transaction as the business change and published to the job queue (see [events and webhooks](../../04-api/events-and-webhooks.md)).
- **Owner module:** Platform
- **Volume:** About 35,000 rows at any time; purged 30 days after publication.

| Column | Type | Null | Key / constraint | Class | Description | Example |
|---|---|---|---|---|---|---|
| id | uuid | N | PK | Internal | Event ID (the CloudEvents `id`). | `0e1f2a3b-4c5d-4e6f-9a7b-8c9d0e1f2a08` |
| event_type | text | N | | Internal | Event type. | `dose.missed` |
| subject | text | N | | Internal | Aggregate reference. | `dose-tasks/2e3f4a5b-…-1c2d3e4f5a01` |
| payload | jsonb | N | | PHI | Event data. Identifiers and facts, no names. | `{"doseTaskId":"2e3f4a5b-…","clientId":"5b2e8f14-…","scheduledAt":"2026-09-08T12:00:00Z"}` |
| occurred_at | timestamptz | N | | Internal | Business time. | `2026-09-08T14:00:00Z` |
| published_at | timestamptz | Y | | Internal | When the event was enqueued. | `2026-09-08T14:00:01Z` |

## 6. Example: pricing visible in the data

The canonical Hourly example (US-045) produces these rows for client C-10234 on authorization T1019 at 725 cents per unit:

| invoice_lines.description | units | unit_rate_cents | amount_cents | billable | non_billable_reason |
|---|---|---|---|---|---|
| 2026-09-15 (127 min: 8 r7, no round-up) | 8 | 725 | 5800 | true | |
| 2026-09-17 (113 min: 7 r8, round up) | 8 | 725 | 5800 | true | |
| 2026-09-19 (120 min) | 8 | 725 | 5800 | true | |
| **invoices.subtotal_cents** | | | **17400** | | |

If only 20 units remain on the authorization, the third visit splits into a 4-unit billable line (2,900 cents) and a 4-unit line with `billable = false`, `amount_cents = 0` and `non_billable_reason = 'EXCEEDS_AUTHORIZATION'`. The subtotal is then 14,500 cents (FR-BIL-03, BR-049).

## 7. Enumerations

Values are stored exactly as shown (case-sensitive) and match the API enums.

| Enumeration | Values | Used by | Source |
|---|---|---|---|
| tenant_status | `Pending`, `Trial`, `Active`, `ReadOnly`, `Cancelled` | tenants.status | FR-ONB-07, BR-003 |
| plan_status | `Active`, `Retired` | plans.status | FR-ONB-08 |
| promo_kind | `Trial`, `Discount` | promo_codes.kind | BR-004 |
| discount_type | `Percent`, `Fixed` | promo_codes.discount_type | BR-004 |
| promo_status | `Active`, `Retired` (design-defined; not enumerated in the SRS) | promo_codes.status | FR-ONB-08 |
| subscription_status | `Trialing`, `Active`, `PastDue`, `ReadOnly`, `Cancelled` | subscriptions.status | FR-ONB-06, FR-ONB-07 |
| user_status | `Invited`, `Active`, `Locked`, `Deactivated` | users.status | FR-IAM-03 |
| override_effect | `Grant`, `Deny` | user_permission_overrides.effect | BR-005 |
| support_grant_scope | `ReadOnly`, `ReadWrite` | support_access_grants.scope | BR-008 |
| support_grant_status | `Requested`, `Active`, `Expired`, `Revoked`, `Declined` | support_access_grants.status | FR-IAM-07 |
| sign_in_outcome | `Success`, `BadPassword`, `MfaFailed`, `Locked` | sign_in_events.outcome | FR-IAM-08 |
| service_line_code | `HOME_VISIT`, `ADULT_DAY`, `SUPPORTED_LIVING` | service_lines.code | FR-ONB-01 |
| client_status | `Active`, `OnHold`, `Discharged` | clients.status | FR-CLI-07 |
| pref_kind | `Preferred`, `Excluded` | client_caregiver_prefs.kind | BR-017 |
| payer_type | `Medicaid`, `ManagedCare`, `LTCInsurance`, `PrivatePay`, `VA` | payers.payer_type | FR-CLI-03 |
| billing_model | `Hourly`, `PerVisit`, `Daily`, `FixedMonthly` | service_authorizations.billing_model | FR-BIL-02 |
| unit_type | `Unit15Min`, `Visit`, `Day`, `Month` | service_authorizations.unit_type | FR-CLI-03 |
| authorization_status | `Active`, `Expired`, `Suspended` | service_authorizations.status | BR-009 |
| care_plan_status | `Draft`, `PendingApproval`, `Active`, `Superseded` | care_plans.status | BR-012 |
| task_category | `ADL`, `IADL`, `Clinical` | care_plan_tasks.category | FR-CLI-05 |
| employment_type | `FullTime`, `PartTime`, `PerDiem` | caregivers.employment_type | FR-WRK-01 |
| caregiver_status | `Active`, `Inactive` | caregivers.status | FR-WRK-06 |
| credential_status | `Valid`, `Expiring`, `Expired` | caregiver_credentials.status | BR-014 |
| pay_type | `Hourly`, `Salaried` | pay_profiles.pay_type | FR-WRK-05 |
| visit_status | `Scheduled`, `InProgress`, `Completed`, `NeedsReview`, `Verified`, `Cancelled`, `Missed` | visits.status | BR-019 |
| punch_type | `In`, `Out` | evv_punches.type | FR-EVV-02 |
| punch_source | `Mobile`, `MobileOffline`, `Manual`, `System` | evv_punches.source | BR-025, BR-026, BR-027 |
| identity_result | `Pass`, `Fail` | identity_checks.result | FR-EVV-04 |
| exception_code | `LATE_START`, `EARLY_END`, `LOCATION_MISMATCH`, `LOW_GPS_ACCURACY`, `MISSING_CLOCK_OUT`, `UNSCHEDULED_VISIT`, `LATE_OFFLINE_SYNC`, `AUTO_CLOSED`, `IDENTITY_CHECK_FAILED` | visit_exceptions.code | FR-EVV-07; `LOW_GPS_ACCURACY` added by CR-004 |
| exception_status | `Open`, `Resolved`, `Waived` | visit_exceptions.status | FR-EVV-08 |
| task_result_status | `Done`, `NotDone` | visit_task_results.status | FR-EVV-06 |
| medication_order_status | `PendingApproval`, `Active`, `Discontinued` | medication_orders.status | FR-MAR-01 |
| dose_status | `Due`, `Overdue`, `Given`, `Refused`, `Held`, `NotAvailable`, `SelfAdministered`, `MissedUndocumented` | dose_tasks.status | FR-MAR-03, FR-MAR-04, BR-030 |
| vital_type | `BP`, `PULSE`, `TEMP`, `SPO2`, `RESP`, `GLUCOSE`, `WEIGHT`, `PAIN` | vital_readings.type, vital_ranges.type | FR-MAR-07 |
| note_status | `Draft`, `Submitted`, `Locked` | visit_notes.status | BR-035 |
| incident_category | `Fall`, `Injury`, `MedicationError`, `Behavioral`, `SuspectedAbuseNeglect`, `PropertyDamage`, `Other` | client_incidents.category | FR-DOC-03 |
| incident_severity | `Low`, `Medium`, `High` | client_incidents.severity | FR-DOC-04 |
| incident_status | `Reported`, `UnderReview`, `ActionsOpen`, `Closed` | client_incidents.status | FR-DOC-05 |
| incident_action_status | `Open`, `Done`, `Waived` | incident_actions.status | BR-037 |
| leave_type | `PTO`, `Sick`, `Unpaid`, `Bereavement` | time_off_requests, leave_balances | FR-TOF-01 |
| time_off_status | `Pending`, `Approved`, `Declined`, `Cancelled` | time_off_requests.status | FR-TOF-03 |
| pay_frequency | `Weekly`, `BiWeekly`, `SemiMonthly` | pay_periods.frequency | FR-PAY-01 |
| pay_period_status | `Open`, `Locked` | pay_periods.status | BR-046 |
| payroll_line_type | `Regular`, `Overtime`, `DoubleTime`, `Holiday`, `Travel`, `PTO`, `Mileage`, `Adjustment` | payroll_lines.line_type | FR-PAY-02; `DoubleTime` used by CR-001 |
| billing_run_status | `Running`, `Completed`, `Failed` (design-defined) | billing_runs.status | FR-BIL-01 |
| invoice_status | `Draft`, `Approved`, `Issued`, `PartiallyPaid`, `Paid`, `Overdue`, `Void` | invoices.status | FR-BIL-04 |
| non_billable_reason | `EXCEEDS_AUTHORIZATION`, `NO_COVERING_AUTHORIZATION`, `ADDITIONAL_VISIT_SAME_DAY` (design-defined) | invoice_lines.non_billable_reason | FR-BIL-03, BR-048 |
| payment_method | `Card`, `ACH`, `Check`, `Payer` | payments.method | FR-BIL-05 |
| payment_status | `Pending`, `Succeeded`, `Failed`, `Refunded` (design-defined) | payments.status | FR-BIL-05 |
| notification_channel | `InApp`, `Push`, `Email`, `SMS` | notifications.channel, notification_preferences.channels | FR-NTF-01 |
| notification_status | `Queued`, `Held`, `Sent`, `Failed`, `Suppressed` | notifications.status | FR-NTF-02, FR-NTF-04 |
| actor_type | `User`, `System`, `Support` | audit_events.actor_type | BR-057 |
| job_execution_status | `Running`, `Succeeded`, `Failed` (design-defined) | job_executions.status | ADR-003 |

**Default reason codes (seeded by FR-ONB-04; tenant-configurable)**

| List | Codes |
|---|---|
| EVV_RESOLUTION | `CAREGIVER_FORGOT_TO_CLOCK`, `DEVICE_OR_APP_ISSUE`, `GPS_DRIFT_CONFIRMED`, `SERVICE_AT_ALTERNATE_LOCATION`, `CLIENT_CONFIRMED_BY_PHONE`, `NO_SERVICE_DELIVERED` |
| TIME_CORRECTION | `CAREGIVER_FORGOT_TO_CLOCK`, `DEVICE_OR_APP_ISSUE`, `AUTO_CLOSE_ACTUAL_END_CONFIRMED`, `WRONG_VISIT_SELECTED` |
| VISIT_CANCELLATION | `CLIENT_REQUEST`, `CLIENT_HOSPITALIZED`, `CLIENT_DISCHARGED`, `CAREGIVER_UNAVAILABLE`, `TIME_OFF_APPROVED`, `WEATHER_OR_EMERGENCY`, `AUTHORIZATION_ENDED` |

## 8. Index and constraint highlights

| # | Object | Definition | Purpose and reference |
|---|---|---|---|
| 1 | `ux_invoices_idempotency_key` | `UNIQUE INDEX (idempotency_key) WHERE status <> 'Void'` on `invoices` (partial) | The database guarantee of one non-void invoice per tenant, client, payer and period, while still allowing void-and-reissue (BR-051). Billing upserts with `ON CONFLICT (idempotency_key) WHERE status <> 'Void' DO UPDATE ... WHERE invoices.status = 'Draft'` (BR-050, CR-005, ADR-003, INC-2026-007). |
| 2 | `ux_notifications_dedupe_key` | `UNIQUE (dedupe_key)` on `notifications` | One delivery per event, recipient, step and channel; redelivered events are no-ops (BR-055, FR-NTF-04). |
| 3 | `ix_visit_exceptions_open` | `INDEX (tenant_id, code, created_at) WHERE status = 'Open'` | Coordinator exception queue and the dashboard count (FR-EVV-08, FR-RPT-01). Partial, so resolved history does not bloat it. |
| 4 | `ux_visit_exceptions_open_code` | `UNIQUE (visit_id, code) WHERE status = 'Open'` | At most one open exception of each code per visit. A repeat condition updates the existing exception. |
| 5 | `ux_job_executions_idempotency_key` | `UNIQUE (idempotency_key)` on `job_executions` | Single-flight scheduled jobs and idempotent webhook processing (ADR-003, NFR-MNT-02). |
| 6 | `ux_evv_punches_identity_check` | `UNIQUE (identity_check_id) WHERE identity_check_id IS NOT NULL` | An identity check authorizes one punch only (BR-024). |
| 7 | `ex_visits_caregiver_overlap` | `EXCLUDE USING gist (tenant_id WITH =, caregiver_id WITH =, tstzrange(scheduled_start, scheduled_end) WITH &&) WHERE (caregiver_id IS NOT NULL AND status NOT IN ('Cancelled','Missed'))` | Database backstop for the caregiver overlap hard block (BR-016). Requires `btree_gist`. |
| 8 | `ex_service_authorizations_overlap` | `EXCLUDE USING gist (client_id WITH =, payer_id WITH =, service_code WITH =, daterange(period_start, period_end, '[]') WITH &&) WHERE (status = 'Active')` | No two active authorizations for the same service and payer overlap (BR-009). |
| 9 | `ux_care_plans_active` | `UNIQUE (client_id) WHERE status = 'Active'` | One active care plan per client (BR-012). |
| 10 | `ux_dose_tasks_order_time` | `UNIQUE (order_id, scheduled_at)` | Idempotent rolling 7-day generation (FR-MAR-02). |
| 11 | `ix_dose_tasks_escalation` | `INDEX (tenant_id, window_end) WHERE status IN ('Due','Overdue')` | The escalation job finds doses to move to `Overdue` or `MissedUndocumented` (BR-030). |
| 12 | `ux_pay_profiles_effective` | `UNIQUE (caregiver_id, effective_from)` | Effective dating (BR-015). |
| 13 | `ex_pay_periods_overlap` | `EXCLUDE USING gist (tenant_id WITH =, daterange(start_date, end_date, '[]') WITH &&)` | Contiguous, non-overlapping pay periods (FR-PAY-01). |
| 14 | `ux_subscriptions_current` | `UNIQUE (tenant_id) WHERE status <> 'Cancelled'` | One live subscription per tenant. |
| 15 | `ux_clients_number`, `ux_caregivers_employee_number`, `ux_invoices_number` | `UNIQUE (tenant_id, client_number)`, `UNIQUE (tenant_id, employee_number)`, `UNIQUE (tenant_id, number)` | Human-readable identifiers, unique per tenant. |
| 16 | `ix_clients_medicaid_bidx`, `ix_clients_dob_bidx` | `INDEX (tenant_id, medicaid_id_bidx)`, `INDEX (tenant_id, dob_bidx, lower(last_name))` | Duplicate-client warning without decrypting PHI (FR-CLI-02). |
| 17 | `ux_payments_provider_ref` | `UNIQUE (provider_ref)` | A replayed provider webhook cannot record a payment twice (FR-BIL-05). |
| 18 | `ix_visits_board` | `INDEX (tenant_id, scheduled_start) INCLUDE (caregiver_id, client_id, status)` | Schedule board week view of 500 visits in 2.5 s or less at p95 (NFR-PERF-03). |
| 19 | `ix_caregiver_credentials_expiry` | `INDEX (tenant_id, expires_on) WHERE status <> 'Expired'` | Daily status recompute and the 30/14/1-day reminders (FR-WRK-02, FR-WRK-04). |
| 20 | `ix_audit_events_entity` | `INDEX (tenant_id, entity_type, entity_id, occurred_at)` on each monthly partition | Audit search by record (FR-RPT-03). |
| 21 | Check constraints | `chk_task_result_reason`: `status = 'Done' OR reason IS NOT NULL`; `chk_dose_reason`: `status NOT IN ('Refused','Held','NotAvailable') OR reason IS NOT NULL`; `chk_action_waiver`: `status <> 'Waived' OR waiver_reason IS NOT NULL`; `chk_manual_punch`: `source <> 'Manual' OR (reason_code IS NOT NULL AND note IS NOT NULL)`; `chk_invoice_balance`: `balance_cents = subtotal_cents - credits_cents - paid_cents`; `chk_grant_duration`: `expires_at <= starts_at + interval '4 hours'` | Rules enforced by the database as well as the API (FR-EVV-06, BR-032, BR-037, BR-026, FR-BIL-07, BR-008). |
| 22 | Append-only triggers | `BEFORE UPDATE OR DELETE` trigger raising an exception on `evv_punches`, `audit_events`, `sign_in_events`, `note_addenda`, `prn_administrations`, `payroll_exports` | Immutability (BR-026, BR-057). |
| 23 | RLS policies | `tenant_isolation` on every table with `tenant_id` | Tenant isolation in the database (BR-001, ADR-001). |

## Related documents

- [Entity relationship model](erd.md)
- [Data classification and retention](data-classification-and-retention.md)
- [Software requirements specification](../../02-requirements/SRS.md)
- [Business rules catalog](../../02-requirements/business-rules.md)
- [Glossary](../../02-requirements/glossary.md)
- [Non-functional requirements](../../02-requirements/non-functional-requirements.md)
- [OpenAPI specification](../../04-api/openapi.yaml)
- [Events and webhooks](../../04-api/events-and-webhooks.md)
- [Test data](../../06-quality/test-data/README.md)
