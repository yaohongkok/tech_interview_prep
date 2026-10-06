# 347. Top K Frequent Elements (using heapq)

import heapq

class Solution:
    def topKFrequent(self, nums: list[int], k: int) -> list[int]:
        numCounter = {}

        for n in nums:
            if n not in numCounter:
                numCounter[n] = 1
            else:
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