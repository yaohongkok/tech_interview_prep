# Given a complete binary tree, count the number of nodes.
#
# Note:
#
# Definition of a complete binary tree from Wikipedia:
# In a complete binary tree every level, except possibly the last, is completely filled, and all nodes in the last level are as far left as possible. It can have between 1 and 2h nodes inclusive at the last level h.

# Input: 
#    1
#   / \
#  2   3
# / \  /
#4  5 6

# Output: 6

# Definition for a binary tree node.
# class TreeNode(object):
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None

class Solution(object):
    
    def countNodes(self, root):
        """
        :type root: TreeNode
        :rtype: int
        """
        if root == None:
            return 0
        
        maxD = self.maxDepth(root)
        
        subtotal = 0
        for i in xrange(0,maxD):
            subtotal = subtotal + 2**i
            
        
        lo = 0
        hi = 2**maxD
        
        while(hi>lo):
            mid = (lo + hi)//2
            nav = self.positionToNav(mid, maxD)
            isNone = self.checkNoneWithNav(root, nav)
                
            if(isNone):
                hi = mid
            else:
                lo = mid + 1
        
        return (subtotal + lo)
    
    def checkNoneWithNav(self, root, nav):
        temp = root
        
        for i in xrange(0,len(nav)):
            if nav[i] == 'L':
                temp = temp.left
            else:
                temp = temp.right
        
        if(temp==None):
            return True
        else:
            return False
        
    
    def positionToNav(self, pos, level):
        res = ''
        
        for i in xrange(0,level):
            if pos % 2 == 0:
                res = 'L' + res
            else:
                res = 'R' + res
            
            pos = pos//2
        
        return res
            
    
    def maxDepth(self, root):
        level = 0
        
        while(root.left!=None):
            level = level + 1
            root = root.left
            
        return level
