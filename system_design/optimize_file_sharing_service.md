# Optimizing a File Sharing Service Running Out of One Box

## The Starting Point

A single-box file sharing service is simple to operate but hits limits fast: disk fills up, bandwidth saturates, the CPU chokes on concurrent uploads/downloads, and any deploy or crash takes the whole service down. The goal is to squeeze maximum performance and reliability out of that one machine first — then know exactly when and where to scale out.

---

## 1. Storage Layer

### Use a fast local filesystem layout

**Design choice:** Avoid storing all files in a flat directory. Instead, shard files into subdirectories using the first N characters of the file's hash.

```
/data/files/
  a3/
    a3f8c1d2e4...   ← actual file content
  7b/
    7b209a...
```

**Why:** Most filesystems (ext4, XFS) degrade badly when a single directory contains millions of entries. Sharding keeps directory lookups O(1) and avoids inode exhaustion.

### Content-addressable storage (CAS)

**Design choice:** Name every file by the SHA-256 hash of its content, not by a user-supplied name.

**Why:** This gives you deduplication for free — if two users upload the same file, you store it once. It also makes integrity verification trivial: re-hash and compare. Store a metadata DB (see §3) that maps user-facing IDs/names → content hashes.

### Separate hot and cold storage paths

**Design choice:** Keep a fixed-size LRU cache of recently/frequently accessed files on a fast NVMe partition; less-accessed files live on a larger, slower HDD or compressed volume.

**Why:** On a single box you can't scale out, but you can tier storage. A file downloaded 1,000 times a day should not compete for I/O with one downloaded once a month.

---

## 2. Network & I/O

### Offload static file serving to the OS: use `sendfile(2)`

**Design choice:** Use a web server (Nginx, Caddy) as the front door. Never read file bytes into application memory and write them to a socket manually.

**Why:** `sendfile()` is a zero-copy kernel syscall — it transfers bytes directly from the page cache to the NIC, bypassing userspace entirely. This cuts CPU usage on large downloads by 50–80% and keeps application threads free for metadata work.

### Streaming uploads with chunked transfer

**Design choice:** Accept uploads as chunked multipart streams; hash and write chunks as they arrive rather than buffering the whole file.

**Why:** Buffering a 2 GB upload in RAM before writing it will OOM a single-box server under concurrent load. Streaming keeps memory flat regardless of file size.

### Rate limiting and connection caps

**Design choice:** Set per-IP connection limits and per-connection bandwidth caps at the Nginx layer.

**Why:** Without this, one aggressive client can saturate the uplink and starve everyone else. On a single box there is no other line of defense.

### Enable HTTP/2 (or HTTP/3)

**Design choice:** Terminate TLS at Nginx and enable HTTP/2.

**Why:** Multiplexing reduces the overhead of many small requests (metadata fetches, thumbnail loads) sharing the same connection, and header compression reduces per-request overhead. HTTP/3 (QUIC) further helps on lossy mobile connections.

---

## 3. Metadata & Database

### Separate metadata from file content

**Design choice:** Store file metadata (owner, name, size, content hash, upload time, access count, expiry) in a local SQLite or PostgreSQL database — never in the filesystem.

**Why:** Filesystem metadata (mtime, name) is coarse and hard to query. A real database lets you answer "show me all files uploaded by user X in the last 7 days larger than 100 MB" efficiently, and gives you ACID guarantees on operations like rename and delete.

### Index aggressively

Key indexes:
- `(owner_id, created_at)` — user file listings
- `content_hash` — deduplication lookups
- `expires_at` — efficient expiry sweeps

**Why:** Without these, listing a user's files becomes a full table scan once the table grows past a few hundred thousand rows.

### Use WAL mode (SQLite) or connection pooling (Postgres)

**Design choice:** Enable Write-Ahead Logging in SQLite, or use PgBouncer in front of Postgres.

**Why:** WAL allows concurrent readers without blocking a writer. On a single box this is critical — reads (downloads) vastly outnumber writes (uploads) and must not be serialized behind them.

---

## 4. Caching

### Page cache is your first cache — don't fight it

**Design choice:** Let the OS page cache do its job. Do not use `O_DIRECT` unless you have a very specific reason.

**Why:** Frequently accessed files will naturally be cached in RAM. `sendfile()` + page cache is often faster than any userspace cache you could build.

### Add an application-level cache for metadata

**Design choice:** Use an in-process cache (e.g., Redis running locally, or a simple LRU map in the app) for hot metadata: does this file exist? What is its content hash? Who owns it?

**Why:** Every download requires at least one metadata lookup (auth + file existence). At high concurrency, these round-trips to the DB add up. A cache with a short TTL (a few seconds) eliminates the vast majority of them.

