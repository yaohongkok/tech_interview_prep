# Given a non negative integer number num. For every numbers i in the 
# range 0 ≤ i ≤ num calculate the number of 1's in their binary representation 
# and return them as an array.
#
# Input: 2
# Output: [0,1,1]


import math

class Solution(object):
    def countBits(self, num):
        """
        :type num: int
        :rtype: List[int]
        """
        
        if(num==0):
            return [0]
        
        if(num==1):
            return [0,1]
        
        if(num==2):
            return [0,1,1]
        
        if(num==3):
            return [0,1,1,2]
        
        bitCount = [0,1,1,2] + [-1]*(num-3)
        
        for i in xrange(4,num+1):
            normalizedIndexFor2N = i - 2**(int(math.log(i,2)))
            startIndexForPrev2N = 2**(int(math.log(i,2)) - 1)
            
            if(normalizedIndexFor2N < startIndexForPrev2N):
                bitCount[i] = bitCount[startIndexForPrev2N + normalizedIndexFor2N]
            else:
                bitCount[i] = bitCount[startIndexForPrev2N + normalizedIndexFor2N] + 1
        
        return bitCount
