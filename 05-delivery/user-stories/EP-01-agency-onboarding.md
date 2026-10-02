# EP-01 Agency Onboarding & Subscription: user stories

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DEL-US-01 |
| Version | 1.2 |
| Status | Baselined |
| Owner | Business Analyst |
| Last updated | 2026-06-12 |
| Reviewers | Product Owner, Engineering Lead, QA Lead, UX Designer, Customer Success Lead |

## Purpose and scope

This file holds the user stories, acceptance criteria and story notes for EP-01. It covers self-service agency sign-up, trial and promo codes, email verification, the setup checklist, subscription seats and the Read-only state for unpaid tenants. Story IDs, requirement links, estimates and sprint allocation match the requirements baseline (SRS v1.3). Acceptance criterion IDs follow the pattern `US-NNN-ACn` and are traced to test cases in the test suite.

## Epic

| Field | Value |
|---|---|
| Epic ID | EP-01 |
| Name | Agency Onboarding & Subscription |
| Module | ONB |
| Goal | Let a care agency go from the public sign-up site to a provisioned, correctly billed tenant in one sitting, with no Tendwell Labs staff involvement, and make sure subscription problems never block care delivery. |
| Objectives | Enabler for OBJ-01 to OBJ-06 (no direct KPI). Leading indicator: pilot tenants complete the setup checklist within 5 business days of activation. |
| Business need | BN-01 |
| Release | R1 |

## Story list

| Story | Title | Persona | Priority | Points | Sprint |
|---|---|---|---|---|---|
| US-001 | Register my agency | PER-05 Tom Brennan (AG-ADM) | Must | 8 | S1 |
| US-002 | Apply a trial or promo code at sign-up | PER-05 Tom Brennan (AG-ADM) | Must | 3 | S1 |
| US-003 | Verify my email and complete the setup checklist | PER-05 Tom Brennan (AG-ADM) | Must | 5 | S1 |
| US-004 | Manage my subscription seats and payment method | PER-05 Tom Brennan (AG-ADM) | Must | 5 | S1 |
| US-005 | Manage plans and promo codes | Platform Administrator (PLT-ADM) | Must | 5 | S1 |
| US-006 | Move unpaid tenants to read-only without blocking care | System (SYS) | Must | 3 | S6 |
| **Total** | | | | **29** | |

Shared test data: plan `Core` at $14.00 per active client seat per month; tenant time zone America/New_York; owner email `tom.brennan@example.com`; owner phone +1-614-555-0142; registered address 200 Harbor Street, Lakemont, OH 43999.

## Stories

### US-001 · Register my agency

| Field | Value |
|---|---|
| Epic | EP-01 Agency Onboarding & Subscription |
| Persona | PER-05 Tom Brennan (AG-ADM) |
| Priority | Must |
| Estimate | 8 points |
| Sprint / Release | S1 / R1 |
| Requirements | FR-ONB-01, FR-ONB-04 |
| Business rules | BR-002 |
| Dependencies | US-005, DEP-05 |

**Story**
As an agency owner, I want to register my agency online with my details, the agency's legal details, a plan and our service lines, so that I can start using Tendwell the same day without waiting for a call or manual setup by Tendwell staff.

**Acceptance criteria**

