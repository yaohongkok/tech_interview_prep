# Redis & Caching — Interview Preparation Guide

---

## Part 1: Core Concepts

### What Is Caching?

Caching is the practice of storing copies of frequently accessed data in a fast-access storage layer (the **cache**) so future requests for that data can be served faster, reducing load on the primary data store (e.g., a database).

The goal: **lower latency**, **higher throughput**, and **reduced backend load**.

---

### Cache Terminology

| Term | Definition |
|---|---|
| **Cache Hit** | The requested data is found in the cache. |
| **Cache Miss** | The requested data is not in the cache; must be fetched from the source. |
| **Cache Eviction** | Removing data from the cache, typically due to capacity limits. |
| **TTL (Time-to-Live)** | How long a cached entry is considered valid before expiring. |
| **Hot Key** | A cache key that receives a disproportionately high number of requests. |
| **Cache Stampede / Thundering Herd** | Many requests simultaneously miss the cache and all hit the database at once. |

---

### Caching Strategies (Write Policies)

#### 1. Cache-Aside (Lazy Loading)
The application is responsible for reading and writing the cache.

**Flow:**
1. Read from cache.
2. On a miss, read from the database.
3. Write the result into the cache, then return it.

**Pros:** Only caches what's actually needed. Resilient to cache failures.  
**Cons:** Cache misses add latency. Risk of stale data if not managed carefully.

---

#### 2. Write-Through
Data is written to the cache and the database simultaneously on every write.

**Pros:** Cache is always consistent with the database.  
**Cons:** Write latency is higher. May cache data that is never read.

---

#### 3. Write-Behind (Write-Back)
Data is written to the cache first; the database is updated asynchronously.

**Pros:** Very fast writes.  
**Cons:** Risk of data loss if the cache fails before the async write completes.

---

#### 4. Read-Through
The cache sits in front of the database. On a miss, the cache itself (not the app) fetches from the database and populates itself.

**Pros:** Logic is centralized in the cache layer, not the application.  
**Cons:** First request always incurs a miss.

---

### Cache Eviction Policies

When a cache reaches capacity, it must evict entries. Common policies:

| Policy | Description |
|---|---|
| **LRU** (Least Recently Used) | Evict the entry that was accessed least recently. Most common default. |
| **LFU** (Least Frequently Used) | Evict the entry accessed the fewest times. Better for skewed access patterns. |
| **FIFO** (First In, First Out) | Evict the oldest inserted entry regardless of use. |
| **TTL-based** | Expire entries after a set duration. |
| **Random** | Evict a random entry. Simple but unpredictable. |
| **allkeys-lru** | Redis-specific: apply LRU across all keys (not just those with TTL). |

---

### Cache Invalidation

One of the hardest problems in caching. Stale data must be removed or updated when the source of truth changes. Common approaches:

- **TTL expiry** — let entries expire after a set time.
- **Event-driven invalidation** — invalidate cache entries when a write event occurs (e.g., via pub/sub or message queues).
- **Write-through/write-around** — keep cache in sync at write time.
- **Versioned keys** — e.g., `user:42:v3` — change the key on updates so old keys become unreachable.

---

### Distributed Caching

A cache shared across multiple application servers. Avoids each server having its own local cache that can become inconsistent.

**Challenges:**
- **Consistency** across nodes.
- **Network latency** (though still faster than a DB).
- **Hot keys** overloading a single node in a sharded cache.

---

## Part 2: Redis Deep Dive

### What Is Redis?

**Redis** (Remote Dictionary Server) is an open-source, in-memory data structure store used as a cache, message broker, and primary database. It stores data in RAM, making reads and writes extremely fast (typically sub-millisecond).

Redis is **single-threaded** for command execution (as of v6, uses I/O threads for networking, but the command pipeline remains single-threaded), which simplifies consistency and avoids locking.

---

### Redis Data Types

| Type | Use Cases | Key Commands |
|---|---|---|
| **String** | Simple values, counters, session tokens | `GET`, `SET`, `INCR`, `EXPIRE` |
| **Hash** | Object fields (e.g., user profile) | `HGET`, `HSET`, `HMGET`, `HDEL` |
| **List** | Queues, activity feeds, ordered events | `LPUSH`, `RPUSH`, `LPOP`, `LRANGE` |
| **Set** | Unique tags, membership checks, unions/intersections | `SADD`, `SMEMBERS`, `SINTER`, `SUNION` |
| **Sorted Set (ZSet)** | Leaderboards, priority queues, range queries | `ZADD`, `ZRANGE`, `ZRANK`, `ZSCORE` |
| **Bitmap** | Compact boolean flags, user activity tracking | `SETBIT`, `GETBIT`, `BITCOUNT` |
| **HyperLogLog** | Approximate unique count (e.g., unique visitors) | `PFADD`, `PFCOUNT` |
| **Stream** | Append-only log, event streaming (like Kafka-lite) | `XADD`, `XREAD`, `XGROUP` |

---

### Redis Persistence

Redis is in-memory, but it supports optional persistence to disk:

