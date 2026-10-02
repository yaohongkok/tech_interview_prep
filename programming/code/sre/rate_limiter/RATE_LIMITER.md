# Rate Limiter: Token Bucket vs Sliding Window

## Summary

- **Token bucket** stores two numbers per client and allows controlled bursts. It is the default choice for API rate limiting.
- **Sliding window** comes in two variants that behave very differently on memory:
  - **Sliding window log** stores one timestamp per request. It is exact, but memory grows with the limit.
  - **Sliding window counter** stores two counters per client. It is approximate and can over-admit on bursty traffic, with memory comparable to token bucket.
- Choose token bucket when bursts are acceptable and you want to cap the average rate. Choose a sliding window when the rule is a hard quota: "never more than N in any period W".

## Token bucket

Each client has a bucket that holds up to `capacity` tokens and refills at `rate` tokens per second. A request spends one token. If the bucket is empty, the request is rejected.

No background timer is needed. The refill is computed lazily from the time elapsed since the last request.

Implementation: [token_bucket.py](token_bucket.py)

Properties:

- **Two independent knobs.** `rate` sets the sustained throughput and `capacity` sets the burst size.
- **Bursts are allowed.** An idle client can send `capacity` requests at once.
- **The bound is loose.** Over any interval of `T` seconds a client can send up to `capacity + rate * T` requests. With `capacity = 100` and `rate = 100/min`, that is up to 200 requests in one minute.
- **Recovery is smooth.** After a burst, the client gets one request back every `1/rate` seconds.
- **Weighted requests are easy.** An expensive endpoint charges `cost > 1`.
- **`Retry-After` is trivial.** It is `(cost - tokens) / rate`.

## Sliding window

A fixed window counter (reset the count every minute) lets a client send `2 * limit` requests across a window boundary: `limit` at 0:59 and `limit` again at 1:01. A sliding window fixes this by evaluating the window relative to the current time.

### Sliding window log

Store the timestamp of every accepted request. On each request, drop the timestamps older than `now - window`, then count what is left.

Implementation: [sliding_window_log.py](sliding_window_log.py)

Properties:

- **Exact.** There are never more than `limit` requests in any window of length `window`.
- **Memory grows with the limit**, up to `limit` timestamps per client.
- **Recovery is abrupt.** A client that sends `limit` requests at once is locked out for the full window, then gets all of them back at once.
- **Log only accepted requests.** If rejected requests are also logged, an abusive client can grow the log without bound and never recover.

### Sliding window counter

Keep a count for the current fixed window and the previous one. Estimate the sliding count by weighting the previous window by how much of it still overlaps.

```
estimate = prev_count * (1 - elapsed_fraction_of_current_window) + curr_count
```

Implementation: [sliding_window_counter.py](sliding_window_counter.py)

Properties:

- **Approximate.** It assumes requests in the previous window were evenly spread, so it over-counts or under-counts when they were not.
- **The worst case is close to `2 * limit`.** If the previous window's requests all arrive at its end, the estimate discounts them too early. Two bursts almost one window apart both get through.
- **It still fixes the fixed window's boundary problem.** Two bursts a few seconds apart across a boundary are blocked.
- **Constant memory**, regardless of the limit.
- **Good enough for evenly spread traffic.** Cloudflare uses this approach and reported an error rate of about 0.003% of requests on its traffic.

## Memory analysis

`K` is the number of active clients (keys) and `L` is the limit per window.

| Algorithm | State per key | Space per key | Total space | Time per request |
|---|---|---|---|---|
| Token bucket | `tokens`, `last_refill` | O(1), about 16 bytes | O(K) | O(1) |
| Sliding window counter | `prev`, `curr`, window index | O(1), about 24 bytes | O(K) | O(1) |
| Sliding window log | one timestamp per request | O(L), up to `8 * L` bytes | O(K * L) | O(1) amortized with a deque, O(log L) with a sorted set |

Worst case for 1 million active clients, counting raw state only (8 bytes per number):

| Limit | Token bucket | Sliding window counter | Sliding window log |
|---|---|---|---|
| 100 per minute | 16 MB | 24 MB | 800 MB |
| 1,000 per hour | 16 MB | 24 MB | 8 GB |
| 10,000 per day | 16 MB | 24 MB | 80 GB |

Points to draw from this:

- **Token bucket and sliding window counter are independent of the limit.** Raising the limit from 100 to 10,000 costs nothing.
- **Sliding window log scales with the limit, not the window length.** A long window only hurts because long windows usually have large limits.
- **Real numbers are higher in a store such as Redis.** Each key carries its name and object overhead, and each sorted-set entry costs several times the raw 8 bytes. The ratios between the algorithms stay roughly the same.
- **Idle keys must expire.** Set a TTL on each key: `capacity / rate` for token bucket (the bucket is full again by then), `window` for the log, and `2 * window` for the counter. Without a TTL, memory grows with every client ever seen, not with active clients.
- **Multiple tiers multiply the cost.** A rule such as "10 per second and 1,000 per hour" needs one state record per tier per key.

