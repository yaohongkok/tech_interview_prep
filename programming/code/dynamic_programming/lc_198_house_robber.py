# Leet Code  198 - House Robber

# Key Tricks:
# - Dynamic programming - Bellman
# - If take nums[i], we have to skip to V(i+2)
# - Else, we can compute V(i+1)
# - V(i) = max( V(i+2) + nums[i], V(i+1) )

from functools import lru_cache

class Solution:
    # If dp[i-1] = 1, dp[i] = 0
    # Else: dp[i] = 0 or 1
    # Goal: V_max = max(dp[0]*nums[0] + ... + dp[i-1]*nums[i-1] + dp[i]*nums[i] + ...)
    # Can be further simplify as Bellman equation
    # State is dp[i-1]
    # Bellman equation can simplified down to:
    # V(i) = max( V(i+2) + nums[i], V(i+1) )

    @lru_cache(maxsize=None)
    def _V(self, nums: tuple, i) -> int:
        if i >= len(nums):
            return 0
        
        # If take nums[i], we have to skip to V(i+2)
        # Else, we can compute V(i+1)
        return max( self._V(nums, i+2) + nums[i], self._V(nums, i+1))

    def rob(self, nums: list[int]) -> int:
        return self._V(tuple(nums), 0)