#### RDB (Redis Database Snapshot)
- Saves a point-in-time snapshot of the dataset at configured intervals.
- **Pros:** Compact file, fast restarts.
- **Cons:** Data written since the last snapshot is lost on a crash.

#### AOF (Append-Only File)
- Logs every write operation. On restart, Redis replays the log.
- **Pros:** More durable (can be configured to fsync every write).
- **Cons:** Larger files, slower restarts.

#### RDB + AOF (Hybrid)
- Recommended for most production use cases. Uses RDB for fast restarts and AOF for durability.

---

### Redis High Availability & Scalability

#### Replication
- Redis supports **master-replica** (primary-replica) replication.
- Replicas are read-only and asynchronously receive updates from the master.
- Useful for read scaling and failover.

#### Redis Sentinel
- Provides **automatic failover**: monitors masters and replicas, and promotes a replica if the master goes down.
- Also provides service discovery (clients can ask Sentinel for the current master address).

#### Redis Cluster
- Horizontal **sharding** across multiple nodes.
- Data is split into **16,384 hash slots** distributed across nodes.
- Supports automatic resharding and failover.
- Tradeoff: multi-key operations across different slots are not supported.

---

### Redis Pub/Sub

Redis supports a **publish/subscribe** messaging pattern:
- Publishers send messages to a **channel**.
- Subscribers receive messages on channels they subscribe to.
- Messages are not persisted — if a subscriber is offline, the message is lost. (Use **Streams** for durable messaging.)

```
SUBSCRIBE news
PUBLISH news "Breaking: Redis 8.0 released"
```

---

### Redis Transactions

Redis supports basic transactions via `MULTI` / `EXEC`:
- Commands queued between `MULTI` and `EXEC` are executed atomically.
- Unlike SQL transactions, there is **no rollback** on individual command errors within a transaction.
- `WATCH` can be used for optimistic locking: if a watched key changes before `EXEC`, the transaction is aborted.

---

### Redis Lua Scripting

For complex atomic operations, Redis supports **Lua scripts** via `EVAL`. The script runs atomically on the server, avoiding multiple round-trips.

---

## Part 3: Interview Questions & Answers

---

### General Caching

**Q1: What is the difference between a cache hit and a cache miss? How do you measure cache effectiveness?**

A **cache hit** occurs when the requested data is found in the cache; a **cache miss** means it wasn't and must be fetched from the origin. Cache effectiveness is measured by the **hit rate** (hits / total requests). A high hit rate (typically > 90–95%) indicates the cache is working well. You should also monitor **latency**, **eviction rate**, and **memory usage** to get a full picture.

---

**Q2: What is cache stampede (thundering herd) and how do you prevent it?**

A **cache stampede** happens when a popular cache key expires and many concurrent requests simultaneously miss the cache, all hitting the database at once. Prevention strategies include:

- **Mutex/locking**: Only one request fetches from the DB and repopulates the cache; others wait.
- **Probabilistic early expiration**: Refresh the cache slightly before it expires, reducing the chance of simultaneous misses.
- **Background refresh**: A separate process refreshes cache entries proactively before they expire.
- **Stale-while-revalidate**: Serve the stale value while a background job updates it.

---

**Q3: What is cache invalidation and why is it hard?**

Cache invalidation means removing or updating stale entries when the underlying data changes. It's hard because the cache and the database are separate systems that can drift out of sync. The key challenges are:

- Knowing *when* data has changed (requires tight coupling or event-driven architecture).
- Handling race conditions (a read may populate stale data just after a write invalidates the key).
- Cascading invalidations (one update may affect many cached keys).

Phil Karlton's famous quote: *"There are only two hard things in Computer Science: cache invalidation and naming things."*

---

**Q4: When should you NOT use a cache?**

- When data changes extremely frequently (high write-to-read ratio).
- When data freshness is critical and stale reads are unacceptable.
- When the dataset is too large and eviction would be constant (poor hit rate).
- When the operation being cached is already cheap.
- When the complexity of cache invalidation outweighs the performance benefit.

---

### Redis-Specific

**Q5: Why is Redis so fast?**

- **In-memory storage**: All data lives in RAM; no disk I/O on reads/writes.
- **Single-threaded command execution**: No locking overhead; commands execute sequentially.
- **Efficient data structures**: Purpose-built structures (skip lists, hash tables, zip lists) optimized for the access patterns of each type.
- **Non-blocking I/O multiplexing**: Redis uses `epoll`/`kqueue` to handle thousands of client connections concurrently without threads.

---

**Q6: Explain the difference between Redis RDB and AOF persistence. Which would you choose?**

| | RDB | AOF |
|---|---|---|
| What it stores | Point-in-time snapshots | Log of every write command |
| Durability | Lower (data since last snapshot is lost) | Higher (can fsync every second or every command) |
| Restart speed | Faster | Slower (replays the log) |
| File size | Compact | Larger (grows over time; can be rewritten via `BGREWRITEAOF`) |

**Choice:** For most production systems, use **both** (hybrid mode). If you need maximum durability (e.g., Redis as a primary store), use AOF with `appendfsync everysec`. If you're using Redis purely as a cache where data loss is acceptable, you can disable persistence entirely.

---

