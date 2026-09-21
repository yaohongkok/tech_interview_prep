# Subscription Billing & Payment System — Architecture Notes

Companion description for [subs_billing_payment_arch.puml](subs_billing_payment_arch.puml).

## Edge / API Layer

- **Customer Portal / Mobile App** — Customer-facing entry point for managing subscriptions, viewing invoices, and updating payment methods.
- **API Gateway** — Single ingress for all client and ops traffic. Handles authentication, rate limiting, and issues/validates idempotency keys so retried requests aren't double-processed downstream.

**Interactions:** Customer and Ops both go through the Gateway (Ops directly, Customers via the Portal). The Gateway fans out to `Subscription Service` (plan changes) and `Invoice Service` (billing history/invoice retrieval).

## Core Billing Domain

- **Subscription Service** — Owns plan lifecycle: trials, upgrades/downgrades, cancellations.
- **Pricing & Rating Engine** — Computes cost from tiers, discounts, proration, and tax rules.
- **Usage Metering Service** — Tracks consumption for usage-based/metered billing.
- **Invoice Service** — Generates invoices and credit notes; the trigger point for actually collecting payment.
- **Dunning & Retry Service** — Manages recovery workflows for failed payments (retry scheduling, grace periods, escalation).

**Interactions:** `Subscription Service` calls `Pricing` and `Metering` to determine charges. Both feed `Invoice Service`, which triggers a charge on `Payment Orchestrator`. Failed payments (via the event bus) route to `Dunning`, which schedules retries back through `Payment Orchestrator`.

## Payment Processing

- **Payment Orchestrator** — Central coordinator for charging: routes to a gateway, applies idempotency keys, and manages retries/failover.
- **Fraud & Risk Engine** — Pre-charge risk scoring to block/flag suspicious transactions.
- **Tokenization / Vault** — PCI-scoped storage of tokenized card data; never exposes raw card numbers to other services.
- **Payment Gateway A / B** — External payment processors; B is a failover if A fails or is unavailable.

**Interactions:** On a charge trigger, `Payment Orchestrator` checks `Fraud`, fetches a token from `Vault`, then attempts `Gateway A` (falling back to `Gateway B`). Both gateways send async webhook results back to the Orchestrator and settlement files to `Reconciliation`. Outcomes are published as `PaymentSucceeded`/`PaymentFailed` events to the Event Bus.

## Reliability & Messaging Backbone

- **Outbox / CDC Relay** — Implements the transactional outbox pattern so DB writes and event publication stay consistent (no dual-write problem).
- **Event Bus / Message Broker** — Kafka-style backbone with exactly-once semantics for propagating billing/payment events.
- **Saga / Workflow Orchestrator** — Coordinates distributed transactions spanning `Subscription Service`, `Payment Orchestrator`, and `Invoice Service` (e.g., a plan upgrade that requires a successful charge before activating).
- **Dead Letter Queue Handler** — Catches unprocessable events for manual inspection/replay instead of blocking the pipeline.

**Interactions:** `Invoice Service` writes to `Outbox`, which relays to the `Bus`. The `Bus` distributes events to `Ledger` (financial records), `Dunning` (failed payments), and `DLQ` (poison messages). `Saga` orchestrates cross-service steps asynchronously via the Bus.

## Ledger & Reconciliation

- **Reconciliation Service** — Matches gateway settlement files against internal ledger entries, flagging discrepancies.
- **Double-Entry Ledger Service** — The immutable source of financial truth; all reporting reads from here, not the operational Billing DB.
- **Revenue Recognition Service** — Derives recognized revenue from ledger entries per accounting rules.

**Interactions:** `Ledger` consumes payment/invoice events from the `Bus` and feeds `Revenue Recognition`. `Reconciliation` independently cross-checks `Ledger` against gateway settlement data.

## Data Stores

- **Idempotency Key Store** (Redis/DynamoDB) — Fast lookup used by `Payment Orchestrator` to detect/prevent duplicate charge attempts.
- **Billing DB** (multi-AZ, primary/replica) — Operational store for `Subscription Service`, `Pricing`, and `Invoice Service`.
- **Ledger DB** (append-only, immutable) — Backing store for the `Ledger Service`; write-once for audit integrity.

## Cross-Cutting Concerns

- **Secrets & Key Management (KMS/HSM)** — Supplies encryption keys to `Vault` for protecting stored payment tokens.
- **Notification Service** — Sends email/SMS/webhook notifications triggered by bus events (e.g., payment failed, invoice ready).
- **Audit & Compliance Logging** — Immutable trail for SOC2/PCI compliance, fed by `Payment Orchestrator` and `Ledger`.
- **Observability Stack** — Metrics, tracing, and alerting across `Subscription Service`, `Payment Orchestrator`, and `Ledger`.

## Key Reliability Patterns

1. **Idempotency everywhere** — Gateway-issued keys plus the `Idempotency Key Store` prevent duplicate charges on retry.
2. **Multi-gateway failover** — `Payment Orchestrator` fails over from Gateway A to Gateway B with circuit breakers and exponential backoff.
3. **Transactional outbox** — Avoids dual-write inconsistency between DB state and published events.
4. **At-least-once + idempotent consumers + DLQ** — The Event Bus guarantees delivery; consumers must dedupe, and unprocessable messages land in the DLQ rather than blocking the pipeline.
5. **Ledger as source of truth** — All financial reporting/revenue recognition reads from the append-only Ledger DB, not the mutable Billing DB.

## End-to-End Flow (Happy Path)

1. Customer requests a plan change via Portal → Gateway → `Subscription Service`.
2. `Subscription Service` consults `Pricing`/`Metering` → `Invoice Service` generates an invoice.
3. `Invoice Service` triggers `Payment Orchestrator`, which checks `Fraud`, pulls a token from `Vault`, and charges via `Gateway A` (or `B` on failure).
4. On success, `Payment Orchestrator` publishes `PaymentSucceeded` to the `Bus`; `Invoice Service` also writes through the `Outbox` to the `Bus`.
5. `Ledger` records the transaction; `Reconciliation` later verifies it against the gateway's settlement file.
6. `Notify` sends a confirmation; `Audit`/`Observability` capture the trail and metrics throughout.

## Failure Path

- A failed charge emits `PaymentFailed` → `Dunning` schedules a retry → back to `Payment Orchestrator`.
- Unprocessable events on the `Bus` land in the `DLQ` for manual handling.
