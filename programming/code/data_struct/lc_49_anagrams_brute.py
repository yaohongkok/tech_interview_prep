# LeetCode 49 - Group Anagram

from collections import defaultdict

class Solution:
    def getCharCountDict(self, s):
        charCount = defaultdict(int)
        for c in s:
            charCount[c]+=1
        
        return charCount


    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        result = []

        charCountDict = defaultdict(lambda: defaultdict(int))
        for s in strs:
            charCountDict[s] = self.getCharCountDict(s)

        visitedIdx = set()
        i = 0
        
        while len(visitedIdx) < len(strs):
            if i not in visitedIdx:
                group = []
                s = strs[i]
                charCount = charCountDict[s]
                group.append(s)

                # Most efficient way to find similarity?
                for k in range(i + 1, len(strs)):
                    nextS = strs[k]

                    if charCount == charCountDict[nextS]:
                        visitedIdx.add(k)
                        group.append(nextS)

                visitedIdx.add(i)
                result.append(group)
            
            i += 1

        return result