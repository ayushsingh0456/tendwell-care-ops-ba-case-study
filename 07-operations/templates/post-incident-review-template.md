# Post-Incident Review: INC-YYYY-NNN <Short title>

<!--
How to use this template
- Copy it to 07-operations/incidents/INC-YYYY-NNN-short-title.md.
- Replace every <placeholder>. Delete guidance blocks (lines starting with ">") before approval.
- Write blamelessly: name roles, not people. "Human error" is never a root cause.
- No PHI anywhere in this document: use counts, record identifiers such as invoice numbers or client numbers only where needed, and never client names.
- Times are 24-hour, in the tenant time zone (America/New_York for the pilot tenants). Dates are ISO (YYYY-MM-DD).
- Owner: Business Analyst. Accountable: Incident Commander.
-->

## Document control

| Field | Value |
|---|---|
| Document ID | PIR-YYYY-NNN |
| Version | 0.1 |
| Status | Draft / In review / Approved |
| Owner | Business Analyst |
| Last updated | YYYY-MM-DD |
| Reviewers | Incident Commander (role), Technical Lead (role), Communications Lead (role), QA Lead, Product Owner, and the Compliance and Privacy Officer or Clinical SME where relevant |

## Incident summary

| Field | Value |
|---|---|
| Incident ID | INC-YYYY-NNN |
| Title | <Plain-language title that a customer would understand> |
| Severity | SEV-<n> (<privacy> if applicable) |
| Status | Open / Resolved / Closed |
| Incident date | YYYY-MM-DD |
| Start (trigger) | YYYY-MM-DD HH:MM ET |
| Detected | YYYY-MM-DD HH:MM ET (<alert / ticket / customer call>) |
| Mitigated | YYYY-MM-DD HH:MM ET |
| Resolved | YYYY-MM-DD HH:MM ET |
| Duration (start to resolved) | <h> h <m> min |
| Incident Commander | <role> |
| PIR author | Business Analyst |
| Reviewers | <roles> |
| Related CR | CR-00N or None |
| Related ADR / NFR | ADR-00N, NFR-<CAT>-NN |

> Guidance: "Start" is when the system first behaved incorrectly, which is often earlier than anyone noticed. "Detected" is when the first signal reached Tendwell Labs, even if nobody recognized it. Keep these honest; they drive MTTD and MTTA.

## 1. Executive summary

> Guidance: five to eight sentences for a reader who will read nothing else. What happened, who was affected, how much, how it was fixed, the root cause in one sentence, and the most important corrective action. No jargon.

<Summary>

## 2. Customer and business impact

> Guidance: the Business Analyst completes this from the impact analysis. Quantify everything. State what did not happen as well (for example "No caregiver was blocked from clocking in").

| Dimension | Impact |
|---|---|
| Tenants affected | <number> of <live tenants>; <which service lines> |
| Users affected | <roles and counts> |
| Records affected | <entity and count, for example 214 draft invoices> |
| Money | <amounts moved, refunded, at risk> |
| Care delivery | <any effect on visits, doses, alerts> |
| Compliance | <EVV completeness, payroll deadlines, PHI, BAA obligations> |
| Downstream workflows | <payroll export, billing, aggregator export, notifications> |

## 3. Timeline

> Guidance: the Scribe's channel log is the source. Include the trigger, the first signal, every escalation, each mitigation, each customer communication and resolution. Mark the key points (start, detect, acknowledge, mitigate, resolve) in bold.

| Time (ET) | Event | Actor (role) |
|---|---|---|
| YYYY-MM-DD HH:MM | **Start:** <trigger> | System |
| YYYY-MM-DD HH:MM | **Detected:** <first signal> | <role> |
| YYYY-MM-DD HH:MM | **Acknowledged:** <who started triage> | <role> |
| YYYY-MM-DD HH:MM | Severity declared SEV-<n>; IC assigned | <role> |
| YYYY-MM-DD HH:MM | **Mitigated:** <action> | <role> |
| YYYY-MM-DD HH:MM | Status page / customer email sent | Communications Lead |
| YYYY-MM-DD HH:MM | **Resolved:** <state> | IC |

## 4. Detection analysis

> Guidance: why did detection take as long as it did? Which signal existed but was not watched? Which alert would have caught it, and how fast? Compare with the MTTD target for this severity.

<Analysis>

## 5. Response analysis

> Guidance: assess acknowledgement, mobilization, mitigation choice, communications and data correction against the severity targets. Note decisions that worked and decisions that cost time.

| Measure | Target (severity matrix) | Actual | Met? |
|---|---|---|---|
| Acknowledge | | | |
| IC assigned | | | |
| First status page post | | | |
| Update cadence | | | |
| Mitigation | n/a | | |

