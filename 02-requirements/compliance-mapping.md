# Compliance Mapping: Tendwell

## Document control

| Field | Value |
|---|---|
| Document ID | TW-REQ-CMP |
| Version | 1.3 (aligned with SRS v1.3) |
| Status | Approved (baselined) |
| Owner | Business Analyst |
| Last updated | 2026-09-24 |
| Reviewers | Compliance and Privacy Officer; Engineering Lead; Clinical SME (RN advisor); QA Lead; Product Owner |

**Purpose and scope.** This document maps Tendwell's requirements and controls to the regulations and standards that shape them:
- the HIPAA Security Rule technical safeguards;
- the HIPAA Privacy Rule minimum-necessary standard;
- breach notification;
- 21st Century Cures Act EVV;
- the FLSA and the DOL Home Care Rule;
- WCAG 2.2 AA;
- NIST SP 800-63B.

For each obligation it shows the Tendwell control, the requirement IDs that implement it and what the agency remains responsible for. It is the input to the Compliance and Privacy Officer's reviews and to agency security questionnaires.

> **Disclaimer.** Tendwell is designed to support an agency's compliance. It does not make an agency compliant. The agency, as the covered entity and employer, remains responsible for its own policies, workforce, configuration choices, filings and determinations. This document is a requirements traceability artifact, not legal advice. Citations are summarized for readability; the regulation text is authoritative.

## 1. How to read this mapping

- **R / A** marks a HIPAA implementation specification as Required or Addressable. Addressable does not mean optional: the entity implements it, or documents why an equivalent alternative is reasonable. Tendwell implements every addressable specification listed here.
- **Tendwell control** is what the product and platform do. **Agency remains responsible for** is the part no software can do for the agency.
- HHS published proposed amendments to the Security Rule in January 2025 that would, among other things, remove the required/addressable distinction. The Compliance and Privacy Officer tracks the rulemaking. Because Tendwell already treats the addressable specifications below as required, no requirement change is expected.

## 2. HIPAA Security Rule: technical safeguards (45 CFR 164.312)

