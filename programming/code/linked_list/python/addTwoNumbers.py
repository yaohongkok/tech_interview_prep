# Definition for singly-linked list.
# class ListNode(object):
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution(object):
    def addTwoNumbers(self, l1, l2):
        """
        :type l1: ListNode
        :type l2: ListNode
        :rtype: ListNode
        """
        
        resultHead = l1
        carry = 0
        
        while(l1 is not None):
            l1.val = l1.val + l2.val
            
            if(carry==1):
                carry = 0
                l1.val = l1.val + 1
            
            if(l1.val > 9):
                l1.val = l1.val - 10
                carry = 1
            
            
            
            if(l1.next is None && l2.next is not None):
                node = ListNode()
                node.val = 0
                l1.next = node
            
            if(l2.next is None && l1.next is not None):
                node = ListNode()
                node.val = 0
                l2.next = node
            
            l1 = l1.next
            l2 = l2.next
            
        
        return resultHead
