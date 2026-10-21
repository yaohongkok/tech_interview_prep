# System Design Concepts — 1-Hour Review

Core concepts you'll reach for in any system design interview, with notes on how each one applies to Grab (ride-hailing, food delivery, payments, Southeast Asia scale).

**Suggested pacing (~60 min)**

| # | Section | Time |
|---|---------|------|
| 0 | Interview framework | 3 min |
| 1 | Capacity planning | 7 min |
| 2 | Databases | 10 min |
| 3 | Caching | 6 min |
| 4 | Async processing & messaging | 8 min |
| 5 | CAP & consistency | 5 min |
| 6 | Distributed systems | 8 min |
| 7 | Scalability | 5 min |
| 8 | Reliability | 5 min |
| 9 | Deployment strategies | 3 min |
| — | Grab cheat sheet | — |

---

## 0. Interview Framework (how the concepts get used)

1. **Clarify requirements.** Functional (what it does) and non-functional (latency, availability, consistency, scale). Say which ones matter most.
2. **Estimate** QPS (queries/request per second), storage, and bandwidth (Section 1).
3. **API + data model.** Main endpoints, entities, access patterns.
4. **High-level design.** Client → LB/API gateway → services → DB/cache/queue.
5. **Deep dive** on the bottleneck: hot partitions, consistency, failure modes.
6. **Trade-offs and wrap-up.** What you'd change at 10x, what you'd monitor.

> Interviewers grade **trade-off reasoning**, not just the final diagram. For every choice, say *"I pick X over Y because the requirement is Z; the cost is W."*

---

## 1. Capacity Planning

### Numbers to memorize

| Item | Value |
|------|-------|
| Seconds/day | ~86,400 ≈ **10⁵** |
| 1M req/day | ≈ **12 QPS** |
| 100M req/day | ≈ **1,200 QPS** |
| Peak factor | **2–5x** average (Grab: meal times, rain, rush hour) |
| L1 cache / RAM read | ~1 ns / ~100 ns |
| SSD random read | ~100 µs |
| Same-DC round trip | ~0.5 ms |
| Cross-region round trip | ~50–150 ms |
| Single Redis node | ~100k ops/s |
| Single Postgres/MySQL node | ~5–10k simple writes/s, more for reads |
| Single Kafka partition | ~10 MB/s; a cluster handles millions of msgs/s |
| Typical app server | ~1k–10k RPS (depends heavily on work per request) |

### AWS numbers to memorize

Approximate defaults; many are soft quotas you can raise. Check Service Quotas before relying on one.

