# Payments Reconciliation System Design

> **Design rationale is called out in each section.** Every significant architectural decision includes an explanation of *why* it was made — not just *what* was chosen.

---

## 1. Problem Statement

A payments reconciliation system must reliably match financial records across three heterogeneous data sources:

- **Transaction histories** — internal ledger records from your application or ERP
- **Payment gateway data** — records from processors like Stripe, Adyen, or Braintree
- **Bank statements** — official settlement records from the receiving bank

Discrepancies between these sources — caused by timing lags, fees, chargebacks, currency conversion, or data errors — must be detected, classified, and resolved with a full audit trail.

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        DATA INGESTION                        │
│  Transaction History │ Payment Gateway API │ Bank Statements │
└───────────────┬──────────────────┬──────────────────┬────────┘
                │                  │                  │
                ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    NORMALIZATION LAYER                        │
│         Canonical Transaction Format + Deduplication         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    MATCHING ENGINE                            │
│   Exact Match → Fuzzy Match → Rule-Based → Manual Queue      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               DISCREPANCY CLASSIFICATION                      │
│   Timing | Fee | FX | Missing | Duplicate | Data Error       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│            RESOLUTION WORKFLOW & AUDIT TRAIL                  │
│         Auto-resolve | Escalate | Write-back to GL           │
└─────────────────────────────────────────────────────────────┘
```

**Design choice — layered pipeline over a monolithic processor:** Each stage is independently deployable and testable. Matching logic can be updated without touching ingestion, and new data sources can be added without rewriting the engine.

---

## 3. Data Ingestion

### 3.1 Source Adapters

Each data source gets its own adapter implementing a common interface:

```python
class SourceAdapter(ABC):
    def fetch(self, date_range: DateRange) -> Iterator[RawTransaction]:
        ...
    def get_schema_version(self) -> str:
        ...
```

| Source              | Ingestion Method                         | Cadence            |
|---------------------|------------------------------------------|--------------------|
| Internal ledger     | Direct DB read / CDC (Change Data Capture) | Near-real-time   |
| Payment gateway     | REST API (paginated) + webhooks          | Every 15 min       |
| Bank statements     | SFTP file pickup (MT940, BAI2, CSV)      | Daily or on-demand |

**Design choice — adapter pattern per source:** Payment gateways change their APIs frequently. Isolating each integration behind an adapter means a Stripe API version change only requires updating one class, not the whole pipeline.

**Design choice — event-driven ingestion for gateways (webhooks):** Polling alone creates lag. Webhooks give near-instant notification of settlement, refunds, and disputes, reducing the reconciliation window.

### 3.2 Raw Storage

All ingested data is written to an **immutable raw store** before any transformation:

```
s3://recon-raw/
  gateway/stripe/2024-11-01/batch_001.jsonl
  bank/hsbc/2024-11-01/statement.mt940
  ledger/2024-11-01/snapshot.parquet
