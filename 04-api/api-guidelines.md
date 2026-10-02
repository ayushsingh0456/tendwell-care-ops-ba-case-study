# Tendwell API Design Guidelines

## Document control

| Field | Value |
|---|---|
| Document ID | TW-API-02 |
| Version | 1.3 |
| Status | Baselined (aligned to SRS v1.3) |
| Owner | Business Analyst |
| Last updated | 2026-09-24 |
| Reviewers | Engineering Lead (approver), Backend Developers, Mobile Developer, QA Lead, Compliance and Privacy Officer |

## 1. Purpose and scope

These guidelines define the conventions that every Tendwell REST endpoint follows. Developers use them to build the API, QA uses them to test it, and integrators use them to call it.

The contract itself is [openapi.yaml](openapi.yaml), OpenAPI 3.1, covering 105 operations. Domain events and the payment webhook are in [events and webhooks](events-and-webhooks.md).

The rules apply to all `/v1` endpoints used by:
- the Agency Web App;
- the Caregiver Mobile App;
- the Platform Console;
- the public sign-up site;
- the Family Portal in Release 2.

## 2. Design principles

1. **Contract first.** The OpenAPI document is written and reviewed before code. It carries traceability extensions:
   - `x-requirements`, `x-business-rules` and `x-change-requests`;
   - `x-permission` and `x-roles`;
   - `x-phi` and `x-release`.

   CI checks that each of these extensions is present.
2. **Business rules on the server.** Every rule is enforced by the API, and by the database where possible: RLS, unique keys, exclusion constraints. A client cannot bypass a rule by calling the API directly (FR-IAM-06).
3. **Care is never blocked.** These care-critical writes are designed to always succeed:
   - EVV clock-in and clock-out;
   - offline sync;
   - point-of-care documentation.

   Data quality problems become reviewable exceptions, not errors (FR-EVV-03, BR-003).
4. **Minimum necessary.** Responses carry only the PHI the caller's task needs. Designated PHI is masked until revealed (NFR-PRIV-01).
5. **Explicit over clever.** State changes with business meaning are named commands, such as `POST /invoices/{invoiceId}/issue`, not generic field updates. Each command has its own permission, its own rules and its own audit event.

## 3. Versioning and deprecation

| Topic | Rule |
|---|---|
| Major version | In the URL path: `https://api.tendwell.example/v1`. A new major version (`/v2`) is introduced only for breaking changes, and both versions run in parallel during the deprecation period. |
| Contract version | `info.version` uses semantic versioning and moves with the SRS: `1.3.0` corresponds to SRS v1.3. |
| Non-breaking changes (allowed in `/v1`) | New endpoints; new optional request fields; new response fields; new optional query parameters; new error codes; relaxed validation. |
| Breaking changes (need `/v2` or a new operation) | Removing or renaming a field, parameter or endpoint; changing a type or format; making an optional field required; tightening validation; changing the meaning of a status or an enum value. |
| New enum values | Clients must tolerate unknown enum values and unknown properties (tolerant reader). New values are announced in the changelog at least 30 days before they are first returned. |
| Deprecation notice | At least **6 months** between the deprecation announcement and removal. Deprecated operations set `deprecated: true` in OpenAPI and return the `Deprecation` header (date of announcement), the `Sunset` header (RFC 8594, removal date) and `Link: <docs URL>; rel="deprecation"`. |
| Communication | Changelog entry, an in-app banner for Agency Administrators, and an email to the technical contacts. Usage of deprecated operations is tracked per client so that remaining callers can be contacted before the sunset date. |
| Mobile app versions | Caregiver devices update slowly. The API supports every Caregiver App version released in the last 6 months. Older versions receive `426 Upgrade Required` only after the in-app upgrade prompt has run for 30 days. Offline sync is never rejected because of the app version: punches are always accepted and the upgrade prompt follows. |

## 4. Resource naming and URL design

| Rule | Example |
|---|---|
| Plural nouns, lowercase kebab-case path segments | `/visit-exceptions`, `/time-off-requests` |
| Path parameters in camelCase, named `{resourceId}` | `/clients/{clientId}/authorizations` |
| Nest one level at most, and only when the child's lifecycle belongs to the parent | `/clients/{clientId}/care-plans`, then `/care-plans/{carePlanId}/approve` |
| Business commands are `POST` to a verb sub-resource | `/visits/{visitId}/cancel`, `/invoices/{invoiceId}/void`, `/clients/{clientId}/discharge` |
| Caller-scoped resources live under `/me` | `/me/notifications`, `/me/notification-preferences` |
| The tenant comes from the token, never from the URL | There is no `/tenants/{tenantId}/...` path for agency users |
| IDs are opaque UUIDs. Human-readable numbers are fields, not keys. | `clientNumber: C-10234`, `employeeNumber: E-2041`, `number: INV-2026-000123` |
| JSON properties and query parameters in camelCase | `scheduledStart`, `amountCents`, `?serviceLineCode=HOME_VISIT` |
| Enum values exactly as in the data model: PascalCase for statuses, UPPER_SNAKE for codes | `NeedsReview`, `LOCATION_MISMATCH`, `HOME_VISIT` |
| Event types in lowercase `entity.past_tense` | `visit.clocked_in`, `payperiod.locked` |
| Platform-only resources under `/platform` | `/platform/plans` |

### 4.1 Methods