| Service | Key numbers | Why it matters in a design |
|---------|-------------|----------------------------|
| **Same-region cross-AZ** | ~1–2 ms RTT; $0.01/GB each way | Multi-AZ is cheap on latency, but chatty cross-AZ traffic costs money |
| **S3** | **5,500 reads/s, 3,500 writes/s per prefix**; ~100 MB/s per connection, 10+ GB/s with parallel requests; object ≤ 5 TB | Spread hot keys across prefixes; first byte ~10s–100 ms, so not a low-latency store (S3 Express One Zone for single-digit ms) |
| **DynamoDB** | Per partition: **3,000 reads/s (~12 MB/s), 1,000 writes/s (~1 MB/s)**; per table ~40k each (raisable); item ≤ 400 KB | Single-digit ms; hot partition keys throttle; 1 RCU = 4 KB strong read, 1 WCU = 1 KB write; big blobs go in S3 with a pointer |
| **ElastiCache (Redis/Valkey)** | **~100k+ ops/s per node**; ~1–3 GB/s per node (NIC-bound); ≤ 500 shards | Sub-ms; cache hot reads, sessions, leaderboards, geo (`GEOADD`) |
| **RDS / Aurora** | One writer: **~10k–100k writes/s** (instance-dependent); storage I/O ~100s MB/s to few GB/s; ≤ 15 read replicas | Replica lag < 100 ms on Aurora; shard or switch stores when writes outgrow one primary |
| **SQS** | Standard: **~unlimited**; FIFO: *300 msg/s (3,000 batched)*, higher in high-throughput mode; msg ≤ 1 MiB | Standard is at-least-once, so make consumers idempotent; FIFO only when order per group matters; retention ≤ 14 days |
| **SNS** | **~30k publishes/s** (us-east-1, lower elsewhere); msg ≤ 256 KB | SNS → multiple SQS queues is the standard fan-out pattern |
| **Kinesis Data Streams** | Per shard: **1,000 records/s or 1 MB/s in; 2 MB/s out** | Shard count = max(ingest MB/s ÷ 1, records/s ÷ 1,000); ordered per shard, like a Kafka partition |
| **MSK (Kafka)** | **~10 MB/s per partition**; ~100–500 MB/s per broker | Pick over Kinesis for Kafka ecosystem, long retention, very high throughput |
| **Lambda** | **1,000 concurrent/region** (~10k RPS cap); max 15 min; payload ≤ 6 MB | Concurrency ≈ RPS × duration (s): 1,000 RPS × 0.2 s = 200 concurrent. Cold start ~100 ms–1 s+; avoid for long jobs or steady very high load |
| **API Gateway** | **10,000 RPS/region** (burst 5,000); timeout 29 s | Throttles before your backend does; long jobs should be async (return 202 + poll or webhook) |
| **ALB / NLB** | ALB: **~100k+ RPS**, ~GB/s, auto-scales; NLB: **millions RPS**, 10s of GB/s, sub-ms | ALB for HTTP routing (adds a few ms); NLB for TCP/UDP, extreme scale, or static IPs |
| **CloudFront** | **250k RPS**, **150 Gbps (~19 GB/s) per distribution**; 600+ edges | Cache static assets and cacheable API responses near users |
| **EBS** | gp3: **3,000 IOPS / 125 MB/s** baseline, up to 80k IOPS / 2 GB/s; io2: up to 256k IOPS / 4 GB/s | Disk IOPS often caps self-managed DBs before CPU does |
| **Step Functions** | Standard: **~hundreds starts/s**, ≤ 1 yr; Express: **~6k starts/s**, ≤ 5 min | Standard (exactly-once) for long sagas; Express (at-least-once) for high-rate short workflows |
| **EC2 instance network** | 10–25 Gbps (~1–3 GB/s) mid-size; 100+ Gbps (~12+ GB/s) large | Sanity check for bandwidth-heavy services (video, data pipelines) |

### Formulas

```
QPS (avg)      = DAU × actions_per_user_per_day / 86,400
QPS (peak)     = QPS_avg × peak_factor
Storage/yr     = writes_per_day × record_size × 365 × replication_factor
Bandwidth      = QPS × payload_size
Servers needed = peak_QPS / per_server_QPS  (+30–50% headroom, N+1 for AZ loss)
Cache size     = hot_fraction (~20%) × daily_data   (80/20 rule)
```

### Worked example: driver location updates (Grab-flavoured)

- 5M active drivers at peak, each pinging every 4 s → **1.25M writes/s**.
- Payload ~100 B → ~125 MB/s ingest.
- **Takeaway:** too much for a relational DB. Use in-memory, geo-indexed storage (Redis or a custom service) for the *latest* location, and stream to Kafka → cold storage for history. Estimation drives the architecture; that's the point of doing it.

### Tips
- Round hard (powers of 10). Interviewers want order of magnitude, not precision.
- Always separate **read QPS vs write QPS**. The read:write ratio decides caching and replication strategy.
- State the **latency budget** (e.g. p99 < 200 ms) and spend it per hop.

---

## 2. Databases

### SQL vs NoSQL

| | Relational (MySQL, Postgres, Aurora, TiDB) | NoSQL |
|---|---|---|
| Model | Tables, joins, schema | KV (Redis, DynamoDB), wide-column (Cassandra, ScyllaDB), document (MongoDB), graph |
| Transactions | ACID, multi-row | Usually single-key/partition; some offer limited txns |
| Scaling | Vertical + read replicas; sharding is manual/hard (except NewSQL) | Horizontal by design (partition key) |
| Pick when | Money, orders, relationships, complex queries, strong consistency | Massive scale, simple access patterns by key, flexible schema, high write throughput |

**Rule of thumb:** start with SQL unless scale or access pattern clearly rules it out. Money ledgers → SQL. Location pings, event logs, chat → NoSQL / time-series.

### ACID vs BASE
- **ACID:** Atomicity, Consistency, Isolation, Durability.
- **Isolation levels** (weak → strong): Read Uncommitted → Read Committed → Repeatable Read → Serializable. Know the anomalies: dirty read, non-repeatable read, phantom read, lost update.
- **BASE:** Basically Available, Soft state, Eventually consistent.

