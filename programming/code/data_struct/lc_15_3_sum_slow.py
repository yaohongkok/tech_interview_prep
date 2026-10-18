# Leetcode 15. 3Sum

class Solution:
    def createNumDict(self, nums: list[int]) -> dict[int, set[int]]:
        numDict = {}

        for i, n in enumerate(nums):
            numDict.setdefault(n, set()).add(i)

        return numDict

    def threeSum(self, nums: list[int]) -> list[list[int]]:
        print('Start')
        resultSet = set()

        numDict = self.createNumDict(nums)

        for i, ni in enumerate(nums):
            for j, nj in enumerate(nums):
                if i == j:
                    continue

                target = -ni - nj

                if target in numDict:
                    for ki in numDict[target]:
                        if i != ki and j != ki:
                            candidate = tuple(sorted([ni, nj, target]))
                            resultSet.add(candidate)

        return [list(r) for r in resultSet ]