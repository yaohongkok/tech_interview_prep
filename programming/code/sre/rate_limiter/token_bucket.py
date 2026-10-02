# Token bucket rate limiter: a bucket holds up to `capacity` tokens and refills
# at `rate` tokens per second. Each request spends tokens; an empty bucket
# rejects the request.

import time


class TokenBucket:
    def __init__(self, rate, capacity, clock=time.monotonic):
        self.rate = rate            # tokens added per second
        self.capacity = capacity    # max burst size
        # clock is injectable so tests can control time instead of sleeping
        self.clock = clock
        self.tokens = capacity      # start full so an idle client can burst
        self.last = clock()

    def allow(self, cost=1):
        """Spend `cost` tokens if available. A rejected request spends nothing."""
        now = self.clock()
        # Lazy refill: add the tokens earned since the last call, so no
        # background timer is needed. min() discards anything over capacity.
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False
