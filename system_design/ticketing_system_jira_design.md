# System Design: Ticketing System (JIRA-like)

---

## 1. Requirements Clarification

Before diving in, it's important to define scope. This drives every architecture decision that follows.

### Functional Requirements
- Users can **create, read, update, and delete** tickets (issues)
- Tickets have: title, description, type (bug/story/task), status, priority, assignee, reporter, labels, comments, attachments, due date
- **Workflows**: tickets move through configurable status transitions (e.g., `To Do → In Progress → In Review → Done`)
- **Projects**: tickets belong to projects; projects have members with roles (admin, developer, viewer)
- **Boards**: Kanban and Scrum sprint boards to visualize tickets
- **Search & filtering**: full-text search, filter by assignee, label, status, date range
- **Notifications**: email/in-app alerts on ticket updates, mentions, assignments
- **Comments & mentions**: threaded comments with `@user` mentions
- **Attachments**: upload files/images to tickets
- **Activity log**: audit trail of all changes per ticket

### Non-Functional Requirements
- **Scale**: 10M+ users, 500M+ tickets, ~50K concurrent users
- **Availability**: 99.9% uptime (≤8.7 hrs/year downtime)
- **Latency**: ticket reads <100ms (p99), search <500ms
- **Consistency**: eventual consistency acceptable for notifications; strong consistency required for ticket state transitions
- **Durability**: no data loss for tickets or comments

---

## 2. Capacity Estimation

> **Why estimate early?** These numbers steer storage engine selection, sharding strategy, and caching policy.

| Metric | Estimate |
|---|---|
| Total users | 10M |
| Daily active users (DAU) | 1M |
| Tickets created/day | 500K |
| Comments/day | 2M |
| Reads/writes ratio | ~10:1 |
| Avg ticket size (metadata) | ~2 KB |
| Total ticket storage (5 yr) | ~1.8 TB |
| Attachments storage (5 yr) | ~50 TB |
| Peak QPS (reads) | ~5,800 |
| Peak QPS (writes) | ~580 |

---

## 3. High-Level Architecture

```
                         ┌───────────────┐
  Browser / Mobile  ──►  │   CDN/Edge    │  (static assets, API caching)
                         └──────┬────────┘
                                │
                         ┌──────▼────────┐
                         │  API Gateway  │  (auth, rate limiting, routing)
                         └──────┬────────┘
                                │
              ┌─────────────────┼──────────────────┐
              │                 │                  │
       ┌──────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐
       │  Ticket Svc │  │  Search Svc  │  │  Notif. Svc  │
       └──────┬──────┘  └───────┬──────┘  └───────┬──────┘
              │                 │                  │
       ┌──────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐
       │  Primary DB │  │Elasticsearch │  │  Message Que  │
       │ (Postgres)  │  │              │  │  (Kafka)      │
       └──────┬──────┘  └──────────────┘  └───────┬──────┘
              │                                    │
       ┌──────▼──────┐                    ┌────────▼─────┐
       │  Read Replicas│                  │  Email / Push │
       │  + Redis Cache│                  │  Workers      │
       └─────────────┘                    └──────────────┘
```

---

## 4. Core Services

### 4.1 API Gateway

**Design choice: single entry point**

The API Gateway handles:
- **Authentication** via JWT tokens (stateless, horizontally scalable)
- **Rate limiting** per user/IP to prevent abuse
- **Routing** to downstream microservices
- **TLS termination**

> **Why JWT over sessions?** Sessions require shared state (sticky sessions or a session store). JWTs are self-contained, allowing any API Gateway node to validate a request without a network hop. The trade-off is token revocation complexity — we mitigate this with short-lived access tokens (15 min) + refresh tokens.

---

### 4.2 Ticket Service

The core of the system. Responsible for CRUD on tickets, status transitions, and comments.

**Design choice: PostgreSQL as primary database**

