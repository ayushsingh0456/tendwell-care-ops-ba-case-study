# EP-02 Identity & Access Management: user stories

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DEL-US-02 |
| Version | 1.2 |
| Status | Baselined |
| Owner | Business Analyst |
| Last updated | 2026-06-12 |
| Reviewers | Product Owner, Engineering Lead, QA Lead, Compliance and Privacy Officer |

## Purpose and scope

This file holds the user stories and acceptance criteria for EP-02. It covers sign-in with multi-factor authentication, password reset, roles and permission overrides, account lockout, session timeouts and time-boxed support access. The controls are designed to support the HIPAA Security Rule technical safeguards (45 CFR 164.312) and follow NIST SP 800-63B for passwords. The agency remains responsible for its own access reviews.

## Epic

| Field | Value |
|---|---|
| Epic ID | EP-02 |
| Name | Identity & Access Management |
| Module | IAM |
| Goal | Give every user secure, least-privilege access limited to their tenant and assigned locations, keep a complete sign-in and access trail, and let Tendwell Labs support staff into a tenant only with the agency's time-boxed consent. |
| Objectives | Enabler for OBJ-01 to OBJ-06 (no direct KPI). Guardrails: zero cross-tenant access findings in the penetration test (NFR-SEC-02); 100% MFA enrollment for MFA-mandatory roles. |
| Business need | BN-02 |
| Release | R1 |

## Story list

| Story | Title | Persona | Priority | Points | Sprint |
|---|---|---|---|---|---|
| US-007 | Sign in with multi-factor authentication | PER-05 Tom Brennan (AG-ADM) | Must | 5 | S1 |
| US-008 | Reset a forgotten password | PER-01 Rosa Delgado (CG) | Must | 2 | S1 |
| US-009 | Assign roles and permission overrides | PER-05 Tom Brennan (AG-ADM) | Must | 8 | S1 |
| US-010 | Lock accounts and expire idle sessions | System (SYS) | Must | 3 | S1 |
| US-011 | Request time-boxed support access to a tenant | Platform Support Agent (PLT-SUP) | Should | 5 | S2 |
| **Total** | | | | **23** | |

## Stories

### US-007 · Sign in with multi-factor authentication

| Field | Value |
|---|---|
| Epic | EP-02 Identity & Access Management |
| Persona | PER-05 Tom Brennan (AG-ADM) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S1 / R1 |
| Requirements | FR-IAM-01, FR-IAM-08 |
| Business rules | BR-006, BR-007 |
| Dependencies | US-001 |

**Story**
As an Agency Administrator, I want to sign in with my password and a second factor, so that nobody can reach my agency's client and payroll data with a stolen password.

**Acceptance criteria**

```gherkin
Scenario: US-007-AC1 Sign in with password and authenticator code
  Given Tom has the AG-ADM role and an enrolled authenticator app
  When he enters "tom.brennan@example.com", his correct password and a current 6-digit TOTP code
  Then he is signed in to the Agency Web App
  And a sign-in event is recorded with outcome "Success", IP address, device and timestamp

Scenario Outline: US-007-AC2 MFA is mandatory for privileged roles
  Given a user whose only role is <role> signs in for the first time with a correct password
  When the password step succeeds
  Then MFA enrollment is <enrollment>

  Examples:
    | role     | enrollment                                         |
    | AG-ADM   | required before any page is shown                  |
    | AG-SUPV  | required before any page is shown                  |
    | AG-FIN   | required before any page is shown                  |
    | PLT-ADM  | required before any page is shown                  |
    | PLT-SUP  | required before any page is shown                  |
    | AG-COORD | offered and can be skipped                         |
    | CG       | offered and can be skipped                         |

Scenario Outline: US-007-AC3 Record failed sign-ins without revealing which factor failed
  When a sign-in attempt for "<email>" fails because <cause>
  Then the user sees "<message>"
  And a sign-in event is recorded with outcome "<outcome>" and the attempted email

  Examples:
    | email                     | cause                        | message                                   | outcome     |
    | tom.brennan@example.com   | the password is wrong        | Email or password is incorrect.           | BadPassword |
    | nobody@example.com        | no account exists            | Email or password is incorrect.           | BadPassword |
    | tom.brennan@example.com   | the TOTP code is wrong       | That code did not work. Try a new code.   | MfaFailed   |

Scenario Outline: US-007-AC4 Enforce the password policy
  When Tom sets his password to a <candidate>
  Then the password is <result>

  Examples:
    | candidate                                         | result                                                       |
    | 11-character password not on the breached list   | rejected: use at least 12 characters                         |
    | 12-character password not on the breached list   | accepted                                                     |
    | 12-character password found on the breached list | rejected: this password has appeared in a data breach        |

Scenario: US-007-AC5 No forced periodic rotation
  Given Tom's password was set 400 days ago and has not appeared on the breached list
  When he signs in
  Then he is not asked to change his password

Scenario: US-007-AC6 Use an SMS one-time code without PHI
  Given Tom chose SMS as his second factor with verified phone "+1-614-555-0142"
  When he passes the password step
  Then an SMS is sent containing only a one-time code and the text "Tendwell sign-in code. Do not share it."
```

