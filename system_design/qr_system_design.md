# System Design: QR Code System for a Grocery Shop

---

## 1. Clarifying the Scope

Before diving in, it's worth noting that "QR code system" for a grocery shop can mean several things. The most complete answer covers all three primary use cases:

- **Product QR codes** — on shelves/labels for product info, pricing, or promotions
- **Self-checkout QR codes** — customers scan items to build a cart and pay
- **Receipt / loyalty QR codes** — post-purchase tracking, loyalty points, digital receipts

**Design choice:** I address all three in the architecture, because they share the same backend infrastructure (product catalogue, auth, payment). A real interview would narrow scope; here I cover breadth with depth on checkout.

---

## 2. Requirements

### Functional
- Generate unique QR codes for every product SKU
- Customer scans QR → sees product detail (name, price, allergens, promotions)
- Customer can add items to a cart via scan
- Cart totalling, discount application, and payment via QR (e.g., link to payment gateway or in-app)
- Staff admin panel to update products and regenerate QR codes

### Non-Functional
- **Low latency:** Scan → product info in < 200 ms (customers are standing in an aisle)
- **High availability:** 99.9% uptime; a downed system means lost sales
- **Scalability:** A busy weekend grocery shop might see 5,000+ scans/hour
- **Offline resilience:** Basic product info should work even with spotty in-store Wi-Fi
- **Security:** Payment flows must be encrypted and fraud-resistant

---

## 3. High-Level Architecture

```
[Customer Phone]
      |
      | HTTPS
      v
[CDN / Edge Cache]  <--- static product pages cached here
      |
      v
[API Gateway]
      |
      |----> [Product Service]  ----> [Product DB (PostgreSQL)]
      |                                      |
      |----> [Cart Service]    <-----------> [Cache (Redis)]
      |
      |----> [Auth Service]    ----> [User DB]
      |
      |----> [Payment Service] ----> [Payment Gateway (Stripe / FPX)]
      |
      |----> [Notification Service] ---> [Email / SMS]
      |
[Admin Panel] -----> [QR Generation Service] ----> [Object Storage (S3)]
```

**Design choice — separate microservices:** Product lookup, cart management, and payment are independently scalable. During a flash sale, the Product Service may need 10× more instances while Payment stays the same. Monoliths are simpler to start but don't scale independently.

---

## 4. QR Code Generation

Each QR code encodes a **short URL**:

```
https://shop.example.com/p/{product_id}
```

- `product_id` is an opaque UUID (not sequential integers — avoids enumeration attacks)
- The URL resolves via the Product Service
- QR image is generated once per product and stored in object storage (S3/Cloudflare R2)

**Design choice — URL-based QR, not data-embedded:** Embedding full product data in the QR payload limits you. A URL means you can update prices, descriptions, and promos without reprinting QR codes. The QR just needs to survive until the shelf label is reprinted.

**Design choice — UUID over sequential ID:** If you use `product_id=1001`, a competitor or attacker can enumerate your entire catalogue. UUIDs prevent this.

### QR Generation Flow (Admin)
1. Admin creates/updates product in admin panel
2. Admin panel calls `POST /api/qr/generate` with `product_id`
3. QR Generation Service creates the PNG using a library (e.g., `qrcode` in Python)
4. PNG uploaded to S3 with key `qr/{product_id}.png`
5. S3 URL stored in product record

---

## 5. Product Lookup Flow (Customer Scans QR)

```
Phone camera scans QR
    → Browser opens https://shop.example.com/p/{uuid}
    → CDN checks cache (hit? return cached HTML in ~20ms)
    → Cache miss → API Gateway → Product Service
    → Product Service reads from Redis cache
    → Redis miss → PostgreSQL read replica
    → Returns: name, price, image, allergens, promotions
    → Response cached in CDN for 60s
```

**Design choice — CDN caching:** Product pages are read-heavy and mostly static. Caching at the CDN edge means the majority of scans never hit the origin. A 60-second TTL balances freshness (price changes propagate within a minute) with load reduction.

**Design choice — Redis in front of PostgreSQL:** The hot product catalogue (top 1,000 SKUs) lives in Redis. This avoids hammering the DB on every scan. TTL of 5 minutes; explicit invalidation on product update.

---

## 6. Cart and Checkout Flow