### Indexing
- **B-tree** (default in RDBMS): good for range + equality queries; makes writes slower.
- **LSM tree** (Cassandra, RocksDB, ScyllaDB): fast writes (append + compaction), slower reads (needs bloom filters).
- **Composite index:** column order matters (leftmost prefix rule).
- **Geospatial:** geohash, quadtree, S2/H3 hexagons. Used for "find nearby drivers" (core Grab concept).
- **Inverted index:** full-text search (Elasticsearch), e.g. restaurant/menu search.

### Replication
| Type | How | Trade-off |
|---|---|---|
| Leader–follower | Writes go to leader, async to replicas | Simple; replication lag → stale reads; failover may lose writes |
| Synchronous / semi-sync | Leader waits for ≥1 replica ack | Durable, adds write latency |
| Multi-leader | Writes in multiple regions | Conflict resolution needed (LWW, CRDTs) |
| Leaderless (Dynamo-style) | Quorum: **W + R > N** → read sees latest write | Tunable consistency; repair needed (read repair, anti-entropy) |

**Read-your-writes problem:** user updates profile, then reads a stale replica. Fix: read from the leader for X seconds after a write, or use session/version tokens.

### Partitioning / Sharding
- **Range-based:** good for range scans; risk of hot ranges (e.g. time-based keys).
- **Hash-based:** even spread; range queries become scatter-gather.
- **Consistent hashing** (with virtual nodes): adding or removing a node moves only ~1/N of keys.
- **Geo/tenant-based:** shard by city/country. Natural for Grab (Jakarta ≠ Singapore traffic), but watch for uneven city sizes.
- **Choosing a shard key:** high cardinality, even distribution, matches the dominant query. Avoid hot keys (celebrity user, mega-merchant). Mitigate with key salting or splitting a hot shard.
- **Costs of sharding:** cross-shard joins/transactions, rebalancing, global secondary indexes.

### Other storage types
- **Object storage (S3):** images, receipts, ML models, logs. Cheap and durable; serve through a CDN.
- **Time-series (Prometheus, InfluxDB, TimescaleDB):** metrics, telemetry.
- **OLAP / data warehouse (Redshift, BigQuery, Presto/Trino on a data lake):** analytics. Keep it separate from OLTP and feed it via CDC/Kafka.
- **NewSQL (TiDB, CockroachDB, Spanner):** SQL + horizontal scale + distributed transactions. Grab has written publicly about adopting TiDB.

### Grab angle
- Orders/bookings: high write volume with a clear key (`order_id`). Grab's engineering blog describes splitting **OLTP (DynamoDB-style KV, keyed by order ID)** from **OLAP/analytics queries (MySQL/RDS fed asynchronously via Kafka)**. CQRS is a good pattern to mention here.
- Payments/wallet (GrabPay): relational, ACID, double-entry ledger, append-only, idempotent.

---

## 3. Caching

### Where to cache
Client/app → CDN (static assets, images, menus) → API gateway → app in-process cache → distributed cache (Redis/Memcached) → DB buffer pool.

### Patterns
| Pattern | Flow | Notes |
|---|---|---|
| **Cache-aside (lazy)** | App reads cache; on miss reads DB and fills cache | Most common; first read is slow; stale until TTL/invalidation |
| **Read-through** | Cache loads from DB itself | Simpler app code |
| **Write-through** | Write cache + DB synchronously | Consistent; slower writes |
| **Write-behind (write-back)** | Write cache; flush to DB async | Fast writes; risk of data loss |
| **Write-around** | Write DB only; cache fills on read | Avoids caching rarely-read data |

### Eviction
- Strategy to remove entries when it needs more room
- Without it, memory max out.
- LRU (default choice), LFU (stable hot sets), FIFO, TTL-based. Always set a TTL as a safety net.

### Invalidation (the hard part)
- Why hard?
  - 2 writes can't be atomic due to separate system.
  - Race condition: (1) Req A misses cache & reads DB for v1, (2) Req B updates DB with v2 & delete cache, (3) Req A writes v1 to cache.
    - Perhaps use read-write lock
  - Knowing what to invalidate. One DB row can feed lots of caches.
  - Cache replicas compound this problem.