**Notes**
- MFA uses TOTP or SMS one-time codes through the managed OIDC provider; access tokens live 15 minutes and refresh tokens rotate on use.
- Recovery when an MFA device is lost: another Agency Administrator resets the factor, or Tendwell Support does so under a support grant (US-011). The reset is audited.
- Analytics: sign-in success rate and MFA failure rate per tenant feed the security dashboard.
- Out of scope: SSO with agency identity providers (backlog candidate); WebAuthn passkeys (R2 candidate).

### US-008 · Reset a forgotten password

| Field | Value |
|---|---|
| Epic | EP-02 Identity & Access Management |
| Persona | PER-01 Rosa Delgado (CG) |
| Priority | Must |
| Estimate | 2 points |
| Sprint / Release | S1 / R1 |
| Requirements | FR-IAM-02 |
| Business rules | BR-007 |
| Dependencies | US-007 |

**Story**
As a caregiver, I want to reset my forgotten password from my phone, so that I can sign in before my next visit without calling the office.

**Acceptance criteria**

```gherkin
Scenario: US-008-AC1 Request a reset without revealing whether the email is registered
  When Rosa requests a password reset for "rosa.delgado@example.com"
  And another person requests a reset for "unknown.person@example.com"
  Then both see "If an account exists for this email, we sent a reset link. It expires in 30 minutes."
  And only "rosa.delgado@example.com" receives an email
  And both responses take a similar time, within 100 ms of each other at p95

Scenario Outline: US-008-AC2 The reset link is valid for 30 minutes and single use
  Given a reset link was sent to Rosa at 06:30
  When she opens it at <time> <state>
  Then <result>

  Examples:
    | time  | state                     | result                                                         |
    | 06:59 | for the first time        | she can set a new password                                     |
    | 07:00 | for the first time        | she can set a new password                                     |
    | 07:01 | for the first time        | she sees "This link has expired. Request a new one."           |
    | 06:45 | after already resetting   | she sees "This link has already been used. Sign in instead."   |

Scenario: US-008-AC3 Apply the password policy on reset
  When Rosa enters an 11-character new password
  Then she sees "Use at least 12 characters. A short phrase is easier to remember."
  And her old password still works

Scenario: US-008-AC4 Revoke other sessions after a reset
  Given Rosa is signed in on a tablet and on her phone
  When she completes a password reset from her phone
  Then the tablet session and all refresh tokens issued before the reset are revoked
  And Rosa receives an email confirming the password change with no PHI
  And unsynced EVV punches on both devices are kept and sync after she signs in again

Scenario: US-008-AC5 Deactivated users cannot reset
  Given the user "former.aide@example.com" is Deactivated
  When a reset is requested for that email
  Then the neutral confirmation message is shown and no email is sent
```

**Notes**
- The reset email contains no PHI and no account details other than the link.
- UX: the mobile app opens the reset link inside the app when installed (universal link / app link).
- Out of scope: reset by SMS link (phones are often shared in households).

### US-009 · Assign roles and permission overrides

| Field | Value |
|---|---|
| Epic | EP-02 Identity & Access Management |
| Persona | PER-05 Tom Brennan (AG-ADM) |
| Priority | Must |
| Estimate | 8 points |
| Sprint / Release | S1 / R1 |
| Requirements | FR-IAM-05, FR-IAM-06 |
| Business rules | BR-001, BR-005 |
| Dependencies | US-007 |

