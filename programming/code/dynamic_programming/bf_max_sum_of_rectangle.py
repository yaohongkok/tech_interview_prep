subMatrixSum = {}

class Solution(object):
    
    def maxSumSubmatrix(self, matrix, k):
        """
        :type matrix: List[List[int]]
        :type k: int
        :rtype: int
        """
        matrixWidth = len(matrix[0])
        matrixHeight = len(matrix)
        
        maxSum = None
        
        for subHeight in xrange(0,matrixHeight):
            for subWidth in xrange(0,matrixWidth):
                currentSum = self.findMaxForMatrixSize(subWidth,subHeight,matrix,k)

                if(currentSum>maxSum):
                    maxSum = currentSum
        
        return maxSum
    
    
    def findMaxForMatrixSize(self, subWidth, subHeight, matrix, k):
        matrixWidth = len(matrix[0])
        matrixHeight = len(matrix)
        maxSum = None
        
        for top in xrange(0, matrixHeight-subHeight):
            for left in xrange(0,matrixWidth-subWidth):
                total = self.getSumForSubmatrix(left, top, subWidth, subHeight, matrix)
                
                if(total > maxSum and total<=k):
                    maxSum = total
        
        return maxSum
    
    def getSumForSubmatrix(self, left, top, subWidth, subHeight, matrix):
        total = 0
        
        if((left, top, subWidth-1, subHeight) in subMatrixSum):
            for h in xrange(top,top+subHeight+1): 
                total = total + matrix[h][left+subWidth]
                
            total = total + subMatrixSum[(left, top, subWidth-1, subHeight)]
        elif((left, top, subWidth, subHeight-1) in subMatrixSum):
            total = subMatrixSum[(left, top, subWidth, subHeight-1)] + sum(matrix[top+subHeight][left:left+subWidth+1])
        else:
            for h in xrange(top,top+subHeight+1):
                total = total + sum(matrix[h][left:left+subWidth+1])
        
        subMatrixSum[(left, top, subWidth, subHeight)] = total
        
        return total