| Considered | Chosen | Reason |
|---|---|---|
| MongoDB | PostgreSQL | Tickets have relational data (projects, users, sprints). ACID transactions are critical for status transitions and preventing race conditions. |
| MySQL | PostgreSQL | Better JSON support for flexible metadata; JSONB column for custom fields. |
| Cassandra | PostgreSQL | Write-heavy NoSQL is overkill here; our write QPS (~580) is well within PostgreSQL's range. |

**Schema (simplified):**

```sql
-- Projects
CREATE TABLE projects (
  id          UUID PRIMARY KEY,
  name        TEXT NOT NULL,
  key         TEXT UNIQUE NOT NULL,   -- e.g. "PROJ"
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- Tickets
CREATE TABLE tickets (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id   UUID REFERENCES projects(id),
  key          TEXT UNIQUE NOT NULL,  -- e.g. "PROJ-123"
  title        TEXT NOT NULL,
  description  TEXT,
  type         TEXT CHECK (type IN ('bug','story','task','epic')),
  status       TEXT NOT NULL DEFAULT 'todo',
  priority     TEXT CHECK (priority IN ('low','medium','high','critical')),
  assignee_id  UUID REFERENCES users(id),
  reporter_id  UUID REFERENCES users(id) NOT NULL,
  sprint_id    UUID REFERENCES sprints(id),
  custom_fields JSONB,               -- flexible extension without schema migration
  created_at   TIMESTAMPTZ DEFAULT now(),
  updated_at   TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX idx_tickets_project_status ON tickets(project_id, status);
CREATE INDEX idx_tickets_assignee       ON tickets(assignee_id);
CREATE INDEX idx_tickets_updated_at     ON tickets(updated_at DESC);

-- Comments
CREATE TABLE comments (
  id         UUID PRIMARY KEY,
  ticket_id  UUID REFERENCES tickets(id) ON DELETE CASCADE,
  author_id  UUID REFERENCES users(id),
  body       TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

> **Why `custom_fields JSONB`?** JIRA's killer feature is extensibility. Teams add custom fields (story points, severity scores, etc.). Storing these in JSONB avoids costly `ALTER TABLE` migrations for each new field type, while PostgreSQL still allows indexing into JSONB for querying.

**Status transitions — optimistic locking:**

```sql
UPDATE tickets
SET status = 'in_progress', updated_at = now()
WHERE id = $1
  AND status = 'todo'          -- guard: only valid if current state is expected
  AND updated_at = $2;         -- optimistic lock: reject if someone else updated first