| Citation | Standard or implementation specification | R / A | Tendwell control | Requirement IDs | Agency remains responsible for |
|---|---|---|---|---|---|
| 164.312(a)(1) | **Access control:** allow access only to authorized persons or software | Standard | Permissions default to deny and are enforced server-side on every request. Tenant isolation by database row-level security. Location scoping. Caregivers see only assigned clients. Support staff see nothing without a time-boxed grant. | FR-IAM-05, FR-IAM-06, FR-IAM-07, BR-001, BR-005, BR-008, NFR-SEC-04 | Assigning roles that match each job; running the quarterly access review (NFR-SEC-04) |
| 164.312(a)(2)(i) | Unique user identification | R | Every person has their own account and email; no shared logins. Every action is attributed to one user, or to System or Support with a grant ID. Sign-in events are recorded. | FR-IAM-01, FR-IAM-08, FR-RPT-03, BR-057 | Not sharing credentials; deactivating leavers promptly (FR-WRK-06) |
| 164.312(a)(2)(ii) | Emergency access procedure | R | Care continues in an outage: the caregiver app captures EVV and documentation offline for 72 h, with today's care-plan tasks, allergies and due doses cached on the device (NFR-AVL-02). A Read-only tenant keeps point-of-care actions available (BR-003, TBD-07). An agency that loses its only administrator recovers access through a verified support procedure. | NFR-AVL-02, BR-003, FR-EVV-05, NFR-DR-01 | Its own emergency-mode operations plan; keeping more than one Agency Administrator |
| 164.312(a)(2)(iii) | Automatic logoff | A | Web sessions end after 15 minutes idle, with a 60-second warning. Mobile requires re-authentication with device PIN or biometrics every 12 hours. | FR-IAM-04 | Device screen-lock policy on caregiver phones |
| 164.312(a)(2)(iv) | Encryption and decryption | A | AES-256 at rest; field-level envelope encryption of PHI (date of birth, Medicaid ID, phone, service address, diagnoses) with KMS keys rotated annually; encrypted offline queue on devices. | NFR-SEC-01, BR-011, NFR-MOB-02 | Encryption of any PHI it exports and stores outside Tendwell |
| 164.312(b) | **Audit controls:** record and examine activity in systems containing ePHI | Standard (R) | An immutable audit log of creates, updates, deletes, PHI reveals (with reason), exports, sign-ins, permission changes and support access, kept 7 years. Filterable and exportable by the Agency Administrator. | FR-RPT-03, FR-RPT-04, FR-IAM-08, BR-057, BR-058, NFR-PRIV-02 | Reviewing audit activity (for example PHI reveals) under its own policy |
| 164.312(c)(1) | **Integrity:** protect ePHI from improper alteration or destruction | Standard | EVV punches are append-only, with corrections as new punches (BR-026). Visit notes lock after 24 h and change only by addenda (BR-035). Doses are never deleted (BR-031). Issued invoices are immutable (BR-051). Audit events are append-only. | BR-026, BR-031, BR-035, BR-051, BR-057, FR-EVV-08, FR-DOC-02 | Using corrections and addenda rather than workarounds outside the system |
| 164.312(c)(2) | Mechanism to authenticate ePHI | A | SHA-256 recorded for every payroll export; signed webhooks; database uniqueness constraints on invoice keys (CR-005); checksums in tenant exports (NFR-PRIV-03). | FR-PAY-05, BR-050, NFR-PRIV-03, IF-01 | Verifying checksums when importing exports elsewhere |
| 164.312(d) | **Person or entity authentication** | Standard (R) | Email and password under NIST SP 800-63B rules; MFA mandatory for the administrator, supervisor, finance and platform roles; account lockout; OIDC identity provider. At the point of care, an optional selfie liveness and face match ties each punch to the caregiver. | FR-IAM-01, FR-IAM-03, BR-006, BR-007, FR-EVV-04, BR-024, IF-10 | Deciding whether to enable identity checks; enrolling caregivers with consent; acting on TBD-09 (MFA for Coordinators) |
| 164.312(e)(1) | **Transmission security** | Standard | TLS 1.2 or later everywhere, with HSTS. Documents move through short-lived pre-signed URLs. SMS, push and email, which are not end-to-end encrypted, carry no PHI, only a sign-in deep link. | NFR-SEC-01, FR-NTF-05, BR-056 | Not forwarding exports or screenshots over unsecured channels |
| 164.312(e)(2)(i) | Integrity controls (in transit) | A | TLS integrity; signed webhooks with replay protection; idempotency keys on unsafe requests; offline sync idempotent by punch UUID. | IF-01, FR-EVV-05, NFR-SEC-01 | None beyond the above |
| 164.312(e)(2)(ii) | Encryption (in transit) | A | TLS 1.2+ for all API, web, mobile and vendor traffic. | NFR-SEC-01 | Its own email and file transfers of exported data |

Beyond 164.312, two administrative and physical safeguards depend on the product:
- **Device and media controls (164.310(d)(1)).** Supported by the encrypted queue and remote wipe on deactivation (NFR-MOB-02). The agency owns device policy and mobile device management.
- **Information access management (164.308(a)(4)).** Supported by role templates, overrides and the access review (FR-IAM-05, NFR-SEC-04).

## 3. HIPAA Privacy Rule: minimum necessary (45 CFR 164.502(b), 164.514(d))

The standard does not apply to disclosures to a provider for treatment. Tendwell still masks by default because most uses inside an agency are operational (scheduling, billing, payroll), not treatment.