**Story**
As an Agency Administrator, I want to assign role templates and individual permission overrides and see the effective result before saving, so that each person gets exactly the access their job needs.

**Acceptance criteria**

```gherkin
Scenario: US-009-AC1 Preview effective permissions before saving
  Given Marcus Hale has no roles
  When Tom assigns the role template AG-COORD and the location "Lakemont North"
  Then before saving, Tom sees the effective permission list including "visits:create" and "visit_exceptions:resolve"
  And after saving, the change is audited with before and after values

Scenario Outline: US-009-AC2 Compute effective permissions with deny winning
  Given Marcus has role template AG-COORD
  And the template <template state> "<permission>"
  And Marcus has the override <override>
  Then the effective permission "<permission>" is <effective>

  Examples:
    | template state | permission           | override       | effective |
    | grants         | clients:reveal_phi   | none           | granted   |
    | grants         | clients:reveal_phi   | Deny           | denied    |
    | does not grant | payroll:export       | Grant          | granted   |
    | does not grant | payroll:export       | none           | denied    |
    | grants         | visits:cancel        | Grant          | granted   |

Scenario: US-009-AC3 Enforce permissions on the server
  Given Marcus has an effective Deny on "clients:reveal_phi"
  When he calls POST /v1/clients/{clientId}/phi-reveals directly with a valid token
  Then the API returns 403 with an application/problem+json body
  And the denied attempt is written to the audit log

Scenario: US-009-AC4 Isolate tenants in the database
  Given client C-10234 belongs to Harborview Home Care (TEN-001)
  When an Agency Administrator of Cedar Lane Adult Day Center (TEN-002) requests GET /v1/clients/{id of C-10234}
  Then the API returns 404, not 403, so the record's existence is not confirmed
  And a database query run under TEN-002's session returns no rows for C-10234 because row-level security filters on tenant_id

Scenario: US-009-AC5 Limit data to assigned locations
  Given Marcus is assigned only to "Lakemont North"
  And Harborview also has the location "Lakemont South"
  When Marcus opens the client list
  Then only clients of "Lakemont North" are listed
  And a request for a "Lakemont South" client returns 404

Scenario: US-009-AC6 Keep at least one active Agency Administrator
  Given Tom is the only active user with the AG-ADM role
  When he removes AG-ADM from himself
  Then the change is rejected with "Your agency needs at least one active Agency Administrator. Assign the role to someone else first."
```

**Notes**
- Permission changes apply on the user's next request; permissions are evaluated server-side and are not embedded in the 15-minute access token.
- Permissions default to deny (NFR-SEC-04); Agency Administrators receive a quarterly access-review report.
- Row-level security on `tenant_id` follows ADR-001 and DEC-01; the API never accepts a tenant ID from the client.
- Out of scope: custom role templates authored from scratch (R1 supports copying and editing the defaults).

### US-010 · Lock accounts and expire idle sessions

| Field | Value |
|---|---|
| Epic | EP-02 Identity & Access Management |
| Persona | System (SYS) |
| Priority | Must |
| Estimate | 3 points |
| Sprint / Release | S1 / R1 |
| Requirements | FR-IAM-03, FR-IAM-04 |
| Business rules | None |
| Dependencies | US-007 |

**Story**
As the authentication service, I want to lock accounts after repeated failed sign-ins and end idle sessions, so that password guessing and unattended screens do not expose PHI.

**Acceptance criteria**

```gherkin
Scenario Outline: US-010-AC1 Lock after 5 consecutive failures
  Given Marcus's account is Active
  When <failures> consecutive sign-in attempts fail with a wrong password
  Then the account status is "<status>"
  And the account owner email is <email>

  Examples:
    | failures | status | email    |
    | 4        | Active | not sent |
    | 5        | Locked | sent     |

Scenario Outline: US-010-AC2 The lock lasts 15 minutes
  Given Marcus's account was locked at 09:00
  When he signs in with the correct password at <time>
  Then the result is "<result>"

  Examples:
    | time     | result                                                                         |
    | 09:14:59 | Your account is temporarily locked. Try again later or reset your password.    |
    | 09:15:00 | Signed in                                                                      |

Scenario: US-010-AC3 A successful sign-in resets the failure counter
  Given Marcus has 4 consecutive failed attempts
  When he signs in successfully and later fails 4 more times
  Then the account is not locked

Scenario: US-010-AC4 Warn and then end an idle web session
  Given Denise is signed in to the Agency Web App and has been idle for 14 minutes
  Then a dialog warns "You will be signed out in 60 seconds" with a "Stay signed in" button
  When she does not respond for 60 seconds
  Then the session ends and she sees the sign-in page with "You were signed out after 15 minutes of inactivity."
  And PHI is no longer displayed on the screen

Scenario: US-010-AC5 Re-authenticate on mobile after 12 hours
  Given Rosa last authenticated on the Caregiver app 12 hours ago
  When she opens the app
  Then she must confirm her identity with the device PIN or biometrics
  And if that fails 3 times she must sign in with her password
  And punches queued offline before the prompt are kept and sync after she authenticates
```

