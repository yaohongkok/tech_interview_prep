# Leet Code 875

# Key Tricks:
# - Create a function to calculate totalEatingHours
# - The feasiblity condition is hoursTaken <= h
#    Every time we get into the feasibility condition, we 
#    push the answer to left (i.e. minimizing).
# - Save the answer when the feasibility condition is met.

from math import ceil

class Solution:
    def totalEatingHours(self, piles:list[int], quantityPerHour: int) -> int:
        totalHours = 0

        for pile in piles:
            hours = ceil(pile / quantityPerHour)
            totalHours += hours

        return totalHours

    def minEatingSpeed(self, piles: list[int], h: int) -> int:
        # Yields fastest hours taken
        # Anything lower will yield longer hours
        maxQuantityPerHour = max(piles)

        if len(piles) == h:
            return maxQuantityPerHour

        lo = 1
        hi = maxQuantityPerHour
        ans = hi

        while lo <= hi:
            mid = (lo + hi) // 2

            hoursTook = self.totalEatingHours(piles, mid)

            # Whenever we get a feasible answer,
            # the answer is getting smaller
            if hoursTook <= h:
                ans = mid
                hi = mid - 1
            else:
                lo = mid + 1


        return ans