| Control area | Tendwell control | Requirement IDs | Agency remains responsible for |
|---|---|---|---|
| Role-based access | Role templates give each job only the modules it needs. Billing & Payroll Specialists have no eMAR or clinical-note access ([SRS section 3.3](SRS.md#33-role-permission-matrix)). | FR-IAM-05, NFR-SEC-04 | Role assignment; approving overrides only with a reason |
| Location and assignment scope | Coordinators, Supervisors and Caregivers see only their locations. Caregivers see only the clients they are assigned to, and only what the visit needs. | FR-IAM-06 | Keeping location assignments current |
| Masking and reveal | PHI fields are masked in lists and detail views; a reveal requires a permission and a reason and is audited. | FR-CLI-06, BR-011, NFR-PRIV-01 | Reviewing reveal patterns; sanctions for misuse |
| Messages | SMS, push and email carry no client names, diagnoses, medications or addresses. Templates use allow-listed variables only. Recipients are resolved at send time from active users. | FR-NTF-05, BR-054, BR-056, CR-006 | Not putting PHI in free-text fields that feed messages |
| Support access | No tenant data access without an Agency Administrator-approved grant of at most 4 hours, read-only by default; PHI reveal is not available under a grant in R1. | FR-IAM-07, BR-008, TBD-10 | Approving only the scope that is needed |
| Exports | Every export is watermarked and audited. | FR-RPT-04, BR-058 | Handling exported files under its own policy |
| Logs and telemetry | No PHI in logs or traces; this is scanned. | NFR-OBS-01 | n/a |
| Vendors | Maps receive addresses only, with no name or ID. Payments receive invoice number and amount only, with no clinical data. Push and SMS carry no PHI. | IF-01 to IF-05, NFR-CMP-01 | n/a |
| Family access (R2) | Consent is recorded before any invitation; the family contact sees one client's schedule and visit summaries only. | FR-FAM-01 | Verifying the contact's authority as personal representative |
| Incident narratives | Other clients involved are referenced by client number, not name. | FR-DOC-03 (field rule) | Training staff to write factual, minimal narratives |

## 4. Breach notification support (45 CFR 164.400-414)

### 4.1 Who does what

| Party | Obligation | How Tendwell supports it |
|---|---|---|
| Tendwell Labs, as business associate | Notify the covered entity of a breach of unsecured PHI without unreasonable delay and no later than 60 calendar days after discovery (164.410), with the identities of affected individuals where known. The BAA sets a shorter notice period. | The [incident management process](../07-operations/incident-management-process.md) treats any suspected PHI exposure as SEV-1 (privacy). The audit log and notification records establish scope. |
| The agency, as covered entity | Decide whether a breach occurred (four-factor risk assessment, 164.402). Notify affected individuals (164.404), HHS (164.408) and, above 500 residents of a state or jurisdiction, the media (164.406). | Tendwell provides the facts for the assessment and the affected-record list. The determination and the notifications are the agency's. |

### 4.2 The Business Analyst's role in a privacy incident

The Business Analyst does not decide whether an event is a breach and does not give legal advice. The role is to make the facts and the fix precise:
1. **Scope the data.** Use the [data classification](../03-design/data/data-classification-and-retention.md) and [data-flow diagram](../03-design/diagrams/data-flow-diagram.md) to list exactly which PHI elements could have travelled through the affected channel.
2. **Establish the facts.** Query the audit log and notification records for recipients, content, times and delivery status. This gives the Compliance and Privacy Officer evidence for each of the four factors.
3. **Find the requirement gap.** Trace the root cause to a missing or ambiguous requirement, not only to code.
4. **Write the change.** Draft the change request; update the affected BRs, FRs and NFRs, the [traceability matrix](requirements-traceability-matrix.md) and the acceptance criteria; agree the regression tests with QA.
5. **Close the loop.** Confirm the fix in UAT, and record the requirement change in the [post-incident review](../07-operations/templates/post-incident-review-template.md).

### 4.3 Worked example: INC-2026-015

On 2026-09-09, a client-incident escalation email went to a deactivated former Care Coordinator's mailbox, which forwarded to a personal address. Escalation recipients had been cached when the ladder was configured, rather than resolved at send time. Full review: [INC-2026-015](../07-operations/incidents/INC-2026-015-escalation-email-to-deactivated-user.md).

| Four-factor assessment (164.402) | Facts established |
|---|---|
| 1. Nature and extent of the PHI | One email containing the client's first name, last initial and incident category. No date of birth, address, Medicaid ID or diagnosis. |
| 2. The unauthorized person | A former agency workforce member, through automatic forwarding to a personal address. |
| 3. Whether the PHI was actually acquired or viewed | Delivered to the personal mailbox; treated as viewed. |
| 4. Extent of mitigation | The recipient confirmed deletion in writing. |

Response:
- The Compliance and Privacy Officer ran the assessment and the covered-entity agency was notified within 24 hours under the BAA. The final breach determination rests with the covered entity.
- Requirement changes (CR-006, SRS v1.3):
  - BR-054: recipients are resolved at send time; deactivated users never receive notifications.
  - BR-056 and FR-NTF-05: no PHI in email bodies, extended from SMS and push.
  - NFR-OBS-02: any send addressed to a deactivated user is blocked and pages on-call.
- Regression tests cover a ladder whose configured role holder is deactivated before the event fires.

## 5. 21st Century Cures Act section 12006: EVV

Section 12006 added section 1903(l) to the Social Security Act. It requires EVV for Medicaid personal care services and home health care services, capturing six data elements (BR-020). Tendwell captures all six for every visit and exports them through IF-09 (NFR-CMP-02).

| # | Data element | Tendwell source fields | How it is captured | Integrity controls |
|---|---|---|---|---|
| 1 | Type of service performed | `visits.service_authorization_id` to `service_authorizations.service_code`; `visits.service_line_id` to `service_lines.code`. Supporting: `visit_task_results` (tasks done). | From the authorization the visit is scheduled against (BR-009) | A visit cannot be scheduled without a matching Active authorization (hard block S3 in [business-rules.md](business-rules.md#34-scheduling-compliance-checks)) |
| 2 | Individual receiving the service | `visits.client_id` to `clients.client_number`, `clients.first_name`, `clients.last_name`, `clients.medicaid_id_enc` | From the schedule | Duplicate-client check (FR-CLI-02); Medicaid ID format validation |
| 3 | Date of the service | `evv_punches.punch_time` where `type` = In, rendered in `tenants.time_zone` | Device capture time at clock-in; server receipt time in `evv_punches.received_at` (BR-025) | Late offline sync exception after 24 h (BR-025) |
| 4 | Location of service delivery | `evv_punches.lat`, `evv_punches.lng`, `evv_punches.accuracy_m`, `evv_punches.distance_m`, compared with `clients.lat`, `clients.lng`, `clients.geofence_radius_m` (address in `clients.service_address_enc`) | Device GPS at each punch; distance computed on the server (BR-021) | Location mismatch and Low GPS accuracy exceptions (BR-021, BR-022) |
| 5 | Individual providing the service | `visits.caregiver_id` to `caregivers.employee_number`, `caregivers.first_name`, `caregivers.last_name`; `evv_punches.device_id`; `evv_punches.identity_check_id` to `identity_checks.result` where enabled | The signed-in caregiver's assigned visit; optional selfie check (FR-EVV-04) | Single-use 90-second identity check (BR-024); Identity check failed exception |
| 6 | Time the service begins and ends | `evv_punches.punch_time` for `type` In and Out; `evv_punches.source` (Mobile, MobileOffline, Manual, System) | Clock-in and clock-out on the device; corrections as new punches with `supersedes_punch_id`, `reason_code`, `note` and `created_by` (BR-026) | Append-only ledger; Late start, Early end, Missing clock-out and Auto-closed exceptions |

Applicability and agency responsibilities:
- **Which visits are in scope.** The mandate covers Medicaid personal care and home health services. CMS guidance indicates that services in congregate residential settings where 24-hour service is available are not subject to it. Whether ADULT_DAY and SUPPORTED_LIVING visits are reported is decided by the agency per payer and state. Tendwell captures the same elements for every visit regardless.
- **Manual corrections.** States commonly monitor manual-edit rates. The export includes the punch source and the reason code, so a manually corrected visit is never presented as device-captured. OBJ-01 reports the manual-correction rate alongside completeness for the same reason.
- **Submission.** The agency uploads the export to the state aggregator and works any rejections. State-specific formats and direct submission are R2 (TBD-12).

## 6. FLSA and the DOL Home Care Rule

Since the DOL Home Care Rule took effect in 2015, third-party employers such as agencies cannot claim the companionship-services or live-in exemptions for their home care workers (29 CFR 552.109). Agency caregivers are therefore owed minimum wage and overtime, and their travel time between clients counts as hours worked. Any future change to the federal third-party employer provisions would be tracked by the Compliance and Privacy Officer. Several states require overtime independently, so Tendwell keeps these rules tenant-configurable rather than hard-coded.

| Obligation | Citation | Tendwell rule | Requirement IDs | Agency remains responsible for |
|---|---|---|---|---|
| Overtime at 1.5x the regular rate for hours over 40 in a workweek | 29 USC 207(a)(1) | Weekly overtime over 40 h at 1.5x for overtime-eligible caregivers, assigned to the chronologically last minutes of the tenant's workweek | BR-041, FR-PAY-02 | Defining the workweek. Regular-rate treatment of pay outside Tendwell: Tendwell computes overtime on the base rate, so shift differentials and non-discretionary bonuses paid elsewhere must be included by the payroll provider. |
| No companionship or live-in exemption for third-party employers | 29 CFR 552.109 | Pay profiles default to overtime-eligible for hourly caregivers | FR-WRK-05 | Classifying each worker correctly |
| Travel between clients during the workday is hours worked | 29 CFR 785.38 | Paid travel = min(actual gap, estimated drive time + 10 min) between consecutive visits when the gap is 2 h or less; it counts toward overtime | BR-043, FR-PAY-02 | Confirming the 2-hour off-duty threshold and the 10-minute allowance with its own counsel. A gap is off duty only if the caregiver is completely relieved and can use the time for their own purposes (29 CFR 785.16). |
| Ordinary home-to-work commute is not hours worked | 29 CFR 785.35 | Travel is paid only between consecutive visits, never before the first or after the last ([business-rules.md](business-rules.md#33-payroll-hour-classification), table 3.3b, row V1) | BR-043 | n/a |
| Each hour worked counted once | FLSA hours-worked principles | Overlapping time from different sources is merged, held to the second | BR-045, FR-PAY-03 | n/a |
| Holiday premium of at least 1.5x is creditable toward overtime | 29 USC 207(e)(6) and (h)(2); 29 CFR 778.203 | No stacking: a minute that is both holiday and overtime is paid once at the higher multiplier | BR-042 | Its holiday-pay policy (holiday premium itself is not a federal requirement) |
| Expense reimbursements are excluded from the regular rate | 29 CFR 778.217 | Mileage is a reimbursement line, not wages, and never changes hours | BR-044 | Setting a reasonable mileage rate |
| Paid leave is not hours worked | FLSA hours-worked principles | PTO does not count toward overtime | BR-040 | State rules that differ |
| State daily overtime | State law | Optional daily profile: over 8 h at 1.5x, over 12 h at 2.0x (CR-001) | BR-041 | Choosing the profile. Rules not modeled in R1, such as seventh-consecutive-day premiums, must be applied by the payroll provider. |
| Records of hours worked each workday and workweek | 29 CFR 516.2, 516.5, 516.6 | Append-only punches; payroll lines with source visits; exports with SHA-256; tenant export on exit | BR-026, BR-046, FR-PAY-05, NFR-PRIV-03 | Keeping payroll records for 3 years and time records for 2 years in its payroll system |

The canonical payroll example ([SRS Appendix B.1](SRS.md#b1-payroll-us-041)) shows the overtime, holiday, travel and mileage rules applied together.

## 7. WCAG 2.2 AA

NFR-ACC-01 sets WCAG 2.2 AA for the web app and screen-reader and 200% font support for the mobile app. HHS's 2024 Section 504 rule adopts WCAG 2.1 AA for the web content and mobile apps of recipients of HHS funding, which includes many agencies; WCAG 2.2 AA exceeds that baseline. The criteria that matter most in Tendwell:

| Success criterion | Level | Where it matters in Tendwell | Control | Verification |
|---|---|---|---|---|
| 1.3.1 Info and Relationships | A | Schedule board, MAR grid, payroll and invoice tables | Semantic tables with headers; grid pattern for the board | axe-core; screen-reader test |
| 1.4.1 Use of Color | A | Color-coded visit status (FR-SCH-06); exception and dose status | A text label and icon always accompany color | Inspection |
| 1.4.3 Contrast (Minimum) | AA | All text | Design tokens at 4.5:1 or better | axe-core |
| 1.4.4 Resize Text; 1.4.10 Reflow | AA | Web at 200% and 400% zoom; mobile at 200% font | Responsive layouts; no fixed-height text containers | Manual |
| 2.1.1 Keyboard | A | Schedule board, forms, exception queue | Every action keyboard-operable | Manual |
| 2.2.1 Timing Adjustable | A | The 15-minute idle sign-out (FR-IAM-04) | 60-second warning with "Stay signed in", unlimited extensions | Manual |
| 2.4.11 Focus Not Obscured (Minimum) | AA (new in 2.2) | Sticky headers and toasts over the schedule board | Scroll padding; toasts never cover the focused element | Manual |
| 2.5.7 Dragging Movements | AA (new in 2.2) | Drag-and-drop visit moves on the schedule board | A "Move to..." menu alternative | Manual |
| 2.5.8 Target Size (Minimum) | AA (new in 2.2) | All controls, especially on mobile | At least 24 x 24 CSS px on web; 44 x 44 pt on mobile | axe-core; manual |
| 3.2.6 Consistent Help | A (new in 2.2) | Help and support entry points | Same position on every screen | Inspection |
| 3.3.1 Error Identification; 3.3.3 Error Suggestion | A; AA | Every form | Messages state the problem and the fix (NFR-USE-03) | Inspection |
| 3.3.7 Redundant Entry | A (new in 2.2) | Multi-step sign-up; client intake | Values entered earlier are carried forward, never retyped | Manual |
| 3.3.8 Accessible Authentication (Minimum) | AA (new in 2.2) | Sign-in, MFA, password reset | Paste and password managers allowed; no puzzles or transcription tests | Manual |
| 4.1.3 Status Messages | AA | Offline sync status; save confirmations | Polite live regions | Screen-reader test |

## 8. NIST SP 800-63B: passwords and authenticators

BR-007 cites NIST SP 800-63B. The table compares Tendwell's controls with the current revision (SP 800-63B-4, 2025) and flags one gap.

| SP 800-63B expectation | Tendwell control | Requirement IDs | Status |
|---|---|---|---|
| Minimum length: at least 15 characters for a password used as a single factor; at least 8 when used only with MFA | Minimum 12 characters for everyone | BR-007, BR-006 | Meets the MFA case. **Gap** for users without MFA (AG-COORD and CG may opt out). TBD-09 recommends MFA for Coordinators, or 15 characters for users without MFA. |
| Allow at least 64 characters, all printable characters and spaces | Up to 64 characters; Unicode and spaces allowed | BR-007 | Meets |
| No composition rules | None imposed | BR-007 | Meets |
| No periodic forced change; change on evidence of compromise | No forced rotation | BR-007 | Meets |
| Screen new passwords against breached and common lists | Checked against a breached-password list | BR-007 | Meets |
| Allow paste and password managers | Allowed (also WCAG 3.3.8) | NFR-ACC-01 | Meets |
| Limit failed attempts (at most 100 consecutive) | Lockout for 15 minutes after 5 consecutive failures, with an email to the owner | FR-IAM-03 | Meets (stricter) |
| No hints or knowledge-based recovery | Recovery only by a single-use email link valid for 30 minutes; the response does not reveal whether the account exists | FR-IAM-02 | Meets |
| Out-of-band codes over SMS are a restricted authenticator | SMS codes allowed alongside authenticator-app TOTP | FR-IAM-01 | **Accepted risk**, pending TBD-09. TOTP is the default in onboarding; SMS is a fallback. |
| Session management and reauthentication appropriate to the assurance level | Web idle sign-out after 15 minutes; mobile re-authentication every 12 hours | FR-IAM-04 | Confirm against the assurance level chosen per role (TBD-09) |

## 9. Shared responsibility summary

| Area | Tendwell Labs | Agency |
|---|---|---|
| Risk analysis (45 CFR 164.308(a)(1)) | Platform risk analysis and remediation | Its own enterprise risk analysis, including how it uses Tendwell |
| Workforce | Tendwell staff training and sanctions; support access only by grant | Its staff's training, role assignment, sanctions and prompt deactivation |
| Devices | App-level encryption, no PHI in plain storage, remote wipe on deactivation | Device policy, mobile device management, lost-device reporting |
| Breaches | Detection, facts, notice to the agency under the BAA | Determination; notices to individuals, HHS and media |
| EVV | Capture of the six elements; exceptions; export | State submission; rejection handling; deciding which visits are in scope |
| Payroll | Classification per configured rules; export | Rule configuration, regular rate, tax, payment and filings |
| Client incidents | Deadline tracking and alerts | Reporting to the state authority and follow-up |
| Accessibility | Product conformance to WCAG 2.2 AA | Accessibility of documents it uploads or sends |

## Related documents

- [Software Requirements Specification](SRS.md)
- [Non-functional requirements](non-functional-requirements.md)
- [Business rules](business-rules.md)
- [Glossary](glossary.md)
- [Data classification and retention](../03-design/data/data-classification-and-retention.md)
- [Deployment and security architecture](../03-design/architecture/deployment-and-security.md)
- [Incident management process](../07-operations/incident-management-process.md)
- [INC-2026-015 post-incident review](../07-operations/incidents/INC-2026-015-escalation-email-to-deactivated-user.md)
- [Change request log](../05-delivery/change-request-log.md)
- [Requirements traceability matrix](requirements-traceability-matrix.md)