- On write: **update the DB, then delete the cache key**. Don't update the cache directly, because it races with concurrent reads.
- Event-driven invalidation via Change Data Capture (CDC).  E.g. Debezium (read DB data changes) → Kafka → invalidate.
- Versioned keys (`menu:v42`) avoid invalidation entirely. `v42` is the version of the DB row (that was updated).

### Failure modes and fixes
| Problem | What happens | Fix |
|---|---|---|
| **Cache stampede / thundering herd** | Hot key expires and 10k requests hit the DB | Request coalescing (singleflight), lock/lease, early probabilistic refresh |
| **Cache penetration** | Queries for non-existent keys always miss | Cache negative results (short TTL), bloom filter |
| **Cache avalanche** | Many keys expire at once / cache cluster down | Jittered TTLs, multi-level cache, circuit breaker to DB |
| **Hot key** | One key overloads one shard | Replicate the key across shards, local in-process cache |

### Grab angle
- Restaurant menus, merchant info, pricing config → heavily cached (read-heavy, tolerant of seconds of staleness).
- Driver live locations → Redis as the *primary* store for ephemeral data (geo commands / geohash buckets), not just a cache.
- Never serve wallet balances from a stale cache for debits. Make the consistency requirement explicit.

---

## 4. Async Processing & Messaging

### Why go async
Decouple services, absorb spikes (load leveling), retry failures, fan out one event to many consumers, and keep user-facing latency low ("accept → 202 → process later").

### Queue vs Log/Stream
| | Message queue (SQS, RabbitMQ) | Log/stream (Kafka, Kinesis, Pulsar) |
|---|---|---|
| Consumption | Message deleted after ack | Retained; consumers track offsets; replayable |
| Fan-out | Needs pub/sub topology (SNS→SQS) | Native: many consumer groups |
| Ordering | Best effort (FIFO queues are limited) | Ordered **per partition** |
| Use | Task/job queues, work distribution | Event streaming, CDC, analytics, event sourcing |

**Kafka essentials:** topic → partitions (unit of parallelism and ordering) → consumer group (one consumer per partition). Partition key = `order_id` gives per-order ordering. Max consumers in a group = number of partitions. Watch **consumer lag**.

### Delivery semantics
- **At-most-once:** may lose messages (fire-and-forget metrics).
- **At-least-once:** default. May duplicate, so **consumers must be idempotent**.
- **Exactly-once:** really "effectively once" = at-least-once + idempotency/dedup (or Kafka transactions within Kafka).

### Idempotency (very important for Grab payments/bookings)
- Client sends an `Idempotency-Key`; the server stores `key → result`; a retry returns the stored result.
- Use DB unique constraints / conditional writes (`INSERT ... ON CONFLICT DO NOTHING`, DynamoDB condition expressions).
- Make operations naturally idempotent: "set status = PAID" rather than "increment balance".

### Key patterns
- **Transactional outbox:** write the business row and an `outbox` row in the same DB txn; a relay/CDC publishes to Kafka. Solves the dual-write problem (DB commit OK, publish failed).
- **Saga:** a distributed transaction as a sequence of local txns with **compensating actions**. *Choreography* (services react to events) vs *orchestration* (central coordinator, e.g. Temporal/Cadence/Step Functions). Example: food order → reserve payment → confirm merchant → assign driver; if no driver, refund.
- **Retries with exponential backoff + jitter**, then a **dead-letter queue (DLQ)** for poison messages.
- **Backpressure:** bounded queues, rate limiting producers, autoscaling consumers on lag.
- **Command Query Responsibility Segragation (CQRS):** separate write model from read models.
- **Event sourcing:** Rebuild state from the event log
- **Delayed / scheduled jobs:** timeouts (e.g. "cancel booking if no driver in 60 s"). Use a delay queue, timer wheel, or workflow engine.

### Real-time push to clients
Polling < long polling < **SSE** (server → client) < **WebSockets** (bidirectional). Mobile apps: persistent connection when in foreground + **push notifications (FCM/APNs)** when backgrounded. Grab context: live driver tracking on the map, order status updates.

---

## 5. CAP & Consistency

