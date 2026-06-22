# Kafka & Event-Driven Design — Interview Prep Guide

---

## Part 1: Core Concepts

### 1.1 What Is Event-Driven Architecture (EDA)?

Event-Driven Architecture is a design paradigm where components communicate by **producing and consuming events** rather than calling each other directly. An **event** is an immutable record of something that happened (e.g., `OrderPlaced`, `PaymentProcessed`).

**Three core roles:**
- **Producer** — emits events when something happens
- **Broker** — receives, stores, and routes events (e.g., Kafka)
- **Consumer** — reacts to events it's interested in

**Key benefit:** producers and consumers are **decoupled** — they don't know about each other, enabling independent scaling and deployment.

---

### 1.2 Apache Kafka Architecture

Kafka is a distributed **event streaming platform** designed for high-throughput, fault-tolerant, durable event storage and delivery.

#### Core Components

| Component | Role |
|-----------|------|
| **Broker** | A Kafka server that stores and serves messages |
| **Topic** | A named, ordered, append-only log of events |
| **Partition** | A topic is split into partitions for parallelism; each is an ordered sub-log |
| **Producer** | Writes records to a topic |
| **Consumer** | Reads records from a topic |
| **Consumer Group** | A group of consumers that collectively process a topic; each partition is assigned to one consumer in the group |
| **ZooKeeper / KRaft** | Cluster metadata management (ZooKeeper is being replaced by KRaft in newer versions) |
| **Offset** | A sequential ID for each record within a partition; consumers track their position using offsets |

#### Topic Partitions — Why They Matter

```
Topic: "orders"  (3 partitions)

Partition 0: [msg0] [msg3] [msg6] ...
Partition 1: [msg1] [msg4] [msg7] ...
Partition 2: [msg2] [msg5] [msg8] ...
```

- **Ordering** is guaranteed **within a partition**, not across partitions
- Producers choose the partition via a **key** (same key → same partition, ensuring ordering per entity, e.g., per `userId`)
- More partitions = higher throughput (more consumers can work in parallel)

---

### 1.3 Delivery Semantics

| Semantic | Description | Risk |
|----------|-------------|------|
| **At-most-once** | Message delivered zero or one time | Data loss possible |
| **At-least-once** | Message delivered one or more times | Duplicate processing possible |
| **Exactly-once** | Message delivered exactly once | Requires idempotent producers + transactional consumers |

Kafka supports **exactly-once semantics (EOS)** via:
- `enable.idempotence=true` on the producer
- Kafka Transactions (`beginTransaction` / `commitTransaction`)
- Transactional reads on the consumer side (`isolation.level=read_committed`)

---

### 1.4 Producer Concepts

**Key configuration knobs:**

| Config | Purpose |
|--------|---------|
| `acks=0/1/all` | How many broker acknowledgements before the write is considered successful. `all` = strongest durability |
| `retries` | Number of retry attempts on transient failure |
| `enable.idempotence` | Prevents duplicate writes on retry |
| `linger.ms` | Batching delay — wait up to N ms before sending to improve throughput |
| `batch.size` | Max size of a batch of records sent together |
| `compression.type` | `none`, `gzip`, `snappy`, `lz4`, `zstd` |

**Partition routing:**
- No key → round-robin across partitions
- With key → `murmur2(key) % numPartitions` → deterministic partition
- Custom → implement `Partitioner` interface

---

### 1.5 Consumer Concepts

**Consumer Groups** allow horizontal scaling: Kafka assigns each partition to exactly one consumer in a group. If a consumer dies, Kafka triggers a **rebalance** to reassign partitions.

**Offset management:**
- Consumers commit their offset to track progress
- **Auto-commit** (`enable.auto.commit=true`): convenient but can cause data loss or duplicates
- **Manual commit**: gives precise control — commit only after successful processing

**Rebalance strategies:**
- `RangeAssignor` — assigns contiguous partition ranges
- `RoundRobinAssignor` — distributes evenly round-robin
- `StickyAssignor` — minimises partition movement during rebalances (preferred for stateful consumers)
- `CooperativeStickyAssignor` — incremental rebalance; consumers continue processing while reassignment happens