```gherkin
Scenario: US-001-AC1 Register with a trial code and no payment method
  Given the public sign-up site shows the Active plan "Core"
  And the sign-up link carries the valid trial code "TRIAL21"
  When Tom enters his first name, last name, email "tom.brennan@example.com" and phone "+1-614-555-0142"
  And he enters legal name "Harborview Home Care LLC", EIN "12-3456789", registered address "200 Harbor Street, Lakemont, OH 43999" and time zone "America/New_York"
  And he selects plan "Core" and service line "HOME_VISIT", accepts the terms and the BAA, and submits
  Then a tenant is created with status "Pending"
  And no payment method is requested
  And the EIN is stored encrypted and shown only as "**-***6789"
  And a verification email is sent to "tom.brennan@example.com"

Scenario: US-001-AC2 Register without a trial code
  Given Tom has not applied a trial code
  When he completes the sign-up form and submits
  Then the payment provider's hosted card form is shown before submission completes
  And card details are never sent to or stored by Tendwell
  And after email verification the subscription starts with status "Active" instead of "Trialing"

Scenario Outline: US-001-AC3 Reject incomplete or invalid registration data
  Given Tom is on the agency details step
  When he submits with <field> set to "<value>"
  Then the form is not submitted
  And the message "<message>" is shown next to the field

  Examples:
    | field         | value       | message                                                       |
    | legal name    |             | Enter the agency's legal name as registered with the IRS.     |
    | EIN           | 12345       | Enter the EIN as 9 digits in the format 12-3456789.           |
    | service lines | none        | Select at least one service line your agency provides.        |
    | time zone     |             | Select the time zone your agency schedules visits in.         |
    | owner email   | tom@example | Enter a full email address, for example name@example.com.     |

Scenario: US-001-AC4 Provision the tenant on activation
  Given tenant "Harborview Home Care LLC" is "Pending" with trial code "TRIAL21"
  When Tom verifies his email address
  Then the tenant is provisioned with role templates for AG-ADM, AG-COORD, AG-SUPV, AG-FIN and CG
  And default credential types, EVV reason codes, notification templates and escalation ladders are created
  And tenant settings use the platform defaults, including a 150 m geofence radius and clock-in opening 15 minutes before the scheduled start
  And Tom is assigned the AG-ADM role
  And the tenant status becomes "Trial" with the trial ending 21 days after activation

Scenario: US-001-AC5 Provisioning is retried without creating duplicates
  Given provisioning for a newly verified tenant fails after the role templates were created
  When the provisioning job retries
  Then provisioning completes with exactly one set of role templates, credential types and escalation ladders
  And the tenant stays "Pending" until every provisioning step has succeeded
  And Tom sees "We are finishing setting up your account. This usually takes less than a minute." instead of an error code
```

**Notes**
- UX: three-step wizard (owner, agency, plan and service lines) with a progress indicator; the BAA is presented as a separate checkbox with a link to the full text.
- Analytics: track step completion and abandonment per step; target 70% or more of started sign-ups reach email verification.
- Out of scope: multi-entity agencies (one EIN per tenant in R1); bulk data import, which Customer Success handles for the pilot (DEP-03).
- One tenant per EIN: a second registration with an EIN that already has an Active or Trial tenant is routed to Customer Success rather than rejected, to avoid confirming that the agency is a customer.

### US-002 · Apply a trial or promo code at sign-up

| Field | Value |
|---|---|
| Epic | EP-01 Agency Onboarding & Subscription |
| Persona | PER-05 Tom Brennan (AG-ADM) |
| Priority | Must |
| Estimate | 3 points |
| Sprint / Release | S1 / R1 |
| Requirements | FR-ONB-03 |
| Business rules | BR-002, BR-004 |
| Dependencies | US-001, US-005 |

**Story**
As an agency owner, I want to apply a trial or promo code and see its effect on the price before I submit, so that I know exactly what my agency will pay.

**Acceptance criteria**

```gherkin
Scenario Outline: US-002-AC1 Show the price effect of a valid code
  Given Tom has selected plan "Core" at $14.00 per active client seat per month
  When he applies the code "<code>"
  Then the code is accepted
  And the price summary shows "<effect>" before he submits

  Examples:
    | code       | kind     | effect                                                    |
    | TRIAL21    | Trial    | 21-day free trial, no payment method required             |
    | LAKEMONT20 | Percent  | $11.20 per active client seat per month (20% off)         |
    | WELCOME50  | Fixed    | $50.00 off each monthly subscription invoice              |

Scenario Outline: US-002-AC2 Reject an unusable code with a specific reason
  Given Tom has selected plan "Core"
  And today is 2026-03-16
  When he applies the code "<code>"
  Then the code is rejected with the message "<message>"
  And the price summary is unchanged
  And Tom can still submit the sign-up without a code

  Examples:
    | code       | condition                                    | message                                                        |
    | NOPE99     | does not exist                               | We could not find this code. Check the spelling and try again. |
    | SPRING25   | status Inactive                              | This code is no longer active.                                 |
    | WINTER10   | expired on 2026-02-28                        | This code expired on 2026-02-28.                               |
    | FIRST50    | max redemptions 50, redemptions 50           | This code has reached its redemption limit.                    |
    | PLUSONLY   | eligible only for plan "Plus"                | This code is not valid for the Core plan.                      |

Scenario: US-002-AC3 Only one code per subscription
  Given Tom has applied the code "LAKEMONT20"
  When he applies the code "WELCOME50"
  Then he is asked to confirm replacing "LAKEMONT20" with "WELCOME50"
  And after he confirms, only "WELCOME50" is attached to the sign-up

Scenario: US-002-AC4 The last redemption cannot be used twice
  Given the code "FIRST50" has max redemptions 50 and 49 redemptions
  When two agencies submit sign-ups with "FIRST50" at the same moment
  Then exactly one sign-up keeps the code and the redemption count becomes 50
  And the other agency sees "This code has reached its redemption limit." and can submit without the code

Scenario: US-002-AC5 Code matching ignores case and surrounding spaces
  When Tom applies the code " lakemont20 "
  Then the code "LAKEMONT20" is applied
```

