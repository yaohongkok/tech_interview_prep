# Input:  1->2->6->3->4->5->6, val = 6
# Output: 1->2->3->4->5

class Solution(object):
    def removeElements(self, head, val):
        """
        :type head: ListNode
        :type val: int
        :rtype: ListNode
        """
        
        if head==None:
            return None
        
        if(head.val==val):
            head = self.removeElements(head.next, val)
            return head
        
        head.next = self.removeElements(head.next, val)
        return head