```

**Design choice — store raw data before transforming:** This is the single most important data integrity decision. If the normalization logic has a bug, you can re-process from raw without re-fetching from sources. It also provides an audit trail back to the original source document.

---

## 4. Normalization Layer

### 4.1 Canonical Transaction Model

Every ingested record is mapped to a single canonical format:

```json
{
  "canonical_id":       "recon-txn-abc123",
  "source":             "gateway:stripe",
  "source_id":          "ch_3OxK2...",
  "amount_minor":       10050,
  "currency":           "USD",
  "value_date":         "2024-11-01",
  "settlement_date":    "2024-11-03",
  "type":               "CHARGE",
  "status":             "SETTLED",
  "reference":          "ORDER-98765",
  "metadata":           { "customer_id": "cust_abc", "fee_minor": 59 }
}
```

**Design choice — amounts stored as minor units (integers):** Floating-point arithmetic is unreliable for financial calculations. Storing `10050` cents instead of `100.50` dollars eliminates rounding errors during comparison and aggregation. This is standard practice (e.g., Stripe's API does the same).

**Design choice — separate `value_date` and `settlement_date`:** Many reconciliation failures stem from comparing records at different temporal positions. A charge occurs on Nov 1 but settles on Nov 3. Keeping both dates makes timing discrepancies detectable rather than hidden.

### 4.2 Deduplication

Before matching, duplicates are eliminated using a content-addressed hash:

```python
dedup_key = sha256(source + source_id + amount_minor + currency + value_date)
```

**Design choice — deduplication before matching:** Webhook retries, manual re-imports, and API re-fetches can insert the same transaction multiple times. Deduplicating early prevents false positives in the matching stage where a transaction appears "matched twice."

---

## 5. Matching Engine

Matching runs in priority order — cheaper exact matches first, expensive fuzzy matches only for survivors.

### 5.1 Match Tiers

**Tier 1 — Exact Match**

```python
match_key = (reference, amount_minor, currency, value_date)
```

Matches records across all three sources by the same `reference` (order ID), amount, currency, and date. This resolves ~85–90% of transactions in a healthy system.

**Tier 2 — Fuzzy / Rule-Based Match**

Applied when exact match fails. Rules include:

| Rule | When to apply |
|------|---------------|
| Amount within gateway fee range | Gateway deducts processing fee before settling |
| Date shift ±2 business days | Bank settlement lag |
| Currency-converted amount within FX tolerance | Cross-currency payments |
| Reference prefix match | Some banks truncate reference fields |

**Tier 3 — Manual Review Queue**

Unmatched records after all automated tiers are surfaced in a workflow UI with suggested candidates ranked by similarity score.

**Design choice — tiered matching instead of a single algorithm:** A single fuzzy algorithm over everything would produce too many false positives. Starting with exact matching and only escalating survivors keeps the false-positive rate low and the manual queue manageable. Operators can tune thresholds per tier independently.

### 5.2 Matching Algorithm (Fuzzy Tier)

```python
def similarity_score(a: CanonicalTx, b: CanonicalTx) -> float:
    score = 0.0
    score += 0.4 * amount_score(a, b)      # Weighted most heavily
    score += 0.3 * date_proximity_score(a, b)
    score += 0.2 * reference_similarity(a, b)
    score += 0.1 * metadata_score(a, b)
    return score  # 0.0 – 1.0; threshold ≥ 0.85 for auto-match
```

**Design choice — weighted scoring over hard rules:** Hard rules like "amount must match exactly" break when gateway fees vary. Weighted scoring allows partial credit and surfaces the best candidate even when no single field matches perfectly.

---

## 6. Discrepancy Classification

When a match is found but values differ, or when a record is unmatched, the system classifies the discrepancy:

| Class | Description | Typical Resolution |
|-------|-------------|-------------------|
| `TIMING_LAP` | Settlement date differs by 1–5 days | Auto-resolve on next run |
| `FEE_DEDUCTION` | Amount differs by known gateway fee | Auto-resolve with fee posting |
| `FX_VARIANCE` | Amount differs within FX tolerance band | Auto-resolve with FX entry |
| `MISSING_BANK` | Gateway settled but no bank record | Escalate to treasury |
| `MISSING_GATEWAY` | Internal charge but no gateway record | Investigate: failed charge? |
| `DUPLICATE` | Same transaction appears twice in one source | Suppress duplicate, alert |
| `DATA_ERROR` | Reference field corrupted or missing | Route to data quality team |
| `UNKNOWN` | None of the above | Manual review |

**Design choice — explicit classification taxonomy:** Grouping discrepancies into named classes allows automated resolution for known patterns (fee deductions, timing laps) and targeted escalation for structural problems (missing bank records). Without classification, everything lands in a generic "exceptions" bucket that overwhelms operations teams.

---

## 7. Resolution Workflow

### 7.1 Automated Resolution

Auto-resolvable discrepancy types are handled without human input:

```python
class FeeDeductionResolver:
    def resolve(self, discrepancy: Discrepancy) -> Resolution:
        fee_entry = JournalEntry(
            debit_account="gateway_fees_expense",
            credit_account="accounts_receivable",
            amount=discrepancy.delta_minor,
            reference=discrepancy.canonical_id,
        )
        return Resolution(status="AUTO_RESOLVED", entries=[fee_entry])
