# Subscription Billing & Payment System — Key Workflows

Companion to [subs_billing_payment_arch.md](subs_billing_payment_arch.md).

Workflows are grouped by **initiator** — external customer, internal employee/ops, or event/system-triggered — and ordered within the list by **occurrence frequency** (most frequent first). In a running subscription business, the recurring billing cycle (invoice generation + charge) dominates volume; everything else is a smaller slice riding on top of it.

## 1. Bill/Invoice Creation — *Event-based (recurring)*

The highest-volume workflow: runs once per billing cycle for every active subscription.

1. A billing-cycle trigger (scheduler/cron, or a metering threshold) fires per subscription.
2. `Subscription Service` consults `Pricing & Rating Engine` and `Usage Metering Service` to compute the charge (tiers, discounts, proration, usage, tax).
3. `Invoice Service` generates the invoice (and credit notes if applicable) and persists it to `Billing DB`.
4. `Invoice Service` writes through the `Outbox / CDC Relay` to the `Event Bus`, and triggers `Payment Orchestrator` to collect payment (→ Workflow 2).

## 2. Payment Processing (Charge) — *Event-based, immediately follows Workflow 1*

Runs at essentially the same frequency as invoice creation — every invoice needs a charge attempt.

1. `Invoice Service` triggers `Payment Orchestrator`.
2. `Payment Orchestrator` checks `Idempotency Key Store` to avoid double-charging on retry.
3. `Payment Orchestrator` checks `Fraud & Risk Engine`, pulls a token from `Tokenization/Vault`, and charges via `Gateway A` (failing over to `Gateway B` on error, with circuit breakers/backoff).
4. Gateway sends an async webhook result back to `Payment Orchestrator`; outcome is published as `PaymentSucceeded`/`PaymentFailed` to the `Event Bus`.
5. `Double-Entry Ledger Service` records the transaction; `Notification Service` sends a confirmation. `Audit & Compliance Logging` / `Observability Stack` capture the trail throughout.

## 3. Usage Metering Ingestion — *Event-based (continuous)*

Highest raw event volume, but feeds Workflow 1 rather than standing alone.

1. Customer/product usage events stream continuously into `Usage Metering Service`.
2. Usage is aggregated and stored, ready to be read by `Pricing & Rating Engine` at the next billing cycle (Workflow 1, step 2).

## 4. Failed Payment → Dunning & Retry — *Event-based, subset of Workflow 2*

Occurs for the fraction of charges that fail — frequent in aggregate, but a minority of Workflow 2 attempts.

1. `PaymentFailed` event lands on the `Event Bus`.
2. `Dunning & Retry Service` schedules a retry per policy (backoff, grace period, escalation).
3. Retry re-enters `Payment Orchestrator`, repeating Workflow 2 steps 2–5.
4. If retries are exhausted, `Dunning & Retry Service` escalates (e.g., suspend subscription, notify customer/ops).

## 5. Customer: Plan Change (Upgrade/Downgrade/Cancel/Trial) — *Customer-initiated*

Less frequent than the billing cycle itself, but the main customer-driven workflow.

1. Customer requests a plan change via `Portal/Mobile App` → `API Gateway` → `Subscription Service`.
2. `Subscription Service` updates plan state and may trigger an immediate proration invoice (re-enters Workflow 1) via `Pricing & Rating Engine` → `Invoice Service`.
3. If the change requires payment before activation (e.g., upgrade), `Saga / Workflow Orchestrator` coordinates: charge must succeed (Workflow 2) before `Subscription Service` activates the new plan.

## 6. Customer: Update Payment Method — *Customer-initiated*

1. Customer submits new card details via `Portal/Mobile App` → `API Gateway`.
2. Card data is tokenized and stored in `Tokenization/Vault` (never exposed raw to other services), protected by `Secrets & Key Management (KMS/HSM)`.
3. `Subscription Service`/`Payment Orchestrator` reference the new token on subsequent charges.

## 7. Customer: View Invoices/Billing History — *Customer-initiated (read-only)*

1. Customer requests billing history via `Portal/Mobile App` → `API Gateway` → `Invoice Service`.
2. `Invoice Service` reads from `Billing DB` and returns invoice/credit-note records.

## 8. Reconciliation — *Event-based (scheduled batch)*

Typically daily, matching a batch of settlement data against the ledger.

1. Gateways deliver settlement files to `Reconciliation Service`.
2. `Reconciliation Service` cross-checks entries against `Double-Entry Ledger Service`, flagging discrepancies.
3. `Revenue Recognition Service` derives recognized revenue from ledger entries per accounting rules.

## 9. Internal/Ops: Manual Adjustments (Refunds, Credit Notes, Overrides) — *Internal-initiated*

Lower frequency, ad hoc — typically support/finance handling exceptions.

1. Ops user acts via `API Gateway` directly (not through the Portal).
2. Actions such as issuing a credit note or manual refund go through `Invoice Service`/`Payment Orchestrator`, producing the same downstream events as Workflows 1–2 (ledger update, notification, audit trail).
3. Discrepancies surfaced by Workflow 8 (Reconciliation) often feed back into this workflow for manual resolution.

## 10. Cross-Cutting: Outbox Relay & DLQ Handling — *Event-based (infrastructure)*

Not a business workflow itself, but underlies every event-emitting workflow above.

1. Any domain write (invoice, payment outcome, subscription change) is paired with an `Outbox` record in the same DB transaction.
2. `Outbox / CDC Relay` relays it to the `Event Bus`, avoiding dual-write inconsistency.
3. Consumers dedupe (at-least-once delivery); unprocessable events land in the `Dead Letter Queue Handler` for manual replay.

## Summary Table (ordered by frequency)

| # | Workflow | Initiator | Frequency |
|---|---|---|---|
| 1 | Bill/Invoice Creation | Event-based (recurring cycle) | Very high — every active subscription, every cycle |
| 2 | Payment Processing (Charge) | Event-based (follows #1) | Very high — one per invoice |
| 3 | Usage Metering Ingestion | Event-based (continuous) | Highest raw event rate, feeds #1 |
| 4 | Failed Payment → Dunning/Retry | Event-based (subset of #2) | Moderate — fraction of charges fail |
| 5 | Customer Plan Change | Customer-initiated | Moderate-low |
| 6 | Customer Payment Method Update | Customer-initiated | Low |
| 7 | Customer Invoice/History View | Customer-initiated | Low-moderate (read-only, variable) |
| 8 | Reconciliation | Event-based (scheduled batch) | Low (daily batch) |
| 9 | Internal/Ops Manual Adjustments | Internal-initiated | Low (ad hoc/exception) |
| 10 | Outbox Relay & DLQ Handling | Event-based (infrastructure) | Underlies all above, continuous |
