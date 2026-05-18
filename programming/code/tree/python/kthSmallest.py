# Given a binary search tree, write a function kthSmallest 
# to find the kth smallest element in it.

class Solution(object):
    smallestLevel = 0
    
    def kthSmallest(self, root, k):
        """
        Use of pre-order traversal to solve this problem.
        :type root: TreeNode
        :type k: int
        :rtype: int
        """

        # When end of tree     
        if(root==None):
            return None
        
        # Tree traversal
        res = self.kthSmallest(root.left,k)
        # Stop traversing once you found the result
        # res is not None once result is found
        if res!=None:
            return res
    
        ####################
        # Visit part of the traversal algorithm
        self.smallestLevel = self.smallestLevel + 1
        
        if(k==self.smallestLevel):
            return root.val
        ####################
            
        res = self.kthSmallest(root.right,k)
        if res!=None:
            return res
        
        return None
