class Solution(object):
    def isPerfectSquare(self, num):
        """
        :type num: int
        :rtype: bool
        """
        
        result = False
        
        low = 1
        high = num
        prev_mid = 1
        
        while(1):
            mid = (low + high)//2
            
            if(mid**2 == num):
                result = True
                break
            
            # When there isn't a perfect square
            if(mid==prev_mid):
                result = False
                break
            
            # When mid^2 is smaller than num, estimate a larger number
            # by setting the low to mid
            if(mid**2<num):
                low = mid
            # Vice versa
            elif(mid**2>num):
                high = mid
            
            prev_mid = mid
            
        
        return result
