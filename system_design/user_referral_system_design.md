# System Design: User Referral System (Uber-like)

---

## 1. Clarifying the Problem

Before jumping in, clarify scope with the interviewer:

- **Who can refer?** Existing riders? Drivers? Both?
- **What is the reward?** Ride credits, cash, discounts?
- **When is reward given?** When referee signs up, or after their first ride?
- **Is there a cap?** Max referrals per user, max reward per user?
- **Fraud concern?** How aggressively do we combat fake referrals?

**Assumed scope for this design:**
- Riders refer new riders
- Referrer earns credit when referee completes their **first ride**
- Referee gets a discount on that first ride
- A user can only use one referral code
- Scale: Uber-level (~100M users, millions of rides/day)

---

## 2. High-Level Requirements

### Functional
- Generate a unique referral code per user
- Share code via link/SMS/social
- Apply a referral code at signup
- Track whether the referee completed their first ride
- Credit the referrer's account after qualifying event
- Prevent abuse (self-referral, duplicate accounts, code reuse)

### Non-Functional
- **High availability**: Referral credit must not block the ride flow
- **Eventual consistency** is acceptable for crediting (a few seconds delay is fine)
- **Idempotency**: Crediting must happen exactly once per qualifying event
- **Low latency**: Code lookup at signup must be fast (< 50ms)
- **Scalability**: Handle millions of signups and ride completions per day

---

## 3. Core Entities & Data Model

### Design Choice: Separate Referral Tables from Users

Keeping referral data in its own tables avoids polluting the core `users` table and makes the referral system independently deployable and scalable.

```
users
-----
user_id         UUID (PK)
email           VARCHAR
phone           VARCHAR
referral_code   VARCHAR(8)  [indexed, unique]
referred_by     UUID        [FK → users.user_id, nullable]
created_at      TIMESTAMP

referral_events
---------------
event_id        UUID (PK)
referrer_id     UUID        [FK → users.user_id]
referee_id      UUID        [FK → users.user_id]
status          ENUM('pending', 'rewarded', 'fraud_flagged')
qualifying_ride_id  UUID   [nullable]
reward_amount   DECIMAL
created_at      TIMESTAMP
rewarded_at     TIMESTAMP
```

### Design Choice: Store `referral_code` on the user row

Fast O(1) lookup at signup validation without a join. Code is generated once at account creation.

---

## 4. Referral Code Generation

### Design Choice: Short alphanumeric codes (e.g., `JOHN7X2`)

- Short codes are shareable verbally and via SMS
- 8-character alphanumeric (Base36) → 36^8 ≈ 2.8 trillion combinations — no collision concern at Uber scale
- Generated at signup using a UUID prefix + Base36 encoding, checked for uniqueness before persisting

```
code = base36(sha256(user_id)[:6]).upper() + random_suffix(2)
```

If collision (extremely rare), retry generation. Store in Redis for O(1) lookup in addition to the DB index.

---

## 5. System Flow

### 5a. Sharing a Referral Link

```
User → GET /referral/my-code
     → Returns: { code: "JOHN7X2", link: "uber.com/signup?ref=JOHN7X2" }
```

The link is a deep link that pre-fills the referral code on the signup screen.

---

### 5b. Signup with Referral Code

```
New User → POST /auth/signup { ..., referral_code: "JOHN7X2" }

Signup Service:
  1. Validate referral_code → Redis lookup → O(1)
  2. Check: referrer != new user (no self-referral)
  3. Check: new user's phone/email/device not already in system (fraud check)
  4. Create user row with referred_by = referrer_id
  5. Create referral_event row with status = 'pending'
  6. Apply first-ride discount to new user's account
```

### Design Choice: Validate at signup, not at first ride

Catching invalid/fraudulent codes early avoids dangling state. The first-ride discount is pre-applied so it's seamless for the referee.

---

### 5c. Triggering the Reward (First Ride Completion)

```
Ride Completion → Ride Service publishes event to Kafka:
  { ride_id, rider_id, status: "completed", is_first_ride: true }

Referral Service (consumer):
  1. Check if rider has a referral_event in 'pending' state
  2. Verify qualifying_ride_id is not already set (idempotency check)
  3. Update referral_event: status='rewarded', qualifying_ride_id=ride_id
  4. Call Payments Service → credit referrer's wallet
  5. Emit referral_rewarded event (for notifications)
```