### CAP
During a **network Partition**, a distributed system must choose between **Consistency** (every read sees the latest write or errors) and **Availability** (every request gets a non-error response).
- Partitions *will* happen, so the real choice is **CP vs AP during a partition**.
- **CP:** ZooKeeper/etcd, HBase, Spanner, banks' ledgers. Reject requests rather than diverge.
- **AP:** Cassandra, DynamoDB (default eventual reads), DNS, shopping carts. Accept writes and reconcile later.

### PACELC (more useful in interviews)
If **P**artition → **A** or **C**; **E**lse (normal operation) → **L**atency or **C**onsistency.
Example: DynamoDB/Cassandra = PA/EL. Spanner = PC/EC.

### Consistency models (strong → weak)
Linearizable → Sequential → Causal → Read-your-writes / Monotonic reads → Eventual.

- Linearizable: Write to one node, guarantees reading the same values from other nodes. No stale data.
- Sequential: All clients see operations in same order. May still see stale data.
- Casual: Casual operation are seen in same order. Concurrent, unrelated operations show up in different order.
- Read-your-writes: Your writes will always be readable by yourself but not necessarily others.


### How to answer "which do you choose?"
Choose **per feature**, not per system:
| Grab feature | Choice | Why |
|---|---|---|
| Wallet debit / payment | **CP / strong** | Can't double-spend; fail rather than be wrong |
| Booking assignment (one driver ↔ one ride) | **Strong on the assignment** (conditional write / lock) | Prevents double allocation |
| Driver location on map | **AP / eventual** | A 2-s-old location is fine; availability matters more |
| Restaurant ratings, menus | **AP / eventual** | Staleness is harmless |
| Surge price shown vs charged | Lock the quoted price with a TTL'd token | User sees and pays the same price |

---

## 6. Distributed Systems Fundamentals

### Fallacies to remember
The network is not reliable, latency is not zero, bandwidth is not infinite, topology changes, clocks are not synchronized.

### Time & ordering
- Wall clocks drift. Don't use timestamps to order events across machines for correctness.
- **Lamport clocks** (total order, not causality detection), **vector clocks** (detect concurrent writes), **hybrid logical clocks** (CockroachDB), **TrueTime** (Spanner).
- **Last-write-wins** is simple but silently drops concurrent updates.

### Consensus & coordination
- **Raft / Paxos:** a majority (quorum) agrees on a log. Tolerates **f failures with 2f+1 nodes** (3 nodes → 1 failure, 5 → 2).
- Used for: leader election, config, service discovery, distributed locks (etcd, ZooKeeper, Consul).
- Don't implement consensus yourself in an interview; *use* etcd/ZooKeeper.

### Distributed locks
- Redis `SET key val NX PX ttl` is fine for efficiency (avoiding duplicate work). For **correctness**, use **fencing tokens** (monotonic numbers checked by the storage layer), because a lock holder can pause (GC) past its TTL.
- Often better: avoid locks with **optimistic concurrency** (`UPDATE ... WHERE version = ?`) or conditional writes.

### Distributed transactions
- **2PC:** coordinator prepare → commit. Atomic, but blocking if the coordinator dies, and slow. Rare across microservices.
- **Sagas** (Section 4) are the microservices default; accept eventual consistency + compensation.

### Unique IDs
UUIDv4 (random, bad for B-tree locality), **UUIDv7 / ULID** (time-ordered), **Snowflake** (timestamp + machine ID + sequence; 64-bit, sortable), DB ticket server/ranges.

### Microservices plumbing
- **Service discovery** (Consul, k8s DNS), **API gateway** (auth, rate limit, routing), **service mesh** (Envoy/Istio: mTLS, retries, observability).
- **Sync** (REST/gRPC: simple, but creates temporal coupling) vs **async** (events: decoupled, harder to debug). Grab's backend is largely Go microservices talking over gRPC/HTTP with Kafka for events.
- Load balancing: L4 vs L7; algorithms: round robin, least connections, consistent hashing (sticky), power-of-two-choices.

### Geo / location concepts (Grab-specific must-know)
- **Geohash:** encode lat/lng into a string prefix; nearby points share prefixes. Query the cell + 8 neighbors. Edge problem at cell boundaries.
- **Quadtree:** adaptive subdivision; dense cities get smaller cells.
- **S2 / H3 (hexagons):** uniform neighbor distances; good for surge-pricing zones and supply-demand heatmaps.
- **Matching/dispatch:** find candidate drivers in nearby cells → rank by ETA (not straight-line distance) → offer → accept with timeout → fall back to the next candidate. Batch matching (assign over a small time window) beats greedy matching for global efficiency.

