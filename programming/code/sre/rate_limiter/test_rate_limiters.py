# Unit tests for the three rate limiters. Time is driven by a fake clock, so
# the tests are deterministic and never sleep.
#
# usage: python test_rate_limiters.py [-v]

import random
import unittest

from sliding_window_counter import SlidingWindowCounter
from sliding_window_log import SlidingWindowLog
from token_bucket import TokenBucket


class FakeClock:
    """Stands in for time.monotonic(); time only moves when advance() is called."""

    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def count_allowed(limiter, requests):
    """Send `requests` requests at the current time and count the accepted ones."""
    return sum(limiter.allow() for _ in range(requests))


def max_in_any_window(timestamps, window):
    """Largest number of timestamps that fall inside any (t - window, t] interval."""
    best = left = 0
    for right, ts in enumerate(timestamps):
        while timestamps[left] <= ts - window:
            left += 1
        best = max(best, right - left + 1)
    return best


class TokenBucketTest(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.bucket = TokenBucket(rate=1, capacity=5, clock=self.clock)

    def test_starts_full_and_allows_burst_up_to_capacity(self):
        self.assertEqual(count_allowed(self.bucket, 10), 5)

    def test_refills_at_rate(self):
        count_allowed(self.bucket, 5)
        self.clock.advance(2)
        self.assertEqual(count_allowed(self.bucket, 10), 2)

    def test_partial_token_is_not_enough(self):
        count_allowed(self.bucket, 5)
        self.clock.advance(0.5)
        self.assertFalse(self.bucket.allow())
        self.clock.advance(0.5)
        self.assertTrue(self.bucket.allow())

    def test_refill_is_capped_at_capacity(self):
        count_allowed(self.bucket, 5)
        self.clock.advance(1000)
        self.assertEqual(count_allowed(self.bucket, 10), 5)

    def test_weighted_request_spends_cost_tokens(self):
        self.assertTrue(self.bucket.allow(cost=3))
        # 2 tokens left: a rejected request must not spend any of them
        self.assertFalse(self.bucket.allow(cost=3))
        self.assertTrue(self.bucket.allow(cost=2))
        self.assertFalse(self.bucket.allow())

    def test_burst_plus_refill_can_reach_twice_capacity_in_one_window(self):
        # Documents the loose bound: capacity + rate * T requests in T seconds.
        accepted = []
        for _ in range(5):
            if self.bucket.allow():
                accepted.append(self.clock())
        for _ in range(4):
            self.clock.advance(1)
            if self.bucket.allow():
                accepted.append(self.clock())
        self.assertEqual(max_in_any_window(accepted, window=5), 9)


class SlidingWindowLogTest(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.limiter = SlidingWindowLog(limit=3, window=10, clock=self.clock)

    def test_allows_up_to_limit(self):
        self.assertEqual(count_allowed(self.limiter, 10), 3)

    def test_entries_expire_after_window(self):
        count_allowed(self.limiter, 3)
        self.clock.advance(9.9)
        self.assertFalse(self.limiter.allow())
        self.clock.advance(0.1)
        self.assertEqual(count_allowed(self.limiter, 10), 3)

    def test_window_slides_with_each_request(self):
        self.assertTrue(self.limiter.allow())       # t=0
        self.clock.advance(6)
        self.assertEqual(count_allowed(self.limiter, 10), 2)    # t=6
        self.clock.advance(4)
        # t=10: only the t=0 request has expired, so exactly one slot is free
        self.assertEqual(count_allowed(self.limiter, 10), 1)

    def test_rejected_requests_are_not_logged(self):
        count_allowed(self.limiter, 3)
        self.clock.advance(5)
        self.assertEqual(count_allowed(self.limiter, 100), 0)
        self.assertEqual(len(self.limiter.log), 3)
        self.clock.advance(5)
        # If the rejections at t=5 had been logged, the client would still be blocked.
        self.assertEqual(count_allowed(self.limiter, 10), 3)

    def test_never_exceeds_limit_in_any_window_under_random_traffic(self):
        rng = random.Random(42)
        accepted = []
        for _ in range(5000):
            self.clock.advance(rng.uniform(0, 2))
            if self.limiter.allow():
                accepted.append(self.clock())
            self.assertLessEqual(len(self.limiter.log), 3)
        self.assertEqual(max_in_any_window(accepted, window=10), 3)


class SlidingWindowCounterTest(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.limiter = SlidingWindowCounter(limit=10, window=10, clock=self.clock)

    def test_allows_up_to_limit(self):
        self.assertEqual(count_allowed(self.limiter, 20), 10)

    def test_previous_window_is_weighted_by_overlap(self):
        count_allowed(self.limiter, 10)             # t=0, fills window 0
        self.clock.advance(15)
        # t=15 is halfway through window 1, so half of window 0 still counts:
        # estimate = 10 * 0.5 = 5, leaving room for 5.
        self.assertEqual(count_allowed(self.limiter, 20), 5)

    def test_blocks_burst_across_window_boundary(self):
        # A fixed window counter would allow 10 + 10 here.
        self.clock.advance(9)
        count_allowed(self.limiter, 10)             # t=9
        self.clock.advance(2)
        self.assertEqual(count_allowed(self.limiter, 20), 1)    # t=11

    def test_previous_count_dropped_after_idle_gap(self):
        count_allowed(self.limiter, 10)             # t=0, window 0
        self.clock.advance(25)                      # t=25, window 2
        self.assertEqual(count_allowed(self.limiter, 20), 10)

    def test_over_admits_when_previous_window_was_bunched_at_the_end(self):
        # Documents the approximation. All 10 requests land at t=9, but at
        # t=18 the estimate treats them as evenly spread and counts only 2.
        accepted = []
        self.clock.advance(9)
        for _ in range(10):
            if self.limiter.allow():
                accepted.append(self.clock())
        self.clock.advance(9)
        for _ in range(20):
            if self.limiter.allow():
                accepted.append(self.clock())
        # 18 requests accepted inside one real 10 second window, limit is 10
        self.assertEqual(max_in_any_window(accepted, window=10), 18)


if __name__ == "__main__":
    unittest.main()
