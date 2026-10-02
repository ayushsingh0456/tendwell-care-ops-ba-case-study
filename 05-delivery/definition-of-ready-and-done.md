# Definition of Ready and Definition of Done

## Document control

| Field | Value |
|---|---|
| Document ID | TW-DEL-005 |
| Version | 1.3 |
| Status | Approved |
| Owner | Business Analyst |
| Last updated | 2026-09-24 |
| Reviewers | Product Owner, Engineering Lead, QA Lead, UX Designer, Compliance and Privacy Officer |

## Purpose and scope

This document defines when work is ready to enter a sprint and when it is done, at three levels: story, sprint and release. It is the working agreement for the Tendwell delivery team and is reviewed at every third retrospective. Items marked **[BA]** are owned by the Business Analyst; the BA confirms them in Jira before refinement closes. Version history:

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-03-06 | Baseline agreed at sprint 0 |
| 1.1 | 2026-04-03 | Added the PHI classification check to the story DoR (S2 retrospective) |
| 1.2 | 2026-05-15 | Added the worked-example rule for stories above 8 points (S5 retrospective) and the external-dependency rule (S4 retrospective) |
| 1.3 | 2026-09-24 | Added the device-matrix, single-flight and recipient checks to the story DoD after INC-2026-007, INC-2026-011 and INC-2026-015 |

## Definition of Ready

### Story level

A story enters sprint planning only when every item is checked.

**Value and structure**
- [ ] The story uses the format "As a ..., I want ..., so that ..." and names a persona (PER-01 to PER-05) or a role code.
- [ ] It meets INVEST. It is independent enough to deliver alone, negotiable, valuable to a named user, estimable, small (8 points or fewer, 13 only with a signed-off worked example) and testable.
- [ ] Priority (MoSCoW) and target sprint are agreed with the Product Owner.

**Requirements and rules**
- [ ] **[BA]** The story is linked to its FR IDs and BR IDs, and every BR it relies on is linked in the story table.
- [ ] **[BA]** Configuration defaults used in the acceptance criteria match the single source of truth (for example 150 m geofence, 90 s identity check, 15-minute units with 8-minute rounding).
- [ ] **[BA]** Any change to an approved requirement goes through a change request. The CR ID is referenced and the CR is Approved.
- [ ] **[BA]** Stories above 8 points have a worked example signed off by the domain owner, such as the E-2041 payroll example or the C-10234 billing example.

**Acceptance criteria**
- [ ] **[BA]** There are 3 to 6 Gherkin scenarios with IDs `US-NNN-ACn`, covering the happy path, at least one negative case, boundaries (Scenario Outline with Examples) and permissions.
- [ ] **[BA]** Acceptance criteria were reviewed with QA in refinement, and the QA Lead confirmed each scenario is testable with known test data.
- [ ] User-facing messages state the problem and the fix (NFR-USE-03), and the exact text is in the scenario.

**Design, data and compliance**
- [ ] **[BA]** A UX wireframe or an annotated screenshot is attached for any new or changed screen, and accessibility notes are included (WCAG 2.2 AA).
- [ ] **[BA]** The data and PHI classification is checked. New fields are classified in the data dictionary, PHI fields are marked for field-level encryption and masking, and notification content contains no PHI.
- [ ] Clinical stories (EP-07, EP-08) are reviewed by the Clinical SME, and privacy-relevant stories by the Compliance and Privacy Officer.
- [ ] API changes are drafted in the OpenAPI contract (path, schemas, problem types).

**Dependencies**
- [ ] Story dependencies are Done or planned earlier in the same sprint.
- [ ] External dependencies have a needed-by date, an owner and a status in the RAID log (DEP-NN), and none is Red.
- [ ] **[BA]** The traceability matrix row exists for each FR in the story.

### Sprint level

- [ ] At least 1.5 sprints of stories meet the story DoR before planning.
- [ ] Capacity is calculated from availability, holidays and planned leave against the 48-point planned velocity.
- [ ] The sprint goal is written in one sentence and agreed with the Product Owner.
- [ ] Stretch items are marked and limited to 5 points.
- [ ] Test data needs are listed, with synthetic data only (555-01xx phones, example.com emails, ZZ Medicaid IDs).
- [ ] Risks that could affect the sprint are reviewed in the RAID log.

### Release level

- [ ] Release goal and scope are agreed in the roadmap; the SRS version for the release is baselined.
- [ ] Every story in scope has an Approved status in the traceability matrix.
- [ ] UAT participants, the UAT plan and the environments are booked.
- [ ] Contracts and BAAs needed for the release are signed or have dated plans (NFR-CMP-01).