## Distributed implementation (Redis)

| Algorithm | Redis structure | Operations | Atomicity |
|---|---|---|---|
| Token bucket | Hash with 2 fields | Read, compute refill, write | Needs a Lua script. Read-modify-write races otherwise. |
| Sliding window log | Sorted set, score = timestamp | `ZREMRANGEBYSCORE`, `ZCARD`, `ZADD` | Needs a Lua script or `MULTI`. |
| Sliding window counter | Two string counters | `GET` previous, `INCR` current, `EXPIRE` | `INCR` is atomic. A small race on the read is tolerable because the result is already approximate. |

Use the Redis server time (`TIME`) inside the script rather than the application server's clock, so that clock skew between app servers does not affect the result.

## When to use each

| Situation | Choice | Reason |
|---|---|---|
| General API rate limiting | Token bucket | Tolerates the bursts that real clients produce, with constant memory |
| Bursts should be allowed but sized separately from the sustained rate | Token bucket | `rate` and `capacity` are independent |
| Requests have different costs | Token bucket | Charge more tokens for expensive calls |
| Hard quota that must never be exceeded (login attempts, OTP sends, payment attempts) | Sliding window log | Exact, and limits are small so memory is cheap |
| Need an audit trail of when each request happened | Sliding window log | The timestamps are already stored |
| "N per window" semantics at very large scale, where some overshoot is tolerable | Sliding window counter | Close to exact on evenly spread traffic, with constant memory |
| High limits (thousands per window) across many keys | Token bucket or sliding window counter | The log's O(K * L) memory is too expensive |
| Protecting a downstream that cannot absorb any burst | Neither. Use a leaky bucket | It smooths output to a constant rate |

Rules of thumb:

- **Start with token bucket.** It is what AWS API Gateway and Stripe use for request rate limiting.
- **Move to a sliding window when the requirement is worded as a quota**, such as "5 login attempts per 15 minutes". Product and security requirements are usually stated this way, and a sliding window maps to them directly.
- **Use the log when the limit is small or the quota must never be exceeded.** Otherwise use the counter.
- **Combine them when needed.** A common setup is a token bucket per client for short-term burst control plus a sliding window counter for the hourly or daily quota.

## Comparison at a glance

| | Token bucket | Sliding window log | Sliding window counter |
|---|---|---|---|
| Memory per key | O(1) | O(L) | O(1) |
| Accuracy | Exact for its own model | Exact | Approximate |
| Burst handling | Allowed up to `capacity` | Allowed up to `limit`, then full lockout | Allowed up to `limit`, more if the previous window was bunched |
| Max requests in any window `W` | `capacity + rate * W` | `limit` | `limit` on even traffic, close to `2 * limit` worst case |
| Recovery after burst | Gradual | All at once when entries expire | Gradual |
| Parameters | `rate`, `capacity` | `limit`, `window` | `limit`, `window` |
| Weighted requests | Natural | Awkward | Possible (increment by cost) |

## Code and tests

| File | Purpose |
|---|---|
| [token_bucket.py](token_bucket.py) | Token bucket |
| [sliding_window_log.py](sliding_window_log.py) | Sliding window log |
| [sliding_window_counter.py](sliding_window_counter.py) | Sliding window counter |
| [test_rate_limiters.py](test_rate_limiters.py) | Unit tests for all three |
| [simulate.py](simulate.py) | Replays traffic patterns against all three and measures memory per client |

Each limiter takes an optional `clock` argument that defaults to `time.monotonic`. The tests and the simulation pass in a fake clock, so they are deterministic and never sleep.

Run from this directory. Only the standard library is needed.

```
python3 test_rate_limiters.py -v
python3 simulate.py
```

Results from `simulate.py` with a limit of 60 requests per 60 seconds. Each cell is requests accepted, with the peak in any 60 second window in brackets.

| Scenario | Fixed window | Token bucket | Sliding window log | Sliding window counter |
|---|---|---|---|---|
| 120 requests at t=0 | 60 (60) | 60 (60) | 60 (60) | 60 (60) |
| 60 at t=59, 60 at t=61 | 120 (120) | 62 (62) | 60 (60) | 61 (61) |
| 60 at t=59, 60 at t=118 | 120 (120) | 119 (119) | 60 (60) | 118 (118) |
| 60 at t=0, then 1 per second until t=120 | 121 (60) | 180 (119) | 121 (60) | 120 (60) |
| 2 per second for 300 seconds | 300 (60) | 359 (119) | 300 (60) | 298 (60) |

Measured Python heap per client at the limit, in bytes. The absolute figures include Python object overhead, so compare the growth across the row.

| Algorithm | limit=10 | limit=100 | limit=1000 |
|---|---|---|---|
| Token bucket | 163 | 180 | 180 |
| Sliding window log | 1,103 | 4,316 | 33,308 |
| Sliding window counter | 131 | 128 | 160 |
