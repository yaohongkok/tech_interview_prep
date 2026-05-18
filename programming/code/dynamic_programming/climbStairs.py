# You are climbing a stair case. It takes n steps to reach to the top.
#
# Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?
#
# Input: 2
# Output: 2
# Explanation: There are two ways to climb to the top.
# 1. 1 step + 1 step
# 2. 2 steps

class Solution(object):
    memo = {}
    
    def climbStairs(self, n):
        """
        :type n: int
        :rtype: int
        """
        
        if(n<1):
            return 0
        
        if(n in self.memo):
            return self.memo[n]
        
        if(n==1):
            self.memo[n] = 1
            return 1
            
        if(n==2):
            self.memo[n] = 2
            return 2
        
        r2 = self.climbStairs(n-2)
        if(n-2 not in self.memo):
            self.memo[n-2] = r2
            
        r1 = self.climbStairs(n-1)
        if(n-1 not in self.memo):
            self.memo[n-1] = r1
        
        
        return r1 + r2
