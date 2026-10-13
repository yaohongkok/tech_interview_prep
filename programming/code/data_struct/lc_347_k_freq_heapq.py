# 347. Top K Frequent Elements (using heapq)

# Key Tricks:
# 1. Use a min heap to keep track of the k largest elements
# 2. When you pop the min heap, it is always the smallest element in the heap


import heapq
from collections import defaultdict

class Solution:
    def topKFrequent(self, nums: list[int], k: int) -> list[int]:
        numCounter = defaultdict(int)

        for n in nums:
            numCounter[n] += 1
        
        heapList = []

        for n, c in numCounter.items():
            # Build a k-element heap that contains largest k nums only
            # We can also build max heap but we need to use .nlargest() 
            # to get the largest k elements, 
            # which is less efficient than using a min heap
            heapq.heappush(heapList, (c, n))

            # Pop out the lowest value
            if len(heapList) > k:
                heapq.heappop(heapList)

        return [ n  for _, n in heapList ]