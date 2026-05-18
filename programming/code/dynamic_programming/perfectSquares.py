# Given a positive integer n, find the least number of perfect square numbers (for example, 1, 4, 9, 16, ...) which sum to n.
#
# Input: n = 12
# Output: 3 
# Explanation: 12 = 4 + 4 + 4.

class Solution:
	# These are the base case for the numbers 0, 1, 2, 3
    _memo = [0,1,2,3]
    def numSquares(self, n):
        """
        :type n: int
        :rtype: int
        """
        # Base case
        if n < 4: return self._memo[n]
        
        # Start building up from 4 onwards
        k = len(self._memo)
        for i in range(k,n+1):
            j, minval = 1, float('inf')
            
            # Try to build upon the previous result count
            while i-(j*j) >= 0:
                print("i, j: " + str(i) + ", " + str(j))
                minval = min(minval, self._memo[i-(j*j)]+1)
                print(minval)
                j+=1
            self._memo.extend([minval])
            print(self._memo)
            print("+++++++++++++++++++++++")
        return self._memo[n]
        
if __name__ == "__main__":
	output = Solution().numSquares(15)
	print(output)
