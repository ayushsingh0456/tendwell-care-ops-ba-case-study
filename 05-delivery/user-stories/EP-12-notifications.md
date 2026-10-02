# EP-12 Notifications & Escalations: user stories

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DEL-US-12 |
| Version | 1.3 |
| Status | Baselined |
| Owner | Business Analyst |
| Last updated | 2026-09-24 |
| Reviewers | Product Owner, Engineering Lead, QA Lead, Compliance and Privacy Officer |

## Purpose and scope

This file holds the user stories and acceptance criteria for EP-12. It covers notification channels and preferences, quiet hours, PHI-free message content, configurable escalation ladders, deduplication and retries. The notification service carries the urgent clinical alerts of EP-07 and EP-08, so its rules are safety rules as much as convenience rules.

Version 1.3 aligns US-049 and US-050 with CR-006 (SRS v1.3, raised from INC-2026-015): recipients are resolved at send time from active users, and email bodies, like SMS and push, carry no PHI.

## Epic

| Field | Value |
|---|---|
| Epic ID | EP-12 |
| Name | Notifications & Escalations |
| Module | NTF |
| Goal | Deliver the right message to the right active person on the right channel at the right time, with no PHI in message bodies, no duplicates and escalation that stops as soon as the problem is fixed. |
| Objectives | OBJ-03 Undocumented doses (missed-dose escalation); OBJ-05 Credential lapses (expiry reminders); OBJ-01 EVV completeness (exception alerts). Guardrail: zero notifications to deactivated users (NFR-OBS-02). |
| Business need | BN-12 |
| Release | R1 |

## Story list

| Story | Title | Persona | Priority | Points | Sprint |
|---|---|---|---|---|---|
| US-049 | Choose notification channels and respect quiet hours | PER-01 Rosa Delgado (CG) | Must | 5 | S2 |
| US-050 | Configure escalation ladders | PER-05 Tom Brennan (AG-ADM) | Must | 8 | S4 |
| **Total** | | | | **13** | |

## Stories

### US-049 · Choose notification channels and respect quiet hours

| Field | Value |
|---|---|
| Epic | EP-12 Notifications & Escalations |
| Persona | PER-01 Rosa Delgado (CG) |
| Priority | Must |
| Estimate | 5 points |
| Sprint / Release | S2 / R1 |
| Requirements | FR-NTF-01, FR-NTF-02, FR-NTF-05 |
| Business rules | BR-053, BR-056 |
| Dependencies | US-007, DEP-01 |

**Story**
As a caregiver, I want to choose how Tendwell contacts me and not be disturbed at night by anything that can wait, so that I see what matters without my phone buzzing all evening.

**Acceptance criteria**

```gherkin
Scenario: US-049-AC1 Choose channels per event type
  When Rosa sets "Schedule changed" to Push and SMS and "Credential expiring" to In-app only
  Then a schedule change is delivered to her by push and SMS
  And a credential reminder appears only in her in-app inbox
  And In-app delivery cannot be switched off for any event type

Scenario Outline: US-049-AC2 Hold non-urgent notifications during quiet hours
  Given the tenant time zone is America/New_York
  When a <kind> notification for Rosa is created at <time>
  Then it is <result>

  Examples:
    | kind                        | time  | result                     |
    | non-urgent schedule change  | 20:59 | sent immediately           |
    | non-urgent schedule change  | 21:00 | held and sent at 07:00     |
    | non-urgent schedule change  | 06:59 | held and sent at 07:00     |
    | non-urgent schedule change  | 07:00 | sent immediately           |
    | urgent missed-dose alert    | 23:15 | sent immediately           |

Scenario Outline: US-049-AC3 Keep PHI out of every external channel
  When a "Schedule changed" notification for a visit to C-10234 is sent by <channel>
  Then the message text is "<text>"
  And it contains no client name, initials, diagnosis, medication or address

  Examples:
    | channel | text                                                                         |
    | SMS     | Tendwell: your schedule changed. Open the app to see details.                |
    | Push    | Your schedule changed. Tap to see details.                                   |
    | Email   | Your schedule changed. Sign in to Tendwell to see details. (with deep link)  |

Scenario: US-049-AC4 Deep links require sign-in
  Given Rosa's session has expired
  When she taps the deep link in a notification
  Then she is asked to sign in or confirm her device PIN
  And she then lands on the changed visit

Scenario: US-049-AC5 Release held notifications in order
  Given 3 non-urgent notifications for Rosa were held between 21:10 and 23:50
  When the time reaches 07:00
  Then they are delivered in the order they were created
  And a notification whose visit was later cancelled is delivered as the cancellation only
```

