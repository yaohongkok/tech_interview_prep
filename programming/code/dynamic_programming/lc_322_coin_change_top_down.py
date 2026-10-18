# Leet Code 322 - Coin Change

# Bellman equation:
# f(r) = 1 + min ( f(r - c[0]), f(r - c[1]), ... )
# Base cases:
#  f(0) = 0
#  f(-x) = +Inf

import math
from functools import lru_cache

class Solution:

    @lru_cache(maxsize=None)
    def _f(self, coins:tuple, amt:int) -> int:
        if amt == 0:
            return 0

        if amt < 0:
            return math.inf

        f_opts = [self._f(coins, amt - c) for c in coins]

        return 1 + min(f_opts)

    def coinChange(self, coins: list[int], amount: int) -> int:
        ans = self._f(tuple(coins), amount)

        if math.isinf(ans):
            ans = -1

        return ans