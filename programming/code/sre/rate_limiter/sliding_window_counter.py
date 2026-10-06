# Sliding window counter rate limiter: keep one count for the current fixed
# window and one for the previous window, and estimate the sliding count by
# weighting the previous window by how much of it still overlaps.
# Approximate, but memory is O(1) per client.

import time


class SlidingWindowCounter:
    def __init__(self, limit, window, clock=time.monotonic):
        self.limit = limit
        self.window = window        # seconds
        # clock is injectable so tests can control time instead of sleeping
        self.clock = clock
        self.curr_idx = 0           # which fixed window `curr` belongs to
        self.curr_req_count = 0
        self.prev_req_count = 0

    def prepare_windows_state(self, now):
        idx = int(now // self.window)

        if idx != self.curr_idx:
            prev_idx = self.curr_idx

            # The previous count only carries over if the windows are
            # adjacent. After a longer idle gap it is too old to matter.
            if idx == prev_idx + 1:
                self.prev_req_count = self.curr_req_count
            else:
                self.prev_req_count = 0

            self.curr_req_count = 0
            self.curr_idx = idx

    def allow(self):
        now = self.clock()

        self.prepare_windows_state(now)

        # Fraction of the current fixed window that has elapsed. The sliding
        # window still overlaps the remaining (1 - elapsed) of the previous one.
        elapsed = (now % self.window) / self.window

        # Assumes the previous window's requests were evenly spread. If they
        # were bunched at the end, this under-counts and over-admits.
        est_req_count = self.prev_req_count * (1 - elapsed) + self.curr_req_count

        if est_req_count < self.limit:
            self.curr_req_count += 1
            return True

        return False
