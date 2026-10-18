# Leet Code 875

# Key Tricks:
# - Create a function to calculate totalEatingHours
# - First, use binary search to find a mid value where hoursTaken == h
# - Finally, decrement to find the min value (can use another round of BS too)

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

        while lo <= hi:
            mid = (lo + hi) // 2

            hoursTook = self.totalEatingHours(piles, mid)

            if hoursTook == h:
                # There can be multiple values that satisfy eating hours == h
                # So, we need to find the min
                while mid > 0 and self.totalEatingHours(piles, mid) == h:
                    knownGoodMid = mid
                    mid -= 1

                return knownGoodMid
            elif hoursTook > h:
                lo = mid + 1
            else:
                hi = mid - 1

        hoursTook = self.totalEatingHours(piles, mid)

        if hoursTook > h:
            mid += 1

        return mid