```

**Design choice — generate journal entries, not just mark-as-resolved:** Marking a record "resolved" without posting a correcting entry leaves the general ledger out of balance. Every resolution must produce a traceable accounting entry.

### 7.2 Manual Review UI

Unresolved discrepancies surface in a case-management interface showing:

- Side-by-side source records
- Suggested matching candidates with similarity scores
- History of previous similar discrepancies and how they were resolved
- One-click actions: Approve match, Reject, Escalate, Flag as duplicate

### 7.3 Escalation SLAs

| Priority | Trigger | SLA |
|----------|---------|-----|
| P1 | Missing bank settlement > $10,000 | 4 hours |
| P2 | Unresolved discrepancy > $1,000 | 24 hours |
| P3 | Any unresolved after 3 reconciliation cycles | 72 hours |

---

## 8. Audit Trail & Compliance

Every action — ingestion, normalization, matching decision, resolution — is appended to an immutable event log:

```json
{
  "event_id":    "evt-001",
  "timestamp":   "2024-11-03T14:22:00Z",
  "event_type":  "MATCH_APPLIED",
  "actor":       "system:matching-engine-v2.1",
  "canonical_id": "recon-txn-abc123",
  "payload":     { "tier": 1, "score": 1.0, "matched_to": "recon-txn-xyz789" }
}
```

**Design choice — append-only event log (not mutable state):** Reconciliation is a regulated activity. Auditors need to see exactly what happened, when, and why. Mutable updates would allow records to be altered without trace. An append-only log is tamper-evident and supports point-in-time reconstruction.

**Design choice — include `actor` on every event:** Whether an action was taken by the automated engine or a human operator must be distinguishable for SOX and PCI-DSS audit purposes.

---

## 9. Data Storage Design

| Store | Technology | Rationale |
|-------|-----------|-----------|
| Raw ingest | S3 / object store | Cheap, durable, immutable-by-policy |
| Canonical transactions | PostgreSQL + partitioned by date | ACID guarantees; date partitioning for query performance |
| Matching index | Redis sorted sets | Sub-millisecond lookup for exact-match keys during high-volume batch runs |
| Audit log | Append-only Kafka topic → cold storage | High write throughput; compacted for compliance retention |
| Manual queue | PostgreSQL + row-level locking | Prevents two operators resolving the same case simultaneously |

**Design choice — PostgreSQL for canonical records (not a data warehouse):** Reconciliation requires ACID transactions. If a match is written and then the corresponding journal entry fails to post, you need the ability to roll back atomically. Columnar data warehouses don't provide this.

---

## 10. Observability & Alerting

Key metrics to monitor continuously:

| Metric | Alert threshold |
|--------|----------------|
| Reconciliation rate (% matched) | < 98% for any batch |
| Unmatched amount (sum of unmatched records) | > $5,000 |
| Processing latency (time from ingestion to match result) | > 30 minutes |
| Manual queue depth | > 50 items |
| Auto-resolution error rate | > 1% |

**Design choice — alert on *amount* as well as *count*:** A single unmatched $500,000 wire is far more critical than 1,000 unmatched $1 micropayments. Count-only alerting misses the business risk.

---

## 11. Key Non-Functional Requirements

| Requirement | Design response |
|-------------|----------------|
| **Idempotency** | All pipeline stages are idempotent; re-running a batch produces the same result |
| **Scalability** | Batch matching parallelized by currency/date shard; can process 10M transactions/day |
| **Resilience** | Failed ingestion retried with exponential backoff; partial batch failures don't block others |
| **Security** | Bank files decrypted in-transit only; PII masked in logs; role-based access to manual queue |
| **Auditability** | Full lineage from bank statement line → canonical record → journal entry |

---

## 12. Summary of Major Design Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Amount representation | Integer minor units | Eliminates floating-point rounding errors |
| Raw data retention | Immutable object store | Enables reprocessing; provides audit source |
| Matching strategy | Tiered (exact → fuzzy → manual) | Maximizes auto-match rate while controlling false positives |
| Discrepancy handling | Classified taxonomy | Enables automated resolution of known patterns |
| Resolution output | Journal entries, not flags | Keeps the general ledger in balance |
| Audit log | Append-only event stream | Tamper-evident; satisfies regulatory requirements |
| Canonical store | RDBMS with ACID | Enables atomic match + journal entry writes |
| Alerting | Amount + count thresholds | Captures business risk, not just operational noise |
