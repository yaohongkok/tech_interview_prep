from collections import defaultdict

class Solution:
    def getCharCount(self, s):
        charCount = [0] * 26
        for c in s:
            charIdx = ord(c) - ord('a')
            charCount[charIdx] += 1

        # list is not hashable.
        return tuple(charCount)


    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        resDict = defaultdict(list)

        for s in strs:
            charCount = self.getCharCount(s)
            resDict[charCount].append(s)
        
        return list(resDict.values())