class Solution(object):
    def countNumbersWithUniqueDigits(self, n):
        """
        :type n: int
        :rtype: int
        """
        if(n==0):
            return 1
        
        if(n==1):
            return 10
        
        if(n>9):
            return self.countNumbersWithUniqueDigits(n-1)
        else:
            nonBeginningCombination = 1;
        
            for i in xrange(0,n-1):
                nonBeginningCombination = nonBeginningCombination*(9-i)
            
            return self.countNumbersWithUniqueDigits(n-1) + 9*nonBeginningCombination
    
