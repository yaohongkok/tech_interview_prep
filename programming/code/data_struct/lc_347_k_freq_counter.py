# 347. Top K Frequent Elements (using counter)

from collections import Counter

class Solution:
    def topKFrequent(self, nums: list[int], k: int) -> list[int]:
        numCounter = Counter()

        for n in nums:
            numCounter[n] += 1
        
        kMostCommon = numCounter.most_common(k)
        return [ n for n, _ in kMostCommon]

