# ADR-004: Identity verification through a third-party liveness vendor behind `IdentityVerificationPort`

## Document control

| Field | Value |
|---|---|
| Document ID | ADR-004 |
| Version | 1.0 |
| Status | Accepted |
| Owner | Business Analyst |
| Last updated | 2026-04-08 |
| Reviewers | Engineering Lead, Compliance and Privacy Officer, UX Designer, QA Lead |

## Status

**Accepted, 2026-04-08**, before Sprint S4 (US-026). Deciders: Engineering Lead, Compliance and Privacy Officer, Product Owner. Consulted: Business Analyst, mobile developer, UX Designer.

## Context and problem statement

Pilot agencies reported proxy clock-ins: one caregiver clocking in for another, or a family member operating the caregiver's phone. FR-EVV-04 (Should) lets a tenant require a selfie liveness check matched server-side against the caregiver's enrolled reference; a successful result is valid for 90 seconds and for one punch only (BR-024). The identity check must complete with a p95 of 4 s or less (NFR-PERF-02) and must not slow the 3-tap clock-in target (NFR-USE-01) more than necessary.

Face images and templates are biometric identifiers. They are sensitive under HIPAA when linked to care records and are regulated by some state biometric privacy laws. The team has no computer-vision specialists, and presentation-attack detection (printed photos, screen replays, masks) is a specialized field with its own test standard (ISO/IEC 30107-3).

How should Tendwell verify that the enrolled caregiver is physically present at clock-in without building biometric technology in-house or retaining images?

## Decision drivers

1. Server authority: the device must not be able to declare a pass (the same principle as server-computed distance in BR-021).
2. Resistance to presentation attacks, evidenced by independent testing.
3. No raw images retained by Tendwell; minimum biometric data overall (NFR-PRIV-01).
4. Vendor replaceability as the market changes; no vendor types in domain code.
5. Latency within NFR-PERF-02 and a graceful path when the vendor is down, because care must never be blocked.
6. Coverage under a BAA (NFR-CMP-01).

## Considered options

### Option 1: On-device face match

The app compares a selfie with a reference template stored on the device and sends pass or fail.

| Pros | Cons |
|---|---|
| Works offline; fast | The device declares the result; a modified app or rooted phone can fake a pass |
| No vendor cost | Liveness on device without vendor PAD is weak against replays |
| | Templates stored on many devices widen the biometric footprint |

### Option 2: In-house server-side matching with an open-source model

| Pros | Cons |
|---|---|
| Server authority; no per-check vendor fee | No in-house expertise for model accuracy, demographic bias testing or presentation-attack detection |
| | Tendwell would process and transiently hold raw images, enlarging the security scope |
| | Ongoing model maintenance competes with the core roadmap |

### Option 3: Third-party liveness and face match behind `IdentityVerificationPort` (chosen)

The vendor SDK guides capture on the device and produces an encrypted, vendor-signed capture package. The API forwards it to the vendor, which performs liveness and a 1:1 match against the caregiver's enrolled reference and returns the result to the server.

| Pros | Cons |
|---|---|
| Server-side result; the device cannot read or alter the package | Per-check vendor cost |
| Vendor provides independently tested presentation-attack detection | Dependency on vendor availability and latency |
| Tendwell stores no images; the vendor holds the enrolled template under contract | Vendor must sign a BAA and meet deletion terms |
| Port isolates vendor specifics; switching vendors means a new adapter and re-enrollment | Matching needs connectivity, so offline captures are matched only at sync |

### Option 4: Alternatives without biometrics (PIN, client signature, telephony)

| Pros | Cons |
|---|---|
| No biometric data | A PIN is shared as easily as a phone; client signatures are unreliable for clients with cognitive impairment |
| Cheap | Does not address the proxy clock-in problem pilots raised |

## Decision outcome

**Chosen option: Option 3, a third-party liveness and face-match vendor behind `IdentityVerificationPort`**, because it keeps the result under server authority (driver 1), gives tested presentation-attack detection (driver 2) and keeps raw images out of Tendwell (driver 3), while the port keeps the vendor replaceable (driver 4).

### Port

```text
IdentityVerificationPort
  enroll(caregiverId, capturePackage)   -> { enrollmentRef }
  verify(enrollmentRef, capturePackage) -> { livenessPassed, matchScore, vendorTxnId }
  deleteEnrollment(enrollmentRef)       -> void
```