---

## 7. Scalability

### Vertical vs horizontal
- **Vertical (scale up):** bigger machine. Simple, has a ceiling, single point of failure.
- **Horizontal (scale out):** more machines. Requires **stateless services** (state goes in DB/cache/session store).

### Toolkit
| Layer | Technique |
|---|---|
| Edge | CDN, DNS geo-routing, edge caching |
| Traffic | Load balancers, API gateway, **rate limiting** (token bucket, sliding window; per user/IP/merchant) |
| Compute | Stateless services + **autoscaling** (CPU, QPS, queue lag; pre-scale for known peaks like lunch/dinner) |
| Data reads | Caching, read replicas, denormalization, materialized views |
| Data writes | Sharding, batching, async writes via queues, LSM-based stores |
| Work | Async queues, worker pools, batch vs stream processing |
| Geography | Multi-region / cell-based architecture: route each city/country to its own "cell" |

### Bottlenecks to call out
- **Hot partitions / hot keys** (one huge merchant, a stadium event, a popular promo).
- **Fan-out** (one write → millions of reads): fan-out-on-write vs fan-out-on-read, hybrid for celebrities.
- **Chatty services** (N+1 RPCs). Batch, cache, or aggregate.
- **Connection limits** to the DB. Use connection pooling (PgBouncer, RDS Proxy).

### Grab angle
- Traffic is **spiky and predictable** (meal times, morning/evening commute, payday promos) plus **unpredictable** (sudden rain → demand surge, supply drop). Mention pre-scaling and **load shedding** of non-critical features.
- **Multi-country:** data residency, per-country config, regional deployments. Cell/city-based partitioning limits blast radius.
- **Clients on poor networks / low-end devices:** small payloads, compression, retry-safe (idempotent) APIs, offline tolerance.

---

## 8. Reliability