### Design Choice: Event-driven via Kafka (async)

- Ride completion is on the critical path for the user — crediting the referrer should **never** block or slow down ride completion
- Kafka provides durability: if the Referral Service is down, the event is replayed
- Decouples the Ride Service from Referral Service entirely

### Design Choice: Idempotency via `qualifying_ride_id`

Before crediting, check `qualifying_ride_id IS NULL`. If already set, skip. This ensures exactly-once reward even if the Kafka event is delivered more than once (at-least-once delivery).

---

## 6. Fraud Prevention

Referral fraud is a major concern at scale (fake accounts, SIM farms, device farms).

### Signals to check at signup:
| Signal | Method |
|---|---|
| Same device (fingerprint) | Device ID / fingerprint stored per user |
| Same IP address at signup | Rate-limit referrals per IP (e.g., max 3/day) |
| Same phone number | Phone verification required before reward |
| Same payment method | Check card BIN/last-4 at first ride |
| Velocity: referrer sends 100 codes in 1 hour | Rate-limit referral code generation |

### Design Choice: Phone Verification as a Gate for Reward

The referrer only gets credited after the referee **verifies their phone** AND completes a ride. This eliminates most fake-email account farms.

### Design Choice: Async Fraud Review for High-Risk Accounts

Flag suspicious `referral_events` (e.g., referrer with 50+ pending referrals) for async human/ML review before crediting. Don't block the system; just delay reward.

---

## 7. Caching Strategy

| Data | Cache | TTL |
|---|---|---|
| `referral_code → user_id` | Redis | Until account deleted |
| User's pending referral count | Redis counter | 24h rolling |
| Referral code validation result | Redis | Short (5 min) |

### Design Choice: Redis for Code Lookup

DB index lookup is fast, but at Uber scale (millions of signups/day), Redis gives sub-millisecond lookup and reduces DB load dramatically. Redis is the source of truth for validation; DB is the durable store.

---

## 8. API Design (Key Endpoints)

```
GET  /v1/referral/code              → Returns user's referral code + link
GET  /v1/referral/status            → Returns list of referee statuses
POST /v1/auth/signup                → body includes optional referral_code
POST /v1/referral/apply             → Apply code post-signup (edge case)
GET  /v1/referral/rewards           → Reward history for the referrer
```

---

## 9. Scalability & Reliability

### Design Choice: Referral Service is a Separate Microservice

- Independent deployment and scaling
- Ride Service, Auth Service, and Referral Service are loosely coupled via events
- Referral Service can go down without affecting rides

### Kafka Topic Design

```
Topic: ride.completed
  → Partitioned by rider_id (ensures ordering per rider)
  → Referral Service is a consumer group

Topic: referral.rewarded
  → Consumed by Notification Service, Analytics
```

### Database

- **PostgreSQL** for referral_events (ACID needed for exactly-once crediting)
- Shard by `referrer_id` if needed at extreme scale
- Read replicas for reporting/analytics queries

---

## 10. Monitoring & Observability

Key metrics to track:

| Metric | Alert Threshold |
|---|---|
| Referral-to-signup conversion rate | Drop > 20% |
| Reward processing lag (Kafka consumer lag) | > 60 seconds |
| Fraud flag rate | Spike > 5% of new referrals |
| Duplicate credit attempts (idempotency hits) | Any non-zero rate |
| Referral code lookup p99 latency | > 50ms |

---

## 11. Summary of Key Design Decisions

| Decision | Reasoning |
|---|---|
| Async reward via Kafka | Don't block ride completion; resilience to service downtime |
| Idempotency via `qualifying_ride_id` | Exactly-once crediting despite at-least-once delivery |
| Redis for code lookup | Sub-millisecond validation at signup scale |
| Separate `referral_events` table | Clean separation of concerns; auditable history |
| Phone verification gate | Eliminates majority of fake-account fraud |
| Rate limits per referrer | Prevents code farming and velocity abuse |
| Reward on first *completed* ride | Prevents credit-then-cancel abuse |
