class Solution(object):
    memo = {}
    
    def searchMax(self, root, choose):
        if(root==None):
            return 0
        
        if((root,choose) in self.memo):
            return self.memo[(root, choose)]
        
        leftNo = self.searchMax(root.left, False)
        rightNo = self.searchMax(root.right, False)
        
        if choose==True:
            val = root.val + leftNo + rightNo
        else:
            leftYes = self.searchMax(root.left, True)
            rightYes = self.searchMax(root.right, True)
            
            val = max(leftYes, leftNo) + max(rightYes, rightNo)

        self.memo[(root, choose)] = val

        return val
    
    
    def rob(self, root):
        """
        :type root: TreeNode
        :rtype: int
        """
        return max(self.searchMax(root, True), self.searchMax(root, False))