### Cache-Control headers

**Design choice:** Serve files with `Cache-Control: public, max-age=31536000, immutable` when the URL embeds the content hash.

**Why:** Immutable, content-addressed URLs can be cached forever by browsers and CDN edges. This reduces repeat-download load to near zero for popular files, even before you add a CDN.

---

## 5. Concurrency & Process Model

### Use an async/event-driven server

**Design choice:** Run the application on an async framework (Node.js, Python asyncio + uvicorn, Go's net/http, or Nginx + FastCGI) rather than a threaded model with one thread per connection.

**Why:** File serving is I/O-bound, not CPU-bound. A thread-per-connection model wastes ~8 MB of stack RAM per idle connection and thrashes the scheduler. An event loop handles thousands of concurrent connections with a handful of OS threads.

### Worker count = CPU core count (for CPU-bound work)

**Design choice:** Spawn N worker processes where N = number of CPU cores for any CPU-bound processing (hashing, thumbnail generation, virus scanning).

**Why:** This saturates CPU without over-subscribing and causing excessive context switching.

### Background job queue for heavy work

**Design choice:** Move post-upload processing (virus scan, thumbnail extraction, metadata extraction) to an in-process or local job queue (e.g., a simple Redis list or a SQLite-backed queue).

**Why:** The upload HTTP response should return in milliseconds. If you run a 10-second virus scan synchronously, the upload connection times out and the user retries — doubling your load.

---

## 6. Reliability on a Single Box

### Graceful degradation under load

**Design choice:** Implement request shedding — return `503 Service Unavailable` with a `Retry-After` header when the queue depth exceeds a threshold.

**Why:** It is far better to explicitly reject excess load than to accept it and have the entire server thrash into unresponsiveness. Clients can retry; a hung server cannot serve anyone.

### Atomic writes with temp-file-then-rename

**Design choice:** Write uploads to a temp file in the same filesystem, then `rename()` it into the final content-addressed path.

**Why:** `rename()` is atomic on POSIX filesystems. A crash mid-upload leaves a temp file (easily cleaned up) and never produces a partial file at the canonical path.

### Health checks and auto-restart

**Design choice:** Run the application under systemd (or a process supervisor like s6) with automatic restart on failure.

**Why:** On a single box there is no orchestrator to reschedule you. A supervisor that restarts within 1–2 seconds is your only failover mechanism.

### Regular backups

**Design choice:** Schedule incremental backups of both the metadata DB and the file store to a separate destination (object storage, another machine, tape).

**Why:** A single box is a single point of failure. Backups are the only disaster recovery available at this tier.

---

## 7. Observability

### Instrument before you optimize

**Design choice:** Add structured logging (request ID, file hash, duration, bytes transferred, status code) and expose a `/metrics` endpoint (Prometheus format).

**Why:** You cannot optimize what you cannot measure. Before declaring a bottleneck, verify it with data. The most common mistake is optimizing the wrong layer.

Key metrics to track:
- Upload/download throughput (MB/s)
- P50/P95/P99 latency per operation
- Active connection count
- Disk I/O wait %
- Page cache hit rate
- DB query latency

---

## 8. When to Graduate Beyond One Box

The single-box optimizations above will take you surprisingly far. The natural graduation points are:

| Signal | Next step |
|---|---|
| Disk full, dedup exhausted | Add object storage (S3-compatible) as the backing store; keep the app layer on the box |
| Network bandwidth saturated | Put a CDN in front; files become edge-cached |
| CPU saturated on hashing/scanning | Move processing workers to a second machine |
| DB becomes the bottleneck | Migrate to a dedicated DB host |
| Need zero-downtime deploys | Add a second app node behind a load balancer |

Each of these steps is a clean interface cut — the design choices above (CAS, metadata/content separation, async serving, background queues) make each graduation possible without a rewrite.

---

## Summary of Key Design Choices

| Choice | Reason |
|---|---|
| Content-addressable storage | Free deduplication, trivial integrity verification |
| Hash-sharded directories | Avoid filesystem directory limits at scale |
| `sendfile()` via Nginx | Zero-copy I/O; keeps app threads free |
| Streaming uploads | Constant memory regardless of file size |
| Metadata in a real DB | Queryable, ACID-safe, indexed |
| Async server model | Handles high concurrency without thread explosion |
| Temp-file-then-rename | Atomic, crash-safe writes |
| Cache-Control: immutable | Eliminates repeat-download load for free |
| Request shedding at overload | Fail fast gracefully rather than thrash |
| Structured metrics/logging | Measure before optimizing |
