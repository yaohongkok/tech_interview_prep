class Solution(object):
    def integerBreak(self, n):
        """
        :type n: int
        :rtype: int
        """
        if(n==2):
            return 1
        elif(n==3):
            return 2
        else:
            return self.helper(n)
    
    def helper(self, n):
        
        if(n==2):
            return 2
        
        if(n==3):
            return 3
        
        temp = n - 3
        subtractor = 3
        
        if(temp==1):
            temp = n-2
            subtractor = 2
        
        return subtractor*self.helper(temp)
