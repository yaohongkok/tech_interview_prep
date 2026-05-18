# Input:  1->2->6->3->4->5->6, val = 6
# Output: 1->2->3->4->5

class Solution(object):
    def removeElements(self, head, val):
        """
        :type head: ListNode
        :type val: int
        :rtype: ListNode
        """
        
        if not head:
            return None
        
        head = self.findNode(head,val)
        temp = head
        
        while (temp!=None and temp.next!=None):
            temp.next = self.findNode(temp.next,val)
            temp = temp.next
        
        return head
        
    
    def findNode(self,head,val):
        while(head.val==val):
            head = head.next
            
            if (head==None):
                break
        
        return head
        