**Notes**
- Validation calls `POST /promo-codes/validate`; a redemption is counted only when the sign-up is submitted, not when the code is checked.
- Fixed-amount codes apply to the monthly subscription invoice total, not per seat (confirmed with the Product Owner on 2026-03-04).
- Analytics: code acceptance and rejection reasons per code, to show Platform Administrators which campaigns fail.
- Out of scope: stacking codes and agency-to-agency invite codes (BR-004 allows one code per subscription).

### US-003 · Verify my email and complete the setup checklist

| Field | Value |
|---|---|
| Epic | EP-01 Agency Onboarding & Subscription |
| Persona | PER-05 Tom Brennan (AG-ADM) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S1 / R1 |
| Requirements | FR-ONB-02, FR-ONB-05 |
| Business rules | None |
| Dependencies | US-001 |

**Story**
As an agency owner, I want to verify my email address and then follow a setup checklist, so that my agency is activated securely and I know exactly what to configure before the first visit.

**Acceptance criteria**

```gherkin
Scenario: US-003-AC1 Verify within 24 hours and land on the checklist
  Given a verification email was sent to "tom.brennan@example.com" at 2026-03-16 09:00
  When Tom opens the link at 2026-03-17 08:59
  Then his email is marked verified and the tenant is activated
  And Tom is signed in and lands on the setup checklist showing "0 of 6 complete"

Scenario Outline: US-003-AC2 Reject an expired, used or altered link
  Given a verification email was sent at 2026-03-16 09:00
  When Tom opens <link> at <time>
  Then he sees "<message>"
  And the tenant stays "Pending"

  Examples:
    | link                        | time             | message                                                        |
    | the original link           | 2026-03-17 09:01 | This link has expired. Send a new verification email.          |
    | a link he has already used  | 2026-03-16 09:30 | This link has already been used. Sign in to continue.          |
    | a link with an altered token| 2026-03-16 09:05 | This link is not valid. Send a new verification email.         |

Scenario: US-003-AC3 Resending invalidates earlier links
  Given Tom requested a second verification email at 2026-03-16 10:00
  When he opens the first link at 2026-03-16 10:05
  Then he sees "This link is not valid. Send a new verification email."
  And the second link still verifies his email

Scenario Outline: US-003-AC4 Checklist items complete automatically
  Given Tom's tenant is active and the checklist shows "<before> of 6 complete"
  When <action>
  Then the item "<item>" is ticked without any manual step
  And the checklist shows "<after> of 6 complete"

  Examples:
    | before | action                                                        | item               | after |
    | 0      | Tom saves the location "Lakemont North"                       | Add a location     | 1     |
    | 1      | Tom confirms service line HOME_VISIT in settings              | Set service lines  | 2     |
    | 2      | Tom adds payer "Lakemont County Medicaid" of type Medicaid    | Add a payer        | 3     |
    | 3      | a caregiver profile is created                                | Add a caregiver    | 4     |
    | 4      | a client is admitted                                          | Add a client       | 5     |
    | 5      | the first visit is scheduled                                  | Create a schedule  | 6     |

Scenario: US-003-AC5 Checklist visibility and dismissal
  Given the checklist shows "4 of 6 complete"
  When Tom dismisses the checklist
  Then it is hidden from his home page and can be reopened from Settings
  And users without the AG-ADM role never see the checklist
  And when all 6 items are complete the checklist is replaced by "Setup complete" for 7 days and then hidden
```

**Notes**
- UX: each checklist item deep-links to the screen that completes it; wireframe referenced in the wireframe index.
- Analytics: time from activation to "6 of 6 complete" per tenant; pilot target is 5 business days or fewer.
- Security: verification tokens are single use, stored hashed and compared in constant time; the email contains no PHI.
- Out of scope: guided product tours.

### US-004 · Manage my subscription seats and payment method

| Field | Value |
|---|---|
| Epic | EP-01 Agency Onboarding & Subscription |
| Persona | PER-05 Tom Brennan (AG-ADM) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S1 / R1 |
| Requirements | FR-ONB-06 |
| Business rules | BR-002 |
| Dependencies | US-001, DEP-05 |

**Story**
As an agency owner, I want to see and manage my subscription seats and payment method, so that I am billed correctly for the clients we actually serve and our account never lapses by surprise.

**Acceptance criteria**