```

> **Why optimistic locking over pessimistic (SELECT FOR UPDATE)?**  
> Pessimistic locks hold DB connections open and cause contention at scale. Most ticket updates don't conflict — developers rarely update the same ticket simultaneously. Optimistic locking only pays a cost on the rare collision.

---

### 4.3 Caching Layer (Redis)

**What to cache:**

| Cache Key | TTL | Reason |
|---|---|---|
| `ticket:{id}` | 5 min | Single ticket fetches are frequent; data is read ~10x more than written |
| `project:{id}:tickets` | 1 min | Board views load many tickets at once |
| `user:{id}:permissions` | 10 min | Permission checks happen on every request |
| `search:{hash}` | 30 sec | Repeated searches from board filters |

**Cache invalidation strategy: write-through**

On every ticket write, the service immediately updates (or deletes) the cache entry. This keeps cache and DB in sync without needing complex invalidation logic.

> **Why not cache-aside?** Cache-aside (lazy loading) leads to thundering herd on cold starts — many requests hit the DB simultaneously after a deploy. Write-through pre-warms the cache and reduces this risk.

**Cache miss handling:**

On a miss, the service queries PostgreSQL read replicas (not the primary) to distribute load.

---

### 4.4 Search Service (Elasticsearch)

Ticket search needs to handle:
- Full-text search across title, description, comments
- Faceted filters (status, assignee, label, date range)
- Ranked results

**Design choice: Elasticsearch, separate from the primary DB**

> PostgreSQL's `tsvector` full-text search can handle moderate search loads, but at 500M tickets with complex faceting and relevance scoring, Elasticsearch is the right choice. It's purpose-built for distributed search and supports near-real-time indexing.

**Sync strategy: Kafka-based CDC (Change Data Capture)**

```
PostgreSQL  →  Debezium (CDC)  →  Kafka topic  →  ES Indexer Worker  →  Elasticsearch
```

Debezium reads PostgreSQL's WAL (write-ahead log) and publishes change events to Kafka. An indexer worker consumes these and upserts into Elasticsearch.

> **Why CDC over dual-writes?** Dual-writes (writing to DB + ES in the same request) risk partial failures — the DB write succeeds but the ES write fails, causing search to go stale silently. CDC is reliable because it reads from the durable WAL — if the ES write fails, the Kafka offset isn't committed and it will retry.

**Elasticsearch index mapping (simplified):**

```json
{
  "mappings": {
    "properties": {
      "id":          { "type": "keyword" },
      "project_id":  { "type": "keyword" },
      "title":       { "type": "text", "analyzer": "english" },
      "description": { "type": "text", "analyzer": "english" },
      "status":      { "type": "keyword" },
      "assignee_id": { "type": "keyword" },
      "priority":    { "type": "keyword" },
      "created_at":  { "type": "date" }
    }
  }
}
```

---

### 4.5 Notification Service

Handles: email alerts, in-app notifications, webhook delivery.

**Design choice: async, event-driven via Kafka**

Every ticket update publishes an event:

```json
{
  "event": "ticket.updated",
  "ticket_id": "abc-123",
  "project_id": "proj-456",
  "changed_fields": ["status", "assignee"],
  "actor_id": "user-789",
  "timestamp": "2026-05-18T10:00:00Z"
}
```

Notification workers consume these events and fan out to subscribers (users watching the ticket or project).

> **Why Kafka over a simple task queue (like Celery/Redis)?** Kafka retains messages by offset, allowing workers to replay events if they crash. It also supports multiple consumer groups — the email worker, the in-app notification worker, and the webhook worker all consume the same event stream independently.

**Fan-out strategy:**

For projects with many watchers, generating one notification per user synchronously would be slow. Instead:
1. Event hits Kafka
2. Worker resolves the subscriber list
3. Per-user notification records are bulk-inserted into a `notifications` table
4. In-app notifications are served from this table via polling or WebSocket push

---

### 4.6 Attachment Service

**Design choice: object storage (S3-compatible)**

File uploads go directly to object storage (AWS S3, GCS, or MinIO for on-prem). The Ticket Service only stores the metadata (filename, size, S3 key, uploaded_by).

**Upload flow:**

```
Client  →  Ticket Svc: "I want to upload logo.png"
Ticket Svc  →  Client: pre-signed S3 URL (valid 10 min)
Client  →  S3: PUT logo.png (direct, bypasses backend)
Client  →  Ticket Svc: "Upload complete, here's the S3 key"
Ticket Svc  →  DB: INSERT INTO attachments ...
```

> **Why pre-signed URLs?** Direct browser-to-S3 uploads avoid routing large files through the application server. This reduces bandwidth costs, API server memory pressure, and upload latency.

---

## 5. Database Scaling

### Read Replicas

At 50K concurrent users, the primary DB would be overwhelmed by reads. PostgreSQL streaming replication provides read replicas:

- **Primary**: handles all writes
- **Replicas (×3)**: handle reads; lag is typically <100ms (acceptable for ticket views)

The application layer uses a connection pool (PgBouncer) and routes `SELECT` queries to replicas.

### Sharding (future scale)

At current estimates, PostgreSQL with read replicas handles the load. If the ticket count grows to billions, **horizontal sharding by `project_id`** is the natural partition key — all tickets in a project are accessed together, so keeping them co-located avoids cross-shard joins.

> **Why not shard by `ticket_id`?** Ticket views are always project-scoped. Sharding by ticket_id would scatter a project's tickets across shards, requiring expensive scatter-gather queries for every board load.

---

## 6. Real-Time Board Updates (WebSockets)

Teams watching a Kanban board expect to see ticket moves in real time.

**Design choice: WebSocket server with pub/sub via Redis**

```
Client A moves ticket  →  Ticket Svc writes to DB
                       →  Publishes event to Redis channel "project:{id}:updates"
