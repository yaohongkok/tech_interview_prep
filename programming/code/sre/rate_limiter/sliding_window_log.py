# Sliding window log rate limiter: keep the timestamp of every accepted
# request and allow a new one only if fewer than `limit` fall inside the last
# `window` seconds. Exact, but memory is O(limit) per client.

import time
from collections import deque


class SlidingWindowLog:
    def __init__(self, limit, window, clock=time.monotonic):
        self.limit = limit
        self.window = window        # seconds
        # clock is injectable so tests can control time instead of sleeping
        self.clock = clock
        # Timestamps are appended in order, so the oldest is always on the
        # left and expiry is a popleft() rather than a scan.
        self.log = deque()

    def allow(self):
        now = self.clock()
        # The window is (now - window, now]: a request exactly `window`
        # seconds old has expired.
        while self.log and self.log[0] <= now - self.window:
            self.log.popleft()
        if len(self.log) < self.limit:
            # Only accepted requests are logged. Logging rejections too would
            # let an abusive client grow the log without bound and never recover.
            self.log.append(now)
            return True
        return False