**Notes**
- Before CR-006, email bodies could include the client's first name, last initial and incident category; INC-2026-015 showed that this was unsafe, and AC3 now covers email as well as SMS and push.
- The SMS vendor operates under a BAA (DEP-01), but message content is still PHI-free by design (minimum necessary, NFR-PRIV-01).
- Quiet hours follow the tenant's time zone, not the device's.
- Out of scope: per-user quiet-hour settings (R2 candidate).

### US-050 · Configure escalation ladders

| Field | Value |
|---|---|
| Epic | EP-12 Notifications & Escalations |
| Persona | PER-05 Tom Brennan (AG-ADM) |
| Priority | Must |
| Estimate | 8 points |
| Sprint / Release | S4 / R1 |
| Requirements | FR-NTF-03, FR-NTF-04 |
| Business rules | BR-054, BR-055 |
| Dependencies | US-049, US-009 |

**Story**
As an Agency Administrator, I want to configure who is alerted, how and after what delay when an urgent event is not handled, so that nothing urgent sits unnoticed and escalation stops as soon as someone acts.

**Acceptance criteria**

```gherkin
Scenario: US-050-AC1 Configure a ladder by role
  When Tom configures the ladder for "Client incident - High severity" as:
    | step | delay  | recipient role | channels          |
    | 1    | 0 min  | AG-SUPV        | Push, SMS, Email  |
    | 2    | 15 min | AG-ADM         | Push, SMS         |
    | 3    | 30 min | AG-COORD       | Push, SMS         |
  Then the ladder is saved and audited with before and after values
  And it applies to new incidents in every location of the tenant

Scenario: US-050-AC2 Stop escalating once the condition is resolved
  Given a High severity incident was reported at 14:00 and step 1 was sent
  When Priya opens the incident and sets it to "UnderReview" at 14:09
  Then step 2 at 14:15 and step 3 at 14:30 are not sent

Scenario: US-050-AC3 Resolve recipients at send time from active users
  Given the ladder was configured when Coordinator "Casey Lund" was active in "Lakemont North"
  And Casey Lund was deactivated on 2026-09-01
  When step 3 fires for an incident in "Lakemont North" on 2026-09-09
  Then the recipients are the users who are active and hold AG-COORD in "Lakemont North" at that moment
  And Casey Lund receives nothing on any channel
  And if no active user holds the role in that location, the step goes to the tenant's Agency Administrators and the ladder shows a configuration warning

Scenario Outline: US-050-AC4 Deduplicate by event, recipient and step
  Given notification <first> was already queued
  When notification <second> is created
  Then <result>

  Examples:
    | first                          | second                         | result                         |
    | event E1, Priya, step 1        | event E1, Priya, step 1        | no second notification         |
    | event E1, Priya, step 1        | event E1, Priya, step 2        | a second notification is sent  |
    | event E1, Priya, step 1        | event E2, Priya, step 1        | a second notification is sent  |

Scenario: US-050-AC5 Retry failed deliveries at 1, 4 and 16 minutes
  Given an SMS to Priya fails at 14:00:00
  Then it is retried at 14:01:00, 14:05:00 and 14:21:00
  And if the third retry fails, the notification status is "Failed" and it stays visible in Priya's in-app inbox

Scenario Outline: US-050-AC6 Validate ladder configuration
  When Tom saves a ladder with <setting>
  Then it is rejected with "<message>"

  Examples:
    | setting                                    | message                                                      |
    | step 2 delay 10 min after step 1 at 15 min | Each step must start later than the step before it.          |
    | a step with no recipient role              | Choose a recipient role for each step.                       |
    | no steps for an urgent event type          | Urgent event types need at least one step.                   |
```

**Notes**
- AC3 was rewritten by CR-006 after INC-2026-015, in which an escalation email reached a deactivated former Coordinator because recipients had been cached when the ladder was configured. Ladders now store roles only, never user IDs.
- NFR-OBS-02 alerts on any notification addressed to a deactivated user; the target is zero.
- Dose escalation timing (BR-030) is fixed by the clinical rule; the ladder controls recipients and channels, not the 60-minute thresholds.
- Clarification of BR-055: the 1, 4 and 16 minutes are the waits between attempts (exponential backoff, factor 4), so retries happen 1, 5 and 21 minutes after the first failure. Confirmed with the Engineering Lead on 2026-04-22.

## Related documents

- [Epics overview](../epics.md)
- [Change request log](../change-request-log.md)
- [Software requirements specification](../../02-requirements/SRS.md)
- [Business rules catalog](../../02-requirements/business-rules.md)
- [Events and webhooks](../../04-api/events-and-webhooks.md)
- [Data classification and retention](../../03-design/data/data-classification-and-retention.md)
- [INC-2026-015 Escalation email to a deactivated user](../../07-operations/incidents/INC-2026-015-escalation-email-to-deactivated-user.md)
- [Test cases](../../06-quality/test-cases.md)
