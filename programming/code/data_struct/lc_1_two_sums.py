# LC #1

# Key trick:
# 1. Dictionary to store the number and its index.
# 2. Check remainder in dictionary

class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        numsDict = {n: i for i, n in enumerate(nums)}

        for i, n in enumerate(nums):
            remainder = target - n
            
            if remainder in numsDict and numsDict[remainder]!= i :
                return [i, numsDict[remainder]]