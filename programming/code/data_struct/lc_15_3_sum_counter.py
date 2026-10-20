# Leetcode 15. 3Sum


# Key tricks:
# - Use a counter to keep track of the # of occurrences of each number.
# - Result should be ascending order tuples.
#     This create the requirement: ni <= nj <= target (nk)
# - Loop through the counter keys in ascending order. 
#     This ensures that we only consider valid combinations of ni, nj, nk.
# - Decrease the counter for ni and nj when we are considering them, 
#     and increase it back after we are done.


from collections import Counter

class Solution:
    def createNumCounter(self, nums: list[int]) -> dict[int, set[int]]:
        numCounter = Counter()

        for n in nums:
            if n not in numCounter:
                numCounter[n] = 0
            
            numCounter[n] += 1

        return numCounter

    def threeSum(self, nums: list[int]) -> list[list[int]]:
        resultList = []

        numCounter = self.createNumCounter(nums)

        counterKeys = sorted(numCounter.keys())

        for i, ni in enumerate(counterKeys):
            # Different ordering does not matter. So, we keep ascending order.
            # We enforce our tuple to be ni <= nj <= target
            if ni > 0:
                break

            if numCounter[ni] == 0:
                continue

            numCounter[ni] -= 1

            # Loop through ascending order
            for nj in counterKeys[i:]:
                if numCounter[nj] == 0:
                    continue

                target = -ni - nj

                # Need to adhere to ni <= nj <= target
                if target < nj:
                    break

                # Only decrement when condition is valid
                numCounter[nj] -= 1

                if target in numCounter and numCounter[target] >0:
                    resultList.append([ni, nj, target])
                
                numCounter[nj] += 1
            
            numCounter[ni] += 1

        return resultList