```gherkin
Scenario: US-004-AC1 View the subscription summary
  Given Harborview Home Care is Active on plan "Core" with 60 seats for the cycle 2026-09-01 to 2026-09-30
  When Tom opens Settings > Subscription
  Then he sees the plan, 60 seats, the number of active client seats so far this cycle, the next invoice date 2026-10-01 and its estimated amount
  And the payment method is shown only as the card brand and last 4 digits

Scenario: US-004-AC2 Prorate a seat increase within the cycle
  Given the cycle 2026-09-01 to 2026-09-30 was billed in advance for 60 seats at $14.00
  When the 62nd client becomes an active seat on 2026-09-16 because a visit is scheduled for them
  Then seats increase to 62
  And a proration charge of $14.00 is added (2 seats x $14.00 x 15/30 days)
  And Tom sees the proration on the next invoice preview

Scenario: US-004-AC3 Count a client as an active seat only once per cycle
  Given client C-10234 already counts as an active seat in the cycle
  When a second and third visit are scheduled for C-10234 in the same cycle
  Then the seat count does not change
  And a client with no scheduled visit in the cycle is not counted

Scenario: US-004-AC4 Seat decreases take effect next cycle
  Given the tenant has 62 seats in the current cycle
  When only 58 clients have a scheduled visit in the next cycle
  Then the next cycle is billed for 58 seats
  And no credit is issued for the current cycle

Scenario: US-004-AC5 Update the payment method securely
  When Tom replaces the card on file using the payment provider's hosted form
  Then the new card is shown as brand and last 4 digits only
  And an audit event "subscription.payment_method_updated" records Tom as actor
  And no card number, expiry or CVC reaches Tendwell servers

Scenario: US-004-AC6 Only Agency Administrators manage the subscription
  Given Denise Carter has the AG-FIN role and no subscription permission override
  When she opens Settings
  Then the Subscription page is not shown
  And a direct call to PATCH /v1/subscription returns 403 with an application/problem+json body
```

**Notes**
- Seat proration uses calendar days in the cycle, inclusive of the day the seat is added; amounts are rounded half-up to the cent.
- Out of scope: annual billing, invoicing by bank transfer, and mid-cycle plan downgrades (handled at cycle end).
- Open question (closed 2026-03-11): Should discharged clients release a seat mid-cycle? Decision: no; seats are counted per cycle, per BR-002.

### US-005 · Manage plans and promo codes

| Field | Value |
|---|---|
| Epic | EP-01 Agency Onboarding & Subscription |
| Persona | Platform Administrator (PLT-ADM) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S1 / R1 |
| Requirements | FR-ONB-08 |
| Business rules | BR-004 |
| Dependencies | US-007 |

**Story**
As a Platform Administrator, I want to create, edit and retire plans and promo codes in the Platform Console, so that we can run pricing and campaigns without a code release.

**Acceptance criteria**

```gherkin
Scenario: US-005-AC1 Create a plan that appears on sign-up
  When the Platform Administrator creates plan code "CORE", name "Core", price $14.00 per seat per month
  Then the plan is saved with status "Active"
  And it is listed by GET /v1/plans on the public sign-up site

Scenario: US-005-AC2 Retire a plan without disturbing existing subscribers
  Given 12 tenants subscribe to plan "Core"
  When the Platform Administrator retires plan "Core"
  Then "Core" is no longer offered on the sign-up site
  And the 12 tenants stay on "Core" at their current price until their plan is changed

Scenario Outline: US-005-AC3 Validate promo code settings
  When the Platform Administrator saves a promo code with <setting>
  Then the result is "<result>"

  Examples:
    | setting                                     | result                                              |
    | Percent discount of 20                      | Saved                                               |
    | Percent discount of 0                       | Rejected: enter a percentage from 1 to 100          |
    | Percent discount of 101                     | Rejected: enter a percentage from 1 to 100          |
    | Fixed discount of $0.00                     | Rejected: enter an amount greater than $0.00        |
    | expiry date earlier than today              | Rejected: the expiry date must be in the future     |
    | max redemptions of 0                        | Rejected: max redemptions must be 1 or more         |
    | code "lakemont20" when "LAKEMONT20" exists  | Rejected: this code already exists                  |

Scenario: US-005-AC4 Max redemptions cannot drop below current redemptions
  Given promo code "FIRST50" has 37 redemptions
  When the Platform Administrator sets max redemptions to 30
  Then the change is rejected with "Max redemptions cannot be lower than the 37 redemptions already made."

Scenario: US-005-AC5 Restrict plan and promo management to platform administrators
  Given a Platform Support Agent and an Agency Administrator are signed in
  When either calls POST /v1/platform/promo-codes
  Then the request returns 403
  And every successful plan or promo change by a Platform Administrator creates an audit event with before and after values
```