### Vocabulary
- **Availability:** 99.9% ≈ 8.8 h/yr down; 99.99% ≈ 52 min/yr; 99.999% ≈ 5 min/yr.
- Serial dependencies **multiply**: three services at 99.9% each → ~99.7% overall. Parallel redundancy improves it: 1 − (1 − a)².
- **SLI** (what's measured, e.g. p99 latency) → **SLO** (internal target) → **SLA** (contract with penalties). **Error budget** = 1 − SLO, which decides when to freeze releases.
- **RPO** (how much data you can lose) vs **RTO** (how fast you must recover).

### Resilience patterns
| Pattern | Purpose |
|---|---|
| **Timeouts** | Every remote call has one; never wait forever |
| **Retries + exponential backoff + jitter** | Survive transient faults without a retry storm. Retry only idempotent ops; cap with a retry budget |
| **Circuit breaker** | Stop calling a failing dependency (closed → open → half-open). Grab has written about using circuit breakers widely |
| **Bulkhead** | Isolate resource pools so one bad dependency can't exhaust all threads/connections |
| **Fallback / graceful degradation** | Serve cached/default data (e.g. hide ETA instead of failing the booking) |
| **Load shedding / admission control** | Drop low-priority traffic under overload to protect core flows (booking, payment) |
| **Rate limiting** | Protect services from abusive or buggy clients |
| **Health checks** | Liveness vs readiness probes; remove unhealthy instances from the LB |
| **Redundancy** | N+1 instances, multi-AZ by default, multi-region for critical paths |

### Disaster recovery strategies (cheap → expensive)
Backup & restore → pilot light → warm standby → **active-active multi-region**.

### Observability
- **Metrics** (RED: Rate, Errors, Duration; USE: Utilization, Saturation, Errors), **logs** (structured, correlation IDs), **traces** (OpenTelemetry/Jaeger for cross-service latency).
- Alert on **symptoms / SLO burn rate**, not every cause.
- **Chaos engineering:** inject failures in production-like environments to verify the fallbacks actually work.

### Data reliability
Backups + tested restores, point-in-time recovery, replication across AZs, **reconciliation jobs** (e.g. payments vs bank/partner statements daily), audit logs.

---

## 9. Deployment Strategies

| Strategy | How | Pros | Cons |
|---|---|---|---|
| **Recreate** | Stop old, start new | Simple | Downtime |
| **Rolling** | Replace instances in batches | No extra infra; k8s default | Mixed versions live at once; slow rollback |
| **Blue-green** | Two full envs; switch traffic at once | Instant rollback | 2x infra; DB migrations still shared |
| **Canary** | Ship to 1% → 5% → 25% → 100%, gated on metrics | Small blast radius, real-traffic validation | Needs good metrics + automation |
| **Feature flags** | Deploy code dark, enable per user/city/percent | Decouples deploy from release; kill switch | Flag debt; config complexity |
| **Shadow / dark launch** | Mirror real traffic to the new version, discard responses | Zero user impact testing | Side effects must be suppressed (no double charges) |
| **A/B testing** | Split users to measure business metrics | Product experimentation | Not a safety mechanism by itself |

### Practices to mention
- **Backward-compatible changes:** API versioning; never break old mobile clients (users don't update apps promptly).
- **DB migrations: expand → migrate → contract.** Add the new column/table → dual-write/backfill → switch reads → remove the old column. Never ship a breaking schema change together with code.
- **Automated rollback** on SLO/error-rate regression during canary.
- **Progressive rollout by region/city.** For Grab: start in a smaller market before Jakarta/Manila.
- **Immutable infrastructure, IaC (Terraform), CI/CD, GitOps (ArgoCD).**

---

## Grab Cheat Sheet

**Business domains:** Mobility (rides), Deliveries (GrabFood, GrabMart, GrabExpress), Financial services (GrabPay wallet, PayLater, lending), plus the merchant and driver platforms. Operates across ~8 Southeast Asian countries, 400+ cities.

**Recurring design themes:**
1. **Geospatial at scale:** live driver locations, nearby search, ETA, geofences, surge zones (geohash/H3, in-memory geo indexes).
2. **Dispatch/matching:** low latency, exactly one driver per job, timeouts, re-dispatch, batching.
3. **Supply–demand pricing (surge):** stream processing over location + demand events per zone; price quotes locked with a token.
4. **Payments & wallet:** idempotency keys, double-entry ledger, sagas with compensation, outbox, reconciliation, strong consistency, audit.
5. **Order lifecycle as a state machine:** `CREATED → PAID → MERCHANT_ACCEPTED → DRIVER_ASSIGNED → PICKED_UP → DELIVERED`, with valid transitions enforced (conditional writes) and events emitted on each change.
6. **Event-driven backbone:** Kafka for orders, locations, and analytics; CDC into the data lake; real-time ML features (fraud, ETA, recommendations).
7. **Peaks & resilience:** meal times, weather, promos → autoscaling, pre-scaling, load shedding, circuit breakers, graceful degradation.
8. **Emerging-market constraints:** flaky mobile networks, low-end Android devices, multiple currencies and languages, cash payments, per-country regulation and data residency.
9. **Fraud & safety:** GPS spoofing, promo abuse, fake accounts. Rule engines + ML scoring, inline (sync, low latency) vs offline (async).

**Phrases that score well:**
- "This path is user-facing, so I'll keep it synchronous and push everything else async through Kafka."
- "Consumers are at-least-once, so the handler is idempotent keyed on `order_id` + `event_version`."
- "I'll shard by city/geo cell so a spike in Jakarta doesn't affect Singapore. It also limits blast radius."
- "For the wallet I choose consistency over availability: a failed payment is recoverable, a double debit isn't."
- "Driver location is ephemeral and high-write, so it goes to an in-memory geo index with TTL, and history is streamed to cold storage."

---

## Final 5-Minute Self-Check
- [ ] Can I estimate QPS/storage for 10M DAU in under 2 minutes?
- [ ] Can I justify SQL vs NoSQL and pick a shard key with a hot-key mitigation?
- [ ] Can I explain cache-aside + invalidation + stampede protection?
- [ ] Can I explain at-least-once + idempotency + outbox + saga?
- [ ] Can I pick CP vs AP per feature, using PACELC?
- [ ] Can I explain quorum (W+R>N), consensus (2f+1), and fencing tokens?
- [ ] Can I list 5 resilience patterns and explain the SLO/error budget?
- [ ] Can I compare canary vs blue-green and explain expand-contract migrations?
- [ ] Can I explain geohash/H3 nearby search and dispatch matching?