---

### 1.6 Kafka Storage & Retention

Kafka stores messages on disk in **segment log files**. Unlike traditional message queues, **messages are not deleted on consumption** — they are retained based on policy:

- **Time-based**: `retention.ms` (default 7 days)
- **Size-based**: `retention.bytes`
- **Compaction**: keeps only the latest record per key (`log.cleanup.policy=compact`) — useful for maintaining a "current state" view

**Log compaction use cases:** user profile updates, latest device config, materialised views.

---

### 1.7 Kafka Replication & Fault Tolerance

Each partition has one **leader** and N-1 **followers** (replicas). All reads/writes go to the leader; followers replicate asynchronously.

- **Replication Factor**: how many copies of each partition exist (typically 3 in production)
- **ISR (In-Sync Replicas)**: set of replicas that are caught up to the leader
- **`min.insync.replicas`**: minimum number of ISR replicas that must acknowledge a write when `acks=all`. Guards against data loss if a replica is lagging.

If the leader fails, an ISR follower is elected as the new leader.

---

### 1.8 Kafka Streams & ksqlDB

**Kafka Streams** is a Java library for building stream processing applications on top of Kafka. Key abstractions:

| Abstraction | Description |
|-------------|-------------|
| `KStream` | Unbounded stream of records (insert semantics) |
| `KTable` | Changelog stream — each key has a latest value (update semantics) |
| `GlobalKTable` | KTable replicated to all instances; used for lookups/joins |
| `Windowing` | Time-based grouping: Tumbling, Hopping, Session windows |

**ksqlDB** provides a SQL-like interface to process Kafka topics as streams or tables, without writing Java code.

---

### 1.9 Schema Management

In event-driven systems, schema compatibility matters because producers and consumers evolve independently.

**Apache Avro** (with **Confluent Schema Registry**) is the most common approach:
- Schemas are versioned and stored in the registry
- Producers and consumers reference schemas by ID
- Compatibility modes: `BACKWARD`, `FORWARD`, `FULL`, `NONE`

**Backward compatibility**: new schema can read data written by old schema (safe for consumer upgrade first).
**Forward compatibility**: old schema can read data written by new schema (safe for producer upgrade first).

---

### 1.10 Event-Driven Patterns

#### CQRS (Command Query Responsibility Segregation)
Separates **writes** (commands that change state) from **reads** (queries). Events are produced on writes and consumed to build read-optimised projections/views.

#### Event Sourcing
The system's state is stored as a **sequence of events**, not as the current value. To get current state, replay the event log. Kafka's durable log makes it a natural fit.

- Pros: full audit trail, time travel, replayability
- Cons: eventual consistency, snapshot management complexity

#### Outbox Pattern
To atomically persist a database change **and** produce a Kafka event, write the event to an **outbox table** in the same DB transaction, then a separate process (or CDC tool like Debezium) reads and publishes it.

#### Saga Pattern
Manages distributed transactions across services using a sequence of local transactions, each publishing an event to trigger the next step. On failure, compensating transactions are issued.

- **Choreography saga**: each service reacts to events autonomously
- **Orchestration saga**: a central coordinator directs the steps

#### Dead Letter Queue (DLQ)
When a consumer cannot process a message after N retries, the message is routed to a DLQ topic for later inspection and reprocessing.

---

### 1.11 Kafka vs. Other Systems

| | **Kafka** | **RabbitMQ** | **AWS SQS/SNS** |
|---|---|---|---|
| Model | Log-based pub/sub | Message queue / exchange | Queue / fan-out |
| Message retention | Configurable (days+) | Deleted on ACK | Up to 14 days |
| Consumer replay | Yes (seek to any offset) | No | No |
| Ordering | Per partition | Per queue | FIFO queues only |
| Throughput | Very high | Medium | High (managed) |
| Ideal for | Event streaming, audit logs | Task queues, RPC | Serverless, AWS-native |

---

## Part 2: Interview Questions & Answers

---

