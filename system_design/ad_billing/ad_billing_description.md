# Ad Click & Impression Tracking with Billing — System Design

> **Problem:** Track ad impressions and clicks at very high write volume, aggregate them for advertiser dashboards, deduplicate them, and bill advertisers accurately.
>
> **The core tension:** the write path has to be *fast and always available*, and the billing path has to be *exact and auditable*. Most of the design is about keeping these two apart.
>
> References like **(OVERVIEW §4)** point to [OVERVIEW.md](../OVERVIEW.md).

**Reading time: ~18 min**

---

## 1. Requirements (OVERVIEW §0)

### Functional
1. **Record events:** impressions (ad rendered/viewed) and clicks (user tapped the ad → redirect to the advertiser).
2. **Real-time reporting:** advertisers see impressions, clicks, CTR, and spend per campaign/ad, fresh to about **1 minute**.
3. **Billing:** charge advertisers per **CPM** (cost per 1,000 impressions) or **CPC** (cost per click). Produce daily statements and monthly invoices.
4. **Budget enforcement:** stop serving a campaign when its daily or total budget runs out.
5. **Invalid traffic filtering:** don't bill for bots, duplicates, or forged events.

### Non-functional (ranked)
| Priority | Requirement | Why |
|---|---|---|
| 1 | **Billing accuracy:** no double-charging, no lost billable events, full audit trail | It's money. Overcharging loses advertiser trust; undercharging loses revenue |
| 2 | **Ingest durability:** once acked, an event is never lost | A lost click is lost revenue and can't be recovered later |
| 3 | **Ingest availability + low latency:** p99 < 50 ms, 99.99% | It sits on the user's page-load / click-redirect path. A slow redirect hurts the advertiser |
| 4 | **Dashboard freshness:** ~1 min, eventually consistent | Advertisers tolerate approximate numbers in real time, as long as the invoice is exact |
| 5 | **Replayability:** recompute any day from raw events | Needed for bug fixes, fraud refunds, and disputes |

**Out of scope:** ad selection/auction (we assume an ad server already picked the ad and price), payment collection (hand off to a payments system).

> **Key framing to say out loud:** *"Two consistency levels. Dashboards and budget pacing are AP and approximate. The invoice is strongly consistent and exact. I'll build a fast streaming path for the first and an authoritative batch path for the second, then reconcile them."* (OVERVIEW §5: choose consistency per feature.)

---

## 2. Capacity Estimates (OVERVIEW §1)

Assumptions: a mid-to-large ad network.

| Metric | Estimate | Math |
|---|---|---|
| Impressions/day | **10B** | — |
| Clicks/day | **100M** | ~1% CTR |
| Impression QPS (avg / peak) | **~115k/s / ~500k/s** | 10B ÷ 86,400; peak ×4–5 |
| Click QPS (avg / peak) | **~1.2k/s / ~6k/s** | 100M ÷ 86,400 |
| Raw event size | ~500 B | IDs, timestamps, user agent, IP, geo, price |
| Ingest bandwidth (peak) | **~250 MB/s** | 500k × 500 B |
| Raw storage/day | **~5 TB** raw → ~1 TB compressed Parquet | ~365 TB/yr compressed |
| Kafka partitions | **≥ 50, use ~256** | 250 MB/s ÷ ~10 MB/s per partition, plus headroom for consumer parallelism |
| Collector servers | **~100** | 500k ÷ ~10k RPS each, +50% headroom, N+1 per AZ |

**What the numbers tell us:**
- **~500k writes/s is far beyond one SQL primary** (~10k writes/s). Raw events go to a **log (Kafka)**, then to object storage, never row by row into a relational DB.
- **Clicks are 100× fewer than impressions but carry most of the money** (CPC is usually dollars per click; CPM is fractions of a cent per impression). We can spend more per click on exact dedup and fraud checks.
- **Aggregated data is small.** 10M active ads × 1,440 minutes/day ≈ 14B rows/day at minute grain, but most ads are idle in any given minute. Roll up to hourly/daily for history.
- **The billing ledger is tiny.** About 1M campaigns × 1 daily entry = 1M rows/day. This fits easily in **Postgres/Aurora** with full ACID (OVERVIEW §2: *money ledgers → SQL*).

