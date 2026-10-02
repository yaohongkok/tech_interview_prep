# Replays the same traffic patterns against each rate limiter and compares
# how many requests get through and how much memory each client costs.
# Time is simulated, so the whole run takes a moment rather than minutes.
#
# usage: python simulate.py

import tracemalloc

from sliding_window_counter import SlidingWindowCounter
from sliding_window_log import SlidingWindowLog
from token_bucket import TokenBucket

LIMIT = 60      # requests
WINDOW = 60     # seconds, so the sustained rate is 1 request per second


class FakeClock:
    """Stands in for time.monotonic() so a scenario can jump to any timestamp."""

    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


class FixedWindowCounter:
    """Baseline only: the naive counter that the sliding windows improve on."""

    def __init__(self, limit, window, clock):
        self.limit = limit
        self.window = window
        self.clock = clock
        self.idx = 0
        self.count = 0

    def allow(self):
        idx = int(self.clock() // self.window)
        if idx != self.idx:
            self.idx = idx
            self.count = 0
        if self.count < self.limit:
            self.count += 1
            return True
        return False


# name -> factory(limit, window, clock). Token bucket is configured so that
# its sustained rate and burst size match the window limit.
RATE_LIMITERS = {
    "fixed window (baseline)": FixedWindowCounter,
    "token bucket": lambda limit, window, clock: TokenBucket(limit / window, limit, clock),
    "sliding window log": SlidingWindowLog,
    "sliding window counter": SlidingWindowCounter,
}

# name -> [(timestamp, number of requests sent at that timestamp)]
SCENARIOS = {
    "Burst from idle: 120 requests at t=0":
        [(0, 120)],
    "Burst across a fixed window boundary: 60 at t=59, 60 at t=61":
        [(59, 60), (61, 60)],
    "Two bursts almost one window apart: 60 at t=59, 60 at t=118":
        [(59, 60), (118, 60)],
    "Burst then steady: 60 at t=0, then 1 per second until t=120":
        [(0, 60)] + [(t, 1) for t in range(1, 121)],
    "Sustained overload: 2 per second for 300 seconds":
        [(t, 2) for t in range(300)],
}


def max_in_any_window(timestamps, window):
    """Largest number of timestamps that fall inside any (t - window, t] interval."""
    best = left = 0
    for right, ts in enumerate(timestamps):
        while timestamps[left] <= ts - window:
            left += 1
        best = max(best, right - left + 1)
    return best


def replay(factory, traffic):
    """Return the timestamps of the requests the limiter accepted."""
    clock = FakeClock()
    limiter = factory(LIMIT, WINDOW, clock)
    accepted = []
    for timestamp, requests in traffic:
        clock.now = float(timestamp)
        for _ in range(requests):
            if limiter.allow():
                accepted.append(clock.now)
    return accepted


def compare_behaviour():
    print(f"Limit: {LIMIT} requests per {WINDOW} seconds\n")
    for scenario, traffic in SCENARIOS.items():
        sent = sum(requests for _, requests in traffic)
        print(scenario)
        print(f"  {'algorithm':<25} {'accepted':>10}   {'peak in any ' + str(WINDOW) + 's':>16}")
        for rl_name, rl_factory in RATE_LIMITERS.items():
            accepted_ts = replay(rl_factory, traffic)
            peak = max_in_any_window(accepted_ts, WINDOW)
            # the peak is what the limit is supposed to cap
            flag = "  <-- over limit" if peak > LIMIT else ""
            print(f"  {rl_name:<25} {len(accepted_ts):>4}/{sent:<5}   {peak:>16}{flag}")
        print()


def bytes_per_client(factory, limit, clients=500):
    """Measure the Python heap used per client once each one has hit its limit."""
    clock = FakeClock()
    tracemalloc.start()
    before = tracemalloc.get_traced_memory()[0]
    limiters = [factory(limit, WINDOW, clock) for _ in range(clients)]
    # Spread the requests over the window and give every client its own
    # arrival time, so each logged timestamp is a separate float object as it
    # would be with real traffic. Sharing one timestamp between clients would
    # hide most of the log's cost.
    step = WINDOW / limit
    for i in range(limit):
        for offset, limiter in enumerate(limiters):
            clock.now = (i + offset / clients) * step
            limiter.allow()
    after = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()
    return (after - before) / clients


def compare_memory():
    limits = (10, 100, 1000)
    print("Memory per client at the limit (bytes of Python heap)")
    print(f"  {'algorithm':<25}" + "".join(f"{'limit=' + str(limit):>14}" for limit in limits))
    for name, factory in RATE_LIMITERS.items():
        if factory is FixedWindowCounter:
            continue
        sizes = "".join(f"{bytes_per_client(factory, limit):>14,.0f}" for limit in limits)
        print(f"  {name:<25}{sizes}")
    # CPython stores every number as a heap object, so the absolute figures
    # are far above the 8 bytes per value a compact store would need. The
    # point is the growth: flat for two of them, linear in the limit for the log.
    print("\n  Absolute sizes include Python object overhead; compare the growth, not the bytes.")


if __name__ == "__main__":
    compare_behaviour()
    compare_memory()