### Fundamentals

---

**Q1: What is the difference between a message queue and a log-based broker like Kafka?**

**A:** In a traditional message queue (e.g., RabbitMQ, SQS), messages are **deleted once consumed** and each message is typically delivered to one consumer. In a log-based system like Kafka, messages are written to an **immutable, ordered log** and retained for a configured period. Multiple independent consumer groups can read the same topic from any offset, enabling replay, auditing, and decoupled processing pipelines. This makes Kafka suited for event streaming, not just task distribution.

---

**Q2: How does Kafka guarantee message ordering?**

**A:** Kafka guarantees ordering **within a single partition**. Records written to the same partition are always read in the order they were written. To ensure ordering for a specific entity (e.g., all events for a given `orderId`), producers use a **partition key** — Kafka hashes the key to deterministically route all records with the same key to the same partition. Ordering across partitions is not guaranteed.

---

**Q3: What is a consumer group and how does partition assignment work?**

**A:** A consumer group is a set of consumers that collaboratively consume a topic. Kafka assigns each partition to exactly **one consumer within the group** at a time, so partitions are the unit of parallelism. If a consumer group has fewer consumers than partitions, some consumers handle multiple partitions. If there are more consumers than partitions, the excess consumers sit idle. When a consumer joins or leaves, Kafka triggers a **rebalance** to redistribute partitions.

---

**Q4: Explain the `acks` configuration and its trade-offs.**

**A:**
- `acks=0`: producer fires and forgets — highest throughput, but data loss is possible if the broker crashes before writing.
- `acks=1`: leader acknowledges after writing to its log — moderate durability; data is lost if the leader crashes before replication.
- `acks=all` (or `-1`): the leader waits for all **in-sync replicas** to acknowledge — strongest durability, higher latency. Combined with `min.insync.replicas=2`, this ensures at least one replica has the data beyond the leader.

For financial or critical data, `acks=all` + idempotent producer is the standard choice.

---

**Q5: What is the difference between at-least-once and exactly-once delivery in Kafka?**

**A:** With **at-least-once**, a producer retries on failure, potentially writing a duplicate if the original write succeeded but the acknowledgement was lost. A consumer might also reprocess events if it crashes before committing its offset. With **exactly-once semantics (EOS)**, Kafka uses idempotent producers (each message has a sequence number; the broker deduplicates retries) and transactions (producer groups writes to multiple partitions atomically, and consumers use `read_committed` isolation). EOS adds latency and is only needed when duplicate processing has side effects.

---

**Q6: How does Kafka handle consumer lag and what monitoring would you put in place?**

**A:** Consumer lag is the difference between the **latest offset** in a partition and the **committed offset** of a consumer group — i.e., how many messages the consumer is behind. High lag indicates the consumer is slower than the producer.

Monitoring approach:
- Track `consumer_lag` per partition via Kafka's consumer group API or tools like Burrow, Confluent Control Center, or Prometheus JMX exporter
- Alert when lag exceeds a threshold or grows monotonically
- Remediation: increase consumer parallelism (add more partitions + consumers), optimise processing logic, or scale consumer instances horizontally

---

### Design & Architecture

---

**Q7: How would you design a system to guarantee no message loss in Kafka?**

**A:** A defence-in-depth approach:

1. **Producer side**: `acks=all`, `enable.idempotence=true`, `retries=MAX_INT`, `max.in.flight.requests.per.connection=5` (or 1 for strict ordering)
2. **Broker side**: replication factor ≥ 3, `min.insync.replicas=2`, disable unclean leader election (`unclean.leader.election.enable=false`)
3. **Consumer side**: manual offset commits, only committing after successful processing; idempotent processing logic to handle duplicates gracefully
4. **Operational**: monitor ISR shrinkage, set retention long enough to cover failure recovery windows

---

**Q8: How would you implement exactly-once processing end-to-end (from DB → Kafka → DB)?**

**A:** Use the **Outbox Pattern** with CDC:

1. Application writes to the DB and inserts an event record into an **outbox table** in the **same transaction** — atomicity guaranteed by the DB.
2. A CDC tool (e.g., **Debezium**) reads the outbox table's WAL/changelog and publishes events to Kafka, using Kafka transactions for exactly-once delivery to Kafka.
3. The consumer reads from Kafka using `read_committed` isolation, processes the event, and writes to the target DB — using idempotent writes (upsert with a unique event ID) to handle any duplicates.

This avoids the dual-write problem (writing to both DB and Kafka non-atomically).

---

**Q9: A topic has 12 partitions and a consumer group has 4 consumers. How would you scale if consumers are falling behind?**

**A:** Options in order of preference:

1. **Increase consumer instances up to 12** (max 1 consumer per partition). Since we have 12 partitions, we can add up to 8 more consumers for full parallelism.
2. **Optimise consumer processing** — batch DB writes, async I/O, reduce per-message overhead.
3. **Increase partitions** (from 12 to, say, 24) — allows even more consumers. Caution: you cannot reduce partitions once increased; also affects key-based ordering guarantees.
4. **Use a separate thread pool** within each consumer for CPU-bound processing (decoupling Kafka polling from processing).

---

**Q10: How does log compaction work and when would you use it?**

**A:** Log compaction (`log.cleanup.policy=compact`) causes Kafka to retain only the **latest record for each key** in a partition. Older records with the same key are eventually garbage collected. A tombstone (record with a `null` value) signals deletion of a key.

**When to use it:**
- Materialised views or read models that need only the latest state per entity
- Event sourcing snapshots (e.g., latest user profile, device config)
- Change Data Capture (CDC) topics — downstream consumers can rebuild current state by replaying only compacted logs
- Kafka Streams `KTable` topics internally use compaction

It is **not** appropriate for event streams where history matters (e.g., click events, audit logs) — use time-based retention there.

---

**Q11: Design an event-driven order processing system.**

**A:**

**Topics:**
- `orders.created`
- `orders.payment.requested`
- `orders.payment.completed` / `orders.payment.failed`
- `orders.fulfillment.started`
- `orders.shipped`

**Services:**
- **Order Service**: accepts REST command → validates → persists → publishes `orders.created`
- **Payment Service**: consumes `orders.created` → charges payment → publishes `orders.payment.completed` or `orders.payment.failed`
- **Inventory Service**: consumes `orders.payment.completed` → reserves stock → publishes `orders.fulfillment.started`
- **Shipping Service**: consumes `orders.fulfillment.started` → arranges delivery → publishes `orders.shipped`
- **Notification Service**: consumes multiple topics → sends email/SMS per event type

**Resilience:**
- Each service uses manual offset commits and idempotent writes
- Failed payments trigger a compensating event to release any reserved resources (Saga pattern)
- DLQ topics handle poison messages

**Partition key**: `orderId` → all events for an order land on the same partition, enabling per-order ordering guarantees.

---

### Advanced Topics

---

**Q12: What is the difference between KStream and KTable in Kafka Streams?**

**A:**
- **KStream** represents an **unbounded stream of events** with insert semantics — every record is an independent event (e.g., page views, transactions).
- **KTable** represents a **changelog stream** with update semantics — each new record for a key replaces the previous value. It represents the current state of an entity (e.g., latest account balance per user).

In practice, KStream is like a continuously appended log; KTable is like a materialised view. You can join them: e.g., enrich a click-stream (KStream) with user profile data (KTable) to get the profile at the time of the click.

---

**Q13: How does Kafka handle back-pressure?**

**A:** Kafka does not natively implement back-pressure in the reactive sense — producers can write faster than consumers can process. Back-pressure is handled indirectly:

- **Producer side**: `buffer.memory` limits how much data the producer buffers locally. If the buffer fills up, `send()` blocks (or throws if `max.block.ms` is exceeded), slowing the producer organically.
- **Consumer side**: consumers pull at their own rate — they won't be overwhelmed since they control when to call `poll()`.
- **Lag monitoring**: consumer lag is the visible symptom of back-pressure; it triggers scaling.
- **Application level**: consumers can implement flow control (e.g., pause a partition via `consumer.pause()` when a downstream dependency is slow, then resume later).