**Notes**
- Lockout messaging is deliberately the same whether the account exists or not after lock, except for the lock text itself; the Compliance and Privacy Officer accepted the small enumeration risk in exchange for fewer support calls.
- Lockout applies per account, not per IP; IP rate limiting is handled at the WAF.
- Out of scope: risk-based or adaptive authentication.

### US-011 · Request time-boxed support access to a tenant

| Field | Value |
|---|---|
| Epic | EP-02 Identity & Access Management |
| Persona | Platform Support Agent (PLT-SUP) |
| Priority | Should |
| Estimate | 5 points |
| Sprint / Release | S2 / R1 |
| Requirements | FR-IAM-07 |
| Business rules | BR-008 |
| Dependencies | US-009 |

**Story**
As a Platform Support Agent, I want to request time-boxed access to an agency's tenant that starts only after the agency approves it, so that I can troubleshoot with the agency's consent and a full audit trail.

**Acceptance criteria**

```gherkin
Scenario: US-011-AC1 Request access with a reason
  When the support agent requests ReadOnly access to Harborview Home Care for 2 hours with reason "Ticket 4821: schedule board not loading"
  Then a grant is created with status "Requested"
  And Tom Brennan receives an in-app and email notification asking him to approve or decline

Scenario Outline: US-011-AC2 Limit the duration to 4 hours
  When the support agent requests access for <duration>
  Then the request is <result>

  Examples:
    | duration          | result                                         |
    | 4 hours           | accepted                                       |
    | 4 hours 1 minute  | rejected: access can last at most 4 hours      |
    | 0 minutes         | rejected: enter a duration of at least 1 minute |

Scenario: US-011-AC3 No access before approval and none after expiry
  Given a grant is "Requested"
  When the support agent opens the tenant's client list
  Then the request returns 403
  When Tom approves the grant at 10:00 for 2 hours
  Then the support agent can view the tenant's data until 12:00
  And the first request after 12:00 returns 403 and the grant status is "Expired"

Scenario: US-011-AC4 Revoke or decline at any time
  Given a grant is "Active"
  When Tom revokes it
  Then the grant status is "Revoked" and the support agent's next request returns 403
  And a declined request ends with status "Declined" and the support agent is notified

Scenario: US-011-AC5 Audit and restrict actions under a grant
  Given a ReadOnly grant is "Active"
  When the support agent views client C-10234 and then tries to edit the client's phone number
  Then the view is audited with actor type "Support" and the grant ID
  And the edit returns 403 because the grant is read-only
```

**Notes**
- ReadWrite grants are available only when Tom selects ReadWrite during approval; the default is ReadOnly (BR-008).
- Support agents never see PHI unmasked unless the grant is approved and their platform role holds the reveal permission; every reveal still needs a reason (US-015).
- Analytics: number of grants per tenant per month and median grant duration, reviewed quarterly by the Compliance and Privacy Officer.

## Related documents

- [Epics overview](../epics.md)
- [Story map](../story-map.md)
- [Software requirements specification](../../02-requirements/SRS.md)
- [Business rules catalog](../../02-requirements/business-rules.md)
- [Non-functional requirements](../../02-requirements/non-functional-requirements.md)
- [Compliance mapping](../../02-requirements/compliance-mapping.md)
- [ADR-001 Multi-tenancy with row-level security](../../03-design/architecture/adr/ADR-001-multi-tenancy-row-level-security.md)
- [Deployment and security architecture](../../03-design/architecture/deployment-and-security.md)
- [Test cases](../../06-quality/test-cases.md)