---

## 3. API & Data Model

### 3.1 The signed ad token (the most important design choice)

When the ad server serves an ad, it creates an **`impression_id`** (Snowflake/ULID, OVERVIEW §6) and embeds a **signed token** in the ad markup:

```
token = base64( impression_id | ad_id | campaign_id | advertiser_id |
                pricing_model | price_micros | served_at | placement_id )
        + HMAC-SHA256(secret_key_v3, payload)
```

Note: Token consists of all the fields mentioned above.

Why it matters:
- **Dedup key decided at the source.** Every retry of the same impression carries the same `impression_id`, so dedup becomes a simple key lookup.
- **Price locked at serve time.** The bill uses the auction price that was actually agreed, not whatever the price is when the event arrives. This is the same idea as locking a surge price quote with a token (OVERVIEW §5).
- **Forgery protection.** Collectors reject any event without a valid HMAC, so attackers can't invent impressions for a competitor's campaign.
- **Click ↔ impression link.** `click_id = hash(impression_id)` (one billable click per impression), and every click must join to a real impression.
- This design reduces the amount of data that needs to be stored.

### 3.2 Endpoints

```
GET  /v1/imp?t=<token>          → 204 No Content   (or 1×1 pixel / navigator.sendBeacon)
GET  /v1/click?t=<token>&dest=  → 302 Redirect to advertiser landing page
GET  /v1/reports?campaign_id=&from=&to=&granularity=minute|hour|day   (dashboard)
GET  /v1/billing/statements?advertiser_id=&month=                     (invoice)
```

- The click endpoint **redirects first and logs asynchronously**. It writes to Kafka, then returns 302. It never waits on aggregation (OVERVIEW §4, *accept → process later*).
- Viewability (for example, 50% of the ad in view for 1 s) is measured client-side and sent as an `imp` with `viewable=true`. CPM is often billed only on viewable impressions.

### 3.3 Data stores

| Data | Store | Why (OVERVIEW §2) |
|---|---|---|
| Raw event stream | **Kafka** (`raw-impressions`, `raw-clicks`), 7-day retention | High write throughput, replayable, multiple consumer groups |
| Raw event archive | **S3 data lake** (Parquet, partitioned by `dt/hour`) | Cheap, durable source of truth for batch billing and audits |
| Real-time aggregates | **OLAP store**: Apache Pinot / Druid / ClickHouse | Fast slice-and-dice over time + dimensions; built for upserts from streams |
| Budget spend counters | **Redis** (`spend:{campaign_id}:{date}`) | Sub-ms reads on the ad-serving hot path; ~100k ops/s per node |
| Billing ledger + invoices | **Postgres/Aurora** (double-entry, append-only) | ACID, unique constraints, auditors understand it |
| Dedup state | **Flink keyed state** (RocksDB) | Local to the stream processor, checkpointed, no network hop per event |

**Why open-source engines are still the default here.** Most of the AWS options above are *managed versions of the same open-source engines* (MSK = Kafka, Managed Flink = Flink, ElastiCache = Redis/Valkey, Aurora = Postgres), so they're the easy win: same APIs, less ops. The places where the open-source choice beats an AWS-native service:
- **Kafka over Kinesis.** Kafka is cheaper at ~250 MB/s, keeps events longer for replay, and makes it easy to add consumer groups (Flink, S3 sink, fraud ML). Kinesis is per-shard throughput-capped and its fan-out costs extra.
- **Pinot/Druid/ClickHouse over Redshift.** They're built for sub-second, high-concurrency queries on data that's seconds old, which is what advertiser dashboards need. Redshift is better for batch/BI over hours-old data, so use it for finance reporting rather than the live dashboard.
- **Flink state over DynamoDB for dedup.** A DynamoDB conditional write per event would mean ~500k network calls/s at peak and a large bill. Flink keeps dedup state local and checkpointed.
- **Portability.** Interviewers often want a cloud-agnostic design. Naming the engine (Kafka, Flink) and then saying "on AWS I'd run it as MSK / Managed Flink" covers both.