WebSocket Server       →  Subscribed to Redis channel, pushes delta to all clients in project
Client B's browser     →  Receives update, re-renders card
```

> **Why Redis pub/sub over polling?** Polling at 1-second intervals for 50K users generates ~50K req/sec of read load for no new data most of the time. Redis pub/sub pushes updates only when they exist. The trade-off is statefulness — WebSocket connections must be managed (heartbeats, reconnection logic).

---

## 7. API Design

RESTful, resource-oriented:

```
POST   /api/v1/projects                          → create project
GET    /api/v1/projects/{projectKey}/tickets      → list/filter tickets
POST   /api/v1/projects/{projectKey}/tickets      → create ticket
GET    /api/v1/tickets/{ticketKey}                → get ticket detail
PATCH  /api/v1/tickets/{ticketKey}               → update ticket (status, assignee, etc.)
DELETE /api/v1/tickets/{ticketKey}               → delete ticket

POST   /api/v1/tickets/{ticketKey}/comments       → add comment
GET    /api/v1/tickets/{ticketKey}/activity       → audit log

GET    /api/v1/search?q=login+bug&project=PROJ    → full-text search
```

> **Why PATCH over PUT for updates?** Ticket updates are partial — a user drags a card to change status without touching title or description. PATCH semantics let the client send only what changed, reducing payload size and avoiding accidental overwrites (e.g., two users editing different fields simultaneously).

---

## 8. Security

| Concern | Approach |
|---|---|
| Authentication | JWT access tokens (15 min) + refresh tokens (7 days, stored in HttpOnly cookies) |
| Authorization | Role-Based Access Control (RBAC) per project: Admin / Member / Viewer |
| Input sanitization | Sanitize description/comments server-side to prevent stored XSS |
| Attachment scanning | Virus scan uploads via ClamAV before making them accessible |
| Rate limiting | 1000 req/min per authenticated user at API Gateway |
| Audit log | Append-only `ticket_events` table; no deletes permitted |

---

## 9. Key Design Trade-offs Summary

| Decision | Choice | Trade-off |
|---|---|---|
| Database | PostgreSQL | Strong consistency & ACID vs. horizontal write scalability of NoSQL |
| Search | Elasticsearch via CDC | Near-real-time search vs. slight eventual consistency (seconds of lag) |
| Caching | Redis write-through | Lower read latency vs. added complexity in write path |
| Event streaming | Kafka | Durable, replayable events vs. operational overhead of running Kafka |
| File uploads | S3 pre-signed URLs | Scalable direct uploads vs. client-side complexity |
| Status transitions | Optimistic locking | Higher throughput vs. occasional retry on conflict |
| Real-time updates | WebSockets + Redis pub/sub | Low-latency push vs. connection management complexity |

---

## 10. What I Would NOT Build on Day 1

To avoid over-engineering:

- **Microservice-per-entity**: Start with a monolith or 3–4 services. Splitting into 20 microservices early adds deployment/networking complexity before you understand the seams.
- **Custom workflow engine**: A simple state machine in application code handles 90% of workflows. A full BPM engine is premature.
- **Multi-region active-active**: Single-region with read replicas is sufficient initially. Multi-region adds distributed transactions complexity (2PC or saga patterns) that aren't justified until you have global traffic.
- **ML-based ticket routing**: Auto-assignment by ML is a feature, not infrastructure. Build manual assignment first.