## Definition of Done

### Story level

A story is Done only when every item applies or is explicitly marked not applicable with a reason.

**Build and test**
- [ ] Code is merged to main through a reviewed pull request. CI is green, with lint, unit, integration and contract tests passing.
- [ ] Every acceptance criterion has at least one passing automated or documented manual test, linked by AC ID to a test case (TC-MOD-NNN).
- [ ] Every BR the story implements has at least one automated test (NFR-MNT-01). Domain modules (EVV, payroll, billing, eMAR) keep line coverage at 80% or more.
- [ ] Mobile stories are tested on the agreed device matrix, including iOS "Precise Location: Off" and Android "Approximate location" since v1.3, and at 200% font scaling.
- [ ] Scheduled or background jobs are proven single-flight by a test that runs two workers at once (ADR-003; added after INC-2026-007).
- [ ] Notification changes are tested with a deactivated user in the recipient role, and the test shows nothing is sent (added after INC-2026-015).

**Security, privacy and quality**
- [ ] Permissions are enforced server-side. There is a test for an unauthorized role and a test for cross-tenant access returning 404.
- [ ] No PHI appears in logs, notification bodies or analytics events. Secret scanning passes (NFR-SEC-03).
- [ ] Audit events are written for every create, update, delete, reveal and export that the story introduces.
- [ ] Web screens pass automated accessibility checks and a keyboard-only walkthrough.
- [ ] Performance budgets in the related NFRs are met in the CI performance smoke test.

**Documentation and traceability**
- [ ] **[BA]** The traceability matrix is updated (FR, BR, US, AC and TC links), and the story status in Jira is Done.
- [ ] **[BA]** Any rule clarification made during the sprint is recorded in the story notes. If it changes a requirement, it is raised as a change request.
- [ ] The OpenAPI contract and the events catalog match the implementation.
- [ ] Feature flags are named and defaulted. Configuration defaults are documented.
- [ ] The Product Owner accepted the story in the sprint review or earlier.

### Sprint level

- [ ] All committed stories are Done. Carry-overs are re-estimated and explained in the sprint report.
- [ ] The increment is deployed to staging with zero-downtime migrations that are backward-compatible for one release (NFR-MNT-02).
- [ ] The regression suite passes on staging.
- [ ] The sprint review demonstrates the goal with synthetic data. Pilot agency feedback is captured and triaged into the backlog or a change request.
- [ ] The burn-up, the RAID log and the decision log are updated. Retrospective actions have owners.

### Release level

- [ ] All Must stories are Done. Should and Could stories are Done or formally deferred with Product Owner approval.
- [ ] UAT exit criteria are met and signed off by each participating agency.
- [ ] There are no open Critical or High defects, and no open Critical or High penetration test findings (NFR-SEC-02).
- [ ] NFR evidence is collected for performance, availability, disaster-recovery restore, accessibility and mobile.
- [ ] Release notes, user guides and training materials are published, and the support team has been briefed.
- [ ] Runbooks, dashboards, SLO burn-rate alerts and business anomaly alerts (NFR-OBS-02) are live, and the on-call rotation is staffed.
- [ ] **[BA]** The SRS version, revision history and traceability matrix are baselined for the release. Change requests included in the release are marked Implemented.
- [ ] Go/no-go criteria are reviewed, and the decision is recorded in the decision log.

## How the BA applies these checks

| Moment | BA check | Evidence |
|---|---|---|
| Refinement (day 3 of each sprint) | DoR items marked [BA] for the next 1.5 sprints | Jira "Ready" status with checklist complete |
| Three amigos (BA, developer, QA) per story | AC walk-through, boundary values, negative cases and message text | Comments on the story; QA Lead approval |
| Sprint review | Acceptance of each story against its AC | Product Owner acceptance in Jira |
| Release readiness | Traceability and SRS baselines | RTM export attached to the go/no-go pack |

## Related documents

- [Release and sprint plan](release-and-sprint-plan.md)
- [User stories, EP-01 to EP-14](user-stories/EP-01-agency-onboarding.md)
- [Change request log](change-request-log.md)
- [Requirements traceability matrix](../02-requirements/requirements-traceability-matrix.md)
- [Data classification and retention](../03-design/data/data-classification-and-retention.md)
- [Data dictionary](../03-design/data/data-dictionary.md)
- [API guidelines](../04-api/api-guidelines.md)
- [Test strategy and plan](../06-quality/test-strategy-and-plan.md)
- [ADR-003 Single-flight scheduled jobs](../03-design/architecture/adr/ADR-003-single-flight-scheduled-jobs.md)