## 6. Root cause analysis

### 6.1 Five whys

> Guidance: start from the customer-visible symptom. Stop when you reach a cause the organization can change. If the chain branches, show the branches.

1. Why <symptom>? Because <cause 1>.
2. Why <cause 1>? Because <cause 2>.
3. Why <cause 2>? Because <cause 3>.
4. Why <cause 3>? Because <cause 4>.
5. Why <cause 4>? Because <root cause>.

**Root cause statement:** <one sentence>.

### 6.2 Contributing factors

> Guidance: the Business Analyst classifies each factor. "Requirements" means the specification was missing, ambiguous or wrong; "Technology" means the system did not behave as specified or a technical design was fragile; "Process" covers release, testing, triage and operations; "People" covers knowledge, staffing and handoffs (never blame).

| Category | Factor |
|---|---|
| Requirements | |
| Technology | |
| Process | |
| People | |

### 6.3 Requirement-gap classification

| Cause | Requirements gap / Implementation defect / Test gap | Evidence (requirement ID and version) |
|---|---|---|
| | | |

## 7. What went well, what went poorly, where we got lucky

| What went well | What went poorly | Where we got lucky |
|---|---|---|
| | | |

> Guidance: "lucky" items are near misses. Each one should map to a CAPA item or an explicit decision to accept the risk.

## 8. Corrective and preventive actions

> Guidance: every action has one owner role and a date. Types: Prevent (stop recurrence), Detect (find it faster), Mitigate (reduce impact), Process (change how we work). Tracking ref links to CR, NFR, ADR, test case or backlog item. An action closes only when effectiveness is verified.

| ID | Action | Type | Owner (role) | Due | Status | Tracking ref |
|---|---|---|---|---|---|---|
| CAPA-NNN-01 | | Prevent | | YYYY-MM-DD | Open | |

## 9. Requirement and documentation changes

> Guidance: list every FR, BR, NFR, ADR, test case and runbook that changed, with the SRS version that baselined the change. Quote old and new wording for rules.

| Artifact | Change | Baselined in |
|---|---|---|
| | | SRS v<x.y> |

## 10. Lessons learned

> Guidance: three to five lessons that apply beyond this incident. Write each as something the team now does differently.

1. <Lesson>

## 11. Privacy assessment (privacy incidents only)

> Guidance: completed by the Compliance and Privacy Officer, with data facts from the Business Analyst. Delete this section for non-privacy incidents. The final breach determination rests with the covered entity; this section is Tendwell's input to that determination and is not legal advice.

### 11.1 Four-factor assessment (45 CFR 164.402)

| Factor | Facts | Assessment |
|---|---|---|
| 1. Nature and extent of PHI, including identifiers and likelihood of re-identification | | |
| 2. The unauthorized person who used or received the PHI | | |
| 3. Whether the PHI was actually acquired or viewed | | |
| 4. Extent to which the risk has been mitigated | | |

### 11.2 Notification timeline

| Time (ET) | Event | Owner |
|---|---|---|
| | Discovery | |
| | Initial notice to covered entity | Compliance and Privacy Officer |
| | Written report to covered entity | Compliance and Privacy Officer |

### 11.3 Recipient deletion attestation

| Field | Value |
|---|---|
| Requested | |
| Received | |
| Scope | |
| Obtained through | |

## 12. Data correction and reconciliation (where data was changed)

> Guidance: describe each correction, the rule used to choose records, the dry-run reconciliation, and the final counts. Corrections void, supersede or append; they never delete business records.

| Step | Rule | Records | Verified by |
|---|---|---|---|
| | | | |

## Appendix A. Key metrics

| Metric | Value |
|---|---|
| Time to detect | |
| Time to acknowledge | |
| Time to mitigate | |
| Time to resolve (from detection) | |
| Duration (start to resolved) | |

## Appendix B. Customer communication excerpt

```text
<Paste the key customer-facing message, with no PHI.>
```

## Approval

| Role | Decision | Date |
|---|---|---|
| Incident Commander | | |
| Product Owner | | |
| Compliance and Privacy Officer (privacy incidents) | | |
| Business Analyst (author) | Prepared | |

## Related documents

- [Incident management process](../incident-management-process.md)
- [Incident register](../incident-register.csv)
- [Change request log](../../05-delivery/change-request-log.md)
- [Software requirements specification](../../02-requirements/SRS.md)
- [Requirements traceability matrix](../../02-requirements/requirements-traceability-matrix.md)
- [Test cases](../../06-quality/test-cases.md)