| Method | Use | Idempotent | Body |
|---|---|---|---|
| `GET` | Read. Never changes state. | Yes | None |
| `POST` | Create, or run a business command | With `Idempotency-Key` (section 9) | JSON |
| `PATCH` | Partial update with JSON merge-patch semantics (RFC 7396): absent fields are unchanged and `null` clears a nullable field | Yes, with `If-Match` | JSON |
| `PUT` | Full replacement of a sub-resource set, such as roles, overrides, vital ranges, preferences or an escalation ladder | Yes | JSON |
| `DELETE` | Not used in Release 1. Records are deactivated, cancelled or voided rather than deleted ([ERD section 7.6](../03-design/data/erd.md#76-soft-delete-and-hard-delete-policy)). | n/a | n/a |

## 5. Request and response format

- **Content type.** `application/json; charset=utf-8`. The identity check upload uses `multipart/form-data`. Exports also offer `text/csv` and `application/pdf` through `Accept`.
- **Collections.** Collections return `{ "data": [...], "page": { "nextCursor": "...", "hasMore": true } }`. Single resources are returned unwrapped.
- **Nulls.** Nullable fields are always present in responses, with `null` when empty. Clients must not depend on property order.
- **Unknown request properties.** These are rejected with `400 API_VALIDATION_FAILED`, which catches typos such as `scheduledstart`. Responses may gain new properties at any time.
- **Money.** Money is an integer number of cents in fields ending in `Cents`, such as `amountCents: 17400`. The currency is always USD. Floating-point money is never used.
- **Quantities.** Hours and units are JSON numbers. Hours are rounded to 2 decimals for display only (BR-045).
- **Status codes on success.** `200` for reads and commands, `201` for creates (with `Location`), `202` for asynchronous work (billing runs, audit exports, sign-up), and `204` when there is no body.

## 6. Pagination

- All collections use cursor pagination. Cursors are opaque, base64url-encoded and bound to the query's filters and sort order.
- `limit` defaults to 50, with a maximum of 200. `page.nextCursor` is `null` when there are no more results.
- Cursors expire after 24 hours. An expired or tampered cursor returns `400 API_CURSOR_INVALID`, and the client restarts from the first page.
- Ordering is stable: the sort key plus `id` as a tie-breaker. Rows inserted during paging do not cause duplicates or gaps.
- Total counts are not returned by default because they are expensive at scale (NFR-SCL-01). Dashboards use dedicated count endpoints such as `GET /reports/operations-dashboard`.

## 7. Filtering and sorting

| Rule | Example |
|---|---|
| Equality filters use the response property name | `GET /visits?caregiverId=9d4f1a37-...&serviceLineCode=HOME_VISIT` |
| Multiple values are comma-separated (OR) | `GET /visit-exceptions?code=LOCATION_MISMATCH,LOW_GPS_ACCURACY` |
| Different filters combine with AND | `?status=Open&locationId=...` |
| Instant ranges use `from` (inclusive) and `to` (exclusive), in RFC 3339 UTC | `GET /visits?from=2026-09-07T04:00:00Z&to=2026-09-14T04:00:00Z` |
| Date ranges in reports use tenant-local dates, inclusive | `GET /reports/EVV_COMPLIANCE?from=2026-09-01&to=2026-09-30` |
| Range limits | Visits: 31 days (`400 SCH_DATE_RANGE_TOO_LARGE`). Reports and audit exports: 366 days (`422 RPT_DATE_RANGE_TOO_LARGE`). |
| `sort` takes one field from the endpoint's allow-list; a `-` prefix means descending | `GET /invoices?sort=-dueDate` |
| **No PHI in filters** | Names, date of birth, Medicaid ID, phone, address, diagnosis and medication are never filter parameters. A query parameter that looks like one returns `400 API_PHI_IN_QUERY_REJECTED` (section 13). |
| Location scoping is always applied | `locationId` can narrow the results, never widen them beyond the caller's assigned locations |

## 8. Errors

Every error response is an RFC 9457 problem document with media type `application/problem+json`:

```json
{
  "type": "https://api.tendwell.example/problems/EVV_CLOCK_IN_WINDOW_NOT_OPEN",
  "title": "It is too early to clock in",
  "status": 422,
  "detail": "Clock-in opens at 08:45, 15 minutes before the 09:00 start. Try again then.",
  "instance": "/v1/visits/a1f3c5e7-0b2d-4c6e-8f1a-20260908a001/clock-in",
  "code": "EVV_CLOCK_IN_WINDOW_NOT_OPEN",
  "requestId": "5e1d7a90-3c2b-4f8e-9a6d-0b1c2d3e4f5a",
  "errors": [
    { "code": "EVV_CLOCK_IN_WINDOW_NOT_OPEN", "message": "Opens 2026-09-08T12:45:00Z.", "ruleRef": "BR-023" }
  ]
}
```

- `code` is stable and machine-readable, in the form `<MODULE>_<REASON>`. Clients branch on `code`, never on `title` or `detail`.
- `title` and `detail` are user-safe and state the problem and the fix (NFR-USE-03). The UI may show them directly, and the UI never shows the raw code to end users.
- `errors[]` lists field-level problems (`pointer` is a JSON Pointer into the request) or every rule broken. For example, a visit that breaks two hard blocks returns both.
- Problem documents never contain client names, dates of birth, addresses, Medicaid IDs, diagnoses or medication names. They may contain times, counts and opaque record numbers. They are not logged beyond `code`, `status` and `requestId`.

### 8.1 Status code usage

| Status | When |
|---|---|
| 400 | Malformed JSON, schema validation failure, unknown property, invalid cursor, PHI in the query string, invalid webhook signature |
| 401 | Missing, expired or revoked token; wrong credentials or MFA code at sign-in |
| 403 | Authenticated, but not allowed: missing permission, location out of scope, MFA required, tenant `ReadOnly`, support grant read-only or expired, account locked |
| 404 | Not found, or not visible to the caller. Records of other tenants always return 404, never 403, so their existence is not revealed. |
| 409 | The resource's current state does not allow the command (already issued, already claimed, locked period, discharged), or a duplicate exists, or the same Idempotency-Key is in flight |
| 412 | The `If-Match` value is stale |
| 422 | A well-formed request breaks a business rule (scheduling hard block, PRN limit, missing reason), or an Idempotency-Key was reused with a different body |
| 428 | `If-Match` is required but missing |
| 429 | Rate limit exceeded (section 11) |
| 500 / 503 | Unexpected error, or planned maintenance (`503` with `Retry-After`). Clients retry with backoff and quote `requestId` to support. |

### 8.2 Error code catalog

The HTTP status for warnings is "200 (warning)": warnings are returned as `ComplianceFinding` items with `severity: Warning` and do not fail the request.

| Code | HTTP | Meaning | User-facing message | Ref |
|---|---|---|---|---|
| **Platform** | | | | |
| API_VALIDATION_FAILED | 400 | Body, path or query fails schema validation | Fix the highlighted fields and try again. | NFR-USE-03 |
| API_CURSOR_INVALID | 400 | Pagination cursor expired, tampered or mismatched to the filters | The list was refreshed. Start again from the first page. | NFR-SCL-01 |
| API_PHI_IN_QUERY_REJECTED | 400 | A query parameter carries a PHI field | Search by client number, or open the client list and filter there. | NFR-PRIV-01, BR-011 |
| API_IDEMPOTENCY_KEY_REQUIRED | 400 | `Idempotency-Key` missing on an operation that requires it | Something went wrong sending this request. Try again. | BR-050 |
| API_IDEMPOTENCY_KEY_REUSED | 422 | Same key sent with a different body | This request key was already used for different data. Start a new request. | BR-050 |
| API_IDEMPOTENCY_REQUEST_IN_PROGRESS | 409 | First request with the same key still running | Your earlier request is still being processed. Wait a few seconds and try again. | BR-050 |
| API_RESOURCE_NOT_FOUND | 404 | Record missing or not visible | We could not find that record. It may have been removed or you may not have access to it. | BR-001 |
| API_PRECONDITION_FAILED | 412 | Stale `If-Match` | Someone else saved a change to this record. Reload it, review the changes and try again. | FR-SCH-04 |
| API_PRECONDITION_REQUIRED | 428 | `If-Match` missing | Reload the record and try again. | FR-SCH-04 |
| API_RATE_LIMITED | 429 | Rate limit exceeded | You are sending requests too quickly. Wait a moment and try again. | NFR-AVL-01 |
| API_SERVICE_UNAVAILABLE | 503 | Planned maintenance or overload | Tendwell is briefly unavailable. Clock-ins are saved on your phone and will sync automatically. | NFR-AVL-01, NFR-AVL-02 |
| **Identity and access** | | | | |
| IAM_UNAUTHENTICATED | 401 | Token missing or expired | Your session has ended. Sign in again to continue. | FR-IAM-04 |
| IAM_INVALID_CREDENTIALS | 401 | Email or password wrong (same response for unknown email) | Email or password is incorrect. After 5 failed attempts your account is locked for 15 minutes. | FR-IAM-01, FR-IAM-03 |
| IAM_ACCOUNT_LOCKED | 403 | 5 consecutive failures; locked for 15 minutes | Too many failed sign-in attempts. Try again after 15 minutes or reset your password. | FR-IAM-03 |
| IAM_MFA_REQUIRED | 403 | Role requires MFA and the session has no second factor | Your role requires two-step verification. Set it up, then sign in again. | BR-006 |
| IAM_MFA_CODE_INVALID | 401 | Wrong TOTP or SMS code | The code is not correct. Enter the current 6-digit code. | FR-IAM-01 |
| IAM_MFA_CHALLENGE_EXPIRED | 401 | MFA challenge older than 5 minutes | The sign-in attempt timed out. Sign in again to get a new code. | FR-IAM-01 |
| IAM_REFRESH_TOKEN_INVALID | 401 | Refresh token reused, revoked or past the 12-hour mobile limit | Your session has ended. Sign in again to continue. | FR-IAM-04 |
| IAM_SESSION_EXPIRED | 401 | Web idle timeout (15 minutes) reached | You were signed out after 15 minutes of inactivity. Sign in again. | FR-IAM-04 |
| IAM_PASSWORD_POLICY_VIOLATION | 422 | Shorter than 12 characters or found in a breach list | Use at least 12 characters, and avoid passwords that have appeared in a data breach. | BR-007 |
| IAM_RESET_TOKEN_INVALID | 422 | Reset link expired (30 minutes) or already used | This reset link is no longer valid. Request a new link. | FR-IAM-02 |
| IAM_PERMISSION_DENIED | 403 | Effective permissions lack the operation's permission | Your role does not allow this action. Ask your Agency Administrator if you need access. | FR-IAM-06, BR-005 |
| IAM_LOCATION_OUT_OF_SCOPE | 403 | Write references a location the user is not assigned to | You can only work with records for your assigned locations. | FR-IAM-06 |
| IAM_EMAIL_IN_USE | 409 | Email already belongs to an account | This email already has an account. Use a different email. | FR-IAM-05 |
| IAM_LAST_ADMINISTRATOR | 422 | Change would leave no active Agency Administrator | Your agency needs at least one administrator. Assign the role to someone else first. | FR-IAM-05 |
| IAM_UNKNOWN_PERMISSION | 422 | Override names a permission that does not exist | One of the permissions does not exist. Choose permissions from the list. | FR-IAM-05 |
| IAM_SUPPORT_GRANT_DURATION_EXCEEDED | 422 | Requested more than 240 minutes | Support access is limited to 4 hours. | BR-008 |
| IAM_SUPPORT_GRANT_ALREADY_ACTIVE | 409 | A grant is already requested or active for the tenant | A support session is already open for this agency. | FR-IAM-07 |
| IAM_SUPPORT_GRANT_NOT_PENDING | 409 | Approving a grant that is not `Requested` | This request was already handled. | FR-IAM-07 |
| IAM_SUPPORT_GRANT_NOT_ACTIVE | 409 | Revoking a grant that has ended | This support session has already ended. | FR-IAM-07 |
| IAM_SUPPORT_GRANT_READ_ONLY | 403 | Write attempted under a `ReadOnly` grant | This support session is read-only. | BR-008 |
| IAM_SUPPORT_GRANT_EXPIRED | 403 | Grant expired or revoked mid-session | Your support access has ended. Request access again if needed. | BR-008 |
| **Tenancy and onboarding** | | | | |
| TEN_READ_ONLY | 403 | Tenant is `ReadOnly`; writes other than care-critical ones are refused | Your agency account is read-only because the trial ended or a payment is overdue. You can view and export data. Clock-in and clock-out still work. | BR-003, FR-ONB-07 |
| ONB_PROMO_CODE_INVALID | 422 | Code does not exist or is retired | We do not recognize this code. Check the spelling or remove it. | FR-ONB-03 |
| ONB_PROMO_CODE_EXPIRED | 422 | Code past `expires_at` | This code has expired. Remove it or enter a different code. | FR-ONB-03, BR-004 |
| ONB_PROMO_CODE_EXHAUSTED | 422 | Redemption cap reached | This code has reached its limit. Remove it or enter a different code. | BR-004 |
| ONB_PROMO_CODE_NOT_ELIGIBLE | 422 | Code not valid for the selected plan | This code does not apply to the selected plan. | BR-004 |
| ONB_PROMO_CODE_EXISTS | 409 | Platform: code already defined | This code already exists. Choose a different code. | FR-ONB-08 |
| ONB_PLAN_CODE_EXISTS | 409 | Platform: plan code already defined | A plan with this code already exists. | FR-ONB-08 |
| ONB_PLAN_RETIRED | 422 | Selecting a retired plan for a new subscription or a plan change | This plan is no longer offered. Choose one of the current plans. | FR-ONB-08 |
| ONB_VERIFICATION_LINK_EXPIRED | 422 | Email verification link older than 24 hours or used | This verification link has expired. Request a new link. | FR-ONB-02 |
| ONB_SEATS_BELOW_ACTIVE | 422 | Seat decrease below active seats this cycle | Choose at least as many seats as you have active clients this month. | BR-002 |
| **Clients** | | | | |
| CLI_POSSIBLE_DUPLICATE | 409 | Same name and date of birth, or same Medicaid ID | This client may already exist. Open the existing record, or confirm this is a different person. | FR-CLI-02 |
| CLI_ADDRESS_NOT_GEOCODED | 422 | Address could not be geocoded | We could not locate this address. Check the street, city and ZIP code. | FR-CLI-01, BR-021 |
| CLI_PHI_REVEAL_REASON_REQUIRED | 422 | Reveal without a reason of 10 or more characters | Enter why you need to see this information. The reason is recorded. | FR-CLI-06, BR-011 |
| CLI_CLIENT_DISCHARGED | 409 | Write to a discharged (read-only) client | This client has been discharged, so the record is read-only. | BR-013 |
| CLI_DISCHARGE_DATE_INVALID | 422 | Discharge date before admission | Choose a discharge date on or after the admission date. | FR-CLI-07 |
| CLI_AUTHORIZATION_OVERLAP | 409 | Overlapping active authorization for the same payer and service | Another active authorization covers these dates. Adjust the dates or suspend it. | BR-009 |
| CLI_AUTHORIZATION_PERIOD_INVALID | 422 | End date before start date | The end date must be on or after the start date. | FR-CLI-03 |
| CLI_UNIT_TYPE_MISMATCH | 422 | Unit type inconsistent with the billing model | Hourly uses 15-minute units, Daily uses days, Per visit uses visits and Fixed monthly uses months. | FR-CLI-03 |
| CLI_CARE_PLAN_PENDING_EXISTS | 409 | A version is already pending approval | A care plan version is waiting for approval. Ask the Clinical Supervisor to review it first. | BR-012 |
| CLI_CARE_PLAN_NOT_PENDING | 409 | Approving a version that is not pending | This version is not waiting for approval. | BR-012 |
| **Workforce** | | | | |
| WRK_EMPLOYEE_NUMBER_EXISTS | 409 | Employee number already used in the tenant | This employee number is already used. Check the number from your payroll system. | FR-WRK-01 |
| WRK_CREDENTIAL_DATES_INVALID | 422 | Expiry on or before issue date | The expiry date must be after the issue date. | FR-WRK-02 |
| WRK_CAREGIVER_INACTIVE | 409 | Action on an inactive caregiver | This caregiver is inactive. | FR-WRK-06 |
| **Scheduling** | | | | |
| SCH_CAREGIVER_OVERLAP | 422 | Caregiver already has an overlapping visit (hard block) | The caregiver already has a visit at this time. Choose a different time or caregiver. | BR-016 |
| SCH_TRAVEL_BUFFER_SHORT | 200 (warning) | Less than 15 minutes between visits at different addresses | Only a few minutes between visits. Allow at least 15 minutes, or confirm to keep this time. | BR-016 |
| SCH_BLOCKING_CREDENTIAL_EXPIRED | 422 | Caregiver has an expired blocking credential (hard block) | This caregiver's required credential has expired. Choose another caregiver or record the renewal. | BR-014, FR-WRK-03 |
| SCH_CLIENT_EXCLUSION | 422 | Client excluded this caregiver (hard block) | This client has declined this caregiver. Choose another caregiver. | BR-017 |
| SCH_AUTHORIZATION_EXPIRED | 422 | Authorization expired for the visit date (hard block) | The authorization has expired. Select a current one or record the renewal first. | BR-010 |
| SCH_AUTHORIZATION_NOT_COVERING | 422 | No active authorization for the date and service line (hard block) | No active authorization covers this date and service. Record or select one first. | BR-009 |
| SCH_AUTHORIZATION_UNITS_EXCEEDED | 200 (warning) | Visit needs more units than remain; override reason required | This visit uses more units than remain on the authorization. Enter a reason to continue. | BR-010 |
| SCH_OVERRIDE_REASON_REQUIRED | 422 | Units warning acknowledged without a reason | Enter a reason to schedule beyond the authorization, or shorten the visit. | BR-010 |
| SCH_CAREGIVER_ON_TIME_OFF | 422 | Caregiver has approved time off (hard block) | The caregiver has approved time off on this date. Choose another caregiver. | BR-039 |
| SCH_CANCEL_REASON_REQUIRED | 422 | Cancellation without a reason code | Select a reason to cancel this visit. | FR-SCH-04 |
| SCH_VISIT_ALREADY_STARTED | 409 | Editing or cancelling a visit that has started | This visit has already started. Use a time correction instead. | BR-018, BR-019 |
| SCH_OPEN_SHIFT_ALREADY_CLAIMED | 409 | Another caregiver claimed first | Someone else claimed this shift first. Check the list for other shifts. | FR-SCH-05 |
| SCH_NOT_ELIGIBLE_FOR_SHIFT | 422 | Claimant fails a compliance check | You cannot take this shift. It conflicts with your schedule or requirements. | FR-SCH-05 |
| SCH_DATE_RANGE_TOO_LARGE | 400 | Visit list range over 31 days | Choose a range of 31 days or less. | FR-SCH-06 |
| **EVV** | | | | |
| EVV_VISIT_NOT_ASSIGNED | 403 | Punch on a visit not assigned to the caller | You can only clock in to your own visits. Contact the office if this visit should be yours. | FR-EVV-01 |
| EVV_CLOCK_IN_WINDOW_NOT_OPEN | 422 | More than 15 minutes before the scheduled start | It is too early to clock in. Clock-in opens 15 minutes before the start time. | BR-023 |
| EVV_CLOCK_IN_WINDOW_CLOSED | 422 | After the scheduled end | This visit has ended. Ask the office to record it. | FR-EVV-01 |
| EVV_ALREADY_CLOCKED_IN | 409 | Second clock-in with a different `punchId` | You are already clocked in to this visit. | FR-EVV-01 |
| EVV_NOT_CLOCKED_IN | 409 | Clock-out with no clock-in | You have not clocked in. If you forgot, ask the office to add the time. | FR-EVV-06 |
| EVV_IDENTITY_CHECK_REQUIRED | 422 | Tenant requires a check and none was sent | Take a quick selfie to clock in. | FR-EVV-04 |
| EVV_IDENTITY_CHECK_EXPIRED | 422 | Check older than 90 seconds | Your selfie check has expired. Take a new selfie and clock in right away. | BR-024 |
| EVV_IDENTITY_CHECK_ALREADY_USED | 422 | Check already consumed by a punch | Each selfie check works once. Take a new selfie. | BR-024 |
| EVV_IDENTITY_NOT_ENROLLED | 422 | Caregiver has no enrolled reference | Ask the office to set up your reference photo. | FR-EVV-04 |
| EVV_TASK_STATUS_REQUIRED | 422 | A care plan task has no status at clock-out | Mark each task as Done or Not done before clocking out. | FR-EVV-06 |
| EVV_TASK_REASON_REQUIRED | 422 | Not done without a reason | Add a reason for each task marked Not done. | FR-EVV-06 |
| EVV_VISIT_NOTE_REQUIRED | 422 | Care plan requires a note | Add a short visit note, then clock out. | FR-EVV-06, BR-012 |
| EVV_DEVICE_TIME_INVALID | 422 (per sync item) | Capture time later than server time plus 5 minutes of skew | Your phone's date and time look wrong. Check the settings; the office will record this punch. | BR-025 |
| EVV_SYNC_BATCH_TOO_LARGE | 400 | More than 200 punches in a batch | Upload at most 200 punches at a time. The app splits larger queues automatically. | FR-EVV-05, NFR-AVL-02 |
| EVV_EXCEPTION_ALREADY_RESOLVED | 409 | Resolving a closed exception | This exception is already resolved. | FR-EVV-08 |
| EVV_REASON_CODE_INVALID | 422 | Reason code not in the tenant's active list | Choose a reason from the list. | FR-EVV-08 |
| EVV_CORRECTION_REQUIRED | 422 | `AUTO_CLOSED` or `MISSING_CLOCK_OUT` resolved without a time correction | Record the actual end time with a time correction first. | BR-027 |
| EVV_CORRECTION_REASON_REQUIRED | 422 | Correction without a reason code and note | Choose a reason and describe how the time was confirmed. | BR-026 |
| EVV_CORRECTION_TIME_INVALID | 422 | Corrected time out of order or in the future | The clock-out time must be after the clock-in time and not in the future. | FR-EVV-08 |
| **eMAR and vitals** | | | | |
| MAR_WINDOW_OUT_OF_RANGE | 422 | Window outside 15-120 minutes | The administration window must be 15 to 120 minutes. | BR-029 |
| MAR_PRN_LIMITS_REQUIRED | 422 | PRN order missing indication, 24-hour maximum or interval | Enter the indication, the maximum doses in 24 hours and the minimum interval. | FR-MAR-05 |
| MAR_ORDER_NOT_PENDING | 409 | Approving an order that is not pending | This order is not waiting for approval. | FR-MAR-01 |
| MAR_ORDER_NOT_ACTIVE | 409 | Discontinuing or dosing against an inactive order | This order is not active. | FR-MAR-01 |
| MAR_REASON_REQUIRED | 422 | Refused, Held or Not available without a reason | A reason is required when a dose is refused, held or not available. | BR-032, FR-MAR-03 |
| MAR_DOSE_ALREADY_RECORDED | 409 | Dose already has an outcome | This dose was already recorded. Ask the Clinical Supervisor to annotate it if it is wrong. | BR-031 |
| MAR_LATE_ENTRY_WINDOW_EXPIRED | 422 | More than 24 hours after the scheduled time | Doses can be recorded up to 24 hours late. Ask the Clinical Supervisor to add an annotation. | BR-031 |
| MAR_PRN_INDICATION_REQUIRED | 422 | PRN dose without an indication | Describe the symptom before giving an as-needed dose. | FR-MAR-05 |
| MAR_PRN_MAX_DOSES_EXCEEDED | 422 | Would exceed the maximum in any rolling 24 hours | The maximum doses for 24 hours have been given. The message shows when the next dose is allowed. | BR-033 |
| MAR_PRN_MIN_INTERVAL_NOT_MET | 422 | Inside the minimum interval since the last PRN dose | It is too soon since the last dose. The message shows when the next dose is allowed. | BR-033 |
| MAR_NOT_PRN_ORDER | 422 | PRN administration against a scheduled order | This is a scheduled medication. Record it from the dose list. | FR-MAR-05 |
| **Documentation** | | | | |
| DOC_NOTE_LOCKED | 409 | Editing a note more than 24 hours after clock-out | This note is locked. Add an addendum instead. | BR-035, FR-DOC-02 |
| DOC_NOTE_NOT_LOCKED | 409 | Addendum on a note that is still editable | This note can still be edited. Edit it directly until it locks. | BR-035 |
| DOC_SIGNATURE_REQUIRED | 422 | Addendum without an electronic signature | Re-enter your password and confirm the attestation to sign. | BR-035 |
| DOC_INCIDENT_ACTIONS_OPEN | 409 | Closing with open corrective actions | Corrective actions are still open. Mark them Done or waive them with a reason first. | BR-037 |
| DOC_WAIVER_REASON_REQUIRED | 422 | Waiving an action without a reason | Explain why the corrective action is not needed. | BR-037 |
| DOC_INCIDENT_CLOSED | 409 | Changing a closed incident | This incident is closed and read-only. | FR-DOC-05 |
| **Time off** | | | | |
| TOF_DATES_INVALID | 422 | End before start, or partial hours on a multi-day request | Check the dates. Partial hours apply to single-day requests only. | FR-TOF-01 |
| TOF_OVERLAPPING_REQUEST | 409 | Overlaps an existing pending or approved request | You already have a request for these dates. | FR-TOF-01 |
| TOF_INSUFFICIENT_BALANCE | 422 | PTO request exceeds the balance | Not enough PTO. Shorten the request or choose Unpaid. | FR-TOF-04, BR-040 |
| TOF_REQUEST_ALREADY_DECIDED | 409 | Deciding twice | This request was already decided. | FR-TOF-03 |
| TOF_HOLIDAY_EXISTS | 409 | Holiday already on that date | This date is already a holiday. | FR-TOF-05 |
| **Payroll** | | | | |
| PAY_PERIOD_LOCKED | 409 | Change that would alter a locked (exported) period | That date is in a pay period that has been exported. Changes are paid as adjustments in the next open period. | BR-046, FR-PAY-06 |
| PAY_EXPORT_HAS_OPEN_ISSUES | 422 | Export while the pre-export review lists issues, without acknowledgement | Some visits still need review. Resolve them, or confirm the export and they will be paid later. | FR-PAY-04 |
| PAY_COLUMN_MAPPING_INVALID | 422 | Required export columns not mapped | Map the required columns in Payroll settings, then export again. | FR-PAY-05 |
| **Billing** | | | | |
| BIL_RUN_IN_PROGRESS | 409 | A run for the tenant and period is already running (single-flight) | A billing run for this period is already running. Wait for it to finish. | BR-050, CR-005 |
| BIL_INVOICE_IMMUTABLE | 409 | Change to an issued invoice | This invoice has been issued and cannot change. Issue a credit note, or void and reissue it if unpaid. | BR-051, FR-BIL-04 |
| BIL_INVALID_STATUS_TRANSITION | 409 | Command not valid for the invoice's status | This action is not available for the invoice's current status. | FR-BIL-04 |
| BIL_DUPLICATE_INVOICE_SUSPECTED | 409 | Pre-issue check found another non-void invoice for the same client, payer and period | A matching invoice already exists. Void one of them before issuing. | BR-050, CR-005 |
| BIL_INVOICE_HAS_PAYMENTS | 409 | Voiding an invoice with payments | Invoices with payments cannot be voided. Issue a credit note instead. | BR-051 |
| BIL_INVOICE_NOT_ISSUED | 409 | Credit note against an invoice that is not issued | Credit notes apply to issued invoices. | FR-BIL-07 |
| BIL_CREDIT_EXCEEDS_BALANCE | 422 | Credit larger than the balance | The credit is larger than the balance. Enter a smaller amount. | FR-BIL-07 |
| BIL_PAYMENT_LINK_NOT_PRIVATE_PAY | 422 | Payment link for a non-private-pay invoice | Payment links are for private-pay invoices. Submit this one in a claim batch. | FR-BIL-05 |
| BIL_CLAIM_BATCH_EMPTY | 422 | No billable lines for the payer and period | There is nothing to submit for this payer and period. | FR-BIL-06 |
| BIL_WEBHOOK_SIGNATURE_INVALID | 400 | Payment webhook signature or timestamp check failed (machine-to-machine) | Not shown to users. | FR-BIL-05 |
| **Notifications** | | | | |
| NTF_CHANNEL_NOT_ALLOWED | 422 | Preferences would silence an urgent event type | Keep Push or SMS on for urgent alerts so you are alerted right away. | BR-053, FR-NTF-02 |
| NTF_LADDER_INVALID_STEP | 422 | Step delays not increasing, or more than 5 steps | Each step must start later than the one before it. | FR-NTF-03 |
| NTF_RECIPIENT_MUST_BE_ROLE | 422 | Ladder step names a user instead of a role | Escalations go to roles. People are picked automatically when the alert is sent. | BR-054, CR-006 |
| **Reporting** | | | | |
| RPT_DATE_RANGE_TOO_LARGE | 422 | Report or audit export over 366 days | Choose a range of 366 days or less. | FR-RPT-02, FR-RPT-03 |
| **Family portal (Release 2)** | | | | |
| FAM_CONSENT_NOT_RECORDED | 403 | No recorded client consent for this family contact | The agency has not set up your access yet. Contact the agency. | FR-FAM-01 |

## 9. Idempotency

| Topic | Rule |
|---|---|
| Header | `Idempotency-Key: <client-generated value, 8-128 characters; a UUID is recommended>` on unsafe `POST` requests. |
| Required on | Operations that move money, create files or create tenants: `POST /signups`, `POST /billing-runs`, `POST /pay-periods/{periodId}/exports`, `POST /invoices/{invoiceId}/payment-links`, `POST /invoices/{invoiceId}/credit-notes`, `POST /claim-batches`. A missing key returns `400 API_IDEMPOTENCY_KEY_REQUIRED`. |
| Optional on | All other create and command `POST` operations. Clients should always send one. |
| Natural keys instead | EVV punches use the client-generated `punchId` in the body, so online retries and offline sync of the same punch converge (FR-EVV-05). The payment webhook uses the provider event `id`. Neither needs the header. `POST /visits/compliance-checks` and the auth endpoints have no side effects to repeat. |
| Scope | The key is scoped to tenant + user + method + route template. The same key on a different route is a different request. |
| Retention | The first completed response (status, headers, body) is stored for **24 hours**. Retries within 24 hours return the stored response with `Idempotent-Replayed: true`. |
| Same key, different body | The canonical JSON body is hashed. A mismatch returns **`422 API_IDEMPOTENCY_KEY_REUSED`**, and nothing is executed. |
| Concurrent retry | When the first request is still running, the retry gets `409 API_IDEMPOTENCY_REQUEST_IN_PROGRESS`; the client retries after `Retry-After`. |
| Failures | `5xx` and `429` responses are not stored, so the client can retry with the same key. `4xx` business errors are stored and replayed. |
| Defense in depth | The API key store is not the only guard. Database unique keys back the critical writes: `invoices.idempotency_key` (CR-005), `evv_punches.id`, `payments.provider_ref`, `job_executions.idempotency_key` and `notifications.dedupe_key`. INC-2026-007 showed that an application-level check-then-insert is not enough under concurrency. |
| Client retry policy | Exponential backoff with full jitter (1, 2, 4, 8 seconds, then a 60-second cap). Always reuse the same key or `punchId` for a retry. |

## 10. Optimistic concurrency

- `GET` of a single mutable resource returns a strong `ETag`: the quoted `row_version`, for example `"4"`. Write responses return the new `ETag`.
- These operations **require** `If-Match`:
  - every `PATCH`;
  - the versioned `PUT` operations (`/users/{userId}/roles`, `/users/{userId}/permission-overrides`, `/caregivers/{caregiverId}/pay-profiles`, `/clients/{clientId}/vital-ranges`, `/escalation-ladders/{eventType}`);
  - the state commands on invoices (`approve`, `issue`, `void`), care plans (`approve`) and incidents (`close`).
- A stale value returns **`412 API_PRECONDITION_FAILED`** with the current `ETag`. A missing header returns `428 API_PRECONDITION_REQUIRED`.
- The UI handles `412` by reloading the record, showing what changed, and asking the user to re-apply the edit. Coordinators editing the same schedule board is the common case.
- `PUT /me/notification-preferences` is the one replacement without `If-Match`. It is the caller's own data, so last write wins.

## 11. Rate limits

Limits are enforced per caller and route class at the edge (WAF) and in the API (Redis token bucket). Every response carries `RateLimit-Limit`, `RateLimit-Remaining` and `RateLimit-Reset`. A `429` also carries `Retry-After`.

| Client type or role | Scope | Sustained limit | Burst | Notes |
|---|---|---|---|---|
| Public auth and sign-up (no token) | Per IP | 20 requests/min | 10 | Also 10 login attempts per email per 15 minutes, on top of account lockout (FR-IAM-03). `POST /auth/password/forgot` is limited to 5 per hour per email and IP. |
| Caregiver mobile app (`CG`) | Per user | 120 requests/min | 30 | Clock-in, clock-out, identity checks and dose outcomes draw on reserved capacity and are excluded from tenant-wide limits, so care is never throttled. |
| Offline sync (`POST /evv/punches/sync`) | Per device | 30 requests/min | 10 | At most 200 punches per batch. 72 hours of punches drain in a few calls (NFR-AVL-02). |
| Agency web app (`AG-ADM`, `AG-COORD`, `AG-SUPV`, `AG-FIN`) | Per user | 600 requests/min | 100 | Schedule board polling counts here. |
| Agency tenant total | Per tenant | 6,000 requests/min | 1,000 | Protects other tenants on the shared cluster (NFR-PERF-01). |
| Reports and exports (`/reports/*` with CSV or PDF, `/audit-events/exports`, payroll exports, claim batches) | Per user | 10 exports/hour; 60 report runs/hour | 5 | Exports are heavy and audited. |
| PHI reveals (`POST /clients/{clientId}/phi-reveals`) | Per user | 30/hour | 10 | A spike raises a security alert to the Compliance and Privacy Officer. |
| Platform Console (`PLT-ADM`, `PLT-SUP`) | Per user | 300 requests/min | 50 | A support session under a grant is limited to 120 requests/min. |
| Payment webhook | Per endpoint | 100 requests/s | 200 | Also restricted to the provider's published IP ranges. |
| Family portal (`FAM`, Release 2) | Per user | 60 requests/min | 20 | |

## 12. Authentication and authorization

### 12.1 Authentication

- Sign-in uses a managed OIDC identity provider behind `POST /auth/login` and `POST /auth/mfa/verify`.
- MFA (TOTP or SMS) is mandatory for `AG-ADM`, `AG-SUPV`, `AG-FIN` and all platform roles (BR-006). A token without `mfa` in `amr` for one of these roles gets `403 IAM_MFA_REQUIRED`.
- Access tokens are JWTs signed with RS256 and valid for **15 minutes**. Refresh tokens are opaque and rotate on every use; reusing one revokes the whole token family.
- Web sessions end after 15 minutes idle. Mobile sessions require device PIN or biometrics after 12 hours (FR-IAM-04).
- Deactivation and logout add the session ID (`sid`) to a deny-list that is checked on every request. A revoked session stops working immediately, not when the token expires (FR-WRK-06).

**Access token claims**

| Claim | Example | Meaning |
|---|---|---|
| `iss` | `https://auth.tendwell.example/` | Issuer |
| `sub` | `3d9b6c3a-5b2e-4f14-a7e2-c0000000a001` | User ID |
| `aud` | `https://api.tendwell.example` | Audience |
| `iat`, `exp` | `1790942400`, `1790943300` | Issued at and expiry (15 minutes) |
| `jti` | `0f4c2e8a-...` | Token ID |
| `sid` | `5b7d...` | Session ID, checked against the revocation deny-list |
| `tenant_id` | `7c1e4a52-3b9d-4f0e-9a61-2d8f5b3c1a01` | Tenant. The API sets `app.tenant_id` for row-level security from this claim (BR-001). `null` for platform users outside a support grant. |
| `roles` | `["AG-COORD"]` | Role codes |
| `locations` | `["1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c01"]` | Assigned location IDs used for location scoping (FR-IAM-06) |
| `amr` | `["pwd","mfa"]` | Authentication methods used |
| `client_type` | `Web`, `Mobile` or `Console` | Drives session and rate-limit policy |
| `device_id` | `and-5f2c9e81b7a4` | Mobile only; used for remote wipe and EVV punches |
| `support_grant_id` | `f0e1d2c3-...` | Present only on grant-scoped support tokens (BR-008) |

```json
{
  "iss": "https://auth.tendwell.example/",
  "sub": "3d9b6c3a-5b2e-4f14-a7e2-c0000000a001",
  "aud": "https://api.tendwell.example",
  "iat": 1790942400,
  "exp": 1790943300,
  "jti": "0f4c2e8a-6d1b-4a3e-9c5f-7b2d8e1a4c60",
  "sid": "5b7d9e1f-3a2c-4e6b-8d0f-1c3e5a7b9d21",
  "tenant_id": "7c1e4a52-3b9d-4f0e-9a61-2d8f5b3c1a01",
  "roles": ["AG-COORD"],
  "locations": ["1a2b3c4d-5e6f-4a7b-8c9d-0e1f2a3b4c01"],
  "amr": ["pwd"],
  "client_type": "Web"
}
```

### 12.2 Authorization

- **Permission strings.** Permissions are `resource:action` strings in lowercase snake_case, for example `clients:read`, `clients:reveal_phi` and `invoices:issue`. Each operation declares exactly one permission in `x-permission`. Public operations declare `public:anonymous`, and the payment webhook declares `webhooks:receive_payments`.
- **Evaluated on every request, not stored in the token.** Effective permissions = role template permissions + Grant overrides - Deny overrides; a Deny always wins (BR-005). They are cached per user for 60 seconds and invalidated at once when roles or overrides change, so a change does not wait for token expiry. The default is deny (NFR-SEC-04).
- **Three layers on every request.**
  1. The tenant: RLS on `tenant_id`, which the database enforces.
  2. The permission.
  3. The location scope: the record's location must be in the `locations` claim, checked against `user_locations`.

  A record that fails layer 1 or 3 returns `404`. A missing permission returns `403`.
- **Ownership rules.** Caregivers act only on their own visits, dose tasks, time-off requests, leave balances and credentials. The API derives "own" from `sub`, never from a request field.
- **Read-only tenants (BR-003).** All writes return `403 TEN_READ_ONLY` except:
  - auth;
  - `PATCH /subscription`, so the agency can restore payment;
  - `/me/*`;
  - care-critical operations: identity checks, clock-in, clock-out, offline sync, dose outcomes, PRN doses, vital readings, visit notes and incident reports;
  - exports.
- **Support access (BR-008).** An approved grant lets a `PLT-SUP` user exchange their platform token for a grant-scoped token. That token carries:
  - `tenant_id` set to the target tenant;
  - `support_grant_id`;
  - an expiry of the earlier of 15 minutes or the grant's `expiresAt`.

  Writes under a `ReadOnly` grant return `403 IAM_SUPPORT_GRANT_READ_ONLY`. Every action is audited with the grant ID.

### 12.3 Default permission matrix

The default role templates provisioned for each tenant (FR-ONB-04) hold the permissions below. Agency Administrators can change any user's effective permissions with overrides (FR-IAM-05).

| Permission | Default role templates | Operations |
|---|---|---|
| `subscription:read`, `subscription:update` | AG-ADM | `GET`, `PATCH /subscription` |
| `platform_plans:read` / `:create` / `:update` | PLT-ADM | `/platform/plans` |
| `platform_promo_codes:create` / `:update` | PLT-ADM | `/platform/promo-codes` |
| `users:read`, `users:create`, `users:update`, `users:assign_roles`, `users:manage_overrides` | AG-ADM | `/users/*` |
| `support_access:request` | PLT-SUP | `POST /support-access-grants` |
| `support_access:approve`, `support_access:revoke` | AG-ADM | `/support-access-grants/{grantId}/approve`, `/revoke` |
| `clients:read` | AG-ADM, AG-COORD, AG-SUPV, AG-FIN | `GET /clients`, `GET /clients/{clientId}` |
| `clients:create`, `clients:update` | AG-ADM, AG-COORD | `POST /clients`, `PATCH /clients/{clientId}` |
| `clients:reveal_phi` | AG-ADM, AG-COORD, AG-SUPV | `POST /clients/{clientId}/phi-reveals` |
| `clients:discharge` | AG-COORD | `POST /clients/{clientId}/discharge` |
| `authorizations:read` | AG-ADM, AG-COORD, AG-FIN | `GET /clients/{clientId}/authorizations` |
| `authorizations:create` | AG-COORD, AG-FIN | `POST /clients/{clientId}/authorizations` |
| `care_plans:create` | AG-COORD, AG-SUPV | `POST /clients/{clientId}/care-plans` |
| `care_plans:approve` | AG-SUPV | `POST /care-plans/{carePlanId}/approve` |
| `caregivers:read` | AG-ADM, AG-COORD, AG-SUPV, AG-FIN | `GET /caregivers` |
| `caregivers:create`, `caregivers:update` | AG-ADM, AG-COORD | `POST /caregivers`, `PATCH /caregivers/{caregiverId}` |
| `caregivers:deactivate` | AG-ADM | `POST /caregivers/{caregiverId}/deactivate` |
| `credentials:create` | AG-COORD, CG (own) | `POST /caregivers/{caregiverId}/credentials` |
| `credentials:read` | AG-ADM, AG-COORD | `GET /credentials` |
| `pay_profiles:update` | AG-ADM, AG-FIN | `PUT /caregivers/{caregiverId}/pay-profiles` |
| `visit_patterns:create` | AG-COORD | `POST /visit-patterns` |
| `visits:read` | AG-ADM, AG-COORD, AG-SUPV, AG-FIN, CG (own) | `GET /visits` |
| `visits:create` | AG-COORD | `POST /visits`, `POST /visits/compliance-checks` |
| `visits:update`, `visits:cancel` | AG-COORD | `PATCH /visits/{visitId}`, `POST /visits/{visitId}/cancel` |
| `open_shifts:read` | AG-COORD, CG | `GET /open-shifts` |
| `open_shifts:claim` | CG | `POST /visits/{visitId}/claim` |
| `evv:identity_check`, `evv:clock`, `evv:sync` | CG | Identity checks, clock-in, clock-out, offline sync |
| `visit_exceptions:read` | AG-ADM, AG-COORD, AG-SUPV | `GET /visit-exceptions` |
| `visit_exceptions:resolve`, `evv:correct_time` | AG-COORD | Resolve exceptions, time corrections |
| `medication_orders:create` | AG-COORD, AG-SUPV | `POST /clients/{clientId}/medication-orders` |
| `medication_orders:approve`, `medication_orders:discontinue` | AG-SUPV | Approve and discontinue orders |
| `dose_tasks:read` | AG-COORD, AG-SUPV, CG (own) | `GET /dose-tasks` |
| `dose_tasks:record`, `prn_administrations:create` | CG | Dose outcomes, PRN doses |
| `vital_readings:create` | AG-SUPV, CG | `POST /clients/{clientId}/vital-readings` |
| `vital_ranges:update` | AG-SUPV | `PUT /clients/{clientId}/vital-ranges` |
| `mar:read` | AG-COORD, AG-SUPV | `GET /clients/{clientId}/mar` |
| `visit_notes:create` | CG | `POST /visits/{visitId}/notes` |
| `note_addenda:create` | AG-SUPV, CG | `POST /visit-notes/{noteId}/addenda` |
| `incidents:create` | AG-COORD, CG | `POST /client-incidents` |
| `incidents:update`, `incident_actions:create`, `incidents:close` | AG-SUPV | Incident investigation and closure |
| `time_off_requests:create` | CG | `POST /time-off-requests` |
| `time_off_requests:decide` | AG-COORD | Impact preview and decision |
| `leave_balances:read` | AG-COORD, AG-FIN, CG (own) | `GET /caregivers/{caregiverId}/leave-balances` |
| `holidays:read` | All agency roles | `GET /holidays` |
| `holidays:create` | AG-ADM | `POST /holidays` |
| `pay_periods:read` | AG-ADM, AG-FIN | Pay periods, summary, pre-export review |
| `payroll:export` | AG-FIN | `POST /pay-periods/{periodId}/exports` |
| `billing_runs:create`, `invoices:approve`, `invoices:issue`, `invoices:void`, `payment_links:create`, `credit_notes:create`, `claim_batches:create` | AG-FIN | Billing commands |
| `invoices:read` | AG-ADM, AG-FIN | `GET /invoices`, `GET /invoices/{invoiceId}` |
| `notifications:read_own`, `notifications:manage_own` | All agency roles | `/me/notifications`, `/me/notification-preferences` |
| `escalation_ladders:read`, `escalation_ladders:update` | AG-ADM | `/escalation-ladders` |
| `reports:read_dashboard` | AG-ADM, AG-COORD, AG-SUPV | `GET /reports/operations-dashboard` |
| `reports:read` | AG-ADM, AG-COORD, AG-SUPV, AG-FIN | `GET /reports/{reportCode}` |
| `audit_events:read`, `audit_events:export` | AG-ADM | Audit search and export |
| `webhooks:receive_payments` | SYS (signature, no user) | `POST /webhooks/payments` |
| `family:read_visits`, `family:send_messages` | FAM (Release 2) | `/family/*` |

## 13. PHI handling in APIs

| Rule | Detail |
|---|---|
| **Masked by default** | The API masks client date of birth, Medicaid ID, phone, service address and diagnoses in every list and detail response (BR-011, NFR-PRIV-01). Responses set `phiMasked: true`. Lists show clients as first name and last initial (`clientDisplayName: "Evelyn M."`) where the full name is not needed. Mask formats are in [data classification and retention, section 3.1](../03-design/data/data-classification-and-retention.md#31-masking-rules). |
| **Reveal endpoint** | `POST /clients/{clientId}/phi-reveals` returns only the requested fields. It requires `clients:reveal_phi` and a reason of 10 or more characters. It writes an audit event with field names and reason, never the values (FR-CLI-06, BR-057), and is rate-limited (section 11). |
| **Treatment-time access** | Caregivers get the address, phone, allergies, tasks and due doses for their own assigned visits in the visit detail, from 24 hours before the start until the visit is Verified. This is minimum-necessary access by assignment, and it is audited as `visit.detail_viewed`. |
| **Never in URLs or query strings** | Paths and query strings carry only opaque UUIDs, enumerations, dates and agency record numbers such as `C-10234`. Names, date of birth, Medicaid ID, phone, address, diagnosis, medication and note text never appear there. URLs end up in proxy, CDN and browser logs, history and `Referer` headers. Searches that need PHI go in a `POST` body (the duplicate check in `POST /clients`). Violations return `400 API_PHI_IN_QUERY_REJECTED`. |
| **Caching** | Responses from `x-phi: true` operations send `Cache-Control: no-store` and `Pragma: no-cache`. The CDN never caches API responses. The mobile app keeps PHI only in the SQLCipher store (NFR-MOB-02). |
| **Logging** | Structured logs carry `requestId`, `tenantId`, `userId`, the route **template** (`/v1/clients/{clientId}`, never the raw URL), status, latency and the problem `code` (NFR-OBS-01). Bodies of `x-phi: true` operations are never logged. The logging library also redacts known field names (`firstName`, `lastName`, `dateOfBirth`, `medicaidId`, `phone`, `serviceAddress`, `lat`, `lng`, `narrative`, `description`, `reason`, `indication`). Error tracking scrubs PHI before data leaves the service. Traces carry IDs only. |
| **Errors** | Problem documents never contain client names, dates of birth, addresses, Medicaid IDs, diagnoses or medication names (section 8). |
| **Notifications and email** | Push, SMS and email bodies carry generic text and a deep link that requires sign-in (BR-056, CR-006). In-app notifications follow the same rule. |
| **Exports** | Every CSV or PDF is watermarked with user, tenant and timestamp (`X-Export-Watermark`), audited (BR-058) and delivered through a pre-signed link valid for 15 minutes. |
| **Non-production** | The sandbox and all test environments hold synthetic data only. Production PHI is never copied to them. |

## 14. Time zones and timestamps

- **Instants** are RFC 3339 strings in UTC with a `Z` suffix, for example `2026-09-08T12:56:10Z`. Requests may send an offset, which the API normalizes to UTC; responses always use `Z` (NFR-DAT-01).
- **Business dates** (`periodStart`, `dueDate`, `dateOfBirth`, holiday `date`) are `YYYY-MM-DD` with no time zone, interpreted in the tenant time zone. The samples use `America/New_York`.
- **Local times of day** in visit patterns and medication schedules (`startTime: "09:00"`, `scheduleTimes: ["08:00"]`) use the location's IANA time zone. Each occurrence is converted to UTC at materialization, so a 09:00 visit stays at 09:00 across daylight saving changes.
- **Durations** are computed from UTC instants. An overnight shift from 22:00 on 2026-10-31 to 07:00 on 2026-11-01 is 10 hours, because clocks fall back that night.
- **Device time versus server time.** EVV punches send `deviceCapturedAt`, which is kept as the punch time. The server records `receivedAt` separately (BR-025). A capture time more than 5 minutes ahead of server time is rejected with `EVV_DEVICE_TIME_INVALID`. A receipt more than 24 hours after capture raises `LATE_OFFLINE_SYNC`.
- **Display.** Clients display times in the tenant time zone. The API does not localize strings.

## 15. Webhook security

### 15.1 Inbound: payment provider (`POST /webhooks/payments`)

- **Authentication.** The request carries no bearer token. The `Stripe-Signature` header (`t=<unix time>,v1=<HMAC-SHA256>`) is verified against the endpoint secret over `<t>.<raw body>`, using a constant-time comparison, **before** the JSON is parsed.
- **Tolerance.** The timestamp tolerance is 5 minutes. Replays outside it are rejected with `400 BIL_WEBHOOK_SIGNATURE_INVALID`.
- **Idempotent processing.** Processing is keyed on the provider event `id`, recorded in `job_executions`. A replayed event returns `200` and changes nothing.
- **Order.** Order is not assumed. State transitions are monotonic, and the current object is re-read from the provider when an event is older than the state already applied.
- **Network and secrets.** Requests are accepted only from the provider's published IP ranges. Two secrets can be active during a rotation.
- **Response.** The endpoint returns `200` within 2 seconds and processes the event asynchronously.

Full design: [events and webhooks, section 7](events-and-webhooks.md#7-inbound-payment-webhook-handling).

### 15.2 Outbound: agency webhooks (Release 2)

Not available in Release 1. The planned design is:
- HMAC-SHA256 signatures in a `Tendwell-Signature` header with a timestamp;
- thin, PHI-minimized payloads;
- retries with backoff and a dead-letter view.

See [events and webhooks, section 8](events-and-webhooks.md#8-outbound-agency-webhooks-release-2).

## 16. Observability

- Every response carries `X-Request-Id`. Clients may send their own value. The API also accepts and propagates W3C `traceparent` for OpenTelemetry traces (NFR-OBS-01).
- Business anomaly alerts are emitted from the API layer (NFR-OBS-02). They fire when:
  - a billing run's invoice count deviates more than 20% from the previous run;
  - the EVV exception rate exceeds 2x its 7-day baseline;
  - any notification is addressed to a deactivated user.
- SLO burn-rate alerts are defined per route class. The targets are p95 read latency of 400 ms or less, p95 write latency of 800 ms or less, and p95 clock-in and clock-out of 2 s or less (NFR-PERF-01, NFR-PERF-02).

## 17. Contract governance

| Practice | Rule |
|---|---|
| Review | The BA and Engineering Lead review every contract change in a pull request. A change to a requirement-bearing operation updates `x-requirements` and the [requirements traceability matrix](../02-requirements/requirements-traceability-matrix.md). |
| Linting | CI lints the OpenAPI document. The build fails when:<ul><li>an operation lacks `operationId`, `x-requirements` or `x-permission`;</li><li>a property is not camelCase;</li><li>an error response does not use `Problem`;</li><li>a query parameter matches the PHI field list.</li></ul> |
| Breaking-change check | CI diffs the contract against the last release tag and blocks breaking changes in `/v1`. |
| Contract tests | Run from the [Postman collection](../06-quality/api-tests/tendwell.postman_collection.json) against the sandbox on every deployment. Responses are validated against the schemas. |
| Mocks | The mobile team develops against a mock server generated from the contract and its examples. |

## Related documents

- [OpenAPI specification](openapi.yaml)
- [Events and webhooks](events-and-webhooks.md)
- [Software requirements specification](../02-requirements/SRS.md)
- [Business rules catalog](../02-requirements/business-rules.md)
- [Non-functional requirements](../02-requirements/non-functional-requirements.md)
- [Data dictionary](../03-design/data/data-dictionary.md)
- [Data classification and retention](../03-design/data/data-classification-and-retention.md)
- [Deployment and security architecture](../03-design/architecture/deployment-and-security.md)
- [Sequence diagrams](../03-design/diagrams/sequence-diagrams.md)
- [Test strategy and plan](../06-quality/test-strategy-and-plan.md)
- [Change request log](../05-delivery/change-request-log.md)
