class Solution(object):
    def longestValidParentheses(self, s):
        """
        :type s: str
        :rtype: int
        """
        level = 0
        levelIndexTracker = {0:-1}
        maxLength = 0
        
        for i in xrange(0,len(s)):
            if(s[i]==")" and level==0):
                levelIndexTracker[level] = i
                continue
            
            if(s[i]=="("):
                level = level + 1
                levelIndexTracker[level] = i
                
            if(s[i]==")"):
                level = level - 1
                length = i - levelIndexTracker[level]
                
                if(length>maxLength):
                    maxLength = length
        
        return maxLength