---

**Q14: How would you handle schema evolution in a Kafka-based system?**

**A:** Use a **Schema Registry** (e.g., Confluent Schema Registry) with **Avro**, **Protobuf**, or **JSON Schema**:

1. Register schemas with version numbers
2. Choose a **compatibility mode**:
   - `BACKWARD`: consumers using the new schema can read old data (add optional fields, remove fields with defaults) — upgrade consumers first
   - `FORWARD`: old consumers can read new data — upgrade producers first
   - `FULL`: both directions — safest, most restrictive
3. Set `auto.register.schemas=false` in production to prevent accidental schema changes
4. Use schema IDs embedded in the message payload (Confluent wire format: 5-byte header) — consumers fetch the schema by ID at read time

For breaking changes that can't fit a compatibility mode, produce to a new topic version (`orders.v2`) and migrate consumers gradually.

---

**Q15: What is the Outbox Pattern and why is it important?**

**A:** The Outbox Pattern solves the **dual-write problem**: when a service needs to both update a database and publish a Kafka event, doing them separately risks inconsistency (one succeeds, the other fails).

**Solution:**
1. Write the DB update **and** an event record to an `outbox` table in a **single ACID transaction**
2. A relay process (e.g., Debezium reading the DB changelog, or a polling process) reads new outbox records and publishes them to Kafka
3. Once successfully published, the outbox record is marked as processed or deleted

This guarantees that the DB state and the Kafka event are always consistent. The relay may publish duplicates on retry, so consumers should be idempotent.

---

**Q16: How would you implement a distributed lock or exactly-once action across services using Kafka?**

**A:** Kafka itself is not a distributed lock, but you can achieve single-writer semantics:

- **Single-partition, single-consumer**: assign one partition for a resource key; only one consumer processes it at a time by group assignment
- **Optimistic locking with event versioning**: include a `version` field in events; consumers validate the version before applying and reject out-of-order events
- **Fencing tokens**: when a new consumer takes over a partition after a rebalance, generate a new fencing token; discard writes from old instances using the previous token (useful when writing to external systems)
- For actual distributed locking needs, use **Redis** (Redlock) or **ZooKeeper/etcd** — Kafka is not designed for this use case directly

---

**Q17: Walk me through what happens when a Kafka broker goes down.**

**A:**

1. The failed broker stops responding to heartbeats sent to the **Controller** (or ZooKeeper in older versions)
2. The Controller detects the failure and identifies all partitions for which the failed broker was the **leader**
3. For each such partition, the Controller elects a new leader from the **ISR** (in-sync replicas) of that partition
4. The Controller updates partition metadata and propagates it to all remaining brokers and clients
5. **Producers** that were connected to the failed broker receive a `NotLeaderForPartition` error, fetch updated metadata, and retry against the new leader
6. **Consumers** similarly refresh metadata and reconnect to the new leader
7. If `unclean.leader.election.enable=false` (recommended), only ISR replicas can be elected — preventing data loss at the cost of temporary unavailability if no ISR replica is available

The whole failover typically completes in seconds.

---

### Quick-Reference Cheat Sheet

| Concept | One-liner |
|---------|-----------|
| Topic | Append-only, ordered log; split into partitions |
| Partition | Unit of parallelism and ordering |
| Consumer Group | Collectively consumes a topic; 1 consumer per partition |
| Offset | Position of a record within a partition |
| ISR | Replicas caught up to the leader |
| `acks=all` | Strongest durability; waits for all ISR to acknowledge |
| Idempotent Producer | Deduplicates retries via sequence numbers |
| Log Compaction | Keeps only latest record per key |
| Outbox Pattern | Atomic DB + event write using a relay |
| Saga | Distributed transaction via compensating events |
| CQRS | Separate write model from read model using events |
| Event Sourcing | State = replay of event log |
| DLQ | Parking lot for unprocessable messages |
| KStream | Unbounded insert stream |
| KTable | Latest-value-per-key changelog |