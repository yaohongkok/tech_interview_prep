# Given 1->2->3->4, you should return the list as 2->1->4->3.

class Solution(object):
    def swapPairs(self, head):
        """
        :type head: ListNode
        :rtype: ListNode
        """
        
        if head == None:
            return None
        
        if head.next == None:
            return head
        
        nextPairHead = self.swapPairs(head.next.next)
        nextNode = head.next
        curNode = head
        nextNode.next = curNode
        curNode.next = nextPairHead
        
        return nextNode