---

## 4. High-Level Architecture (OVERVIEW §0 step 4)

See [ad_billing_arch.puml](ad_billing_arch.puml) for the architecture diagram.

**Design choice: Lambda architecture (stream + batch) over pure streaming (Kappa).**
- *Requirement:* real-time dashboards **and** invoice-grade accuracy, with fraud decisions that may come hours later.
- *Pick:* streaming for speed, batch over the immutable S3 archive for the final bill.
- *Cost:* two codepaths computing similar numbers, which can drift. We mitigate this with **shared aggregation logic** (same library/SQL in both) and a **reconciliation job** that alerts when they differ.
- *Alternative to mention:* Kappa (stream only, replay Kafka to recompute) works if your stream processor guarantees exactly-once and fraud rules are stable. Many teams start with Kappa and add batch billing once disputes appear.

**Design choice: a separate, logic-free archiver (Kafka Connect) over having Flink write S3.**
- *Requirement:* the batch path must still be correct when the stream path is wrong. Lambda only helps if the two paths don't share a failure mode.
- *Pick:* the Kafka Connect S3 sink, running as its own consumer group. It copies raw records to S3 unchanged and contains no business logic.
- *Why not Flink:*
  - **Correlated bugs.** Flink dedups, filters and joins. If it wrote the archive, you'd be tempted to archive its *cleaned* output. Then a dedup bug or an over-aggressive bot rule would silently drop billable events from the source of truth too, and you couldn't recompute from raw data (requirement #5).
  - **Blast radius and deploy cadence.** Flink logic changes often (fraud rules, windows, schemas), and each redeploy restarts the job. The archiver almost never changes. It keeps running when Flink crashes, is mid-deploy, or is backpressured by a slow Pinot or Redis.
  - **File sizing.** Flink's file sink commits files on checkpoints. The fast path wants frequent checkpoints, which means many small Parquet files. Spark wants large files (~128 MB–1 GB), and Connect rolls files by size or time independently.
  - **Simplicity.** The S3 sink is configuration only. It names files deterministically from Kafka offsets, so a retry overwrites the same file. That gives effectively-once writes into `dt=/hour=` partitions.
- *Cost:* one more component to run and monitor.
- *Alternative to mention:* what matters is a separate job with no logic, not the specific tool. A second, minimal Flink job that only archives, Kinesis Firehose, or MSK Connect all work.

**Design choice: land raw events in S3 first, then run Spark over S3, instead of Spark reading Kafka directly.** Kafka moves the events; S3 is the permanent record.

| Concern | Spark reads Kafka directly | S3 → Spark |
|---|---|---|
| Retention | 7 days. Disputes, fraud refunds and audits need months | Cheap, effectively unlimited (13 months kept), 11 nines durability |
| Reproducibility | Input is an offset range that eventually expires | Day D = a fixed set of immutable files. A re-run gives the same bill, which `source_run_id` relies on |
| Read efficiency | Row-by-row reads of all ~5 TB/day of raw records | Columnar Parquet (~1 TB). Spark reads only needed columns and skips partitions |
| Impact on ingest | A full-day scan pushes hot data out of the brokers' page cache and competes with producers and Flink | Zero load on Kafka |
| Other uses | — | Ad-hoc queries (Athena), ML fraud training, shadow runs, recomputing old days |

Two parts of the design also depend on S3:
- The **late-event grace period (T+6 h)** works naturally on time-partitioned files: wait, then read partitions `dt=D`.
- The reconciliation check **Kafka count vs S3 count per hour** (§5.4) only works because S3 is a separate copy you can count against.

*Modern variant:* Kafka tiered storage, or writing an **Iceberg/Delta** table instead of plain Parquet, blurs this line. Iceberg snapshots let you bill exactly what was visible at close time. The principle stays the same: bill from an immutable, long-lived, columnar copy, not from a short-lived log.

> **Phrase:** *"The raw archive is written by something with no logic and no shared code, so a bug in my streaming logic can't corrupt my billing input. Kafka is the transport; S3 is the permanent record."*

---

## 5. Deep Dives

### 5.1 Write path: fast, available, durable

The collector is on the user's critical path, so it does as little as possible:

1. Parse + **verify HMAC** (pure CPU, microseconds). Reject invalid tokens with 204, so we don't give attackers feedback.
2. **Enrich** cheaply: server receive time, IP → geo, user-agent class.
3. **Produce to Kafka** with `acks=all`, `min.insync.replicas=2`, `enable.idempotence=true`, batching with `linger.ms≈5`.
4. Return 204 / 302 **only after the Kafka ack**. That ack is the durability promise.

**If Kafka is slow or down:** the collector writes to a **local disk spool** (an append-only file) and a sidecar replays it later. It still returns success to the client, because the event is durable on local disk. This is write-behind with a durable buffer (OVERVIEW §3), and it keeps the redirect working during a Kafka incident (graceful degradation, OVERVIEW §8).

**Design choice: Kafka over SQS/Kinesis (OVERVIEW §4).** Kafka keeps events so they can be replayed, supports many consumer groups (Flink, S3 sink, fraud ML), and handles ~250 MB/s easily. Kinesis would need ~250+ shards at 1 MB/s each. SQS deletes messages on ack, so there's no replay.

**Partition key = `impression_id`:** this spreads load evenly across partitions with no hot campaign at ingest. It also routes an impression and its click to the **same partition**, which makes the click↔impression join and dedup local.

**Multi-region:** collectors and Kafka run in every region, close to users (cross-region RTT is 50–150 ms). MirrorMaker replicates to a central region for billing. Events are keyed by a globally unique ID, so merging regions can't create collisions.

### 5.2 Deduplication: where duplicates come from and how each layer handles them

Delivery is **at-least-once end to end** (OVERVIEW §4), so duplicates *will* happen:

| Source of duplicate | Example | Defence |
|---|---|---|
| Client retry | Beacon times out on a flaky mobile network and resends | Same `impression_id` in token → dedup downstream |
| Page reload / ad re-render | User refreshes; same cached ad markup fires again | Same token → same `impression_id` → dropped |
| Double-click | User taps twice | `click_id = hash(impression_id)` → one click per impression |
| Collector → Kafka retry | Ack lost, producer resends | Kafka **idempotent producer** (sequence numbers per partition) |
| Flink restart | Reprocesses from last checkpoint | **Exactly-once checkpoints** + idempotent sinks (§5.3) |
| Spool replay | Spool event already reached Kafka before crash | Event-level dedup in Flink |
| Batch job re-run | Daily job retried | Ledger unique constraint (§5.4) |

**Streaming dedup in Flink:**
```
stream.keyBy(event_id)
      .process(  if state.seen(event_id): drop
                 else: state.put(event_id, ttl = 24h); emit )
```
- **Clicks:** exact dedup. 100M/day × ~40 B ≈ 4 GB of state. Easy.
- **Impressions:** 10B/day × ~40 B ≈ 400 GB of state across the cluster. That's feasible with RocksDB state on local SSD. Alternatively use a **Bloom filter per time bucket**, which is far smaller, but a false positive drops a real impression (under-counting). That's acceptable for the *approximate* dashboard because the batch path recounts exactly.
- **TTL bound:** tokens expire (for example, reject events with `served_at` > 24 h old at the collector), so dedup state never needs to remember older than that.

**Batch dedup (authoritative):** `SELECT DISTINCT ON (event_id)` / `GROUP BY event_id` over a full day in Spark. It's exact, needs no TTL tricks, and has no state limits. **This is the number we bill.**

> **Phrase:** *"Exactly-once doesn't exist on the network. I get effectively-once with at-least-once delivery plus idempotency at every hop, keyed on an ID that the ad server generates."*

### 5.3 Aggregation: event time, late data, idempotent sinks

**Event time, not processing time.** Bucket by `served_at` / client event time, not arrival time. Otherwise a 10-minute Kafka backlog would shift spend into the wrong minute, or even the wrong billing day. Clocks drift (OVERVIEW §6), so:
- Use **server-signed `served_at`** from the token as the authoritative time. Client clocks can't be trusted.
- Flink **watermarks** allow ~1–2 minutes of out-of-order data. A window closes when the watermark passes it.
- **Late events** (after the watermark) go to a side output. The batch path picks them up anyway, so nothing billable is lost.

**Window:** 1-minute tumbling windows keyed by `(ad_id)`, emitting `{ad_id, campaign_id, minute, impressions, viewable_impressions, clicks, spend_micros}`.

**Idempotent sink: upsert, don't increment.** Write aggregates as `UPSERT (ad_id, minute) SET counts = X`, not `counts += X`. If Flink replays a window after a crash, the same row is overwritten with the same value. This is the "set status = PAID rather than increment balance" rule (OVERVIEW §4). Pinot/Druid/ClickHouse all support keyed upserts or replacing segments.

**Hot keys (OVERVIEW §2, §7):** a Super Bowl campaign might take 20% of all impressions. Keying by `ad_id` would overload one Flink subtask. Fix it with **two-phase aggregation**:
1. Pre-aggregate locally per `(ad_id, partition)` (or key-salt: `ad_id#rand(0..15)`).
2. Then combine partial sums by `ad_id`. This shrinks shuffle volume by about 1,000×.

### 5.4 Billing accuracy: the money path

**Principles:**
- **Money in integer micros** (`BIGINT`, 1 USD = 1,000,000 micros). Never floats.
- **Price comes from the signed token**, not looked up later.
- **Append-only, double-entry ledger** (OVERVIEW §2, Grab angle: GrabPay). Corrections are new entries, never `UPDATE`s.
- **Streaming spend is provisional; batch spend is final.**

**Daily billing close (per advertiser time zone, after a grace period, e.g. T+6 h for late events):**

```
1. Spark reads S3 raw events for billing day D
2. Exact dedup by event_id
3. Apply invalid-traffic filter (rules + ML scores, which are only available offline)
4. Drop clicks with no matching valid impression
5. billable = Σ price_micros  per (campaign_id, D)
6. Cap at budget:  charge = min(billable, campaign_budget_for_D)
7. Write to ledger in ONE transaction (below)
```

**Ledger schema (Postgres):**
```sql
CREATE TABLE ledger_entries (
  entry_id        BIGINT PRIMARY KEY,
  idempotency_key TEXT   NOT NULL UNIQUE,   -- 'daily:{campaign_id}:{D}:v{run}'
  account_id      BIGINT NOT NULL,          -- advertiser_receivable / ad_revenue
  direction       TEXT   NOT NULL CHECK (direction IN ('DEBIT','CREDIT')),
  amount_micros   BIGINT NOT NULL CHECK (amount_micros > 0),
  campaign_id     BIGINT NOT NULL,
  billing_date    DATE   NOT NULL,
  source_run_id   TEXT   NOT NULL,          -- which Spark run produced it (audit)
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```
- Each daily charge = **one debit (advertiser receivable) + one credit (revenue)** in the same transaction. Debits always equal credits.
- `INSERT ... ON CONFLICT (idempotency_key) DO NOTHING` makes re-running the job safe (OVERVIEW §4 idempotency). A retry can't double-charge.
- Results are reproducible because the input (immutable S3 files for day D) and the code version are both recorded in `source_run_id`.

**Corrections (fraud refunds, disputes, late events after close):** run a recompute for day D → diff against what was billed → post an **adjusting entry** (`idempotency_key = 'adjust:{campaign}:{D}:{reason}:{n}'`). The original entry is never touched. Auditors can trace every cent.

**Reconciliation (OVERVIEW §8 data reliability):**
| Check | Alert threshold |
|---|---|
| Stream provisional spend vs batch final spend per campaign | diff > 0.5% |
| Kafka message count vs S3 row count per hour | any gap |
| Collector "accepted" count vs Kafka produced count | any gap |
| Ledger: Σ debits = Σ credits | must be exactly 0 |
| Invoice total vs ledger total per advertiser/month | must be exactly 0 |

> **Phrase:** *"For billing I choose correctness over freshness. An invoice that's 6 hours late is fine; an invoice that's wrong is a support ticket, a refund, and lost trust."*

### 5.5 Budget enforcement: the overspend problem

The ad server must stop serving when a campaign's budget is exhausted. But spend is known only after events flow through the pipeline (seconds of lag), and at 500k QPS the ad server can't do a strongly consistent check on every serve.

**Design:**
- Flink increments `spend:{campaign_id}:{date}` in **Redis** each window (idempotent: `SET` the window's value into a hash field `minute → spend`, and the reader sums the fields).
- The ad server reads the spend from a local cache refreshed every ~1 s, and stops serving at `spend ≥ budget`.
- **Pacing:** throttle serving probabilistically as spend approaches budget (e.g. serve probability falls as you near 100%) so the campaign doesn't burst past it in the final seconds.

**Trade-off (OVERVIEW §5 CAP per feature):**
| Feature | Choice | Consequence |
|---|---|---|
| Budget check on serve | **AP / eventual** | Small overspend (~seconds of traffic) is possible |
| Advertiser charge | **CP / exact** | Billing caps at budget, so **the advertiser never pays more than their budget** |
| Overdelivery cost | Absorbed by the platform | Monitored as a KPI; tune pacing if it grows |

A strongly consistent alternative (a distributed counter with a lock or conditional decrement per serve) would add latency to every ad request and create a hot key per big campaign. The cost isn't worth a few cents of overdelivery.

### 5.6 Invalid traffic and fraud (OVERVIEW Grab cheat sheet §9)

Layered, from cheap/inline to expensive/offline:

| Layer | Where | Catches |
|---|---|---|
| HMAC token validation | Collector (inline) | Forged events, tampered prices |
| Token expiry (`served_at` < 24 h) | Collector | Replay of old tokens |
| Rate limiting per IP / device ID (token bucket, OVERVIEW §7) | Collector | Click floods |
| Click must join a valid impression; click within N s after impression is suspicious | Flink | Click injection |
| Known bot lists / data-centre IP ranges / UA rules | Flink | Simple bots |
| ML model (behaviour patterns, click farms, CTR anomalies) | Batch (offline) | Sophisticated fraud |
| Post-billing refund via adjusting ledger entry | Billing svc | Fraud discovered days later |

Invalid events are **not deleted**. They're flagged (`ivt_reason`) and kept for audit and model training. Advertisers can see the "invalid traffic filtered" counts in their reports, which builds trust.

### 5.7 Reliability & operations (OVERVIEW §8)

- **Failure modes:**
  - *Collector dies:* stateless, so the NLB health check removes it. The client retries, and the dedup key makes that safe.
  - *Kafka broker dies:* RF=3, `min.insync.replicas=2`, so no data is lost and the cluster keeps serving.
  - *Flink job crashes:* restore from the last checkpoint, then replay from the committed Kafka offsets. Idempotent sinks make the replay safe.
  - *OLAP store down:* dashboards are stale, but billing is unaffected because it reads S3.
  - *Bad deploy of aggregation logic:* fix the code, **replay** Kafka (7 days) or recompute from S3, then post adjusting entries.
- **RPO / RTO:** ingest RPO = 0 after ack. Dashboard RTO ~minutes. Billing RTO ~hours (it's a daily batch anyway).
- **Key metrics:** collector p99 + error rate (RED), Kafka **consumer lag**, dedup drop rate (a spike means a client retry bug), late-event rate, stream-vs-batch diff, IVT rate per publisher, overdelivery $.
- **Deployments (OVERVIEW §9):** canary collectors by region. For aggregation/billing logic changes, **shadow-run** the new Spark job on the same day's data and diff the output before switching. Never let a shadow run write to the ledger.
- **Data retention/privacy:** keep raw events in S3 for 13 months (dispute window + yearly comparisons), hash or truncate IPs, honour user opt-outs.

---

## 6. Trade-offs & Wrap-up (OVERVIEW §0 step 6)

| Decision | Chose | Over | Because | Cost |
|---|---|---|---|---|
| Ingest store | Kafka | Direct DB writes | 500k writes/s, replay, fan-out | Operational complexity |
| Processing model | Lambda (stream + batch) | Pure streaming | Fast dashboards *and* exact, re-computable bills | Two codepaths; needs reconciliation |
| Raw archiver | Kafka Connect S3 sink (no logic) | Flink writing S3 | Stream-path bugs can't corrupt the billing input; separate deploys; large files | One more component to run |
| Batch input | S3 Parquet | Spark reading Kafka | Long retention, reproducible input, columnar scans, no load on brokers | Extra storage copy (cheap) |
| Dedup key | Server-generated `impression_id` in signed token | Client-generated or content hash | Stable across retries, unforgeable | Token adds ~200 B to ad markup |
| Delivery | At-least-once + idempotency | Exactly-once transport | Exactly-once over a network isn't real | Every sink must be idempotent |
| Dashboards | Eventual (~1 min) | Strong | Volume; advertisers accept approximate | Small stream-vs-invoice diffs |
| Budget | Eventual + pacing + charge cap | Strongly consistent counter | No latency on serving path, no hot key | Platform absorbs small overspend |
| Ledger | Postgres, double-entry, append-only | NoSQL | ACID, unique constraints, auditability | Doesn't need scale, so no real cost |
| Money type | Integer micros | Float/decimal in app | No rounding drift across billions of events | — |

**At 10× (5M events/s):**
- Add Kafka partitions and Flink parallelism. The partition key already spreads load evenly.
- Switch impression dedup to Bloom filters on the fast path. Keep exact dedup in batch.
- **Cell-based architecture** (OVERVIEW §7): independent ingest + stream cells per region, so a spike in one region doesn't hurt others.
- Pre-aggregate on the collector (micro-batches of counts per ad per second) for impressions only. Keep clicks as individual events because they carry the money.
- Move the billing batch to hourly so less lands at day close.

**Summary to give the interviewer (30 seconds):**
> *"The ad server signs a token with a unique impression ID and the locked price. Stateless collectors validate it and write to Kafka with acks=all before responding, so ingest is fast, available, and durable. From Kafka, a Flink job dedups, filters, and aggregates into 1-minute windows with event time and idempotent upserts, feeding dashboards and budget counters. That path is approximate by design. Raw events also land in S3, where a daily Spark job does exact dedup and offline fraud filtering, then writes idempotent, double-entry entries to a Postgres ledger. That's the number we invoice. A reconciliation job compares the two paths, and corrections are always new adjusting entries."*

---

## Self-check
- [ ] Can I explain why the dedup key must be created by the ad server, not the client or collector?
- [ ] Can I list five sources of duplicates and the defence for each?
- [ ] Can I explain event time vs processing time, watermarks, and what happens to late events?
- [ ] Can I explain why aggregate sinks upsert instead of increment?
- [ ] Can I defend Lambda over Kappa for billing, and say when Kappa would be fine?
- [ ] Can I explain why the S3 archiver is separate from Flink, and why Spark reads S3 rather than Kafka?
- [ ] Can I explain how budget overspend is bounded and why the advertiser is never overcharged?
- [ ] Can I sketch the double-entry ledger with an idempotency key and adjusting entries?