Domain code depends only on this interface. The adapter handles vendor authentication, a 6-second timeout per attempt with one retry (interface IF-06 in the SRS; the 4 s figure in NFR-PERF-02 is the p95 target, not the timeout) and a circuit breaker.

### Rules

1. **Enrollment.** At onboarding, the caregiver consents in the app and enrolls through the SDK. Tendwell stores only `caregivers.identity_enrolled = true` and the vendor `enrollmentRef` (encrypted). The agency remains responsible for any state biometric-privacy notice and consent obligations; the consent text is tenant-configurable.
2. **Verification.** `POST /visits/{visitId}/identity-checks` receives the capture package. The API calls `verify`, then inserts an `identity_checks` row with `result` (Pass when liveness passed and the score meets the platform threshold), `match_score`, `liveness_passed` and `expires_at = now() + 90 s`. The package is held in memory only, never written to disk, logs, traces or S3.
3. **Single use.** `POST /visits/{visitId}/clock-in` (or clock-out) includes `identityCheckId`. The server consumes it atomically: `UPDATE identity_checks SET consumed_at = now() WHERE id = $1 AND caregiver_id = $2 AND visit_id = $3 AND result = 'Pass' AND consumed_at IS NULL AND expires_at > now() RETURNING id`. No row means expired, reused or mismatched (BR-024).
4. **Failure handling.** A Fail result lets the caregiver try again, up to three attempts. After the third failure, or when the vendor is unavailable, the caregiver may still clock in; the punch is accepted and IDENTITY_CHECK_FAILED is raised with the reason (failed match or vendor unavailable) for Coordinator review (FR-EVV-07). Vendor-unavailable exceptions can be bulk-resolved because they are systemic. Care is never blocked.
5. **Offline (SRS TBD-03 working assumption).** When the device is offline, the SDK capture package is stored in the encrypted outbox with the punch. At sync the API verifies it; the 90-second validity is measured between the identity capture and the punch capture on the device clock, cross-checked with the monotonic clock (ADR-006). A failed or missing match raises IDENTITY_CHECK_FAILED. The package is deleted from the device when the sync is acknowledged.
6. **Threshold.** The match threshold is a platform setting chosen with the vendor's published error rates; tenants can enable or disable the feature but cannot lower the threshold.
7. **Vendor terms.** BAA in place; capture packages processed transiently and not retained after the transaction; delayed verification accepted for offline packages up to 72 hours old; enrolled templates deleted within 30 days of caregiver deactivation (FR-WRK-06) through `deleteEnrollment`; annual evidence of presentation-attack testing.

## Consequences

**Positive**

- Proxy clock-ins become detectable and attributable without Tendwell holding images.
- The vendor can be replaced through a new adapter; domain logic, data model and API stay unchanged.
- The 90-second, single-use token prevents a passing check from being reused for a second visit or a colleague's punch.

**Negative**

- Each check costs a vendor fee, so the feature is enabled per tenant through a feature flag and its usage is reported per tenant.
- Offline captures are matched hours after the fact, so liveness assurance for them depends on the vendor's delayed-verification controls; a failed delayed match adds Coordinator workload in low-coverage areas.
- Switching vendors requires every caregiver to re-enroll, because templates are not portable.
- Some caregivers may be uncomfortable with selfie checks; the UX provides clear purpose text and the agency handles alternatives under its HR policy.

## Compliance and requirements links

| Type | IDs |
|---|---|
| Business rules | BR-024, BR-021 (server-authority principle) |
| Functional requirements | FR-EVV-04, FR-EVV-05, FR-EVV-07, FR-WRK-06 |
| Interfaces and open items | IF-06; TBD-03 (offline identity checks) |
| Non-functional requirements | NFR-PERF-02, NFR-PRIV-01, NFR-CMP-01, NFR-SEC-02, NFR-USE-01 |
| User stories | US-026 |
| Regulation (designed to support) | HIPAA Security Rule 45 CFR 164.312(d) person or entity authentication |

## Related documents

- [Sequence diagrams: clock-in with identity check](../../diagrams/sequence-diagrams.md)
- [Wireframe cg-02 clock-in](../../wireframes/README.md)
- [ADR-006 Offline-first caregiver app](ADR-006-offline-first-caregiver-app.md)
- [Data classification and retention](../../data/data-classification-and-retention.md)
- [EP-06 EVV user stories](../../../05-delivery/user-stories/EP-06-evv.md)
- [Compliance mapping](../../../02-requirements/compliance-mapping.md)