**Notes**
- The Platform Console requires MFA for every platform role (BR-006).
- Analytics: redemptions per code per week on the platform dashboard.
- Out of scope: tenant-specific negotiated pricing (handled by a dedicated plan in R1).

### US-006 · Move unpaid tenants to read-only without blocking care

| Field | Value |
|---|---|
| Epic | EP-01 Agency Onboarding & Subscription |
| Persona | System (SYS) |
| Priority | Must |
| Estimate | 3 points |
| Sprint / Release | S6 / R1 |
| Requirements | FR-ONB-07 |
| Business rules | BR-003 |
| Dependencies | US-004, US-025, US-049 |

**Story**
As the subscription lifecycle job, I want to move a tenant to Read-only when its trial or payments lapse and restore it as soon as payment succeeds, so that unpaid use is contained while caregivers can always deliver and record care.

**Acceptance criteria**

```gherkin
Scenario Outline: US-006-AC1 Start Read-only 7 days after the trigger
  Given tenant "Cedar Lane Adult Day Center" has no successful payment
  And <trigger> occurred at 2026-06-21 00:00 America/New_York
  When the lifecycle job runs at <run time>
  Then the tenant status is "<status>"

  Examples:
    | trigger                         | run time         | status   |
    | the trial expired               | 2026-06-27 23:59 | Trial    |
    | the trial expired               | 2026-06-28 00:00 | ReadOnly |
    | the third payment retry failed  | 2026-06-27 23:59 | Active   |
    | the third payment retry failed  | 2026-06-28 00:00 | ReadOnly |

Scenario: US-006-AC2 Warn the Agency Administrator during the grace period
  Given the trial expired at 2026-06-21 00:00
  When Tom signs in on 2026-06-25
  Then a banner states "Your account becomes read-only on 2026-06-28. Add a payment method to keep full access."
  And Tom receives an email and in-app notification with the same date and no PHI

Scenario: US-006-AC3 Read-only allows viewing and exporting but not office edits
  Given the tenant is "ReadOnly"
  When Marcus Hale tries to create a visit pattern
  Then the request returns 403 with problem type "tenant-read-only" and the message "Your agency account is read-only. Ask your administrator to update billing."
  And Marcus can still view the schedule board and export reports

Scenario: US-006-AC4 Care delivery stays available in Read-only
  Given the tenant is "ReadOnly"
  And Rosa Delgado has a visit scheduled today at 08:00
  When Rosa clocks in, records task statuses, documents a dose, writes the visit note and clocks out
  Then every action succeeds exactly as it would for an Active tenant
  And incident reporting from the Caregiver app also stays available

Scenario: US-006-AC5 Restore Active when payment succeeds
  Given the tenant is "ReadOnly"
  When the payment provider's webhook reports a successful payment at 10:12
  Then the tenant status is "Active" within 5 minutes
  And the Read-only banner is removed for all users

Scenario: US-006-AC6 The lifecycle job is single-flight
  Given two scheduler workers start the lifecycle job for the same night
  When both attempt to process tenant "Cedar Lane Adult Day Center"
  Then the status changes exactly once
  And exactly one Read-only notification is sent to each Agency Administrator
```

**Notes**
- Clarification (Product Owner and Clinical SME, 2026-05-19): BR-003 says "EVV clock-in stays available". The team agreed that the whole caregiver visit flow (clock-in, tasks, eMAR, vitals, notes, incidents, clock-out) stays available, because blocking any part of it would block or hide care.
- Clarification: the 7-day grace applies to both triggers, matching the configuration defaults.
- Single-flight execution follows ADR-003 (`job_executions` with a unique idempotency key).
- Out of scope: automatic cancellation. Cancellation and the 90-day retention are handled by Customer Success in R1.

## Related documents

- [Epics overview](../epics.md)
- [Story map](../story-map.md)
- [Release and sprint plan](../release-and-sprint-plan.md)
- [Software requirements specification](../../02-requirements/SRS.md)
- [Business rules catalog](../../02-requirements/business-rules.md)
- [Requirements traceability matrix](../../02-requirements/requirements-traceability-matrix.md)
- [ADR-003 Single-flight scheduled jobs](../../03-design/architecture/adr/ADR-003-single-flight-scheduled-jobs.md)
- [Wireframes index](../../03-design/wireframes/README.md)
- [Test cases](../../06-quality/test-cases.md)
