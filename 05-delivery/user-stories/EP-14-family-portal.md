# EP-14 Family Portal: user stories

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DEL-US-14 |
| Version | 1.1 |
| Status | Draft (Release 2 backlog) |
| Owner | Business Analyst |
| Last updated | 2026-09-28 |
| Reviewers | Product Owner, Compliance and Privacy Officer, UX Designer, Customer Success Lead |

## Purpose and scope

This file holds the Release 2 user stories for EP-14. The Family Portal gives a client's authorized family contact read-only visibility of visits, optional visit start and end notifications, and a message channel to the Care Coordinator. EP-14 was in the R1 baseline (SRS v1.0) and was deferred to Release 2 by CR-003 (SRS v1.1). The stories are refined to Definition of Ready level for discovery but are not yet sprint-planned; acceptance criteria will be revisited in R2 refinement, including the lessons of CR-006 on notification content.

## Epic

| Field | Value |
|---|---|
| Epic ID | EP-14 |
| Name | Family Portal |
| Module | FAM |
| Goal | Give a client's authorized family contact timely, read-only reassurance that visits happen as planned, and a simple way to reach the Care Coordinator, without exposing more PHI than the client has consented to share. |
| Objectives | No direct R1 KPI. R2 hypothesis: reduce inbound "did the aide come today?" calls to Coordinators by 30% at agencies that enable the portal. Supports OBJ-01 indirectly (families notice missed visits sooner). |
| Business need | BN-14 |
| Release | R2 |

## Story list

| Story | Title | Persona | Priority | Points | Sprint |
|---|---|---|---|---|---|
| US-053 | View my relative's visits | Family Contact (FAM) | Could | 8 | R2 |
| US-054 | Get notified when a visit starts and ends | Family Contact (FAM) | Could | 3 | R2 |
| **Total** | | | | **11** | |

## Stories

### US-053 · View my relative's visits

| Field | Value |
|---|---|
| Epic | EP-14 Family Portal |
| Persona | Family Contact (FAM) |
| Priority | Could |
| Estimate | 8 points |
| Sprint / Release | R2 (unscheduled) / R2 |
| Requirements | FR-FAM-01, FR-FAM-03 |
| Business rules | BR-001 |
| Dependencies | US-012, US-029, US-009 |

**Story**
As a family contact of a client, I want to see my relative's upcoming visits and summaries of completed visits and message the Care Coordinator, so that I know care is happening without calling the agency.

**Acceptance criteria**

```gherkin
Scenario: US-053-AC1 Invite a family contact only after consent
  Given C-10234's legal representative Jamie Kimball is a client contact with email "jamie.kimball@example.org"
  And no family-access consent is recorded
  When Marcus tries to invite Jamie to the Family Portal
  Then the invite is blocked with "Record the client's consent to share visit information before inviting a family contact."
  When Marcus records consent with the date, who gave it and the scope "Schedule and visit summaries"
  Then the invitation can be sent

Scenario: US-053-AC2 Show only the schedule and completed visit summaries
  Given Jamie accepted the invitation and signed in with MFA
  When Jamie opens the portal
  Then Jamie sees C-10234's visits for the next 14 days with date, time window and caregiver first name
  And for completed visits, the clock-in and clock-out times and which care-plan tasks were done
  And Jamie does not see visit notes, medications, vitals, diagnoses, incidents or billing

Scenario: US-053-AC3 Isolate data to one client and one tenant
  Given Jamie has access to C-10234 only
  When Jamie requests GET /v1/family/clients/{clientId}/visits for another client of the same agency or of another agency
  Then the API returns 404
  And row-level security returns no rows outside C-10234's tenant

Scenario: US-053-AC4 Message the Care Coordinator
  When Jamie sends the message "Mom has a doctor's appointment on Thursday at 10:00."
  Then the Coordinators of C-10234's location see it in the Agency Web App
  And the message and any reply are kept in the client's record and audited
  And the portal shows "For emergencies, call 911. Messages are answered during office hours."

Scenario: US-053-AC5 Withdrawing consent removes access at once
  Given Jamie is signed in to the portal
  When Marcus records that the client withdrew consent
  Then Jamie's next request returns 403 and the portal shows "Your access to this information has ended."
```

**Notes**
- Deferred by CR-003 (DEC-09): the consent model and minimum-necessary scope needed more privacy review than R1 allowed, and the pilot agencies ranked the portal lowest of the R1 features.
- MFA for family contacts, the consent scopes and the retention of messages are open questions for R2 discovery with the Compliance and Privacy Officer.
- Out of scope for R2: family access to clinical documentation or invoices.

### US-054 · Get notified when a visit starts and ends

| Field | Value |
|---|---|
| Epic | EP-14 Family Portal |
| Persona | Family Contact (FAM) |
| Priority | Could |
| Estimate | 3 points |
| Sprint / Release | R2 (unscheduled) / R2 |
| Requirements | FR-FAM-02 |
| Business rules | BR-056 |
| Dependencies | US-053, US-049 |

**Story**
As a family contact, I want an optional notification when a visit starts and ends, so that I know my relative has been seen without having to check the portal.

**Acceptance criteria**

```gherkin
Scenario: US-054-AC1 Notifications are off until the family contact opts in
  Given Jamie has just joined the Family Portal
  Then visit start and end notifications are off
  When Jamie switches them on for push and email
  Then they are sent for every visit of C-10234 from then on

Scenario: US-054-AC2 Send start and end notifications without PHI
  Given Jamie has opted in
  When the caregiver clocks in at 08:02 and clocks out at 09:58
  Then Jamie receives "Today's visit has started. Open the Family Portal for details." at clock-in
  And "Today's visit has ended. Open the Family Portal for details." at clock-out
  And neither message contains the client's name, the caregiver's name or the address

Scenario Outline: US-054-AC3 Skip stale notifications from offline punches
  Given a clock-in captured offline at 08:02
  When the punch syncs at <sync time>
  Then the start notification is <result>

  Examples:
    | sync time | result                                                   |
    | 08:40     | sent, saying the visit started at 08:02                  |
    | 09:03     | not sent; the portal shows the visit start time          |

Scenario: US-054-AC4 Quiet hours apply
  Given a supported-living visit ends at 21:30
  Then the end notification is held and sent at 07:00, or dropped if a newer notification for the same visit exists

Scenario: US-054-AC5 Notifications stop when access ends
  Given Jamie's portal access was removed because consent was withdrawn
  When the next visit starts
  Then no notification is sent to Jamie
```

**Notes**
- The 60-minute staleness limit in AC3 is a proposal for R2 refinement.
- Recipients are resolved at send time (BR-054), reusing the CR-006 design.
- SMS for family contacts is out of scope until the consent scope covers phone numbers.

## Related documents

- [Epics overview](../epics.md)
- [Product roadmap](../product-roadmap.md)
- [Change request log](../change-request-log.md)
- [Decision log](../decision-log.md)
- [Software requirements specification](../../02-requirements/SRS.md)
- [Business rules catalog](../../02-requirements/business-rules.md)
- [Compliance mapping](../../02-requirements/compliance-mapping.md)
- [Personas](../../01-discovery/personas.md)
