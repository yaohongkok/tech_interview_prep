# LeetCode 49 - Group Anagram

from collections import defaultdict

class Solution:
    def getCharCount(self, s) -> dict:
        charCount = defaultdict(int)
        for c in s:
            charCount[c]+=1
        
        return charCount


    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        resDict = defaultdict(list)

        for s in strs:
            charCount = self.getCharCount(s)

            # Need to convert dict to hashable
            resKey = tuple(sorted(charCount.items()))
            resDict[resKey].append(s)
        
        return list(resDict.values())