**Q7: What Redis data type would you use for a leaderboard and why?**

A **Sorted Set (ZSet)**. Each member has an associated floating-point **score**, and members are always stored in sorted order by score. This makes it trivial to:

- Add/update a user's score: `ZADD leaderboard 9500 "user:42"`
- Get the top N players: `ZREVRANGE leaderboard 0 9 WITHSCORES`
- Get a user's rank: `ZREVRANK leaderboard "user:42"`

All these operations are O(log N), making sorted sets extremely efficient for leaderboard use cases.

---

**Q8: What is Redis Cluster and how does sharding work?**

Redis Cluster horizontally scales Redis across multiple nodes by sharding data. It divides the keyspace into **16,384 hash slots**. Each key is assigned to a slot using `CRC16(key) % 16384`, and each node in the cluster is responsible for a range of slots.

**Key characteristics:**
- Supports automatic failover (each primary has replica nodes).
- Clients are redirected to the correct node via `MOVED` responses.
- Multi-key operations (e.g., `MGET`) are only supported if all keys map to the same slot (use **hash tags** like `{user}.name` and `{user}.age` to force co-location).

---

**Q9: How would you implement distributed locking with Redis?**

Using the **SET NX EX** pattern (or the **Redlock** algorithm for multi-node setups):

```
SET lock:resource_id unique_token NX PX 5000
```

- `NX` — only set if the key does not exist (atomic acquisition).
- `PX 5000` — auto-expire after 5000ms to prevent deadlocks if the lock holder crashes.

To release, use a **Lua script** to atomically check and delete:
```lua
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
```

The unique token ensures a client only releases its own lock. For high-availability setups, use **Redlock** (acquire lock on a majority of N independent Redis nodes).

---

**Q10: What is the difference between Redis `EXPIRE` and `EXPIREAT`?**

- `EXPIRE key seconds` — sets TTL relative to **now** (e.g., expire in 300 seconds).
- `EXPIREAT key unix-timestamp` — sets TTL to an **absolute Unix timestamp** (e.g., expire at midnight).
- `PEXPIRE` and `PEXPIREAT` are millisecond-precision equivalents.

Use `EXPIREAT` when you want cache entries to expire at a specific wall-clock time (e.g., end of business day).

---

**Q11: What is the Redis eviction policy `allkeys-lru` vs `volatile-lru`?**

- **`volatile-lru`** — apply LRU eviction only to keys that have a TTL set. Keys without a TTL are never evicted.
- **`allkeys-lru`** — apply LRU eviction to *all* keys, regardless of whether they have a TTL.

If Redis is used purely as a cache (no persistent data), `allkeys-lru` is usually the right choice. If Redis holds a mix of ephemeral cache entries (with TTL) and persistent data (without TTL), use `volatile-lru` to protect the persistent keys.

---

**Q12: How does Redis handle transactions? Does it support rollbacks?**

Redis transactions use `MULTI` / `EXEC`:
1. `MULTI` starts a transaction.
2. Commands are queued (not executed).
3. `EXEC` executes all queued commands atomically.

**No rollbacks.** If a command fails at runtime (e.g., wrong type), Redis executes the remaining commands. Syntax errors before `EXEC` (e.g., unknown command) will abort the whole transaction. For optimistic concurrency, use `WATCH` on keys — if any watched key is modified before `EXEC`, the transaction aborts and returns `nil`.

---

**Q13: How would you cache database query results in a web application? Walk me through the pattern.**

Using **cache-aside**:

1. Receive request for `/api/users/42`.
2. Generate the cache key: `user:42`.
3. `GET user:42` from Redis.
4. **Cache hit** → deserialize and return the result.
5. **Cache miss** → query the database for user 42.
6. Serialize the result and `SET user:42 <data> EX 300` (cache for 5 minutes).
7. Return the result.

On writes (e.g., updating user 42):
- Update the database.
- `DEL user:42` to invalidate the cache (or update it via write-through).

---

**Q14: What is the difference between Redis Pub/Sub and Redis Streams?**

| | Pub/Sub | Streams |
|---|---|---|
| Message persistence | None — fire and forget | Yes — messages persisted in the log |
| Delivery to offline consumers | Not delivered | Consumers can read from any offset |
| Consumer groups | Not supported | Supported (like Kafka consumer groups) |
| Use case | Real-time notifications, ephemeral events | Durable event logs, task queues |

Use **Pub/Sub** for lightweight real-time fanout (e.g., chat notifications). Use **Streams** when you need message durability, replay, or consumer group semantics.

---

**Q15: How would you handle a "hot key" problem in Redis?**

A hot key is a single Redis key receiving so many requests that it saturates a single node (especially in a Redis Cluster).

Mitigation strategies:
- **Local in-process caching**: Cache the hot key's value in the application's memory for a short duration, reducing Redis requests.
- **Key replication**: Store the value under multiple keys (e.g., `hot_key:0` through `hot_key:9`) and randomly select one per request to distribute load.
- **Read replicas**: Route reads for the hot key to replica nodes.
- **Reduce TTL frequency**: If the key expires frequently, use background refresh to avoid stampedes.

---

*End of Guide*