```
Customer scans product QR
    → Taps "Add to Cart"
    → POST /api/cart/{session_id}/items  { product_id, qty }
    → Cart Service validates product exists and has stock
    → Cart stored in Redis (TTL: 2 hours, matching a typical shopping trip)

Customer taps "Checkout"
    → GET /api/cart/{session_id}/summary  → totals, taxes, applied promos
    → Customer selects payment method
    → POST /api/payment/initiate
    → Payment Service calls Stripe/FPX
    → On success: Order record written to DB, cart cleared, receipt generated
```

**Design choice — Redis for cart state:** Carts are ephemeral and session-scoped. They need fast read/write and natural expiry. A relational DB is overkill and slower. Redis TTL handles abandoned cart cleanup automatically.

**Design choice — idempotency key on payment:** The payment initiation request includes a UUID idempotency key. If the customer's phone loses connectivity mid-request and retries, the Payment Service recognises the duplicate and doesn't double-charge.

---

## 7. Database Schema (simplified)

```sql
-- Products
products (
  id          UUID PRIMARY KEY,
  sku         VARCHAR(50) UNIQUE,
  name        VARCHAR(200),
  price_cents INT,
  category    VARCHAR(100),
  qr_url      TEXT,
  updated_at  TIMESTAMP
)

-- Promotions (separate table, many promos per product)
promotions (
  id          UUID PRIMARY KEY,
  product_id  UUID REFERENCES products(id),
  discount_pct DECIMAL(5,2),
  valid_from  TIMESTAMP,
  valid_until TIMESTAMP
)

-- Orders
orders (
  id            UUID PRIMARY KEY,
  customer_id   UUID,
  total_cents   INT,
  status        VARCHAR(50),
  created_at    TIMESTAMP
)

-- Order line items
order_items (
  id          UUID PRIMARY KEY,
  order_id    UUID REFERENCES orders(id),
  product_id  UUID REFERENCES products(id),
  qty         INT,
  unit_price_cents INT
)
```

**Design choice — price stored in cents (integer):** Floating-point arithmetic on currency causes rounding bugs. Integers are exact. Divide by 100 only at display time.

---

## 8. Handling Offline / Poor Connectivity

In-store Wi-Fi can be unreliable. Mitigation strategies:

- **Progressive Web App (PWA) with service worker:** Cache recently scanned product pages locally on the phone
- **QR codes include basic info in the URL path** (category hint) so the CDN can serve a cached shell even if the origin is slow
- **Staff fallback:** Cashier override terminal that can process sales manually if all systems fail

**Design choice — PWA over native app:** Customers don't want to download an app just to scan a grocery QR. A PWA works in the browser, can be added to the home screen, and supports offline caching.

---

## 9. Security Considerations

| Threat | Mitigation |
|--------|-----------|
| Fake/tampered QR codes | QR encodes HTTPS URL to your domain; phishing domains are caught by browser warnings |
| Cart manipulation | Cart items validated server-side against product DB; price never trusted from client |
| Payment fraud | Stripe handles PCI-DSS compliance; 3DS authentication on large transactions |
| Enumeration of products | UUID product IDs; rate limiting on product endpoint |
| Session hijacking | Cart session tied to device fingerprint + short TTL |

---

## 10. Scalability Estimates

Assume: 500 customers/hour peak, average 30 scans per customer = **15,000 scans/hour** ≈ **4 req/sec**.

This is modest — a single API server handles this easily. However:

- A regional chain with 50 stores = 750 req/sec — horizontal scaling kicks in
- Use **auto-scaling groups** behind the API Gateway
- **Read replicas** on PostgreSQL for product reads
- **CDN absorbs 80–90% of product lookups** (cache hit ratio on popular items)

---

## 11. Key Trade-offs Summary

| Decision | Choice | Why |
|----------|--------|-----|
| QR payload | URL (not embedded data) | Update info without reprinting |
| Product ID | UUID | Security; prevent enumeration |
| Cart storage | Redis | Speed, natural TTL, ephemeral data |
| Price storage | Integer (cents) | Avoid floating-point errors |
| App delivery | PWA | No install friction; offline support |
| Caching | CDN + Redis | Latency reduction; DB protection |
| Microservices | Yes | Independent scaling of hot paths |

---

*Designed with a mid-size grocery shop in mind — scales from a single store to a regional chain without rearchitecting the core.*
